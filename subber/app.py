import falcon
import reddit


class SessionMiddleware(object):
    def process_request(self, req, resp):
        """Add Reddit API session to request context

        Keyword arguments:
        req  -- request object to be routed to the request handler
        resp -- resp object to append response content

        Side effects:
        req -- API session added to request context
        """
        with reddit.Reddit() as session:
            req.context = {'session': session}


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
        session = req.context['session']

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

        except Exception as e:
            response = {'status': 'failure', 'user': user}
            resp.status = falcon.HTTP_500

        resp.media = response


api = falcon.API(middleware=[SessionMiddleware()])
api.add_route('/user/{user}', Recommend())
