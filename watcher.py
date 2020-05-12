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

    def __init__(self, **kwargs):
        '''
        Usage: Watcher(client_id, client_secret, user_agent, subs=[])
        Usage: Watcher(Praw.Reddit, subs=[])
        '''
        self.reddit = kwargs.get(
            'reddit',
            praw.Reddit(
                client_id=kwargs.get('client_id'),
                client_secret=kwargs.get('client_secret'),
                user_agent=kwargs.get('user_agent')
            )
        )
        self._watched_subs = []
        for s in kwargs.get('subs', []):
            self.watch_sub(s)

    def watch_sub(self, sub_id):
        if not self.is_watching_sub(sub_id):
            sub, md5_hash = self.get_sub_and_hash(sub_id)
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

    def get_sub_and_hash(self, sub_id):
        reddit_sub = self.reddit.submission(sub_id)
        m = md5()
        m.update(reddit_sub.selftext.encode('utf-8'))
        return reddit_sub, m.hexdigest()

    async def check_subs(self):
        '''
        Checks if the followed subs have been edited
        :return: list of subs that have been edited
        '''
        updated_subs = []
        for s in self._watched_subs:
            sub, new_hash = self.get_sub_and_hash(s['id'])

            if new_hash != s['md5']:
                updated_subs.append(sub)
                s['md5'] = new_hash
        return updated_subs

    async def watch(self, callback, freq=300):
        '''
        Watches followed subs and runs callback every <freq> seconds
        :param callback: called when >0 subs updated, list of updated sub ids is passed
        :param freq: frequency this function is run in minutes
        '''
        while True:
            updated_subs = await self.check_subs()
            if len(updated_subs) > 0:
                await callback(updated_subs)
            await asyncio.sleep(freq)

def get_watcher(bot_data=None, settings=None, reddit=None):
    '''
    :param bot_data: an object containing bot data
    :param settings: an object containing settings (followed subs)
    :param reddit: An instance of praw Reddit
    :return: an instance of Watcher
    '''
    # reddit api login
    if bot_data is None:
        with open("bot_data.json") as f:
            bot_data = json.load(f)

    if settings is None:
        with open("settings.json") as f:
            settings = json.load(f)

    if reddit is None:
        return Watcher(
            client_id=bot_data['client_id'],
            client_secret=bot_data['client_secret'],
            user_agent=bot_data['user_agent'],
            subs=settings['followed_subs']
        )
    else:
        return Watcher(
            reddit=reddit,
            subs=settings['followed_subs']
        )

async def test_method(subs: list):
    print('The following subs have updated: ', subs)

if __name__ == '__main__':
    watcher = get_watcher()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Runs the following method every 5 minutes passing it the subs that
    # have had their submission text updated
    result = loop.run_until_complete(watcher.watch(test_method, 5))
