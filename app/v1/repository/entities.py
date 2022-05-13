'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.models.security import SecurityElement, User, PersonExtension
from app.v1.models.hr import Beneficiario, HistoriaMedica, Persona,Estado,Municipio,Trabajador,TipoTrabajador,EstatusTrabajador,TipoNomina,\
    TipoCargo,UbicacionLaboral,Empresa, Patologia
from app import redis_client, db
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from app.exceptions.base import CryptoPOSException, ConnectionException,NotImplementedException,DatabaseException,IntegrityException, ParametersNotFoundException
from .base import SinergiaRepository

from app.exceptions.base import DataNotFoundException

import pandas as pd
import logging

from sqlalchemy import text    
from sqlalchemy import select 

from psycopg2 import OperationalError, errorcodes, errors    
from sqlalchemy import exc
from datetime import datetime


class TipoCargoRepository(SinergiaRepository):
    def get(self,query_params):
        sql = '''
        SELECT * FROM hospitalario.tipocargo
        {conditions}
        {order_by}
        {limits_offset}
        '''
        count_sql = '''
        SELECT COUNT(*) count_rows  FROM hospitalario.tipocargo
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
                    if 'codigo' in filter_conditions:
                        conditions.append("codigo  = '{codigo}' ")

                    if 'nombre' in filter_conditions:
                        conditions.append("descripcion LIKE '%{descripcion}%' ")

                    where_clausule = 'WHERE ' + ' AND '.join(conditions)
                    where_clausule = where_clausule.format(**filter_conditions)

                    parameters['conditions'] = where_clausule
            
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

        try:
            table_df = pd.read_sql_query(sql,con=db.engine)
            rows = table_df.to_dict('records')
            count_result_rows = limit

            count_sql = count_sql.format(**parameters)
            count_df = pd.read_sql_query(count_sql,con=db.engine)
            result_count = count_df.to_dict('records')
            count_all_rows = result_count[0]['count_rows']

            return  { 'count': count_result_rows, 'total':  count_all_rows  ,'data' : rows}
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)


class EstatusTrabajadorRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from hospitalario.estatustrabajador',con=db.engine)
            table_df = table_df.fillna('')
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

class TipoNominaRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from hospitalario.tiponomina',con=db.engine)
            table_df = table_df.fillna('')
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

class UbicacionLaboralRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from hospitalario.ubicacionlaboral',con=db.engine)
            table_df = table_df.fillna('')
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

class TipoTrabajadorRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from hospitalario.tipotrabajador',con=db.engine)
            table_df = table_df.fillna('')
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

class EmpresaRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from hospitalario.empresa',con=db.engine)
            table_df = table_df.fillna('')
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

class EstadoRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from hospitalario.estado',con=db.engine)
            table_df = table_df.fillna('')
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

class MunicipioRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from hospitalario.municipio',con=db.engine)
            table_df = table_df.fillna('')
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

#################################################################################################################

class PersonaRepository(SinergiaRepository):

    def get(self,query_params):

        sql = '''
        SELECT  * 
        FROM hospitalario.persona t
        {conditions}
        {order_by}
        {limits_offset}
        '''
        count_sql = '''
        SELECT COUNT(*) count_rows 
        FROM hospitalario.persona t
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
                    if 'cedula' in filter_conditions:
                        conditions.append("t.cedula  = '{cedula}' ")

                    if 'apellidos' in filter_conditions:
                        conditions.append("t.apellidos  LIKE '%{apellidos}% ")

                    if 'nombres' in filter_conditions:
                        conditions.append("t.nombres  LIKE '%{nombres}%  ")
                        

                    where_clausule = 'WHERE ' + ' AND '.join(conditions)
                    where_clausule = where_clausule.format(**filter_conditions)

                    parameters['conditions'] = where_clausule
            
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

        textual_sql = text(sql)
        rows = db.session.query(Persona).from_statement(textual_sql).all()
        count_result_rows = len(rows)

        count_sql = count_sql.format(**parameters)
        count_df = pd.read_sql_query(count_sql,con=db.engine)
        result_count = count_df.to_dict('records')
        count_all_rows = result_count[0]['count_rows']

        return { 'count': count_result_rows, 'total':  count_all_rows  ,'data' : rows} 

    def getByCedula(self,cedula):
        try:
            persona = Persona.query.filter(Persona.cedula == cedula).first()
            if persona is None:
                raise DataNotFoundException()
            return persona
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)


class TrabajadorRepository(SinergiaRepository):

    def get(self,query_params):

        sql = '''
        SELECT t.*
        FROM hospitalario.trabajador t 
        join hospitalario.persona p on p.cedula = t.cedula
        {conditions}
        {order_by}
        {limits_offset}
        '''
        count_sql = '''
        SELECT COUNT(*) count_rows
        FROM hospitalario.trabajador t 
        join hospitalario.persona p on p.cedula = t.cedula
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
                    if 'cedula' in filter_conditions:
                        conditions.append('p.cedula  = {cedula}')

                    if 'apellidos' in filter_conditions:
                        conditions.append("p.apellidos  LIKE '%{apellidos}% ")

                    if 'nombres' in filter_conditions:
                        conditions.append("p.nombres  LIKE '%{nombres}%  ")                        

                    if 'codigoempresa' in filter_conditions:
                        if type(filter_conditions['codigoempresa']) == str :
                            conditions.append("t.codigoempresa = '{codigoempresa}' ")
                        else:
                            if type(filter_conditions['codigoempresa'] is list) and len(filter_conditions['codigoempresa']) > 1:
                                filter_conditions['codigoempresa'] = tuple(filter_conditions['codigoempresa'])
                                conditions.append('t.codigoempresa IN {codigoempresa}')
                            else:
                                filter_conditions['codigoempresa'] = (filter_conditions['codigoempresa'][0])
                                conditions.append("t.codigoempresa = '{codigoempresa}' ")
                            

                    where_clausule = 'WHERE ' + ' AND '.join(conditions)
                    where_clausule = where_clausule.format(**filter_conditions)

                    parameters['conditions'] = where_clausule
            
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

        textual_sql = text(sql)
        rows = db.session.query(Trabajador).from_statement(textual_sql).all()
        count_result_rows = len(rows)

        count_sql = count_sql.format(**parameters)
        count_df = pd.read_sql_query(count_sql,con=db.engine)
        result_count = count_df.to_dict('records')
        count_all_rows = result_count[0]['count_rows']

        return { 'count': count_result_rows, 'total':  count_all_rows  ,'data' : rows } 


    def getByCedula(self,cedula):
        try:
            trabajador = Trabajador.query.filter(Trabajador.cedula == cedula).first()
            if trabajador is None:
                raise DataNotFoundException()
            return trabajador
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

class EstadoRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from hospitalario.estado',con=db.engine)
            table_df = table_df.fillna('')
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

    
class MunicipioRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from hospitalario.municipio',con=db.engine)
            table_df = table_df.fillna('')
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)


class PatologiaRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from hospitalario.patologia',con=db.engine)
            table_df = table_df.fillna('')
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)


class BeneficiarioRepository(SinergiaRepository):

    def get_patologias(self,payload):
        patologias_list = []
        if 'patologias' in payload:
            ids_patologias = payload['patologias']
            patologias_list = Patologia.query.filter(Patologia.codigopatologia.in_(ids_patologias)).all()
        return patologias_list

    def new(self,payload):
        cedula = payload['cedula'] if 'cedula' in payload else None
        if cedula:
            #Se chequea que el beneficario NO exista previamente 
            aux = Beneficiario.query.filter(Beneficiario.cedula == cedula).first()
            if aux:
                #Se arroja excepcion, el beneficiario ya esta creado
                raise DataNotFoundException()

            beneficiario = Beneficiario()
            beneficiario.cedula             = payload['cedula']
            beneficiario.cedulatrabajador   = payload['cedulatrabajador']
            beneficiario.vinculo            = payload['vinculo']

            beneficiario.nombres            = payload['nombres']
            beneficiario.apellidos          = payload['apellidos']
            beneficiario.sexo               = payload['sexo']
            beneficiario.fechanacimiento    = payload['fechanacimiento']
            
            historiamedica = HistoriaMedica()
            historiamedica.cedula = cedula
            historiamedica.gruposanguineo = payload['gruposanguineo']
            historiamedica.discapacidad   = payload['tipodiscapacidad']
            historiamedica.fecha          = datetime.now().date()
            
            #Se procesan las Patologias de la Historia Medica
            patologias = self.get_patologias(payload) 
            if len(patologias):
                historiamedica.patologias = [p for p in patologias] 
           
            db.session.add(historiamedica)
            db.session.add(beneficiario)
            db.session.commit()            
        else:
            #No se proporciono el username o la contrasena, es obligatorio 
            raise ParametersNotFoundException()

    
    def save(self,payload):
        cedula = payload['cedula'] if 'cedula' in payload else None
        if cedula:
            #Se chequea que el beneficario NO exista previamente 
            beneficiario = Beneficiario.query.filter(Beneficiario.cedula == cedula).first()
            if beneficiario is None:
                #Se arroja excepcion, el beneficiario ya esta creado
                raise DataNotFoundException()

            beneficiario.cedula             = payload['cedula']
            beneficiario.cedulatrabajador   = payload['cedulatrabajador']
            beneficiario.vinculo            = payload['vinculo']

            beneficiario.nombres            = payload['nombres']
            beneficiario.apellidos          = payload['apellidos']
            beneficiario.sexo               = payload['sexo']
            beneficiario.fechanacimiento    = payload['fechanacimiento']

            beneficiario.historiamedica.gruposanguineo = payload['gruposanguineo']
            beneficiario.historiamedica.discapacidad   = payload['tipodiscapacidad']

            #Se procesan las Patologias de la Historia Medica
            patologias = self.get_patologias(payload) 
            if len(patologias) > 0:
                beneficiario.historiamedica.patologias = [p for p in patologias] 
            else:
                beneficiario.historiamedica.patologias = []

            db.session.add(beneficiario)
            db.session.commit()            
        else:
            #No se proporciono el username o la contrasena, es obligatorio 
            raise ParametersNotFoundException()
    

    def delete(self,cedula):
        beneficiario = Beneficiario.query.filter(Beneficiario.cedula == cedula).first()
        if beneficiario is None:
            #Se arroja excepcion, el beneficiario ya esta creado
            raise DataNotFoundException()
        historia = HistoriaMedica.query.filter(HistoriaMedica.cedula == cedula).first()
        db.session.delete(historia)
        db.session.delete(beneficiario)
        db.session.commit()