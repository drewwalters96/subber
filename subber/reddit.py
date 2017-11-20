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


def get_user_recommendations(session, user):
    """Return a list of recommended subs for a user

    Keyword arguments:
    session  -- instance of the Reddit api
    user     -- username to retrieve recommendations for
    """
    # Get similar users
    similar_users = _get_similar_users(session, user)

    # Create a list of sub recommendations
    subs = []
    for user in similar_users:
        # Get active subs for similar user
        active_subs = _get_active_subs(session, user)

        # Add active subs to recommendations
        for sub in active_subs:
            if sub not in subs:
                subs.append(sub)

    return subs


def _get_similar_users(session, user):
    """Return a list containing users that have commented on a user's post
    and users whose posts have been commented on by a user.

    Keyword arguments:
    session -- instance of the Reddit api
    user    -- username to retrieve similar users for
    """
    # Retrieve commenters from parent comments
    parent_commenters = []
    comments = _get_user_comments(session, user)
    try:
        for comment in comments:
            parent = comment.parent().author.name
            parent_commenters.append(parent)
    except Exception:
        pass

    # Retrieve commenters from user's top posts
    submission_commenters = []
    submissions = _get_user_submissions(session, user)
    try:
        for s in submissions:
            for c in s.comments[:4]:
                if c.author:
                    submission_commenters.append(c.author.name)
    except Exception:
        pass

    return parent_commenters + submission_commenters


def _get_user_comments(session, user):
    """Return a list of a user's thirty newest comments

    Keyword arguments:
    session  -- instance of the Reddit api
    user     -- username to retrieve comments for
    """
    return session.redditor(user).comments.new(limit=30)


def _get_user_submissions(session, user):
    """Return a list of a user's top fifteen submissions

    Keyword arguments:
    session  -- instance of the Reddit api
    user     -- username to retrieve submissions for
    """
    return session.redditor(user).submissions.top(limit=15)


def _get_active_subs(session, user):
    """Return a list of subs a user is active in

    Keyword arguments:
    session -- instance of the Reddit api
    user    -- username to retrieve active subs for
    """
    def process_posts(posts):
        subs = []
        try:
            for p in posts:
                sub = p.subreddit_name_prefixed

                if sub not in subs:
                    subs.append(sub)
        except Exception:
            pass

        return subs

    # Retrieve user comments and posts
    comments = _get_user_comments(session, user)
    submissions = _get_user_submissions(session, user)

    # Process active subs
    subs = process_posts(comments) + process_posts(submissions)

    return subs


def get_sub_info(session, sub):
    """Return a dictionary containing metadata for a subreddit

    Keyword arguments:
    session -- instance of the Reddit api
    sub     -- subreddit to get metadata for
    """
    subreddit = session.subreddit(sub)
    sub_name = 'r/{}'.format(sub)

    return {'sub': {'name': sub_name,
                    'title': subreddit.title,
                    'desc': subreddit.description}}
