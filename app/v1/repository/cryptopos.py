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
    
    def create(self,data):
        data = self.executePost('/api/v2/mobile_user', data)
        return data

    def update(self,data):
        data = self.executePut('/api/v2/mobile_user/%s' % data['user_id'], data)
        return data

