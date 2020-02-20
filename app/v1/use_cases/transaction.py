'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.repository.cryptopos import TransactionRepository,\
    TerminalRepository
from app.v1.use_cases.security import GetAnyMemberProfileUseCase
import json
from app.exceptions.base import CryptoPOSException
from app.v1.use_cases.application import GetCoinBySymbolUseCase

class MakePaymentQRUseCase(object):
    def execute(self,security_credentials,payload):
        coin = GetCoinBySymbolUseCase().execute(security_credentials, { 'symbol' : payload['coin_symbol']})
        if coin is None:
            raise CryptoPOSException()
        payload['coin_id'] = coin['data']['id']
        return TransactionRepository(username=security_credentials['username'],password=security_credentials['password']).makePaymentQR(payload)

class MakeTransferenceUseCase(object):
    def execute(self,security_credentials,payload):
        target_person = GetAnyMemberProfileUseCase().execute(security_credentials, {'email' : payload['target'] })
        payload['target_id'] = target_person['data']['id']
        
        coin = GetCoinBySymbolUseCase().execute(security_credentials, { 'symbol' : payload['coin_symbol']})
        if coin is None:
            raise CryptoPOSException()

        payload['coin_id'] = coin['data']['id']
        
        return TransactionRepository(username=security_credentials['username'],password=security_credentials['password']).makeTransference(payload)
    
class MakeReloadUseCase(object):
    def execute(self,security_credentials,payload):
        return TransactionRepository(username=security_credentials['username'],password=security_credentials['password']).makeReload(payload)
    
class GetTransactionUseCase(object):
    def execute(self,security_credentials,query_params):

        if 'filter' in  query_params and query_params['filter']:
            filter = eval(query_params['filter'])
            request_payload = filter 
            query_params['filter'] = json.dumps({'filter': request_payload} )
        
        return TransactionRepository(username=security_credentials['username'],password=security_credentials['password']).get(query_params)

class GetTransactionByTerminalUseCase(object):
    def execute(self,security_credentials,query_params):

        filter = eval(query_params['filter'])

        terminal = TerminalRepository(username=security_credentials['username'],password=security_credentials['password']).getById({'id' :  filter['terminal_id']})

        if terminal is not None:        
            filter['device_id'] = terminal['data']['device_id']
            request_payload = filter 
            query_params['filter'] = json.dumps({'filter': request_payload} )
        else:
            raise CryptoPOSException()
        
        return TransactionRepository(username=security_credentials['username'],password=security_credentials['password']).get(query_params)
