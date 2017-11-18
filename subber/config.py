import configparser
import os

def get_config():
    """Return dictionary containing Subber connfig values"""
    config = configparser.ConfigParser()
    config.readfp(open('subber.cfg'))

    return config
