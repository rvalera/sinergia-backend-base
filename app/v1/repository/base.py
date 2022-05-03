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


# from .cryptopos import *
