"""
    Different configs needed:
    logging
    sqlalchemy
    spotify
"""
# TODO: add import logmatic
import logging
import logging.config
import os
import yaml
from dotenv import load_dotenv

load_dotenv()

with open('log config.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
# This might not log other files correctly
logger = logging.getLogger(__name__)

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """
        Staging database configuration.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(base_dir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
