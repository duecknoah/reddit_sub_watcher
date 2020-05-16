# Login to reddit every 5 mins
# Compare previous post with current and look for difference
# If there was an update notify the user

# v2 - list of multiple posts
import praw
import simplejson as json
from hashlib import md5
import asyncio
from sub_handler import SubHandler

class Watcher:
    """Watches reddit submissions to see if they have been edited/updated"""

    def __init__(self, **kwargs):
        """
        Usage: Watcher(client_id, client_secret, username, password, user_agent, subhandler=SubHandler)
        Usage: Watcher(Praw.Reddit, subhandler=SubHandler)
        """
        self.reddit = kwargs.get(
            'reddit',
            praw.Reddit(
                client_id=kwargs.get('client_id'),
                client_secret=kwargs.get('client_secret'),
                username=kwargs.get('username'),
                password=kwargs.get('password'),
                user_agent=kwargs.get('user_agent')
            )
        )
        self.sub_handler = kwargs.get('subhandler', SubHandler())

    # def watch_sub(self, sub_id):
    #     if not self.is_watching_sub(sub_id):
    #         sub, md5_hash = self.get_sub_and_hash(sub_id)
    #         self._watched_subs.append({
    #             'id': sub_id,
    #             'md5': md5_hash,
    #             'selftext': sub.selftext,
    #         })
    #
    # def is_watching_sub(self, sub_id):
    #     for s in self._watched_subs:
    #         if s['id'] == sub_id:
    #             return True
    #     return False
    #
    # def remove_sub(self, sub_id):
    #     for index, s in enumerate(self._watched_subs):
    #         if s['id'] == sub_id:
    #             del(self.watch_subs[index])

    def get_sub_and_hash(self, sub_id):
        reddit_sub = self.reddit.submission(sub_id)
        m = md5()
        m.update(reddit_sub.selftext.encode('utf-8'))
        return reddit_sub, m.hexdigest()

    async def check_messages(self):
        """
        Checks for any messages from people, to use the bot they must type:
        @DojoBlue !follow
        <BotMention> <action>
        :return:
        """

        for message in self.reddit.inbox.unread(limit=30):
            subject = message.subject.lower()
            if subject == 'username mention' and isinstance(message, praw.models.Comment):
                # process the comment here, mark as read when you're done
                tokenized_input = message.body.lower().strip().split(' ')
                action = tokenized_input[1]

                if action == 'watch':
                    self.sub_handler.follow_sub(message.author.name, message.submission.id)
                elif action == 'unwatch':
                    self.sub_handler.unfollow_sub(message.author.name, message.submission.id)


    async def check_subs(self):
        """
        Checks if the followed subs have been edited
        :return: list of subs that have been edited
        """
        updated_subs = []
        for sid in self.sub_handler.get_sub_ids():
            sub, new_hash = self.get_sub_and_hash(sid)
            if self.sub_handler.update_sub_data(sid, new_hash, sub.selftext):
                updated_subs.append(sid)

        return updated_subs

    async def _notify_followers(self, sub_ids):
        """
        Notifies the followed users of what was changed about the sub ids
        """
        print('notifying about ', sub_ids)
        for sid in sub_ids:
            users = self.sub_handler.get_users_of(sid)
            for user in users:
                msg = self.sub_handler.get_sub_data(sid)['body_diff']
                subject = 'sub {} updated!'.format(sid)
                self.reddit.redditor(user).message(subject, msg)
                print('messaged: ', user, ' about ', sid)



    async def default_watch(self, freq=300):
        """
        A wrapper for watch, where action taken on subs is to message the followed redditors
        what was changed
        :param freq:
        """
        await self.watch(self._notify_followers, freq)

    async def watch(self, callback, freq=300):
        """
        Watches followed subs and any new user messages, runs callback every <freq> seconds
        :param callback: called when >0 subs updated, list of updated sub ids is passed
        :param freq: frequency this function is run in minutes
        """
        while True:
            await self.check_messages()
            updated_subs = await self.check_subs()
            if len(updated_subs) > 0:
                await callback(updated_subs)
            await asyncio.sleep(freq)

def get_watcher(bot_data=None, settings=None, reddit=None):
    """
    :param bot_data: an object containing bot data
    :param settings: an object containing settings (followed subs)
    :param reddit: An instance of praw Reddit
    :return: an instance of Watcher
    """
    # reddit api login
    if bot_data is None:
        with open("bot_data.json") as f:
            bot_data = json.load(f)

    if settings is None:
        with open("settings.json") as f:
            settings = json.load(f)

    subhandler = SubHandler()

    if reddit is None:
        return Watcher(
            client_id=bot_data['client_id'],
            client_secret=bot_data['client_secret'],
            username=bot_data['username'],
            password=bot_data['password'],
            user_agent=bot_data['user_agent'],
            subhandler=subhandler
        )
    else:
        return Watcher(
            reddit=reddit,
            subhandler=subhandler
        )

async def test_method(subs: list):
    print('The following subs have updated: ', subs)
    print('orgtext: ', subs[0]['orgtext'])
    print('newtext: ', subs[0]['sub'].selftext)

if __name__ == '__main__':
    watcher = get_watcher()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Runs the following method every 5 minutes passing it the subs that
    # have had their submission text updated
    result = loop.run_until_complete(watcher.default_watch(5))
