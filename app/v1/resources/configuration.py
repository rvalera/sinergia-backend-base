from app.v1 import v1_api
from flask_jwt_extended.view_decorators import jwt_required
from flask_restplus import Resource, Namespace, fields
from app.v1.resources.base import ProxySecureResource, secureHeader,queryParams
from app.v1.use_cases.configuration import GetHolguraListUseCase,NewHolguraUseCase,SaveHolguraUseCase,DeleteHolguraUseCase,\
    GetTurnoListUseCase,NewTurnoUseCase,SaveTurnoUseCase,DeleteTurnoUseCase,ApproveHolguraUseCase
from flask.globals import request    
import json 

configuration_ns = v1_api.namespace('configuration', description='Configuration Services')

HolguraStruct = v1_api.model('HolguraStruct', { 
    'id' : fields.Integer(), 
    'fecha_desde' : fields.String(format='date-time'),   
    'fecha_hasta' : fields.String(format='date-time'),   
    'autorizado_por' : fields.String(),  
    'minutos_tolerancia' : fields.Integer(), 
    'id_centro_costo' : fields.String(),  
    'nombre_centro_costo' : fields.String(),  
    'id_tipo_nomina' : fields.String(),  
    'nombre_tipo_nomina' : fields.String(),
    'cedula_trabajador' : fields.String(required=True),  
    'apellidos' : fields.String(required=True),  
    'nombres' : fields.String(required=True),  
}) 

NewHolguraStruct = v1_api.model('NewHolguraStruct', { 
    'fecha_desde' : fields.String(required=True,format='date-time'),   
    'fecha_hasta' : fields.String(required=True,format='date-time'),   
    'autorizado_por' : fields.String(required=True),  
    'minutos_tolerancia' : fields.Integer(required=True), 
    'id_centro_costo' : fields.String(required=True),  
    'id_tipo_nomina' : fields.String(required=True),  
    'cedula_trabajador' : fields.String(required=True),  
}) 

SaveHolguraStruct = v1_api.model('SaveHolguraStruct', { 
    'id' : fields.Integer(), 
    'fecha_desde' : fields.String(required=True,format='date-time'),   
    'fecha_hasta' : fields.String(required=True,format='date-time'),   
    'autorizado_por' : fields.String(required=True),  
    'minutos_tolerancia' : fields.Integer(required=True), 
    'id_centro_costo' : fields.String(required=True),  
    'id_tipo_nomina' : fields.String(required=True),  
    'cedula_trabajador' : fields.String(required=True),  
}) 


GetHolguraListStruct = v1_api.model('GetHolguraListResult', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'count' : fields.Integer(description='Count Row'), 
    'total' : fields.Integer(description='Total Row'), 
    'data' : fields.Nested(HolguraStruct,attribute='data')
}) 

TurnoStruct = v1_api.model('TurnoStruct', { 
    'codigo' : fields.String(required=True), 
    'descripcion' : fields.String(required=True),   
    'hora_inicio' : fields.String(required=True,format='time'),   
    'hora_final' : fields.String(required=True,format='time'),   
    'cantidad_horas_diurnas' : fields.Float(), 
    'hinicio_descanso' : fields.String(required=True,format='time'),   
    'hfinal_descanso' : fields.String(required=True,format='time'),   
    'horas_nocturnas' : fields.Float(), 
    'status' : fields.String(),  
}) 

GetTurnoListStruct = v1_api.model('GetTurnoListStruct', { 
    'ok' : fields.Integer(description='Ok Result'), 
    'count' : fields.Integer(description='Count Row'), 
    'total' : fields.Integer(description='Total Row'), 
    'data' : fields.Nested(TurnoStruct,attribute='data')
})

@configuration_ns.route('/holgura')
@v1_api.expect(secureHeader)
class HolguraResource(ProxySecureResource): 
# class HolguraResource(Resource): 

    @configuration_ns.doc('Get Holgura List')
    @v1_api.expect(queryParams)    
    @jwt_required    
    @v1_api.marshal_with(GetHolguraListStruct) 
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
        
        data = GetHolguraListUseCase().execute(security_credentials,query_params)
        data['ok']= 1
        return  data , 200

    @configuration_ns.doc('New Holgura')
    @v1_api.expect(NewHolguraStruct)    
    @jwt_required    
    def post(self):
        payload = request.json        
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}
        NewHolguraUseCase().execute(security_credentials,payload)
        return  {'ok': 1}, 200

    @configuration_ns.doc('Save Holgura')
    @v1_api.expect(SaveHolguraStruct)    
    @jwt_required    
    def put(self):
        payload = request.json        
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}
        SaveHolguraUseCase().execute(security_credentials,payload)
        return  {'ok': 1}, 200


@configuration_ns.route('/holgura/<id>')
@configuration_ns.param('id', 'Holgura Id')
@v1_api.expect(secureHeader)
class DeleteHolguraResource(ProxySecureResource):
# class DeleteHolguraResource(Resource):
    
    @configuration_ns.doc('Remove Holgura')
    @jwt_required    
    def delete(self,id):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'guest'}
        query_params = {'id': id}
        DeleteHolguraUseCase().execute(security_credentials,query_params)
        return  {'ok': 1}, 200

@configuration_ns.route('/holgura/<id>/approve')
@configuration_ns.param('id', 'Holgura Id')
@v1_api.expect(secureHeader)
class ApproveHolguraResource(ProxySecureResource):
# class DeleteHolguraResource(Resource):
    
    @configuration_ns.doc('Approve Holgura')
    @jwt_required    
    def put(self,id):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'guest'}
        ApproveHolguraUseCase().execute(security_credentials,id)
        return  {'ok': 1}, 200


###################################################################################################

@configuration_ns.route('/turno')
@v1_api.expect(secureHeader)
class TurnoResource(ProxySecureResource): 

    @configuration_ns.doc('Get Turno List')
    @v1_api.expect(queryParams)    
    @jwt_required    
    @v1_api.marshal_with(GetTurnoListStruct) 
    def get(self):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'guest'}
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
        
        data = GetTurnoListUseCase().execute(security_credentials,query_params)
        data['ok']= 1
        return  data , 200

    @configuration_ns.doc('New Turno')
    @v1_api.expect(TurnoStruct)    
    @jwt_required    
    def post(self):
        payload = request.json        
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'guest'}
        NewTurnoUseCase().execute(security_credentials,payload)
        return  {'ok': 1}, 200

    @configuration_ns.doc('Save Turno')
    @v1_api.expect(TurnoStruct)    
    @jwt_required    
    def put(self):
        payload = request.json        
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'guest'}
        SaveTurnoUseCase().execute(security_credentials,payload)
        return  {'ok': 1}, 200



@configuration_ns.route('/turno/<codigo>')
@configuration_ns.param('codigo', 'Turno Codigo')
@v1_api.expect(secureHeader)
class DeleteTurnoResource(ProxySecureResource):
    
    @configuration_ns.doc('Remove Turno')
    @jwt_required    
    def delete(self,codigo):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'guest'}
        query_params = {'codigo': codigo}
        DeleteTurnoUseCase().execute(security_credentials,query_params)
        return  {'ok': 1}, 200

###################################################################################################
