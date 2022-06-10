'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.repository.entities import EmpresaRepository, HistoriaMedicaRepository, TipoNominaRepository, TrabajadorRepository, EstadoRepository, MunicipioRepository, \
    PatologiaRepository, BeneficiarioRepository, EspecialidadRepository, CitaRepository, DiscapacidadRepository, PersonaRepository, VisitaRepository, ConsultaMedicaRepository, \
    AreaRepository, MedicoRepository, ConsultorioRepository

class GetEmpresaListUseCase(object):
    def execute(self,security_credentials):
        return EmpresaRepository(username=security_credentials['username']).getAll()

class GetTipoNominaListUseCase(object):
    def execute(self,security_credentials):
        return TipoNominaRepository(username=security_credentials['username']).getAll()

class GetAreaListUseCase(object):
    def execute(self,security_credentials):
        return AreaRepository(username=security_credentials['username']).getAll()

class GetConsultorioListUseCase(object):
    def execute(self,security_credentials):
        return ConsultorioRepository(username=security_credentials['username']).getAll()

class GetPatologiaListUseCase(object):
    def execute(self,security_credentials):
        return PatologiaRepository(username=security_credentials['username']).getAll()

class GetDiscapacidadListUseCase(object):
    def execute(self,security_credentials):
        return DiscapacidadRepository(username=security_credentials['username']).getAll()

class GetEspecialidadListUseCase(object):
    def execute(self,security_credentials):
        return EspecialidadRepository(username=security_credentials['username']).getAll()

class CreateEspecialidadUseCase(object):
    def execute(self,security_credentials,payload):
        EspecialidadRepository(username=security_credentials['username']).new(payload)

class SaveEspecialidadUseCase(object):
    def execute(self,security_credentials,payload):
        EspecialidadRepository(username=security_credentials['username']).save(payload)

class GetEspecialidadUseCase(object):
    def execute(self,security_credentials,query_params):
        return EspecialidadRepository(username=security_credentials['username']).getById(query_params['codigoespecialidad'])

class GetPersonaUseCase(object):
    def execute(self,security_credentials,query_params):
        return PersonaRepository(username=security_credentials['username']).getByCedula(query_params['cedula'])

class SaveTrabajadorUseCase(object):
    def execute(self,security_credentials,payload):
        TrabajadorRepository(username=security_credentials['username']).save(payload)

class GetTrabajadorUseCase(object):
    def execute(self,security_credentials,query_params):
        return TrabajadorRepository(username=security_credentials['username']).getByCedula(query_params['cedula'])

class GetEstadoListUseCase(object):
    def execute(self,security_credentials):
        return EstadoRepository(username=security_credentials['username']).getAll()

class GetMunicipioListUseCase(object):
    def execute(self,security_credentials):
        return MunicipioRepository(username=security_credentials['username']).getAll()

class CreateBeneficiarioUseCase(object):
    def execute(self,security_credentials,payload):
        BeneficiarioRepository(username=security_credentials['username']).new(payload)

class SaveBeneficiarioUseCase(object):
    def execute(self,security_credentials,payload):
        BeneficiarioRepository(username=security_credentials['username']).save(payload)

class DeleteBeneficiarioUseCase(object):
    def execute(self,security_credentials,query_params):
        BeneficiarioRepository(username=security_credentials['username']).delete(query_params['cedula'])

class GetHistoriaMedicaUseCase(object):
    def execute(self,security_credentials,query_params):
        return HistoriaMedicaRepository(username=security_credentials['username']).getByCedula(query_params['cedula'])

class CreateMedicoUseCase(object):
    def execute(self,security_credentials,payload):
        MedicoRepository(username=security_credentials['username']).new(payload)

class SaveMedicoUseCase(object):
    def execute(self,security_credentials,payload):
        MedicoRepository(username=security_credentials['username']).save(payload)

class DeleteMedicoUseCase(object):
    def execute(self,security_credentials,query_params):
        MedicoRepository(username=security_credentials['username']).delete(query_params['cedula'])

class GetMedicoUseCase(object):
    def execute(self,security_credentials,query_params):
        return MedicoRepository(username=security_credentials['username']).getByCedula(query_params['cedula'])

class GetMedicoListUseCase(object):
    def execute(self,security_credentials):
        return MedicoRepository(username=security_credentials['username']).getAll()

class GetCitaUseCase(object):
    def execute(self,security_credentials,query_params):
        return CitaRepository(username=security_credentials['username']).getByCedula(query_params['cedula'])

class GetCitasMedicasListUseCase(object):
    def execute(self,security_credentials, query_params):
        return CitaRepository(username=security_credentials['username']).getByFechaCita(query_params['fechacita'])

class GetCitasMedicasPersonaListUseCase(object):
    def execute(self,security_credentials, query_params):
        return CitaRepository(username=security_credentials['username']).getCitasByCedula(query_params['cedula'])

class GetProximasCitasMedicasPersonaListUseCase(object):
    def execute(self,security_credentials, query_params):
        return CitaRepository(username=security_credentials['username']).getProximasCitasByCedula(query_params['cedula'])

class GetCitasDisponiblesListUseCase(object):
    def execute(self,security_credentials, query_params):
        return CitaRepository(username=security_credentials['username']).getFechasDisponibleByEspecialidad(query_params['codigoespecialidad'],query_params['fechainicio'],query_params['fechafin'])

class GetCitasCedulaEspecialidadFechaListUseCase(object):
    def execute(self,security_credentials, query_params):
        return CitaRepository(username=security_credentials['username']).getCitasByCedulaEspecialidadFecha(query_params['cedula'],query_params['codigoespecialidad'],query_params['fechacita'])

class CreateCitaMedicaUseCase(object):
    def execute(self,security_credentials,payload):
        CitaRepository(username=security_credentials['username']).new(payload)

class SaveCitaMedicaUseCase(object):
    def execute(self,security_credentials,payload):
        CitaRepository(username=security_credentials['username']).save(payload)

class GetCitaMedicaUseCase(object):
    def execute(self,security_credentials,query_params):
        return CitaRepository(username=security_credentials['username']).getById(query_params['id'])

class ConfirmCitaMedicaUseCase(object):
    def execute(self,security_credentials,payload):
        CitaRepository(username=security_credentials['username']).confirm(payload)

class DeleteCitaMedicaUseCase(object):
    def execute(self,security_credentials,query_params):
        CitaRepository(username=security_credentials['username']).cancelCita(query_params['idcita'])

class GetVisitasListUseCase(object):
    def execute(self,security_credentials, query_params):
        return VisitaRepository(username=security_credentials['username']).getByFechaVista(query_params['fechavisita'])

class CreateVisitaUseCase(object):
    def execute(self,security_credentials,payload):
        VisitaRepository(username=security_credentials['username']).new(payload)

class CreateConsultaMedicaUseCase(object):
    def execute(self,security_credentials,payload):
        ConsultaMedicaRepository(username=security_credentials['username']).new(payload)

class SaveConsultaMedicaUseCase(object):
    def execute(self,security_credentials,payload):
        ConsultaMedicaRepository(username=security_credentials['username']).save(payload)

class GetConsultasMedicasPersonaListUseCase(object):
    def execute(self,security_credentials, query_params):
        return ConsultaMedicaRepository(username=security_credentials['username']).getByCedula(query_params['cedula'])

class GetConsultaMedicaUseCase(object):
    def execute(self,security_credentials,query_params):
        return ConsultaMedicaRepository(username=security_credentials['username']).getById(query_params['id'])

class DeleteConsultaMedicaUseCase(object):
    def execute(self,security_credentials,query_params):
        ConsultaMedicaRepository(username=security_credentials['username']).delete(query_params['id'])
