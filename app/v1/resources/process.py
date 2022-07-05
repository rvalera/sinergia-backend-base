from app.v1 import v1_api
from flask_jwt_extended.view_decorators import jwt_required
from flask_restplus import Resource, Namespace, fields
from app.v1.resources.base import ProxySecureResource, secureHeader,queryParams

# from app.v1.use_cases.process import GetDailyMarkingListUseCase,GetOvertimeEventUseCase,GetAbsenceEventUseCase,ApproveOvertimeEventUseCase,NewAbsenceJustificationUseCase,\
#     SaveAbsenceJustificationUseCase,DeleteAbsenceJustificationUseCase,ApproveAbsenceJustificationUseCase,\
#     GetBatchAbsenceJustificationUseCase,NewBatchAbsenceJustificationUseCase,SaveBatchAbsenceJustificationUseCase,DeleteBatchAbsenceJustificationUseCase,ApproveBatchAbsenceJustificationUseCase,\
#     GetBatchOvertimeUseCase,NewBatchOvertimeUseCase,SaveBatchOvertimeUseCase,DeleteBatchOvertimeUseCase,ApproveBatchOvertimeUseCase,\
#     GetDetailBatchAbsenceJustificationUseCase,GetDetailBatchOvertimeUseCase
# from app.v1.use_cases.process import GetManualMarkingUseCase, GetDetailManualMarkingUseCase, NewManualMarkingUseCase, SaveManualMarkingUseCase, DeleteManualMarkingUseCase, \
#     GetDailyMarkingDetailUseCase
from flask.globals import request    
import json

from app.v1.use_cases.process import GetBiostarDeviceListUseCase, GrantAccessBiostarUseCase, ReadRFIDCardUseCase 

process_ns = v1_api.namespace('process', description='Process Services')

GrantAccesBiostarStruct = v1_api.model('GrantAccesBiostarStruct', { 
    'user_id' : fields.String(), 
    'name' : fields.String(),
    'id_card1' : fields.String(),
    'id_card2' : fields.String(),
    'start_datetime' : fields.String(),
    'expiry_datetime' : fields.String()
})


@process_ns.route('/biostar/card')
@v1_api.expect(secureHeader)
class  BiostarCardListResource(ProxySecureResource):

    @process_ns.doc('Read RFID Card List Enrolled in Biostar')
    @jwt_required
    def get(self):
        security_credentials = self.checkCredentials()
        str_data = ''' 
        [ 
            {
            "name" : "CARD1", 
            "cardid": "4600272105" 
            },
            {
            "name" : "CARD2", 
            "cardid": "4600272106" 
            },
            {
            "name" : "CARD3", 
            "cardid": "4600272107" 
            }
        ]
        '''
        data = json.loads(str_data)
        return  { 'ok': 1, 'data' : data, "count": len(data), "total": len(data) }, 200

@process_ns.route('/biostar/card/<id_biostar_device>')
@process_ns.param('id_biostar_device', 'Biostar Device ID')
@v1_api.expect(secureHeader)
class  BiostarCardResource(ProxySecureResource):

    @process_ns.doc('Read RFID Card')
    @jwt_required
    def get(self,id_biostar_device):
        security_credentials = self.checkCredentials()
        # data = ReadRFIDCardUseCase().execute(id_biostar_device)
        str_data = ''' 
            {
            "codigo" : 200, 
            "card_id": "4600272105",
            "message": "Success"
            }
        '''
        data = json.loads(str_data)
        return  { 'ok': 1, 'data' : data } , 200


# {
#   "user_id": "27027161",
#   "name": "Marie Curie",
#   "id_card1": "68801245811",
#   "id_card2": "72801245852",
#   "start_datetime": "2022-06-28T00:00:00.00Z",
#   "expiry_datetime": "2022-06-29T00:00:00.00Z"
# }
@process_ns.route('/biostar/access/grant')
@v1_api.expect(secureHeader)
class GrantAccessBiostarResource(ProxySecureResource): 

    @process_ns.doc('Grant Access to Biostar')
    @process_ns.expect(GrantAccesBiostarStruct)
    @jwt_required
    def post(self):
        payload = request.json        
        security_credentials = self.checkCredentials()
        # data = GrantAccessBiostarUseCase().execute(payload)
        str_data = ''' 
            {
                "codigo": 200,
                "id": "27027161",
                "tarjeta_asignada1": "68801245811",
                "tarjeta_asignada2": "72801245852",
                "message": "Success"
            }
        '''
        data = json.loads(str_data)
        return  {'ok': 1, 'data' : data}, 200

@process_ns.route('/biostar/device')
@v1_api.expect(secureHeader)
class GetBiostarDeviceListResource(ProxySecureResource): 

    @process_ns.doc('Get Biostar Devices List')
    @jwt_required
    def get(self):
        security_credentials = self.checkCredentials()
        # data = GetBiostarDeviceListUseCase().execute()
        str_data = ''' 
{
    "codigo": 200,
    "total": "1",
    "lista": [
        {
            "id": "544207733",
            "name": "BioEntry W2 544207733 (192.168.1.18)",
            "device_type_id": {
                "id": "13",
                "name": "BioEntry W2"
            },
            "status": "0"
        }
    ],
    "message": "Success"
}
        '''
        data = json.loads(str_data)
        return  { 'ok': 1, 'data' : data } , 200



# NewManualMarkingStruct = v1_api.model('NewManualMarkingStruct', { 
#     'fecha' : fields.String(required=True,format='date'),   
#     'cedula' : fields.Integer(required=True),   
#     'observaciones' : fields.String(required=True), 
#     'id_turno' : fields.String(required=True), 
#     'tipo_evento' : fields.Integer(required=True,description = "1: Entrada, 2:Salida"), 
#     'fecha_hora_evento' : fields.String(required=True,description = "Formato YYYY-MM-DD HH24:MI:SS"), 
# }) 

# SaveManualMarkingStruct = v1_api.model('SaveManualMarkingStruct', { 
#     'id' : fields.Integer(required=True), 
#     'fecha' : fields.String(required=True,format='date'),   
#     'cedula' : fields.Integer(required=True),   
#     'observaciones' : fields.String(required=True), 
#     'id_turno' : fields.String(required=True), 
#     'tipo_evento' : fields.Integer(required=True,description = "1: Entrada, 2:Salida"), 
#     'fecha_hora_evento' : fields.String(required=True,description = "Formato YYYY-MM-DD HH24:MI:SS"), 
# }) 

# ###############################################################################################33

# NewBatchAbsenceJustificationStruct = v1_api.model('NewBatchAbsenceJustificationStruct', { 
#     'fecha_inicio' : fields.String(required=True,format='date'),   
#     'fecha_fin' : fields.String(required=True,format='date'),   
#     'cantidad_horas' : fields.Float(required=True), 
#     'id_justificacion_ausencia' : fields.Integer(required=True), 
#     'observaciones' : fields.String(required=True), 
#     'trabajadores' : fields.List(fields.Integer()),
# }) 

# SaveBatchAbsenceJustificationStruct = v1_api.model('SaveBatchAbsenceJustificationStruct', { 
#     'id' : fields.Integer(required=True), 
#     'fecha_inicio' : fields.String(required=True,format='date'),   
#     'fecha_fin' : fields.String(required=True,format='date'),   
#     'cantidad_horas' : fields.Float(required=True), 
#     'id_justificacion_ausencia' : fields.Integer(required=True), 
#     'observaciones' : fields.String(required=True), 
#     'trabajadores' : fields.List(fields.Integer()),
# }) 

# ###############################################################################################33

# NewBatchOvertimeStruct = v1_api.model('NewBatchOvertimeStruct', { 
#     'fecha_inicio' : fields.String(required=True,format='date'),   
#     'fecha_fin' : fields.String(required=True,format='date'),   
#     'cantidad_horas' : fields.Float(required=True), 
#     'tipo_hora' : fields.Integer(required=True), 
#     'observaciones' : fields.String(required=True), 
#     'trabajadores' : fields.List(fields.Integer()),
# })


# SaveBatchOvertimeStruct = v1_api.model('SaveBatchOvertimeStruct', { 
#     'id' : fields.Integer(required=True), 
#     'fecha_inicio' : fields.String(required=True,format='date'),   
#     'fecha_fin' : fields.String(required=True,format='date'),   
#     'cantidad_horas' : fields.Float(required=True), 
#     'tipo_hora' : fields.Integer(required=True),
#     'observaciones' : fields.String(required=True), 
#     'trabajadores' : fields.List(fields.Integer()),
# }) 

# ###############################################################################################33

# NewAbsenceJustificationStruct = v1_api.model('NewAbsenceJustificationStruct', { 
#     'fecha' : fields.String(required=True,format='date'),   
#     'cedula' : fields.String(required=True),   
#     'horas_generadas' : fields.Float(required=True), 
#     'id_justificacion_ausencia' : fields.Integer(required=True),
#     'observaciones' : fields.String(required=True),
# }) 

# SaveAbsenceJustificationStruct = v1_api.model('SaveAbsenceJustificationStruct', { 
#     'id' : fields.Integer(required=True), 
#     'fecha' : fields.String(required=True,format='date'),   
#     'cedula' : fields.String(required=True),   
#     'horas_generadas' : fields.Float(required=True), 
#     'id_justificacion_ausencia' : fields.Integer(required=True), 
#     'observaciones' : fields.String(required=True),    
# }) 


# ApproveOvertimeStruct = v1_api.model('ApproveOvertimeStruct', { 
#     'observaciones' : fields.String(required=True),    
# }) 

# @process_ns.route('/daily_marking')
# @v1_api.expect(secureHeader)
# class DailyMarkingResource(ProxySecureResource): 

#     @process_ns.doc('Get Marcajes Diarios')
#     @v1_api.expect(queryParams)
#     @jwt_required    
#     def get(self):
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'guest'}
#         query_params = {}
#         request_payload =  {}        
#         if 'filter' in  request.args and request.args['filter']:
#             filter = eval(request.args['filter'])
#             request_payload = filter
#             query_params['filter'] = request_payload

#         if 'order' in  request.args and request.args['order']:
#             order = eval(request.args['order'])
#             query_params['order'] = order
#         query_params['order'] = ['fecdia ASC','cedula ASC']

        
#         if 'range' in  request.args and request.args['range']:
#             range = eval(request.args['range'])
#             query_params['range'] = range
        
#         data = GetDailyMarkingListUseCase().execute(security_credentials,query_params)
#         data['ok']= 1
#         return  data , 200


# @process_ns.route('/daily_marking/<event_date>/<cedula>')
# @process_ns.param('event_date', 'Fecha Evento')
# @process_ns.param('cedula', 'Cedula Trabajador')
# @v1_api.expect(secureHeader)
# class GetDailyMarkingDetailResource(ProxySecureResource): 

#     @process_ns.doc('Get Detalles de Marcaje Diario')
#     @jwt_required
#     def get(self,event_date,cedula):
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'guest'}
#         data = GetDailyMarkingDetailUseCase().execute(security_credentials,event_date,cedula)
#         return  {'ok':1, 'data': data} , 200


# @process_ns.route('/daily_marking/overtime/<event_date>/<cedula>')
# @process_ns.param('event_date', 'Fecha Evento')
# @process_ns.param('cedula', 'Cedula Trabajador')
# @v1_api.expect(secureHeader)
# class GetOvertimeEventResource(ProxySecureResource): 

#     @process_ns.doc('Get Evento de Horas Extras')
#     @jwt_required
#     def get(self,event_date,cedula):
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'guest'}        
#         data = GetOvertimeEventUseCase().execute(security_credentials,event_date,cedula)
#         return  {'ok':1, 'data': data} , 200


# @process_ns.route('/daily_marking/overtime/<event_date>/<cedula>/<id>/approve')
# @process_ns.param('event_date', 'Fecha Evento')
# @process_ns.param('cedula', 'Cedula Trabajador')
# @process_ns.param('id', 'Identificador')
# @v1_api.expect(secureHeader)
# class  ApproveOvertimeEventResource(ProxySecureResource):        

#     @process_ns.doc('Aprobar Evento de Horas Extras')
#     @jwt_required
#     @v1_api.expect(ApproveOvertimeStruct)
#     def put(self,event_date,cedula,id):
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}  
#         payload = request.json    
#         payload['event_date'] = event_date
#         payload['cedula'] = cedula
#         payload['id'] = id
#         data = ApproveOvertimeEventUseCase().execute(security_credentials,payload)
#         return  { 'ok': 1 } , 200
  

# @process_ns.route('/daily_marking/absence/<event_date>/<cedula>')
# @process_ns.param('event_date', 'Fecha Evento')
# @process_ns.param('cedula', 'Cedula Trabajador')
# @v1_api.expect(secureHeader)
# class GetAbsenceEventResource(ProxySecureResource): 

#     @process_ns.doc('Get Ausencia y sus correspondientes Justificaciones para un Marcaje determinado')
#     @jwt_required
#     def get(self,event_date,cedula):
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}               
#         data = GetAbsenceEventUseCase().execute(security_credentials,event_date,cedula)
#         return  {'ok':1, 'data': data} , 200


# @process_ns.route('/daily_marking/absence_justification')
# @v1_api.expect(secureHeader)
# class AbsenceJustificationResource(ProxySecureResource): 

#     @process_ns.doc('New Justificacion de Ausencia')
#     @v1_api.expect(NewAbsenceJustificationStruct)    
#     @jwt_required
#     def post(self):
#         payload = request.json        
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}
#         NewAbsenceJustificationUseCase().execute(security_credentials,payload)
#         return  {'ok': 1}, 200

#     @process_ns.doc('Update Justificacion de Ausencia')
#     @v1_api.expect(SaveAbsenceJustificationStruct)    
#     @jwt_required
#     def put(self):
#         payload = request.json        
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}
#         SaveAbsenceJustificationUseCase().execute(security_credentials,payload)
#         return  {'ok': 1}, 200


# @process_ns.route('/daily_marking/absence_justification/<event_date>/<cedula>/<id>/approve')
# @process_ns.param('event_date', 'Fecha Evento')
# @process_ns.param('cedula', 'Cedula Trabajador')
# @process_ns.param('id', 'Identificador')
# @v1_api.expect(secureHeader)
# class  ApproveAbsenceJustificationResource(ProxySecureResource):        

#     @process_ns.doc('Aprobar Justificacion de Ausencia')
#     @jwt_required
#     def put(self,event_date,cedula,id):
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}                
#         data = ApproveAbsenceJustificationUseCase().execute(security_credentials,event_date,cedula,id)
#         return  { 'ok': 1 } , 200


# @process_ns.route('/daily_marking/absence_justification/<event_date>/<cedula>/<id>')
# @process_ns.param('event_date', 'Fecha Evento')
# @process_ns.param('cedula', 'Cedula Trabajador')
# @process_ns.param('id', 'Identificador')
# @v1_api.expect(secureHeader)
# class  DeleteAbsenceJustificationResource(ProxySecureResource):        

#     @process_ns.doc('Eliminar Justificacion de Ausencia')
#     @jwt_required
#     def delete(self,event_date,cedula,id):
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}        
#         data = DeleteAbsenceJustificationUseCase().execute(security_credentials,event_date,cedula,id)
#         return  { 'ok': 1 } , 200

# ##########################################################################################################################3

# @process_ns.route('/batch_absence_justification')
# @v1_api.expect(secureHeader)
# class BatchAbsenceJustificationResource(ProxySecureResource): 

#     @process_ns.doc('Get Justificacion de Ausencia por Lotes')
#     @v1_api.expect(queryParams)
#     @jwt_required    
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
#         query_params['order'] = ['fecha_inicio ASC','fecha_fin ASC']

        
#         if 'range' in  request.args and request.args['range']:
#             range = eval(request.args['range'])
#             query_params['range'] = range
        
#         data = GetBatchAbsenceJustificationUseCase().execute(security_credentials,query_params)
#         data['ok']= 1
#         return  data , 200    

#     @process_ns.doc('New Justificacion de Ausencia por Lotes')
#     @v1_api.expect(NewBatchAbsenceJustificationStruct)    
#     @jwt_required
#     def post(self):
#         payload = request.json        
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}
#         NewBatchAbsenceJustificationUseCase().execute(security_credentials,payload)
#         return  {'ok': 1}, 200

#     @process_ns.doc('Update Justificacion de Ausencia por Lotes')
#     @v1_api.expect(SaveBatchAbsenceJustificationStruct)    
#     @jwt_required
#     def put(self):
#         payload = request.json        
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}
#         SaveBatchAbsenceJustificationUseCase().execute(security_credentials,payload)
#         return  {'ok': 1}, 200
    

# @process_ns.route('/batch_absence_justification/<id>/approve')
# @process_ns.param('id', 'Identificador')
# @v1_api.expect(secureHeader)
# class  ApproveBatchAbsenceJustificationResource(ProxySecureResource):        

#     @process_ns.doc('Aprobar Justificacion de Ausencia por Lotes')
#     @jwt_required
#     def put(self,id):
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}        
#         data = ApproveBatchAbsenceJustificationUseCase().execute(security_credentials,id)
#         return  { 'ok': 1 } , 200


# @process_ns.route('/batch_absence_justification/<id>')
# @process_ns.param('id', 'Identificador')
# @v1_api.expect(secureHeader)
# class  DetailBatchAbsenceJustificationResource(ProxySecureResource):        

#     @process_ns.doc('Eliminar Justificacion de Ausencia por Lotes')
#     @jwt_required
#     def delete(self,id):
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}        
#         data = DeleteBatchAbsenceJustificationUseCase().execute(security_credentials,id)
#         return  { 'ok': 1 } , 200

#     @process_ns.doc('Get Detalles Justificacion de Ausencia por Lotes')
#     @jwt_required
#     def get(self,id):
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}        
#         data = GetDetailBatchAbsenceJustificationUseCase().execute(security_credentials,id)
#         return  { 'ok': 1, 'data' : data } , 200

# #############################################################################################################

# @process_ns.route('/batch_overtime')
# @v1_api.expect(secureHeader)
# class BatchOvertimeResource(ProxySecureResource): 

#     @process_ns.doc('Get Sobretiempo por Lotes')
#     @v1_api.expect(queryParams)
#     @jwt_required    
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
#         query_params['order'] = ['fecha_inicio ASC','fecha_fin ASC']
        
#         if 'range' in  request.args and request.args['range']:
#             range = eval(request.args['range'])
#             query_params['range'] = range
        
#         data = GetBatchOvertimeUseCase().execute(security_credentials,query_params)
#         data['ok']= 1
#         return  data , 200    

#     @process_ns.doc('New Sobretiempo por Lotes')
#     @v1_api.expect(NewBatchOvertimeStruct)    
#     @jwt_required
#     def post(self):
#         payload = request.json        
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}
#         NewBatchOvertimeUseCase().execute(security_credentials,payload)
#         return  {'ok': 1}, 200

#     @process_ns.doc('Update Sobretiempo por Lotes')
#     @v1_api.expect(SaveBatchOvertimeStruct)    
#     @jwt_required
#     def put(self):
#         payload = request.json        
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}
#         SaveBatchOvertimeUseCase().execute(security_credentials,payload)
#         return  {'ok': 1}, 200
    

# @process_ns.route('/batch_overtime/<id>/approve')
# @process_ns.param('id', 'Identificador')
# @v1_api.expect(secureHeader)
# class  ApproveBatchOvertimeResource(ProxySecureResource):        

#     @process_ns.doc('Aprobar Sobretiempo por Lotes')
#     @jwt_required
#     def put(self,id):
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}        
#         data = ApproveBatchOvertimeUseCase().execute(security_credentials,id)
#         return  { 'ok': 1 } , 200


# @process_ns.route('/batch_overtime/<id>')
# @process_ns.param('id', 'Identificador')
# @v1_api.expect(secureHeader)
# class  DetailBatchOvertimeResource(ProxySecureResource):

#     @process_ns.doc('Eliminar Sobretiempo por Lotes')
#     @jwt_required
#     def delete(self,id):
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}        
#         data = DeleteBatchOvertimeUseCase().execute(security_credentials,id)
#         return  { 'ok': 1 } , 200

#     @process_ns.doc('Get Detalles Sobretiempo por Lotes')
#     @jwt_required
#     def get(self,id):
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}        
#         data = GetDetailBatchOvertimeUseCase().execute(security_credentials,id)
#         return  { 'ok': 1, 'data' : data } , 200

# #############################################################################################################

# @process_ns.route('/manual_marking')
# @v1_api.expect(secureHeader)
# class ManualMarkingResource(ProxySecureResource): 

#     @process_ns.doc('Get Marcajes Manuales')
#     @v1_api.expect(queryParams)
#     @jwt_required    
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
#         query_params['order'] = ['fecha_marcaje ASC','cedula ASC']

        
#         if 'range' in  request.args and request.args['range']:
#             range = eval(request.args['range'])
#             query_params['range'] = range
        
#         data = GetManualMarkingUseCase().execute(security_credentials,query_params)
#         data['ok']= 1
#         return  data , 200    

#     @process_ns.doc('New Marcaje Manual')
#     @v1_api.expect(NewManualMarkingStruct)
#     @jwt_required
#     def post(self):
#         payload = request.json
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}
#         NewManualMarkingUseCase().execute(security_credentials,payload)
#         return  {'ok': 1}, 200

#     @process_ns.doc('Update Marcaje Manual')
#     @v1_api.expect(SaveManualMarkingStruct)    
#     @jwt_required
#     def put(self):
#         payload = request.json        
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}
#         SaveManualMarkingUseCase().execute(security_credentials,payload)
#         return  {'ok': 1}, 200
    

# @process_ns.route('/manual_marking/<event_date>/<cedula>/<id>')
# @process_ns.param('event_date', 'Fecha Evento')
# @process_ns.param('cedula', 'Cedula Trabajador')
# @process_ns.param('id', 'Identificador')
# @v1_api.expect(secureHeader)
# class  DetailManualMarkingResource(ProxySecureResource):

#     @process_ns.doc('Eliminar Marcaje Manual')
#     @jwt_required
#     def delete(self,event_date,cedula,id):
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}        
#         data = DeleteManualMarkingUseCase().execute(security_credentials,event_date,cedula,id)
#         return  { 'ok': 1 } , 200

#     @process_ns.doc('Get Marcaje Manual')
#     @jwt_required
#     def get(self,event_date,cedula,id):
#         security_credentials = self.checkCredentials()
#         # security_credentials = {'username': 'prueba'}        
#         data = GetDetailManualMarkingUseCase().execute(security_credentials,event_date,cedula,id)
#         return  { 'ok': 1, 'data' : data } , 200
