'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.repository.cryptopos import WalletRepository,\
    PaymentInstrumentRepository, MemberRepository, MemberCardRepository,\
    AffiliateRepository, TerminalRepository, WithdrawalRepository

class AffiliateSignupUseCase(object):
    def execute(self,security_credentials,query_params):
        return AffiliateRepository(username=security_credentials['username'],password=security_credentials['password']).signup(query_params)

class AffiliateTerminalListUseCase(object):
    def execute(self,security_credentials,query_params):
        return TerminalRepository(username=security_credentials['username'],password=security_credentials['password']).get(query_params)
    
class CreateAffiliateTerminalUseCase(object):
    def execute(self,security_credentials,payload):
        return TerminalRepository(username=security_credentials['username'],password=security_credentials['password']).create(payload)    

class DeleteAffiliateTerminalUseCase(object):
    def execute(self,security_credentials,query_params):
        return TerminalRepository(username=security_credentials['username'],password=security_credentials['password']).remove(query_params)    

class GetAffiliateTerminalUseCase(object):
    def execute(self,security_credentials,query_params):
        return TerminalRepository(username=security_credentials['username'],password=security_credentials['password']).getById(query_params)    

    
class LockAffiliateTerminalUseCase(object):
    def execute(self,security_credentials,query_params):
        return TerminalRepository(username=security_credentials['username'],password=security_credentials['password']).lock(query_params)    
    
class UnlockAffiliateTerminalUseCase(object):
    def execute(self,security_credentials,query_params):
        return TerminalRepository(username=security_credentials['username'],password=security_credentials['password']).unlock(query_params)    

class AffiliateWithdrawalListUseCase(object):
    def execute(self,security_credentials,query_params):
        return WithdrawalRepository(username=security_credentials['username'],password=security_credentials['password']).get(query_params)