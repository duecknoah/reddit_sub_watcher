import difflib
import re


class SubHandler:
    """
    A wrapper class for the structure that contains subs, users, and other metadata
    """

    def __init__(self):
        self._subs = dict()

    def follow_sub(self, user, sub_id):
        subkey = self._subs.setdefault(sub_id, {
            'users': set(),
            'md5': None,
            'body': 'this is temporary\nand yea thats about it\n',
            'bodydiff': None
        })
        subkey['users'].add(user)
        print('{} followed {}'.format(user, sub_id))

    def unfollow_sub(self, user, sub_id):
        if sub_id in self._subs:
            self._subs[sub_id]['users'].remove(user)

            # Remove sub id if no users are watching
            # it anymore
            if len(self._subs[sub_id]['users']) == 0:
                self._subs.pop(sub_id)
            print('{} unfollowed {}'.format(user, sub_id))

    @staticmethod
    def get_diff(before, after):
        before = re.split('(\n)', before)
        after = re.split('(\n)', after)
        diffstring = ""

        for line in difflib.context_diff(before, after):
            diffstring += line
        return diffstring

    def update_sub_data(self, sub_id, md5, body, subreddit_name, submission_name, permalink):
        """
        Updates sub md5 hash and selftext
        :param sub_id: the id of the submission
        :param md5: the md5 hash of the sub selftext
        :param body: the raw string of the sub selftext
        :param subreddit_name: the fullname string of the subreddit
        :param submission_name: the fullname string of the submission
        :return: True if changed, None otherwise
        """
        if md5 != self._subs[sub_id]['md5']:
            is_initialized = self._subs[sub_id]['md5'] is not None

            self._subs[sub_id]['md5'] = md5
            self._subs[sub_id]['body_diff'] = SubHandler.get_diff(self._subs[sub_id]['body'], body)
            self._subs[sub_id]['body'] = body
            self._subs[sub_id]['subreddit'] = subreddit_name
            self._subs[sub_id]['submission'] = submission_name
            self._subs[sub_id]['permalink'] = permalink

            # First time setting values, don't count as update
            if not is_initialized:
                return False

            print('{} updated'.format(sub_id))
            return True
        return False

    def get_sub_data(self, sub_id):
        if sub_id in self._subs:
            return self._subs[sub_id]
        return set()

    def get_users_of(self, sub_id):
        if sub_id in self._subs:
            return self._subs[sub_id]['users']
        return set()

    def get_sub_ids(self):
        return self._subs.keys()
