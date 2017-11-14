import falcon, reddit

class Score:
    def on_get(self, req, resp, user):
        resp.media = reddit.Reddit().get_user_sub_score(user)

api = falcon.API()
api.add_route('/user/{user}', Score())
