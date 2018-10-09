# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import logging

import flask

from subber import config, reddit

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

    logger.info('Received recommendation request '
                'for user {0}'.format(user))

    # Make sure user exists
    try:
        logger.info('User {} tested for existence'.format(user))
        redditor = session.redditor(user)
        hasattr(redditor, 'created')
    except reddit.prawcore.exceptions.NotFound:
        logger.error('Unable to fetch recommendations for {} - '
                     'user does not exist'.format(user))
        response = flask.render_template('invalid-user.html', user=user)
        return response

    # Get recommendations
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
    cfg = config.get_config()
    return reddit.Reddit(cfg['id'],
                         cfg['secret'],
                         cfg['password'],
                         cfg['username']).get_session()


init_logging()
session = init_session()
