'''
Created on 17 dic. 2019

@author: ramon
'''
from getpass import getuser
from app.v1.models.security import SecurityElement, User, PersonExtension
from app.v1.models.hr import Beneficiario, CarnetizacionLog, Especialidad, EstacionTrabajo, HistoriaMedica, Persona,Estado,Municipio, SalaDeEspera,Trabajador,TipoTrabajador,EstatusTrabajador,TipoNomina,\
    TipoCargo,UbicacionLaboral,Empresa, Patologia, Cita, Discapacidad, Visita, ConsultaMedica, Medico
from app import redis_client, db
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from app.exceptions.base import DataNotFoundException, CitaFechaInvalidaException, CitaFechaSinCupoException, CryptoPOSException, ConnectionException,NotImplementedException,DatabaseException,\
                                IntegrityException, ParametersNotFoundException, CitaException, CitaConConsultaException, CitaPersonaEquivocadaException, PacienteConCitaException, DeleteDataException,\
                                DataAlreadyRegisteredException                                    
from .base import SinergiaRepository

import pandas as pd
import logging

from sqlalchemy import text    
from sqlalchemy import select, func
from sqlalchemy import and_

from psycopg2 import OperationalError, errorcodes, errors    
from sqlalchemy import exc
from datetime import datetime, timedelta
from app.v1.models.constant import *


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


class AreaRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from hospitalario.area',con=db.engine)
            table_df = table_df.fillna('')
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)


class EstacionTrabajoRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from hospitalario.estaciontrabajo',con=db.engine)
            table_df = table_df.fillna('')
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

    def getByName(self, nombre):
        try:
            estaciontrabajo = EstacionTrabajo.query.filter(EstacionTrabajo.nombre == nombre).first()
            if estaciontrabajo is None:
                #Se arroja excepcion, el Medico ya esta creado
                raise DataNotFoundException()     
                  
            return estaciontrabajo
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

    def new(self,payload):
        direccionip = payload['direccionip'] if 'direccionip' in payload else None
        if direccionip:
            #Se chequea que la direccion ip no esté registrada
            aux = EstacionTrabajo.query.filter(EstacionTrabajo.direccionip == direccionip).first()
            if aux:
                #Se arroja excepcion, el beneficiario ya esta creado
                raise DataAlreadyRegisteredException()

            estacion = EstacionTrabajo()
            estacion.nombre = payload['nombre']
            estacion.direccionip = payload['direccionip']
            estacion.dispositivobiostar = payload['dispositivobiostar']
            db.session.session.add(estacion)
            db.session.commit() 
        else:
            #No se proporciono la direccion ip de la estacion
            raise ParametersNotFoundException()
    
    def save(self,payload):
        idestaciontrabajo = payload['idestaciontrabajo'] if 'idestaciontrabajo' in payload else None
        if idestaciontrabajo:
            #Se chequea que la estacion exista previamente 
            estaciontrabajo = EstacionTrabajo.query.filter(EstacionTrabajo.idestaciontrabajo == idestaciontrabajo).first()
            if estaciontrabajo is None:
                #Se arroja excepcion, la estaciontrabajo no existe
                raise DataNotFoundException()

            estaciontrabajo.nombre = payload['nombre']
            estaciontrabajo.direccionip = payload['direccionip']
            estaciontrabajo.dispositivobiostar = payload['dispositivobiostar']
            db.session.add(estaciontrabajo)
            db.session.commit()            
        else:
            #No se proporciono el codigo, es obligatorio 
            raise ParametersNotFoundException()

    def delete(self,idestaciontrabajo):
        estaciontrabajo = EstacionTrabajo.query.filter(EstacionTrabajo.idestaciontrabajo == idestaciontrabajo).first()
        if estaciontrabajo is None:
            #Se arroja excepcion, no existe la estacion
            raise DataNotFoundException()
        
        db.session.delete(estaciontrabajo)
        db.session.commit()


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

    def get_patologias(self,payload):
        patologias_list = []
        if 'patologias' in payload:
            ids_patologias = payload['patologias']
            patologias_list = Patologia.query.filter(Patologia.codigopatologia.in_(ids_patologias)).all()
        return patologias_list

    def get_discapacidades(self,payload):
        discapacidades_list = []
        if 'discapacidades' in payload:
            ids_discapacidades = payload['discapacidades']
            discapacidades_list = Discapacidad.query.filter(Discapacidad.codigodiscapacidad.in_(ids_discapacidades)).all()
        return discapacidades_list

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
            current_user = self.getUser()
            empresa_user = current_user.person_extension.empresa
            if not empresa_user is None:
                empresa_id = empresa_user.codigo
                trabajador = Trabajador.query.filter(and_(Trabajador.cedula == cedula, Trabajador.codigoempresa == empresa_id)).first()
            else:
                trabajador = Trabajador.query.filter(Trabajador.cedula == cedula).first()
            if trabajador is None:
                raise DataNotFoundException()
            return trabajador
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)


    def save(self,payload):
        cedula = payload['cedula'] if 'cedula' in payload else None
        if cedula:
            #Se chequea que el trabajador exista previamente 
            trabajador = Trabajador.query.filter(Trabajador.cedula == cedula).first()
            if trabajador is None:
                #Se arroja excepcion, el trabajador no existe
                raise DataNotFoundException()

            trabajador.telefonocelular = payload['telefonocelular']
            trabajador.telefonoresidencia = payload['telefonoresidencia']
            trabajador.correo = payload['correo']
            trabajador.codigoestado = payload['codigoestado']
            trabajador.codigomunicipio = payload['codigomunicipio']
            trabajador.parroquia = payload['parroquia']
            trabajador.sector = payload['sector']
            trabajador.avenidacalle = payload['avenidacalle']
            trabajador.edifcasa = payload['edifcasa']
            trabajador.camisa = payload['camisa']
            trabajador.pantalon = payload['pantalon']
            trabajador.calzado = payload['calzado']
            trabajador.observaciones = payload['observaciones']

            trabajador.historiamedica.gruposanguineo = payload['gruposanguineo']
            #trabajador.historiamedica.discapacidad   = payload['tipodiscapacidad']

            #Se procesan las Patologias de la Historia Medica
            patologias = self.get_patologias(payload) 
            if len(patologias) > 0:
                trabajador.historiamedica.patologias = [p for p in patologias] 
            else:
                trabajador.historiamedica.patologias = []

            #Se procesan las Discapacidades de la Historia Medica
            discapacidades = self.get_discapacidades(payload) 
            if len(discapacidades) > 0:
                trabajador.historiamedica.discapacidades = [p for p in discapacidades] 
            else:
                trabajador.historiamedica.discapacidades = []

            trabajador.fechaactualizacion = datetime.now()
            user = User.query.filter(User.name==self.username.lower()).first()        
            if user:
                trabajador.idusuarioactualizacion = user.id

            #Log Solicitado para Carnetizacion
            carnetizacion_log = CarnetizacionLog()
            carnetizacion_log.cedula = trabajador.cedula 
            carnetizacion_log.telefonocelular = trabajador.telefonocelular
            carnetizacion_log.telefonoresidencia = trabajador.telefonoresidencia
            carnetizacion_log.correo = trabajador.correo
            carnetizacion_log.codigoestado = trabajador.codigoestado
            carnetizacion_log.codigomunicipio = trabajador.codigomunicipio
            carnetizacion_log.parroquia = trabajador.parroquia
            carnetizacion_log.sector = trabajador.sector
            carnetizacion_log.avenidacalle = trabajador.avenidacalle
            carnetizacion_log.edifcasa = trabajador.edifcasa
            carnetizacion_log.camisa = trabajador.camisa
            carnetizacion_log.pantalon = trabajador.pantalon
            carnetizacion_log.calzado = trabajador.calzado
            carnetizacion_log.observaciones = trabajador.observaciones
            carnetizacion_log.gruposanguineo = trabajador.historiamedica.gruposanguineo

            carnetizacion_log.patologias = ",".join([p.nombre for p in patologias] )  
            carnetizacion_log.fechaactualizacion = datetime.now()
            carnetizacion_log.usuarioactualizacion = self.username.lower()

            db.session.add(trabajador)
            db.session.add(carnetizacion_log)
            db.session.commit()            
        else:
            #No se proporciono el username o la contrasena, es obligatorio 
            raise ParametersNotFoundException()

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

class DiscapacidadRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from hospitalario.discapacidad',con=db.engine)
            table_df = table_df.fillna('')
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)


class SalaDeEsperaRepository(SinergiaRepository):
    def getAll(self):
        try:
            table_df = pd.read_sql_query('select * from hospitalario.saladeespera',con=db.engine)
            table_df = table_df.fillna('')
            result = table_df.to_dict('records')
            return result
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

    def new(self,payload):
        salaespera = SalaDeEspera()
        salaespera.nombre = payload['nombre']
        db.session.add(salaespera)
        db.session.commit()            
    
    def save(self,payload):
        idsala = payload['idsala'] if 'idsala' in payload else None
        if idsala:
            #Se chequea que la sala exista previamente 
            salaespera = SalaDeEspera.query.filter(SalaDeEspera.idsala == idsala).first()
            if salaespera is None:
                #Se arroja excepcion, la salaespera ya esta creado
                raise DataNotFoundException()

            salaespera.nombre = payload['nombre']
            db.session.add(salaespera)
            db.session.commit()            
        else:
            #No se proporciono el codigo, es obligatorio 
            raise ParametersNotFoundException()

    def delete(self,idsala):
        #Se chequea que la sala exista previamente 
        salaespera = SalaDeEspera.query.filter(SalaDeEspera.idsala == idsala).first()
        if salaespera is None:
            #Se arroja excepcion, la salaespera no existe
            raise DataNotFoundException()

        db.session.delete(salaespera)
        db.session.commit()


class EspecialidadRepository(SinergiaRepository):
    def getAll(self):
        try:
            '''
            table_df = pd.read_sql_query('select * from hospitalario.especialidad',con=db.engine)
            table_df = table_df.fillna('')
            result = table_df.to_dict('records')
            return result
            '''
            especialidades = Especialidad.query.order_by(Especialidad.nombre.asc()).all()
            return especialidades

            
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)
    
    def getById(self,codigoespecialidad):
        try:
            especialidad = Especialidad.query.filter(Especialidad.codigoespecialidad == codigoespecialidad).first()
            if especialidad is None:
                raise DataNotFoundException()
            return especialidad
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

    def new(self,payload):
        codigoespecialidad = payload['codigoespecialidad'] if 'codigoespecialidad' in payload else None
        if codigoespecialidad:
            #Se chequea que el codigo de la especialidad no se este usando
            aux = Especialidad.query.filter(Especialidad.codigoespecialidad == codigoespecialidad).first()
            if aux:
                #Se arroja excepcion, la especialidad ya esta creada
                raise DataAlreadyRegisteredException()

            especialidad = Especialidad()
            especialidad.codigoespecialidad  = payload['codigoespecialidad']
            especialidad.nombre = payload['nombre']
            especialidad.diasdeatencion = payload['diasdeatencion']
            especialidad.autogestionada = payload['autogestionada']
            especialidad.cantidadmaximapacientes = payload['cantidadmaximapacientes']
            especialidad.colaactiva = True
          
            db.session.add(especialidad)
            db.session.commit()            
        else:
            #No se proporciono el codigo de la especialidad, es obligatorio 
            raise ParametersNotFoundException()
    
    def save(self,payload):
        codigoespecialidad = payload['codigoespecialidad'] if 'codigoespecialidad' in payload else None
        if codigoespecialidad:
            #Se chequea que la especialidad exista previamente 
            especialidad = Especialidad.query.filter(Especialidad.codigoespecialidad == codigoespecialidad).first()
            if especialidad is None:
                #Se arroja excepcion, la especialidad no esta creado
                raise DataNotFoundException()

            especialidad.nombre = payload['nombre']
            especialidad.diasdeatencion = payload['diasdeatencion']
            especialidad.autogestionada = payload['autogestionada']
            especialidad.cantidadmaximapacientes = payload['cantidadmaximapacientes']
            especialidad.idsala = payload['idsala']
            
            db.session.add(especialidad)
            db.session.commit()            
        else:
            #No se proporciono el codigo, es obligatorio 
            raise ParametersNotFoundException()

    def delete(self,codigoespecialidad):
        especialidad = Especialidad.query.filter(Especialidad.codigoespecialidad == codigoespecialidad).first()
        if especialidad is None:
            #Se arroja excepcion, no existe la especialidad
            raise DataNotFoundException()
        
        cita = Cita.query.filter(Cita.codigoespecialidad == codigoespecialidad).first()
        medico = Medico.query.filter(Medico.codigoespecialidad == codigoespecialidad).first()

        if cita or medico:
            #Se arroja excepcion, no se puede borrar la especialidad
            raise DeleteDataException()

        db.session.delete(especialidad)
        db.session.commit()

class MedicoRepository(SinergiaRepository):

    def new(self,payload):
        cedula = payload['cedula'] if 'cedula' in payload else None
        if cedula:
            #Se chequea que el medico NO exista previamente 
            aux = Medico.query.filter(Medico.cedula == cedula).first()
            if aux:
                #Se arroja excepcion, el medico ya esta creado
                raise DataNotFoundException()

            medico = Medico()
            medico.cedula               = payload['cedula']
            medico.nombres              = payload['nombres']
            medico.apellidos            = payload['apellidos']
            medico.sexo                 = payload['sexo']
            medico.fechanacimiento      = payload['fechanacimiento']
            medico.nombres              = payload['nombres']
            medico.apellidos            = payload['apellidos']
            medico.sexo                 = payload['sexo']
            medico.fechanacimiento      = payload['fechanacimiento']
            medico.telefonocelular      = payload['telefonocelular']
            medico.telefonoresidencia   = payload['telefonoresidencia']
            medico.correo               = payload['correo']
            medico.nacionalidad         = payload['nacionalidad']
            medico.sexo                 = payload['sexo']
            medico.codigoestado         = payload['codigoestado']
            medico.codigomunicipio      = payload['codigomunicipio']
            medico.parroquia            = payload['parroquia']
            medico.sector               = payload['sector']
            medico.avenidacalle         = payload['avenidacalle']
            medico.edifcasa             = payload['edifcasa']
            medico.codigoespecialidad   = payload['codigoespecialidad']
          
            db.session.add(medico)
            db.session.commit()            
        else:
            #No se proporciono la cedula, es obligatorio 
            raise ParametersNotFoundException()

    
    def save(self,payload):
        cedula = payload['cedula'] if 'cedula' in payload else None
        if cedula:
            #Se chequea que el medico exista previamente 
            medico = Medico.query.filter(Medico.cedula == cedula).first()
            if medico is None:
                #Se arroja excepcion, el Medico no Existe
                raise DataNotFoundException()

            medico.nombres              = payload['nombres']
            medico.apellidos            = payload['apellidos']
            medico.sexo                 = payload['sexo']
            medico.fechanacimiento      = payload['fechanacimiento']
            medico.nombres              = payload['nombres']
            medico.apellidos            = payload['apellidos']
            medico.sexo                 = payload['sexo']
            medico.fechanacimiento      = payload['fechanacimiento']
            medico.telefonocelular      = payload['telefonocelular']
            medico.telefonoresidencia   = payload['telefonoresidencia']
            medico.correo               = payload['correo']
            medico.nacionalidad         = payload['nacionalidad']
            medico.sexo                 = payload['sexo']
            medico.codigoestado         = payload['codigoestado']
            medico.codigomunicipio      = payload['codigomunicipio']
            medico.parroquia            = payload['parroquia']
            medico.sector               = payload['sector']
            medico.avenidacalle         = payload['avenidacalle']
            medico.edifcasa             = payload['edifcasa']
            medico.codigoespecialidad   = payload['codigoespecialidad']
            
            db.session.add(medico)
            db.session.commit()            
        else:
            #No se proporciono la cedula, es obligatorio 
            raise ParametersNotFoundException()
    

    def delete(self,cedula):
        medico = Medico.query.filter(Medico.cedula == cedula).first()
        if medico is None:
            #Se arroja excepcion, el beneficiario ya esta creado
            raise DataNotFoundException()
        
        consultamedica = ConsultaMedica.query.filter(ConsultaMedica.cedulamedico == cedula).first()
        if consultamedica:
            #Se arroja excepcion, el medico tiene consultas
            raise DeleteDataException()

        db.session.delete(medico)
        db.session.commit()


    def getByCedula(self,cedula):
        try:
            medico = Medico.query.filter(Medico.cedula == cedula).first()
            if medico is None:
                raise DataNotFoundException()
            return medico
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

    
    def getAll(self):
        try:
            medicos = Medico.query.all()
            return medicos
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

    def get_discapacidades(self,payload):
        discapacidades_list = []
        if 'discapacidades' in payload:
            ids_discapacidades = payload['discapacidades']
            discapacidades_list = Discapacidad.query.filter(Discapacidad.codigodiscapacidad.in_(ids_discapacidades)).all()
        return discapacidades_list


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
            #historiamedica.discapacidad   = payload['tipodiscapacidad']
            historiamedica.fecha          = datetime.now().date()
            
            #Se procesan las Patologias de la Historia Medica
            patologias = self.get_patologias(payload) 
            if len(patologias):
                historiamedica.patologias = [p for p in patologias] 

            #Se procesan las Discapacidades de la Historia Medica
            discapacidades = self.get_discapacidades(payload) 
            if len(discapacidades):
                historiamedica.discapacidades = [p for p in discapacidades] 
           
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
            #beneficiario.historiamedica.discapacidad   = payload['tipodiscapacidad']

            #Se procesan las Patologias de la Historia Medica
            patologias = self.get_patologias(payload) 
            if len(patologias) > 0:
                beneficiario.historiamedica.patologias = [p for p in patologias] 
            else:
                beneficiario.historiamedica.patologias = []

            #Se procesan las Discapacidades de la Historia Medica
            discapacidades = self.get_discapacidades(payload) 
            if len(discapacidades) > 0:
                beneficiario.historiamedica.discapacidades = [p for p in discapacidades] 
            else:
                beneficiario.historiamedica.discapacidades = []

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


class HistoriaMedicaRepository(SinergiaRepository):
    def getByCedula(self,cedula):
        try:
            historiamedica = HistoriaMedica.query.filter(HistoriaMedica.cedula == cedula).first()
            if historiamedica is None:
                raise DataNotFoundException()
            return historiamedica
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)


class CitaRepository(SinergiaRepository):

    def getFechasConCitaByEspecialidad(self, codigoespecialidad, fechainicio, fechafin):
        #Buscamos los dias que la especialidad tiene citas en el rango de fecha recibida
        sql_query = f"select fechacita from hospitalario.cita where codigoespecialidad = '{codigoespecialidad}' \
                        and fechacita between '{fechainicio}' and '{fechafin}' and estado <> '{CITA_CANCELADA}'"
        table_df = pd.read_sql_query(sql_query,con=db.engine)
        df2 = table_df.groupby(['fechacita'])['fechacita'].count()
        dictfechasconcita = df2.to_dict()
        formatofecha = '%Y-%m-%d'
        data = {}
        for key in dictfechasconcita:
            pyfecha = key.to_pydatetime()
            fecha = pyfecha.date()
            fechastr = datetime.strftime(fecha, formatofecha)
            nrocitas = dictfechasconcita[key]
            data[fechastr] = nrocitas
        return data


    def canSolicitarCita(self, codigoespecialidad, fechacita):
        especialidad = Especialidad.query.filter(Especialidad.codigoespecialidad == codigoespecialidad).first()
        if especialidad is None:
            raise DataNotFoundException()

        if fechacita is None:
            raise DataNotFoundException()

        cantidadmaximacitas = especialidad.cantidadmaximapacientes
        diasdeatencion = []
        if especialidad.diasdeatencion:
            diasdeatencion = eval(especialidad.diasdeatencion)

        fechacitadt = datetime.strptime(fechacita, '%Y-%m-%d')
        diasemana = fechacitadt.weekday()
        if diasemana not in diasdeatencion:
            raise CitaFechaInvalidaException()

        #Validamos que la fecha de la cita sea valida
        dictfechasconcita = self.getFechasConCitaByEspecialidad(codigoespecialidad, fechacita, fechacita)
        if dictfechasconcita:
            nrocitas = dictfechasconcita[fechacita]
            if nrocitas >= cantidadmaximacitas:
                raise CitaFechaSinCupoException()
        
        return True


    def new(self,payload):
        cedula = payload['cedula'] if 'cedula' in payload else None
        codigoespecialidad = payload['codigoespecialidad'] if 'codigoespecialidad' in payload else None
        fechacita = payload['fechacita'] if 'fechacita' in payload else None

        #Se chequea que la persona exista
        persona = Persona.query.filter(Persona.cedula == cedula).first()
        if persona is None:
            #Se arroja excepcion, la persona no existe en la BD
            raise DataNotFoundException()

        cita_aux = Cita.query.filter(Cita.cedula == cedula, Cita.codigoespecialidad == codigoespecialidad,\
                                 Cita.fechacita == fechacita, Cita.estado != CITA_CANCELADA).first()
        if cita_aux:
            raise PacienteConCitaException()

        if not self.canSolicitarCita(codigoespecialidad, fechacita):
            raise CitaException()

        cita = Cita()
        cita.cedula = cedula
        cita.codigoespecialidad = codigoespecialidad
        cita.fechacita = fechacita
        cita.fechadia = datetime.now().date()
        cita.estado = CITA_PLANIFICADA
        db.session.add(cita)
        db.session.commit()   


    def save(self,payload):         
        idcita = payload['idcita'] if 'idcita' in payload else None
        codigoespecialidad = payload['codigoespecialidad'] if 'codigoespecialidad' in payload else None
        fechacita = payload['fechacita'] if 'fechacita' in payload else None

        cita = Cita.query.filter(Cita.id == idcita, Cita.estado == CITA_PLANIFICADA).first()
        if cita is None:
            raise DataNotFoundException()

        cita_aux = Cita.query.filter(Cita.cedula == cita.cedula, Cita.codigoespecialidad == codigoespecialidad,\
                                 Cita.fechacita == fechacita, Cita.estado != CITA_CANCELADA).first()
        if cita_aux:
            raise PacienteConCitaException()

        if not self.canSolicitarCita(codigoespecialidad, fechacita):
            raise CitaException()
        
        cita.codigoespecialidad = codigoespecialidad
        cita.fechacita = fechacita
        cita.estado = CITA_PLANIFICADA
        db.session.add(cita)
        db.session.commit()   

    
    def confirm(self,payload):         
        idcita = payload['idcita'] if 'idcita' in payload else None

        cita = Cita.query.filter(Cita.id == idcita, Cita.estado == CITA_PLANIFICADA).first()
        if cita is None:
            raise DataNotFoundException()
        
        cita.idbiostar = payload['idbiostar']
        cita.idbiostar2 = payload['idbiostar2']
        cita.estado = CITA_CONFIRMADA
        db.session.add(cita)
        db.session.commit()   


    def attend(self,payload):         
        idcita = payload['idcita'] if 'idcita' in payload else None
        cedulamedico = payload['cedulamedico'] if 'cedulamedico' in payload else None

        cita = Cita.query.filter(Cita.id == idcita, Cita.estado == CITA_EN_COLA).first()
        if cita is None:
            raise DataNotFoundException()

        medico = Medico.query.filter(Medico.cedulamedico == cedulamedico).first()
        if medico is None:
            raise DataNotFoundException()

        cita.fechapasaconsulta = datetime.now()
        cita.estado = CITA_EN_ATENCION

        consulta = ConsultaMedica()
        consulta.cedula = cita.cedula
        consulta.cedulamedico = cedulamedico
        consulta.idcita = cita.id
        consulta.consultorio = None #TODO AQUI VA EL CONSULTORIO
        consulta.estado = CITA_EN_ATENCION

        db.session.add(cita)
        db.session.add(consulta)
        db.session.commit()   


    def end(self,payload):         
        idcita = payload['idcita'] if 'idcita' in payload else None

        cita = Cita.query.filter(Cita.id == idcita, Cita.estado == CITA_EN_ATENCION).first()
        if cita is None:
            raise DataNotFoundException()

        cita.fechafinconsulta = datetime.now()
        cita.estado = CITA_CONCLUIDA
        cita.consultamedica.sintomas = payload['sintomas']
        cita.consultamedica.diagnostico = payload['diagnostico']
        cita.consultamedica.tratamiento = payload['tratamiento']
        cita.consultamedica.examenes = payload['examenes']
        cita.consultamedica.fecha = datetime.now().date()

        db.session.add(cita)
        db.session.commit()   


    def transfer(self,payload):         
        idcita = payload['idcita'] if 'idcita' in payload else None

        cita = Cita.query.filter(Cita.id == idcita, Cita.estado == CITA_EN_ATENCION).first()
        if cita is None:
            raise DataNotFoundException()
        cita.fechafinconsulta = datetime.now().date() 
        cita.estado = CITA_CONCLUIDA

        nueva_cita = Cita()
        nueva_cita.cedula = cita.cedula
        nueva_cita.codigoespecialidad = payload['codigoespecialidad']
        nueva_cita.fechadia = datetime.now().date()
        nueva_cita.fechacita = datetime.now().date()
        nueva_cita.fechaentradacola = datetime.now().date()
        nueva_cita.estado = CITA_EN_COLA

        db.session.add(cita)
        db.session.add(nueva_cita)
        db.session.commit()


    def getById(self,id):
        try:
            citamedica = Cita.query.filter(Cita.id == id).first()
            if citamedica is None:
                raise DataNotFoundException()
            return citamedica
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)


    def getByCedula(self,cedula):
        try:
            citamedica = Cita.query.filter(Cita.cedula == cedula).first()
            if citamedica is None:
                raise DataNotFoundException()
            return citamedica
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

    
    def getCitasByCedula(self,cedula):
        try:
            citamedicas = Cita.query.filter(Cita.cedula == cedula, Cita.estado != CITA_CANCELADA).all()
            return citamedicas
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)


    def getProximasCitasByCedula(self,cedula):
        try:
            formatofecha = '%Y-%m-%d'
            hoy = datetime.now().date()
            hoy_str = datetime.strftime(hoy, formatofecha)
            citamedicas = Cita.query.filter(Cita.cedula == cedula, Cita.estado == CITA_PLANIFICADA, Cita.fechacita >= hoy_str).all()
            return citamedicas
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)


    def getByFechaCita(self,fechacita):
        try:
#            citamedicas = Cita.query.filter(Cita.fechacita == fechacita, Cita.estado.notin_([CITA_CANCELADA])).all()
            citamedicas = Cita.query.filter(Cita.fechacita == fechacita, Cita.estado.in_([CITA_PLANIFICADA])).all()
            return citamedicas
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

    
    def getFechasDisponibleByEspecialidad(self, codigoespecialidad, fechainicio, fechafin):
        try:
            especialidad = Especialidad.query.filter(Especialidad.codigoespecialidad == codigoespecialidad).first()
            if especialidad is None:
                raise DataNotFoundException()

            citasdia = especialidad.cantidadmaximapacientes
            diasdeatencion = []
            if especialidad.diasdeatencion:
                diasdeatencion = eval(especialidad.diasdeatencion)

            fechasconcita = self.getFechasConCitaByEspecialidad(codigoespecialidad, fechainicio, fechafin)
            formatofecha = '%Y-%m-%d'
            fechaauxdt = datetime.strptime(fechainicio, formatofecha)
            fechafindt = datetime.strptime(fechafin, formatofecha)

            fechasrango = []
            while fechaauxdt <= fechafindt:
                fechaauxstr = datetime.strftime(fechaauxdt, formatofecha)
                dict_fecha = {
                        'fecha': fechaauxstr,
                        'citasdia': citasdia,
                        'citasdisponibles': citasdia,
                    }
                diasemana = fechaauxdt.weekday()
                if diasemana in diasdeatencion:
                    if fechaauxstr in fechasconcita.keys():
                        dict_fecha['citasdisponibles'] = citasdia - fechasconcita[fechaauxstr]
                    fechasrango.append(dict_fecha)
                
                fechaauxdt = fechaauxdt + timedelta(days=1)
            
            return fechasrango

        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

    
    def getCitasByCedulaEspecialidadFecha(self, cedula, codigoespecialidad, fechacita):
        try:
            citamedicas = Cita.query.filter(Cita.cedula == cedula, Cita.codigoespecialidad == codigoespecialidad, \
                                            Cita.fechacita == fechacita, Cita.estado != CITA_CANCELADA).all()
            return citamedicas
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)
    

    def cancelCita(self,idcita):
        cita = Cita.query.filter(Cita.id == idcita).first()
        if cita is None:
            #Se arroja excepcion, el beneficiario ya esta creado
            raise DataNotFoundException()
        cita.estado = CITA_CANCELADA
        db.session.add(cita)
        db.session.commit()



class VisitaRepository(SinergiaRepository):

    def new(self,payload):
        visita = Visita()
        visita.cedula = payload['cedula']
        visita.idarea = payload['idarea']
        visita.fechavisita = datetime.now()
        visita.nombre = payload['nombre']
        visita.apellidos = payload['apellidos']
        visita.telefonocelular = payload['telefonocelular']
        visita.telefonofijo = payload['telefonofijo']
        visita.correo = payload['correo']
        visita.responsable = payload['responsable']
        
        db.session.add(visita)
        db.session.commit()   
    

    def getByFechaVista(self,fechavisita):
        try:
            visitas = Visita.query.filter(func.date(Visita.fechavisita) == fechavisita).all()
            return visitas
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)


class ConsultaMedicaRepository(SinergiaRepository):

    def new(self,payload):
        
        idcita = payload['idcita']
        cedula = payload['cedula']

        consulta_aux = ConsultaMedica.query.filter(ConsultaMedica.idcita == idcita).first()
        if consulta_aux:
            #Ya la cita tiene una consulta asociada
            raise CitaConConsultaException()

        citamedica = Cita.query.filter(Cita.id == idcita).first()
        if citamedica is None:
            #La cita no existe
            raise DataNotFoundException()
        
        if citamedica.cedula != cedula:
            #La cita es de otra persona
            raise CitaPersonaEquivocadaException()

        consultamedica = ConsultaMedica()
        consultamedica.cedula = payload['cedula']
        consultamedica.cedulamedico = payload['cedulamedico']
        consultamedica.idcita = payload['idcita']
        consultamedica.sintomas = payload['sintomas']
        consultamedica.diagnostico = payload['diagnostico']
        consultamedica.tratamiento = payload['tratamiento']
        consultamedica.examenes = payload['examenes']
        consultamedica.fecha = payload['fecha']
        
        db.session.add(consultamedica)
        db.session.commit()  


    def save(self,payload): 
        id = payload['id']
        consultamedica = ConsultaMedica.query.filter(ConsultaMedica.id == id).first()
        
        if consultamedica is None:
            raise DataNotFoundException()

        # Modificado por Ramon Valera para poder Almacenar
        # fecha = consultamedica.fecha
        # hoy = datetime.now().date()
        # if fecha != hoy:
        #   raise DataNotFoundException()

        consultamedica.fecha = datetime.now().date()

        consultamedica.sintomas = payload['sintomas']
        consultamedica.diagnostico = payload['diagnostico']
        consultamedica.tratamiento = payload['tratamiento']
        consultamedica.examenes = payload['examenes']

        consultamedica.estado = CITA_CONCLUIDA

        db.session.add(consultamedica)
        db.session.commit()   

    
    def delete(self,id):
        consultamedica = ConsultaMedica.query.filter(ConsultaMedica.id == id).first()
        if consultamedica is None:
            #Se arroja excepcion, el beneficiario ya esta creado
            raise DataNotFoundException()
        db.session.delete(consultamedica)
        db.session.commit()

    
    def getByCedula(self,cedula):
        try:
            consultasmedicas = ConsultaMedica.query.filter(ConsultaMedica.cedula == cedula, ConsultaMedica.estado == CITA_CONCLUIDA).all()
            return consultasmedicas
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)


    def getById(self,id):
        try:
            consultamedica = ConsultaMedica.query.filter(ConsultaMedica.id == id).first()
            if consultamedica is None:
                raise DataNotFoundException()
            return consultamedica
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)


class ColaEsperaRepository(SinergiaRepository):

    def entry(self,payload):         
        idbiostar = payload['idbiostar'] if 'idbiostar' in payload else None
       
        cita = Cita.query.filter(Cita.idbiostar == idbiostar).first()
        if cita is None:
            raise DataNotFoundException()

        cita.estado = CITA_EN_COLA
        cita.fechaentradacola = datetime.now()
        db.session.add(cita)
        db.session.commit()   


    def getBySala(self,idsala):
        especialidades_list = []
        hoy = datetime.now().date()
        #Buscamos las especialidades que dan consulta en la sala
        especialidades = Especialidad.query.filter(Especialidad.idsala == idsala).order_by(Especialidad.nombre.asc()).all()
        for especialidad in especialidades:
            #Buscamos las citas de esa lista de especialidades del dia de hoy discriminadas por estados
            citas_en_cola = Cita.query.filter(Cita.codigoespecialidad == especialidad.codigoespecialidad,\
                                             Cita.fechacita == hoy, Cita.estado == CITA_EN_COLA).order_by(Cita.fechaentradacola.asc()).all()

            citas_en_atencion = Cita.query.filter(Cita.codigoespecialidad == especialidad.codigoespecialidad,\
                                             Cita.fechacita == hoy, Cita.estado == CITA_EN_ATENCION).order_by(Cita.fechapasaconsulta.asc()).all()

            dict_especialidad = {
                'especialidad': especialidad,
                'citas_en_cola': citas_en_cola,
                'citas_en_atencion': citas_en_atencion
            }
            especialidades_list.append(dict_especialidad)
        return especialidades_list

    
    def getEnColaByEspecialidad(self,codigoespecialidad):
        especialidades_list = []
        hoy = datetime.now().date()
        #Buscamos las especialidades que dan consulta en la sala
        especialidad = Especialidad.query.filter(Especialidad.codigoespecialidad == codigoespecialidad).first()
        #Buscamos las citas de esa lista de especialidades del dia de hoy discriminadas por estados
        citas_en_cola = Cita.query.filter(Cita.codigoespecialidad == especialidad.codigoespecialidad,\
                                            Cita.fechacita == hoy, Cita.estado == CITA_EN_COLA).order_by(Cita.fechaentradacola.asc()).all()
        dict_especialidad = {
            'especialidad': especialidad,
            'citas_en_cola': citas_en_cola
        }
        especialidades_list.append(dict_especialidad)
        return especialidades_list

    
    def getEnAtencionByEspecialidad(self,codigoespecialidad):
        especialidades_list = []
        hoy = datetime.now().date()
        #Buscamos las especialidades que dan consulta en la sala
        especialidad = Especialidad.query.filter(Especialidad.codigoespecialidad == codigoespecialidad).first()
        #Buscamos las citas de esa lista de especialidades del dia de hoy discriminadas por estados
        citas_en_atencion = Cita.query.filter(Cita.codigoespecialidad == especialidad.codigoespecialidad,\
                                             Cita.fechacita == hoy, Cita.estado == CITA_EN_ATENCION).order_by(Cita.fechapasaconsulta.asc()).all()

        dict_especialidad = {
            'especialidad': especialidad,
            'citas_en_atencion': citas_en_atencion
        }
        especialidades_list.append(dict_especialidad)
        return especialidades_list


    def getProximaByEspecialidad(self, codigoespecialidad):
        hoy = datetime.now().date()
        proxima_cita = Cita.query.filter(Cita.codigoespecialidad == codigoespecialidad,\
                                        Cita.fechacita == hoy, Cita.estado == CITA_EN_COLA).order_by(Cita.fechaentradacola.asc()).first()
        if proxima_cita is None:
            raise DataNotFoundException()
        return proxima_cita
