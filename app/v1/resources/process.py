from app.v1 import v1_api
from flask_jwt_extended.view_decorators import jwt_required
from flask_restplus import Resource, Namespace, fields
from app.v1.resources.base import ProxySecureResource, secureHeader,queryParams
from app.v1.use_cases.process import GetDailyMarkingListUseCase
from flask.globals import request    
import json 

process_ns = v1_api.namespace('process', description='Process Services')


@process_ns.route('/daily_marking')
@v1_api.expect(secureHeader)
class DailyMarkingResource(ProxySecureResource): 

    @process_ns.doc('Get Marcajes Diarios')
    @v1_api.expect(queryParams)
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'guest'}
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
        
        data = GetDailyMarkingListUseCase().execute(security_credentials,query_params)
        data['ok']= 1
        return  data , 200

