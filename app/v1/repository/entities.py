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
from app.exceptions.base import CryptoPOSException, ConnectionException,NotImplementedException
from .base import SinergiaRepository

import pandas as pd
import logging

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
        # Definiendo Filter
        filter_criteria = {}
        if 'filter' in query_params:
            filter_criteria = query_params['filter']

        # Definiendo order
        if 'order' in query_params:
            order_criteria = query_params['order']
            order_fields = ','.join(order_criteria)

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
        rows = Trabajador.query.filter_by(**filter_criteria).slice(low_limit,high_limit).all()
        count_result_rows = len(rows)
        count_all_rows = Trabajador.query.filter_by(**filter_criteria).count()

        return { 'count': count_result_rows, 'total':  count_all_rows  ,'data' : rows} 


    def getByCedula(self,cedula):
        row = Trabajador.query.filter(Trabajador.cedula == cedula).first()
        return  row


class TipoTrabajadorRepository(SinergiaRepository):
    def getAll(self):
        table_df = pd.read_sql_query('select * from integrador.tipo_trabajador',con=db.engine)
        result = table_df.to_dict('records')
        return result

class GrupoGuardiaRepository(SinergiaRepository):
    def getAll(self):
        table_df = pd.read_sql_query('select * from integrador.grupo_guardia',con=db.engine)
        result = table_df.to_dict('records')
        return result