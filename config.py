import os
import tempfile
from configparser import ConfigParser
import pathlib
from app.tools.config import load_configuration_file

basedir = os.path.abspath(os.path.dirname(__file__))
configuration = load_configuration_file()

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = configuration.get('SECURITY','SECRET_KEY')
    JWT_SECRET_KEY = SECRET_KEY
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = configuration.get('DB','DATABASE_URI')
    
    REDIS_URL = configuration.get('REDIS','DATABASE_URI') 

    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
 
#     def __init__(self):
#         CONFIG_FILE = self.load_file()
#         self.SQLALCHEMY_DATABASE_URI = CONFIG_FILE.get('db','DATABASE_URI')
    

class DevelopmentConfig(Config):
    DEBUG = True
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db_dev.db')
# REDIS_URL = "redis://:password@localhost:6379/0"


class TestingConfig(Config):
    TESTING = True
# REDIS_URL = "redis://:password@localhost:6379/0"
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db_test.db')
    #SECRET_KEY = 'testing'
    # SQLALCHEMY_DATABASE_URI = 'sqlite://'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, tempfile.mktemp(dir='.', suffix='.db'))
    # tempfile.mktemp(dir=basedir, suffix='.db')


class ProductionConfig(Config):
    pass
#     DATABASE_URI = os.environ.get('DATABASE_URI')
#     SECRET_KEY = os.environ.get('SECRET_KEY')
#     JWT_SECRET_KEY = SECRET_KEY


config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig
}

