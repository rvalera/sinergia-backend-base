'''
Created on 17 dic. 2019

@author: ramon
'''
from app.v1.models.security import SecurityElement, User, PersonExtension, Rol
from app.v1.models.hr import Trabajador,CentroCosto
from app.v1.models.constant import *

from app import redis_client, db, alembic
from app.exceptions.base import UserCurrentPasswordException,UserRepeatedPasswordException,RepositoryUnknownException
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from app.exceptions.base import CryptoPOSException, ConnectionException,NotImplementedException,DatabaseException,IntegrityException
from .base import SinergiaRepository

import pandas as pd
import hashlib
import datetime
from sqlalchemy.sql import text

from sqlalchemy import exc


class ApplicationRepository(SinergiaRepository):

    def get(self):
        sql = '''
        SELECT  *
        FROM integrador.parametros 
        '''

        try:
            table_df = pd.read_sql_query(sql,con=db.engine)
            rows = table_df.to_dict('records')
            row = rows[0] if len(rows) > 0 else None
            return  row
        except exc.IntegrityError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise IntegrityException(text=error_description)
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

    def save(self,payload):
        try:
            conn = alembic.op.get_bind()
            conn.execute(
                text(
                    """
                        UPDATE integrador.parametros
                        SET 
                        semanas_de_ajustes = :semanas_de_ajustes
                    """
                ), 
                **payload
            )
        except exc.IntegrityError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise IntegrityException(text=error_description)
        except exc.DatabaseError as err:
            # pass exception to function
            error_description = '%s' % (err)
            raise DatabaseException(text=error_description)

