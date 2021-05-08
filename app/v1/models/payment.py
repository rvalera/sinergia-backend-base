'''
Created on 17 dic. 2019

@author: ramon
'''
from app import db
from sqlalchemy import Column, Integer, String

class Bank(db.Model):
    __tablename__ = 'bank'
    __table_args__ = {'schema' : 'public'}

    id = Column(Integer, primary_key=True)
    name =  Column(String(150))
    status = Column(String(1))