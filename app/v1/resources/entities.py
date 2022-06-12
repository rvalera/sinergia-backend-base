from app.v1 import v1_api
from flask_jwt_extended.view_decorators import jwt_required
from flask_restplus import Resource, Namespace, fields
from app.v1.resources.base import ProxySecureResource, secureHeader, queryParams
from app.v1.use_cases.entities import ConfirmCitaMedicaUseCase, CreateBeneficiarioUseCase, CreateCitaMedicaUseCase, DeleteConsultaMedicaUseCase, GetCitaUseCase, GetCitasMedicasPersonaListUseCase, GetColaAtencionEspecialidadUseCase, GetConsultaMedicaUseCase, GetDiscapacidadListUseCase, GetEmpresaListUseCase, GetEspecialidadListUseCase, GetEstadoListUseCase, GetHistoriaMedicaUseCase, GetMedicoUseCase, GetMunicipioListUseCase,GetTipoNominaListUseCase, \
    GetTrabajadorUseCase, GetEstadoListUseCase, GetMunicipioListUseCase, GetPatologiaListUseCase, SaveBeneficiarioUseCase, DeleteBeneficiarioUseCase, SaveCitaMedicaUseCase, SaveTrabajadorUseCase, \
    GetCitasMedicasListUseCase, GetCitasDisponiblesListUseCase, DeleteCitaMedicaUseCase, GetPersonaUseCase, GetVisitasListUseCase, CreateVisitaUseCase, \
    CreateConsultaMedicaUseCase, SaveConsultaMedicaUseCase, GetConsultasMedicasPersonaListUseCase, GetProximasCitasMedicasPersonaListUseCase, GetCitaMedicaUseCase, \
    GetCitasCedulaEspecialidadFechaListUseCase, GetAreaListUseCase, CreateMedicoUseCase, SaveMedicoUseCase, DeleteMedicoUseCase, CreateEspecialidadUseCase,\
    SaveEspecialidadUseCase, GetEspecialidadUseCase, GetMedicoListUseCase, GetConsultorioListUseCase, EntryColaEsperaUseCase, GetSalaDeEsperaListUseCase,\
    GetProxCitaColaEsperaEspecialidadUseCase, GetColaResumenUseCase, GetColaEsperaEspecialidadUseCase

from flask.globals import request    
import json 

entities_ns = v1_api.namespace('entities', description='Business Entities Services')

EstadoStruct = v1_api.model('EstadoStruct', { 
    'codigo' : fields.String(), 
    'nombre' : fields.String(), 
})

MunicipioStruct = v1_api.model('MunicipioStruct', { 
    'codigo' : fields.String(), 
    'nombre' : fields.String(), 
})

PatologiaStruct = v1_api.model('PatologiaStruct', { 
    'codigopatologia' : fields.String(), 
    'nombre' : fields.String(), 
})

DiscapacidadStruct = v1_api.model('DiscapacidadStruct', { 
    'codigodiscapacidad' : fields.String(), 
    'nombre' : fields.String(), 
})

AreaStruct = v1_api.model('AreaStruct', { 
    'id' : fields.Integer(), 
    'nombre' : fields.String(), 
})

PersonaStruct = v1_api.model('PersonaStruct', { 
    'cedula' : fields.String(), 
    'nombres' : fields.String(),  
    'apellidos' : fields.String(),  
    'sexo' : fields.String(),  
    'fechanacimiento' : fields.String(format='date-time'),   
    'telefonocelular' : fields.String(),  
    'telefonoresidencia' : fields.String(),  
    'correo' : fields.String(),

    'nacionalidad' : fields.String(), 
    'sexo' : fields.String(),  
    'nivel' : fields.String(),  
    'profesion' : fields.String(),  

    'estado': fields.Nested(EstadoStruct,attribute='estado'),
    'municipio': fields.Nested(MunicipioStruct,attribute='municipio'),

    'parroquia' : fields.String(), 
    'sector' : fields.String(),  
    'avenidacalle' : fields.String(),  
    'edifcasa' : fields.String()
}) 

GetPersonaStruct = v1_api.model('GetPersonaResult', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'data' : fields.Nested(PersonaStruct,attribute='data')
})

UpdatePersonaStruct = v1_api.model('UpdatePersonaStruct', { 
    'cedula' : fields.String(), 
})

TipoCargoStruct = v1_api.model('TipoCargoStruct', { 
    'codigo' : fields.String(), 
    'nombre' : fields.String(), 
})


TipoNominaStruct = v1_api.model('TipoNominaStruct', { 
    'codigo' : fields.String(), 
    'nombre' : fields.String(), 
})

EstatusTrabajadorStruct = v1_api.model('EstatusTrabajadorStruct', { 
    'codigo' : fields.String(), 
    'nombre' : fields.String(), 
})

UbicacionLaboralStruct = v1_api.model('UbicacionLaboralStruct', { 
    'codigo' : fields.String(), 
    'nombre' : fields.String(), 
})

TipoTrabajadorStruct = v1_api.model('TipoTrabajadorStruct', { 
    'codigo' : fields.String(), 
    'nombre' : fields.String(), 
})

EmpresaStruct = v1_api.model('EmpresaStruct', { 
    'codigo' : fields.String(), 
    'nombre' : fields.String(), 
})

UpdateEmpresaStruct = v1_api.model('UpdateEmpresaStruct', { 
    'codigo' : fields.String(), 
})

UsuarioActStruct = v1_api.model('UsuarioActStruct', { 
    'name': fields.String()
})

SalaDeEsperaStruct = v1_api.model('SalaDeEsperaStruct', { 
    'idsala' : fields.Integer(), 
    'nombre' : fields.String()
})

GetSalaDeEsperaListStruct = v1_api.model('GetSalaDeEsperaListResult', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'count' : fields.Integer(description='Count Row'), 
    'total' : fields.Integer(description='Total Row'), 
    'data' : fields.Nested(SalaDeEsperaStruct,attribute='data')
})

HistoriaMedicaStruct = v1_api.model('HistoriaMedicaStruct', { 
    'cedula' : fields.String(), 
    'persona': fields.Nested(PersonaStruct,attribute='persona'),
    'gruposanguineo' : fields.String(), 
    'fecha' : fields.String(format='date-time'),
    'patologias': fields.List(fields.Nested(PatologiaStruct)),
    'discapacidades': fields.List(fields.Nested(DiscapacidadStruct))
})

BeneficiarioStruct = v1_api.model('BeneficiarioStruct', { 
    'cedula' : fields.String(),
    'vinculo' : fields.String(),
    'nombres' : fields.String(),  
    'apellidos' : fields.String(),  
    'sexo' : fields.String(),  
    'fechanacimiento' : fields.String(format='date-time'),
    'historiamedica': fields.Nested(HistoriaMedicaStruct,attribute='historiamedica')
})

UpdateBeneficiarioStruct = v1_api.model('UpdateBeneficiarioStruct', { 
    'cedula': fields.String(),
    'nombres': fields.String(),
    'apellidos': fields.String(),
    'sexo': fields.String(),
    'fechanacimiento': fields.String(),
    'cedulatrabajador': fields.String(),
    'vinculo': fields.String(),
    'gruposanguineo': fields.String(),
    'patologias' : fields.List(fields.String()), #Listado de Ids de Patologias
    'discapacidades' : fields.List(fields.String()), #Listado de Ids de Discapacidades
}) 

TrabajadorStruct = v1_api.model('TrabajadorStruct', { 
    'cedula' : fields.String(), 
    'nombres' : fields.String(),  
    'apellidos' : fields.String(),  
    'sexo' : fields.String(),  
    'fechanacimiento' : fields.String(format='date-time'),   
    'telefonocelular' : fields.String(),  
    'telefonoresidencia' : fields.String(),  
    'correo' : fields.String(),

    'nacionalidad' : fields.String(), 
    'sexo' : fields.String(),  
    'suspendido' : fields.String(),  
    'razonsuspension' : fields.String(),  
    'nivel' : fields.String(),  
    'profesion' : fields.String(),  
    'personal': fields.String(),  
    'tiponomina': fields.String(),  
    'ubicacionlaboral': fields.String(),  
    'cargo': fields.String(),  

    'estado': fields.Nested(EstadoStruct,attribute='estado'),
    'municipio': fields.Nested(MunicipioStruct,attribute='municipio'),

    'parroquia' : fields.String(), 
    'sector' : fields.String(),  
    'avenidacalle' : fields.String(),  
    'edifcasa' : fields.String(),  

    'ingreso' : fields.String(format='date-time'),   
    'jornada' : fields.String(),  

    'situacion' : fields.String(), 
    'condicion' : fields.String(),  
    'camisa' : fields.String(),  
    'pantalon' : fields.String(),  
    'calzado' : fields.String(),  
    'observaciones' : fields.String(),  

    'ficha' : fields.String(),
    'historiamedica': fields.Nested(HistoriaMedicaStruct,attribute='historiamedica'),  
    'empresa': fields.Nested(EmpresaStruct,attribute='empresa'),  
    'fechaactualizacion' : fields.DateTime(), 
    'usuarioactualizacion': fields.Nested(UsuarioActStruct,attribute='usuarioactualizacion'),

    'beneficiarios': fields.List(fields.Nested(BeneficiarioStruct))

}) 

UpdateTrabajadorStruct = v1_api.model('UpdateTrabajadorStruct', { 
    'cedula' : fields.String(),   
    'telefonocelular' : fields.String(),  
    'telefonoresidencia' : fields.String(),  
    'correo' : fields.String(),
    'codigoestado': fields.String(), 
    'codigomunicipio': fields.String(), 
    'parroquia' : fields.String(), 
    'sector' : fields.String(),  
    'avenidacalle' : fields.String(),  
    'edifcasa' : fields.String(),  
    'camisa' : fields.String(),  
    'pantalon' : fields.String(),  
    'calzado' : fields.String(),  
    'gruposanguineo': fields.String(),
    'observaciones': fields.String(),
    'patologias' : fields.List(fields.String()), #Listado de Ids de Patologias
    'discapacidades' : fields.List(fields.String()), #Listado de Ids de Discapacidades

}) 

GetTrabajadorListStruct = v1_api.model('GetTrabajadorListResult', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'count' : fields.Integer(description='Count Row'), 
    'total' : fields.Integer(description='Total Row'), 
    'data' : fields.Nested(TrabajadorStruct,attribute='data')
}) 

GetTrabajadorStruct = v1_api.model('GetTrabajadorResult', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'data' : fields.Nested(TrabajadorStruct,attribute='data')
})

GetHistoriaMedicaStruct = v1_api.model('GetHistoriaMedicaResult', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'data' : fields.Nested(HistoriaMedicaStruct,attribute='data')
})

EspecialidadStruct = v1_api.model('EspecialidadStruct', { 
    'codigoespecialidad' : fields.String(), 
    'nombre' : fields.String(), 
    'diasdeatencion' : fields.String(), 
    'autogestionada' : fields.Boolean(), 
    'cantidadmaximapacientes' : fields.Integer(),
    'saladeespera': fields.Nested(SalaDeEsperaStruct,attribute='saladeespera'),
})

UpdateEspecialidadStruct = v1_api.model('UpdateEspecialidadStruct', { 
    'codigoespecialidad' : fields.String(), 
    'nombre' : fields.String(), 
    'diasdeatencion' : fields.String(), 
    'autogestionada' : fields.Boolean(), 
    'cantidadmaximapacientes' : fields.Integer(),
    'idsala' : fields.Integer()
})

GetEspecialidadStruct = v1_api.model('GetEspecialidadResult', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'data' : fields.Nested(EspecialidadStruct,attribute='data')
})

CitaStruct = v1_api.model('CitaStruct', { 
    'id' : fields.String(), 
    'persona': fields.Nested(PersonaStruct,attribute='persona'),
    'especialidad': fields.Nested(EspecialidadStruct,attribute='especialidad'),
    'fechadia' : fields.DateTime(), 
    'fechacita' : fields.DateTime(), 
    'fechaentradacola' : fields.DateTime(), 
    'fechapasaconsulta' : fields.DateTime(), 
    'fechafinconsulta' : fields.DateTime(), 
    'idbiostar' : fields.String(),
    'idbiostar2' : fields.String(),
    'estado' : fields.String()
}) 

CreateCitaStruct = v1_api.model('CreateCitaStruct', { 
    'cedula' : fields.String(),   
    'codigoespecialidad' : fields.String(),  
    'fechacita' : fields.String()
})

UpdateCitaStruct = v1_api.model('UpdateCitaStruct', { 
    'idcita' : fields.String(),   
    'codigoespecialidad' : fields.String(),  
    'fechacita' : fields.String()
})

ConfirmCitaStruct = v1_api.model('ConfirmCitaStruct', { 
    'idcita' : fields.String(),   
    'idbiostar' : fields.String(),
    'idbiostar2' : fields.String()
})

EntryColaStruct = v1_api.model('EntryColaStruct', { 
    'idbiostar' : fields.String()
})

GetCitaStruct = v1_api.model('GetCitaStruct', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'data' : fields.Nested(CitaStruct,attribute='data')
})

GetCitaListStruct = v1_api.model('GetCitaListResult', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'count' : fields.Integer(description='Count Row'), 
    'total' : fields.Integer(description='Total Row'), 
    'data' : fields.Nested(CitaStruct,attribute='data')
}) 
    
VisitaStruct = v1_api.model('VisitaStruct', { 
    'id' : fields.Integer(), 
    'area': fields.Nested(AreaStruct,attribute='area'),
    'cedula' : fields.String(),
    'nombre' : fields.String(),
    'apellidos' : fields.String(),
    'telefonocelular' : fields.String(),
    'telefonofijo' : fields.String(),
    'correo' : fields.String(),
    'responsable' : fields.String(),
    'fechavisita' : fields.DateTime()
})

CreateVisitaStruct = v1_api.model('CreateVisitaStruct', { 
    'idarea' : fields.Integer(), 
    'cedula' : fields.String(),
    'nombre' : fields.String(),
    'apellidos' : fields.String(),
    'telefonocelular' : fields.String(),
    'telefonofijo' : fields.String(),
    'correo' : fields.String(),
    'responsable' : fields.String()
})

GetVisitaListStruct = v1_api.model('GetVisitaListResult', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'count' : fields.Integer(description='Count Row'), 
    'total' : fields.Integer(description='Total Row'), 
    'data' : fields.Nested(VisitaStruct,attribute='data')
})


ConsultorioStruct = v1_api.model('ConsultorioStruct', {     
    'idconsultorio' : fields.Integer(), 
    'saladeespera': fields.Nested(SalaDeEsperaStruct,attribute='saladeespera'),
    'nombre' : fields.String()
})


ColaResumenStruct = v1_api.model('ColaResumenStruct', {     
    'especialidad': fields.Nested(EspecialidadStruct,attribute='especialidad'),
    'citas_en_cola': fields.List(fields.Nested(CitaStruct)),
    'citas_en_atencion': fields.List(fields.Nested(CitaStruct))
})


GetColaResumenStruct = v1_api.model('GetColaResumenResult', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'data' : fields.List(fields.Nested(ColaResumenStruct))
})


MedicoStruct = v1_api.model('MedicoStruct', { 
    'cedula' : fields.String(), 
    'nombres' : fields.String(),  
    'apellidos' : fields.String(),  
    'sexo' : fields.String(),  
    'fechanacimiento' : fields.String(format='date-time'),   
    'telefonocelular' : fields.String(),  
    'telefonoresidencia' : fields.String(),  
    'correo' : fields.String(),

    'nacionalidad' : fields.String(), 
    'sexo' : fields.String(),  

    'estado': fields.Nested(EstadoStruct,attribute='estado'),
    'municipio': fields.Nested(MunicipioStruct,attribute='municipio'),

    'parroquia' : fields.String(), 
    'sector' : fields.String(),  
    'avenidacalle' : fields.String(),  
    'edifcasa' : fields.String(),

    'especialidad': fields.Nested(EspecialidadStruct,attribute='especialidad'),
    'consultorio': fields.Nested(ConsultorioStruct,attribute='consultorio'),
})

UpdateMedicoStruct = v1_api.model('UpdateMedicoStruct', { 
    'cedula' : fields.String(), 
    'nombres' : fields.String(),  
    'apellidos' : fields.String(),  
    'sexo' : fields.String(),  
    'fechanacimiento' : fields.String(format='date-time'),   
    'telefonocelular' : fields.String(),  
    'telefonoresidencia' : fields.String(),  
    'correo' : fields.String(),
    'nacionalidad' : fields.String(), 
    'sexo' : fields.String(),  
    'codigoestado': fields.String(), 
    'codigomunicipio': fields.String(), 
    'parroquia' : fields.String(), 
    'sector' : fields.String(),  
    'avenidacalle' : fields.String(),  
    'edifcasa' : fields.String(),
    'codigoespecialidad' : fields.String()
})

GetMedicoStruct = v1_api.model('GetMedicoResult', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'data' : fields.Nested(MedicoStruct,attribute='data')
})

GetMedicoListStruct = v1_api.model('GetMedicoListResult', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'count' : fields.Integer(description='Count Row'), 
    'total' : fields.Integer(description='Total Row'), 
    'data' : fields.Nested(MedicoStruct,attribute='data')
})

ConsultaMedicaStruct = v1_api.model('ConsultaMedicaStruct', { 
    'id' : fields.Integer(),
    'historiamedica' : fields.Nested(HistoriaMedicaStruct,attribute='historiamedica'),
    'medico' : fields.Nested(MedicoStruct,attribute='medico'),
    'cita' : fields.Nested(CitaStruct,attribute='cita'),
    'sintomas' : fields.String(),
    'diagnostico' : fields.String(),
    'tratamiento' : fields.String(),
    'examenes' : fields.String(),
    'fecha' : fields.Date()
})

CreateConsultaMedicaStruct = v1_api.model('CreateConsultaMedicaStruct', { 
    'cedula' : fields.String(),
    'cedulamedico' : fields.String(),
    'idcita' : fields.Integer(),
    'sintomas' : fields.String(),
    'diagnostico' : fields.String(),
    'tratamiento' : fields.String(),
    'examenes' : fields.String(),
    'fecha' : fields.String()
})

UpdateConsultaMedicaStruct = v1_api.model('UpdateConsultaMedicaStruct', { 
    #TODO Que se actualiza?
    'id' : fields.Integer(),
    'sintomas' : fields.String(),
    'diagnostico' : fields.String(),
    'tratamiento' : fields.String(),
    'examenes' : fields.String()
})


GetConsultaMedicaListStruct = v1_api.model('GetConsultaMedicaListStruct', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'count' : fields.Integer(description='Count Row'), 
    'total' : fields.Integer(description='Total Row'), 
    'data' : fields.Nested(ConsultaMedicaStruct,attribute='data')
})


GetConsultaMedicaStruct = v1_api.model('GetConsultaMedicaStruct', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'data' : fields.Nested(ConsultaMedicaStruct,attribute='data')
})


@entities_ns.route('/empresa')
@v1_api.expect(secureHeader)
class EmpresaResource(ProxySecureResource): 

    @entities_ns.doc('Empresa')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()        
        data = GetEmpresaListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200


@entities_ns.route('/tiponomina')
@v1_api.expect(secureHeader)
class TipoNominaResource(ProxySecureResource): 

    @entities_ns.doc('Tipo Nomina')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        data = GetTipoNominaListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200


@entities_ns.route('/area')
@v1_api.expect(secureHeader)
class AreaResource(ProxySecureResource): 

    @entities_ns.doc('Area')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        data = GetAreaListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200


@entities_ns.route('/consultorio')
@v1_api.expect(secureHeader)
class ConsultorioResource(ProxySecureResource): 

    @entities_ns.doc('Consultorio')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        data = GetConsultorioListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200


@entities_ns.route('/colaespera/entrada')
@v1_api.expect(secureHeader)
class ColaEntradaResource(ProxySecureResource): 

    @entities_ns.doc('Entrada a Cola de Espera')
    @v1_api.expect(EntryColaStruct)    
    @jwt_required    
    def put(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        payload = request.json        
        EntryColaEsperaUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200


@entities_ns.route('/colaespera/resumen/<idsala>')
@entities_ns.param('idsala', 'Id Sala de Espera')
@v1_api.expect(secureHeader)
class ColaEsperaResource(ProxySecureResource):

    @entities_ns.doc('Get Cola de Espera por Sala y Dia de Consulta')
    @v1_api.marshal_with(GetColaResumenStruct) 
    @jwt_required    
    def get(self,idsala):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {
            'idsala': idsala
            }
        data = GetColaResumenUseCase().execute(security_credentials,query_params)
        return  {'ok': 1, 'data': data}, 200


@entities_ns.route('/colaespera/enatencion/<codigoespecialidad>')
@entities_ns.param('codigoespecialidad', 'Codigo de la Especialidad')
@v1_api.expect(secureHeader)
class ColaEsperaResource(ProxySecureResource):

    @entities_ns.doc('Get Cola en Atencion por Especialidad')
    @v1_api.marshal_with(GetColaResumenStruct) 
    @jwt_required    
    def get(self,codigoespecialidad):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {
            'codigoespecialidad': codigoespecialidad
            }
        data = GetColaAtencionEspecialidadUseCase().execute(security_credentials,query_params)
        return  {'ok': 1, 'data': data}, 200


@entities_ns.route('/colaespera/enespera/<codigoespecialidad>')
@entities_ns.param('codigoespecialidad', 'Codigo de la Especialidad')
@v1_api.expect(secureHeader)
class ColaEsperaResource(ProxySecureResource):

    @entities_ns.doc('Get Cola en Espera por Especialidad')
    @v1_api.marshal_with(GetColaResumenStruct) 
    @jwt_required    
    def get(self,codigoespecialidad):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {
            'codigoespecialidad': codigoespecialidad
            }
        data = GetColaEsperaEspecialidadUseCase().execute(security_credentials,query_params)
        return  {'ok': 1, 'data': data}, 200


@entities_ns.route('/colaespera/proximacita/<codigoespecialidad>')
@entities_ns.param('codigoespecialidad', 'Codigo de la Especialidad')
@v1_api.expect(secureHeader)
class ColaProximaCitaResource(ProxySecureResource):

    @entities_ns.doc('Get Proxima Cita en Cola de Espera por Especialidad')
    @v1_api.marshal_with(GetCitaStruct) 
    @jwt_required    
    def get(self,codigoespecialidad):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {
            'codigoespecialidad': codigoespecialidad
            }
        data = GetProxCitaColaEsperaEspecialidadUseCase().execute(security_credentials,query_params)
        return  {'ok': 1, 'data': data}, 200


@entities_ns.route('/persona/<cedula>')
@entities_ns.param('cedula', 'Cedula Persona')
@v1_api.expect(secureHeader)
class OnePersonaResource(ProxySecureResource):

    @entities_ns.doc('Get Persona')
    @v1_api.marshal_with(GetPersonaStruct) 
    @jwt_required    
    def get(self,cedula):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {'cedula': cedula}
        data = GetPersonaUseCase().execute(security_credentials,query_params)
        return  {'ok': 1, 'data': data}, 200


@entities_ns.route('/trabajador/<cedula>')
@entities_ns.param('cedula', 'Cedula Trabajador')
@v1_api.expect(secureHeader)
class OneTrabajadorResource(ProxySecureResource):

    @entities_ns.doc('Get Trabajador')
    @v1_api.marshal_with(GetTrabajadorStruct) 
    @jwt_required    
    def get(self,cedula):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {'cedula': cedula}
        data = GetTrabajadorUseCase().execute(security_credentials,query_params)
        return  {'ok': 1, 'data': data}, 200


@entities_ns.route('/trabajador')
@v1_api.expect(secureHeader)
class TrabajadorResource(ProxySecureResource): 
    
    @entities_ns.doc('Update Trabajador')
    @v1_api.expect(UpdateTrabajadorStruct)    
    @jwt_required    
    def put(self):
        #security_credentials = self.checkCredentials()
        security_credentials = {'username': 'prueba'}
        payload = request.json        
        SaveTrabajadorUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200


@entities_ns.route('/estado')
@v1_api.expect(secureHeader)
class EstadoResource(ProxySecureResource): 

    @entities_ns.doc('Estado')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        data = GetEstadoListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200


@entities_ns.route('/municipio')
@v1_api.expect(secureHeader)
class MunicipioResource(ProxySecureResource): 

    @entities_ns.doc('Municipio')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        data = GetMunicipioListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200


@entities_ns.route('/patologia')
@v1_api.expect(secureHeader)
class PatologiaResource(ProxySecureResource): 

    @entities_ns.doc('Patologia')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        data = GetPatologiaListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200


@entities_ns.route('/discapacidad')
@v1_api.expect(secureHeader)
class DiscapacidadResource(ProxySecureResource): 

    @entities_ns.doc('Discapacidad')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        data = GetDiscapacidadListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200


@entities_ns.route('/saladeespera')
@v1_api.expect(secureHeader)
class SalaDeEsperaResource(ProxySecureResource): 

    @entities_ns.doc('Sala De Espera')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        data = GetSalaDeEsperaListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200


@entities_ns.route('/especialidad')
@v1_api.expect(secureHeader)
class EspecialidadResource(ProxySecureResource): 

    @entities_ns.doc('Especialidad')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        data = GetEspecialidadListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200
    
    @entities_ns.doc('Create Especialidad')
    @v1_api.expect(UpdateEspecialidadStruct)    
    @jwt_required    
    def post(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        payload = request.json        
        CreateEspecialidadUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200

    @entities_ns.doc('Update Especialidad')
    @v1_api.expect(UpdateEspecialidadStruct)    
    @jwt_required    
    def put(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        payload = request.json        
        SaveEspecialidadUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200


@entities_ns.route('/especialidad/<codigoespecialidad>')
@entities_ns.param('codigoespecialidad', 'Codigo de la Especialidad')
@v1_api.expect(secureHeader)
class OneEspecialidadResource(ProxySecureResource):

    @entities_ns.doc('Get Especialidad')
    @v1_api.marshal_with(GetEspecialidadStruct) 
    @jwt_required    
    def get(self,codigoespecialidad):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {'codigoespecialidad': codigoespecialidad}
        data = GetEspecialidadUseCase.execute(security_credentials,query_params)
        return  {'ok': 1, 'data': data}, 200


@entities_ns.route('/beneficiario')
@v1_api.expect(secureHeader)
class BeneficiarioResource(ProxySecureResource): 

    @entities_ns.doc('Create Beneficiario')
    @v1_api.expect(UpdateBeneficiarioStruct)    
    @jwt_required    
    def post(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        payload = request.json        
        CreateBeneficiarioUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200

    @entities_ns.doc('Update Beneficiario')
    @v1_api.expect(UpdateBeneficiarioStruct)    
    @jwt_required    
    def put(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        payload = request.json        
        SaveBeneficiarioUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200
    

@entities_ns.route('/beneficiario/<cedula>')
@entities_ns.param('cedula', 'Cedula Trabajador')
@v1_api.expect(secureHeader)
class DeleteBeneficiarioResource(ProxySecureResource): 
    @entities_ns.doc('Delete Beneficiario')
    @jwt_required
    def delete(self,cedula):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {'cedula': cedula}
        DeleteBeneficiarioUseCase().execute(security_credentials,query_params)
        return  {'ok':1} , 200


@entities_ns.route('/medico')
@v1_api.expect(secureHeader)
class MedicoResource(ProxySecureResource): 

    @entities_ns.doc('Medicos List')
    @v1_api.marshal_with(GetMedicoListStruct) 
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        data = GetMedicoListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200

    @entities_ns.doc('Create Medico')
    @v1_api.expect(UpdateMedicoStruct)    
    @jwt_required    
    def post(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        payload = request.json        
        CreateMedicoUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200

    @entities_ns.doc('Update Medico')
    @v1_api.expect(UpdateMedicoStruct)    
    @jwt_required    
    def put(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        payload = request.json        
        SaveMedicoUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200


@entities_ns.route('/medico/<cedulamed>')
@entities_ns.param('cedulamed', 'Cedula del Medico')
@v1_api.expect(secureHeader)
class OneMedicoResource(ProxySecureResource):

    @entities_ns.doc('Get Medico')
    @v1_api.marshal_with(GetMedicoStruct) 
    @jwt_required    
    def get(self,cedulamed):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {'cedula': cedulamed}
        data = GetMedicoUseCase().execute(security_credentials,query_params)
        return  {'ok': 1, 'data': data}, 200


@entities_ns.route('/medico/<cedula>')
@entities_ns.param('cedula', 'Cedula del Medico')
@v1_api.expect(secureHeader)
class DeleteMedicoResource(ProxySecureResource): 
    @entities_ns.doc('Delete Medico')
    @jwt_required
    def delete(self,cedula):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {'cedula': cedula}
        DeleteMedicoUseCase().execute(security_credentials,query_params)
        return  {'ok':1} , 200

@entities_ns.route('/historiamedica/<cedula>')
@entities_ns.param('cedula', 'Cedula Persona')
@v1_api.expect(secureHeader)
class OneHistoriaMedicaResource(ProxySecureResource):

    @entities_ns.doc('Get Historia Medica')
    @v1_api.marshal_with(GetHistoriaMedicaStruct) 
    @jwt_required    
    def get(self,cedula):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {'cedula': cedula}
        data = GetHistoriaMedicaUseCase().execute(security_credentials,query_params)
        return  {'ok': 1, 'data': data}, 200


@entities_ns.route('/citamedica')
@v1_api.expect(secureHeader)
class CitaResource(ProxySecureResource): 

    @entities_ns.doc('Create Cita Medica')
    @v1_api.expect(CreateCitaStruct)    
    @jwt_required    
    def post(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        payload = request.json        
        CreateCitaMedicaUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200

    @entities_ns.doc('Update Cita Medica')
    @v1_api.expect(UpdateCitaStruct)    
    @jwt_required    
    def put(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        payload = request.json        
        SaveCitaMedicaUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200


@entities_ns.route('/citamedica/confirmar')
@v1_api.expect(secureHeader)
class CitaConfirmResource(ProxySecureResource): 

    @entities_ns.doc('Confirm Cita Medica')
    @v1_api.expect(ConfirmCitaStruct)    
    @jwt_required    
    def put(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        payload = request.json        
        ConfirmCitaMedicaUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200


@entities_ns.route('/citamedica/<id>')
@entities_ns.param('id', 'Id de la Cita Medica')
@v1_api.expect(secureHeader)
class OneCitaMedicaResource(ProxySecureResource):

    @entities_ns.doc('Get Cita Medica')
    @v1_api.marshal_with(GetCitaStruct) 
    @jwt_required    
    def get(self,id):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {'id': id}
        data = GetCitaMedicaUseCase().execute(security_credentials,query_params)
        return  {'ok': 1, 'data': data}, 200


@entities_ns.route('/citamedica/<idcita>')
@entities_ns.param('idcita', 'Id de la Cita Medica')
@v1_api.expect(secureHeader)
class DeleteCitaResource(ProxySecureResource): 
    @entities_ns.doc('Delete Cita Medica')
    @jwt_required
    def delete(self,idcita):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {'idcita': idcita}
        DeleteCitaMedicaUseCase().execute(security_credentials,query_params)
        return  {'ok':1} , 200


@entities_ns.route('/citamedica/cedula/<cedula>')
@entities_ns.param('cedula', 'Cedula Persona')
@v1_api.expect(secureHeader)
class CitaPersonaListResource(ProxySecureResource):

    @entities_ns.doc('Get Citas Medicas by Cedula')
    @v1_api.marshal_with(GetCitaListStruct) 
    @jwt_required    
    def get(self,cedula):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {'cedula': cedula}
        data = GetCitasMedicasPersonaListUseCase().execute(security_credentials, query_params)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200


@entities_ns.route('/citamedica/proxima/cedula/<cedula>')
@entities_ns.param('cedula', 'Cedula Persona')
@v1_api.expect(secureHeader)
class ProximasCitasPersonaListResource(ProxySecureResource):

    @entities_ns.doc('Get Proximas Citas Medicas by Cedula')
    @v1_api.marshal_with(GetCitaListStruct) 
    @jwt_required    
    def get(self,cedula):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {'cedula': cedula}
        data = GetProximasCitasMedicasPersonaListUseCase().execute(security_credentials, query_params)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200


@entities_ns.route('/citamedica/fecha/<fecha>')
@entities_ns.param('fecha', 'Fecha de las Citas Medicas')
@v1_api.expect(secureHeader)
class CitaFechaListResource(ProxySecureResource):

    @entities_ns.doc('Get Citas Medicas by Date')
    @v1_api.marshal_with(GetCitaListStruct) 
    @jwt_required    
    def get(self,fecha):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {'fechacita': fecha}
        data = GetCitasMedicasListUseCase().execute(security_credentials,query_params)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200


@entities_ns.route('/citamedica/disponible/<codigoespecialidad>/<fechainicio>/<fechafin>')
@entities_ns.param('codigoespecialidad', 'Codigo de la Especialidad')
@entities_ns.param('fechainicio', 'Fecha Inicio')
@entities_ns.param('fechafin', 'Fecha Fin')
@v1_api.expect(secureHeader)
class CitaFechaDisponiblesListResource(ProxySecureResource):

    @entities_ns.doc('Get Citas Medicas Disponibles by Especialidad y Rango de Fecha')
    @jwt_required    
    def get(self,codigoespecialidad, fechainicio, fechafin):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {
            'codigoespecialidad': codigoespecialidad,
            'fechainicio': fechainicio,
            'fechafin': fechafin
        }
        data = GetCitasDisponiblesListUseCase().execute(security_credentials,query_params)
        return  {'ok':1, 'data': data} , 200


@entities_ns.route('/citamedica/<cedula>/<codigoespecialidad>/<fechacita>')
@entities_ns.param('cedula', 'Cedula')
@entities_ns.param('codigoespecialidad', 'Codigo de la Especialidad')
@entities_ns.param('fechacita', 'Fecha Cita')
@v1_api.expect(secureHeader)
class CitaCedulaEspecialidadFechaListResource(ProxySecureResource):

    @entities_ns.doc('Get Citas Medicas by Cedula, Especialidad y Fecha')
    @jwt_required    
    def get(self,cedula, codigoespecialidad, fechacita):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {
            'cedula': cedula,
            'codigoespecialidad': codigoespecialidad,
            'fechacita': fechacita
        }
        data = GetCitasCedulaEspecialidadFechaListUseCase().execute(security_credentials,query_params)
        return  {'ok':1, 'data': data} , 200


@entities_ns.route('/visita')
@v1_api.expect(secureHeader)
class VisitaResource(ProxySecureResource): 

    @entities_ns.doc('Create Visita')
    @v1_api.expect(CreateVisitaStruct)    
    @jwt_required    
    def post(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        payload = request.json        
        CreateVisitaUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200

        
@entities_ns.route('/visita/fecha/<fecha>')
@entities_ns.param('fecha', 'Fecha de las Visitas')
@v1_api.expect(secureHeader)
class VisitaFechaListResource(ProxySecureResource):

    @entities_ns.doc('Get Visitas by Date')
    @v1_api.marshal_with(GetVisitaListStruct) 
    @jwt_required    
    def get(self,fecha):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {'fechavisita': fecha}
        data = GetVisitasListUseCase().execute(security_credentials,query_params)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200


@entities_ns.route('/consultamedica')
@v1_api.expect(secureHeader)
class ConsultaMedicaResource(ProxySecureResource): 

    @entities_ns.doc('Create Consulta Medica')
    @v1_api.expect(CreateConsultaMedicaStruct)    
    @jwt_required    
    def post(self):
        security_credentials = self.checkCredentials()
        security_credentials = {'username': 'prueba'}
        payload = request.json        
        CreateConsultaMedicaUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200

    @entities_ns.doc('Update Consulta Medica')
    @v1_api.expect(UpdateConsultaMedicaStruct)    
    @jwt_required    
    def put(self):
        security_credentials = self.checkCredentials()
        security_credentials = {'username': 'prueba'}
        payload = request.json        
        SaveConsultaMedicaUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200


@entities_ns.route('/consultamedica/cedula/<cedula>')
@entities_ns.param('cedula', 'Cedula del Paciente')
@v1_api.expect(secureHeader)
class ConsultaMedicaCedulaListResource(ProxySecureResource):

    @entities_ns.doc('Get Consultas Medicas by Cedula')
    @v1_api.marshal_with(GetConsultaMedicaListStruct) 
    @jwt_required    
    def get(self,cedula):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {'cedula': cedula}
        data = GetConsultasMedicasPersonaListUseCase().execute(security_credentials,query_params)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200


@entities_ns.route('/consultamedica/<id>')
@entities_ns.param('id', 'Id de la Consulta Medica')
@v1_api.expect(secureHeader)
class OneConsultaMedicaResource(ProxySecureResource):

    @entities_ns.doc('Get Consulta Medica')
    @v1_api.marshal_with(GetConsultaMedicaStruct) 
    @jwt_required    
    def get(self,id):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {'id': id}
        data = GetConsultaMedicaUseCase().execute(security_credentials,query_params)
        return  {'ok': 1, 'data': data}, 200


@entities_ns.route('/consultamedica/<id>')
@entities_ns.param('id', 'Id de la Consulta Medica')
@v1_api.expect(secureHeader)
class DeleteConsultaResource(ProxySecureResource): 
    @entities_ns.doc('Delete Consulta Medica')
    @jwt_required
    def delete(self,id):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {'id': id}
        DeleteConsultaMedicaUseCase().execute(security_credentials,query_params)
        return  {'ok':1} , 200