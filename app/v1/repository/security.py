'''
Created on 17 dic. 2019

@author: ramon
'''
from app.tools.utils import generate_alphanumeric_password
import datetime
from app.v1.models.constant import AUTOREGISTER, MOBILE_USER, STATUS_ACTIVE, STATUS_PENDING
from app.v1.models.security import SecurityElement, User, PersonExtension
from app import redis_client, db
from app.exceptions.base import DataAlreadyRegisteredException, DataNotFoundException, UserCurrentPasswordException,UserRepeatedPasswordException
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

    def getByEmail(self,email):
        result = User.query.filter(User.name == email).first()
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
        # TODO: Reiniciar la contrasena mediante un enlace de reinicio de contrasena
        raise NotImplementedException()
    
    def changeOperationKey(self,payload):
        # TODO: Cambiar la clave de operaciones especiales
        raise NotImplementedException()

    def resetOperationKey(self,payload):
        # TODO: Reiniciar la clave de operaciones especiales
        raise NotImplementedException()
    
    def initCreate(self,data):
        # raise NotImplementedException()
        user = self.getByEmail(data['email'])
        if user:
            raise DataAlreadyRegisteredException()
        
        # user_prov_passw = generate_alphanumeric_password()
        user_prov_passw = '12345'

        first_name =  data['first_name']
        last_name =  data['last_name']
    
        person = PersonExtension()
        person.email = data['email'].lower()
        person.first_name = data['first_name']
        person.last_name = data['last_name']
        person.fullname = data['first_name'] + ' ' + data['last_name']
        person.status = STATUS_ACTIVE
        db.session.add(person)

        user = User()
        user.person_extension = person
    
        user.hash_password(user_prov_passw)
        user.register_date = datetime.datetime.now() 
        user.name = data['email'].lower()
        user.status = STATUS_PENDING
        user.register_mode= AUTOREGISTER
        user.type = MOBILE_USER
        
        db.session.add(user)
        db.session.commit()

        # TODO: ENVIAR CORREO ELECTRONICO DE NOTIFICACION USANDO PLANTILLA

        return user


    def finishCreate(self,data):

        user = self.getByEmail(data['username'])
    
        if user is not None:

            print("Finishing Create User -> ")
        
            phone_number =  data['phone_number']
            gender =  data['gender']
            secondary_email =  data['secondary_email']
            birth_date =  data['birth_date']
            operation_key =  data['operation_key']
            password = data['password']
        
            user.hash_password(password.encode('utf-8'))
            user.hash_operation_key(operation_key.encode('utf-8'))
            user.person_extension.phone_number = phone_number
            user.person_extension.gender = gender
            user.person_extension.secondary_email = secondary_email
            user.person_extension.birth_date = birth_date
            user.status = STATUS_ACTIVE

            db.session.add(user)
            db.session.commit()            
        else:
            raise DataNotFoundException()
        
        return user

