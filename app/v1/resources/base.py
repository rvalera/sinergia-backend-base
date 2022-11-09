from flask import current_app, request, jsonify
from flask_restplus import Resource, Namespace, fields
from app import db, redis_client
from app.v1 import v1_api
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
from app.exceptions.base import SinergiaException, ProxyCredentialsNotFound

from app.v1.use_cases.security import   MemberInitSignUpUseCase,\
    MemberFinishRegisterUseCase, GetMemberProfileUseCase,\
    UpdateMemberProfileUseCase, ChangePasswordMemberUseCase,\
    ResetPasswordMemberUseCase, GetAnyMemberProfileUseCase,\
    GetDetailedMemberProfileUseCase, GetUserByNameUseCase

from app.v1.models.constant import STATUS_ACTIVE, STATUS_GENERATED,\
    STATUS_PENDING

from app.tools.sqlalchemy import entity_as_dict
from app.tools.response_tools import make_template_response

member_ns = v1_api.namespace('member', description='Security Services')

mLogin = v1_api.model('Login', {
    'username': fields.String(required=True, description='User Name '),
    'password': fields.String(required=True, description='Password User')
})

mMemberInitRegister = v1_api.model('MemberInitRegister', {
    'email': fields.String(required=True, description='Email'),
    'first_name': fields.String(required=True, description='First Name'),
    'last_name': fields.String(required=True, description='Last Name')
})

mMemberFinishRegister = v1_api.model('MemberFinishRegister', {
    'phone_number': fields.String(required=True, description='Phone Number'),
    'gender': fields.String(required=True, description='Gender'),
    'secondary_email': fields.String(required=True, description='Secondary email'),
    'birth_date': fields.String(required=True, description='Birth Date'),
    'operation_key': fields.String(required=True, description='Operation Key of Operations'),
    'password': fields.String(required=True, description='New Password')
})

mMemberEmail = v1_api.model('MemberEmail', {
    'email': fields.String(required=True, description='Email')
})

mUserExtraInfo = v1_api.model('User Extra Info', { 
    'username': fields.String(description='Username'),
    'status': fields.String(description='Status') 
})

mLoginInfo = v1_api.model('Login Info', {
    'access_token': fields.String(description='Access Token '),
    'refresh_token': fields.String(description='Refresh Token'),
    'extra_info' : fields.Nested(mUserExtraInfo)
})

mResultLogin = v1_api.model('Result Login', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'data' : fields.Nested(mLoginInfo)
}) 

mTokenPair = v1_api.model('TokenPair', {
    'access_token': fields.String(description='Access Token '),
    'refresh_token': fields.String(description='Refresh Token')
})

mResultTokens = v1_api.model('Result Token', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'data' : fields.Nested(mTokenPair)
}) 

mRefreshToken = v1_api.model('RefreshToken', {
    'refresh_token': fields.String(required=True, description='Refresh Token')
}) 

mAccessToken = v1_api.model('AccessToken', {
    'access_token': fields.String(required=True, description='Access Token')
}) 

mMessage = v1_api.model('Message', { 
    'code': fields.String(description='Message Code'),
    'text': fields.String(description='Message Text') 
})

mResult = v1_api.model('Generic Result', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'message' : fields.Nested(mMessage)
}) 

mChangePassword = v1_api.model('ChangePassword', {
    'old_password': fields.String(required=True, description='Old Password'),
    'new_password': fields.String(required=True, description='New Password'),
})

# BankStruct = v1_api.model('BankStruct', { 
#     'id': fields.String(attribute='id'),
#     'name': fields.String(attribute='name'),
#     'account_number': fields.String(attribute='account_number'),
# }) 

UpdateProfileUserStruct = v1_api.model('UpdateProfileUserStruct', {
    'first_name': fields.String(required=True, description='First Name'),
    'last_name': fields.String(required=True, description='Last Name'),
    'phone_number': fields.String(required=True, description='Phone Number'),
    'gender': fields.String(required=True, description='Gender'),
    'secondary_email': fields.String(required=True, description='Secondary email'),
    'birth_date': fields.String(required=True, description='Birth Date'),
})


ProfileRolStruct = v1_api.model('ProfileRolStruct', { 
    'id' : fields.Integer(), 
    'name' : fields.String(), 
})


ProfileUserStruct = v1_api.model('ProfileUserStruct', { 
    'id': fields.String(attribute='id'),
    'id_number': fields.String(attribute='person_extension.id_number'),
    'first_name': fields.String(attribute='person_extension.first_name'),
    'last_name': fields.String(attribute='person_extension.last_name'),
    'fullname': fields.String(attribute='person_extension.fullname'),
    'email': fields.String(attribute='person_extension.email'),
    'gender': fields.String(attribute='person_extension.gender'),
    'address': fields.String(attribute='person_extension.address'),
    'phone_number': fields.String(attribute='person_extension.phone_number'),

    'roles' : fields.Nested(ProfileRolStruct,attribute='roles'),
    # 'bank' : fields.Nested(BankStruct,attribute='person_extension.bank')
}) 

GetProfileUserStruct = v1_api.model('GetProfileUserStruct', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'data' : fields.Nested(ProfileUserStruct,attribute='data')
}) 

DateRangeStruct = v1_api.model('DateRangeStruct', { 
    'from': fields.String(description='From'),
    'to': fields.String(description='To') 
})

secureHeader = v1_api.parser()
secureHeader.add_argument('Authorization', type=str,location='headers',help='Bearer Access Token',required=True)
secureHeader.add_argument('Accept-Language', type=str,location='headers',help="en-US,en;q=0.5")

publicHeader = v1_api.parser()
publicHeader.add_argument('Accept-Language', type=str,location='headers',help="en-US,en;q=0.5")

queryParams = v1_api.parser()
queryParams.add_argument('filter',type=str,  help='{"stringParamName" : "stringParamValue","numericParamName" : numericParamValue}', location='args')
queryParams.add_argument('order',type=str, location='args', help='["field1","field2 ASC","field3 DESC"]')
queryParams.add_argument('range',type=str, location='args', help='[low,high]')

from werkzeug import FileStorage

uploadFilePublicHeader = v1_api.parser()
uploadFilePublicHeader.add_argument('Accept-Language', type=str,location='headers',help="en-US,en;q=0.5")
uploadFilePublicHeader.add_argument('file', location='files', type=FileStorage, required=True)

uploadFileSecureHeader = v1_api.parser()
uploadFileSecureHeader.add_argument('Authorization', type=str,location='headers',help='Bearer Access Token',required=True)
uploadFileSecureHeader.add_argument('Accept-Language', type=str,location='headers',help="en-US,en;q=0.5")
uploadFileSecureHeader.add_argument('file', location='files', type=FileStorage, required=True)

ACCESS_EXPIRES = 86400
REFRESH_EXPIRES = 172800

@member_ns.route('/login')
@v1_api.expect(publicHeader)
class MemberLoginResource(Resource):

    @member_ns.doc('Make Login in Application')
    @member_ns.expect(mLogin)
#     @member_ns.marshal_with(mResultLogin)
#     @member_ns.marshal_with(mResult, code=401,description='Error')
    def post(self):
        data = request.json

        username = data['username']
        password = data['password']        
        
        securityElement = AuthenticateUseCase().execute(username, password)
        if securityElement == None:
            error =  { 'ok' : 0, 
                       'message' : { 
                           'code' : 'ESEC000',
                           'text': "Bad username or password"
                        } 
                      }
            return error, 401
        
        if not securityElement.status in (STATUS_ACTIVE,STATUS_PENDING) : 
            error =  { 'ok' : 0, 
                'message' : { 
                    'code' : 'ESEC000',
                    'text': "Locked User or Not Finished Register"
                } 
                }
            return error, 401

        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
    
        # Store the tokens in redis with a status of not currently revoked. We
        # can use the `get_jti()` method to get the unique identifier string for
        # each token. We can also set an expires time on these tokens in redis,
        # so they will get automatically removed after they expire. We will set
        # everything to be automatically removed shortly after the token expires0
        access_jti = get_jti(encoded_token=access_token)
        refresh_jti = get_jti(encoded_token=refresh_token)
        
        
        payload = { "session_expired" : "false", "username" : username, "password": password, "id" : securityElement.id }
        user = GetUserByNameUseCase().execute(payload)
        # if user.status == STATUS_ACTIVE:
        #     # person = GetMemberProfileUseCase().execute(payload,{})
        #     # payload['person_id'] = person['data']['id']
        #     payload['person_id'] = None            
        #     payload['person_extension_id'] = user.person_extension_id
        # else:
        #     payload['person_id'] = None            
        #     payload['person_extension_id'] = user.person_extension_id

        payload['person_id'] = username
        payload['person_extension_id'] = user.person_extension_id

        redis_client.set(access_jti, json.dumps(payload), ex=int(ACCESS_EXPIRES * 1.2))
        redis_client.set(refresh_jti, json.dumps(payload), ex=int(REFRESH_EXPIRES * 1.2))

        userTokens = {'access_token' : access_jti,'refresh_token': refresh_jti}
        redis_client.set(username, json.dumps(userTokens), ex=int(REFRESH_EXPIRES * 1.2))

        # Use create_access_token() and create_refresh_token() to create our
        # access and refresh tokens
        ret = { 'ok': 1,
            'data': {
                'extra_info' : {
                    'username' : username,
                    'status' : securityElement.status,
                },
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }
        return ret,200


@member_ns.route('/logout')
@v1_api.expect(secureHeader)
class MemberLogoutResource(Resource):

    @member_ns.doc('Make Logout Application')
    @member_ns.expect(mRefreshToken)
    @member_ns.marshal_with(mResult, code=200)
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
            redis_client.set(access_token_jti, json.dumps(json_payload), ex=int(ACCESS_EXPIRES * 1.2))
        else:
            redis_client.set(access_token_jti, json.dumps({"session_expired" : 'true'}), ex=int(ACCESS_EXPIRES * 1.2))            

        if redis_client.get(refresh_token_jti):
            payload = redis_client.get(refresh_token_jti)
            json_payload = json.loads(payload)
            json_payload["session_expired"] = 'true' 
            redis_client.set(refresh_token_jti, json.dumps(json_payload), ex=int(ACCESS_EXPIRES * 1.2))
        else:
            redis_client.set(refresh_token_jti, json.dumps({"session_expired" : 'true'}), ex=int(ACCESS_EXPIRES * 1.2))            

        return { 'ok' : 1, 
                'message' : { 
                    'code' : 'I001',
                    'text': 'OK'
                } 
                },200
    

@member_ns.route('/token/refresh')
@v1_api.expect(secureHeader)
class TokenRefreshResource(Resource):

    @member_ns.doc('Refresh Token')
    @member_ns.marshal_with(mResultTokens, code=200)
    @jwt_refresh_token_required
    def post(self):
        refresh_token_jti = get_raw_jwt()['jti']

        username = get_jwt_identity()
        access_token = create_access_token(identity=username)
        access_jti = get_jti(encoded_token=access_token)

        cacheRepository = CacheRepository()
        payload = cacheRepository.getByKey(refresh_token_jti)

        user = GetUserByNameUseCase().execute(payload)
        if user.status == STATUS_ACTIVE:
            # person = GetMemberProfileUseCase().execute(payload,{})
            # payload['person_id'] = person['data']['id']
            # payload['person_extension_id'] = person['data']['person_extension_id']
            payload['person_id'] = username            
            payload['person_extension_id'] = user.person_extension_id
        else:           
            error =  { 
                'ok' : 0, 
                'message' : { 
                    'code' : 'ESEC000',
                    'text': "Locked User or Not Finished Register"
                } 
            }
            return error, 401            

        payload['session_expired'] = 'false'

        cacheRepository.save(refresh_token_jti, payload, expired_time = int(REFRESH_EXPIRES * 1.2))
        cacheRepository.save(access_jti, payload, expired_time = int(ACCESS_EXPIRES * 1.2))

        userTokens = cacheRepository.getByKey(username)
        userTokens['access_token'] = access_jti
        userTokens['refresh_token'] = refresh_token_jti
        cacheRepository.save(username,userTokens, expired_time = int(REFRESH_EXPIRES * 1.2))

        data = { 'ok': 1,
                'data': { 
                    'access_token': access_token, 
                    'refresh_token': refresh_token_jti 
                    }
                }
        return data, 200


class ProxySecureResource(Resource):
    
    def syncronizePasswordCache(self,password):
        access_token_jti = get_raw_jwt()['jti']
        cacheRepository = CacheRepository()
        cache_payload = cacheRepository.getByKey(access_token_jti)

        cache_payload['password'] = password

        user = GetUserByNameUseCase().execute(cache_payload)
        username = cache_payload['username']

        if user.status == STATUS_ACTIVE:
            # person = GetMemberProfileUseCase().execute(cache_payload,{})
            # cache_payload['person_id'] = person['data']['id']
            # cache_payload['person_extension_id'] = person['data']['person_extension_id']
            cache_payload['person_id'] = username            
            cache_payload['person_extension_id'] = user.person_extension_id
    
        cacheRepository.save(access_token_jti,cache_payload, expired_time = int(ACCESS_EXPIRES * 1.2))

        userTokens = cacheRepository.getByKey(username)
        refresh_token_jti = userTokens['refresh_token'] 
        
        cacheRepository.save(refresh_token_jti,cache_payload, expired_time = int(REFRESH_EXPIRES * 1.2))
        
    
    def checkCredentials(self):
        access_token_jti = get_raw_jwt()['jti']
        security_credentials = CacheRepository().getByKey(access_token_jti)
        # This is used for check if the Signup is Finished
        # if security_credentials == None or (not 'person_id' in security_credentials) or ('person_id' in security_credentials and security_credentials['person_id'] is None):
        #     raise ProxyCredentialsNotFound()
        if security_credentials == None or (not 'person_extension_id' in security_credentials) or ('person_extension_id' in security_credentials and security_credentials['person_extension_id'] is None):
            raise ProxyCredentialsNotFound()
        return security_credentials

    def checkForFinishSignup(self):
        access_token_jti = get_raw_jwt()['jti']
        security_credentials = CacheRepository().getByKey(access_token_jti)
        # This is used for check if the Signup is Finished
        # if not ('person_id' in security_credentials and security_credentials['person_id'] is None):
        #     raise ProxyCredentialsNotFound()
        if ('person_extension_id' in security_credentials) and  (security_credentials['person_extension_id'] is None):
            raise ProxyCredentialsNotFound()
        return security_credentials    


@member_ns.route('/signup')
@v1_api.expect(publicHeader)
class MemberInitSignupResource(Resource):
     
    @member_ns.doc('Member Register (Step-1)')
    @member_ns.expect(mMemberInitRegister)
    @member_ns.marshal_with(mResult, code=200)
    def post(self):
        payload = request.json
        data = MemberInitSignUpUseCase().execute(payload)
        return  { 'ok': 1 } , 200
        

@member_ns.route('/signup/finish')
@v1_api.expect(secureHeader)
class MemberFinishSignupResource(ProxySecureResource):
     
    @member_ns.doc('Member Register (Step-2)')
    @member_ns.expect(mMemberFinishRegister)
    @member_ns.marshal_with(mResult, code=200)
    @jwt_required    
    def put(self):
        security_credentials = self.checkForFinishSignup()
        payload = request.json
        payload['id'] = security_credentials['id']        
        payload['username'] = security_credentials['username']
        data = MemberFinishRegisterUseCase().execute(security_credentials, payload)
        self.syncronizePasswordCache(payload['password'])
        return  { 'ok': 1 } , 200


@member_ns.route('/profile')
@v1_api.expect(secureHeader)
class MemberProfileResource(ProxySecureResource): 
 
    @member_ns.doc('Member Profile')
    @jwt_required   
    @v1_api.marshal_with(GetProfileUserStruct) 
    def get(self):
        security_credentials = self.checkCredentials()
        query_params = {}
        data = GetDetailedMemberProfileUseCase().execute(security_credentials,query_params)
        # return make_template_response(data, 'json/member/get.json'), 200
        return {'ok' : 1, 'data': data },200

    @member_ns.doc('Update Member Profile')
    @v1_api.expect(UpdateProfileUserStruct)
    @jwt_required    
    def put(self):
        payload = request.json        
        security_credentials = self.checkCredentials()
        payload['id'] = security_credentials['id']
        UpdateMemberProfileUseCase().execute(security_credentials,payload)
        return  { 'ok': 1 }, 200

@member_ns.route('/profile/<email>')
@member_ns.param('email', 'Email Member')
@v1_api.expect(secureHeader)
class GetAnyMemberProfileResource(ProxySecureResource): 

    @member_ns.doc('Get Any Member Profile')
    @jwt_required    
    @v1_api.marshal_with(GetProfileUserStruct) 
    def get(self,email):
        security_credentials = self.checkCredentials()
        query_params = {'email': email}
        data = GetAnyMemberProfileUseCase().execute(security_credentials,query_params)
        return  {'ok' : 1, 'data': data }, 200


@member_ns.route('/password')
@v1_api.expect(secureHeader)
class ChangePasswordMemberResource(ProxySecureResource):
 
    @member_ns.doc('Change Password')
    @v1_api.expect(mChangePassword)    
    @jwt_required    
    def put(self):
        user_payload = request.json
        security_credentials = self.checkCredentials()

        request_payload = { 'id': security_credentials['id'] ,
                   'password': user_payload['new_password'],
                   'old_password': user_payload['old_password']}
        ChangePasswordMemberUseCase().execute(security_credentials,request_payload)
        self.syncronizePasswordCache(user_payload['new_password'])
        return  { 'ok': 1 }, 200


@member_ns.route('/password/reset')
@v1_api.expect(publicHeader)
class ResetPasswordMemberResource(Resource):

    @member_ns.doc('Reset Password')
    @v1_api.expect(mMemberEmail)    
    def post(self):
        payload = request.json 
        request_payload = { 'password_type': 'U',  'email': payload['email']}
        data = ResetPasswordMemberUseCase().execute(request_payload)
        return  data, 200

