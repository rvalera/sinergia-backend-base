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
from app.exceptions.base import CryptoPOSException, ConnectionException,NotImplementedException,RepositoryUnknownException
from .base import SinergiaRepository

import json
 
import pandas as pd

from sqlalchemy.sql import text

class HolguraRepository(SinergiaRepository):

    def new(self,payload):
        user = self.getUser()

        parameters = {
            'fecha_desde': payload['fecha_desde'],
            'fecha_hasta': payload['fecha_hasta'],
            'minutos_tolerancia' : payload['minutos_tolerancia'],
            'id_user_creador' : user.id,                                 
        }

        if 'id_centro_costo' in payload:
            if payload['id_centro_costo']:
                parameters['id_centro_costo'] = payload['id_centro_costo']
            else:
                parameters['id_centro_costo'] = None
        else:
            parameters['id_centro_costo'] = None

        if 'id_tipo_nomina' in payload:
            if payload['id_tipo_nomina']:
                parameters['id_tipo_nomina'] = payload['id_tipo_nomina']
            else:
                parameters['id_tipo_nomina'] = None
        else:
            parameters['id_tipo_nomina'] = None

       

        if 'cedula_trabajador' in payload:
            if payload['cedula_trabajador']:
                parameters['cedula_trabajador'] = payload['cedula_trabajador']
            else:
                parameters['cedula_trabajador'] = None
        else:
            parameters['cedula_trabajador'] = None

        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                    insert into integrador.holguras
                    ( 
                    fecha_desde
                    , fecha_hasta
                    , minutos_tolerancia
                    , centro_costo
                    , codigo_nomina
                    , cedula 
                    , fecha_registro 
                    , usuario_creador
                    , status 
                    ) 
                    values 
                    (
                    :fecha_desde
                    ,:fecha_hasta 
                    ,:minutos_tolerancia
                    ,:id_centro_costo
                    ,:id_tipo_nomina
                    ,:cedula_trabajador
                    , CURRENT_DATE
                    ,:id_user_creador
                    , 0
                    ) 
                """
            ), 
            **parameters
        )

    def getById(self,id):

        parameters = {
            'id': id
        }
        
        sql = '''
        SELECT  
            h.id
            , TO_CHAR(h.fecha_desde,'YYYY-MM-DD') fecha_desde
            , TO_CHAR(h.fecha_hasta,'YYYY-MM-DD') fecha_hasta
            , h.minutos_tolerancia
            , h.centro_costo id_centro_costo
            , cc.descripcion nombre_centro_costo
            , h.codigo_nomina id_tipo_nomina
            , tn.descripcion nombre_tipo_nomina
            , TO_CHAR(h.fecha_registro,'YYYY-MM-DD') fecha_registro
            , h.usuario_creador id_usuario_creador
            , se1.name nombre_usuario_creador
            , COALESCE( TO_CHAR(h.fecha_aprobacion,'YYYY-MM-DD'), '' ) fecha_aprobacion
            , COALESCE( h.usuario_aprobador,0) id_usuario_aprobador
            , COALESCE( se2.name, '') nombre_usuario_aprobador
            , h.status estatus            
        FROM integrador.holguras h 
        LEFT JOIN 
            integrador.centro_costo cc 
        ON 
            h.centro_costo = cc.codigo 
        LEFT JOIN 
            integrador.tipos_de_nomina tn
        ON 
            h.codigo_nomina = tn.codigo 
        LEFT JOIN 
            integrador.trabajadores t 
        ON 
            h.cedula = t.cedula 
        LEFT JOIN 
            public.securityelement se1
        ON 
            h.usuario_creador = se1.id
        LEFT JOIN 
            public.securityelement se2
        ON  
            h.usuario_aprobador = se2.id
        WHERE 
            h.id = {id}
        '''

        sql = sql.format(**parameters)
        
        table_df = pd.read_sql_query(sql,con=db.engine)
        rows = table_df.to_dict('records')

        if len(rows) == 0:
            raise RepositoryUnknownException()                

        return rows[0]        

    #Validar que las horas extras se aprueba en el periodo de semanas definidos para la aplicacion
    def approve(self,id):
        holgura = self.getById(id)
        user = self.getUser()

        parameters = {
            'id': id,
            'id_user_aprobador': user.id
        }

        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                    UPDATE integrador.holguras
                    SET 
                    usuario_aprobador = :id_user_aprobador
                    , fecha_aprobacion =  CURRENT_DATE
                    , status = 1
                    WHERE 
                        id = :id
                """
                        ), 
            **parameters
        )

    def save(self,payload):
        holgura = self.getById(payload['id'])
        user = self.getUser()

        parameters = {
            'id' : payload['id'],
            'fecha_desde': payload['fecha_desde'],
            'fecha_hasta': payload['fecha_hasta'],
            'minutos_tolerancia' : payload['minutos_tolerancia'],
            'id_user_creador' : user.id,                                 
        }

        if 'id_centro_costo' in payload:
            if payload['id_centro_costo']:
                parameters['id_centro_costo'] = payload['id_centro_costo']
            else:
                parameters['id_centro_costo'] = None
        else:
            parameters['id_centro_costo'] = None

        if 'id_tipo_nomina' in payload:
            if payload['id_tipo_nomina']:
                parameters['id_tipo_nomina'] = payload['id_tipo_nomina']
            else:
                parameters['id_tipo_nomina'] = None
        else:
            parameters['id_tipo_nomina'] = None

        if 'cedula_trabajador' in payload:
            if payload['cedula_trabajador']:
                parameters['cedula_trabajador'] = payload['cedula_trabajador']
            else:
                parameters['cedula_trabajador'] = None
        else:
            parameters['cedula_trabajador'] = None

        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                    UPDATE integrador.holguras
                    SET 
                    fecha_desde = :fecha_desde
                    ,fecha_hasta = :fecha_hasta
                    ,minutos_tolerancia = :minutos_tolerancia
                    ,centro_costo = :id_centro_costo 
                    ,codigo_nomina = :id_tipo_nomina  
                    ,cedula = :cedula_trabajador
                    ,usuario_creador = :id_user_creador
                    WHERE id = :id
                """
            ), 
            **parameters
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
            h.id
            , TO_CHAR(h.fecha_desde,'YYYY-MM-DD') fecha_desde
            , TO_CHAR(h.fecha_hasta,'YYYY-MM-DD') fecha_hasta
            , h.minutos_tolerancia
            , h.centro_costo id_centro_costo
            , cc.descripcion nombre_centro_costo
            , h.codigo_nomina id_tipo_nomina
            , tn.descripcion nombre_tipo_nomina
            , TO_CHAR(h.fecha_registro,'YYYY-MM-DD') fecha_registro
            , h.usuario_creador id_usuario_creador
            , se1.name nombre_usuario_creador
            , COALESCE( TO_CHAR(h.fecha_aprobacion,'YYYY-MM-DD'), '' ) fecha_aprobacion
            , COALESCE( h.usuario_aprobador,0) id_usuario_aprobador
            , COALESCE( se2.name, '') nombre_usuario_aprobador
            , h.status estatus            
        FROM integrador.holguras h 
        LEFT JOIN 
            integrador.centro_costo cc 
        ON 
            h.centro_costo = cc.codigo 
        LEFT JOIN 
            integrador.tipos_de_nomina tn
        ON 
            h.codigo_nomina = tn.codigo 
        LEFT JOIN 
            integrador.trabajadores t 
        ON 
            h.cedula = t.cedula 
        LEFT JOIN 
            public.securityelement se1
        ON 
            h.usuario_creador = se1.id
        LEFT JOIN 
            public.securityelement se2
        ON  
            h.usuario_aprobador = se2.id
        {conditions}
        {order_by}
        {limits_offset}
        '''

        count_sql = '''
        SELECT COUNT(*) count_rows 
        FROM 
            integrador.holguras h 
        LEFT JOIN 
            integrador.centro_costo cc 
        ON 
            h.centro_costo = cc.codigo 
        LEFT JOIN 
            integrador.tipos_de_nomina tn
        ON 
            h.codigo_nomina = tn.codigo 
        LEFT JOIN 
            integrador.trabajadores t 
        ON 
            h.cedula = t.cedula 
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
                        conditions.append('h.cedula  = {cedula_trabajador}')

                    if 'id_centro_costo' in filter_conditions:
                        if type(filter_conditions['id_centro_costo']) == str :
                            conditions.append("h.centro_costo = '{id_centro_costo}' ")
                        else:
                            if type(filter_conditions['id_centro_costo'] is list) and len(filter_conditions['id_centro_costo']) > 1:
                                filter_conditions['id_centro_costo'] = tuple(filter_conditions['id_centro_costo']) 
                                conditions.append('h.centro_costo IN {id_centro_costo}')
                            else:
                                filter_conditions['id_centro_costo'] = (filter_conditions['id_centro_costo'][0])
                                conditions.append("h.centro_costo = '{id_centro_costo}' ")
                            

                    if 'id_tipo_nomina' in filter_conditions:
                        if type(filter_conditions['id_tipo_nomina']) == str :
                            conditions.append("h.codigo_nomina = '{id_tipo_nomina}'") 
                        else:
                            if type(filter_conditions['id_tipo_nomina'] is list) and len(filter_conditions['id_tipo_nomina']) > 1:
                                filter_conditions['id_tipo_nomina'] = tuple(filter_conditions['id_tipo_nomina'])    
                                conditions.append('h.codigo_nomina IN {id_tipo_nomina}')
                            else:
                                filter_conditions['id_tipo_nomina'] = (filter_conditions['id_tipo_nomina'][0])
                                conditions.append("h.codigo_nomina = '{id_tipo_nomina}'")                            

                    if 'from' in filter_conditions:
                        conditions.append("h.fecha_desde >= '{from}' ")

                    if 'to' in filter_conditions:
                        conditions.append("h.fecha_hasta <= '{to}' ")

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

        table_df = pd.read_sql_query(sql,con=db.engine)
        rows = table_df.to_dict('records')
        count_result_rows = limit

        count_sql = count_sql.format(**parameters)
        count_df = pd.read_sql_query(count_sql,con=db.engine)
        result_count = count_df.to_dict('records')
        count_all_rows = result_count[0]['count_rows']

        return  { 'count': count_result_rows, 'total':  count_all_rows  ,'data' : rows}

#######################################################################################################

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
        {conditions}
        {order_by}
        {limits_offset}
        '''
        count_sql = '''
        SELECT COUNT(*) count_rows FROM integrador.turnos
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

        table_df = pd.read_sql_query(sql,con=db.engine)
        rows = table_df.to_dict('records')
        count_result_rows = limit

        count_sql = count_sql.format(**parameters)
        count_df = pd.read_sql_query(count_sql,con=db.engine)
        result_count = count_df.to_dict('records')
        count_all_rows = result_count[0]['count_rows']

        return  { 'count': count_result_rows, 'total':  count_all_rows  ,'data' : rows}


