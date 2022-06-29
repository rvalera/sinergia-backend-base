'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.models.security import SecurityElement, User, PersonExtension
from app import redis_client, db, alembic
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from app.exceptions.base import CryptoPOSException, ConnectionException,NotImplementedException
from .base import BiostarClient, SinergiaRepository

from app.exceptions.base import RepositoryUnknownException,DataNotFoundException,ParametersNotFoundException

from app.v1.models.hr import Trabajador

import pandas as pd

from sqlalchemy.sql import text
from datetime import datetime, timedelta

from psycopg2 import OperationalError, errorcodes, errors     
from app.exceptions.base import DatabaseException,IntegrityException
from sqlalchemy import exc


class BiostarRepository(BiostarClient):

    def read_card(self,id_device_biostar):
        result = {}
        payload = {}

        result = self.executePost('/api/v1/entitites/dispositivos/scan_card/%s' % id_device_biostar, payload)
        return result

    def grant_access(self,payload):
        data = self.executePost('/api/v1/entitites/tarjeta/asignar', payload)
        return data

    def get_biostar_devices(self):
        query_params = {}
        data = self.executeGet('/api/v1/entitites/dispositivos' , query_params)
        return data
