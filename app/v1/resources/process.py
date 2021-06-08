from app.v1 import v1_api
from flask_jwt_extended.view_decorators import jwt_required
from flask_restplus import Resource, Namespace, fields
from app.v1.resources.base import ProxySecureResource, secureHeader,queryParams
from app.v1.use_cases.process import GetDailyMarkingListUseCase,GetOvertimeEventUseCase,GetAbsenceEventUseCase,ApproveOvertimeEventUseCase,NewAbsenceJustificationUseCase,\
    SaveAbsenceJustificationUseCase,DeleteAbsenceJustificationUseCase,ApproveAbsenceJustificationUseCase,\
    GetBatchAbsenceJustificationUseCase,NewBatchAbsenceJustificationUseCase,SaveBatchAbsenceJustificationUseCase,DeleteBatchAbsenceJustificationUseCase,ApproveBatchAbsenceJustificationUseCase,\
    GetBatchOvertimeUseCase,NewBatchOvertimeUseCase,SaveBatchOvertimeUseCase,DeleteBatchOvertimeUseCase,ApproveBatchOvertimeUseCase,\
    GetDetailBatchAbsenceJustificationUseCase,GetDetailBatchOvertimeUseCase
from flask.globals import request    
import json 

process_ns = v1_api.namespace('process', description='Process Services')

NewBatchAbsenceJustificationStruct = v1_api.model('NewBatchAbsenceJustificationStruct', { 
    'fecha_inicio' : fields.String(required=True,format='date'),   
    'fecha_fin' : fields.String(required=True,format='date'),   
    'cantidad_horas' : fields.Float(required=True), 
    'id_justificacion_ausencia' : fields.Integer(required=True), 
    'observaciones' : fields.String(required=True), 
    'trabajadores' : fields.List(fields.Integer()),
}) 

SaveBatchAbsenceJustificationStruct = v1_api.model('SaveBatchAbsenceJustificationStruct', { 
    'id' : fields.Integer(required=True), 
    'fecha_inicio' : fields.String(required=True,format='date'),   
    'fecha_fin' : fields.String(required=True,format='date'),   
    'cantidad_horas' : fields.Float(required=True), 
    'id_justificacion_ausencia' : fields.Integer(required=True), 
    'observaciones' : fields.String(required=True), 
    'trabajadores' : fields.List(fields.Integer()),
}) 

###############################################################################################33

NewBatchOvertimeStruct = v1_api.model('NewBatchOvertimeStruct', { 
    'fecha_inicio' : fields.String(required=True,format='date'),   
    'fecha_fin' : fields.String(required=True,format='date'),   
    'cantidad_horas' : fields.Float(required=True), 
    'tipo_hora' : fields.Integer(required=True), 
    'observaciones' : fields.String(required=True), 
    'trabajadores' : fields.List(fields.Integer()),
}) 

SaveBatchOvertimeStruct = v1_api.model('SaveBatchOvertimeStruct', { 
    'id' : fields.Integer(required=True), 
    'fecha_inicio' : fields.String(required=True,format='date'),   
    'fecha_fin' : fields.String(required=True,format='date'),   
    'cantidad_horas' : fields.Float(required=True), 
    'tipo_hora' : fields.Integer(required=True),
    'observaciones' : fields.String(required=True), 
    'trabajadores' : fields.List(fields.Integer()),
}) 

###############################################################################################33

NewAbsenceJustificationStruct = v1_api.model('NewAbsenceJustificationStruct', { 
    'fecha' : fields.String(required=True,format='date'),   
    'cedula' : fields.String(required=True),   
    'horas_generadas' : fields.Float(required=True), 
    'id_justificacion_ausencia' : fields.Integer(required=True), 
}) 

SaveAbsenceJustificationStruct = v1_api.model('SaveAbsenceJustificationStruct', { 
    'id' : fields.Integer(required=True), 
    'fecha' : fields.String(required=True,format='date'),   
    'cedula' : fields.String(required=True),   
    'horas_generadas' : fields.Float(required=True), 
    'id_justificacion_ausencia' : fields.Integer(required=True), 
}) 

@process_ns.route('/daily_marking')
@v1_api.expect(secureHeader)
class DailyMarkingResource(ProxySecureResource): 

    @process_ns.doc('Get Marcajes Diarios')
    @v1_api.expect(queryParams)
    @jwt_required    
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
        
        data = GetDailyMarkingListUseCase().execute(security_credentials,query_params)
        data['ok']= 1
        return  data , 200


@process_ns.route('/daily_marking/overtime/<event_date>/<cedula>')
@process_ns.param('event_date', 'Fecha Evento')
@process_ns.param('cedula', 'Cedula Trabajador')
@v1_api.expect(secureHeader)
class GetOvertimeEventResource(ProxySecureResource): 

    @process_ns.doc('Get Evento de Horas Extras')
    @jwt_required
    def get(self,event_date,cedula):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'guest'}        
        data = GetOvertimeEventUseCase().execute(security_credentials,event_date,cedula)
        return  {'ok':1, 'data': data} , 200


@process_ns.route('/daily_marking/overtime/<event_date>/<cedula>/<id>/approve')
@process_ns.param('event_date', 'Fecha Evento')
@process_ns.param('cedula', 'Cedula Trabajador')
@process_ns.param('id', 'Identificador')
@v1_api.expect(secureHeader)
class  ApproveOvertimeEventResource(ProxySecureResource):        

    @process_ns.doc('Aprobar Evento de Horas Extras')
    @jwt_required
    def put(self,event_date,cedula,id):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}        
        data = ApproveOvertimeEventUseCase().execute(security_credentials,event_date,cedula,id)
        return  { 'ok': 1 } , 200
  

@process_ns.route('/daily_marking/absence/<event_date>/<cedula>')
@process_ns.param('event_date', 'Fecha Evento')
@process_ns.param('cedula', 'Cedula Trabajador')
@v1_api.expect(secureHeader)
class GetAbsenceEventResource(ProxySecureResource): 

    @process_ns.doc('Get Ausencia y sus correspondientes Justificaciones para un Marcaje determinado')
    # @jwt_required
    def get(self,event_date,cedula):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}               
        data = GetAbsenceEventUseCase().execute(security_credentials,event_date,cedula)
        return  {'ok':1, 'data': data} , 200

@process_ns.route('/daily_marking/absence_justification')
@v1_api.expect(secureHeader)
class AbsenceJustificationResource(ProxySecureResource): 

    @process_ns.doc('New Justificacion de Ausencia')
    @v1_api.expect(NewAbsenceJustificationStruct)    
    @jwt_required
    def post(self):
        payload = request.json        
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}
        NewAbsenceJustificationUseCase().execute(security_credentials,payload)
        return  {'ok': 1}, 200

    @process_ns.doc('Update Justificacion de Ausencia')
    @v1_api.expect(SaveAbsenceJustificationStruct)    
    # @jwt_required
    def put(self):
        payload = request.json        
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}
        SaveAbsenceJustificationUseCase().execute(security_credentials,payload)
        return  {'ok': 1}, 200
    

@process_ns.route('/daily_marking/absence_justification/<event_date>/<cedula>/<id>/approve')
@process_ns.param('event_date', 'Fecha Evento')
@process_ns.param('cedula', 'Cedula Trabajador')
@process_ns.param('id', 'Identificador')
@v1_api.expect(secureHeader)
class  ApproveAbsenceJustificationResource(ProxySecureResource):        

    @process_ns.doc('Aprobar Justificacion de Ausencia')
    @jwt_required
    def put(self,event_date,cedula,id):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}        
        data = ApproveAbsenceJustificationUseCase().execute(security_credentials,event_date,cedula,id)
        return  { 'ok': 1 } , 200


@process_ns.route('/daily_marking/absence_justification/<event_date>/<cedula>/<id>')
@process_ns.param('event_date', 'Fecha Evento')
@process_ns.param('cedula', 'Cedula Trabajador')
@process_ns.param('id', 'Identificador')
@v1_api.expect(secureHeader)
class  DeleteAbsenceJustificationResource(ProxySecureResource):        

    @process_ns.doc('Eliminar Justificacion de Ausencia')
    @jwt_required
    def delete(self,event_date,cedula,id):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}        
        data = DeleteAbsenceJustificationUseCase().execute(security_credentials,event_date,cedula,id)
        return  { 'ok': 1 } , 200

##########################################################################################################################3

@process_ns.route('/batch_absence_justification')
@v1_api.expect(secureHeader)
class BatchAbsenceJustificationResource(ProxySecureResource): 

    @process_ns.doc('Get Justificacion de Ausencia por Lotes')
    @v1_api.expect(queryParams)
    @jwt_required    
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
        
        data = GetBatchAbsenceJustificationUseCase().execute(security_credentials,query_params)
        data['ok']= 1
        return  data , 200    

    @process_ns.doc('New Justificacion de Ausencia por Lotes')
    @v1_api.expect(NewBatchAbsenceJustificationStruct)    
    @jwt_required
    def post(self):
        payload = request.json        
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}
        NewBatchAbsenceJustificationUseCase().execute(security_credentials,payload)
        return  {'ok': 1}, 200

    @process_ns.doc('Update Justificacion de Ausencia por Lotes')
    @v1_api.expect(SaveBatchAbsenceJustificationStruct)    
    @jwt_required
    def put(self):
        payload = request.json        
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}
        SaveBatchAbsenceJustificationUseCase().execute(security_credentials,payload)
        return  {'ok': 1}, 200
    

@process_ns.route('/batch_absence_justification/<id>/approve')
@process_ns.param('id', 'Identificador')
@v1_api.expect(secureHeader)
class  ApproveBatchAbsenceJustificationResource(ProxySecureResource):        

    @process_ns.doc('Aprobar Justificacion de Ausencia por Lotes')
    @jwt_required
    def put(self,id):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}        
        data = ApproveBatchAbsenceJustificationUseCase().execute(security_credentials,id)
        return  { 'ok': 1 } , 200


@process_ns.route('/batch_absence_justification/<id>')
@process_ns.param('id', 'Identificador')
@v1_api.expect(secureHeader)
class  DetailBatchAbsenceJustificationResource(ProxySecureResource):        

    @process_ns.doc('Eliminar Justificacion de Ausencia por Lotes')
    @jwt_required
    def delete(self,id):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}        
        data = DeleteBatchAbsenceJustificationUseCase().execute(security_credentials,id)
        return  { 'ok': 1 } , 200

    @process_ns.doc('Get Detalles Justificacion de Ausencia por Lotes')
    @jwt_required
    def get(self,id):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}        
        data = GetDetailBatchAbsenceJustificationUseCase().execute(security_credentials,id)
        return  { 'ok': 1, 'data' : data } , 200        

#############################################################################################################

@process_ns.route('/batch_overtime')
@v1_api.expect(secureHeader)
class BatchOvertimeResource(ProxySecureResource): 

    @process_ns.doc('Get Sobretiempo por Lotes')
    @v1_api.expect(queryParams)
    @jwt_required    
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
        
        data = GetBatchOvertimeUseCase().execute(security_credentials,query_params)
        data['ok']= 1
        return  data , 200    

    @process_ns.doc('New Sobretiempo por Lotes')
    @v1_api.expect(NewBatchOvertimeStruct)    
    @jwt_required
    def post(self):
        payload = request.json        
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}
        NewBatchOvertimeUseCase().execute(security_credentials,payload)
        return  {'ok': 1}, 200

    @process_ns.doc('Update Sobretiempo por Lotes')
    @v1_api.expect(SaveBatchOvertimeStruct)    
    @jwt_required
    def put(self):
        payload = request.json        
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}
        SaveBatchOvertimeUseCase().execute(security_credentials,payload)
        return  {'ok': 1}, 200
    

@process_ns.route('/batch_overtime/<id>/approve')
@process_ns.param('id', 'Identificador')
@v1_api.expect(secureHeader)
class  ApproveBatchOvertimeResource(ProxySecureResource):        

    @process_ns.doc('Aprobar Sobretiempo por Lotes')
    @jwt_required
    def put(self,id):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}        
        data = ApproveBatchOvertimeUseCase().execute(security_credentials,id)
        return  { 'ok': 1 } , 200


@process_ns.route('/batch_overtime/<id>')
@process_ns.param('id', 'Identificador')
@v1_api.expect(secureHeader)
class  DetailBatchOvertimeResource(ProxySecureResource):        

    @process_ns.doc('Eliminar Sobretiempo por Lotes')
    @jwt_required
    def delete(self,id):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}        
        data = DeleteBatchOvertimeUseCase().execute(security_credentials,id)
        return  { 'ok': 1 } , 200


    @process_ns.doc('Get Detalles Sobretiempo por Lotes')
    @jwt_required
    def get(self,id):
        security_credentials = self.checkCredentials()
        # security_credentials = {'username': 'prueba'}        
        data = GetDetailBatchOvertimeUseCase().execute(security_credentials,id)
        return  { 'ok': 1, 'data' : data } , 200
