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
from app.v1.resources.base import ProxySecureResource, secureHeader,queryParams


from app.v1.models.constant import STATUS_ACTIVE, STATUS_GENERATED,\
    STATUS_PENDING

# from tools.json import AlchemyEncoder
from app.tools.sqlalchemy import entity_as_dict
from app.tools.response_tools import make_template_response

from app.v1.use_cases.admin import GetAdminMemberListUseCase,GetAdminMemberUseCase,\
    DeleteAdminMemberUseCase,CreateAdminMemberUseCase,SaveAdminMemberUseCase,GetRolListUseCase, SaveRolUseCase
from app.v1.resources.entities import EmpresaStruct, UpdateEmpresaStruct

admin_ns = v1_api.namespace('admin', description='Admin Services')

RolStruct = v1_api.model('RolStruct', { 
    'id' : fields.Integer(), 
    'name' : fields.String(), 
})

UpdateRolStruct = v1_api.model('UpdateRolStruct', { 
    'name': fields.String(),
    # 'privileges' : fields.List(fields.String()), 
}) 

ExtraInfoUserStruct = v1_api.model('ExtraInfoUserStruct', { 
    'id_number': fields.String(attribute='id_number'),
    'first_name': fields.String(attribute='first_name'),
    'last_name': fields.String(attribute='last_name'),
    'fullname': fields.String(attribute='fullname'),
    'email': fields.String(attribute='email'),
    'gender': fields.String(attribute='gender'),
    'address': fields.String(attribute='address'),
    'phone_number': fields.String(attribute='phone_number'),
    # #Datos Adicionales Creados para RRHH
    'empresa': fields.Nested(EmpresaStruct,attribute='empresa'),
}) 

AdminUserStruct = v1_api.model('AdminUserStruct', { 
    'id': fields.String(attribute='id'),
    'name': fields.String(attribute='name'),
    'roles' : fields.Nested(RolStruct,attribute='roles'),
    'extra_info': fields.Nested(ExtraInfoUserStruct,attribute='person_extension'),
}) 

UpdateExtraInfoUserStruct = v1_api.model('UpdateExtraInfoUserStruct', { 
    'id_number': fields.String(),
    'first_name': fields.String(),
    'last_name': fields.String(),
    'fullname': fields.String(),
    'email': fields.String(),
    'gender': fields.String(),
    'address': fields.String(),
    'phone_number': fields.String(),
    #Informacion Adicional Asociado al Usuario
    'empresa': fields.Nested(UpdateEmpresaStruct),
}) 

UpdateAdminUserStruct = v1_api.model('UpdateAdminUserStruct', { 
    'name': fields.String(),
    'password': fields.String(),
    'roles' : fields.List(fields.Integer()), #Listado de Ids de Roles
    'extra_info': fields.Nested(UpdateExtraInfoUserStruct),
}) 


GetAdminUserListStruct = v1_api.model('GetAdminUserListStruct', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'count' : fields.Integer(description='Count Row'), 
    'total' : fields.Integer(description='Total Row'), 
    'data' : fields.Nested(AdminUserStruct,attribute='data')
}) 


GetOneAdminUserStruct = v1_api.model('GetOneAdminUserStruct', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'data' : fields.Nested(AdminUserStruct,attribute='data')
}) 

GetRolListStruct = v1_api.model('GetRolListStruct', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'count' : fields.Integer(description='Count Row'), 
    'total' : fields.Integer(description='Total Row'), 
    'data' : fields.Nested(RolStruct,attribute='data')
}) 


@admin_ns.route('/member')
@v1_api.expect(secureHeader)
class AdminMemberResource(ProxySecureResource): 

    @admin_ns.doc('Admin Member')
    @v1_api.expect(queryParams)    
    @jwt_required    
    @v1_api.marshal_with(GetAdminUserListStruct) 
    def get(self):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}

        query_params = {}
        request_payload =  {}        
        if 'filter' in  request.args and request.args['filter']:
            filter = eval(request.args['filter'])
            request_payload = filter
            query_params['filter'] = request_payload

        if 'order' in  request.args and request.args['order']:
            order = eval(request.args['order'])
            query_params['order'] = order
        
        if 'range' in  request.args and request.args['range']:
            range = eval(request.args['range'])
            query_params['range'] = range
        
        data = GetAdminMemberListUseCase().execute(security_credentials,query_params)
        data['ok']= 1
        return  data , 200

    @admin_ns.doc('Create Member')
    @v1_api.expect(UpdateAdminUserStruct)    
    @jwt_required    
    def post(self):
        security_credentials = self.checkCredentials()
        payload = request.json        
        CreateAdminMemberUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200

    @admin_ns.doc('Update Member')
    @v1_api.expect(UpdateAdminUserStruct)    
    @jwt_required    
    def put(self):
        security_credentials = self.checkCredentials()
        payload = request.json        
        SaveAdminMemberUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200

@admin_ns.route('/member/<username>')
@admin_ns.param('username', 'Nombre de Usuario')
@v1_api.expect(secureHeader)
class OneAdminMemberResource(ProxySecureResource):
    
    @admin_ns.doc('Get Trabajador')
    @v1_api.marshal_with(GetOneAdminUserStruct) 
    @jwt_required    
    def get(self,username):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}
        query_params = {'username': username}
        data = GetAdminMemberUseCase().execute(security_credentials,query_params)
        return  {'ok' : 1, 'data': data}, 200

    @admin_ns.doc('Remove Trabajador')
    @jwt_required    
    def delete(self,username):
        security_credentials = self.checkCredentials()
        query_params = {'username': username}
        DeleteAdminMemberUseCase().execute(security_credentials,query_params)
        return  {'ok':1} , 200


@admin_ns.route('/rol')
@v1_api.expect(secureHeader)
class RolResource(ProxySecureResource): 

    @admin_ns.doc('User Rol')
    @jwt_required    
    @v1_api.marshal_with(GetRolListStruct) 
    def get(self):
        security_credentials = self.checkCredentials()
        query_params = {}
        data = GetRolListUseCase().execute(security_credentials,query_params)
        data['ok']= 1
        return  data , 200

    @admin_ns.doc('Save Rol')
    @v1_api.expect(UpdateRolStruct)    
    @jwt_required    
    def put(self):
        security_credentials = self.checkCredentials()
        payload = request.json        
        SaveRolUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200