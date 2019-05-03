"""
    App initialization.
"""


import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask.logging import create_logger
import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

shocal = Flask(__name__)
logger = create_logger(shocal)
shocal.config.from_object(Config)
db = SQLAlchemy(shocal)
migrate = Migrate(shocal, db)


if not shocal.debug:
    if shocal.config['MAIL_SERVER']:
        auth = None
    if shocal.config['MAIL_USERNAME'] or shocal.config['MAIL_PASSWORD']:
        auth = (shocal.config['MAIL_USERNAME']
                or shocal.config['MAIL_PASSWORD'])
        secure = None
        if shocal.config['MAIL_USE_TLS']:
            secure = ()
            mail_handler = SMTPHandler(mailhost=(shocal.config['MAIL_SERVER'],
                                                 shocal.config['MAIL_PORT']),
                                       fromaddr=f"no-reply@{shocal.config['MAIL_SERVER']}",
                                       toaddrs=shocal.config['ADMINS'],
                                       subject='Shocal Failure',
                                       credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler(
        'logs/flask_app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    
    logger.setLevel(logging.INFO)
    logger.info('Shocal startup')

from app import routes, models, errors