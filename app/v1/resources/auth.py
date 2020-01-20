from flask import current_app, request, jsonify
from flask_restplus import Resource, Namespace, fields
# from ..models.user import User
# from ..models.auth import RefreshToken
from app import db, redis_client
from app.v1 import v1_api
# from ..exceptions import ValidationException
import re
import jwt
import datetime
import hashlib
from flask_jwt_extended.utils import create_access_token, create_refresh_token,\
    get_jti, get_raw_jwt, get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required,\
    jwt_refresh_token_required
from ..use_cases.security import AuthenticateUseCase
import json
import requests
from requests.auth import HTTPBasicAuth
from ..repository.base import CacheRepository
from ..use_cases.wallet import DashboardUseCase
from app.exceptions.base import SinergiaException, ProxyCredentialsNotFound


member_ns = v1_api.namespace('member', description='Member Services')

mLogin = v1_api.model('Login', {
    'username': fields.String(required=True, description='User Name '),
    'password': fields.String(required=True, description='Password User')
})

mTokenPair = v1_api.model('TokenPair', {
    'access_token': fields.String(description='Access Token '),
    'refresh_token': fields.String(description='Refresh Token')
})

mRefreshToken = v1_api.model('RefreshToken', {
    'refresh_token': fields.String(required=True, description='Refresh Token')
}) 

mAccessToken = v1_api.model('AccessToken', {
    'access_token': fields.String(required=True, description='Access Token')
}) 

# request_payload =  {"start_date" : "2019-12-01", "end_date" : "2019-12-08"}

# mDateRange = v1_api.model('DateRange', {
#     'start_date': fields.String(description='Start Date - fmt(YYYY-MM-DD) '),
#     'end_date': fields.String(description='End Date - fmt(YYYY-MM-DD)')
# }) 

mMessage = v1_api.model('Message', {
    'code': fields.String(description='Message Code'),
    'text': fields.String(description='Message Text')
}) 

secureHeader = v1_api.parser()
secureHeader.add_argument('Authorization', type=str,location='headers',help='Bearer Access Token',required=True)
secureHeader.add_argument('Accept-Language', type=str,location='headers',help="en-US,en;q=0.5")

publicHeader = v1_api.parser()
publicHeader.add_argument('Accept-Language', type=str,location='headers',help="en-US,en;q=0.5")

queryParams = v1_api.parser()
queryParams.add_argument('filter',type=str,  help='{"stringParamName" : "stringParamValue","numericParamName" : numericParamValue}', location='args')


ACCESS_EXPIRES = 300
REFRESH_EXPIRES = 86400


@member_ns.route('/login')
@v1_api.expect(publicHeader)
class MemberLoginResource(Resource):

    @member_ns.doc('Make Login in Application')
    @member_ns.expect(mLogin)
    @member_ns.marshal_with(mTokenPair, code=200)
    def post(self):
        data = request.json

        username = data['username']
        password = data['password']        
        
        securityElement = AuthenticateUseCase().execute(username, password)
        if securityElement == None:
            return jsonify({"msg": "Bad username or password"}), 401

        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
    
        # Store the tokens in redis with a status of not currently revoked. We
        # can use the `get_jti()` method to get the unique identifier string for
        # each token. We can also set an expires time on these tokens in redis,
        # so they will get automatically removed after they expire. We will set
        # everything to be automatically removed shortly after the token expires0
        access_jti = get_jti(encoded_token=access_token)
        refresh_jti = get_jti(encoded_token=refresh_token)
        
        payload = { "session_expired" : "false", "username" : username, "password": password }
        
        redis_client.set(access_jti, json.dumps(payload), int(ACCESS_EXPIRES * 1.2))
        redis_client.set(refresh_jti, json.dumps(payload), int(REFRESH_EXPIRES * 1.2))

        # Use create_access_token() and create_refresh_token() to create our
        # access and refresh tokens
        ret = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        return ret,200

@member_ns.route('/logout')
@v1_api.expect(secureHeader)
class MemberLogoutResource(Resource):

    @member_ns.doc('Make Logout Application')
    @member_ns.expect(mRefreshToken)
    @member_ns.marshal_with(mMessage, code=200)
    @jwt_required    
    def post(self):
        data = request.json
        refresh_token = data['refresh_token']

        access_token_jti = get_raw_jwt()['jti']
        refresh_token_jti = get_jti(refresh_token)

        if redis_client.get(access_token_jti):
            payload = redis_client.get(access_token_jti)
            json_payload = json.loads(payload)
            json_payload["session_expired"] = 'true' 
            redis_client.set(access_token_jti, json.dumps(json_payload), int(ACCESS_EXPIRES * 1.2))
        else:
            redis_client.set(access_token_jti, json.dumps({"session_expired" : 'true'}), int(ACCESS_EXPIRES * 1.2))            

        if redis_client.get(refresh_token_jti):
            payload = redis_client.get(refresh_token_jti)
            json_payload = json.loads(payload)
            json_payload["session_expired"] = 'true' 
            redis_client.set(refresh_token_jti, json.dumps(json_payload), int(ACCESS_EXPIRES * 1.2))
        else:
            redis_client.set(refresh_token_jti, json.dumps({"session_expired" : 'true'}), int(ACCESS_EXPIRES * 1.2))            

        return {'code' : 'I001','text': 'OK'},200
    

@member_ns.route('/token/refresh')
@v1_api.expect(secureHeader)
class TokenRefreshResource(Resource):

    @member_ns.doc('Refresh Token')
    @member_ns.marshal_with(mTokenPair, code=200)
    @jwt_refresh_token_required
    def post(self):
        username = get_jwt_identity()

        refresh_token_jti = get_raw_jwt()['jti']
        
        access_token = create_access_token(identity=username)
        access_jti = get_jti(encoded_token=access_token)

        payload = redis_client.get(refresh_token_jti)
        json_payload = json.loads(payload)
        json_payload['session_expired'] = 'false'
        redis_client.set(access_jti, json.dumps(json_payload), int(ACCESS_EXPIRES * 1.2))
        
        data = { 'access_token': access_token, 
                 'refresh_token': None }
        return data, 200


class ProxySecureResource(Resource):

    def check_credentials(self):
        access_token_jti = get_raw_jwt()['jti']
        security_credentials = CacheRepository().getByKey(access_token_jti)
        if security_credentials == None:
            raise ProxyCredentialsNotFound()
        return security_credentials


@member_ns.route('/test')
@v1_api.expect(publicHeader)
class TestResource(Resource):
     
    @member_ns.doc('Test')
    def get(self):
        raise SinergiaException()

from app.v1.resources.wallet import *  


# auth_ns = Namespace('auth')
# 
# register_model = v1_api.model('Register', {
#     'username': fields.String(required=True),
#     'password': fields.String(required=True)
# })
# 
# return_token_model = v1_api.model('ReturnToken', {
#     'access_token': fields.String(required=True),
#     'refresh_token': fields.String(required=True)
# })


# @auth_ns.route('/register')
# class Register(Resource):
#     # 4-16 symbols, can contain A-Z, a-z, 0-9, _ (_ can not be at the begin/end and can not go in a row (__))
#     USERNAME_REGEXP = r'^(?![_])(?!.*[_]{2})[a-zA-Z0-9._]+(?<![_])$'
# 
#     # 6-64 symbols, required upper and lower case letters. Can contain !@#$%_  .
#     PASSWORD_REGEXP = r'^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])[\w\d!@#$%_]{6,64}$'
# 
#     @auth_ns.expect(register_model, validate=True)
#     @auth_ns.marshal_with(User.user_resource_model)
#     @auth_ns.response(400, 'username or password incorrect')
#     def post(self):
#         if not re.search(self.USERNAME_REGEXP, v1_api.payload['username']):
#             raise ValidationException(error_field_name='username',
#                                       message='4-16 symbols, can contain A-Z, a-z, 0-9, _ \
#                                       (_ can not be at the begin/end and can not go in a row (__))')
# 
#         if not re.search(self.PASSWORD_REGEXP, v1_api.payload['password']):
#             raise ValidationException(error_field_name='password',
#                                       message='6-64 symbols, required upper and lower case letters. Can contain !@#$%_')
# 
#         if User.query.filter_by(username=v1_api.payload['username']).first():
#             raise ValidationException(error_field_name='username', message='This username is already exists')
# 
#         user = User(username=v1_api.payload['username'], password=v1_api.payload['password'])
#         db.session.add(user)
#         db.session.commit()
#         return user


# @auth_ns.route('/login')
# class Login(Resource):
#     
#     @auth_ns.expect(register_model)
#     @auth_ns.response(200, 'Success', return_token_model)
#     @auth_ns.response(401, 'Incorrect username or password')
#     def post(self):
#         """
#         Look implementation notes
#         This API implemented JWT. Token's payload contain:
#         'uid' (user id),
#         'exp' (expiration date of the token),
#         'iat' (the time the token is generated)
#         """
#         user = User.query.filter_by(username=v1_api.payload['username']).first()
#         if not user:
#             auth_ns.abort(401, 'Incorrect username or password')
# 
#         from werkzeug.security import check_password_hash
#         if check_password_hash(user.password_hash, v1_api.payload['password']):
#             _access_token = jwt.encode({'uid': user.id,
#                                         'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
#                                         'iat': datetime.datetime.utcnow()},
#                                        current_app.config['SECRET_KEY']).decode('utf-8')
#             _refresh_token = jwt.encode({'uid': user.id,
#                                          'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30),
#                                          'iat': datetime.datetime.utcnow()},
#                                         current_app.config['SECRET_KEY']).decode('utf-8')
# 
#             user_agent_string = request.user_agent.string.encode('utf-8')
#             user_agent_hash = hashlib.md5(user_agent_string).hexdigest()
# 
#             refresh_token = RefreshToken.query.filter_by(user_agent_hash=user_agent_hash).first()
# 
#             if not refresh_token:
#                 refresh_token = RefreshToken(user_id=user.id, refresh_token=_refresh_token,
#                                              user_agent_hash=user_agent_hash)
#             else:
#                 refresh_token.refresh_token = _refresh_token
# 
#             db.session.add(refresh_token)
#             db.session.commit()
#             return {'access_token': _access_token, 'refresh_token': _refresh_token}, 200
# 
#         auth_ns.abort(401, 'Incorrect username or password')


# @auth_ns.route('/refresh')
# class Refresh(Resource):
#     @auth_ns.expect(v1_api.model('RefreshToken', {'refresh_token': fields.String(required=True)}), validate=True)
#     @auth_ns.response(200, 'Success', return_token_model)
#     def post(self):
#         _refresh_token = v1_api.payload['refresh_token']
# 
#         try:
#             payload = jwt.decode(_refresh_token, current_app.config['SECRET_KEY'])
# 
#             refresh_token = RefreshToken.query.filter_by(user_id=payload['uid'], refresh_token=_refresh_token).first()
# 
#             if not refresh_token:
#                 raise jwt.InvalidIssuerError
# 
#             # Generate new pair
# 
#             _access_token = jwt.encode({'uid': refresh_token.user_id,
#                                         'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
#                                         'iat': datetime.datetime.utcnow()},
#                                        current_app.config['SECRET_KEY']).decode('utf-8')
#             _refresh_token = jwt.encode({'uid': refresh_token.user_id,
#                                          'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30),
#                                          'iat': datetime.datetime.utcnow()},
#                                         current_app.config['SECRET_KEY']).decode('utf-8')
# 
#             refresh_token.refresh_token = _refresh_token
#             db.session.add(refresh_token)
#             db.session.commit()
# 
#             return {'access_token': _access_token, 'refresh_token': _refresh_token}, 200
# 
#         except jwt.ExpiredSignatureError as e:
#             raise e
#         except (jwt.DecodeError, jwt.InvalidTokenError)as e:
#             raise e
#         except:
#             auth_ns.abort(401, 'Unknown token error')


# from ..utils import token_required


# # This resource only for test
# @auth_ns.route('/protected')
# class Protected(Resource):
#     @token_required
#     def get(self, current_user):
#         return {'i am': 'protected', 'uid': current_user.id}
