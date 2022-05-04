'''
Created on 17 dic. 2019

@author: ramon
'''
from app import db
from flask_sqlalchemy.model import Model
from sqlalchemy import Table, Column, ForeignKey, Integer, String, Float, Boolean, DateTime, Text, Date
from sqlalchemy.orm import relationship, backref

class TipoTrabajador(db.Model):
    __tablename__ = 'tipotrabajador'
    __table_args__ = {'schema' : 'hospitalario'}

    codigo = Column(String(10), primary_key=True)
    nombre = Column(String(100)) 

class EstatusTrabajador(db.Model):
    __tablename__ = 'estatustrabajador'
    __table_args__ = {'schema' : 'hospitalario'}

    codigo = Column(String(10), primary_key=True)
    nombre = Column(String(100)) 

class TipoNomina(db.Model):
    __tablename__ = 'tiponomina'
    __table_args__ = {'schema' : 'hospitalario'}

    codigo = Column(String(10), primary_key=True)
    nombre = Column(String(100)) 

class TipoCargo(db.Model):
    __tablename__ = 'tipocargo'
    __table_args__ = {'schema' : 'hospitalario'}

    codigo = Column(String(10), primary_key=True)
    nombre = Column(String(100)) 

class UbicacionLaboral(db.Model):
    __tablename__ = 'ubicacionlaboral'
    __table_args__ = {'schema' : 'hospitalario'}

    codigo = Column(String(10), primary_key=True)
    nombre = Column(String(100)) 

class Empresa(db.Model):
    __tablename__ = 'empresa'
    __table_args__ = {'schema' : 'hospitalario'}

    codigo = Column(String(10), primary_key=True)
    nombre = Column(String(100)) 


class Estado(db.Model):
    __tablename__ = 'estado'
    __table_args__ = {'schema' : 'hospitalario'}

    codigo = Column(String(10), primary_key=True)
    nombre = Column(String(100)) 

class Municipio(db.Model):
    __tablename__ = 'municipio'
    __table_args__ = {'schema' : 'hospitalario'}

    codigo = Column(String(10), primary_key=True)
    nombre = Column(String(100)) 

class Persona(db.Model):
    __tablename__ = 'persona'
    __table_args__ = {'schema' : 'hospitalario'}

    cedula = Column(String(12), primary_key=True) 
    nombres = Column(String(100))
    apellidos = Column(String(100)) 
    nacionalidad = Column(String(1)) 
    fechanacimiento = Column(Date()) 
    sexo = Column(String(1)) 

    nivel = Column(String(100))
    profesion = Column(String(100)) 

    telefonocelular = Column(String(12))
    telefonoresidencia = Column(String(12)) 
    correo = Column(String(100))

    codigoestado = Column('codigoestado',String(10), ForeignKey('hospitalario.estado.codigo'))
    estado = relationship("Estado")

    codigomunicipio = Column('codigomunicipio',String(10), ForeignKey('hospitalario.municipio.codigo'))
    municipio = relationship("Municipio")

    parroquia = Column(String(100))
    sector = Column(String(100))
    avenidacalle = Column(String(100))
    edifcasa = Column(String(100))

    discriminator = Column(String)

    __mapper_args__ = {
        'polymorphic_on':'discriminator',
    }      


class Trabajador(Persona):
    __tablename__ = 'trabajador'
    __table_args__ = {'schema' : 'hospitalario'}
    cedula = Column(Integer, ForeignKey('hospitalario.persona.cedula'), primary_key=True)

    jornada = Column(String(100))
    ingreso = Column(Date()) 

    situacion = Column(String(100))
    condicion = Column(String(100))

    camisa = Column(String(5))
    pantalon = Column(String(5))
    calzado = Column(String(4))

    ficha = Column(String(12))

    suspendido = Column(String(10)) 

    personal = Column(String(100))
    tiponomina = Column(String(100))
    ubicacionlaboral = Column(String(100))
    cargo = Column(String(100))

    observaciones = Column(String())
    fechaactualizacion = Column(DateTime()) 

    idusuarioactualizacion = Column('idusuarioactualizacion',String(10), ForeignKey('public.user.id'))
    # usuario = relationship("Usuario")


    # codigotipotrabajador = Column('codigotipotrabajador',String(10), ForeignKey('hospitalario.tipotrabajador.codigo'))
    # tipotrabajador = relationship("TipoTrabajador")

    # codigotiponomina = Column('codigotiponomina',String(10), ForeignKey('hospitalario.tiponomina.codigo'))
    # tiponomina = relationship("TipoNomina")

    # codigoestatustrabajador = Column('codigoestatustrabajador',String(10), ForeignKey('hospitalario.estatustrabajador.codigo'))
    # estatustrabajador = relationship("EstatusTrabajador")

    # codigoubicacionlaboral = Column('ubicacionlaboral',String(10), ForeignKey('hospitalario.ubicacionlaboral.codigo'))
    # ubicacionlaboral = relationship("UbicacionLaboral")

    # codigotipocargo = Column('codigotipocargo',String(10), ForeignKey('hospitalario.tipocargo.codigo'))
    # tipocargo = relationship("TipoCargo")

    codigoempresa = Column('codigoempresa',String(10), ForeignKey('hospitalario.empresa.codigo'))
    empresa = relationship("Empresa")

    __mapper_args__ = {
        'polymorphic_identity':'trabajador'
    }

