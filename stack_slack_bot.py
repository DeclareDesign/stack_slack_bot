""" Asks StackExchange for questions about subjects, reports them to a Slack channel. """

import datetime
import json
import sys
import sqlite3
import traceback
import requests


def process_single_response(response):
	""" Reshapes response JSON object into the fields we care about. """
	processed_response = {
		"id": response["question_id"],
		"user": response["owner"]["display_name"],
		"link": response["link"],
		"title": response["title"],
		"tags": response["tags"]
	}
	return processed_response


def db_init(db, cursor):
	""" Initialize the DB if it doesn't exist. """
	cursor.execute("CREATE TABLE IF NOT EXISTS whitelist (id INTEGER);")
	db.commit()


def add_id(db, cursor, insert_id):
	""" Cache the question ID in the DB so we don't spam multiple notifications. """

	cursor.execute("INSERT INTO whitelist (id) VALUES (?)", [insert_id])
	db.commit()


def tell_slack(question, config):
	""" Tell slack we found a question. """

	if len(question["tags"]):
		body_message = "Tags: " + " ".join(question["tags"])
	else:
		body_message = "No tags"

	message = {
		"attachments": [
			{
				"color": "#5D65C4",
				"pretext": "New Stack question detected",
				"author_name": question["user"],
				"title": question["title"],
				"title_link": question["link"],
				"text": body_message
			}
		]
	}

	requests.post(config["slack_hook"], json=message)


def ping_stack_exchange(site, query, config):
	""" Ask Stack Exchange for questions in the last week. """

	# Reported whitelist
	whitelist_db = sqlite3.connect("whitelist.db")
	whitelist_cursor = whitelist_db.cursor()
	db_init(whitelist_db, whitelist_cursor)
	whitelisted_query = whitelist_cursor.execute("SELECT id FROM whitelist;")
	whitelisted_ids = []
	for row in whitelisted_query:
		whitelisted_ids.append(row[0])

	# Search scope to last week
	current_date = datetime.datetime.now().strftime("%s")
	last_week = (datetime.datetime.now() - datetime.timedelta(days=config["days_to_search"])).strftime("%s")
	request = {
		"key": config["stack_key"],
		"order": "desc",
		"sort": "creation",
		"q": query,
		"site": site,
		"closed": False,
		"fromdate": last_week,
		"todate": current_date
	}

	response_data = requests.get(config["stack_api"], data=request).json()

	for item in response_data["items"]:
		fix_response = process_single_response(item)
		if fix_response["id"] in whitelisted_ids:
			continue

		add_id(whitelist_db, whitelist_cursor, fix_response["id"])
		tell_slack(fix_response, config)

	return


def main_loop():
	""" Iterate through sites/searches. """
	try:
		config = json.load(open("config.json", "r"))
	except:
		print "You must setup the config.json file."
		sys.exit(1)

	if any(x not in config or not len(config[x]) for x in ["stack_key", "stack_api", "slack_hook", "sites", "searches"]):
		print "You must fill out the fields in the config.json file."
		sys.exit(1)

	for site in config["sites"]:
		for package in config["searches"]:
			try:
				ping_stack_exchange(site, package, config)
			except:
				print "Error checking", site, "for questions for", package
				print traceback.format_exc()
				sys.exit(1)


if __name__ == "__main__":
	main_loop()
