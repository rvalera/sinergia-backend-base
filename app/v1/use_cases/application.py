'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.repository.cryptopos import ApplicationRepository, CoinRepository

class GetApplicationUseCase(object):
    def execute(self,security_credentials,query_params):
        return ApplicationRepository(username=security_credentials['username'],password=security_credentials['password']).get(query_params)

class GetDefaultCoinUseCase(object):
    def execute(self,security_credentials,query_params):
        return CoinRepository(username=security_credentials['username'],password=security_credentials['password']).getDefault(query_params)
    
class GetCoinBySymbolUseCase(object):
    def execute(self,security_credentials,query_params):
        return CoinRepository(username=security_credentials['username'],password=security_credentials['password']).getBySymbol(query_params)
