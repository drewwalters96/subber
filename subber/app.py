import logging

import falcon

from subber import reddit

logger = logging.getLogger(__name__)


class Recommend:
    def on_get(self, req, resp, user):
        """Get user recommendations

        Keyword arguments:
        req  -- request object routed from upstream
        resp -- resp object to be updated
        user -- string containing reddit username

        Side effects:
        resp -- response added to response object media
        """
        logging.info('Recieved request GET /user/{}'.format(user))
        try:
            subs = reddit.get_user_recommendations(session, user)

            response = {'status': 'success',
                        'user': user,
                        'recommendations': subs}

            resp.status = falcon.HTTP_200
            logging.info('Returning success response for user {} with '
                         'recommendations {}'.format(user, subs))

        except Exception:
            logging.exception('Exception while getting user recommendations '
                              'for user {}'.format(user))
            response = {'status': 'failure', 'user': user}
            resp.status = falcon.HTTP_500

        resp.media = response


def init_logging():
    """Init Subber logging"""
    try:
        logging.basicConfig(filename='subber.log', level=logging.DEBUG,
                            format='%(asctime)-26s %(name)-17s '
                                   '%(levelname)-8s %(message)s', filemode='a')

        # Suppress outside loggers
        logging.getLogger('prawcore').setLevel(logging.WARNING)
        logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
        logging.getLogger('werkzeug').setLevel(logging.WARNING)

    except Exception as e:
        raise RuntimeError('Unable to initiate logging:\n{}'.format(e))


def init_api():
    try:
        api = falcon.API()
        api.add_route('/user/{user}', Recommend())

        return api
    except Exception as e:
        logging.critical('Error initializing API:\n{}'.format(e))
        raise RuntimeError('Error initializing API')


init_logging()
session = reddit.Reddit().get_session()
api = init_api()
