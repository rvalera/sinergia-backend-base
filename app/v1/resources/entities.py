from app.v1 import v1_api
from flask_jwt_extended.view_decorators import jwt_required
from app.v1.resources.base import ProxySecureResource, secureHeader
from app.v1.use_cases.entities import GetCargoListUseCase

entities_ns = v1_api.namespace('entities', description='Business Entities Services')

@entities_ns.route('/cargo')
@v1_api.expect(secureHeader)
class CoinSettingsResource(ProxySecureResource): 
 
    @entities_ns.doc('Cargo')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        data = GetCargoListUseCase().execute(security_credentials)
        return  {'ok':1, 'data': data} , 200
