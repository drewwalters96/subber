import config, praw

class Reddit(object):
    def __init__(self):
        self._api = self._get_api_wrapper()

    def _get_api_cfg(self, cfg):
        """Return the API configuration options"""
        return cfg['reddit-api']

    def _get_api_wrapper(self):
        """Returns an instance of the Python Reddit API Wrapper"""
        # Load app config
        cfg = config.get_config()
        api_cfg = self._get_api_cfg(cfg)

        # Get wrapper
        return praw.Reddit(client_id=api_cfg['id'],
                           client_secret=api_cfg['secret'],
                           password=api_cfg['password'], user_agent='web app',
                           username=api_cfg['username'])

    def get_user_comments(self, user):
        """Returns a list of user comments"""
        return self._api.redditor(user).comments.new(limit=None)

    def get_user_submissions(self, user):
        """Returns a list of user submissions"""
        return self._api.redditor(user).submissions.top('all')

    def get_user_sub_score(self, user):
        """Returns a dictionary containing a user's active subreddits with a
           calculated score.
        """
        subs = dict()

        # Score subreddits from user comments
        comments = self.get_user_comments(user)
        for c in comments:
            sub = c.subreddit_name_prefixed

            if sub in subs:
                subs[sub] = subs[sub] + 1
            else:
                subs[sub] = 1

        # Score subreddits from user posts
        posts = self.get_user_submissions(user)
        for p in posts:
            sub = p.subreddit_name_prefixed

            if sub in subs:
                subs[sub] = subs[sub] + 2
            else:
                subs[sub] = 2

        return subs
