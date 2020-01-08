'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.models.security import SecurityElement
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


class CacheRepository(object):

    def getByKey(self,key):
        value = redis_client.get(key)
        json_value = json.loads(value)        
        return json_value


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
            raise ConnectionException(text='HTTP error occurred: %s' % http_err)
        except Exception as err:
            raise CryptoPOSException(text='Other error occurred: %s' % err)
        else:
            json_response = json.loads(response.text)
        
        return json_response


from .cryptopos import *

