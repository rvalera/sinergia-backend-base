'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.models.security import SecurityElement, User, PersonExtension, Rol, Privilege
from app.v1.models.hr import Empresa
from app.v1.models.constant import *

from app import redis_client, db
from app.exceptions.base import UserCurrentPasswordException,UserRepeatedPasswordException,RepositoryUnknownException,DataNotFoundException,ParametersNotFoundException
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from app.exceptions.base import CryptoPOSException, ConnectionException,NotImplementedException,ParametersNotFoundException,DataNotFoundException,DatabaseException,IntegrityException
from .base import SinergiaRepository

import pandas as pd
import hashlib
import datetime

from sqlalchemy import text    
from sqlalchemy import select    

from psycopg2 import OperationalError, errorcodes, errors        
from sqlalchemy import exc

class MemberRepository(SinergiaRepository):

    def get(self,query_params):
        sql = '''
        SELECT DISTINCT s.*
        FROM securityelement s
        JOIN "user" u 
        ON s.id = u.id 
        JOIN personextension pe
        ON u.person_extension_id = pe.id
        LEFT JOIN securityelement_rol sr 
        ON s.id = sr.securityelement_id 
        LEFT JOIN rol r 
        ON sr.rol_id = r.id  
        {conditions}
        {order_by}
        {limits_offset}
        '''

        count_sql = '''
        SELECT COUNT(DISTINCT s.*) count_rows
        FROM securityelement s
        JOIN "user" u 
        ON s.id = u.id 
        JOIN personextension pe
        ON u.person_extension_id = pe.id
        LEFT JOIN securityelement_rol sr 
        ON s.id = sr.securityelement_id 
        LEFT JOIN rol r 
        ON sr.rol_id = r.id  
        {conditions}
        '''

        parameters = {'conditions' : '', 'order_by': '', 'limits_offset': ''}

        limit = 10
        offset = 0        
        if len(query_params) > 0:

            if 'filter' in query_params:
                filter_conditions = query_params['filter']

                if len(filter_conditions) > 0 :

                    conditions = []         

                    if 'username' in filter_conditions:
                        conditions.append("s.name  LIKE  '%{username}%' ")

                    if 'cedula' in filter_conditions:
                        conditions.append("pe.id_number LIKE '%{cedula}%' ")

                    if 'first_name' in filter_conditions:
                        conditions.append("pe.first_name LIKE '%{first_name}%' ")

                    if 'last_name' in filter_conditions:
                        conditions.append("pe.last_name LIKE '%{last_name}%' ")

                    if 'rolname' in filter_conditions:
                        if type(filter_conditions['rolname']) == str:
                            conditions.append("r.name = '{rolname}' ")
                        else:
                            if type(filter_conditions['rolname'] is list) and len(filter_conditions['rolname']) > 1:
                                filter_conditions['rolname'] = tuple(filter_conditions['rolname'])    
                                conditions.append('r.name IN {rolname}')
                            else:
                                filter_conditions['rolname'] = (filter_conditions['rolname'][0])
                                conditions.append("r.name = '{rolname}' ")
                    
                    if len(conditions) > 0: 
                        if len(conditions) > 1:
                            where_clausule = 'WHERE ' + ' AND '.join(conditions)
                            where_clausule = where_clausule.format(**filter_conditions)
                        else:
                            where_clausule = 'WHERE ' + ' '.join(conditions)
                            where_clausule = where_clausule.format(**filter_conditions)

                        parameters['conditions'] = where_clausule
                    else:
                        parameters['conditions'] = ''

            # Definiendo order
            if 'order' in query_params:
                order_criteria = query_params['order']
                order_fields = ','.join(order_criteria)
                parameters['order_by'] = 'ORDER BY ' + order_fields


        # Definiendo los Rangos de Paginacion
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
        parameters['limits_offset'] = ' LIMIT %s OFFSET %s ' % (limit,offset)

        sql = sql.format(**parameters)
        print(sql)

        try:

            textual_sql = text(sql)
            rows = db.session.query(User).from_statement(textual_sql).all()
            count_result_rows = len(rows)

            count_sql = count_sql.format(**parameters)
            count_df = pd.read_sql_query(count_sql,con=db.engine)
            result_count = count_df.to_dict('records')
            count_all_rows = result_count[0]['count_rows']

            return { 'count': count_result_rows, 'total':  count_all_rows  ,'data' : rows} 

        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)


    def getByUsername(self,p_username):
        user = User.query.filter(User.name == p_username).first()
        if user is None:
            raise DataNotFoundException()
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

    def new(self,payload):
        username = payload['name'] if 'name' in payload else None
        password = payload['password'] if 'password' in payload else None         

        if username and password:
            #Se chequea que el usuario NO exista previamente 
            user = User.query.filter(User.name == username).first()
            if not user is None:
                #Se arroja excepcion, el usuario ya esta creado
                raise DataNotFoundException()

            user = User()
            user.name = username
            user.hash_password(password)
            user.register_date = datetime.datetime.now() 

            user.status = STATUS_ACTIVE
            user.register_mode = FROM_BACKOFFICE
            user.type = CONSOLE_USER

            #Se Verifica si el usuario es un trabajador asociado a RH
            if 'extra_info' in payload:

                id_number = payload['extra_info']['id_number'] if 'id_number' in payload['extra_info'] else ''
                first_name =  payload['extra_info']['first_name'] if 'first_name' in payload['extra_info'] else ''
                last_name =  payload['extra_info']['last_name'] if 'last_name' in payload['extra_info'] else ''

                phone_number =  payload['extra_info']['phone_number'] if 'phone_number' in payload['extra_info'] else ''
                gender =  payload['extra_info']['gender'] if 'gender' in payload['extra_info'] else ''
                email =  payload['extra_info']['email'] if 'email' in payload['extra_info'] else ''

                user.person_extension = PersonExtension()

                # Actualizar la empresa si viniera en el Payload / Esto es Opcional
                if 'empresa' in payload['extra_info'] \
                    and 'codigo' in payload['extra_info']['empresa'] :
                    empresa_id = payload['extra_info']['empresa']['codigo']
                    empresa = Empresa.query.filter(Empresa.codigo == empresa_id).first()
                    if not empresa is None:
                        user.person_extension.empresa_id = empresa_id
                    else:
                        user.person_extension.empresa_id = None


                user.person_extension.id_number = id_number
                user.person_extension.first_name = first_name
                user.person_extension.last_name = last_name
                user.person_extension.fullname =  first_name + ' ' + last_name
                user.person_extension.phone_number = phone_number
                user.person_extension.email = email
                user.person_extension.gender = gender

            #Se procesan los Roles del Usuario
            roles = self.get_roles(payload) 
            if len(roles):
                user.roles = [r for r in roles]

            db.session.add(user)
            db.session.commit()            
        else:
            #No se proporciono el username o la contrasena, es obligatorio 
            raise ParametersNotFoundException('El nombre de usuario y contrasena son obligatorios')

    def save(self,payload):
        username = payload['name'] if 'name' in payload else None
        password = payload['password'] if 'password' in payload else None         

        if username:
            #Se chequea que el usuario NO exista previamente 
            user = User.query.filter(User.name == username).first()
            if user is None:
                #Se arroja excepcion, el usuario ya esta creado
                raise DataNotFoundException()

            if not password:
                raise ParametersNotFoundException('Debe proporcionar una contrasena de Usuario')

            user.hash_password(password)
            user.register_date = datetime.datetime.now() 

            user.status = STATUS_ACTIVE
            user.register_mode = FROM_BACKOFFICE
            user.type = CONSOLE_USER

            #Se Verifica si el usuario es un trabajador asociado a RH
            if 'extra_info' in payload:
                id_number = payload['extra_info']['id_number'] if 'id_number' in payload['extra_info'] else ''
                first_name =  payload['extra_info']['first_name'] if 'first_name' in payload['extra_info'] else ''
                last_name =  payload['extra_info']['last_name'] if 'last_name' in payload['extra_info'] else ''
                phone_number =  payload['extra_info']['phone_number'] if 'phone_number' in payload['extra_info'] else ''
                gender =  payload['extra_info']['gender'] if 'gender' in payload['extra_info'] else ''
                email =  payload['extra_info']['email'] if 'email' in payload['extra_info'] else ''

                # Actualizar la empresa si viniera en el Payload / Esto es Opcional
                if 'empresa' in payload['extra_info'] \
                    and 'codigo' in payload['extra_info']['empresa'] :
                    empresa_id = payload['extra_info']['empresa']['codigo']
                    empresa = Empresa.query.filter(Empresa.codigo == empresa_id).first()
                    if not empresa is None:
                        user.person_extension.empresa_id = empresa_id
                    else:
                        user.person_extension.empresa_id = None

               
                user.person_extension.id_number = id_number
                user.person_extension.first_name = first_name
                user.person_extension.last_name = last_name
                user.person_extension.fullname =  first_name + ' ' + last_name
                user.person_extension.phone_number = phone_number
                user.person_extension.email = email
                user.person_extension.gender = gender

            #Se procesan los Roles del Usuario
            roles = self.get_roles(payload) 
            if len(roles):
                user.roles = [r for r in roles] 
            
            db.session.add(user)
            db.session.commit()            
        else:
            #No se proporciono el username o la contrasena, es obligatorio 
            raise ParametersNotFoundException()

class RolRepository(SinergiaRepository):

    def get_privileges(self,payload):
        privileges_list = []
        if 'privileges' in payload:
            ids_privileges = payload['privileges']
            privileges_list = Privilege.query.filter(Privilege.name.in_(ids_privileges)).all()
        return privileges_list    

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
                raise DataNotFoundException() 

            privileges = self.get_privileges(payload)
            if len(privileges):
                rol.privileges = [p for p in privileges] 

            db.session.add(rol)
            db.session.commit()
        else:
            raise DataNotFoundException()

