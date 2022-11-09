from app.v1 import v1_api
from app.v1.use_cases.application import GetApplicationUseCase, GetCoinBySymbolUseCase, GetDefaultCoinUseCase
from flask_jwt_extended.view_decorators import jwt_required
from flask_restplus import Resource, Namespace, fields
from app.v1.resources.base import ProxySecureResource, secureHeader,queryParams

from flask.globals import request    
import json

application_ns = v1_api.namespace('application', description='Aplication Services')


CoinStruct = v1_api.model('CoinStruct', { 
    'id':  fields.String(),
    'diminutive':   fields.String(),
    'name':  fields.String(),
    'description':  fields.String(),
    'dec_separator':  fields.String(),
    'th_separator':  fields.String(),
    'creation_date': fields.DateTime(),
    'blockchain_address':  fields.String(),
    'application_id':  fields.String(),
    'status':  fields.String()
})

GetOneCoinStruct = v1_api.model('GetOneCoinStruct', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'data' : fields.Nested(CoinStruct,attribute='data')
}) 

ApplicationStruct = v1_api.model('ApplicationStruct', { 
    'id' : fields.String(),
    'app_key' : fields.String(), 
    'fiat_coin': fields.Nested(CoinStruct,attribute='default_fiat_coin'),    
    'app_iv': fields.String(), 
    'name' : fields.String(), 
    'crypto_coin': fields.Nested(CoinStruct,attribute='default_crypto_coin'),
    'status': fields.String()
})

GetOneApplicationStruct = v1_api.model('GetOneApplicationStruct', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'data' : fields.Nested(ApplicationStruct,attribute='data')
}) 


@application_ns.route('/')
@v1_api.expect(secureHeader)
class AppSettingsResource(ProxySecureResource): 
    @application_ns.doc('Application Settings')
    @v1_api.marshal_with(GetOneApplicationStruct)        
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        data = GetApplicationUseCase().execute(security_credentials)
        return  {'ok' : 1, 'data': data}, 200

@application_ns.route('/coin')
@v1_api.expect(secureHeader)
class CoinSettingsResource(ProxySecureResource): 
 
    @application_ns.doc('Coin Settings')
    @v1_api.marshal_with(GetOneCoinStruct)            
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        data = GetDefaultCoinUseCase().execute(security_credentials)
        return  {'ok' : 1, 'data': data}, 200


@application_ns.route('/coin/<symbol>')
@application_ns.param('symbol', 'Coin Symbol')
@v1_api.expect(secureHeader)
class GetCoinResource(ProxySecureResource): 
 
    @application_ns.doc('Get Coin By Symbol')
    @v1_api.marshal_with(GetOneCoinStruct) 
    @jwt_required    
    def get(self,symbol):
        security_credentials = self.checkCredentials()
        query_params = { 'symbol':  symbol}
        data = GetCoinBySymbolUseCase().execute(security_credentials,query_params)
        return  {'ok' : 1, 'data': data}, 200
