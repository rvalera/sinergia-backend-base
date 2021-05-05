'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.models.security import SecurityElement, User, PersonExtension
from app import redis_client, db, alembic
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from app.exceptions.base import CryptoPOSException, ConnectionException,NotImplementedException
from .base import SinergiaRepository

import pandas as pd

from sqlalchemy.sql import text

class HolguraRepository(SinergiaRepository):

    def new(self,payload):
        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                    insert into integrador.holguras
                    ( 
                    fecha_desde
                    ,fecha_hasta
                    ,autorizado_por
                    ,minutos_tolerancia
                    ,centro_costo
                    ) 
                    values 
                    (
                    :fecha_desde
                    ,:fecha_hasta 
                    ,:autorizado_por
                    ,:minutos_tolerancia
                    ,:id_centro_costo
                    ) 
                """
            ), 
            **payload
        )


    def save(self,payload):
        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                    UPDATE integrador.holguras
                    SET 
                    fecha_desde = :fecha_desde
                    ,fecha_hasta = :fecha_hasta
                    ,autorizado_por = :autorizado_por
                    ,minutos_tolerancia = :minutos_tolerancia
                    ,centro_costo = :id_centro_costo 
                    WHERE id = :id
                """
            ), 
            **payload
        )

    def delete(self,query_params):
        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                    DELETE FROM integrador.holguras
                    WHERE id = :id
                """
            ), 
            **query_params
        )


    def get(self,query_params):
        sql = '''
        SELECT  
            id, 
            fecha_desde, 
            fecha_hasta, 
            autorizado_por, 
            minutos_tolerancia, 
            centro_costo id_centro_costo, cc.descripcion nombre_centro_costo
        FROM integrador.holguras h 
        JOIN integrador.centro_costo cc 
        ON h.centro_costo = cc.codigo 
        '''
        count_sql = 'SELECT COUNT(*) count_rows FROM integrador.holguras '

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

#
class TurnoRepository(SinergiaRepository):

    def new(self,payload):
        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                    insert into integrador.turnos
                    ( 
                    codigo
                    , descripcion
                    , hora_inicio
                    , hora_final
                    , cantidad_horas_diurnas
                    , hinicio_descanso
                    , hfinal_descanso
                    , horas_nocturnas
                    , status
                    ) 
                    values 
                    (
                    :codigo
                    , :descripcion
                    , :hora_inicio
                    , :hora_final
                    , :cantidad_horas_diurnas
                    , :hinicio_descanso
                    , :hfinal_descanso
                    , :horas_nocturnas
                    , :status
                    ) 
                """
            ), 
            **payload
        )


    def save(self,payload):
        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                    UPDATE integrador.turnos
                    SET 
                    descripcion = :descripcion
                    , hora_inicio = :hora_inicio
                    , hora_final = :hora_final
                    , cantidad_horas_diurnas = :cantidad_horas_diurnas
                    , hinicio_descanso = :hinicio_descanso 
                    , hfinal_descanso =  :hfinal_descanso
                    , horas_nocturnas = :horas_nocturnas
                    , status = :status
                    WHERE codigo = :codigo
                """
            ), 
            **payload
        )

    def delete(self,query_params):
        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                    DELETE FROM integrador.turnos
                    WHERE codigo = :codigo
                """
            ), 
            **query_params
        )


    def get(self,query_params):
        sql = '''
        SELECT  *
        FROM integrador.turnos 
        '''
        count_sql = 'SELECT COUNT(*) count_rows FROM integrador.turnos '

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
