import config, praw

class Subber(object):
    def __init__(self):
        # Load config
        cfg = config.get_config()

        # Load API wrapper
        api_cfg = self._get_api_cfg(cfg)
        api = self._get_api_wrapper(api_cfg)

    def _get_api_cfg(self, cfg):
        return cfg['reddit-api']

    def _get_api_wrapper(self, cfg):
        return praw.Reddit(client_id=cfg['id'], client_secret=cfg['secret'],
                           password=cfg['password'], user_agent='web app',
                           username=cfg['username'])

def run():
    app = Subber()

run()
