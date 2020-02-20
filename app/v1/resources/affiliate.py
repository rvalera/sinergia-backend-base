from .base import secureHeader, ProxySecureResource,\
    queryParams, mResult
from app.v1 import v1_api
from flask.globals import request
from flask_jwt_extended.view_decorators import jwt_required
from flask_restplus import fields    
from app.v1.use_cases.affiliate import AffiliateSignupUseCase,\
    AffiliateTerminalListUseCase, CreateAffiliateTerminalUseCase,\
    DeleteAffiliateTerminalUseCase, UnlockAffiliateTerminalUseCase,\
    LockAffiliateTerminalUseCase, AffiliateWithdrawalListUseCase,\
    GetAffiliateTerminalUseCase
import json
from app.v1.use_cases.transaction import GetTransactionUseCase,\
    GetTransactionByTerminalUseCase

affiliate_ns = v1_api.namespace('affiliate', description='Affiliate Services')

mCreateTerminal = v1_api.model('CreateTerminal', {
    'quantity': fields.Integer(required=True, value=1, description='Quantity')
})


@affiliate_ns.route('/signup')
@v1_api.expect(secureHeader)
class AffiliateSignupResource(ProxySecureResource):
     
    @affiliate_ns.doc('Affiliate Signup')
    @affiliate_ns.marshal_with(mResult, code=200)
    @jwt_required
    def post(self):
        security_credentials = self.checkCredentials()
        query_params = {'person_id' : security_credentials['person_id']}
        data = AffiliateSignupUseCase().execute(security_credentials,query_params)
        return  data, 200


@affiliate_ns.route('/terminal')
@v1_api.expect(secureHeader)
class AffiliateTerminalResource(ProxySecureResource):
 
    @affiliate_ns.doc('List Terminal')
    @v1_api.expect(queryParams)
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        query_params = { 'filter': json.dumps({'person_id': str(security_credentials['person_id']) }) }
        
        if 'sort' in  request.args and request.args['sort']:
            sort = eval(request.args['sort'])
            query_params['sort'] = json.dumps(sort)
        
        if 'range' in  request.args and request.args['range']:
            range = eval(request.args['range'])
            query_params['range'] = json.dumps(range)

        data = AffiliateTerminalListUseCase().execute(security_credentials,query_params)
        return  data, 200

    @affiliate_ns.doc('Create Terminal')
    @affiliate_ns.expect(mCreateTerminal)
    @jwt_required        
    def post(self):
        payload = request.json        
        security_credentials = self.checkCredentials()
        payload['person_id'] = security_credentials['person_id']
        payload['type'] = 'P' # Point of Sale
        data = CreateAffiliateTerminalUseCase().execute(security_credentials,payload)
        return  data, 200


@affiliate_ns.route('/terminal/<id>')
@affiliate_ns.param('id', 'Terminal Id')
@v1_api.expect(secureHeader)
class RemoveAffiliateTerminalResource(ProxySecureResource):


    @affiliate_ns.doc('Get Terminal')
    @jwt_required    
    def get(self,id):
        security_credentials = self.checkCredentials()
        query_params = {'id': id}
        data = GetAffiliateTerminalUseCase().execute(security_credentials,query_params)
        return  data, 200
 
    @affiliate_ns.doc('Remove Terminal')
    @jwt_required    
    def delete(self,id):
        security_credentials = self.checkCredentials()
        query_params = {'id': id}
        data = DeleteAffiliateTerminalUseCase().execute(security_credentials,query_params)
        return  data, 200


@affiliate_ns.route('/terminal/<id>/transaction')
@affiliate_ns.param('id', 'Terminal Id')
@v1_api.expect(secureHeader)
class TerminalTransactionResource(ProxySecureResource):
 
    @affiliate_ns.doc('Terminal Transactions')
    @v1_api.expect(queryParams)
    @jwt_required    
    def get(self,id):
        security_credentials = self.checkCredentials()
 
        query_params = {}

        request_payload =  {}        
        if 'filter' in  request.args and request.args['filter']:
            filter = eval(request.args['filter'])
            filter['terminal_id'] = id            
            request_payload = filter
        else:
            request_payload['terminal_id'] = id

        query_params['filter'] = json.dumps(request_payload) 

        if 'sort' in  request.args and request.args['sort']:
            sort = eval(request.args['sort'])
            query_params['sort'] = json.dumps(sort)
        
        if 'range' in  request.args and request.args['range']:
            range = eval(request.args['range'])
            query_params['range'] = json.dumps(range)
        
        data = GetTransactionByTerminalUseCase().execute(security_credentials, query_params)
        
        return  data, 200
    
    
@affiliate_ns.route('/terminal/<id>/lock')
@affiliate_ns.param('id', 'Terminal Id')
@v1_api.expect(secureHeader)
class LockAffiliateTerminalResource(ProxySecureResource):
 
    @affiliate_ns.doc('Lock Terminal')
    @jwt_required    
    def put(self,id):
        security_credentials = self.checkCredentials()
        query_params = {'id': id}
        data = LockAffiliateTerminalUseCase().execute(security_credentials,query_params)
        return  data, 200


@affiliate_ns.route('/terminal/<id>/unlock')
@affiliate_ns.param('id', 'Terminal Id')
@v1_api.expect(secureHeader)
class UnLockAffiliateTerminalResource(ProxySecureResource):
 
    @affiliate_ns.doc('UnLock Terminal')
    @jwt_required    
    def put(self,id):
        security_credentials = self.checkCredentials()
        query_params = {'id': id}
        data = UnlockAffiliateTerminalUseCase().execute(security_credentials,query_params)
        return  data, 200
    
@affiliate_ns.route('/withdrawal') 
@v1_api.expect(secureHeader)
class AffiliateWithdrawalResource(ProxySecureResource):
 
    @affiliate_ns.doc('Withdrawal List')
    @v1_api.expect(queryParams)
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        query_params = { 'filter': json.dumps( {'person_id': security_credentials['person_id'] }) }
        
        if 'sort' in  request.args and request.args['sort']:
            sort = eval(request.args['sort'])
            query_params['sort'] = json.dumps(sort)
        
        if 'range' in  request.args and request.args['range']:
            range = eval(request.args['range'])
            query_params['range'] = json.dumps(range)

        data = AffiliateWithdrawalListUseCase().execute(security_credentials,query_params)
        return  data, 200
    