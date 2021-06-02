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

class DailyMarkingRepository(SinergiaRepository):

    def get(self,query_params):
        sql = '''
    SELECT 
        integrador.trabajadores.codigo as ficha
        ,integrador.marcaciones_dia.cedula
        ,integrador.trabajadores.nombres 
        ,integrador.trabajadores.apellidos 
        ,integrador.tipo_trabajador.descripcion as tipo_de_trabajador 
        ,TO_CHAR(integrador.marcaciones_dia.fecdia,'YYYY-MM-DD') as fecha_marcaje
        , CASE
            WHEN (extract(dow from  marcaciones_dia.fecdia) = 0)  THEN 'DOM'
            WHEN (extract(dow from  marcaciones_dia.fecdia) = 1)  THEN 'LUN'
            WHEN (extract(dow from  marcaciones_dia.fecdia) = 2)  THEN 'MAR'
            WHEN (extract(dow from  marcaciones_dia.fecdia) = 3)  THEN 'MIE'
            WHEN (extract(dow from  marcaciones_dia.fecdia) = 4)  THEN 'JUE'
            WHEN (extract(dow from  marcaciones_dia.fecdia) = 5)  THEN 'VIE'
            WHEN (extract(dow from  marcaciones_dia.fecdia) = 6)  THEN 'SAB'
        END dia_marcaje 
        , CONCAT(  LPAD(DATE_PART('hour', integrador.marcaciones_dia.hora_inicial_p::timestamp )::text,'0') , ':', DATE_PART('minute', integrador.marcaciones_dia.hora_inicial_p::timestamp ))  as llegada_nomina
        , CONCAT  ( DATE_PART('hour', integrador.marcaciones_dia.hora_fin_p::timestamp ), ':', DATE_PART('minute', integrador.marcaciones_dia.hora_fin_p::timestamp ))  as salida_nomina
        , CONCAT  ( DATE_PART('hour',integrador.marcaciones_dia.fecha_inicio_dia ::timestamp ), ':', DATE_PART('minute', integrador.marcaciones_dia.fecha_inicio_dia::timestamp ))  as llegada_control
        , CONCAT  ( DATE_PART('hour',integrador.marcaciones_dia.fecha_fin_dia ::timestamp ), ':', DATE_PART('minute', integrador.marcaciones_dia.fecha_fin_dia::timestamp ))  as salida_control
        , DATE_PART('minute', integrador.marcaciones_dia.fecha_inicio_dia::timestamp - integrador.marcaciones_dia.hora_inicial_p::timestamp) as minutos_retardo_entrada
        , DATE_PART('minute', integrador.marcaciones_dia.fecha_fin_dia::timestamp - integrador.marcaciones_dia.hora_fin_p::timestamp) as minutos_extras_salida
        , TO_CHAR( integrador.marcaciones_dia.total_horas_marcaje, 'HH:MI' ) as horas_control
        , integrador.marcaciones_dia.turno as id_turno
        , integrador.turnos.descripcion as descrip_turno
        , integrador.centro_costo.codigo as id_ceco
        , integrador.centro_costo.descripcion  as descrip_ceco
        , integrador.marcaciones_dia.codigo_biostar as tipo_de_marcaje 
        , integrador.tipos_de_marcaje.descripcion_biostar as descripcion_tipo_marcaje
        , TO_CHAR( integrador.turnos.hora_inicio, 'HH24:MI' ) as hora_inicio_del_turno 
        , TO_CHAR( integrador.turnos.hora_final, 'HH24:MI' ) as hora_final_turno
        , TO_CHAR( integrador.marcaciones_dia.hora_inicial_p, 'HH:MI' ) as fecha_horai_programada
        , TO_CHAR( integrador.marcaciones_dia.hora_fin_p, 'HH24:MI' ) as fecha_horaf_programada
        , TO_CHAR(integrador.marcaciones_dia.fecha_inicio_dia,'YYYY-MM-DD HH24:MI:SS')  as fecha_hora_primer_marcaje
        , TO_CHAR(integrador.marcaciones_dia.fecha_fin_dia,'YYYY-MM-DD HH24:MI:SS')  as fecha_hora_ultimo_marcaje
    FROM 
        integrador.marcaciones_dia
        JOIN integrador.trabajadores
        ON integrador.marcaciones_dia.cedula =  integrador.trabajadores.cedula 
        JOIN integrador.turnos
        ON integrador.marcaciones_dia.turno = integrador.turnos.codigo 
        JOIN integrador.centro_costo
        ON integrador.trabajadores.centro_costo = integrador.centro_costo.codigo 
        JOIN integrador.tipos_de_marcaje
        ON integrador.marcaciones_dia.codigo_biostar = integrador.tipos_de_marcaje.codigo_biostar 
        JOIN integrador.tipo_trabajador
        ON integrador.trabajadores.tipo_de_trabajador  = integrador.tipo_trabajador.codigo 
    {conditions}
    {order_by}
    {limits_offset}
    '''

        count_sql = '''
    SELECT COUNT(*) count_rows 
    FROM 
        integrador.marcaciones_dia
        JOIN integrador.trabajadores
        ON integrador.marcaciones_dia.cedula =  integrador.trabajadores.cedula 
        JOIN integrador.turnos
        ON integrador.marcaciones_dia.turno = integrador.turnos.codigo 
        JOIN integrador.centro_costo
        ON integrador.trabajadores.centro_costo = integrador.centro_costo.codigo 
        JOIN integrador.tipos_de_marcaje
        ON integrador.marcaciones_dia.codigo_biostar = integrador.tipos_de_marcaje.codigo_biostar 
        JOIN integrador.tipo_trabajador
        ON integrador.trabajadores.tipo_de_trabajador  = integrador.tipo_trabajador.codigo 
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
                        conditions.append('integrador.marcaciones_dia.cedula  = {cedula_trabajador}')

                    if 'id_centro_costo' in filter_conditions:
                        conditions.append('id_ceco = {id_centro_costo}')

                    if 'id_tipo_trabajador' in filter_conditions:
                        conditions.append('integrador.tipo_trabajador.codigo = {id_tipo_trabajador}')

                    if 'id_turno' in filter_conditions:
                        conditions.append('id_turno = {id_turno}')

                    if 'to' in filter_conditions:
                        conditions.append("fecha_inicio_dia >= '{to}' ")

                    if 'from' in filter_conditions:
                        conditions.append('fecha_inicio_dia <= {from}')

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
        count_sql = count_sql.format(**parameters)

        table_df = pd.read_sql_query(sql,con=db.engine)
        rows = table_df.to_dict('records')
        count_result_rows = limit

        count_df = pd.read_sql_query(count_sql,con=db.engine)
        result_count = count_df.to_dict('records')
        count_all_rows = result_count[0]['count_rows']

        return  { 'count': count_result_rows, 'total':  count_all_rows  ,'data' : rows}



