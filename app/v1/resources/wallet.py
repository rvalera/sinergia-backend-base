from app.v1.resources.base import member_ns, secureHeader, ProxySecureResource,\
    queryParams
from app.v1 import v1_api
from flask.globals import request
from flask_jwt_extended.view_decorators import jwt_required
from app.v1.use_cases.wallet import DashboardUseCase

@member_ns.route('/dashboard')
@v1_api.expect(secureHeader)
class MemberDashboardResource(ProxySecureResource):
 
    @member_ns.doc('User Dashboard')
    @v1_api.expect(queryParams)
    @jwt_required    
    def get(self):

        security_credentials = self.check_credentials()
 
        query_params = {}
        request_payload =  {"start_date" : None, "end_date" : None}        
        if 'filter' in  request.args and request.args['filter']:
            json_filter = eval(request.args['filter'])
            request_payload = json_filter.copy()

        query_params['filter'] = request_payload
        
        data = DashboardUseCase().execute(security_credentials, query_params)
        
        return  data, 200
