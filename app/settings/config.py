import os, sys
import yaml
from dotenv import load_dotenv, find_dotenv
import logging

logger = logging.getLogger(__name__)

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

def get_config():
    config = None
    try:
        with open(os.path.join(os.path.dirname(__file__), "config.env.yml"), 'r') as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    except FileNotFoundError:
        logger.error("Ensure that you have provided a config.env.yml file in the settings folder")

    return config

### Currently only using information from the yml file
def get_env_variable(name):
    try:
        return os.environ.get(name)
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)

config = get_config()


class BaseConfig(object):
    """Parent configuration class."""

    DEBUG = config['postgres']['DEBUG']
    SECRET_KEY = config['postgres']['SECRET_KEY']
    SQLALCHEMY_TRACK_MODIFICATIONS = config['postgres']['SQLALCHEMY_TRACK_MODIFICATIONS']
    DB_HOST = config['postgres']['db_host']
    DATABASE_NAME = config['postgres']['db_name']
    DB_USERNAME = config['postgres']['db_username']
    DB_PASSWORD = config['postgres']['db_password']
    DB_PSQL_BASE_URI = config['postgres']['db_psql_base_uri']
    DB_URI = "%s://%s:%s@%s/%s" % (DB_PSQL_BASE_URI, DB_USERNAME, DB_PASSWORD, DB_HOST, DATABASE_NAME)
    SQLALCHEMY_DATABASE_URI = "%s://%s:%s@%s/%s" % (DB_PSQL_BASE_URI, DB_USERNAME, DB_PASSWORD, DB_HOST, DATABASE_NAME)
 