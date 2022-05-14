from app.v1 import v1_api
from flask_jwt_extended.view_decorators import jwt_required
from flask_restplus import Resource, Namespace, fields
from app.v1.resources.base import ProxySecureResource, secureHeader, queryParams
from app.v1.use_cases.entities import CreateBeneficiarioUseCase, GetEmpresaListUseCase, GetEstadoListUseCase, GetMunicipioListUseCase,GetTipoNominaListUseCase, \
    GetTrabajadorUseCase, GetEstadoListUseCase, GetMunicipioListUseCase, GetPatologiaListUseCase, SaveBeneficiarioUseCase, DeleteBeneficiarioUseCase
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

HistoriaMedicaStruct = v1_api.model('HistoriaMedicaStruct', { 
    'cedula' : fields.String(), 
    'gruposanguineo' : fields.String(), 
    'discapacidad' : fields.String(), 
    'fecha' : fields.String(format='date-time'),
    'patologias': fields.List(fields.Nested(PatologiaStruct))
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
    'suspendido' : fields.String(),  
    'nivel' : fields.String(),  
    'profesion' : fields.String(),  

    'estado': fields.Nested(EstadoStruct,attribute='estado'),
    'municipio': fields.Nested(MunicipioStruct,attribute='municipio'),

    'parroquia' : fields.String(), 
    'sector' : fields.String(),  
    'avenidacalle' : fields.String(),  
    'edifcasa' : fields.String()
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
    'tipodiscapacidad': fields.String(),
    'patologias' : fields.List(fields.String()), #Listado de Ids de Patologias
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

BeneficiarioStruct = v1_api.model('BeneficiarioStruct', { 
    'cedula' : fields.String(),
    'vinculo' : fields.String(),
    'nombres' : fields.String(),  
    'apellidos' : fields.String(),  
    'sexo' : fields.String(),  
    'fechanacimiento' : fields.String(format='date-time'),
    'historiamedica': fields.Nested(HistoriaMedicaStruct,attribute='historiamedica')
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
    'nivel' : fields.String(),  
    'profesion' : fields.String(),  


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

    'ficha' : fields.String(),
    'historiamedica': fields.Nested(HistoriaMedicaStruct,attribute='historiamedica'),  
    'empresa': fields.Nested(EmpresaStruct,attribute='empresa'),  
    'usuarioactualizacion': fields.Nested(UsuarioActStruct,attribute='usuarioactualizacion'),

    'beneficiarios': fields.List(fields.Nested(BeneficiarioStruct))

}) 

UpdatePersonaStruct = v1_api.model('UpdatePersonaStruct', { 
    'cedula' : fields.String(), 
}) 

UpdateTrabajadorStruct = v1_api.model('UpdateTrabajadorStruct', { 
    'cedula' : fields.String(), 
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

@entities_ns.route('/trabajador/<cedula>')
@entities_ns.param('cedula', 'Cedula Trabajador')
@v1_api.expect(secureHeader)
class OneTrabajadorResource(ProxySecureResource):


    @entities_ns.doc('Get Trabajador')
    @v1_api.marshal_with(GetTrabajadorStruct) 
    #@jwt_required    
    def get(self,cedula):
        #security_credentials = self.checkCredentials()
        security_credentials = {'username': 'prueba'}
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
class EstadoResource(ProxySecureResource): 

    @entities_ns.doc('Patologia')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        #security_credentials = {'username': 'prueba'}
        data = GetPatologiaListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200


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