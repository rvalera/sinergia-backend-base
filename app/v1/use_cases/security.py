'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.repository.base import SecurityElementRepository
from app.v1.repository.cryptopos import MemberRepository

class AuthenticateUseCase(object):
    securityElementRepository = SecurityElementRepository()
    
    def execute(self,username_or_token,password):
        security_element = self.securityElementRepository.getByAuthToken(username_or_token)
        if not security_element:
            security_element = self.securityElementRepository.getByName(username_or_token)
            if not security_element or not security_element.verify_password(password):
                return None
            else:
                return security_element
        else:
            return security_element

class GetMemberProfileUseCase(object):
    def execute(self,security_credentials,payload):
        return MemberRepository(username=security_credentials['username'],password=security_credentials['password']).get(payload)

class GetAnyMemberProfileUseCase(object):
    def execute(self,security_credentials,payload):
        return MemberRepository(username=security_credentials['username'],password=security_credentials['password']).getByEmail(payload)


class UpdateMemberProfileUseCase(object):
    def execute(self,security_credentials,payload):
        return MemberRepository(username=security_credentials['username'],password=security_credentials['password']).save(payload)

class MemberInitSignUpUseCase(object):
    def execute(self,payload):
        return MemberRepository().initCreate(payload)

class MemberFinishRegisterUseCase(object):
    def execute(self,security_credentials,payload):
        return MemberRepository(username=security_credentials['username'],password=security_credentials['password']).finishCreate(payload)

class ChangePasswordMemberUseCase(object):
    def execute(self,security_credentials,payload):
        return MemberRepository(username=security_credentials['username'],password=security_credentials['password']).changePassword(payload)

class ResetPasswordMemberUseCase(object):
    def execute(self,payload):
        return MemberRepository().resetPassword(payload)

