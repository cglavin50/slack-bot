import os
import redis
from dotenv import load_dotenv, find_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
from slack_sdk import WebClient

# env initialization
load_dotenv(find_dotenv(), verbose=True) # searches locally, could be optimized later

# init web server TODO
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], '/slack/events', app)
@app.route('/')
def hello_world():
    return "Hello World"

# write the html using <form> attributes on index.html, and serve it for GET ip:port/

# slack init
client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
bot_id = client.api_call("auth.test")['user_id'] # fetch bot information
reactions_list = ["bike", "chris", "ab", "schmitty", "hawk", "ezra", "erik", "cooper", "beard_simon", "tupp"]
default_reaction = "robot_face"


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
else:
    print("Redis connection failed")
    quit

# slack event handlers
@slack_event_adapter.on('message')
def message(payload):
    # print(payload, flush=True)
    event = payload.get('event', {})
    text = event.get('text')
    timestamp = event.get('ts')
    channel_id = event.get('channel')
    uid = event.get('user')
    text = event.get('text')

    if text == "!list" and uid != bot_id:
        list_db(channel_id)
    elif text == "!leaderboards" and uid != bot_id:
        print("Printing leaderboard updates", flush=True)
        leaderboard_command(channel_id)
    elif text == "!wwc" and uid != bot_id:
        print("Printing wwc", flush=True)
        wwc_list(channel_id)
    elif text == "!clear" and uid == os.environ["ADMIN_ID"]:
        print("Clearing the DB", flush=True)
        clear()
    elif uid != bot_id:
        users = parse_text(uid, text)
        for user in users:
            print(f"user from parse-text: {user}", flush=True)
        files = event.get('files')
        if files:
            update_counts(users, channel_id, timestamp, text)
# end message handler

def parse_text(sender, txt): # takes in UID of the sender, and the text to see if there are any more mentioned user IDs
    response = client.users_profile_get(user = sender) 
    user_profile = response.get("profile")
    real_name = user_profile.get("real_name")
    users = [real_name]
    split = txt.replace("<", " ").replace(">", " ").strip().split("@") # looking for any mentioned user IDs
    for str in split: # inefficient but low cost anyways
        try:
            response = client.users_profile_get(user = str)
            user_profile = response.get("profile")
            real_name = user_profile.get("real_name")
            print(real_name + " mentioned in a message", flush=True)
            users = users.append(real_name)
        except:
            print("Unidentified user mentioned in message: " + str, flush=True)
            continue
    # populate user array with any mentioned users
    return users
# end parse_text function
    
def list_db(channel_id): # for debugging
    throwing_dict = {}
    workout_dict = {}
    for key in redis_client.scan_iter():
        if "throwing" in key:
            throwing_dict[key] = redis_client.get(key)
        if "workout" in key:
            workout_dict[key] = redis_client.get(key)
    
    sorted_throwing = sorted(throwing_dict.items(), key=lambda x:int(x[1]), reverse=True) # figure out this lambda later
    sorted_workout = sorted(workout_dict.items(), key=lambda x:int(x[1]), reverse=True)


    msg_text = "*Justice Summer Leaderboards*\n\n\t*Throwing Leaderboard* :flying_disc:\n\t"
    for item in sorted_throwing:
        msg_text += item[0].replace(" throwing", "") + ": " + item[1] + "\n\t"
    msg_text += "\n\t*Workouts Leaderboard* :muscle:\n\t"
    for item in sorted_workout:
        msg_text += item[0].replace(" workout", "") + ": " + item[1] + "\n\t"

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
# end list (extended leaderboard) function

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
    sorted_throwing = sorted(throwing_dict.items(), key=lambda x:int(x[1]), reverse=True) # figure out this lambda later
    sorted_workout = sorted(workout_dict.items(), key=lambda x:int(x[1]), reverse=True)

    msg_text = "*Justice Summer Leaderboards*\n\n\t*Throwing Leaderboard* :flying_disc:\n\t"
    counter = 1
    for item in sorted_throwing:
        if counter > 3:
            break
        msg_text += str(counter) + ". " + item[0].replace(" throwing", "") + ": " + item[1] + "\n\t"
        counter += 1
    counter = 1
    msg_text += "\n\t*Workouts Leaderboard* :muscle:\n\t"
    for item in sorted_workout:
        if counter > 3:
            break
        msg_text += str(counter) + ". " + item[0].replace(" workout", "") + ": " + item[1] + "\n\t"
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

def wwc_list(channel_id): # post everyones total by team 
    lloyd = ["Ezra Tinsky", "Thomas Schmitt", "Tommy Reichard", "Nikolai Seferian", "Bilal"]
    kai = ["Chris Strawn", "Joshua Datz", "Erik Anaya", "Braden Laidlaw", "Will Thomas", "Brooks Clifford"]
    jay = ["Isaac Hawkins", "Grandpa", "Andreas Moeller", "Matt O'Connor", "Aidan Williams"] # Stevie = grandpa
    zane = ["Michael Gordon", "Simon Mulrooney", "Hou Ning Song", "Benjamin Portner", "Rishu Nevatia"]
    cole = ["Cooper Glavin", "Joshua Chilmaid", "Kaden Saad", "Lucas Suarez", "Jacob Graybow"]
    garmadon = ["Andrew Sington", "Will Riley", "Archie Kranz", "Aaron Magtoto", "Sassan Fiske"]
    
    teams = [lloyd, kai, jay, zane, cole, garmadon]
    
    lloyd_text = "\t*Team Lloyd* :lloyd:\n\t\t"
    kai_text = "\t*Team Kai* :kai:\n\t\t"
    jay_text = "\t*Team Jay* :jay:\n\t\t"
    zane_text = "\t*Team Zane* :zane:\n\t\t"
    cole_text = "\t*Team Cole* :cole:\n\t\t"
    garmadon_text = "\t*Team Garmadon* :garmadon:\n\t\t"
    categories = ["sprint", "lift", "agility", "mobility", "mental"]
    
    texts = [lloyd_text, kai_text, jay_text, zane_text, cole_text, garmadon_text]
    
    message = "*Weekly WWC Updates :snowflake::snowflake:*\n"
    
    for i in range(len(teams)):
        team = teams[i]
        text = texts[i]
        for player in team:
            line = "- " + player + ": "
            line_list = []
            for category in categories:
                key = player + " " + category
                print(f"fetching key {key}", flush=True)
                value = redis_client.get(key)
                if value:
                    line_list.append(category + " " + value)
            line += ", ".join(line_list) + "\n\t\t"
            text += line
        message += text + "\n"
        
    # post message 
    client.chat_postMessage(
        channel = channel_id,
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }
        ],
        text = message,
    )
# end wwc leaderboard
            
def clear():
    # clear the redis DB
    redis_client.flushall()

# def mini(message): # create a poll to select mini times
#     reaction_list = random.sample(reaction_list, 4)
    
#     times = message.split(" ")
#     start = times[1]
#     # end = times[2]
    
#     msg_text = '''
#     **React to Vote for Mini Times**
#     > ${reaction_list[0]} to vote for ${start}
    
#     > ${reaction_list[1]} to vote for ${start + 1}
    
#     '''
    
#     client.chat_postMessage(
#         channel = os.environ["MINI_ID"],
#         blocks = [
#             {
#                 "type": "section",
#                 "text": {
#                     "type": "mrkdwn",
#                     "text": msg_text
#                 }
#             }
#         ],
#         text = msg_text,
#     ) # TODO: add implementation to send mini times as a survey
# end mini function
    

def update_counts(names, channel_id, ts, text): # takes in array of user real names, and increments the keys accordingly
    real_name = names[0] # for each mention name, grab appropriate categories and update
    for name in names:
        workout_channel = "C05J39BKG3S" # os.environ["WORKOUT_ID"] # TODO move to workout ID once working # "C05J39BKG3S"
        throwing_channel =  os.environ["THROW_ID"]
        key = ""
        if channel_id == workout_channel:
            # key = name + " workout"
            key = extract_workout_key(name, text)
        elif channel_id == throwing_channel:
            key = name + " throwing"
            
        value = redis_client.get(key)
        print(f"Updating key: {key}", flush=True)
        if value:
            updated = int(value) + 1
            print(f"New value: {updated}", flush=True)
            print(redis_client.set(key, updated))
        else:
            print(f"Setting to 1", flush=True)
            print(redis_client.set(key, 1))
    # update each mentioned user (including that who posted it)

    # finally, react to the message to show we processed it
    reaction = default_reaction
    if real_name == "Chris Strawn":
        reaction = "chris"
    if real_name == "Thomas Schmitt":
        reaction = "schmitty"
    if real_name == "Erik Anaya":
        reaction = "erik"
    if real_name == "Cooper Glavin":
        reaction = "cooper"
    if real_name == "Ezra Tinksy":
        reaction = "ezra"
    if real_name == "Simon Mulrooney":
        reaction = "beard_simon"
    if real_name == "Michael Gordon":
        reaction = "tupp"
    if real_name == "Isaac Hawkins":
        reaction = "hawk"
    if real_name == "Yinderman de la Routicus":
        reaction = "paul"
    
    client.reactions_add(channel=channel_id, name=reaction, timestamp=ts)
# end update counts function

def extract_workout_key(name, text): # takes in the text string and sends to appropriate leaderboard ASSUMES ONLY ONE CATEGORY PER
    key = ""
    if "mini" in text.lower() or "biggie" in text.lower() or "pickup" in text.lower():
        key = name + " agility"
        key = name + " sprints"
    elif "lift" in text.lower():
        key = name + " lift"
    elif "sprint" in text.lower():
        key = name + " sprint"
    elif "mobility" in text.lower():
        key = name + " mobility"
    elif "agility" in text.lower():
        key = name + " agility"
    elif "mental" in text.lower():
        key = key + " mental"
        
    return key

if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 80, debug=True)
