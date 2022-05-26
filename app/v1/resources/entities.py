from app.v1 import v1_api
from flask_jwt_extended.view_decorators import jwt_required
from flask_restplus import Resource, Namespace, fields
from app.v1.resources.base import ProxySecureResource, secureHeader, queryParams
from app.v1.use_cases.entities import CreateBeneficiarioUseCase, CreateCitaMedicaUseCase, GetCitaUseCase, GetConsultaMedicaUseCase, GetDiscapacidadListUseCase, GetEmpresaListUseCase, GetEspecialidadListUseCase, GetEstadoListUseCase, GetHistoriaMedicaUseCase, GetMunicipioListUseCase,GetTipoNominaListUseCase, \
    GetTrabajadorUseCase, GetEstadoListUseCase, GetMunicipioListUseCase, GetPatologiaListUseCase, SaveBeneficiarioUseCase, DeleteBeneficiarioUseCase, SaveCitaMedicaUseCase, SaveTrabajadorUseCase, \
    GetCitasMedicasListUseCase, GetCitasDisponiblesListUseCase, DeleteCitaMedicaUseCase, GetPersonaUseCase, GetVisitasListUseCase, CreateVisitaUseCase, \
    CreateConsultaMedicaUseCase, SaveConsultaMedicaUseCase, GetConsultasMedicasPersonaListUseCase
# from app.v1.use_cases.entities import GetCargoListUseCase,GetCentroCostoListUseCase,GetConceptoNominaListUseCase,\
#     GetDispositivoListUseCase,GetEstatusTrabajadorListUseCase,GetTipoAusenciaListUseCase,GetTipoNominaListUseCase,\
#     GetTrabajadorListUseCase,GetTipoTrabajadorListUseCase,GetGrupoGuardiaListUseCase
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

UsuarioActStruct = v1_api.model('UsuarioActStruct', { 
    'name': fields.String()
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
    'cantidadmaximapacientes' : fields.Integer()
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

GetCitaStruct = v1_api.model('GetCitaResult', { 
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


SalaDeEsperaStruct = v1_api.model('SalaDeEsperaStruct', { 
    'idsala' : fields.Integer(), 
    'nombre' : fields.String()
})


ConsultorioStruct = v1_api.model('ConsultorioStruct', { 
    'idconsultorio' : fields.Integer(), 
    'saladeespera': fields.Nested(SalaDeEsperaStruct,attribute='saladeespera'),
    'nombre' : fields.String()
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

    'especialidad': fields.Nested(EspecialidadStruct,attribute='especialidad'),
    'consultorio': fields.Nested(ConsultorioStruct,attribute='consultorio')

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

# @entities_ns.route('/cargo')
# @v1_api.expect(secureHeader)
# class CargoResource(ProxySecureResource): 
#     @entities_ns.doc('Cargo')
#     @v1_api.expect(queryParams)    
#     @jwt_required        
#     def get(self):
#         security_credentials = self.checkCredentials()

#         query_params = {}
#         request_payload =  {}        
#         if 'filter' in  request.args and request.args['filter']:
#             filter = eval(request.args['filter'])
#             request_payload = filter
#             query_params['filter'] = request_payload

#         if 'order' in  request.args and request.args['order']:
#             order = eval(request.args['order'])
#             query_params['order'] = order
        
#         if 'range' in  request.args and request.args['range']:
#             range = eval(request.args['range'])
#             query_params['range'] = range

#         data = GetCargoListUseCase().execute(security_credentials,query_params)
#         data['ok']= 1
#         return  data , 200

# @entities_ns.route('/centro_costo')
# @v1_api.expect(secureHeader)
# class CentroCostoResource(ProxySecureResource): 
#     @entities_ns.doc('Centro de Costo')
#     @v1_api.expect(queryParams)    
#     @jwt_required    
#     def get(self):
#         security_credentials = self.checkCredentials()

#         query_params = {}
#         request_payload =  {}        
#         if 'filter' in  request.args and request.args['filter']:
#             filter = eval(request.args['filter'])
#             request_payload = filter
#             query_params['filter'] = request_payload

#         if 'order' in  request.args and request.args['order']:
#             order = eval(request.args['order'])
#             query_params['order'] = order
        
#         if 'range' in  request.args and request.args['range']:
#             range = eval(request.args['range'])
#             query_params['range'] = range

#         data = GetCentroCostoListUseCase().execute(security_credentials,query_params)
#         data['ok']= 1
#         return  data, 200

# @entities_ns.route('/concepto_nomina')
# @v1_api.expect(secureHeader)
# class ConceptoNominaResource(ProxySecureResource): 

#     @entities_ns.doc('Concepto de Nomina')
#     @v1_api.expect(queryParams)    
#     @jwt_required    
#     def get(self):
#         security_credentials = self.checkCredentials()

#         query_params = {}
#         request_payload =  {}        
#         if 'filter' in  request.args and request.args['filter']:
#             filter = eval(request.args['filter'])
#             request_payload = filter
#             query_params['filter'] = request_payload

#         if 'order' in  request.args and request.args['order']:
#             order = eval(request.args['order'])
#             query_params['order'] = order
        
#         if 'range' in  request.args and request.args['range']:
#             range = eval(request.args['range'])
#             query_params['range'] = range

#         data = GetConceptoNominaListUseCase().execute(security_credentials,query_params)
#         data['ok'] = 1
#         return  data, 200

# @entities_ns.route('/dispositivo_marcaje')
# @v1_api.expect(secureHeader)
# class DispositivoResource(ProxySecureResource): 

#     @entities_ns.doc('Dispositivo de Marcaje')
#     @jwt_required    
#     def get(self):
#         security_credentials = self.checkCredentials()
#         data = GetDispositivoListUseCase().execute(security_credentials)
#         return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200

# @entities_ns.route('/estatus_trabajador')
# @v1_api.expect(secureHeader)
# class EstatusTrabajadorResource(ProxySecureResource): 
 
#     @entities_ns.doc('Estatus de Trabajador')
#     @jwt_required    
#     def get(self):
#         security_credentials = self.checkCredentials()
#         data = GetEstatusTrabajadorListUseCase().execute(security_credentials)
#         return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200

# @entities_ns.route('/tipo_ausencia')
# @v1_api.expect(secureHeader)
# class TipoAusenciaResource(ProxySecureResource): 

#     @entities_ns.doc('Tipo de Ausencia')
#     @jwt_required    
#     def get(self):
#         security_credentials = self.checkCredentials()
#         data = GetTipoAusenciaListUseCase().execute(security_credentials)
#         return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200

# @entities_ns.route('/tipo_nomina')
# @v1_api.expect(secureHeader)
# class TipoNominaResource(ProxySecureResource): 

#     @entities_ns.doc('Tipo de Nomina')
#     @jwt_required    
#     def get(self):
#         security_credentials = self.checkCredentials()
#         data = GetTipoNominaListUseCase().execute(security_credentials)
#         return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200

# @entities_ns.route('/trabajador')
# @v1_api.expect(secureHeader)
# class TrabajadorResource(ProxySecureResource): 

#     @entities_ns.doc('Trabajador')
#     @v1_api.expect(queryParams)    
#     @jwt_required    
#     @v1_api.marshal_with(GetTrabajadorListStruct) 
#     def get(self):
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}
        
#         query_params = {}
#         request_payload =  {}        
#         if 'filter' in  request.args and request.args['filter']:
#             filter = eval(request.args['filter'])
#             request_payload = filter
#             query_params['filter'] = request_payload

#         if 'order' in  request.args and request.args['order']:
#             order = eval(request.args['order'])
#             query_params['order'] = order
        
#         if 'range' in  request.args and request.args['range']:
#             range = eval(request.args['range'])
#             query_params['range'] = range
        
#         data = GetTrabajadorListUseCase().execute(security_credentials,query_params)
#         data['ok']= 1
#         return  data , 200

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


@entities_ns.route('/trabajador')
@v1_api.expect(secureHeader)
class TrabajadorResource(ProxySecureResource): 
    
    @entities_ns.doc('Update Trabajador')
    @v1_api.expect(UpdateTrabajadorStruct)    
    @jwt_required    
    def put(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        payload = request.json        
        SaveTrabajadorUseCase().execute(security_credentials,payload)
        return  {'ok':1} , 200


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


@entities_ns.route('/citamedica/<cedula>')
@entities_ns.param('cedula', 'Cedula Persona')
@v1_api.expect(secureHeader)
class OneCitaResource(ProxySecureResource):

    @entities_ns.doc('Get Cita Medica')
    @v1_api.marshal_with(GetCitaStruct) 
    @jwt_required    
    def get(self,cedula):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        query_params = {'cedula': cedula}
        data = GetCitaUseCase().execute(security_credentials,query_params)
        return  {'ok': 1, 'data': data}, 200


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

# @entities_ns.route('/tipo_trabajador')
# @v1_api.expect(secureHeader)
# class TipoTrabajadorResource(ProxySecureResource): 

#     @entities_ns.doc('Tipo de Trabajador')
#     @jwt_required    
#     def get(self):
#         security_credentials = self.checkCredentials()
#         data = GetTipoTrabajadorListUseCase().execute(security_credentials)
#         return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200

# @entities_ns.route('/grupo_guardia')
# @v1_api.expect(secureHeader)
# class GrupoGuardiaResource(ProxySecureResource): 

#     @entities_ns.doc('Grupo de Guardia')
#     @jwt_required    
#     def get(self):
#         security_credentials = self.checkCredentials()
#         data = GetGrupoGuardiaListUseCase().execute(security_credentials)
#         return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200