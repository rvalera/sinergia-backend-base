from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_redis.client import FlaskRedis
from flask_jwt_extended.jwt_manager import JWTManager
from flask_babel import Babel, get_locale

db = SQLAlchemy()
redis_client = FlaskRedis(strict=True)
jwt = JWTManager()
babel = Babel()

def create_app(config_type='dev'):
    from config import config
    app = Flask(__name__)
    app.config.from_object(config[config_type])

    db.init_app(app)

    redis_client.init_app(app)

    jwt.init_app(app)

    babel.init_app(app)

    from .v1 import v1_blueprint
    app.register_blueprint(v1_blueprint, url_prefix='/api/v1')

    return app
