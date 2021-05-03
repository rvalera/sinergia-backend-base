'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.repository.entities import CargoRepository

class GetCargoListUseCase(object):
    def execute(self,security_credentials):
        return CargoRepository(username=security_credentials['username']).getAll()
