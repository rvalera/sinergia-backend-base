'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.repository.process import DailyMarkingRepository,OvertimeEventRepository,AbsenceEventRepository,JustificationAbsenceRepository

class GetDailyMarkingListUseCase(object):
    def execute(self,security_credentials,query_params):
        return DailyMarkingRepository(username=security_credentials['username']).get(query_params)

class GetOvertimeEventUseCase(object):
    def execute(self,security_credentials,event_date,cedula):
        return OvertimeEventRepository(username=security_credentials['username']).get(event_date,cedula)

class ApproveOvertimeEventUseCase(object):
    def execute(self,security_credentials,event_date,cedula,id):
        return OvertimeEventRepository(username=security_credentials['username']).approve(event_date,cedula,id)                

class GetAbsenceEventUseCase(object):
    def execute(self,security_credentials,event_date,cedula):
        return AbsenceEventRepository(username=security_credentials['username']).get(event_date,cedula)        

class NewAbsenceJustificationUseCase(object):
    def execute(self,security_credentials,payload):
        return JustificationAbsenceRepository(username=security_credentials['username']).new(payload)        

class SaveAbsenceJustificationUseCase(object):
    def execute(self,security_credentials,payload):
        return JustificationAbsenceRepository(username=security_credentials['username']).save(payload)        

class DeleteAbsenceJustificationUseCase(object):
    def execute(self,security_credentials,event_date,cedula,id):
        return JustificationAbsenceRepository(username=security_credentials['username']).delete(event_date,cedula,id)        

class ApproveAbsenceJustificationUseCase(object):
    def execute(self,security_credentials,event_date,cedula,id):
        return JustificationAbsenceRepository(username=security_credentials['username']).approve(event_date,cedula,id)        

        

