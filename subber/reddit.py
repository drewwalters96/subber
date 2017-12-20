import logging

import praw
import prawcore

from subber import config

logger = logging.getLogger(__name__)


class Reddit(object):
    """Reddit API session"""

    def __init__(self):
        self._cfg = config.get_api_config()
        self._session = praw.Reddit(client_id=self._cfg['id'],
                                    client_secret=self._cfg['secret'],
                                    password=self._cfg['password'],
                                    user_agent='web app',
                                    username=self._cfg['username'])

        # Verify connection
        try:
            self._session.user.me()
        except prawcore.exceptions.OAuthException:
            logger.critical('Unable to initialize Reddit API session. Verify '
                            'the credentials in the Subber config file are '
                            'correct.')

            raise RuntimeError('Unable to initialize Reddit API session.')

    def get_session(self):
        return self._session


def get_user_recommendations(session, user):
    """Return a list of recommended subs for a user

    Keyword arguments:
    session  -- instance of the Reddit api
    user     -- username to retrieve recommendations for
    """
    # Get similar users
    try:
        similar_users = _get_similar_users(session, user)
    except Exception as e:
        logger.error('Unable to get recommendations for user {}. Error '
                     'retrieving similar users.'.format(user))
        logger.exception(e)

        return

    # Create a list of sub recommendations
    subs = []
    for sim_user in similar_users:
        # Get active subs for similar user
        try:
            active_subs = _get_active_subs(session, sim_user)

            # Add active subs to recommendations
            for sub in active_subs:
                if sub not in subs:
                    subs.append(sub)

        except Exception as e:
            logger.exception('Unable to get recommendations for user {}. '
                             'Error retrieving active subs for user '
                             '{}'.format(user, sim_user))
            logger.exception(e)

    if len(subs) == 0:
        logger.warning('No recommendations found for user {}'.format(user))
    else:
        logger.debug('Recommending subs {} to user {}.'.format(subs, user))

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
            # Comment is deleted
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
        # Comments missing
        logger.debug('Skipping submission comments for user '
                     '{}'.format(user))
        pass

    similar_users = parent_commenters + submission_commenters
    logger.debug('Returning similar users for user {} as '
                 '{}'.format(user, similar_users))

    return similar_users


def _get_user_comments(session, user):
    """Return a list of a user's thirty newest comments

    Keyword arguments:
    session  -- instance of the Reddit api
    user     -- username to retrieve comments for
    """
    try:
        comments = session.redditor(user).comments.new(limit=30)
        logger.debug('PRAW comment request made for user {}'.format(user))

        return comments
    except Exception:
        logger.error('Error retrieving comments for user {}'.format(user))


def _get_user_submissions(session, user):
    """Return a list of a user's top fifteen submissions

    Keyword arguments:
    session  -- instance of the Reddit api
    user     -- username to retrieve submissions for
    """
    try:
        submissions = session.redditor(user).submissions.top(limit=13)
        logger.debug('PRAW submission request made for user {}'.format(user))

        return submissions
    except Exception:
        logger.error('Error retrieving submissions for user {}'.format(user))


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
            # Skip post if missing metadata
            logger.error('Error processing content request results for user '
                         '{}. User may be deleted'.format(user))
            pass

        return subs

    # Retrieve user comments and submissions
    comments = _get_user_comments(session, user)
    submissions = _get_user_submissions(session, user)

    # Process active subs
    subs = []

    if comments is not None:
        logger.debug('Processing PRAW comment request results for user '
                     '{}'.format(user))

        subs = process_posts(comments)

    if submissions is not None:
        logger.debug('Processing PRAW submission requst results for user '
                     '{}'.format(user))

        subs = subs + process_posts(submissions)

    logger.debug('{} active subs found for user {}'.format(len(subs), user))

    if len(subs) > 0:
        logger.debug('Active subs found for user {} as {}'.format(user, subs))

    return subs


def get_sub_info(session, sub):
    """Return a dictionary containing metadata for a subreddit

    Keyword arguments:
    session -- instance of the Reddit api
    sub     -- subreddit to get metadata for
    """
    try:
        subreddit = session.subreddit(sub)
        sub_name = 'r/{}'.format(sub)

        return {'sub': {'name': sub_name,
                        'title': subreddit.title,
                        'desc': subreddit.description}}
    except Exception:
        logger.debug('Unable to retrieve sub info for {}'.format(sub))
