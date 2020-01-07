'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.repository.auth import SecurityElementRepository

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
