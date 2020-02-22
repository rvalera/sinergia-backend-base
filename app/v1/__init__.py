from flask import Blueprint
from flask_restplus import Api
# from .exceptions import ValidationException
from app import redis_client, jwt, babel
import json
from app.exceptions.base import SinergiaException
from flask.globals import request
from flask_babel import gettext

v1_blueprint = Blueprint('v1_blueprint', __name__,template_folder='/templates')
v1_api = Api(v1_blueprint,
             title='CryptoPOS API',
             version='1.0',
             description='OpenAPI to CryptoPOS Service')

from app.v1.resources.base import member_ns
from app.v1.resources.application import application_ns
from app.v1.resources.transaction import transaction_ns
from app.v1.resources.affiliate import affiliate_ns 

# pybabel extract -o locale/base.pot  .
# pybabel init -i base.pot -d translations -l en
# pybabel compile -d app/translations

LANGUAGES = {
    'en': 'English',
    'es': 'Español'
}

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())


@v1_blueprint.errorhandler(SinergiaException)
def custom_handler_exception(e):
    return {'ok': 0, 'message': {'code': e.code, 'text': e.text} } , 400
    
@jwt.expired_token_loader
def handle_expired_signature_error(e):
    return {'ok': 0, 'message': {'code': 'ESEC001', 'text': 'Token expired'} }, 401

@jwt.invalid_token_loader
@jwt.revoked_token_loader
@jwt.unauthorized_loader
def handle_invalid_token_error(e):
    return {'ok': 0, 'message': {'code': 'ESEC002', 'text': 'Token incorrect, supplied or malformed'} }, 401

@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    jti = decrypted_token['jti']
    entry = redis_client.get(jti)
    if entry is None:
        return True
    json_entry = json.loads(entry)
    return 'session_expired' in json_entry  and json_entry['session_expired'] == 'true'


@v1_blueprint.app_errorhandler(404)
def error_handler_404(error):
    return {'ok': 0, 'message': {'code': 'E404', 'text': 'Path not Found!' } }, 404

@v1_blueprint.app_errorhandler(500)
def error_handler_500(error):
    return {'ok': 0, 'message': {'code': 'E500', 'text': 'Internal Server Error -> %s' % str(error) } }, 500


v1_api.add_namespace(member_ns)
v1_api.add_namespace(application_ns)
v1_api.add_namespace(transaction_ns)
v1_api.add_namespace(affiliate_ns)
