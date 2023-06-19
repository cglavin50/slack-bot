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
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
bot_id = client.api_call("auth.test")['user_id'] # fetch bot information


@slack_event_adapter.on('message')
def message(payload):
    # print(payload)
    event = payload.get('event', {})
    channel_id = event.get('channel')
    uid = event.get('user')
    # text = event.get('text')
    files = event.get('files')
    if files:
        print("Files attached") # files is an array of attachments (files), each one a map
        for item in files:
            print(item) # should be 4th index
    else:
        print("No files")
    # if uid != bot_id:
        # client.chat_postMessage(channel=channel_id, text=text)

    

if __name__ == "__main__":
    app.run(debug=True)
