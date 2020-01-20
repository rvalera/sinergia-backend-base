from app.v1.resources.base import member_ns, secureHeader, ProxySecureResource,\
    queryParams
from app.v1 import v1_api
from flask.globals import request
from flask_jwt_extended.view_decorators import jwt_required
from app.v1.use_cases.wallet import DashboardUseCase,\
    ListPaymentInstrumentUseCase, CreatePaymentInstrumentUseCase,\
    DeletePaymentInstrumentUseCase, GetDefaultPaymentInstrumentUseCase,\
    SetDefaultPaymentInstrumentUseCase, ListMemberCardUseCase,\
    SetPinMemberCardUseCase, LockMemberCardUseCase, UnLockMemberCardUseCase,\
    ChangeOperationKeyMemberUseCase, ResetOperationKeyMemberUseCase,\
    ResetPinyMemberCardUseCase
from flask_restplus import Resource, Namespace, fields    
from app.exceptions.base import CryptoPOSException
import json
from app.v1.use_cases.transaction import GetTransactionUseCase


mNewPaymentInstrument = v1_api.model('PaymentInstrument', {
    'card_number': fields.String(required=True, description='Card Number'),
    'exp_month': fields.String(required=True, description='Expired Month'),
    'exp_year': fields.String(required=True, description='Expired Year'),
    'cvc': fields.String(required=True, description='CVC')
})


mChangePin = v1_api.model('ChangePin', {
    'old_pin': fields.String(required=True, description='Old Pin'),
    'new_pin': fields.String(required=True, description='New Pin'),
})

mChangeOperationKey = v1_api.model('ChangeOperationKey', {
    'old_operation_key': fields.String(required=True, description='Old Operation Key'),
    'new_operation_key': fields.String(required=True, description='New Operation Key'),
})

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


@member_ns.route('/paymentInstrument')
@v1_api.expect(secureHeader)
class MemberPaymentInstrumentResource(ProxySecureResource): 
 
    @member_ns.doc('List Payment Instrument')
    @v1_api.expect(queryParams)
    @jwt_required    
    def get(self):
        security_credentials = self.check_credentials()
        query_params = {}
        data = ListPaymentInstrumentUseCase().execute(security_credentials,query_params)
        return  data, 200

    @member_ns.doc('Add Payment Instrument')
    @v1_api.expect(mNewPaymentInstrument)
    @jwt_required    
    def post(self):
        payload = request.json        
        security_credentials = self.check_credentials()
        data = CreatePaymentInstrumentUseCase().execute(security_credentials,payload)
        return  data, 200

@member_ns.route('/paymentInstrument/<id>')
@member_ns.param('id', 'Payment Instrument Id')
@v1_api.expect(secureHeader)
class DeleteMemberPaymentInstrumentResource(ProxySecureResource):
    
    @member_ns.doc('Remove Payment Instrument')
    @jwt_required    
    def delete(self,id):
        security_credentials = self.check_credentials()
        query_params = {'id': id}
        data = DeletePaymentInstrumentUseCase().execute(security_credentials,query_params)
        return  data, 200
        
@member_ns.route('/paymentInstrument/default')
@v1_api.expect(secureHeader)
class MemberPaymentInstrumentDefaultResource(ProxySecureResource):
 
    @member_ns.doc('Current Default Payment Instrument')
    @jwt_required    
    def get(self):
        security_credentials = self.check_credentials()
        query_params = {}
        data = GetDefaultPaymentInstrumentUseCase().execute(security_credentials,query_params)
        return  data, 200


@member_ns.route('/paymentInstrument/<id>/default')
@member_ns.param('id', 'Payment Instrument Id')
@v1_api.expect(secureHeader)
class SetMemberPaymentInstrumentDefaultResource(ProxySecureResource):
    
    @member_ns.doc('Set Default Payment Instrument')
    @jwt_required    
    def put(self,id):
        security_credentials = self.check_credentials()
        query_params = { 'id': id }
        data = SetDefaultPaymentInstrumentUseCase().execute(security_credentials,query_params)
        return  data, 200


@member_ns.route('/card')
@v1_api.expect(secureHeader)
class MemberCardListResource(ProxySecureResource):
 
    @member_ns.doc('List Member Card')
    @v1_api.expect(queryParams)
    @jwt_required    
    def get(self):
        security_credentials = self.check_credentials()
        query_params = {'person_id' : security_credentials['person_id']}
        data = ListMemberCardUseCase().execute(security_credentials,query_params)
        return  data, 200

@member_ns.route('/card/<id>/transaction')
@member_ns.param('id', 'Card Id')
@v1_api.expect(secureHeader)
class MemberCardTransactionResource(ProxySecureResource):
 
    @member_ns.doc('Card Transactions')
    @v1_api.expect(queryParams)
    @jwt_required    
    def get(self,id):
        security_credentials = self.check_credentials()
 
        query_params = {}

        request_payload =  {}        
        if 'filter' in  request.args and request.args['filter']:
            filter = eval(request.args['filter'])
            filter['blockchain_id'] = id            
            request_payload = filter
        else:
            request_payload['blockchain_id'] = id

        query_params['filter'] = json.dumps(request_payload ) 

        if 'sort' in  request.args and request.args['sort']:
            sort = eval(request.args['sort'])
            query_params['sort'] = json.dumps(sort)
        
        if 'range' in  request.args and request.args['range']:
            range = eval(request.args['range'])
            query_params['range'] = json.dumps(range)
        
        data = GetTransactionUseCase().execute(security_credentials, query_params)
        
        return  data, 200

@member_ns.route('/card/<id>/pin')
@member_ns.param('id', 'Card Id')
@v1_api.expect(secureHeader)
class SetPinMemberCardResource(ProxySecureResource):
 
    @member_ns.doc('Set PIN Member Card')
    @v1_api.expect(mChangePin)    
    @jwt_required    
    def put(self,id):
        user_payload = request.json

        request_payload = { 'id': id ,
                   'new_pin_card': user_payload['new_pin'],
                   'old_pin_card': user_payload['old_pin']}
        
        security_credentials = self.check_credentials()
        data = SetPinMemberCardUseCase().execute(security_credentials,request_payload)
        return  data, 200
    
    
@member_ns.route('/card/<id>/pin/reset')
@member_ns.param('id', 'Card Id')
@v1_api.expect(secureHeader)
class ResetPinMemberCardResource(ProxySecureResource):
 
    @member_ns.doc('Reset PIN Member Card')
    @jwt_required    
    def post(self,id):
        security_credentials = self.check_credentials()
        request_payload = { 'password_type': 'P', 'id': id }
        data = ResetPinyMemberCardUseCase().execute(security_credentials,request_payload)
        return  data, 200
    


@member_ns.route('/card/<id>/lock')
@member_ns.param('id', 'Card Id')
@v1_api.expect(secureHeader)
class LockMemberCardResource(ProxySecureResource):
 
    @member_ns.doc('Lock Member Card')
    @jwt_required    
    def put(self,id):
        security_credentials = self.check_credentials()
        query_params = { 'id': id }
        data = LockMemberCardUseCase().execute(security_credentials,query_params)
        return  data, 200


@member_ns.route('/card/<id>/unlock')
@member_ns.param('id', 'Card Id')
@v1_api.expect(secureHeader)
class UnLockMemberCardResource(ProxySecureResource):
 
    @member_ns.doc('UnLock Member Card')
    @jwt_required    
    def put(self,id):
        security_credentials = self.check_credentials()
        query_params = { 'id': id }
        data = UnLockMemberCardUseCase().execute(security_credentials,query_params)
        return  data, 200

@member_ns.route('/operationKey')
@v1_api.expect(secureHeader)
class ChangeOperationKeyMemberResource(ProxySecureResource):
 
    @member_ns.doc('Change Operation Key')
    @v1_api.expect(mChangeOperationKey)    
    @jwt_required    
    def put(self):
        user_payload = request.json
        security_credentials = self.check_credentials()

        request_payload = { 'id': security_credentials['id'] ,
                   'operation_key': user_payload['new_operation_key'],
                   'old_operation_key': user_payload['old_operation_key']}
        
        data = ChangeOperationKeyMemberUseCase().execute(security_credentials,request_payload)
        return  data, 200

@member_ns.route('/operationKey/reset')
@v1_api.expect(secureHeader)
class ResetOperationKeyMemberResource(ProxySecureResource):
 
    @member_ns.doc('Reset Operation Key')
    @jwt_required    
    def post(self):
        security_credentials = self.check_credentials()
        request_payload = { 'password_type': 'O' }
        data = ResetOperationKeyMemberUseCase().execute(security_credentials,request_payload)
        return  data, 200

@member_ns.route('/transaction')
@v1_api.expect(secureHeader)
class MemberTransactionResource(ProxySecureResource):
 
    @member_ns.doc('Member Transactions')
    @v1_api.expect(queryParams)
    @jwt_required    
    def get(self):
        security_credentials = self.check_credentials()
 
        query_params = {}

        request_payload =  {}        
        if 'filter' in  request.args and request.args['filter']:
            filter = eval(request.args['filter'])
            filter['blockchain_id'] = security_credentials['person_id']            
            request_payload = filter
        else:
            request_payload['blockchain_id'] = security_credentials['person_id']

        query_params['filter'] = json.dumps(request_payload) 

        if 'sort' in  request.args and request.args['sort']:
            sort = eval(request.args['sort'])
            query_params['sort'] = json.dumps(sort)
        
        if 'range' in  request.args and request.args['range']:
            range = eval(request.args['range'])
            query_params['range'] = json.dumps(range)
        
        print(query_params)
        
        data = GetTransactionUseCase().execute(security_credentials, query_params)
        
        return  data, 200