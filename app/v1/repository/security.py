'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.models.security import SecurityElement, User, PersonExtension
from app import redis_client, db
from app.exceptions.base import UserCurrentPasswordException,UserRepeatedPasswordException
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from app.exceptions.base import CryptoPOSException, ConnectionException,NotImplementedException
from .base import SinergiaRepository

import pandas as pd
import hashlib

class SecurityElementRepository(object):
    
    def getByAuthToken(self,token):
        security_element = SecurityElement.verify_auth_token(token)
        return security_element
    
    def getByName(self,name):
        security_element = SecurityElement.query.filter(SecurityElement.name==name.lower()).first()
        return security_element

class UserRepository(object):
    
    def getByName(self,name):
        user = User.query.filter(User.name==name.lower()).first()
        return user

class MemberRepository(SinergiaRepository):

    def get(self,query_params,full=False):
        result = User.query.filter(User.name == self.username).first()
        return result

    def getByEmail(self,query_params):
        result = User.query.filter(User.name == query_params['email']).first()
        return result
    
    def save(self,payload):
        user = User.query.filter(User.name == self.username).first()
        
        first_name =  payload['first_name']
        last_name =  payload['last_name']
        phone_number =  payload['phone_number']
        gender =  payload['gender']
        secondary_email =  payload['secondary_email']
        birth_date =  payload['birth_date']
    
        user.person_extension.first_name = first_name
        user.person_extension.last_name = last_name
        user.person_extension.fullname =  first_name + ' ' + last_name
        user.person_extension.phone_number = phone_number
        user.person_extension.gender = gender
        user.person_extension.secondary_email = secondary_email
        user.person_extension.birth_date = birth_date

        db.session.add(user)
        db.session.commit()
    
    def changePassword(self,payload):

        user = User.query.filter(User.name == self.username).first()

        new_password = payload['password']
        old_password = payload['old_password']        

        if not user.verify_password(old_password):
            raise UserCurrentPasswordException()
        
        if (new_password is not None) and (new_password != ''):
            new_password_hash = hashlib.md5(new_password.encode('utf-8')).hexdigest()
            if new_password_hash == user.password_hash:
                raise UserRepeatedPasswordException()
            user.hash_password(new_password)
            
        db.session.add(user)
        db.session.commit()        


    def resetPassword(self,payload):
        raise NotImplementedException()
    
    def changeOperationKey(self,payload):
        raise NotImplementedException()

    def resetOperationKey(self,payload):
        raise NotImplementedException()
    
    def initCreate(self,data):
        raise NotImplementedException()

    def finishCreate(self,data):
        raise NotImplementedException()



