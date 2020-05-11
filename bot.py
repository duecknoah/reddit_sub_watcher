# Login to reddit every 5 mins
# Compare previous post with current and look for difference
# If there was an update notify the user

# v2 - list of multiple posts
import praw
import simplejson as json
from hashlib import md5
import asyncio

class Watcher:
    '''Watches reddit submissions to see if they have been edited/updated'''

    def __init__(self, client_id, client_secret, user_agent, subs=[]):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self._watched_subs = []
        for s in subs:
            self.watch_sub(s)

    def watch_sub(self, sub_id):
        if not self.is_watching_sub(sub_id):
            md5_hash = self.get_hash_of_sub(sub_id)
            self._watched_subs.append({
                'id': sub_id,
                'md5': md5_hash
            })

    def is_watching_sub(self, sub_id):
        for s in self._watched_subs:
            if s['id'] == sub_id:
                return True
        return False

    def remove_sub(self, sub_id):
        for index, s in enumerate(self._watched_subs):
            if s['id'] == sub_id:
                del(self.watch_subs[index])

    def get_hash_of_sub(self, sub_id):
        reddit_sub = self.reddit.submission(sub_id)
        m = md5()
        m.update(reddit_sub.selftext.encode('utf-8'))
        return m.hexdigest()

    async def check_subs(self):
        '''
        Checks if the followed subs have been edited
        :return: list of sub ids that have been edited
        '''
        updated_subs = []
        for s in self._watched_subs:
            new_hash = self.get_hash_of_sub(s['id'])

            if new_hash != s['md5']:
                updated_subs.append(s['id'])
                s['md5'] = new_hash
        return updated_subs

    async def watch(self, callback, freq=300):
        '''
        Watches followed subs and runs callback every <freq> seconds
        :param callback: callback function, list of updated sub ids is passed
        :param freq: frequence this function is run in minutes
        '''
        while True:
            updated_subs = await self.check_subs()
            await callback(updated_subs)
            await asyncio.sleep(freq)


async def test_method(subs: list):
    if len(subs) > 0:
        print('The following subs have updated: ', subs)

if __name__ == '__main__':
    # reddit api login
    bot_data = {}
    with open("bot_data.json") as f:
        bot_data = json.load(f)

    settings = {}
    with open("settings.json") as f:
        settings = json.load(f)

    watcher = Watcher(
        bot_data['client_id'],
        bot_data['client_secret'],
        bot_data['user_agent'],
        subs=settings['followed_subs']
    )
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(watcher.watch(test_method, 1))
