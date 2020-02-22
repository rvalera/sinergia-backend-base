'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.models.security import SecurityElement, User
from app import redis_client
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from app.exceptions.base import CryptoPOSException, ConnectionException

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


class CacheRepository(object):

    DEFAULT_EXPIRED_TIME = 300

    def getByKey(self,key):
        value = redis_client.get(key)
        json_value = json.loads(value)        
        return json_value

    def save(self,key,payload,expired_time = int(DEFAULT_EXPIRED_TIME)):
        json_payload = json.dumps(payload)
        redis_client.set(key, json_payload,expired_time)



import urllib.parse

class CryptoPOSClient(object):

    username = None
    password = None
    token = None
    url_base = "http://localhost:5002"
    
    def __init__(self,username=None,password=None,token=None):
        self.username = username
        self.password = password
        self.token = token

    def executePost(self, end_point, payload, authenticate = True):
        
        json_response = None

        try:

            headers = {
                'content-type': "application/json",
                'cache-control': "no-cache"
            }
    
            json_payload = json.dumps(payload)
    
            final_url = urllib.parse.urljoin(self.url_base,end_point)
    
            if authenticate  and (self.username != None and self.password != None):
                response = requests.post(final_url ,\
                                         data=json_payload,\
                                         auth=HTTPBasicAuth(self.username,self.password ),\
                                         headers=headers)
            else:
                response = requests.post(final_url ,\
                                         data=json_payload,\
                                         headers=headers)
            
            response.raise_for_status()
            
        except HTTPError as http_err:           
            if response.status_code == 400:
                response_json = response.json()
                raise CryptoPOSException(text=response_json['message']['text'])
            else:
                raise ConnectionException(text='HTTP error occurred: %s' % http_err)
        except Exception as err:
            raise CryptoPOSException(text='Other error occurred: %s' % err)
        else:
            json_response = json.loads(response.text)
        
        return json_response

    def executePut(self, end_point, payload, authenticate = True):
        
        json_response = None

        try:

            headers = {
                'content-type': "application/json",
                'cache-control': "no-cache"
            }
    
            json_payload = json.dumps(payload)
    
            final_url = urllib.parse.urljoin(self.url_base,end_point)
    
            if authenticate  and (self.username != None and self.password != None):
                response = requests.put(final_url ,\
                                         data=json_payload,\
                                         auth=HTTPBasicAuth(self.username,self.password ),\
                                         headers=headers)
            else:
                response = requests.put(final_url ,\
                                         data=json_payload,\
                                         headers=headers)


            response.raise_for_status()
            
        except HTTPError as http_err:
            if response.status_code == 400:
                response_json = response.json()
                raise CryptoPOSException(text=response_json['message']['text'])
            else:
                raise ConnectionException(text='HTTP error occurred: %s' % http_err)
        except Exception as err:
            raise CryptoPOSException(text='Other error occurred: %s' % err)
        else:
            json_response = json.loads(response.text)
        
        return json_response


    def executeGet(self, end_point, params, authenticate = True):
        
        json_response = None

        try:

            headers = {
                'content-type': "application/json",
                'cache-control': "no-cache"
            }
    
            final_url = urllib.parse.urljoin(self.url_base,end_point)
    
            if authenticate  and (self.username != None and self.password != None):
                response = requests.get(final_url ,\
                                         params=params,\
                                         auth=HTTPBasicAuth(self.username,self.password ),\
                                         headers=headers)
            else:
                response = requests.get(final_url ,\
                                         params=params,\
                                         headers=headers)

            response.raise_for_status()
            
        except HTTPError as http_err:
            if response.status_code == 400:
                response_json = response.json()
                raise CryptoPOSException(text=response_json['message']['text'])
            else:
                raise ConnectionException(text='HTTP error occurred: %s' % http_err)
        except Exception as err:
            raise CryptoPOSException(text='Other error occurred: %s' % err)
        else:
            json_response = json.loads(response.text)
        
        return json_response

    def executeDelete(self, end_point, payload, authenticate = True):
        
        json_response = None

        try:

            headers = {
                'content-type': "application/json",
                'cache-control': "no-cache"
            }
    
            json_payload = json.dumps(payload)
    
            final_url = urllib.parse.urljoin(self.url_base,end_point)
    
            if authenticate  and (self.username != None and self.password != None):
                response = requests.delete(final_url ,\
                                         data=json_payload,\
                                         auth=HTTPBasicAuth(self.username,self.password ),\
                                         headers=headers)
            else:
                response = requests.delete(final_url ,\
                                         data=json_payload,\
                                         headers=headers)

            response.raise_for_status()
            
        except HTTPError as http_err:
            if response.status_code == 400:
                response_json = response.json()
                raise CryptoPOSException(text=response_json['message']['text'])
            else:
                raise ConnectionException(text='HTTP error occurred: %s' % http_err)
        except Exception as err:
            raise CryptoPOSException(text='Other error occurred: %s' % err)
        else:
            json_response = json.loads(response.text)
        
        return json_response


from .cryptopos import *
