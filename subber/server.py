import falcon, reddit

class Recommend:
    def on_get(self, req, resp, user):
        resp.media = reddit.Reddit().get_user_recommendations(user)

api = falcon.API()
api.add_route('/user/{user}', Recommend())
