import json
import logging

import flask

from subber import reddit

app = flask.Flask(__name__)
logger = logging.getLogger(__name__)


@app.route('/')
def get_form():
    return flask.render_template('form.html')


@app.route('/user', methods=['POST'])
def get_sub_recommendations():
    """Get user recommendations

    Keyword arguments:
    user -- string containing reddit username
    """
    user = flask.request.form['username']

    logger.info('Recieved recommendation request '
                'for user {0}'.format(user))

    try:
        recommendations = reddit.get_user_recommendations(session, user)

    except Exception as e:
        logger.exception(e)

    try:
        response = flask.render_template('results.html', user=user,
                                         recommendations=recommendations)

        logger.info('Returning success response for user {} with '
                    'recommendations {}'.format(user, recommendations))

    except Exception:
        logger.exception('Exception while getting user recommendations '
                         'for user {}'.format(user))

        response = app.response_class(json.dumps({'status': 'failure',
                                                  'user': user}),
                                      status='INTERNAL SERVER ERROR',
                                      mimetype='application/json')

    return response


def init_logging():
    try:
        logging.basicConfig(filename='subber.log', level=logging.DEBUG,
                            format='%(asctime)-26s %(name)-17s '
                                   '%(levelname)-8s %(message)s', filemode='a')

        # Suppress outside loggers
        logging.getLogger('prawcore').setLevel(logging.WARNING)
        logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
        logging.getLogger('wekzeug').setLevel(logging.WARNING)

    except Exception as e:
        exit('Unable to initiate logging because of: \n{}'.format(e))


def init_session():
    """Init Reddit API session"""
    return reddit.Reddit().get_session()


init_logging()
session = init_session()
