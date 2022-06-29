from flask_babel import gettext

class SinergiaException(Exception):
    def __init__(self, code = 'ESIN001', text=None, *args, **kwargs):
        super().__init__(args, **kwargs) 
        self.code = code
        if text == None:
            i18_text = gettext(self.code)
            self.text = i18_text if i18_text != self.code else 'Unknown Error'
        else:
            self.text = text

class ConnectionException(SinergiaException):
    def __init__(self,text=None):
        super(ConnectionException, self).__init__(code='EHTTP001',text = text)
        
class CryptoPOSException(SinergiaException):
    def __init__(self, text=None):
        super(CryptoPOSException, self).__init__(code='EPOS001',text = text)

class BiostartException(SinergiaException):
    def __init__(self, text=None):
        super(BiostartException, self).__init__(code='BIOS001',text = text)

class ProxyCredentialsNotFound(SinergiaException):
    def __init__(self,text=None):
        super(ProxyCredentialsNotFound, self).__init__(code='ESIN002',text = text)    

class NotImplementedException(SinergiaException):
    def __init__(self,text=None):
        super(NotImplementedException, self).__init__(code='NOTIMP001',text = text)

class UserCurrentPasswordException(SinergiaException):
    def __init__(self,text=None):
        super(UserCurrentPasswordException, self).__init__(code='USRPWD001',text = text)

class UserRepeatedPasswordException(SinergiaException):
    def __init__(self,text=None):
        super(UserRepeatedPasswordException, self).__init__(code='USRPWD002',text = text)

class IntegrityException(SinergiaException):
    def __init__(self,text=None):
        super(IntegrityException, self).__init__(code='INT001',text = text)

class DatabaseException(SinergiaException):
    def __init__(self,text=None):
        super(DatabaseException, self).__init__(code='DB001',text = text)

class DataNotFoundException(SinergiaException):
    def __init__(self,text=None):
        super(DataNotFoundException, self).__init__(code='DAT001',text = text)

class DataAlreadyRegisteredException(SinergiaException):
    def __init__(self,text=None):
        super(DataAlreadyRegisteredException, self).__init__(code='DAT003',text = text)

class DeleteDataException(SinergiaException):
    def __init__(self,text=None):
        super(DeleteDataException, self).__init__(code='DAT002',text = text)

class ParametersNotFoundException(SinergiaException):
    def __init__(self,text=None):
        super(ParametersNotFoundException, self).__init__(code='PAR001',text = text)

class RepositoryUnknownException(SinergiaException):
    def __init__(self,text=None):
        super(RepositoryUnknownException, self).__init__(code='REP001',text = text)

class RESTClientException(SinergiaException):
    def __init__(self, text=None):
        super(RESTClientException, self).__init__(code='AIR001',text = text)



## =============================================================================================================================
## ================================                  CVG EXCEPTIONS               ==============================================
## =============================================================================================================================

class CitaFechaInvalidaException(SinergiaException):
    def __init__(self, text=None):
        super(CitaFechaInvalidaException, self).__init__(code='CIT001',text = text)

class CitaFechaSinCupoException(SinergiaException):
    def __init__(self, text=None):
        super(CitaFechaSinCupoException, self).__init__(code='CIT002',text = text)

class CitaException(SinergiaException):
    def __init__(self, text=None):
        super(CitaException, self).__init__(code='CIT003',text = text)

class CitaConConsultaException(SinergiaException):
    def __init__(self, text=None):
        super(CitaConConsultaException, self).__init__(code='CIT004',text = text)

class CitaPersonaEquivocadaException(SinergiaException):
    def __init__(self, text=None):
        super(CitaPersonaEquivocadaException, self).__init__(code='CIT005',text = text)

class PacienteConCitaException(SinergiaException):
    def __init__(self, text=None):
        super(PacienteConCitaException, self).__init__(code='CIT006',text = text)

class ColaEspecialidadDetenidaException(SinergiaException):
    def __init__(self, text=None):
        super(ColaEspecialidadDetenidaException, self).__init__(code='ESP001',text = text)








