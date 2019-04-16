"""
    Config Docstring
    Different configs...
    logging
    sqlalchemy
    spotify
"""
# logger.info(f"Cached token expires at {time.strftime('%c', time.localtime(self.token_info['expires_at']))}", exc_info=True)

import logging
import logging.config
import os

import yaml

from dotenv import load_dotenv

#TODO: add
# import logmatic


load_dotenv()


with open('log config.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
# This might not log other files correctly
logger = logging.getLogger(__name__)


# base_dir = os.path.abspath(os.path.dirname(__file__))

# class Config(object):
#     """
#         SqlALchemy config
#     """
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
#         'sqlite:///' + os.path.join(basedir, 'app.db')
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     MAIL_SERVER = os.environ.get('MAIL_SERVER')
#     MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
#     MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
#     MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
#     MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
#     ADMINS = ['your-email@example.com']

#     POSTS_PER_PAGE = 3
