'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.models.security import SecurityElement, User, PersonExtension
from app import redis_client, db
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from app.exceptions.base import CryptoPOSException, ConnectionException,NotImplementedException
from .base import SinergiaRepository

import pandas as pd


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
        data = self.executePut('/api/v2/mobile_user/%s' % payload['id'], payload)
        return data
    
    def changePassword(self,payload):
        data = self.executePut('/api/v2/user/password/%s' % payload['id'], payload)
        return data

    def resetPassword(self,payload):
        data = self.executePost('/api/v2/user/reset_user_password/%s' % payload['email'], payload)
        return data
    
    def changeOperationKey(self,payload):
        raise NotImplementedException()

    def resetOperationKey(self,payload):
        raise NotImplementedException()
    
    def initCreate(self,data):
        raise NotImplementedException()

    def finishCreate(self,data):
        raise NotImplementedException()



