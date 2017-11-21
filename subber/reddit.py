import config
import praw
import logging

class Reddit(object):
    """Reddit API connection"""

    def __init__(self):
        try:
            self._cfg = config.get_config()['reddit-api']
        except:
            logging.exception('Unhandled exception while getting '
                          'configuration')

    def __enter__(self):
        try:
            self.session = praw.Reddit(client_id=self._cfg['id'],
                                       client_secret=self._cfg['secret'],
                                       password=self._cfg['password'],
                                       user_agent='web app',
                                       username=self._cfg['username'])
        except KeyError as e:
            logging.exception('Configuration file missing one or more'
                              ' required fields when passed to Reddit'
                              ' connection')
            return
        except Exception as e:
            logging.exception('Unhandled exception while creating a Reddit'
                             ' API connection '
                             'for user {}'.format(self._cfg['username']))
            return
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
    try:
        similar_users = _get_similar_users(session, user)
    except Exception as e:
        logging.exception('Unhandled exception while getting similar '
                          'users for user {}'.format(user))
        return
    # Create a list of sub recommendations
    subs = []
    for sim_user in similar_users:
        # Get active subs for similar user
        try:
            active_subs = _get_active_subs(session, sim_user)
        except Exception as e:
            logging.exception('Unhandled exception while getting '
                              'active subs for similar user {} wh'
                              'ile getting recommendations for us'
                              'er {}'.format(sim_user, user))
            pass
        # Add active subs to recommendations
        for sub in active_subs:
            if sub not in subs:
                subs.append(sub)
    logging.info('Recommendations for user {} found as {}\n'.format(
                 user, subs))
    if len(subs) == 0:
        logging.warning('Warning: 0 recommendations found for user {}'.format(
                        user)
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
    try:
        comments = _get_user_comments(session, user)
    except Exception as e:
        logging.exception('Unhandled exception getting user comments for '
                          'user {}'.format(user))
   if len(comments) == 0:
        logging.warning('Warning: 0 comments found for user {}'.format(user))
   try:
        for comment in comments:
            parent = comment.parent().author.name
            parent_commenters.append(parent)
    except Exception:
        logging.debug('Exception encountered for comment {} for user '
                      '{}'.format(comment, user))
        pass

    # Retrieve commenters from user's top posts
    submission_commenters = []
    try:
        submissions = _get_user_submissions(session, user)
    except Exception as e:
        logging.exception('Unhandled exception while getting comments '
                          'for user {}'.format(user))
        submissions = list()
    try:
        for s in submissions:
            for c in s.comments[:4]:
                if c.author:
                    submission_commenters.append(c.author.name)
    except Exception:
        logging.exception('Error while adding commenters')
        pass
    output = parent_commenters + submission_commenters
    logging.debug('Returning commenters and users as {} for user '
                  '{}'format(output, user))
    return output


def _get_user_comments(session, user):
    """Return a list of a user's thirty newest comments

    Keyword arguments:
    session  -- instance of the Reddit api
    user     -- username to retrieve comments for
    """
    try:
        output = session.redditor(user).comments.new(limit=30)
        logging.debug('User\'s comments retrieved for user {} as {}'.format(
                      user, output))
        return output
    except Exception as e:
        logging.exception('Error retrieving user comments for user {}'.format(
                          user))


def _get_user_submissions(session, user):
    """Return a list of a user's top fifteen submissions

    Keyword arguments:
    session  -- instance of the Reddit api
    user     -- username to retrieve submissions for
    """
    logging.info('Retrieving user submissions for user {}'.format(user))
    output = session.redditor(user).submissions.top(limit=13)
    logging.info('{} User submissions retrieved for user {}'.format(
                 len(output), user))
    logging.debug('User submissions retrieved as {}'.format(output))
    return output


def _get_active_subs(session, user):
    """Return a list of subs a user is active in

    Keyword arguments:
    session -- instance of the Reddit api
    user    -- username to retrieve active subs for
    """
    logging.info('Retrieving active subs for user {}'.format(user))
    def process_posts(posts):
        subs = []
        try:
            for p in posts:
                sub = p.subreddit_name_prefixed

                if sub not in subs:
                    subs.append(sub)
        except Exception:
            logging.exception('Exception procesing user {}\'s post '
                              '{}'.format(user, p))
            pass
        logging.info('Retrieved {} subs for user {}'.format(len(subs), user))
        logging.debug('Subs for user {} retrieved as {}'.format(user, subs))
        return subs

    # Retrieve user comments and posts
    try:
        comments = _get_user_comments(session, user)
    except Exception as e:
        logging.exception('Unhandled exception retrieving user comments '
                          'for user {}'.format(user))
        return subs
    try:
        submissions = _get_user_submissions(session, user)
    except Exception as e:
        logging.exception('Unhandled exception retrieving user posts '
                          'for user {}'.format(user))
        return subs

    # Process active subs
    try:
        subs = process_posts(comments) + process_posts(submissions)
    except Exception as e:
        logging.exception('Error combining processed posts and comments for '
                          'user {}'.format(user))
        return subs
    logging.info('{} subs found for user {}'.format(len(subs), user))
    logging.debug('Subs found for user {} as {}'.format(user, subs))
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
    except Exception as e:
       logging.exception('Unhandled exception retrieving sub info for sub '
                         '{}'.format(sub))
        return

    return {'sub': {'name': sub_name,
                    'title': subreddit.title,
                    'desc': subreddit.description}}
