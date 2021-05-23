'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.models.security import SecurityElement, User, PersonExtension, Rol, Privilege
from app.v1.models.hr import Trabajador,CentroCosto,TipoAusencia
from app.v1.models.constant import *

from app import redis_client, db
from app.exceptions.base import UserCurrentPasswordException,UserRepeatedPasswordException,RepositoryUnknownException
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from app.exceptions.base import CryptoPOSException, ConnectionException,NotImplementedException
from .base import SinergiaRepository

import pandas as pd
import hashlib
import datetime

class MemberRepository(SinergiaRepository):

    def get(self,query_params):
        # Definiendo Filter
        filter_criteria = {}
        if 'filter' in query_params:
            filter_criteria = query_params['filter']

        # Definiendo order
        order_criteria = []
        if 'order' in query_params:
            order_criteria = query_params['order']

        # Definiendo los Rangos de Paginacion
        limit = 10
        offset = 0
        low_limit = 0 
        high_limit = 9 
        query_range = [0,10]
        if 'range' in query_params:
            query_range = query_params['range']
            if len(query_range) >= 2:
                low_limit = query_range[0] 
                high_limit = query_range[1] 
            else:
                low_limit = query_range[0]
                high_limit = query_range[0] 
            limit = (high_limit - low_limit) + 1
            offset = low_limit 

        high_limit = high_limit + 1

        rows = User.query.filter_by(**filter_criteria).slice(low_limit,high_limit).all()
        count_result_rows = len(rows)
        count_all_rows = User.query.filter_by(**filter_criteria).count()

        return { 'count': count_result_rows, 'total':  count_all_rows  ,'data' : rows} 

    def getByUsername(self,p_username):
        user = User.query.filter(User.name == p_username).first()
        if user is None:
            raise RepositoryUnknownException()
        return user

    def deleteByUsername(self,p_username):
        user = self.getByUsername(p_username)
        db.session.delete(user)
        db.session.commit()

    def get_roles(self,payload):
        roles_list = []
        if 'roles' in payload:
            ids_roles = payload['roles']
            roles_list = Rol.query.filter(Rol.id.in_(ids_roles)).all()
        return roles_list

    def get_centro_costo(self,payload):
        centrocosto_list = []
        if 'extra_info' in payload and 'centroscosto' in payload['extra_info']:
            ids_centros_costo = payload['extra_info']['centroscosto']
            centrocosto_list = CentroCosto.query.filter(CentroCosto.codigo.in_(ids_centros_costo)).all()
        return centrocosto_list

    def new(self,payload):
        username = payload['name'] if 'name' in payload else None
        password = payload['password'] if 'password' in payload else None         

        if username and password:
            #Se chequea que el usuario NO exista previamente 
            user = User.query.filter(User.name == username).first()
            if not user is None:
                #Se arroja excepcion, el usuario ya esta creado
                raise RepositoryUnknownException()

            user = User()
            user.name = username
            user.hash_password(password)
            user.register_date = datetime.datetime.now() 

            user.status = STATUS_ACTIVE
            user.register_mode = FROM_BACKOFFICE
            user.type = CONSOLE_USER

            #Se Verifica si el usuario es un trabajador asociado a RH
            if 'extra_info' in payload:

                id_number = payload['extra_info']['id_number'] if 'id_number' in payload else ''
                first_name =  payload['extra_info']['first_name'] if 'first_name' in payload else ''
                last_name =  payload['extra_info']['last_name'] if 'last_name' in payload else ''
                phone_number =  payload['extra_info']['phone_number'] if 'phone_number' in payload else ''
                gender =  payload['extra_info']['gender'] if 'gender' in payload else ''

                user.person_extension = PersonExtension()

                if 'rrhh_info' in payload['extra_info'] and 'cedula' in payload['extra_info']['rrhh_info'] :
                    cedula = payload['extra_info']['rrhh_info']['cedula']
                    trabajador = Trabajador.query.filter(Trabajador.cedula == cedula).first()
                    if not trabajador is None:
                        #El Trabajador existe todos los datos del Usuario debe sacarse de esta tabla
                        id_number = trabajador.cedula
                        first_name =  trabajador.nombres
                        last_name =  trabajador.apellidos
                        phone_number =  trabajador.telefono
                        gender =  trabajador.sexo

                        user.person_extension.id_trabajador = cedula
                
                cecos = self.get_centro_costo(payload)
                if len(cecos):
                    user.person_extension.centroscosto = [c for c in cecos] 

                user.person_extension.id_number = id_number
                user.person_extension.first_name = first_name
                user.person_extension.last_name = last_name
                user.person_extension.fullname =  first_name + ' ' + last_name
                user.person_extension.phone_number = phone_number
                user.person_extension.gender = gender

            #Se procesan los Roles del Usuario
            roles = self.get_roles(payload) 
            if len(roles):
                user.roles = [r for r in roles]

            db.session.add(user)
            db.session.commit()            
        else:
            #No se proporciono el username o la contrasena, es obligatorio 
            raise RepositoryUnknownException()

    def save(self,payload):
        username = payload['name'] if 'name' in payload else None
        password = payload['password'] if 'password' in payload else None         

        if username:
            #Se chequea que el usuario NO exista previamente 
            user = User.query.filter(User.name == username).first()
            if user is None:
                #Se arroja excepcion, el usuario ya esta creado
                raise RepositoryUnknownException()

            if not password:
                raise RepositoryUnknownException()

            user.hash_password(password)
            user.register_date = datetime.datetime.now() 

            user.status = STATUS_ACTIVE
            user.register_mode = FROM_BACKOFFICE
            user.type = CONSOLE_USER

            #Se Verifica si el usuario es un trabajador asociado a RH
            if 'extra_info' in payload:
                id_number = payload['id_number'] if 'id_number' in payload else ''
                first_name =  payload['first_name'] if 'first_name' in payload else ''
                last_name =  payload['last_name'] if 'last_name' in payload else ''
                phone_number =  payload['phone_number'] if 'phone_number' in payload else ''
                gender =  payload['gender'] if 'gender' in payload else ''

                if 'rrhh_info' in payload['extra_info'] and 'cedula' in payload['extra_info']['rrhh_info'] :
                    cedula = payload['extra_info']['rrhh_info']['cedula']
                    trabajador = Trabajador.query.filter(Trabajador.cedula == cedula).first()
                    if not trabajador is None:
                        #El Trabajador existe todos los datos del Usuario debe sacarse de esta tabla
                        id_number = trabajador.cedula
                        first_name =  trabajador.nombres
                        last_name =  trabajador.apellidos
                        phone_number =  trabajador.telefono
                        gender =  trabajador.sexo

                        user.person_extension.id_trabajador = cedula
                
                cecos = self.get_centro_costo(payload)
                if len(cecos):
                    user.person_extension.centroscosto = [c for c in cecos] 

                user.person_extension.id_number = id_number
                user.person_extension.first_name = first_name
                user.person_extension.last_name = last_name
                user.person_extension.fullname =  first_name + ' ' + last_name
                user.person_extension.phone_number = phone_number
                user.person_extension.gender = gender

            #Se procesan los Roles del Usuario
            roles = self.get_roles(payload) 
            if len(roles):
                user.roles = [r for r in roles] 
            
            db.session.add(user)
            db.session.commit()            
        else:
            #No se proporciono el username o la contrasena, es obligatorio 
            raise RepositoryUnknownException()

class RolRepository(SinergiaRepository):

    def get_privileges(self,payload):
        tipos_ausencias_list = []
        if 'privileges' in payload:
            ids_privileges = payload['privileges']
            privileges_list = Privilege.query.filter(Privilege.name.in_(ids_privileges)).all()
        return privileges_list    

    def get_tipos_ausencias(self,payload):
        tipos_ausencias_list = []
        if 'tipos_ausencias' in payload:
            ids_tipos_ausencias = payload['tipos_ausencias']
            tipos_ausencias_list = TipoAusencia.query.filter(TipoAusencia.codigo.in_(ids_tipos_ausencias)).all()
        return tipos_ausencias_list    

    def get(self,query_params):
        rows = Rol.query.all()
        count_result_rows = len(rows)
        count_all_rows = Rol.query.count()
        return { 'count': count_result_rows, 'total':  count_all_rows  ,'data' : rows} 

    def save(self,payload):
        rol_name = payload['name'] if 'name' in payload else None
        if rol_name:
            rol = Rol.query.filter(Rol.name == rol_name).first()
            if rol is None:
                raise RepositoryUnknownException()

            tipos_ausencias = self.get_tipos_ausencias(payload)
            if len(tipos_ausencias):
                rol.tipos_ausencias = [t for t in tipos_ausencias] 

            privileges = self.get_privileges(payload)
            if len(privileges):
                rol.privileges = [p for p in privileges] 

            db.session.add(rol)
            db.session.commit()
        else:
            raise RepositoryUnknownException()

