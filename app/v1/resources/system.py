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
from app.v1.resources.base import ProxySecureResource, secureHeader,queryParams, DateRangeStruct


from app.v1.models.constant import STATUS_ACTIVE, STATUS_GENERATED,\
    STATUS_PENDING

# from tools.json import AlchemyEncoder
from app.tools.sqlalchemy import entity_as_dict
from app.tools.response_tools import make_template_response

from app.v1.use_cases.admin import GetAdminMemberListUseCase,GetAdminMemberUseCase,\
    DeleteAdminMemberUseCase,CreateAdminMemberUseCase,SaveAdminMemberUseCase,GetRolListUseCase
from app.v1.use_cases.system import GetApplicationUseCase,SaveApplicationUseCase,ExecuteSyncUseCase,GetLastSyncStatusUseCase


system_ns = v1_api.namespace('system', description='System Services')

ApplicationStruct = v1_api.model('ApplicationStruct', { 
    'semanas_de_ajustes' : fields.Integer(), 
})


GetApplicationStruct = v1_api.model('GetApplicationStruct', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'data' : fields.Nested(ApplicationStruct,attribute='data')
}) 

@system_ns.route('/application')
@v1_api.expect(secureHeader)
class AdminMemberResource(ProxySecureResource): 

    @system_ns.doc('Application Attributes')
    @jwt_required    
    @v1_api.marshal_with(GetApplicationStruct) 
    def get(self):
        security_credentials = self.checkCredentials()
        data = GetApplicationUseCase().execute(security_credentials)
        return  {'ok':1, 'data': data} , 200

    @system_ns.doc('Update Application Attributes')
    @v1_api.expect(ApplicationStruct)    
    @jwt_required    
    def put(self):
        security_credentials = self.checkCredentials()
        payload = request.json        
        SaveApplicationUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200

@system_ns.route('/application/synchronize')
@v1_api.expect(secureHeader)
class SynchronizeResource(ProxySecureResource): 

    @system_ns.doc('Check Last Sync Process')
    @jwt_required
    def get(self):
        security_credentials = self.checkCredentials()
        data = GetLastSyncStatusUseCase().execute(security_credentials)
        return  {'ok':1, 'data': data} , 200

    @system_ns.doc('Execute Sync')
    @v1_api.expect(DateRangeStruct)    
    @jwt_required
    def post(self):
        security_credentials = self.checkCredentials()
        payload = request.json
        ExecuteSyncUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200
