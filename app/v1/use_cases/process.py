'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.repository.process import DailyMarkingRepository

class GetDailyMarkingListUseCase(object):
    def execute(self,security_credentials,query_params):
        return DailyMarkingRepository(username=security_credentials['username']).get(query_params)
