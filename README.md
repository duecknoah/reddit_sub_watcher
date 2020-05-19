# reddit_sub_watcher
Notifies you when an edit is made to reddit submissions
- [Usage](#Usage)
- [Setup](#Setup)

## Usage
1. comment in the subreddit you want watched via `/u/BOT_NAME_HERE watch`<img src="https://user-images.githubusercontent.com/19723275/82376338-c8d9f600-99d6-11ea-92b8-f0c06ad428d3.png" alt="alt text" width="650" height="auto">
2. When the subreddit post gets edited, you'll recieve a notification in your inbox<img src="https://user-images.githubusercontent.com/19723275/82376342-caa3b980-99d6-11ea-81e9-c279fb073ca0.png" alt="alt text" width="650" height="auto">
<br /><br />
3. You'll see a message from the bot letting you know what subreddit was updated and what was changed<img src="https://user-images.githubusercontent.com/19723275/82376346-cc6d7d00-99d6-11ea-8164-d07840a66140.png" alt="alt text" width="650" height="auto">
<br /><br />
To unwatch a subreddit comment `/u/BOT_NAME_HERE unwatch`

## Setup
1. Run `pip install -r requirements.txt`
2. Make sure you setup a [reddit app](https://reddit.com/prefs/apps)<img src="https://user-images.githubusercontent.com/19723275/82376335-c7a8c900-99d6-11ea-99a4-ba4e52676522.png" alt="alt text" width="650" height="auto">
3. Edit **bot_data.json** and input your reddit apps info.
4. Run `python watcher.py`
