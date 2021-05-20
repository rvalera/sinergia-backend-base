'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.repository.entities import CargoRepository,CentroCostoRepository,ConceptoNominaRepository,DispositivoRepository,\
    EstatusTrabajadorRepository,TipoAusenciaRepository,TipoNominaRepository,TrabajadorRepository

class GetCargoListUseCase(object):
    def execute(self,security_credentials,query_params):
        return CargoRepository(username=security_credentials['username']).get(query_params)

class GetCentroCostoListUseCase(object):
    def execute(self,security_credentials,query_params):
        return CentroCostoRepository(username=security_credentials['username']).get(query_params)

class GetConceptoNominaListUseCase(object):
    def execute(self,security_credentials,query_params):
        return ConceptoNominaRepository(username=security_credentials['username']).get(query_params)


class GetDispositivoListUseCase(object):
    def execute(self,security_credentials):
        return DispositivoRepository(username=security_credentials['username']).getAll()

class GetEstatusTrabajadorListUseCase(object):
    def execute(self,security_credentials):
        return TrabajadorRepository(username=security_credentials['username']).getAll()

class GetTipoAusenciaListUseCase(object):
    def execute(self,security_credentials):
        return TipoAusenciaRepository(username=security_credentials['username']).getAll()

class GetTipoNominaListUseCase(object):
    def execute(self,security_credentials):
        return TipoNominaRepository(username=security_credentials['username']).getAll()

class GetTrabajadorListUseCase(object):
    def execute(self,security_credentials,query_params):
        return TrabajadorRepository(username=security_credentials['username']).get(query_params)

class GetTrabajadorUseCase(object):
    def execute(self,security_credentials,query_params):
        return TrabajadorRepository(username=security_credentials['username']).getByCedula(query_params['cedula'])