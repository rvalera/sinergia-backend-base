'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.models.security import SecurityElement, User, PersonExtension
from app import redis_client, db
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from app.exceptions.base import CryptoPOSException, ConnectionException,NotImplementedException
from .base import SinergiaRepository

import pandas as pd

class CargoRepository(SinergiaRepository):

    # SQL: select * from integrador.cargos
    def getAll(self):
        table_df = pd.read_sql_table('cargos',schema='integrador',con=db.engine)
        result = table_df.to_dict('records')
        return result


