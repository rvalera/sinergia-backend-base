from flask import current_app, request, jsonify
from flask_restplus import Resource, Namespace, fields
# from ..models.user import User
# from ..models.auth import RefreshToken
from app import db, redis_client
from app.v1 import v1_api
# from ..exceptions import ValidationException
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
from ..use_cases.wallet import DashboardUseCase
from app.exceptions.base import SinergiaException, ProxyCredentialsNotFound
from app.v1.use_cases.security import   MemberInitSignUpUseCase,\
    MemberFinishRegisterUseCase, GetMemberProfileUseCase,\
    UpdateMemberProfileUseCase, ChangePasswordMemberUseCase,\
    ResetPasswordMemberUseCase
from app.v1.use_cases.wallet import ChangeOperationKeyMemberUseCase
from app.v1.resources.base import ProxySecureResource, secureHeader
from app.v1.use_cases.transaction import MakeTransferenceUseCase,\
    MakeReloadUseCase, MakePaymentQRUseCase


transaction_ns = v1_api.namespace('transaction', description='Transaction Services')


mQRPaymentTransaction = v1_api.model('QRPaymentTransaction', {
    'terminal_code' : fields.String(required=True, description='Terminal Code'),
    'type': fields.String(required=True, description='Payment Type - (P) Post, (S) Sticker'),
    'amount': fields.Float(required=True, description='Amount Transaction'),
    'coin_symbol': fields.String(required=True, description='Coin Symbol'),
    'concept': fields.String(required=True, description='Transference Concept'),
    'datetime': fields.String(required=True, description='Datetime Transaction'),
})

'''
QR = {
        'device_id': <long>, -> cambiar por terminal_id. (Los servicios que se tienen estan en funcion a terminal) 
        'person_id': <long>, -> cambiar por correo electronico del destino de la transaccion 
        'type' : 'P',
        'qr' : <string>,
        'datetime' : <datestamp>,
        'amount': <float>,
        'coin_id': <long>,
        'concept': <string>
    }
'''



mP2PTransferenceTransaction = v1_api.model('P2PTransferenceTransaction', {
    'target': fields.String(required=True, description='Target Email'),
    'amount': fields.Float(required=True, description='Amount Transaction'),
    'coin_symbol': fields.String(required=True, description='Coin Symbol'),
    'concept': fields.String(required=True, description='Transference Concept'),
    'datetime': fields.String(required=True, description='Datetime Transaction'),
})

mReloadTransaction = v1_api.model('ReloadTransaction', {
    'fiat_coin_symbol': fields.String(required=True, description='Fiat Coin Symbol'),
    'crypto_coin_symbol': fields.String(required=True, description='Crypto Coin Symbol'),
    'payment_instrument_id': fields.String(required=True, description='Payment Instrument ID'),    
    'amount': fields.Float(required=True, description='Amount Transaction'),
})


@transaction_ns.route('/payment/qr')
@v1_api.expect(secureHeader)
class MakePaymentResource(ProxySecureResource): 
 
    @transaction_ns.doc('Make Payment')
    @transaction_ns.expect(mQRPaymentTransaction)
    @jwt_required    
    def post(self):
        payload = request.json        
        security_credentials = self.check_credentials()
        payload['source_id'] = security_credentials['person_extension_id'] 
        data = MakePaymentQRUseCase().execute(security_credentials,payload)
        return  data, 200


@transaction_ns.route('/transfer')
@v1_api.expect(secureHeader)
class MakeTransferenceResource(ProxySecureResource): 
 
    @transaction_ns.doc('Make Transfer')
    @transaction_ns.expect(mP2PTransferenceTransaction)
    @jwt_required    
    def post(self):
        payload = request.json        
        security_credentials = self.check_credentials()
        payload['source_id'] = security_credentials['person_extension_id'] 
        data = MakeTransferenceUseCase().execute(security_credentials,payload)
        return  data, 200

    
@transaction_ns.route('/reload')
@v1_api.expect(secureHeader)
class MakeReloadResource(ProxySecureResource): 
 
    @transaction_ns.doc('Make Reload')
    @transaction_ns.expect(mReloadTransaction)
    @jwt_required    
    def post(self):
        payload = request.json        
        security_credentials = self.check_credentials()
        data = MakeReloadUseCase().execute(security_credentials,payload)
        return  data, 200
    
