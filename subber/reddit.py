import config
import praw


class Reddit(object):
    """Reddit API connection"""

    def __init__(self):
        self._cfg = config.get_config()['reddit-api']

    def __enter__(self):
        self.session = praw.Reddit(client_id=self._cfg['id'],
                                   client_secret=self._cfg['secret'],
                                   password=self._cfg['password'],
                                   user_agent='web app',
                                   username=self._cfg['username'])
        return self.session

    def __exit__(self, exception_type, exception_value, traceback):
        pass


def get_user_comments(session, user):
    """Return a list of user comments

    Keyword arguments:
    session  -- instance of the Reddit api
    user -- the username to retrieve comments for
    """
    return session.redditor(user).comments.new(limit=2)


def get_user_submissions(session, user):
    """Return a list of user submissions

    Keyword arguments:
    session  -- instance of the Reddit api
    user -- the username to retrieve submissions for
    """
    return session.redditor(user).submissions.top(limit=2)


def get_user_sub_score(session, user):
    """Return a dictionary containing a user's active subreddits with a
    calculated score

    Keyword arguments:
    session  -- instance of the Reddit api
    user -- the username to retrieve submissions for
    """
    subs = dict()

    # Score subreddits from user comments
    comments = get_user_comments(session, user)
    for c in comments:
        sub = c.subreddit_name_prefixed

        if sub in subs:
            subs[sub] = subs[sub] + 1
        else:
            subs[sub] = 1

    # Score subreddits from user posts
    posts = get_user_submissions(session, user)
    for p in posts:
        sub = p.subreddit_name_prefixed

        if sub in subs:
            subs[sub] = subs[sub] + 2
        else:
            subs[sub] = 2

    return subs


def get_top_post_commenters(session, user):
    """Return a list of commenters from a user's top posts

    Keyword arguments:
    session  -- instance of the Reddit api
    user -- the username to retrieve submissions for
    """
    submissions = get_user_submissions(session, user)
    return [c.author for s in submissions for c in s.comments[:5]]


def get_user_recommendations(session, user):
    """Return a list of recommended subs for a user

    Keyword arguments:
    session  -- instance of the Reddit api
    user -- the username to retrieve submissions for
    """
    commenters = get_top_post_commenters(session, user)

    # Get subs commenters are active in
    subs = []
    for c in commenters:
        if not c:
            continue
        for sub, _ in get_user_sub_score(session, c.name).items():
            if sub not in subs:
                subs.append(sub)

    return subs
