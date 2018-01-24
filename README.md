# stack_slack_bot

A simple Python bot that asks StackExchange (you specify which sites in the network) for questions about particular subjects, and then tells a Slack channel when it's found some. Useful for any projects who expect to have a tech support burden on StackExchange.

## Configuration, setup, and running instructions

1. Get a StackExchange API key. You can get one [here](https://stackapps.com/apps/oauth/register)
2. Create a Slack app. You can do so [here](https://api.slack.com/apps)
3. Ensure that your Python installation has met the dependencies with `pip install -r requirements.txt`
4. In your Slack app, click "Add features and functionality" and "Incoming webhooks". Create a webhook for the channel of your choice.
5. Copy `config-blank.json` to `config.json` and fill it in:
  * Put your StackExchange API key in "stack_key"
  * Put your Slack webhook URL in "slack_hook"
  * Put the StackExchange network sites you wish to search in the "sites" field (e.g. `["stackoverflow", "stats"]`)
  * Put the searches you wish to report in the "searches" field.
6. Run `stack_slack_bot.py`

## Linting settings:

`pep8 --ignore W191,E101,E111,E501,E128`

`autopep8 --ignore W191,E101,E111,E128,E501 --in-place`

`pylint` (pylint settings contained in `.pylintrc`)
