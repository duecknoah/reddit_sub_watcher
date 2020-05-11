# Login to reddit every 5 mins
# Compare previous post with current and look for difference
# If there was an update notify the user

# v2 - list of multiple posts
import praw
import simplejson as json

# reddit api login
bot_data = {}
with open("bot_data.json") as f:
    bot_data = json.load(f)

reddit = praw.Reddit(
    client_id=bot_data['client_id'],
    client_secret=bot_data['client_secret'],
    user_agent=bot_data['user_agent']
)

