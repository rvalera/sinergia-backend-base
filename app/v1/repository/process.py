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

from app.exceptions.base import RepositoryUnknownException

import pandas as pd

from sqlalchemy.sql import text
from datetime import datetime, timedelta

class AbsenceEventRepository(SinergiaRepository):

    def get(self,event_date,cedula): 

        parameters = {
            'event_date' : event_date,
            'cedula' : cedula
        }

        sql = '''
        SELECT 
            TO_CHAR(md.fecdia,'YYYY-MM-DD') fecha
            , dia_marcaje
            , id_turno
            , nombre_turno 
            , cedula
            , apellidos
            , nombres 
            , id_cargo
            , nombre_cargo
            , id_tipo_trabajador
            , nombre_tipo_trabajador
            , id_centro_costo
            , nombre_centro_costo
            , estatus 
            , id_grupo_guardia
            , nombre_grupo_guardia
            , id_tipo_nomina
            , nombre_tipo_nomina
            , TO_CHAR(marcaje_inicial,'YYYY-MM-DD HH24:MI:SS') marcaje_inicial
            , TO_CHAR(marcaje_final,'YYYY-MM-DD HH24:MI:SS') marcaje_final
            , TO_CHAR(inicio_planificado,'YYYY-MM-DD HH24:MI:SS') inicio_planificado
            , TO_CHAR(fin_planificado,'YYYY-MM-DD HH24:MI:SS') fin_planificado
            , TO_CHAR( hora_inicio_turno, 'HH24:MI' ) hora_inicio_turno
            , TO_CHAR( hora_final_turno, 'HH24:MI' ) hora_final_turno
            , TO_CHAR( horas_planificadas, 'HH24:MI' ) horas_planificadas
            , TO_CHAR( horas_marcajes, 'HH24:MI' ) horas_marcajes
            , id_tipo_marcaje
            , nombre_tipo_marcaje
            , horas_ausencias_calculadas
            , horas_extras_calculadas
            , horas_ausencias_aprobadas
            , horas_extras_aprobadas
        FROM 
            integrador.vw_marcajes_dia md
        WHERE 
            md.fecdia = '{event_date}'        
            AND md.cedula  = {cedula}
        '''

        sql = sql.format(**parameters)
        header_df = pd.read_sql_query(sql,con=db.engine)
        rows = header_df.to_dict('records')

        header  = None
        if len(rows) > 0:
            header = rows[0]

            sql = '''
            SELECT 
                serial id
                , TO_CHAR(mda.fecdia,'YYYY-MM-DD') fecha
                , mda.cedula 
                , ta.codigo id_justificacion_ausencia
                , ta.descripcion nombre_justificacion_ausencia
                , TO_CHAR(mda.fecregistro,'YYYY-MM-DD') fecha_registro
                , mda.cantidad_generada cantidad_generada
                , mda.user_creador id_usuario_creador
                , se1.name nombre_usuario_creador
                , TO_CHAR(mda.fecha_aprobacion,'YYYY-MM-DD') fecha_aprobacion
                , mda.cantidad_aprobada cantidad_aprobada
                , mda.user_aprobador id_usuario_aprobador
                , se2.name nombre_usuario_aprobador
                , mda.estatus estatus 
                , mda.observaciones observaciones
            FROM integrador.marcaciones_dia_ausencias mda
            JOIN integrador.tipos_ausencias ta
            ON mda.tpau = ta.codigo
            LEFT JOIN public.securityelement se1
            ON mda.user_creador = se1.id
            LEFT JOIN public.securityelement se2
            ON  mda.user_aprobador = se2.id
            WHERE 
                mda.fecdia = '{event_date}'        
                AND mda.cedula  = {cedula}
            '''

            sql = sql.format(**parameters)
            details_df = pd.read_sql_query(sql,con=db.engine)
            rows = details_df.to_dict('records')

            header['justificaciones_ausencia'] = rows

        if header is None: #Los datos solicitados no Existen
            raise RepositoryUnknownException()                

        return header


class JustificationAbsenceRepository(SinergiaRepository):

    #Validar que las justificacion se hacen en el periodo de semanas definidos para la aplicacion
    def new(self,payload):

        user = self.getUser()

        parameters = {
            'fecha': payload['fecha'],
            'cedula' : payload['cedula'],
            'id_user_creador' : user.id,
            'horas_generadas' : payload['horas_generadas'],
            'id_justificacion_ausencia' : payload['id_justificacion_ausencia'],
            'observaciones' : payload['observaciones'],
        }

        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                INSERT INTO integrador.marcaciones_dia_ausencias (
                    fecdia
                    ,cedula
                    ,fecregistro
                    ,tpau
                    ,cantidad_generada
                    ,user_creador
                    ,observaciones
                    ,estatus
                    ) 
                VALUES (
                    :fecha
                    ,:cedula
                    ,CURRENT_DATE
                    ,:id_justificacion_ausencia
                    ,:horas_generadas
                    ,:id_user_creador
                    ,:observaciones
                    ,0
                    )
                """
                        ), 
            **parameters
        )

    def getById(self,event_date,cedula,id):

        parameters = {
            'id': id,
            'event_date' : event_date,
            'cedula' : cedula
        }
        
        sql = '''
            SELECT 
                serial id
                , TO_CHAR(mda.fecdia,'YYYY-MM-DD') fecha
                , mda.cedula 
                , ta.codigo id_justificacion_ausencia
                , ta.descripcion nombre_justificacion_ausencia
                , TO_CHAR(mda.fecregistro,'YYYY-MM-DD') fecha_registro
                , mda.cantidad_generada cantidad_generada
                , mda.user_creador id_usuario_creador
                , se1.name nombre_usuario_creador
                , TO_CHAR(mda.fecha_aprobacion,'YYYY-MM-DD') fecha_aprobacion
                , mda.cantidad_aprobada cantidad_aprobada
                , mda.user_aprobador id_usuario_aprobador
                , se2.name nombre_usuario_aprobador
                , mda.estatus estatus 
                , mda.observaciones observaciones
            FROM integrador.marcaciones_dia_ausencias mda
            JOIN integrador.tipos_ausencias ta
            ON mda.tpau = ta.codigo            
            LEFT JOIN public.securityelement se1
            ON mda.user_creador = se1.id
            LEFT JOIN public.securityelement se2
            ON  mda.user_aprobador = se2.id
            WHERE 
                mda.serial = {id}
                AND mda.fecdia = '{event_date}'        
                AND mda.cedula  = {cedula}
        '''

        sql = sql.format(**parameters)
        
        table_df = pd.read_sql_query(sql,con=db.engine)
        rows = table_df.to_dict('records')
        
        if len(rows) == 0:
            raise RepositoryUnknownException()                

        return rows[0]        

    #Validar que las justificacion se hacen en el periodo de semanas definidos para la aplicacion, No Modificar si ya esta aprobada
    def save(self,payload):

        justicacion_ausencia = self.getById(payload['fecha'],payload['cedula'],payload['id'])
        user = self.getUser()

        parameters = {
            'id': payload['id'],
            'fecha': payload['fecha'],
            'cedula' : payload['cedula'],
            'id_user_creador' : user.id,
            'horas_generadas' : payload['horas_generadas'],
            'id_justificacion_ausencia' : payload['id_justificacion_ausencia'],
            'observaciones' : payload['observaciones'],
        }

        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                UPDATE integrador.marcaciones_dia_ausencias 
                SET tpau = :id_justificacion_ausencia
                    , cantidad_generada = :horas_generadas
                    , user_creador = :id_user_creador
                    , observaciones = :observaciones
                WHERE 
                    serial = :id
                    AND fecdia = :fecha
                    AND cedula  = :cedula

                """
                        ), 
            **parameters
        )


    #No Eliminar si ya esta aprobada
    def delete(self,event_date,cedula,id):

        justicacion_ausencia = self.getById(event_date,cedula,id)
        user = self.getUser()

        parameters = {
            'id': id,
            'fecha': event_date,
            'cedula' : cedula,
        }

        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                DELETE FROM integrador.marcaciones_dia_ausencias 
                WHERE 
                    serial = :id
                    AND fecdia = :fecha
                    AND cedula  = :cedula
                """
                        ), 
            **parameters
        )


    #Validar que las justificacion de aprueba se hacen en el periodo de semanas definidos para la aplicacion, No Modificar si ya esta aprobada
    def approve(self,event_date,cedula,id):
        justicacion_ausencia = self.getById(event_date,cedula,id)
        user = self.getUser()

        parameters = {
            'id': id,
            'event_date' : event_date,
            'cedula' : cedula,
            'id_user_aprobador' : user.id
        }

        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                    UPDATE integrador.marcaciones_dia_ausencias
                    SET 
                    fecha_aprobacion = CURRENT_DATE
                    ,cantidad_aprobada = cantidad_generada
                    ,user_aprobador = :id_user_aprobador
                    ,estatus = 1
                    WHERE 
                        serial = :id
                        AND fecdia = :event_date
                        AND cedula  = :cedula
                """
                        ), 
            **parameters
        )



class OvertimeEventRepository(SinergiaRepository):

    def get(self,event_date,cedula):    
        parameters = {
            'event_date' : event_date,
            'cedula' : cedula
        }

        sql = '''
        SELECT 
            TO_CHAR(md.fecdia,'YYYY-MM-DD') fecha
            , dia_marcaje
            , id_turno
            , nombre_turno 
            , cedula
            , apellidos
            , nombres 
            , id_cargo
            , nombre_cargo
            , id_tipo_trabajador
            , nombre_tipo_trabajador
            , id_centro_costo
            , nombre_centro_costo
            , estatus 
            , id_grupo_guardia
            , nombre_grupo_guardia
            , id_tipo_nomina
            , nombre_tipo_nomina
            , TO_CHAR(marcaje_inicial,'YYYY-MM-DD HH24:MI:SS') marcaje_inicial
            , TO_CHAR(marcaje_final,'YYYY-MM-DD HH24:MI:SS') marcaje_final
            , TO_CHAR(inicio_planificado,'YYYY-MM-DD HH24:MI:SS') inicio_planificado
            , TO_CHAR(fin_planificado,'YYYY-MM-DD HH24:MI:SS') fin_planificado
            , TO_CHAR( hora_inicio_turno, 'HH24:MI' ) hora_inicio_turno
            , TO_CHAR( hora_final_turno, 'HH24:MI' ) hora_final_turno
            , TO_CHAR( horas_planificadas, 'HH24:MI' ) horas_planificadas
            , TO_CHAR( horas_marcajes, 'HH24:MI' ) horas_marcajes
            , id_tipo_marcaje
            , nombre_tipo_marcaje
            , horas_ausencias_calculadas
            , horas_extras_calculadas
            , horas_ausencias_aprobadas
            , horas_extras_aprobadas
        FROM 
            integrador.vw_marcajes_dia md
        WHERE 
            md.fecdia = '{event_date}'        
            AND md.cedula  = {cedula}
        '''

        sql = sql.format(**parameters)
        header_df = pd.read_sql_query(sql,con=db.engine)
        rows = header_df.to_dict('records')

        header = None
        if len(rows) > 0:
            header = rows[0]

            sql = '''
            SELECT 
                serial id
                , TO_CHAR(mdh.fecdia,'YYYY-MM-DD') fecha
                , mdh.cedula 
                , mdh.tipo tipo_hora_extra
                , TO_CHAR(mdh.fecregistro,'YYYY-MM-DD') fecha_registro
                , mdh.cantidad_generada cantidad_generada
                , mdh.user_creador id_usuario_creador
                , se1.name nombre_usuario_creador
                , TO_CHAR(mdh.fecha_aprobacion,'YYYY-MM-DD') fecha_aprobacion
                , mdh.cantidad_aprobada cantidad_aprobada
                , mdh.user_aprobador id_usuario_aprobador
                , se2.name nombre_usuario_aprobador
                , mdh.estatus estatus 
                , mdh.observaciones observaciones 
            FROM integrador.marcaciones_dia_he mdh
            LEFT JOIN public.securityelement se1
            ON mdh.user_creador = se1.id
            LEFT JOIN public.securityelement se2
            ON  mdh.user_aprobador = se2.id
            WHERE 
                mdh.fecdia = '{event_date}'        
                AND mdh.cedula  = {cedula}
            '''

            sql = sql.format(**parameters)
            
            details_df = pd.read_sql_query(sql,con=db.engine)
            rows = details_df.to_dict('records')

            header['horas_extras_generadas'] = rows

        if header is None: #Los datos solicitados no Existen
            raise RepositoryUnknownException()                

        return header

    def getById(self,event_date,cedula,id):

        parameters = {
            'id': id,
            'event_date' : event_date,
            'cedula' : cedula
        }
        
        sql = '''
        SELECT 
            serial id
            , TO_CHAR(mdh.fecdia,'YYYY-MM-DD') fecha
            , mdh.cedula 
            , mdh.tipo tipo_hora_extra
            , TO_CHAR(mdh.fecregistro,'YYYY-MM-DD') fecha_registro
            , mdh.cantidad_generada cantidad_generada
            , mdh.user_creador id_usuario_creador
            , se1.name nombre_usuario_creador
            , TO_CHAR(mdh.fecha_aprobacion,'YYYY-MM-DD') fecha_aprobacion
            , mdh.cantidad_aprobada cantidad_aprobada
            , mdh.user_aprobador id_usuario_aprobador
            , se2.name nombre_usuario_aprobador
            , mdh.estatus estatus 
            , mdh.observaciones observaciones 
        FROM integrador.marcaciones_dia_he mdh
        LEFT JOIN public.securityelement se1
        ON mdh.user_creador = se1.id
        LEFT JOIN public.securityelement se2
        ON  mdh.user_aprobador = se2.id
        WHERE 
            mdh.serial = {id}
            AND mdh.fecdia = '{event_date}'        
            AND mdh.cedula  = {cedula}
        '''

        sql = sql.format(**parameters)
        
        table_df = pd.read_sql_query(sql,con=db.engine)
        rows = table_df.to_dict('records')

        if len(rows) == 0:
            raise RepositoryUnknownException()                

        return rows[0]        

    #Validar que las horas extras se aprueba en el periodo de semanas definidos para la aplicacion
    def approve(self,payload):
        overtime_event = self.getById(payload['event_date'],payload['cedula'],payload['id'])
        user = self.getUser()

        parameters = {
            'id': payload['id'],
            'event_date' : payload['event_date'],
            'cedula' : payload['cedula'],
            'id_user_aprobador' : user.id,
        }

        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                    UPDATE integrador.marcaciones_dia_he
                    SET 
                    fecha_aprobacion = CURRENT_DATE
                    ,cantidad_aprobada = cantidad_generada
                    ,user_aprobador = :id_user_aprobador
                    ,estatus = 1
                    WHERE 
                        serial = :id
                        AND fecdia = :event_date
                        AND cedula  = :cedula
                """
                        ), 
            **parameters
        )



class BatchJustificationAbsenceRepository(SinergiaRepository):

    def get(self,query_params):    
        sql = '''
            SELECT DISTINCT
                am."serial" id
                , TO_CHAR(am.hora_inicio,'YYYY-MM-DD') fecha_inicio
                , TO_CHAR(am.hora_final,'YYYY-MM-DD') fecha_fin
                , TO_CHAR(am.fecdia,'YYYY-MM-DD') fecha_registro
                , cantidad cantidad_horas
                , ta.codigo id_justificacion_ausencia
                , ta.descripcion nombre_justificacion_ausencia
                , am.usuario_creador id_usuario_creador
                , se1.name nombre_usuario_creador
                , COALESCE( TO_CHAR(am.fecha_aprobacion,'YYYY-MM-DD'), '' ) fecha_aprobacion
                , COALESCE( am.usuario_aprobador,0) id_usuario_aprobador
                , COALESCE( se2.name, '') nombre_usuario_aprobador
                , am.observaciones observaciones
                , am.status estatus 
            FROM             
                integrador.ausencia_masivas am 
            JOIN  
                integrador.ausencia_masivas_trabajador amt 
            ON  
                am."serial" = amt."serial" 
            JOIN  
                integrador.vw_trabajador vt 
            ON  
                amt.cedula = vt.cedula 
            JOIN  
                integrador.tipos_ausencias ta 
            ON  
                am.tpau = ta.codigo 
            LEFT JOIN 
                public.securityelement se1
            ON 
                am.usuario_creador = se1.id
            LEFT JOIN 
                public.securityelement se2
            ON  
                am.usuario_aprobador = se2.id
            {conditions}
            {order_by}
            {limits_offset}
        '''

        count_sql = '''
            SELECT COUNT(distinct am.*) count_rows 
            FROM             
                integrador.ausencia_masivas am 
            JOIN  
                integrador.ausencia_masivas_trabajador amt 
            ON  
                am."serial" = amt."serial" 
            JOIN  
                integrador.vw_trabajador vt 
            ON  
                amt.cedula = vt.cedula 
            JOIN  
                integrador.tipos_ausencias ta 
            ON  
                am.tpau = ta.codigo 
            LEFT JOIN 
                public.securityelement se1
            ON 
                am.usuario_creador = se1.id
            LEFT JOIN 
                public.securityelement se2
            ON  
                am.usuario_aprobador = se2.id
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
                        conditions.append('vt.cedula  = {cedula_trabajador}')

                    if 'id_centro_costo' in filter_conditions:
                        if type(filter_conditions['id_centro_costo']) == str :
                            conditions.append("vt.id_centro_costo = '{id_centro_costo}' ")
                        else:
                            if type(filter_conditions['id_centro_costo'] is list) and len(filter_conditions['id_centro_costo']) > 1:
                                filter_conditions['id_centro_costo'] = tuple(filter_conditions['id_centro_costo'])
                                conditions.append('vt.id_centro_costo IN {id_centro_costo}')
                            else:
                                filter_conditions['id_centro_costo'] = (filter_conditions['id_centro_costo'][0])
                                conditions.append("vt.id_tipo_nomina = '{id_tipo_nomina}' ")

                    if 'id_tipo_nomina' in filter_conditions:
                        if type(filter_conditions['id_tipo_nomina']) == str:
                            conditions.append("vt.id_tipo_nomina = '{id_tipo_nomina}' ")
                        else:
                            if type(filter_conditions['id_tipo_nomina'] is list) and len(filter_conditions['id_tipo_nomina']) > 1:
                                filter_conditions['id_tipo_nomina'] = tuple(filter_conditions['id_tipo_nomina'])    
                                conditions.append('vt.id_tipo_nomina IN {id_tipo_nomina}')
                            else:
                                filter_conditions['id_tipo_nomina'] = (filter_conditions['id_tipo_nomina'][0])
                                conditions.append("vt.id_tipo_nomina = '{id_tipo_nomina}' ")

                    if 'id_tipo_justificacion_ausencia' in filter_conditions:
                        if type(filter_conditions['id_tipo_justificacion_ausencia']) == int:
                            conditions.append("am.tpau = {id_tipo_justificacion_ausencia} ")
                        else:
                            if type(filter_conditions['id_tipo_justificacion_ausencia'] is list) and len(filter_conditions['id_tipo_justificacion_ausencia']) > 1:
                                filter_conditions['id_tipo_justificacion_ausencia'] = tuple(filter_conditions['id_tipo_justificacion_ausencia'])
                                conditions.append('am.tpau IN {id_tipo_justificacion_ausencia}')
                            else:
                                filter_conditions['id_tipo_justificacion_ausencia'] = (filter_conditions['id_tipo_justificacion_ausencia'][0])
                                conditions.append("am.tpau = {id_tipo_justificacion_ausencia} ")


                    if 'from' in filter_conditions:
                        conditions.append("md.hora_inicio >= '{from}' ")

                    if 'to' in filter_conditions:
                        conditions.append("md.hora_final <= '{to}' ")

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


    def new(self,payload):
        user = self.getUser()

        parameters = {
            'fecha_inicio': payload['fecha_inicio'],
            'fecha_fin': payload['fecha_fin'],
            'cantidad_horas' : payload['cantidad_horas'],
            'id_justificacion_ausencia' : payload['id_justificacion_ausencia'],
            'id_user_creador' : user.id,                                 
            'observaciones' : payload['observaciones']
        }


        conn = alembic.op.get_bind()
        result = conn.execute(
            text(
                """
                INSERT INTO integrador.ausencia_masivas (
                    hora_inicio
                    ,hora_final
                    ,tpau
                    ,cantidad
                    ,fecdia
                    ,usuario_creador
                    ,observaciones 
                    ,status
                    ) 
                VALUES (
                    :fecha_inicio
                    ,:fecha_fin
                    ,:id_justificacion_ausencia
                    ,:cantidad_horas
                    ,CURRENT_DATE
                    ,:id_user_creador
                    ,:observaciones
                    ,0
                    ) RETURNING ausencia_masivas.serial
                """
            ), 
            **parameters
        )

        header_id = result.fetchone()[0]

        for cedula in payload['trabajadores']:
            conn.execute(
                text(
                    """
                    INSERT INTO integrador.ausencia_masivas_trabajador (serial,cedula)
                    VALUES (:header_id,:cedula)
                    """), 
                **{'header_id': header_id,'cedula': cedula}
            )


    def getById(self,id):
        parameters = {
            'id': id,
        }
        
        sql = '''
            SELECT DISTINCT
                am."serial" id
                , TO_CHAR(am.hora_inicio,'YYYY-MM-DD') fecha_inicio
                , TO_CHAR(am.hora_final,'YYYY-MM-DD') fecha_fin
                , TO_CHAR(am.fecdia,'YYYY-MM-DD') fecha_registro
                , cantidad cantidad_horas
                , ta.codigo id_justificacion_ausencia
                , ta.descripcion nombre_justificacion_ausencia
                , am.usuario_creador id_usuario_creador
                , se1.name nombre_usuario_creador
                , COALESCE( TO_CHAR(am.fecha_aprobacion,'YYYY-MM-DD'), '' ) fecha_aprobacion
                , COALESCE( am.usuario_aprobador,0) id_usuario_aprobador
                , COALESCE( se2.name, '') nombre_usuario_aprobador
                , am.observaciones observaciones
                , am.status estatus 
            FROM             
                integrador.ausencia_masivas am 
            JOIN  
                integrador.ausencia_masivas_trabajador amt 
            ON  
                am."serial" = amt."serial" 
            JOIN  
                integrador.vw_trabajador vt 
            ON  
                amt.cedula = vt.cedula 
            JOIN  
                integrador.tipos_ausencias ta 
            ON  
                am.tpau = ta.codigo 
            LEFT JOIN 
                public.securityelement se1
            ON 
                am.usuario_creador = se1.id
            LEFT JOIN 
                public.securityelement se2
            ON  
                am.usuario_aprobador = se2.id
            WHERE 
                am.serial = {id}
        '''

        sql = sql.format(**parameters)
        
        table_df = pd.read_sql_query(sql,con=db.engine)
        rows = table_df.to_dict('records')
        
        if len(rows) == 0:
            raise RepositoryUnknownException()                

        #######################################################################################
        header = rows[0] 

        sql = '''
           SELECT vt.*
            FROM             
                integrador.ausencia_masivas am 
            JOIN  
                integrador.ausencia_masivas_trabajador amt 
            ON  
                am."serial" = amt."serial" 
            JOIN  
                integrador.vw_trabajador vt 
            ON  
                amt.cedula = vt.cedula 
            WHERE 
                am.serial = {id}
        '''
        sql = sql.format(**parameters)
        
        detail_df = pd.read_sql_query(sql,con=db.engine)
        details = detail_df.to_dict('records')

        header['trabajadores'] = details

        return header        


    def save(self,payload):
        justicacion_ausencia_masiva = self.getById(payload['id'])
        user = self.getUser()

        parameters = {
            'id' : payload['id'],
            'fecha_inicio': payload['fecha_inicio'],
            'fecha_fin': payload['fecha_fin'],
            'cantidad_horas' : payload['cantidad_horas'],
            'id_justificacion_ausencia' : payload['id_justificacion_ausencia'],
            'id_user_creador' : user.id,                                 
            'observaciones' : payload['observaciones']
        }

        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                UPDATE integrador.ausencia_masivas 
                SET hora_inicio = :fecha_inicio 
                    , hora_final = :fecha_fin
                    , cantidad = :cantidad_horas
                    , tpau = :id_justificacion_ausencia
                    , usuario_creador = :id_user_creador
                    , observaciones = :observaciones
                WHERE 
                    serial = :id
                """
                        ), 
            **parameters
        )

        #Actualizar los Trabajadores a los que afecta 
        conn.execute(
            text(
                """
                DELETE FROM integrador.ausencia_masivas_trabajador
                WHERE serial = :id
                """), 
            **{'id': payload['id']}
        )

        for cedula in payload['trabajadores']:
            conn.execute(
                text(
                    """
                    INSERT INTO integrador.ausencia_masivas_trabajador (serial,cedula)
                    VALUES (:header_id,:cedula)
                    """), 
                **{'header_id': payload['id'],'cedula': cedula}
            )


    def delete(self,id):
        justicacion_ausencia_masiva = self.getById(id)
        user = self.getUser()

        parameters = {
            'id' : id
        }

        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                DELETE FROM integrador.ausencia_masivas_trabajador
                WHERE 
                    serial = :id;
                DELETE FROM integrador.ausencia_masivas 
                WHERE 
                    serial = :id
                """
            ), 
            **parameters
        )

    def approve(self,id):
        justicacion_ausencia = self.getById(id)
        user = self.getUser()

        parameters = {
            'id': id,
            'id_user_aprobador' : user.id
        }

        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                UPDATE integrador.ausencia_masivas 
                SET fecha_aprobacion = CURRENT_DATE
                    , cantidad_aprobada = cantidad
                    , usuario_aprobador = :id_user_aprobador
                    , status = 1
                WHERE 
                    serial = :id
                """
                        ), 
            **parameters
        )



class BatchOvertimeRepository(SinergiaRepository):

    def get(self,query_params):    
        sql = '''
        SELECT DISTINCT
            am."serial" id
            , TO_CHAR(am.hora_inicio,'YYYY-MM-DD') fecha_inicio
            , TO_CHAR(am.hora_final,'YYYY-MM-DD') fecha_fin
            , TO_CHAR(am.fecdia,'YYYY-MM-DD') fecha_registro
            , cantidad cantidad_horas
            , am.tipo_de_hora tipo_hora
            , am.usuario_creador id_usuario_creador
            , se1.name nombre_usuario_creador
            , COALESCE( TO_CHAR(am.fecha_aprobacion,'YYYY-MM-DD'), '' ) fecha_aprobacion
            , COALESCE( am.usuario_aprobador,0) id_usuario_aprobador
            , COALESCE( se2.name, '') nombre_usuario_aprobador
            , am.observaciones observaciones
            , am.status estatus 
        FROM              
            integrador.horas_exmasivas am 
        JOIN  
            integrador.horas_exmasivas_trabajador amt 
        ON  
            am."serial" = amt."serial" 
        JOIN  
            integrador.vw_trabajador vt 
        ON  
            amt.cedula = vt.cedula 
        LEFT JOIN 
            public.securityelement se1
        ON 
            am.usuario_creador = se1.id
        LEFT JOIN 
            public.securityelement se2
        ON  
            am.usuario_aprobador = se2.id
        {conditions}
        {order_by}
        {limits_offset}
        '''

        count_sql = '''
            SELECT COUNT(distinct am.*) count_rows 
            FROM             
                integrador.horas_exmasivas am 
            JOIN  
                integrador.horas_exmasivas_trabajador amt 
            ON  
                am."serial" = amt."serial" 
            JOIN  
                integrador.vw_trabajador vt 
            ON  
                amt.cedula = vt.cedula 
            LEFT JOIN 
                public.securityelement se1
            ON 
                am.usuario_creador = se1.id
            LEFT JOIN 
                public.securityelement se2
            ON  
                am.usuario_aprobador = se2.id
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
                        conditions.append('vt.cedula  = {cedula_trabajador}')

                    if 'id_centro_costo' in filter_conditions:
                        if type(filter_conditions['id_centro_costo']) == str :
                            conditions.append("vt.id_centro_costo = '{id_centro_costo}' ")
                        else:
                            if type(filter_conditions['id_centro_costo'] is list) and len(filter_conditions['id_centro_costo']) > 1:
                                filter_conditions['id_centro_costo'] = tuple(filter_conditions['id_centro_costo'])    
                                conditions.append('vt.id_centro_costo IN {id_centro_costo}')
                            else:
                                filter_conditions['id_centro_costo'] = (filter_conditions['id_centro_costo'][0])
                                conditions.append("vt.id_centro_costo = '{id_centro_costo}' ")
                            

                    if 'id_tipo_nomina' in filter_conditions:
                        if type(filter_conditions['id_tipo_nomina']) == str:
                            conditions.append("vt.id_tipo_nomina = '{id_tipo_nomina}' ")
                        else:
                            if type(filter_conditions['id_tipo_nomina'] is list) and len(filter_conditions['id_tipo_nomina']) > 1:
                                filter_conditions['id_tipo_nomina'] = tuple(filter_conditions['id_tipo_nomina'])
                                conditions.append('vt.id_tipo_nomina IN {id_tipo_nomina}')
                            else:
                                filter_conditions['id_tipo_nomina'] = (filter_conditions['id_tipo_nomina'][0])
                                conditions.append("vt.id_tipo_nomina = '{id_tipo_nomina}' ")                           

                    if 'from' in filter_conditions:
                        conditions.append("md.hora_final >= '{from}' ")

                    if 'to' in filter_conditions:
                        conditions.append("md.hora_inicio <= '{to}' ")

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

    def new(self,payload):
        user = self.getUser()

        parameters = {
            'fecha_inicio': payload['fecha_inicio'],
            'fecha_fin': payload['fecha_fin'],
            'cantidad_horas' : payload['cantidad_horas'],
            'tipo_hora' : payload['tipo_hora'],
            'id_user_creador' : user.id,                                 
            'observaciones' : payload['observaciones']
        }

        conn = alembic.op.get_bind()
        result = conn.execute(
            text(
                """
                INSERT INTO integrador.horas_exmasivas (
                    hora_inicio
                    ,hora_final
                    ,tipo_de_hora
                    ,cantidad
                    ,fecdia
                    ,usuario_creador
                    ,observaciones 
                    ,status
                    ) 
                VALUES (
                    :fecha_inicio
                    ,:fecha_fin
                    ,:tipo_hora
                    ,:cantidad_horas
                    ,CURRENT_DATE
                    ,:id_user_creador
                    ,:observaciones 
                    ,0
                    ) RETURNING horas_exmasivas.serial
                """
                        ), 
            **parameters
        )

        header_id = result.fetchone()[0]

        for cedula in payload['trabajadores']:
            conn.execute(
                text(
                    """
                    INSERT INTO integrador.horas_exmasivas_trabajador (serial,cedula)
                    VALUES (:header_id,:cedula)
                    """), 
                **{'header_id': header_id,'cedula': cedula}
            )


    def getById(self,id):
        parameters = {
            'id': id,
        }
        
        sql = '''
            SELECT DISTINCT
                am."serial" id
                , TO_CHAR(am.hora_inicio,'YYYY-MM-DD') fecha_inicio
                , TO_CHAR(am.hora_final,'YYYY-MM-DD') fecha_fin
                , TO_CHAR(am.fecdia,'YYYY-MM-DD') fecha_registro
                , cantidad cantidad_horas
                , am.tipo_de_hora tipo_hora
                , am.usuario_creador id_usuario_creador
                , se1.name nombre_usuario_creador
                , TO_CHAR(am.fecha_aprobacion,'YYYY-MM-DD') fecha_aprobacion
                , am.usuario_aprobador id_usuario_aprobador
                , se2.name nombre_usuario_aprobador
                , am.observaciones observaciones
                , am.status estatus 
            FROM             
                integrador.horas_exmasivas am 
            JOIN  
                integrador.horas_exmasivas_trabajador amt 
            ON  
                am."serial" = amt."serial" 
            JOIN  
                integrador.vw_trabajador vt 
            ON  
                amt.cedula = vt.cedula 
            LEFT JOIN 
                public.securityelement se1
            ON 
                am.usuario_creador = se1.id
            LEFT JOIN 
                public.securityelement se2
            ON  
                am.usuario_aprobador = se2.id
            WHERE 
                am.serial = {id}
        '''

        sql = sql.format(**parameters)
        
        table_df = pd.read_sql_query(sql,con=db.engine)
        rows = table_df.to_dict('records')

        if len(rows) == 0:
            raise RepositoryUnknownException()                

        #######################################################################################
        header = rows[0]

        sql = '''
            SELECT vt.*
            FROM             
                integrador.horas_exmasivas am 
            JOIN  
                integrador.horas_exmasivas_trabajador amt 
            ON  
                am."serial" = amt."serial" 
            JOIN  
                integrador.vw_trabajador vt 
            ON  
                amt.cedula = vt.cedula 
            WHERE 
                am.serial = {id}
        '''
        sql = sql.format(**parameters)
        
        detail_df = pd.read_sql_query(sql,con=db.engine)
        details = detail_df.to_dict('records')

        header['trabajadores'] = details

        return header        


    def save(self,payload):
        horas_extras_masiva = self.getById(payload['id'])
        user = self.getUser()

        parameters = {
            'id' : payload['id'],
            'fecha_inicio': payload['fecha_inicio'],
            'fecha_fin': payload['fecha_fin'],
            'cantidad_horas' : payload['cantidad_horas'],
            'tipo_hora' : payload['tipo_hora'],
            'id_user_creador' : user.id,                                 
            'observaciones' : payload['observaciones']
        }

        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                UPDATE integrador.horas_exmasivas 
                SET hora_inicio = :fecha_inicio 
                    , hora_final = :fecha_fin
                    , cantidad = :cantidad_horas
                    , tipo_de_hora = :tipo_hora
                    , usuario_creador = :id_user_creador
                    , observaciones = :observaciones
                WHERE 
                    serial = :id
                """
                        ), 
            **parameters
        )

        #Actualizar los Trabajadores a los que afecta 
        conn.execute(
            text(
                """
                DELETE FROM integrador.horas_exmasivas_trabajador
                WHERE serial = :id
                """), 
            **{'id': payload['id']}
        )

        for cedula in payload['trabajadores']:
            conn.execute(
                text(
                    """
                    INSERT INTO integrador.horas_exmasivas_trabajador (serial,cedula)
                    VALUES (:header_id,:cedula)
                    """), 
                **{'header_id': payload['id'],'cedula': cedula}
            )


    def delete(self,id):
        horas_extras_masiva = self.getById(id)
        user = self.getUser()
        parameters = {
            'id' : id
        }

        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                DELETE FROM integrador.horas_exmasivas_trabajador
                WHERE 
                    serial = :id;
                DELETE FROM integrador.horas_exmasivas 
                WHERE 
                    serial = :id;
                """
            ), 
            **parameters
        )


    def approve(self,id):
        justicacion_ausencia = self.getById(id)
        user = self.getUser()

        parameters = {
            'id': id,
            'id_user_aprobador' : user.id
        }

        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                UPDATE integrador.horas_exmasivas 
                SET fecha_aprobacion = CURRENT_DATE 
                    , cantidad_aprobada = cantidad 
                    , usuario_aprobador = :id_user_aprobador 
                    , status = 1
                WHERE 
                    serial = :id
                """
                        ), 
            **parameters
        )


class DailyMarkingRepository(SinergiaRepository):

    def get_justificaciones_ausencia(self,desde,hasta):
        params = {"from": desde, "to": hasta}
        sql = '''
                select *
                from integrador.ausencia_masivas am 
                join integrador.tipos_ausencias ta 
                on am.tpau = ta.codigo 
                join integrador.ausencia_masivas_trabajador amt 
                on amt.serial = am.serial
                where 
                (am.hora_inicio >= '{from}' OR 
                am.hora_final <= '{to}')       
                and am.status = 1
        '''.format(**params)
        ausencias_masivas_df = pd.read_sql_query(sql,con=db.engine)

        ausencia_dataset = []
        for index,row in ausencias_masivas_df.iterrows():    
            ausencia_df = pd.DataFrame({'fecdia': pd.date_range(row.hora_inicio,row.hora_final)})
            ausencia_df['cedula'] = row.cedula
            ausencia_df['horas_ausencia_lote'] = row.cantidad
            ausencia_df['id_tipo_ausencia'] = row.tpau
            ausencia_df['nombre_tipo_ausencia'] = row.descripcion
            ausencia_df['fecdia'] = ausencia_df['fecdia'].dt.strftime('%Y-%m-%d')
            
            ausencia_dataset.append(ausencia_df)

        columns = ['fecdia','cedula','horas_ausencia_lote','id_tipo_ausencia','nombre_tipo_ausencia']        
        ausencias_depuradas = pd.DataFrame([],columns=columns)
        if len(ausencia_dataset) > 0:
            ausencias_para_aplicar = pd.concat(ausencia_dataset)
            ausencias_para_aplicar = ausencias_para_aplicar.reset_index()
            ausencias_depuradas = ausencias_para_aplicar.loc[ausencias_para_aplicar.groupby(['cedula','fecdia']).horas_ausencia_lote.idxmax()].reset_index(drop=True)
            ausencias_depuradas = ausencias_depuradas[['fecdia','cedula','horas_ausencia_lote','id_tipo_ausencia','nombre_tipo_ausencia']] 

        return ausencias_depuradas

    def get_horas_extras_diurnas(self,desde,hasta):
        params = {"from": desde, "to": hasta}

        sql = '''
                select *
                from integrador.horas_exmasivas hem
                join integrador.horas_exmasivas_trabajador hemt 
                on hem.serial = hemt.serial
                where 
                (hem.hora_inicio >= '{from}' OR 
                hem.hora_final <= '{to}')       
                and hem.status = 1
                and hem.tipo_de_hora = 1
        '''.format(**params)

        horasextras_diurnas_masivas_df = pd.read_sql_query(sql,con=db.engine)

        horas_extras_diurnas_dataset = []
        for index,row in horasextras_diurnas_masivas_df.iterrows():    
            horasextras_diurnas_df = pd.DataFrame({'fecdia': pd.date_range(row.hora_inicio,row.hora_final)})
            horasextras_diurnas_df['cedula'] = row.cedula
            horasextras_diurnas_df['horas_diurnas_lote'] = row.cantidad
            horasextras_diurnas_df['fecdia'] = horasextras_diurnas_df['fecdia'].dt.strftime('%Y-%m-%d')
            
            horas_extras_diurnas_dataset.append(horasextras_diurnas_df)

        columns = ['fecdia','cedula','horas_diurnas_lote']
        horasextras_diurnas_depuradas = pd.DataFrame([],columns=columns)
        if len(horas_extras_diurnas_dataset) > 0 :        
            horasextras_diurnas_para_aplicar = pd.concat(horas_extras_diurnas_dataset)

            horasextras_diurnas_para_aplicar = horasextras_diurnas_para_aplicar.reset_index()
            horasextras_diurnas_depuradas = horasextras_diurnas_para_aplicar.loc[horasextras_diurnas_para_aplicar.groupby(['cedula','fecdia']).horas_diurnas_lote.idxmax()].reset_index(drop=True)
            horasextras_diurnas_depuradas = horasextras_diurnas_depuradas[['fecdia','cedula','horas_diurnas_lote']]

        return horasextras_diurnas_depuradas

    def get_horas_extras_nocturnas(self,desde,hasta):
        params = {"from": desde, "to": hasta}
        sql = '''
                select *
                from integrador.horas_exmasivas hem
                join integrador.horas_exmasivas_trabajador hemt 
                on hem.serial = hemt.serial
                where 
                (hem.hora_inicio >= '{from}' OR 
                hem.hora_final <= '{to}')       
                and hem.status = 1
                and hem.tipo_de_hora = 2
        '''.format(**params)

        horasextras_nocturnas_masivas_df = pd.read_sql_query(sql,con=db.engine)

        horas_extras_nocturnas_dataset = []
        for index,row in horasextras_nocturnas_masivas_df.iterrows():    
            horasextras_nocturnas_df = pd.DataFrame({'fecdia': pd.date_range(row.hora_inicio,row.hora_final)})
            horasextras_nocturnas_df['cedula'] = row.cedula
            horasextras_nocturnas_df['horas_nocturnas_lote'] = row.cantidad
            horasextras_nocturnas_df['fecdia'] = horasextras_nocturnas_df['fecdia'].dt.strftime('%Y-%m-%d')
            
            horas_extras_nocturnas_dataset.append(horasextras_nocturnas_df)

        columns = ['fecdia','cedula','horas_nocturnas_lote']
        horasextras_nocturnas_depuradas = pd.DataFrame([],columns=columns)
        if len(horas_extras_nocturnas_dataset) > 0 :
            horasextras_nocturnas_para_aplicar = pd.concat(horas_extras_nocturnas_dataset)

            horasextras_nocturnas_para_aplicar = horasextras_nocturnas_para_aplicar.reset_index()
            horasextras_nocturnas_depuradas = horasextras_nocturnas_para_aplicar.loc[horasextras_nocturnas_para_aplicar.groupby(['cedula','fecdia']).horas_nocturnas_lote.idxmax()].reset_index(drop=True)
            horasextras_nocturnas_depuradas = horasextras_nocturnas_depuradas[['fecdia','cedula','horas_nocturnas_lote']]

        return horasextras_nocturnas_depuradas

    
    def get_asistencia_diaria(self,query_params):

        sql = '''
        SELECT 
            TO_CHAR(md.fecdia,'YYYY-MM-DD') fecdia
            , dia_marcaje
            , id_turno
            , nombre_turno 
            , cedula
            , apellidos
            , nombres 
            , id_cargo
            , nombre_cargo
            , id_tipo_trabajador
            , nombre_tipo_trabajador
            , id_centro_costo
            , nombre_centro_costo
            , estatus 
            , id_grupo_guardia
            , nombre_grupo_guardia
            , id_tipo_nomina
            , nombre_tipo_nomina
            , nombre_tipo_marcaje
            , TO_CHAR(marcaje_inicial,'YYYY-MM-DD HH24:MI:SS') marcaje_inicial
            , TO_CHAR(marcaje_final,'YYYY-MM-DD HH24:MI:SS') marcaje_final
            , TO_CHAR(inicio_planificado,'YYYY-MM-DD HH24:MI:SS') inicio_planificado
            , TO_CHAR(fin_planificado,'YYYY-MM-DD HH24:MI:SS') fin_planificado
            , TO_CHAR( hora_inicio_turno, 'HH24:MI' ) hora_inicio_turno
            , TO_CHAR( hora_final_turno, 'HH24:MI' ) hora_final_turno 
            , TO_CHAR( horas_planificadas, 'HH24:MI' ) horas_planificadas 
            , TO_CHAR( horas_marcajes, 'HH24:MI' ) horas_marcajes 
            , id_tipo_marcaje 
            , nombre_tipo_marcaje 
            , horas_ausencias_calculadas 
            , horas_extras_calculadas 
            , horas_ausencias_aprobadas 
            , horas_extras_aprobadas 
            , suma_horas_ausencias_creadas
            , suma_horas_extras_creadas 
            , suma_horas_ausencias_aprobadas 
            , suma_horas_extras_aprobadas 
        FROM 
            integrador.vw_marcajes_dia_con_totales md 
        {conditions}
        {order_by}
        {limits_offset}
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
                        conditions.append('md.cedula  = {cedula_trabajador}')

                    if 'id_centro_costo' in filter_conditions:                       
                        if type(filter_conditions['id_centro_costo']) == str :
                            conditions.append("md.id_centro_costo = '{id_centro_costo}' ")
                        else:
                            if type(filter_conditions['id_centro_costo'] is list) and len(filter_conditions['id_centro_costo']) > 1:
                                filter_conditions['id_centro_costo'] = tuple(filter_conditions['id_centro_costo'])    
                                conditions.append('md.id_centro_costo IN {id_centro_costo}')
                            else:
                                filter_conditions['id_centro_costo'] = (filter_conditions['id_centro_costo'][0])
                                conditions.append("md.id_centro_costo = '{id_centro_costo}' ")

                    if 'id_tipo_nomina' in filter_conditions:
                        if type(filter_conditions['id_tipo_nomina']) == str:
                            conditions.append("md.id_tipo_nomina = '{id_tipo_nomina}' ")
                        else:
                            if type(filter_conditions['id_tipo_nomina'] is list) and len(filter_conditions['id_tipo_nomina']) > 1:
                                filter_conditions['id_tipo_nomina'] = tuple(filter_conditions['id_tipo_nomina'])    
                                conditions.append('md.id_tipo_nomina IN {id_tipo_nomina}')
                            else:
                                filter_conditions['id_tipo_nomina'] = (filter_conditions['id_tipo_nomina'][0])
                                conditions.append("md.id_tipo_nomina = '{id_tipo_nomina}' ")

                    if 'id_turno' in filter_conditions:
                        if type(filter_conditions['id_turno']) == str:
                            conditions.append("md.id_turno = '{id_turno}' ")
                        else:
                            if type(filter_conditions['id_turno'] is list) and len(filter_conditions['id_turno']) > 1:
                                filter_conditions['id_turno'] = tuple(filter_conditions['id_turno']) 
                                conditions.append('md.id_turno IN {id_turno}')
                            else:
                                filter_conditions['id_turno'] = (filter_conditions['id_turno'][0])
                                conditions.append("md.id_turno = '{id_turno}' ")

                    if 'from' in filter_conditions:
                        conditions.append("md.fecdia >= '{from}' ")

                    if 'to' in filter_conditions:
                        conditions.append("md.fecdia <= '{to}' ")

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
        return table_df

    def get_cantidad_asistencia_diaria(self,query_params):

        count_sql = '''
    SELECT COUNT(*) count_rows 
    FROM 
    integrador.vw_marcajes_dia_con_totales md
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
                        conditions.append('md.cedula  = {cedula_trabajador}')

                    if 'id_centro_costo' in filter_conditions:
                        if type(filter_conditions['id_centro_costo']) == str :
                            conditions.append("md.id_centro_costo = '{id_centro_costo}' ")
                        else:
                            if type(filter_conditions['id_centro_costo'] is list) and len(filter_conditions['id_centro_costo']) > 1:
                                filter_conditions['id_centro_costo'] = tuple(filter_conditions['id_centro_costo'])    
                                conditions.append('md.id_centro_costo IN {id_centro_costo}')
                            else:
                                filter_conditions['id_centro_costo'] = (filter_conditions['id_centro_costo'][0])
                                conditions.append("md.id_centro_costo = '{id_centro_costo}' ")

                            

                    if 'id_tipo_nomina' in filter_conditions:
                        if type(filter_conditions['id_tipo_nomina']) == str:
                            conditions.append("md.id_tipo_nomina = '{id_tipo_nomina}' ")
                        else:
                            if type(filter_conditions['id_tipo_nomina'] is list) and len(filter_conditions['id_tipo_nomina']) > 1:
                                filter_conditions['id_tipo_nomina'] = tuple(filter_conditions['id_tipo_nomina'])
                                conditions.append('md.id_tipo_nomina IN {id_tipo_nomina}')
                            else:
                                filter_conditions['id_tipo_nomina'] = (filter_conditions['id_tipo_nomina'][0])
                                conditions.append("md.id_tipo_nomina = '{id_tipo_nomina}' ")
                            

                    if 'id_turno' in filter_conditions:
                        if type(filter_conditions['id_turno']) == str:
                            conditions.append("md.id_turno = '{id_turno}' ")
                        else:
                            if type(filter_conditions['id_turno'] is list) and len(filter_conditions['id_turno']) > 1:
                                filter_conditions['id_turno'] = tuple(filter_conditions['id_turno'])    
                                conditions.append('md.id_turno IN {id_turno}')
                            else:
                                filter_conditions['id_turno'] = (filter_conditions['id_turno'][0])
                                conditions.append("md.id_turno = '{id_turno}' ")
                           

                    if 'from' in filter_conditions:
                        conditions.append("md.fecdia >= '{from}' ")

                    if 'to' in filter_conditions:
                        conditions.append("md.fecdia <= '{to}' ")

                    where_clausule = 'WHERE ' + ' AND '.join(conditions)
                    where_clausule = where_clausule.format(**filter_conditions)

                    parameters['conditions'] = where_clausule

        count_sql = count_sql.format(**parameters)
        count_df = pd.read_sql_query(count_sql,con=db.engine)
        result_count = count_df.to_dict('records')
        count_all_rows = result_count[0]['count_rows']

        return count_all_rows


    def get(self,query_params):
        if len(query_params) > 0:

            if 'filter' in query_params:
                filter_conditions = query_params['filter']

                desde = None
                hasta = None

                if 'from' in filter_conditions:
                    desde =  filter_conditions['from']

                if 'to' in filter_conditions:
                    hasta =  filter_conditions['to']

                if desde is None or hasta is None:
                    raise RepositoryUnknownException()                

                asistencia_df = self.get_asistencia_diaria(query_params)
                justificiaciones_df = self.get_justificaciones_ausencia(desde,hasta)
                horas_extras_diurnas_df = self.get_horas_extras_diurnas(desde,hasta)
                horas_extras_nocturnas_df = self.get_horas_extras_nocturnas(desde,hasta)

                analisis_empleado = pd.merge(left=asistencia_df, right=justificiaciones_df, how='left', left_on=['fecdia','cedula'], right_on=['fecdia','cedula'])
                analisis_empleado = pd.merge(left=analisis_empleado, right=horas_extras_diurnas_df, how='left', left_on=['fecdia','cedula'], right_on=['fecdia','cedula'])
                analisis_empleado = pd.merge(left=analisis_empleado, right=horas_extras_nocturnas_df, how='left', left_on=['fecdia','cedula'], right_on=['fecdia','cedula'])

                analisis_empleado["nombre_tipo_ausencia"] = analisis_empleado["nombre_tipo_ausencia"].fillna('')
                analisis_empleado = analisis_empleado.fillna(0)

                rows = analisis_empleado.to_dict('records')
                count_result_rows = len(rows)

                count_all_rows = self.get_cantidad_asistencia_diaria(query_params)

                return  { 'count': count_result_rows, 'total':  count_all_rows  ,'data' : rows}

            else: # El Filter el Obligatorio para que este servicio trabaje
                raise RepositoryUnknownException()                

        else:  # No se ha enviado el payload de condiciones para desarrollar la consulta
            raise RepositoryUnknownException()

class ManualMarkingRepository(SinergiaRepository):

    def getAsistenciaDiaria(self,event_date,cedula):
        parameters = {
            'event_date' : event_date,
            'cedula' : cedula
        }

        sql = '''
        SELECT *
        FROM 
            integrador.vw_marcajes_dia_con_totales md 
        WHERE 
            md.fecdia = '{event_date}'        
            AND md.cedula  = {cedula}
        '''
        sql = sql.format(**parameters)

        table_df = pd.read_sql_query(sql,con=db.engine)
        rows = table_df.to_dict('records')
        
        return rows[0] if len(rows) > 0  else None


    def getAsistenciaPlanificada(self,event_date,cedula):
        parameters = {
            'event_date' : event_date,
            'cedula' : cedula
        }

        sql = '''
        SELECT *
        FROM 
            integrador.hojas_tiempo
        WHERE 
            md.fecha = '{event_date}'        
            AND md.cedula  = {cedula}
        '''
        sql = sql.format(**parameters)

        table_df = pd.read_sql_query(sql,con=db.engine)
        rows = table_df.to_dict('records')

        return rows[0] if len(rows) > 0  else None


    def getTurno(self,codigo):
        parameters = {
            'codigo' : codigo,
        }

        sql = '''
        SELECT *
        FROM 
            integrador.turnos
        WHERE 
            codigo = '{codigo}'        
        '''
        sql = sql.format(**parameters)

        table_df = pd.read_sql_query(sql,con=db.engine)
        rows = table_df.to_dict('records')

        return rows[0] if len(rows) > 0  else None


    def crearAsistenciaDiaria(self,payload,planificacion):
        
        parameters = {
            'fecha' : payload['fecha'],
            'cedula' : payload['cedula'],
            'id_turno': payload['id_turno'],
            'inicio_planificado': None,
            'fin_planificado': None,
            'horas_planificadas': None
        }

        # La planificacion existe usar lo planificado 
        if not planificacion is None:
            fecha_inicio_str = parameters['fecha']
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%y-%m-%d')
            fechahora_inicio = datetime.combine(fecha_inicio,planificacion['hora_inicio'])
            fechahora_fin = datetime.combine(fecha_inicio,planificacion['hora_final'])
            parameters['inicio_planificado'] = fechahora_inicio
            parameters['fin_planificado'] = fechahora_fin
            parameters['horas_planificadas'] = fechahora_fin - fechahora_inicio
        else:
            turno = self.getTurno()
            if not turno is None:
                fecha_inicio_str = parameters['fecha']
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%y-%m-%d')

                fechahora_inicio = datetime.combine(fecha_inicio,turno['hora_inicio'])
                fechahora_fin = datetime.combine(fecha_inicio,turno['hora_final'])
                parameters['inicio_planificado'] = fechahora_inicio
                parameters['fin_planificado'] = fechahora_fin
                parameters['horas_planificadas'] = fechahora_fin - fechahora_inicio

        update_sentence = """ 
            INSERT INTO integrador.marcaciones_dia (
                fecdia
                , cedula
                , turno
                , hora_inicial_p
                , hora_final_p
                , horas_nomina_p
                , codigo_biostar
            ) 
            VALUE (
                :fecha
                , :cedula
                , :id_turno 
                , :inicio_planificado
                , :fin_planificado
                , :horas_planificadas
                , 99
            )
        """

        conn = alembic.op.get_bind()
        conn.execute(text(update_sentence),**parameters)


    def actualizarAsistenciaDiaria(self,payload):

        field_to_update = 'fecha_inicio_dia' if payload['tipo_evento'] == 1 else 'fecha_fin_dia'
        update_sentence = """ 
            UPDATE integrador.marcaciones_dia 
            SET %s   = :fecha_hora_evento
                , codigo_biostar = 99
            WHERE 
                fecdia = :fecha
                AND cedula  = :cedula """   %  (field_to_update)
        conn = alembic.op.get_bind()
        conn.execute(text(update_sentence),**payload)

        update_sentence = """ 
            UPDATE integrador.marcaciones_dia 
            SET  total_horas_marcaje = fecha_fin_dia - fecha_inicio_dia
                , horas_ext_gen = 0
                , horas_ext_aproba = 0
                , horas_ausencias = 0
                , horas_ausencias_aprob = 0
            WHERE 
                fecdia = :fecha
                AND cedula  = :cedula 
                AND NOT fecha_fin_dia IS NULL 
                AND NOT fecha_inicio_dia IS NULL """  
        conn = alembic.op.get_bind()
        conn.execute(text(update_sentence),**payload)


    def calcularSobretiempoYAusencia(self,payload):
        pass


    def sincronizarAsistenciaDiaria(self,payload):
        event_date = payload['fecha']
        cedula = payload['cedula']

        marcaje = self.getAsistenciaDiaria(event_date,cedula)
        if marcaje is None:
            planificacion = self.getAsistenciaPlanificada(event_date,cedula)
            self.crearAsistenciaDiaria(planificacion,payload)
            self.actualizarAsistenciaDiaria(payload)
        else:
            #Se actualiza la fecha de acuerdo al evento
            self.actualizarAsistenciaDiaria(payload)

        self.calcularSobretiempoYAusencia(payload)


    def new(self,payload):
        user = self.getUser()
        parameters = {
            'fecha': payload['fecha'],
            'cedula' : payload['cedula'],
            'id_user_creador' : user.id,
            'observaciones' : payload['observaciones'],
            'id_turno' : payload['id_turno'],
            'tipo_evento' : payload['tipo_evento'], 
            'fecha_hora_evento' : payload['fecha_hora_evento'],
        }
        
        self.sincronizarAsistenciaDiaria(parameters)
        
        insert_sentence = ''' INSERT INTO integrador.marcaciones_dia_manual ( 
                fecdia
                ,cedula
                ,tipo_evento
                ,fechaevento
                ,observaciones
                ,turno
                ,usuario_creador
                ,tipo_de_marcaje
                ,fecharegistro 
            ) VALUES (
                :fecha
                , :cedula
                , :tipo_evento
                , :fecha_hora_evento
                , :observaciones
                , :id_turno
                , :id_user_creador
                , 99
                ,CURRENT_DATE
            )
        '''
        conn = alembic.op.get_bind()
        conn.execute(text(insert_sentence),**parameters)

    
    def getById(self,event_date,cedula,id):
        
        parameters = {
            'id': id,
            'event_date' : event_date,
            'cedula' : cedula
        }
        
        sql = '''
            SELECT 
                mdm."serial" id
                , TO_CHAR(vmd.fecdia,'YYYY-MM-DD') fecha_marcaje
                , vmd.cedula 
                , vmd.apellidos 
                , vmd.nombres 
                , vmd.id_centro_costo 
                , vmd.nombre_centro_costo 
                , vmd.id_tipo_nomina 
                , vmd.nombre_tipo_nomina 
                , vmd.id_cargo 
                , vmd.nombre_cargo 
                , mdm.turno id_turno
                , t.descripcion  nombre_turno 
                , TO_CHAR(mdm.fechaevento,'YYYY-MM-DD HH24:MI:SS') fecha_hora_evento	
                , mdm.tipo_evento tipo_evento
                , mdm.tipo_de_marcaje id_tipo_marcaje 
                , tdm.descripcion_biostar  nombre_tipo_marcaje
                , mdm.observaciones observaciones
                , TO_CHAR(mdm.fecharegistro ,'YYYY-MM-DD') fecha_registro
                , mdm.usuario_creador id_usuario_creador
                , s."name" nombre_usuario_creador	
            FROM 
                integrador.vw_marcajes_dia vmd
            JOIN 
                integrador.marcaciones_dia_manual mdm 
            ON 
                vmd.fecdia = mdm.fecdia 
                and vmd.cedula = mdm.cedula 
            JOIN 
                integrador.tipos_de_marcaje tdm 
            ON 
                tdm.codigo_biostar = mdm.tipo_de_marcaje 
            LEFT JOIN
                integrador.turnos t 
            ON 
                t.codigo  = mdm.turno 
            LEFT JOIN
                public.securityelement s 
            ON
                s.id = mdm.usuario_creador  
            WHERE 
                mdm.serial = {id}
                AND mdm.fecdia = '{event_date}'         
                AND mdm.cedula  = {cedula}
        '''

        sql = sql.format(**parameters)
        
        table_df = pd.read_sql_query(sql,con=db.engine)
        rows = table_df.to_dict('records')
        
        if len(rows) == 0:
            raise RepositoryUnknownException()                

        return rows[0]        


    def save(self,payload):

        manual_marking = self.getById(payload['fecha'],payload['cedula'],payload['id'])
        user = self.getUser()  

        parameters = {
            'id': payload['id'],
            'fecha': payload['fecha'],
            'cedula' : payload['cedula'],
            'id_user_creador' : user.id,
            'observaciones' : payload['observaciones'],
            'id_turno' : payload['id_turno'],
            # 'id_tipo_marcaje' : 99, #99 Marcaje Manual 
            'tipo_evento' : payload['tipo_evento'], #1 Entrada #2 Salida
            'fecha_hora_evento' : payload['fecha_hora_evento'],
        }

        # Reflejar el Cambio en la Tabla de Marcajes Diario
        self.sincronizarAsistenciaDiaria(parameters)

        update_sentence = """
                UPDATE integrador.marcaciones_dia_manual
                SET tipo_evento = :tipo_evento
                    , fechaevento = :fecha_hora_evento
                    , observaciones = :observaciones
                    , turno = :id_turno
                    , usuario_creador = :id_user_creador
                    , tipo_de_marcaje = 99
                    , fecharegistro = CURRENT_DATE
                WHERE 
                    serial = :id
                    AND fecdia = :fecha
                    AND cedula  = :cedula 
                """

        conn = alembic.op.get_bind()
        conn.execute(text( update_sentence),**parameters)

    def get(self,query_params):
        sql = '''
            SELECT 
                mdm."serial" id
                , TO_CHAR(vmd.fecdia,'YYYY-MM-DD') fecha_marcaje
                , vmd.cedula 
                , vmd.apellidos 
                , vmd.nombres 
                , vmd.id_centro_costo 
                , vmd.nombre_centro_costo 
                , vmd.id_tipo_nomina 
                , vmd.nombre_tipo_nomina 
                , vmd.id_cargo 
                , vmd.nombre_cargo 
                , mdm.turno id_turno
                , t.descripcion  nombre_turno 
                , TO_CHAR(mdm.fechaevento,'YYYY-MM-DD HH24:MI:SS') fecha_hora_evento	
                , mdm.tipo_evento tipo_evento
                , mdm.tipo_de_marcaje id_tipo_marcaje 
                , tdm.descripcion_biostar  nombre_tipo_marcaje
                , mdm.observaciones observaciones
                , TO_CHAR(mdm.fecharegistro ,'YYYY-MM-DD') fecha_registro
                , mdm.usuario_creador id_usuario_creador
                , s."name" nombre_usuario_creador	
            FROM 
                integrador.vw_marcajes_dia vmd
            JOIN 
                integrador.marcaciones_dia_manual mdm 
            ON 
                vmd.fecdia = mdm.fecdia 
                and vmd.cedula = mdm.cedula 
            JOIN 
                integrador.tipos_de_marcaje tdm 
            ON 
                tdm.codigo_biostar = mdm.tipo_de_marcaje 
            LEFT JOIN
                integrador.turnos t 
            ON 
                t.codigo  = mdm.turno 
            LEFT JOIN
                public.securityelement s 
            ON
                s.id = mdm.usuario_creador 
        {conditions}
        {order_by}
        {limits_offset}
        '''

        count_sql = '''
            SELECT COUNT(*) count_rows 
            FROM 
                integrador.vw_marcajes_dia vmd
            JOIN 
                integrador.marcaciones_dia_manual mdm 
            ON 
                vmd.fecdia = mdm.fecdia 
                and vmd.cedula = mdm.cedula 
            JOIN 
                integrador.tipos_de_marcaje tdm 
            ON 
                tdm.codigo_biostar = mdm.tipo_de_marcaje 
            LEFT JOIN
                integrador.turnos t 
            ON 
                t.codigo  = mdm.turno 
            LEFT JOIN
                public.securityelement s 
            ON
                s.id = mdm.usuario_creador 
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
                        conditions.append('vmd.cedula  = {cedula_trabajador}')

                    if 'id_centro_costo' in filter_conditions:
                        if type(filter_conditions['id_centro_costo']) == str :
                            conditions.append("vmd.id_centro_costo = '{id_centro_costo}' ")
                        else:
                            if type(filter_conditions['id_centro_costo'] is list) and len(filter_conditions['id_centro_costo']) > 1:
                                filter_conditions['id_centro_costo'] = tuple(filter_conditions['id_centro_costo'])    
                                conditions.append('vmd.centro_costo IN {id_centro_costo}')
                            else:
                                filter_conditions['id_centro_costo'] = (filter_conditions['id_centro_costo'][0])
                                conditions.append("vmd.id_centro_costo = '{id_centro_costo}' ")
                            

                    if 'id_tipo_nomina' in filter_conditions:
                        if type(filter_conditions['id_tipo_nomina']) == str :
                            conditions.append("vmd.id_tipo_nomina = '{id_tipo_nomina}'") 
                        else:
                            if type(filter_conditions['id_tipo_nomina'] is list) and len(filter_conditions['id_tipo_nomina']) > 1:
                                filter_conditions['id_tipo_nomina'] = tuple(filter_conditions['id_tipo_nomina'])    
                                conditions.append('vmd.id_tipo_nomina IN {id_tipo_nomina}')
                            else:
                                filter_conditions['id_tipo_nomina'] = (filter_conditions['id_tipo_nomina'][0])
                                conditions.append("vmd.id_tipo_nomina = '{id_tipo_nomina}'") 

                            

                    if 'id_turno' in filter_conditions:
                        if type(filter_conditions['id_turno']) == str:
                            conditions.append("mdm.turno = '{id_turno}'") 
                        else:
                            if type(filter_conditions['id_turno'] is list) and len(filter_conditions['id_turno']) > 1:
                                filter_conditions['id_turno'] = tuple(filter_conditions['id_turno'])    
                                conditions.append('mdm.turno IN {id_turno}')
                            else:
                                filter_conditions['id_turno'] = (filter_conditions['id_turno'][0])
                                conditions.append("mdm.turno = '{id_turno}'") 

                    if 'from' in filter_conditions:
                        conditions.append("vmd.fecdia >= '{from}' ")

                    if 'to' in filter_conditions:
                        conditions.append("vmd.fecdia <= '{to}' ")

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

    def delete(self,event_date,cedula,id):

        manual_marking = self.getById(event_date,cedula,id)
        user = self.getUser()

        parameters = {
            'id': id,
            'fecha': event_date,
            'cedula' : cedula,
        }        

        field_to_update = 'fecha_inicio_dia' if manual_marking['tipo_evento'] == 1 else 'fecha_fin_dia'
        update_sentence = """ 
            UPDATE integrador.marcaciones_dia 
            SET %s   = NULL
            WHERE 
                fecdia = :fecha
                AND cedula  = :cedula """   %  (field_to_update)
        conn = alembic.op.get_bind()
        conn.execute(text(update_sentence),**parameters)

        parameters = {
            'id': id,
            'fecha': event_date,
            'cedula' : cedula,
        }

        delete_sentence  = """
                DELETE FROM integrador.marcaciones_dia_manual 
                WHERE 
                    serial = :id
                    AND fecdia = :fecha
                    AND cedula  = :cedula
        """
        conn = alembic.op.get_bind()
        conn.execute(text(delete_sentence),**parameters)