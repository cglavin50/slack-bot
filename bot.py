import os
import redis
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
from slack_sdk import WebClient

# env initialization
load_dotenv(find_dotenv(), verbose=True) # searches locally, could be optimized later

# init web server
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], '/slack/events', app)
@app.route('/')
def hello_world():
    return "Hello World"

# write the html using <form> attributes on index.html, and serve it for GET ip:port/

# slack init
client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
bot_id = client.api_call("auth.test")['user_id'] # fetch bot information
default_reaction = ":orangutan:"

# redis init
redis_client = redis.Redis(
    host='db', # migrate this once reach deployment stage
    port=6379,
    charset='utf-8',
    decode_responses=True,
)

response = redis_client.ping()
if response == True:
    print("Redis connection established")


# slack event handlers

@slack_event_adapter.on('message')
def message(payload):
    # print(payload, flush=True)
    event = payload.get('event', {})
    text = event.get('text')
    timestamp = event.get('ts')
    channel_id = event.get('channel')
    uid = event.get('user')

    if text == "!leaderboards" and uid != bot_id:
        print("Printing leaderboard updates", flush=True)
        leaderboard_command(channel_id)
    else:
        files = event.get('files')
        if files:
            update_counts(uid, channel_id, timestamp)
# end message handler


def leaderboard_command(channel_id):
    # write a command to check the DB and send a leaderboard update to given channel
    # should cache this as well
    
    # append all key : value pairs to a dict
    throwing_dict = {}
    workout_dict = {}
    for key in redis_client.scan_iter():
        if "throwing" in key:
            throwing_dict[key] = redis_client.get(key)
        if "workout" in key:
            workout_dict[key] = redis_client.get(key)
    # order dict for leadboards
    sorted_throwing = sorted(throwing_dict.items(), key=lambda x:x[1], reverse=True) # figure out this lambda later
    sorted_workout = sorted(workout_dict.items(), key=lambda x:x[1], reverse=True)
    msg_text = "*Justice Summer Leaderboards*\n\n\t*Throwing Leaderboard* :flying_disc:\n\t"
    counter = 1
    for item in sorted_throwing:
        if counter > 3:
            break
        msg_text += str(counter) + ". " + item[0].replace("throwing", "") + "\n\t"
        counter += 1
    counter = 1
    msg_text += "\n\t*Workouts Leaderboard* :muscle:\n"
    for item in sorted_workout:
        if counter > 3:
            break
        msg_text += str(counter) + ". " + item[0].replace("workout", "") + "\n\t"
        counter += 1
    
    # post message 
    client.chat_postMessage(
        channel = channel_id,
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": msg_text
                }
            }
        ],
        text = msg_text,
    )
# end post leadboards function
    

def update_counts(uid, channel_id, ts): # this function should increment the count of a given user to the redis DB
    response = client.users_profile_get(user=uid)
    user_profile = response.get("profile")
    real_name = user_profile.get("real_name")
    display_name = user_profile.get("display_name")
    workout_channel = os.environ["WORKOUT_ID"]
    # throwing_channel =  os.environ["THROW_ID"]
    throwing_channel = os.environ["COMMAND_ID"]
    if channel_id == workout_channel:
        print("Incrementing workout count for " + real_name + " ("+display_name+")", flush=True)
        key = real_name + " workout"
    elif channel_id == throwing_channel:
        print("Incrementing throwing count for " + real_name + " ("+display_name+")", flush=True)
        key = real_name + " throwing"
    
    print(key)
    value = redis_client.get(real_name)
    if value:
        updated = int(value) + 1
        print(redis_client.set(key, updated))
    else:
        print(redis_client.set(key, 1))


    # finally, react to the message to show we processed it
    client.reactions_add(channel=channel_id, name=default_reaction, timestamp=ts)
# end update counts function

if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 80, debug=True)
