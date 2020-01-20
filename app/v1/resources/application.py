from app.v1 import v1_api
from flask_jwt_extended.view_decorators import jwt_required
from app.v1.resources.base import ProxySecureResource, secureHeader
from app.v1.use_cases.application import GetApplicationUseCase,\
    GetDefaultCoinUseCase, GetCoinBySymbolUseCase

application_ns = v1_api.namespace('application', description='Aplication Services')

@application_ns.route('/')
@v1_api.expect(secureHeader)
class AppSettingsResource(ProxySecureResource): 
 
    @application_ns.doc('Application Settings')
    @jwt_required    
    def get(self):
        security_credentials = self.check_credentials()
        query_params = {  }
        data = GetApplicationUseCase().execute(security_credentials,query_params)
        return  data, 200

@application_ns.route('/coin')
@v1_api.expect(secureHeader)
class CoinSettingsResource(ProxySecureResource): 
 
    @application_ns.doc('Coin Settings')
    @jwt_required    
    def get(self):
        security_credentials = self.check_credentials()
        query_params = {  }
        data = GetDefaultCoinUseCase().execute(security_credentials,query_params)
        return  data, 200


@application_ns.route('/coin/<symbol>')
@application_ns.param('symbol', 'Coin Symbol')
@v1_api.expect(secureHeader)
class GetCoinResource(ProxySecureResource): 
 
    @application_ns.doc('Get Coin By Symbol')
    @jwt_required    
    def get(self,symbol):
        security_credentials = self.check_credentials()
        query_params = { 'symbol':  symbol}
        data = GetCoinBySymbolUseCase().execute(security_credentials,query_params)
        return  data, 200

