import configparser
import logging


def get_config():
    """Return dictionary containing Subber config values"""
    CONFIG_FILE = 'subber.cfg'

    def validate_config(cfg):
        """Validates the cfg file and throws an exception if config is formatted
        incorrectly or missing data.

        Keyword arguments:
        cfg -- the config file to validate
        """
        # Required opt groups
        ID = 'id'
        SECRET = 'secret'
        PASSWORD = 'password'
        USERNAME = 'username'
        reddit_api_opts = [ID, SECRET, PASSWORD, USERNAME]

        # Required sections
        REDDIT_API = 'reddit-api'
        required_sections = {REDDIT_API: reddit_api_opts}

        # Validate required sections contain required opts
        for section, opts in required_sections.items():
            for opt in opts:
                if not config.has_option(section, opt):
                    logging.exception('Missing required config option "{}"'
                                      ' in section "{}"'.format(
                                          opt, section))
                    raise Exception('Required config option "{}" in section '
                                    '"{}" missing from config file '
                                    '"{}"'.format(opt, section, CONFIG_FILE))

    # Load config
    try:
        config = configparser.RawConfigParser()
        config.readfp(open(CONFIG_FILE))
    except Exception:
        logging.exception('Error encountered while loading config file \n')
        raise Exception('Config file not found. Please add a config file '
                        '"{}" to the subber directory.'.format(CONFIG_FILE))

    # Validate config
    validate_config(config)

    return config
