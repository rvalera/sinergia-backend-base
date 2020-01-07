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

from .wallet import *  

