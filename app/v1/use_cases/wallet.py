'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.repository.auth import WalletRepository

class DashboardUseCase(object):
    
    def execute(self,security_credentials,query_params):
        return WalletRepository(username=security_credentials['username'],password=security_credentials['password']).getDashboard(query_params)