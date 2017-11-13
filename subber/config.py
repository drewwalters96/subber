import configparser, os

def get_config():
    config = configparser.ConfigParser()
    config.readfp(open('subber.cfg'))

    return config
