import configparser
import logging

logger = logging.getLogger(__name__)


def get_config():
    """Return dictionary containing Subber config values"""
    CONFIG_FILE = 'subber.cfg'

    def validate_config(cfg):
        """Validates the cfg file and throws an exception if config is formatted
        incorrectly or missing data.

        Keyword arguments:
        cfg -- the config file to validate
        """
        # Required reddit API opt groups
        ID = 'id'
        SECRET = 'secret'
        PASSWORD = 'password'
        USERNAME = 'username'
        reddit_api_opts = [ID, SECRET, PASSWORD, USERNAME]

        # Required recommendation system opt groups
        RECOMMEND_ACTIVES = 'recommend-actives'
        recommendation_system_opts = [RECOMMEND_ACTIVES]

        # Required sections
        REDDIT_API = 'reddit-api'
        RECOMMENDATION_SYSTEM = 'recommendation-system'
        required_sections = {REDDIT_API: reddit_api_opts,
                             RECOMMENDATION_SYSTEM: recommendation_system_opts}

        # Validate required sections contain required opts
        for section, opts in required_sections.items():
            for opt in opts:
                if not config.has_section(section):
                    logger.critical('Missing required config section "{}" in '
                                    'Subber config'.format(section))

                    raise RuntimeError('Subber config file not loaded.')

                if not config.has_option(section, opt):
                    logger.critical('Missing required config option "{}" in '
                                    'section "{}"'.format(opt, section))

                    raise RuntimeError('Subber config file not loaded.')

    # Load config
    try:
        config = configparser.RawConfigParser()
        with open(CONFIG_FILE) as cf:
            config.read_file(cf)
    except configparser.MissingSectionHeaderError:
        logger.critical('Improper config file format detected. No section '
                        'headers found')

        raise RuntimeError('Subber config file not loaded.')
    except Exception:
        logger.critical('Config file not found. Please add a config file "{}" '
                        'to the project directory.'.format(CONFIG_FILE))

        raise RuntimeError('Subber config file not loaded.')

    # Validate config
    validate_config(config)

    return config


def get_api_config():
    try:
        return get_config()['reddit-api']
    except KeyError as e:
        logger.critical('Could not load configuration for Reddit API. '
                        'Verify section "[reddit-api]" exists in Subber '
                        'config.')

        raise RuntimeError('Could not load configuration for Reddit API. '
                           'Verify section "[reddit-api]" exists in Subber '
                           'config.')


def get_recommendation_system_config():
    try:
        return get_config()['recommendation-system']
    except KeyError as e:
        message = ('Could not load configuration for Recommendation'
                   ' System. Verify section "[recommendation-system]" '
                   ' exists in Subber .config.')
        logger.critical(message)

        raise RuntimeError(message)
