'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.repository.process import DailyMarkingRepository,OvertimeEventRepository,AbsenceEventRepository,JustificationAbsenceRepository,\
    BatchJustificationAbsenceRepository,BatchOvertimeRepository,ManualMarkingRepository

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

#################################################################################################################################

class GetBatchAbsenceJustificationUseCase(object):
    def execute(self,security_credentials,query_params):
        return BatchJustificationAbsenceRepository(username=security_credentials['username']).get(query_params)        

class NewBatchAbsenceJustificationUseCase(object):
    def execute(self,security_credentials,payload):
        return BatchJustificationAbsenceRepository(username=security_credentials['username']).new(payload)        

class SaveBatchAbsenceJustificationUseCase(object):
    def execute(self,security_credentials,payload):
        return BatchJustificationAbsenceRepository(username=security_credentials['username']).save(payload)        

class DeleteBatchAbsenceJustificationUseCase(object):
    def execute(self,security_credentials,id):
        return BatchJustificationAbsenceRepository(username=security_credentials['username']).delete(id)      

class GetDetailBatchAbsenceJustificationUseCase(object):
    def execute(self,security_credentials,id):
        return BatchJustificationAbsenceRepository(username=security_credentials['username']).getById(id)        

class ApproveBatchAbsenceJustificationUseCase(object):
    def execute(self,security_credentials,id):
        return BatchJustificationAbsenceRepository(username=security_credentials['username']).approve(id)        

#################################################################################################################################

class GetBatchOvertimeUseCase(object):
    def execute(self,security_credentials,query_params):
        return BatchOvertimeRepository(username=security_credentials['username']).get(query_params)        

class NewBatchOvertimeUseCase(object):
    def execute(self,security_credentials,payload):
        return BatchOvertimeRepository(username=security_credentials['username']).new(payload)        

class SaveBatchOvertimeUseCase(object):
    def execute(self,security_credentials,payload):
        return BatchOvertimeRepository(username=security_credentials['username']).save(payload)        

class DeleteBatchOvertimeUseCase(object):
    def execute(self,security_credentials,id):
        return BatchOvertimeRepository(username=security_credentials['username']).delete(id)        

class GetDetailBatchOvertimeUseCase(object):
    def execute(self,security_credentials,id):
        return BatchOvertimeRepository(username=security_credentials['username']).getById(id)        

class ApproveBatchOvertimeUseCase(object):
    def execute(self,security_credentials,id):
        return BatchOvertimeRepository(username=security_credentials['username']).approve(id)  

#################################################################################################################################


class GetManualMarkingUseCase(object):
    def execute(self,security_credentials,query_params):
        return ManualMarkingRepository(username=security_credentials['username']).get(query_params)        

class NewManualMarkingUseCase(object):
    def execute(self,security_credentials,payload):
        return ManualMarkingRepository(username=security_credentials['username']).new(payload)        

class SaveManualMarkingUseCase(object):
    def execute(self,security_credentials,payload):
        return ManualMarkingRepository(username=security_credentials['username']).save(payload)        

class DeleteManualMarkingUseCase(object):
    def execute(self,security_credentials,event_date,cedula,id):
        return ManualMarkingRepository(username=security_credentials['username']).delete(event_date,cedula,id)        

class GetDetailManualMarkingUseCase(object):
    def execute(self,security_credentials,event_date,cedula,id):
        return ManualMarkingRepository(username=security_credentials['username']).getById(event_date,cedula,id)        
