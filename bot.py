import slack
import os
import redis
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter

# env initialization
env_path = Path('.') / '.env' # stored in root directory
load_dotenv(dotenv_path=env_path)

# init web server
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], '/slack/events', app)

# slack init
client = slack.WebClient(token=os.environ['SLACK_API_TOKEN'])
bot_id = client.api_call("auth.test")['user_id'] # fetch bot information

# redis init
redis_client = redis.Redis(
    host='localhost', # migrate this once reach deployment stage
    port=6379,
    charset='utf-8',
    decode_responses=True,
)

response = redis_client.ping()
print(response)


# slack event handlers

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

def update_counts(uid, channel_id):
    # this function should increment the count of a given user to the redis DB
    response = client.users_profile_get(user=uid)
    user_profile = response.get("profile")
    real_name = user_profile.get("real_name")
    display_name = user_profile.get("display_name")
    # temp
    workout_channel = "temp id"
    throwing_channel = "tempid2"
    if channel_id == workout_channel:
        print("Incrementing workout count for " + real_name + " ("+display_name+")")
        key = real_name + " workout"
    elif channel_id == throwing_channel:
        print("Incrementing throwing count for " + real_name + " ("+display_name+")")
        key = real_name + " throwing"
    
    print(key)
    value = redis_client.get(real_name)
    if value:
        updated = int(value) + 1
        print(redis_client.set(key, updated))
    else:
        print(redis_client.set(key, 1))
# end update counts function

if __name__ == "__main__":
    app.run(debug=True)
