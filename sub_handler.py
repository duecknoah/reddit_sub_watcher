import difflib
import re
import pickle


class SubHandler:
    """
    A wrapper class for the structure that contains subs, users, and other metadata
    """

    def __init__(self, do_load=True):
        self._subs = dict()
        if do_load:
            self.load_data()

    def follow_sub(self, user, sub_id):
        subkey = self._subs.setdefault(sub_id, {
            'users': set(),
            'md5': None,
            'body': '',
            'bodydiff': ''
        })
        subkey['users'].add(user)
        self.save_data()
        print('{} followed {}'.format(user, sub_id))

    def unfollow_sub(self, user, sub_id):
        if sub_id in self._subs:
            self._subs[sub_id]['users'].remove(user)

            # Remove sub id if no users are watching
            # it anymore
            if len(self._subs[sub_id]['users']) == 0:
                self._subs.pop(sub_id)
            self.save_data()
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
        retVal = False
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
                retVal = False
            else:
                print('{} updated'.format(sub_id))
                self.save_data()
                retVal = True
        return retVal

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

    def save_data(self):
        """ Saves sub handler data to subdata.pkl"""
        with open("subdata.pkl", 'wb') as f:
            pickle.dump(self._subs, f, pickle.HIGHEST_PROTOCOL)

    def load_data(self):
        """ Loads subh handler data from subdata.pkl if it exists"""
        try:
            with open("subdata.pkl", 'rb') as f:
                self._subs = pickle.load(f)
        except (IOError, FileNotFoundError, EOFError) as e:
            pass