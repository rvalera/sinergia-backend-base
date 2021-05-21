'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.repository.security import SecurityElementRepository, UserRepository
from app.v1.repository.admin import MemberRepository, RolRepository
from app.v1.repository.system import ApplicationRepository
from app.tools.airflow import AirflowUtils

class GetApplicationUseCase(object):
    def execute(self,security_credentials):
        return ApplicationRepository(username=security_credentials['username']).get()

class SaveApplicationUseCase(object):
    def execute(self,security_credentials,payload):
        ApplicationRepository(username=security_credentials['username']).save(payload)

class GetLastSyncStatusUseCase(object):
    def execute(self,security_credentials):
        response = AirflowUtils().get_last_sync()
        return response

class ExecuteSyncUseCase(object):
    def execute(self,security_credentials,payload):
        AirflowUtils().execute_sync(payload)

