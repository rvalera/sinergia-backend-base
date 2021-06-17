'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.models.security import SecurityElement, User, PersonExtension
from app.v1.models.hr import Trabajador
from app import redis_client, db
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from app.exceptions.base import CryptoPOSException, ConnectionException,NotImplementedException,DatabaseException,IntegrityException
from .base import SinergiaRepository

from app.exceptions.base import RepositoryUnknownException,DataNotFoundException

import pandas as pd
import logging

from sqlalchemy import text    
from sqlalchemy import select 

from psycopg2 import OperationalError, errorcodes, errors    
from sqlalchemy import exc


class CargoRepository(SinergiaRepository):
    def get(self,query_params):
        sql = '''
        SELECT * FROM integrador.cargos
        {conditions}
        {order_by}
        {limits_offset}
        '''
        count_sql = '''
        SELECT COUNT(*) count_rows  FROM integrador.cargos
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

                    if 'descripcion' in filter_conditions:
                        conditions.append("descripcion LIKE '%{descripcion}%' ")

                    if 'codigo_rrhh' in filter_conditions:
                        conditions.append("codigo_rrhh LIKE '%{codigo_rrhh}%' ")


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


class CentroCostoRepository(SinergiaRepository):
    def get(self,query_params):
        sql = '''
        SELECT * FROM integrador.centro_costo
        {conditions}
        {order_by}
        {limits_offset}
        '''
        count_sql = '''
        SELECT COUNT(*) count_rows  FROM integrador.centro_costo
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
    
                    if 'descripcion' in filter_conditions:
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

        


class ConceptoNominaRepository(SinergiaRepository):
    def get(self,query_params):

        sql = '''
        SELECT * FROM integrador.conceptos_nomina
        {conditions}
        {order_by}
        {limits_offset}
        '''
        count_sql = '''
        SELECT COUNT(*) count_rows  FROM integrador.conceptos_nomina        
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
                        conditions.append('codigo  = {codigo}')

                    if 'descripcion' in filter_conditions:
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


class DispositivoRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from integrador.dispositivos',con=db.engine)
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

class EstatusTrabajadorRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from integrador.estatus_trabajador',con=db.engine)
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

class TipoAusenciaRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from integrador.tipos_ausencias',con=db.engine)
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

class TipoNominaRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from integrador.tipos_de_nomina',con=db.engine)
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

#################################################################################################################

class TrabajadorRepository(SinergiaRepository):

    def get(self,query_params):

        sql = '''
        SELECT  * 
        FROM integrador.vw_trabajador t
        {conditions}
        {order_by}
        {limits_offset}
        '''
        count_sql = '''
        SELECT COUNT(*) count_rows 
        FROM integrador.vw_trabajador t
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
                    if 'cedula_trabajador' in filter_conditions:
                        conditions.append('t.cedula  = {cedula_trabajador}')

                    if 'id_centro_costo' in filter_conditions:
                        if type(filter_conditions['id_centro_costo']) == str :
                            conditions.append("t.id_centro_costo = '{id_centro_costo}' ")
                        else:
                            if type(filter_conditions['id_centro_costo'] is list) and len(filter_conditions['id_centro_costo']) > 1:
                                filter_conditions['id_centro_costo'] = tuple(filter_conditions['id_centro_costo'])
                                conditions.append('t.id_centro_costo IN {id_centro_costo}')
                            else:
                                filter_conditions['id_centro_costo'] = (filter_conditions['id_centro_costo'][0])
                                conditions.append("t.id_centro_costo = '{id_centro_costo}' ")
                            

                    if 'id_tipo_nomina' in filter_conditions:
                        if type(filter_conditions['id_tipo_nomina']) == str:
                            conditions.append("t.id_tipo_nomina = '{id_tipo_nomina}' ")
                        else:
                            if type(filter_conditions['id_tipo_nomina'] is list) and len(filter_conditions['id_tipo_nomina']) > 1:
                                filter_conditions['id_tipo_nomina'] = tuple(filter_conditions['id_tipo_nomina'])   
                                conditions.append('t.id_tipo_nomina IN {id_tipo_nomina}')
                            else:
                                filter_conditions['id_tipo_nomina'] = (filter_conditions['id_tipo_nomina'][0])
                                conditions.append("t.id_tipo_nomina = '{id_tipo_nomina}' ")
                            

                    if 'id_estatus' in filter_conditions:
                        if type(filter_conditions['id_estatus']) == str:
                            conditions.append("t.id_estatus = '{id_estatus}' ")
                        else:
                            if type(filter_conditions['id_estatus'] is list) and len(filter_conditions['id_estatus']) > 1:
                                filter_conditions['id_estatus'] = tuple(filter_conditions['id_estatus'])   
                                conditions.append('t.id_estatus IN {id_estatus}')
                            else:
                                filter_conditions['id_estatus'] = (filter_conditions['id_estatus'][0])
                                conditions.append("t.id_estatus = '{id_estatus}' ")
                            

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
            textual_sql = text(sql)
            rows = db.session.query(Trabajador).from_statement(textual_sql).all()
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


class TipoTrabajadorRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from integrador.tipo_trabajador',con=db.engine)
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

class GrupoGuardiaRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from integrador.grupo_guardia',con=db.engine)
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)
