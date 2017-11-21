import falcon
import reddit
import logging

class SessionMiddleware(object):
    def process_request(self, req, resp):
        """Add Reddit API session to request context

        Keyword arguments:
        req  -- request object to be routed to the request handler
        resp -- resp object to append response content

        Side effects:
        req -- API session added to request context
        """
        try:
            with reddit.Reddit() as session:
                req.context = {'session': session}
        except Exception as e:
            logging.exception('Unable add Reddit API session'
                              ' to request context.')


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
        logging.info('Recieved recommendation request '
                     'for user {0}'.format(user))
        try:
            session = req.context['session']
        except KeyError as e:
            logging.exception('Request context does not contain session '
                              'data')
            return

        try:
            recommendations = reddit.get_user_recommendations(session, user)

            # Get subreddit metadata
            subs = []
            for sub in recommendations:
                data = reddit.get_sub_info(session, sub[2:])
                subs.append(data)

            response = {'status': 'success',
                        'user': user,
                        'recommendations': subs}

            resp.status = falcon.HTTP_200
            logging.info('Returning success response for user {} with '
                         'recommendations {}'.format(user, recommendations))

        except Exception as e:
            logging.exception('Exception while getting user recommendations '
                              ' for user {}'.format(user))
            response = {'status': 'failure', 'user': user}
            resp.status = falcon.HTTP_500
        resp.media = response

# Start logging - kill script if there is an error opening log file
try:
    logging.basicConfig(filename='subber.log', level=logging.DEBUG, format='%(asctime)s %(message)s', filemode='a')
except Exception as e:
    exit('Unable to initiate logging because of: \n{}'.format(e))

try:
    api = falcon.API(middleware=[SessionMiddleware()])
    tryapi.add_route('/user/{user}', Recommend())
except Exception as e:
    logging.exception('Unhandled exception while initializing API')
