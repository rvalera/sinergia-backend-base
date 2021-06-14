from app.v1 import v1_api
from flask_jwt_extended.view_decorators import jwt_required
from flask_restplus import Resource, Namespace, fields
from app.v1.resources.base import ProxySecureResource, secureHeader,queryParams
from app.v1.use_cases.entities import GetCargoListUseCase,GetCentroCostoListUseCase,GetConceptoNominaListUseCase,\
    GetDispositivoListUseCase,GetEstatusTrabajadorListUseCase,GetTipoAusenciaListUseCase,GetTipoNominaListUseCase,\
    GetTrabajadorListUseCase,GetTrabajadorUseCase,GetTipoTrabajadorListUseCase,GetGrupoGuardiaListUseCase
from flask.globals import request    
import json 

entities_ns = v1_api.namespace('entities', description='Business Entities Services')

CargoStruct = v1_api.model('CargoStruct', { 
    'codigo' : fields.String(), 
    'descripcion' : fields.String(), 
})

CentroCostoStruct = v1_api.model('CentroCostoStruct', { 
    'codigo' : fields.String(), 
    'descripcion' : fields.String(), 
})

TipoNominaStruct = v1_api.model('TipoNominaStruct', { 
    'codigo' : fields.String(), 
    'descripcion' : fields.String(), 
})

StatusTrabajadorStruct = v1_api.model('StatusTrabajadorStruct', { 
    'codigo' : fields.String(), 
    'descripcion' : fields.String(), 
})

GrupoGuardiaStruct = v1_api.model('GrupoGuardiaStruct', { 
    'codigo' : fields.String(), 
    'descripcion' : fields.String(), 
})

TipoTrabajadorStruct = v1_api.model('TipoTrabajadorStruct', { 
    'codigo' : fields.String(), 
    'descripcion' : fields.String(), 
})

TrabajadorStruct = v1_api.model('TrabajadorStruct', { 
    'cedula' : fields.String(), 
    'codigo' : fields.String(), 
    'nombres' : fields.String(),  
    'apellidos' : fields.String(),  
    'sexo' : fields.String(),  
    'fecha_ingreso' : fields.String(format='date-time'),   
    'fecha_egreso' : fields.String(format='date-time'), 
    'cargo': fields.Nested(CargoStruct,attribute='cargo'),      
    'centro_costo': fields.Nested(CentroCostoStruct,attribute='centro_costo'),
    'tipo_nomina': fields.Nested(TipoNominaStruct,attribute='tipo_nomina'),    
    'status_actual': fields.Nested(StatusTrabajadorStruct,attribute='status_actual'),
    'tipo_trabajador': fields.Nested(TipoTrabajadorStruct,attribute='tipo_trabajador'),
    'grupo_guardia': fields.Nested(GrupoGuardiaStruct,attribute='grupo_guardia'),
    'id_tarjeta': fields.String(),   
    'telefono' : fields.String(),  
    'correo' : fields.String()
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

@entities_ns.route('/cargo')
@v1_api.expect(secureHeader)
class CargoResource(ProxySecureResource): 
    @entities_ns.doc('Cargo')
    @v1_api.expect(queryParams)    
    @jwt_required        
    def get(self):
        security_credentials = self.checkCredentials()

        query_params = {}
        request_payload =  {}        
        if 'filter' in  request.args and request.args['filter']:
            filter = eval(request.args['filter'])
            request_payload = filter
            query_params['filter'] = request_payload

        if 'order' in  request.args and request.args['order']:
            order = eval(request.args['order'])
            query_params['order'] = order
        
        if 'range' in  request.args and request.args['range']:
            range = eval(request.args['range'])
            query_params['range'] = range

        data = GetCargoListUseCase().execute(security_credentials,query_params)
        data['ok']= 1
        return  data , 200

@entities_ns.route('/centro_costo')
@v1_api.expect(secureHeader)
class CentroCostoResource(ProxySecureResource): 
    @entities_ns.doc('Centro de Costo')
    @v1_api.expect(queryParams)    
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()

        query_params = {}
        request_payload =  {}        
        if 'filter' in  request.args and request.args['filter']:
            filter = eval(request.args['filter'])
            request_payload = filter
            query_params['filter'] = request_payload

        if 'order' in  request.args and request.args['order']:
            order = eval(request.args['order'])
            query_params['order'] = order
        
        if 'range' in  request.args and request.args['range']:
            range = eval(request.args['range'])
            query_params['range'] = range

        data = GetCentroCostoListUseCase().execute(security_credentials,query_params)
        data['ok']= 1
        return  data, 200

@entities_ns.route('/concepto_nomina')
@v1_api.expect(secureHeader)
class ConceptoNominaResource(ProxySecureResource): 

    @entities_ns.doc('Concepto de Nomina')
    @v1_api.expect(queryParams)    
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()

        query_params = {}
        request_payload =  {}        
        if 'filter' in  request.args and request.args['filter']:
            filter = eval(request.args['filter'])
            request_payload = filter
            query_params['filter'] = request_payload

        if 'order' in  request.args and request.args['order']:
            order = eval(request.args['order'])
            query_params['order'] = order
        
        if 'range' in  request.args and request.args['range']:
            range = eval(request.args['range'])
            query_params['range'] = range

        data = GetConceptoNominaListUseCase().execute(security_credentials,query_params)
        data['ok'] = 1
        return  data, 200

@entities_ns.route('/dispositivo_marcaje')
@v1_api.expect(secureHeader)
class DispositivoResource(ProxySecureResource): 

    @entities_ns.doc('Dispositivo de Marcaje')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        data = GetDispositivoListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200

@entities_ns.route('/estatus_trabajador')
@v1_api.expect(secureHeader)
class EstatusTrabajadorResource(ProxySecureResource): 
 
    @entities_ns.doc('Estatus de Trabajador')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        data = GetEstatusTrabajadorListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200

@entities_ns.route('/tipo_ausencia')
@v1_api.expect(secureHeader)
class TipoAusenciaResource(ProxySecureResource): 

    @entities_ns.doc('Tipo de Ausencia')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        data = GetTipoAusenciaListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200

@entities_ns.route('/tipo_nomina')
@v1_api.expect(secureHeader)
class TipoNominaResource(ProxySecureResource): 

    @entities_ns.doc('Tipo de Nomina')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        data = GetTipoNominaListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200

@entities_ns.route('/trabajador')
@v1_api.expect(secureHeader)
class TrabajadorResource(ProxySecureResource): 

    @entities_ns.doc('Trabajador')
    @v1_api.expect(queryParams)    
    @jwt_required    
    @v1_api.marshal_with(GetTrabajadorListStruct) 
    def get(self):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}
        
        query_params = {}
        request_payload =  {}        
        if 'filter' in  request.args and request.args['filter']:
            filter = eval(request.args['filter'])
            request_payload = filter
            query_params['filter'] = request_payload

        if 'order' in  request.args and request.args['order']:
            order = eval(request.args['order'])
            query_params['order'] = order
        
        if 'range' in  request.args and request.args['range']:
            range = eval(request.args['range'])
            query_params['range'] = range
        
        data = GetTrabajadorListUseCase().execute(security_credentials,query_params)
        data['ok']= 1
        return  data , 200

@entities_ns.route('/trabajador/<cedula>')
@entities_ns.param('cedula', 'Cedula Trabajador')
@v1_api.expect(secureHeader)
class OneTrabajadorResource(ProxySecureResource):

    @entities_ns.doc('Get Trabajador')
    @v1_api.marshal_with(GetTrabajadorStruct) 
    @jwt_required    
    def get(self,cedula):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}
        query_params = {'cedula': cedula}
        data = GetTrabajadorUseCase().execute(security_credentials,query_params)
        return  {'ok': 1, 'data': data}, 200


@entities_ns.route('/tipo_trabajador')
@v1_api.expect(secureHeader)
class TipoTrabajadorResource(ProxySecureResource): 

    @entities_ns.doc('Tipo de Trabajador')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        data = GetTipoTrabajadorListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200

@entities_ns.route('/grupo_guardia')
@v1_api.expect(secureHeader)
class GrupoGuardiaResource(ProxySecureResource): 

    @entities_ns.doc('Grupo de Guardia')
    @jwt_required    
    def get(self):
        security_credentials = self.checkCredentials()
        data = GetGrupoGuardiaListUseCase().execute(security_credentials)
        return  {'ok':1,  "count": len(data), "total": len(data), 'data': data} , 200