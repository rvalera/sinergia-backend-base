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
                    ,estatus
                    ) 
                VALUES (
                    :fecha
                    ,:cedula
                    ,CURRENT_DATE
                    ,:id_justificacion_ausencia
                    ,:horas_generadas
                    ,:id_user_creador
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
        
        print(sql)

        table_df = pd.read_sql_query(sql,con=db.engine)
        rows = table_df.to_dict('records')
        
        if len(rows) == 0:
            raise RepositoryUnknownException()                

        return rows[0]        

    #Validar que las justificacion se hacen en el periodo de semanas definidos para la aplicacion, No Modificar si ya esta aprobada
    def save(self,payload):

        justicacion_ausencia = self.getById(payload['fecha'],payload['cedula'],payload['id'])
        print(justicacion_ausencia)
        user = self.getUser()

        parameters = {
            'id': payload['id'],
            'fecha': payload['fecha'],
            'cedula' : payload['cedula'],
            'id_user_creador' : user.id,
            'horas_generadas' : payload['horas_generadas'],
            'id_justificacion_ausencia' : payload['id_justificacion_ausencia'],
        }

        conn = alembic.op.get_bind()
        conn.execute(
            text(
                """
                UPDATE integrador.marcaciones_dia_ausencias 
                SET tpau = :id_justificacion_ausencia
                    , cantidad_generada = :horas_generadas
                    , user_creador = :id_user_creador
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
    def approve(self,event_date,cedula,id):
        overtime_event = self.getById(event_date,cedula,id)
        user = self.getUser()

        parameters = {
            'id': id,
            'event_date' : event_date,
            'cedula' : cedula,
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
        pass

    def new(self,payload):
        pass

    def remove(self,payload):
        pass

    def save(self,payload):
        pass

    def approve(self,id):
        pass


class BatchOvertimeRepository(SinergiaRepository):

    def get(self,query_params):    
        pass

    def new(self,payload):
        pass

    def remove(self,payload):
        pass

    def save(self,payload):
        pass

    def approve(self,id):
        pass


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


        horasextras_nocturnas_para_aplicar = pd.concat(horas_extras_nocturnas_dataset)

        horasextras_nocturnas_para_aplicar = horasextras_nocturnas_para_aplicar.reset_index()
        horasextras_nocturnas_depuradas = horasextras_nocturnas_para_aplicar.loc[horasextras_nocturnas_para_aplicar.groupby(['cedula','fecdia']).horas_nocturnas_lote.idxmax()].reset_index(drop=True)
        horasextras_nocturnas_depuradas = horasextras_nocturnas_depuradas[['fecdia','cedula','horas_nocturnas_lote']]

        return horasextras_nocturnas_depuradas

    
    def get_asistencia_diaria(self,query_params):

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
            , nombre_tipo_marcaje
            , TO_CHAR(marcaje_inicial,'YYYY-MM-DD HH24:MI:SS') marcaje_inicial
            , TO_CHAR(marcaje_final,'YYYY-MM-DD HH24:MI:SS') marcaje_final
            , TO_CHAR(inicio_planificado,'YYYY-MM-DD HH24:MI:SS') inicio_planificado
            , TO_CHAR(fin_planificado,'YYYY-MM-DD HH24:MI:SS') fin_planificado
            , TO_CHAR( hora_inicio_turno, 'HH24:MI' ) hora_inicio_turno
            , TO_CHAR( hora_final_turno, 'HH24:MI' ) hora_final_turno
            , TO_CHAR( horas_planificadas, 'HH24:MI' ) hora_inicio_turno
            , TO_CHAR( horas_marcajes, 'HH24:MI' ) hora_final_turno
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
                        conditions.append('md.id_centro_costo = {id_centro_costo}')

                    if 'id_tipo_trabajador' in filter_conditions:
                        conditions.append('md.id_tipo_trabajador = {id_tipo_trabajador}')

                    if 'id_turno' in filter_conditions:
                        conditions.append('md.id_turno = {id_turno}')

                    if 'to' in filter_conditions:
                        conditions.append("md.fecdia >= '{to}' ")

                    if 'from' in filter_conditions:
                        conditions.append("md.fecdia <= '{from}' ")

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
                        conditions.append('md.id_centro_costo = {id_centro_costo}')

                    if 'id_tipo_trabajador' in filter_conditions:
                        conditions.append('md.id_tipo_trabajador = {id_tipo_trabajador}')

                    if 'id_turno' in filter_conditions:
                        conditions.append('md.id_turno = {id_turno}')

                    if 'to' in filter_conditions:
                        conditions.append("md.fecdia >= '{to}' ")

                    if 'from' in filter_conditions:
                        conditions.append("md.fecdia <= '{from}' ")

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
                    desde =  filter_conditions['to']

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

    def new(self,payload):
        pass




