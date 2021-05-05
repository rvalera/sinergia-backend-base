'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.models.security import SecurityElement, User, PersonExtension
from app import redis_client, db
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from app.exceptions.base import CryptoPOSException, ConnectionException,NotImplementedException
from .base import SinergiaRepository

import pandas as pd

class CargoRepository(SinergiaRepository):
    def get(self,query_params):
        sql = 'SELECT * FROM integrador.cargos'
        count_sql = 'SELECT COUNT(*) count_rows  FROM integrador.cargos'

        # Definiendo order
        if 'order' in query_params:
            order_criteria = query_params['order']
            order_fields = ','.join(order_criteria)
            sql += ' ORDER BY %s' % (order_fields)

        # Definiendo los Rangos de Paginacion
        limit = 10
        offset = 0
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
        sql += ' LIMIT %s OFFSET %s' % (limit,offset)

        table_df = pd.read_sql_query(sql,con=db.engine)
        rows = table_df.to_dict('records')
        count_result_rows = limit

        count_df = pd.read_sql_query(count_sql,con=db.engine)
        result_count = count_df.to_dict('records')
        count_all_rows = result_count[0]['count_rows']

        return  { 'count': count_result_rows, 'total':  count_all_rows  ,'data' : rows}


class CentroCostoRepository(SinergiaRepository):
    def get(self,query_params):
        sql = 'SELECT * FROM integrador.centro_costo'
        count_sql = 'SELECT COUNT(*) count_rows  FROM integrador.centro_costo'

        # Definiendo order
        if 'order' in query_params:
            order_criteria = query_params['order']
            order_fields = ','.join(order_criteria)
            sql += ' ORDER BY %s' % (order_fields)

        # Definiendo los Rangos de Paginacion
        limit = 10
        offset = 0
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
        sql += ' LIMIT %s OFFSET %s' % (limit,offset)

        table_df = pd.read_sql_query(sql,con=db.engine)
        rows = table_df.to_dict('records')
        count_result_rows = limit

        count_df = pd.read_sql_query(count_sql,con=db.engine)
        result_count = count_df.to_dict('records')
        count_all_rows = result_count[0]['count_rows']

        return  { 'count': count_result_rows, 'total':  count_all_rows  ,'data' : rows}

class ConceptoNominaRepository(SinergiaRepository):
    def get(self,query_params):
        sql = 'SELECT * FROM integrador.conceptos_nomina'
        count_sql = 'SELECT COUNT(*) count_rows  FROM integrador.conceptos_nomina'

        # Definiendo order
        if 'order' in query_params:
            order_criteria = query_params['order']
            order_fields = ','.join(order_criteria)
            sql += ' ORDER BY %s' % (order_fields)

        # Definiendo los Rangos de Paginacion
        limit = 10
        offset = 0
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
        sql += ' LIMIT %s OFFSET %s' % (limit,offset)

        table_df = pd.read_sql_query(sql,con=db.engine)
        rows = table_df.to_dict('records')
        count_result_rows = limit

        count_df = pd.read_sql_query(count_sql,con=db.engine)
        result_count = count_df.to_dict('records')
        count_all_rows = result_count[0]['count_rows']

        return  { 'count': count_result_rows, 'total':  count_all_rows  ,'data' : rows}



class DispositivoRepository(SinergiaRepository):
    def getAll(self):
        table_df = pd.read_sql_query('select * from integrador.dispositivos',con=db.engine)
        result = table_df.to_dict('records')
        return result

class EstatusTrabajadorRepository(SinergiaRepository):
    def getAll(self):
        table_df = pd.read_sql_query('select * from integrador.estatus_trabajador',con=db.engine)
        result = table_df.to_dict('records')
        return result

class TipoAusenciaRepository(SinergiaRepository):
    def getAll(self):
        table_df = pd.read_sql_query('select * from integrador.tipos_ausencias',con=db.engine)
        result = table_df.to_dict('records')
        return result

class TipoNominaRepository(SinergiaRepository):
    def getAll(self):
        table_df = pd.read_sql_query('select * from integrador.tipos_de_nomina',con=db.engine)
        result = table_df.to_dict('records')
        return result

class TrabajadorRepository(SinergiaRepository):
    def get(self,query_params):
        sql = '''
        SELECT  
            t.cedula, 
            t.codigo, 
            t.nombres, 
            t.apellidos, 
            t.sexo, 
            t.fecha_ingreso, 
            t.fecha_egreso, 
            t.cargo id_cargo, c.descripcion nombre_cargo, 
            t.centro_costo id_centro_costo, cc.descripcion nombre_centro_costo, 
            t.tipo_nomina id_tipo_nomina, tn.descripcion nombre_tipo_nomina, 
            t.status_actual id_status_actual, et.descripcion status_trabajador, 
            t.id_tarjeta, 
            t.telefono, 
            t.correo
        FROM integrador.trabajadores t 
        JOIN integrador.cargos c 
        ON t.cargo = c.codigo
        JOIN integrador.centro_costo cc 
        ON t.centro_costo = cc.codigo 
        JOIN integrador.tipos_de_nomina tn 
        ON t.tipo_nomina = tn.codigo 
        JOIN integrador.estatus_trabajador et 
        ON t.status_actual = et.codigo 
        '''
        count_sql = 'SELECT COUNT(*) count_rows FROM integrador.trabajadores '

        # Definiendo order
        if 'order' in query_params:
            order_criteria = query_params['order']
            order_fields = ','.join(order_criteria)
            sql += ' ORDER BY %s' % (order_fields)

        # Definiendo los Rangos de Paginacion
        limit = 10
        offset = 0
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
        sql += ' LIMIT %s OFFSET %s' % (limit,offset)

        table_df = pd.read_sql_query(sql,con=db.engine)
        rows = table_df.to_dict('records')
        count_result_rows = limit

        count_df = pd.read_sql_query(count_sql,con=db.engine)
        result_count = count_df.to_dict('records')
        count_all_rows = result_count[0]['count_rows']

        return  { 'count': count_result_rows, 'total':  count_all_rows  ,'data' : rows}
