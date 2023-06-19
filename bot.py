import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter

# initialization
env_path = Path('.') / '.env' # stored in root directory
load_dotenv(dotenv_path=env_path)

# init web server
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], '/slack/events', app)

# slack 
client = slack.WebClient(token=os.environ['SLACK_API_TOKEN'])
bot_id = client.api_call("auth.test")['user_id'] # fetch bot information


@slack_event_adapter.on('message')
def message(payload):
    # print(payload)
    event = payload.get('event', {})
    text = event.get('text')

    if text == "/leaderboards":
        leaderboard_command(event.get('channel'))
    else:
        uid = event.get('user')
        files = event.get('files')
        if files:
            print("Files attached") # files is an array of attachments (files), each one a map
            update_counts(uid)

        # if uid != bot_id:
            # client.chat_postMessage(channel=channel_id, text=text)


def leaderboard_command(channel_id):
    # write a command to check the DB and send a leaderboard update to given channel
    # should cache this as well
    print("Implement this later")

def update_counts(uid):
    # this function should increment the count of a given user to the redis DB
    response = client.users_profile_get(user=uid)
    user_profile = response.get("profile")
    real_name = user_profile.get("real_name")
    display_name = user_profile.get("display_name")
    print("Incrementing count for " + display_name + ", aka " + real_name)


if __name__ == "__main__":
    app.run(debug=True)
