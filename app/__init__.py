from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_redis.client import FlaskRedis
from flask_jwt_extended.jwt_manager import JWTManager
from flask_babel import Babel, get_locale
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from flask_alembic import Alembic
from flask_pymongo import PyMongo

import logging
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()
redis_client = FlaskRedis(strict=True)
jwt = JWTManager()
babel = Babel()
alembic = Alembic() 
mongodb = PyMongo()

def create_app(config_type='dev'):
    from config import config
    app = Flask(__name__)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    app.config.from_object(config[config_type])

    db.init_app(app)

    redis_client.init_app(app)

    jwt.init_app(app)

    babel.init_app(app)

    alembic.init_app(app)

    mongodb.init_app(app)
      
    handler = RotatingFileHandler('sinergia.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

    from .v1 import v1_blueprint
    app.register_blueprint(v1_blueprint, url_prefix='/api/v1')

    CORS(app, resources={r'/*': {'origins': '*'}})        

    return app
