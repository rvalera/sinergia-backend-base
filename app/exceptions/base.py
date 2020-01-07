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

class ProxyCredentialsNotFound(SinergiaException):
    def __init__(self,text=None):
        super(ConnectionException, self).__init__(code='ESIN002',text = text)    

