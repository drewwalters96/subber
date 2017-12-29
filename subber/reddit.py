import logging

import praw
import prawcore

from subber import config, util

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

                # Get sub metadata and append if not in subs
                sub_info = get_sub_info(session, sub[2:])

                if sub_info not in subs:
                    subs.append(sub_info)

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
    similar_users = []

    # Retrieve commenters from parent comments
    comments = _get_user_comments(session, user)

    try:
        for comment in comments:
            parent = comment.parent().author.name
            if parent not in similar_users and parent != user:
                similar_users.append(parent)
    except Exception:
        # Comment is deleted
        pass

    # Retrieve commenters from user's top posts
    submissions = _get_user_submissions(session, user)

    try:
        for s in submissions:
            for c in s.comments:
                if (c.author and c.author.name not in similar_users and
                        c.author.name != user):
                    similar_users.append(c.author.name)

                break  # limit to one submission comment
    except Exception:
        # Comments missing
        logger.debug('Skipping submission comments for user '
                     '{}'.format(user))
        pass

    logger.debug('Considering similar users {} for user '
                 '{}'.format(similar_users, user))

    return similar_users


def _get_user_comments(session, user):
    """Return a list of a user's five newest comments

    Keyword arguments:
    session  -- instance of the Reddit api
    user     -- username to retrieve comments for
    """
    try:
        comments = session.redditor(user).comments.new(limit=5)
        logger.debug('PRAW comment request made for user {}'.format(user))

        return comments
    except Exception:
        logger.error('Error retrieving comments for user {}'.format(user))


def _get_user_submissions(session, user):
    """Return a list of a user's top five submissions

    Keyword arguments:
    session  -- instance of the Reddit api
    user     -- username to retrieve submissions for
    """
    try:
        submissions = session.redditor(user).submissions.top(limit=5)
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
                         '{}'.format(user))
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
        # Get subreddit metadata
        subreddit = session.subreddit(sub)

        # Convert seconds after UTC epoch to years since sub creation
        sub_age = util.utc_epoch_sec_to_years(subreddit.created)

        return {'name': subreddit.display_name_prefixed,
                'title': subreddit.title,
                'age': sub_age,
                'subscribers': subreddit.subscribers,
                'over18': subreddit.over18,
                'desc': subreddit.public_description}
    except Exception:
        logger.debug('Unable to retrieve sub info for {}'.format(sub))
