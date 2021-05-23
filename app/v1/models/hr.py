'''
Created on 17 dic. 2019

@author: ramon
'''
from app import db
from flask_sqlalchemy.model import Model
from sqlalchemy import Table, Column, ForeignKey, Integer, String, Float, Boolean, DateTime, Text, Date
from sqlalchemy.orm import relationship, backref

class CentroCosto(db.Model):
    __tablename__ = 'centro_costo'
    __table_args__ = {'schema' : 'integrador'}

    codigo = Column(String(20), primary_key=True)
    descripcion = Column(String(100)) 
    estatus = Column(String(1)) 

class Cargo(db.Model):
    __tablename__ = 'cargos'
    __table_args__ = {'schema' : 'integrador'}

    codigo = Column(String(15), primary_key=True)
    descripcion = Column(String(80)) 
    codigo_rrhh = Column(String(15))

class TipoNomina(db.Model):
    __tablename__ = 'tipos_de_nomina'
    __table_args__ = {'schema' : 'integrador'}

    codigo = Column(String(10), primary_key=True)
    descripcion = Column(String(80)) 
    cantidad_de_horas = Column(Integer()) 
    tipo_sueldo = Column(String(2)) 
    nro_de_dias = Column(Integer()) 
    status = Column(Integer()) 

class EstatusTrabajador(db.Model):
    __tablename__ = 'estatus_trabajador'
    __table_args__ = {'schema' : 'integrador'}

    codigo = Column(String(20), primary_key=True)
    descripcion = Column(String(100)) 

class TipoAusencia(db.Model):
    __tablename__ = 'tipos_ausencias'
    __table_args__ = {'schema' : 'integrador'}

    codigo = Column(Integer(), primary_key=True)
    descripcion = Column(String(200)) 

class TipoTrabajador(db.Model):
    __tablename__ = 'tipo_trabajador'
    __table_args__ = {'schema' : 'integrador'}

    codigo = Column(String(20), primary_key=True)
    descripcion = Column(String(150)) 

class GrupoGuardia(db.Model):
    __tablename__ = 'grupo_guardia'
    __table_args__ = {'schema' : 'integrador'}

    codigo = Column(String(10), primary_key=True)
    descripcion = Column(String(150)) 
    cndtra = Column(String(10)) 

    rotacion = Column(Integer()) 
    origen = Column(Integer()) 
    status = Column(Integer()) 

class Trabajador(db.Model):
    __tablename__ = 'trabajadores'
    __table_args__ = {'schema' : 'integrador'}

    cedula = Column(Integer(), primary_key=True) 
    codigo = Column(String(50))
    nombres = Column(String(80))
    apellidos = Column(String(80)) 
    sexo = Column(String(2)) 
    fecha_ingreso = Column(Date()) 
    fecha_egreso = Column(Date()) 

    id_cargo = Column('cargo',String(15), ForeignKey('integrador.cargos.codigo'))
    cargo = relationship("Cargo")

    id_centro_costo = Column('centro_costo',String(20), ForeignKey('integrador.centro_costo.codigo'))
    centro_costo = relationship("CentroCosto")

    id_tipo_nomina = Column('tipo_nomina',String(10), ForeignKey('integrador.tipos_de_nomina.codigo'))
    tipo_nomina = relationship("TipoNomina")

    id_status_actual = Column('status_actual',String(10),ForeignKey('integrador.estatus_trabajador.codigo'))
    status_actual = relationship("EstatusTrabajador")

    id_tipo_trabajador = Column('tipo_de_trabajador',String(20), ForeignKey('integrador.tipo_trabajador.codigo'))
    tipo_trabajador = relationship("TipoTabajador")

    id_grupo_guardia = Column('grupo_guardia',String(10), ForeignKey('integrador.grupo_guardia.codigo'))
    tipo_trabajador = relationship("GrupoGuardia")
    
    id_tarjeta = Column(Integer()) 
    telefono = Column(String(50))
    correo = Column(String(150))
