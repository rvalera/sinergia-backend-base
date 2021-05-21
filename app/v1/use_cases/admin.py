'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.repository.security import SecurityElementRepository, UserRepository
from app.v1.repository.admin import MemberRepository, RolRepository

class GetAdminMemberListUseCase(object):
    def execute(self,security_credentials,query_params):
        return MemberRepository(username=security_credentials['username']).get(query_params)

class GetAdminMemberUseCase(object):
    def execute(self,security_credentials,query_params):
        return MemberRepository(username=security_credentials['username']).getByUsername(query_params['username'])

class DeleteAdminMemberUseCase(object):
    def execute(self,security_credentials,query_params):
        return MemberRepository(username=security_credentials['username']).deleteByUsername(query_params['username'])

class CreateAdminMemberUseCase(object):
    def execute(self,security_credentials,payload):
        MemberRepository(username=security_credentials['username']).new(payload)

class SaveAdminMemberUseCase(object):
    def execute(self,security_credentials,payload):
        MemberRepository(username=security_credentials['username']).save(payload)

class GetRolListUseCase(object):
    def execute(self,security_credentials,query_params):
        return RolRepository(username=security_credentials['username']).get(query_params)

class SaveRolUseCase(object):
    def execute(self,security_credentials,payload):
        return RolRepository(username=security_credentials['username']).save(payload)
