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

class GetLastImportStatusUseCase(object):
    def execute(self,security_credentials):
        response = AirflowUtils().get_last_import()
        return response

class ExecuteImportUseCase(object):
    def execute(self,security_credentials,payload):
        AirflowUtils().execute_import(payload)

class GetLastExportStatusUseCase(object):
    def execute(self,security_credentials):
        response = AirflowUtils().get_last_export()
        return response

class ExecuteExportUseCase(object):
    def execute(self,security_credentials,payload):
        AirflowUtils().execute_export(payload)
