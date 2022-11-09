'''
Created on 17 dic. 2019

@author: ramon
'''
from app.tools.substrate import Substrate
from app.v1.models.security import SecurityElement, User, PersonExtension
from app import redis_client
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from app.exceptions.base import BiostartException, CryptoPOSException, ConnectionException

class CacheRepository(object):

    DEFAULT_EXPIRED_TIME = 300

    def getByKey(self,key):
        value = redis_client.get(key)
        json_value = json.loads(value)        
        return json_value

    def save(self,key,payload,expired_time = int(DEFAULT_EXPIRED_TIME)):
        json_payload = json.dumps(payload)
        redis_client.set(key, json_payload,ex=expired_time)

class SinergiaRepository(object):
    username = None
    token = None

    def getUser(self):
        user = User.query.filter(User.name==self.username.lower()).first()        
        return user       

    def __init__(self,username=None,token=None):
        self.username = username        
        self.token = token

class SubstrateRepository(object):
    substrate = None
    username = None

    def __init__(self,username=None):
        self.username = username        
        self.substrate = Substrate()


# import urllib.parse

# class BiostarClient(object):

#     url_base = "http://localhost:3005"
    
#     def __init__(self,url_base=None):
#         if (not url_base is None):
#             self.url_base = url_base

#     def executePost(self, end_point, payload, authenticate = True):
#         json_response = None
#         try:
#             headers = {
#                 'content-type': "application/json",
#                 'cache-control': "no-cache"
#             }
    
#             json_payload = json.dumps(payload)
    
#             final_url = urllib.parse.urljoin(self.url_base,end_point)
#             response = requests.post(final_url ,data=json_payload,headers=headers)

#             response.raise_for_status()
#         except HTTPError as http_err:           
#             if response.status_code == 400:
#                 response_json = response.json()
#                 raise BiostartException(text=response_json['message']['text'])
#             else:
#                 raise ConnectionException(text='HTTP error occurred: %s' % http_err)
#         except Exception as err:
#             raise BiostartException(text='Other error occurred: %s' % err)
#         else:
#             json_response = json.loads(response.text)
        
#         return json_response


#     def executeGet(self, end_point, params, authenticate = True):
#         json_response = None
#         try:

#             headers = {
#                 'content-type': "application/json",
#                 'cache-control': "no-cache"
#             }
    
#             final_url = urllib.parse.urljoin(self.url_base,end_point)
#             response = requests.get(final_url ,params=params,headers=headers)
#             response.raise_for_status()
            
#         except HTTPError as http_err:
#             if response.status_code == 400:
#                 response_json = response.json()
#                 raise BiostartException(text=response_json['message']['text'])
#             else:
#                 raise ConnectionException(text='HTTP error occurred: %s' % http_err)
#         except Exception as err:
#             raise BiostartException(text='Other error occurred: %s' % err)
#         else:
#             json_response = json.loads(response.text)
        
#         return json_response

# from .cryptopos import *
