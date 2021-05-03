'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.models.security import SecurityElement, User, PersonExtension
from app import redis_client
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from app.exceptions.base import CryptoPOSException, ConnectionException

class PersonExtensionRepository(object):

    def getById(self,id):
        person_extension = PersonExtension.query.filter( PersonExtension.id_number == id).first()
        return person_extension


class MemberRepository(object):
    
    def get(self,query_params,full=False):
        request_params = {}
        result = {}
        if full:
            result = self.executeGet('/api/v2/user/detail', request_params)
        else:
            result = self.executeGet('/api/v2/person/%s/A' % self.username, request_params)

        return result


    def getByEmail(self,query_params):
        request_params = {}
        result = self.executeGet('/api/v2/person/%s/A' % query_params['email'], request_params)
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
        data = self.executePut('/api/v2/user/operation_key/%s' % payload['id'], payload)
        return data

    def resetOperationKey(self,payload):
        data = self.executePost('/api/v2/user/reset_password/%s' % self.username, payload)
        return data
    
    def initCreate(self,data):
        result = self.executePost('/api/v2/mobile_user', data)
        return result

    def finishCreate(self,data):
        result = self.executePost('/api/v2/app_person/%s' % data['id'], data)
        return result
