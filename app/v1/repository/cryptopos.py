'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.repository.base import CryptoPOSClient

class WalletRepository(CryptoPOSClient):

    def getDashboard(self,query_params):
        data = self.executePost('/api/v2/wallet/dashboard', query_params['filter'])
        return data
        

class MemberRepository(CryptoPOSClient):
    
    def get(self,query_params):
        request_params = {}
        result = self.executeGet('/api/v2/person/%s/A' % self.username, request_params)
        return result

    def getByEmail(self,query_params):
        request_params = {}
        result = self.executeGet('/api/v2/person/%s/A' % query_params['email'], request_params)
        return result
    
    def save(self,payload):
        data = self.executePut('/api/v2/mobile_user/%s' % payload['id'], payload)
        return data
    
    def changePassword(self,payload):
        data = self.executePut('/api/v2/user/password/%s' % payload['id'], payload)
        return data

    def resetPassword(self,payload):
        data = self.executePost('/api/v2/user/reset_user_password/%s' % payload['email'], payload)
        return data
    
    def changeOperationKey(self,payload):
        data = self.executePut('/api/v2/user/operation_key/%s' % payload['id'], payload)
        return data

    def resetOperationKey(self,payload):
        data = self.executePost('/api/v2/user/reset_password/%s' % self.username, payload)
        return data
    
    def initCreate(self,data):
        result = self.executePost('/api/v2/mobile_user', data)
        return result

    def finishCreate(self,data):
        result = self.executePost('/api/v2/app_person/%s' % data['id'], data)
        return result


class PaymentInstrumentRepository(CryptoPOSClient):

    def get(self,query_params):
        data = self.executeGet('/api/v2/payment_instrument', query_params)
        return data

    def save(self,payload):
        data = self.executePost('/api/v2/payment_instrument', payload)
        return data

    def remove(self,payload):
        request_payload = {}
        data = self.executeDelete('/api/v2/payment_instrument/%s' % payload['id'], request_payload)
        return data
    
    def getDefault(self,query_params):
        data = self.executeGet('/api/v2/payment_instrument/default', query_params)
        return data
        
    def setDefault(self,query_params):
        payload = {}
        data = self.executePut('/api/v2/payment_instrument/default/%s' % query_params['id'], payload)
        return data


class MemberCardRepository(CryptoPOSClient):

    def get(self,query_params):
        request_params = {}
#         data = self.executeGet('/api/v2/affiliate/%s' % query_params['person_id'], request_params)
        data = self.executeGet('/api/v2/card/person_id/%s' % query_params['person_id'], request_params)
        return data

    def setPin(self,payload):
        data = self.executePut('/api/v2/card/pin/%s' % payload['id'], payload)
        return data

    def resetPin(self,payload):
        data = self.executePost('/api/v2/user/reset_password/%s' % self.username, payload)
        return data

    def lock(self,payload):
        request_payload = {}
        data = self.executePut('/api/v2/card/block/%s' % payload['id'], request_payload)
        return data
    
    def unlock(self,payload):
        request_payload = {}
        data = self.executePut('/api/v2/card/unblock/%s' % payload['id'] , request_payload)
        return data
        

class AffiliateRepository(CryptoPOSClient):
    
    def signup(self,query_params):
        request_payload = {}
        result = self.executePut('/api/v2/affiliate/request/%s'  % query_params['person_id'], request_payload)
        return result


class WithdrawalRepository(CryptoPOSClient):

    def get(self,query_params):
        result = self.executeGet('/api/v2/personliquidation' , query_params)
        return result
    

class ApplicationRepository(CryptoPOSClient):

    def get(self,query_params):
        result = self.executeGet('/api/v2/app' , query_params)
        return result


class CoinRepository(CryptoPOSClient):
    
    def getDefault(self,query_params):
        result = self.executeGet('/api/v2/coin/active' , query_params)
        return result

    def getBySymbol(self,query_params):
        result = self.executeGet('/api/v2/coin/%s' % query_params['symbol'] , query_params)
        return result


class TerminalRepository(CryptoPOSClient):
    
    def get(self,query_params):
        result = self.executeGet('/api/v2/terminal' , query_params)
        return result

    def getById(self,query_params):
        request_params = {}
        result = self.executeGet('/api/v2/terminal/%s' % query_params['id'] , request_params)
        return result

        
    def create(self,payload):
        result = self.executePost('/api/v2/terminal' , payload)
        return result

    def remove(self,payload):
        request_payload = {}
        data = self.executeDelete('/api/v2/terminal/%s' % payload['id'], request_payload)
        return data

    def lock(self,payload):
        request_payload = {'terminal_id': payload['id']}
        data = self.executePut('/api/v2/terminal/lock', request_payload)
        return data
    
    def unlock(self,payload):
        request_payload = {'terminal_id': payload['id']}
        data = self.executePut('/api/v2/terminal/unlock', request_payload)
        return data

class TransactionRepository(CryptoPOSClient):

    def makePaymentQR(self,payload):
        result = self.executePost('/api/v2/payment/qr2' , payload)
        return result
    
    def makeTransference(self,payload):
        result = self.executePost('/api/v2/app_transference' , payload)
        return result

    def makeReload(self,payload):
        result = self.executePost('/api/v2/person/refill/express' , payload)
        return result
    
    def get(self,query_params):
        result = self.executeGet('/api/v2/transaction' , query_params)
        return result

