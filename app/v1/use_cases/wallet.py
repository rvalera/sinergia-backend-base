'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.repository.cryptopos import WalletRepository,\
    PaymentInstrumentRepository, MemberRepository, MemberCardRepository

class DashboardUseCase(object):
    def execute(self,security_credentials,query_params):
        return WalletRepository(username=security_credentials['username'],password=security_credentials['password']).getDashboard(query_params)

class ListPaymentInstrumentUseCase(object):
    def execute(self,security_credentials,query_params):
        return PaymentInstrumentRepository(username=security_credentials['username'],password=security_credentials['password']).get(query_params)

class CreatePaymentInstrumentUseCase(object):
    def execute(self,security_credentials,payload):
        return PaymentInstrumentRepository(username=security_credentials['username'],password=security_credentials['password']).save(payload)

class DeletePaymentInstrumentUseCase(object):
    def execute(self,security_credentials,query_params):
        return PaymentInstrumentRepository(username=security_credentials['username'],password=security_credentials['password']).remove(query_params)

class GetDefaultPaymentInstrumentUseCase(object):
    def execute(self,security_credentials,query_params):
        return PaymentInstrumentRepository(username=security_credentials['username'],password=security_credentials['password']).getDefault(query_params)

class SetDefaultPaymentInstrumentUseCase(object):
    def execute(self,security_credentials,payload):
        return PaymentInstrumentRepository(username=security_credentials['username'],password=security_credentials['password']).setDefault(payload)

class ListMemberCardUseCase(object):
    def execute(self,security_credentials,query_params):
        return MemberCardRepository(username=security_credentials['username'],password=security_credentials['password']).get(query_params)
    
class SetPinMemberCardUseCase(object):
    def execute(self,security_credentials,payload):
        return MemberCardRepository(username=security_credentials['username'],password=security_credentials['password']).setPin(payload)

class LockMemberCardUseCase(object):
    def execute(self,security_credentials,query_params):
        return MemberCardRepository(username=security_credentials['username'],password=security_credentials['password']).lock(query_params)

class UnLockMemberCardUseCase(object):
    def execute(self,security_credentials,query_params):
        return MemberCardRepository(username=security_credentials['username'],password=security_credentials['password']).unlock(query_params)

class ChangeOperationKeyMemberUseCase(object):
    def execute(self,security_credentials,payload):
        return MemberRepository(username=security_credentials['username'],password=security_credentials['password']).changeOperationKey(payload)

class ResetOperationKeyMemberUseCase(object):
    def execute(self,security_credentials,payload):
        return MemberRepository(username=security_credentials['username'],password=security_credentials['password']).resetOperationKey(payload)

class ResetPinyMemberCardUseCase(object):
    def execute(self,security_credentials,payload):
        return MemberCardRepository(username=security_credentials['username'],password=security_credentials['password']).resetPin(payload)
        