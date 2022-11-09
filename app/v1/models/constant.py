'''
Created on 17 dic. 2019

@author: ramon
'''
from app.tools.config import load_configuration_file

configuration = load_configuration_file()

STATUS_PENDING     = 'P' # Pending
STATUS_GENERATED   = 'G' # Generated
STATUS_ACTIVE      = 'A' # Active
STATUS_LOCKED      = 'L' # Locked
STATUS_REPLACED    = 'R' # Replaced

#User Types
CONSOLE_USER = 'C'
MOBILE_USER = 'M'

#User Source
FROM_BACKOFFICE = 'B'
AUTOREGISTER = 'A'


#Basic Responses
YES = 'Y' # Yes
NO  = 'N' # No

#Custom Privileges
PRIV_MAKE_PAYMENT = 'PAY'
PRIV_MAKE_REFILL = 'REF'
PRIV_LOCK = 'LOCK'
PRIV_UNLOCK = 'UNLOC'
PRIV_ACTIVATION = 'ACTIV'
PRIV_MAKE_TRANSFER = 'TRANS'
PRIV_MAKE_REVERSE = 'REV'


#Estados de Citas Medicas
CITA_PLANIFICADA = 'PLANIFICADA'
CITA_CANCELADA = 'CANCELADA'
CITA_CONFIRMADA = 'CONFIRMADA'
CITA_EN_COLA = 'EN COLA'
CITA_EN_ATENCION = 'EN ATENCION'
CITA_CONCLUIDA = 'CONCLUIDA'