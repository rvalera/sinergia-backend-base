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

    historiamedica = relationship("HistoriaMedica", back_populates="persona", uselist=False)

    discriminator = Column(String)

    __mapper_args__ = {
        'polymorphic_identity':'persona',
        'polymorphic_on':discriminator,
    }      


class Trabajador(Persona):
    __tablename__ = 'trabajador'
    __table_args__ = {'schema' : 'hospitalario'}
    cedula = Column(String(12), ForeignKey('hospitalario.persona.cedula'), primary_key=True)

    jornada = Column(String(100))
    ingreso = Column(Date()) 

    situacion = Column(String(100))
    condicion = Column(String(100))

    camisa = Column(String(5))
    pantalon = Column(String(5))
    calzado = Column(String(5))

    ficha = Column(String(12))

    suspendido = Column(String(10)) 

    personal = Column(String(100))
    tiponomina = Column(String(100))
    ubicacionlaboral = Column(String(100))
    cargo = Column(String(100))

    observaciones = Column(String())
    fechaactualizacion = Column(DateTime()) 

    idusuarioactualizacion = Column('idusuarioactualizacion',Integer(), ForeignKey('public.user.id'))
    usuarioactualizacion = relationship("User")

    codigoempresa = Column('codigoempresa',String(10), ForeignKey('hospitalario.empresa.codigo'))
    empresa = relationship("Empresa")

    beneficiarios = relationship('Beneficiario', primaryjoin="and_(Trabajador.cedula==Beneficiario.cedulatrabajador)")

    __mapper_args__ = {
        'polymorphic_identity':'trabajador'
    }


class Beneficiario(Persona):
    __tablename__ = 'beneficiario'
    __table_args__ = {'schema' : 'hospitalario'}
    cedula = Column(String(12), ForeignKey('hospitalario.persona.cedula'), primary_key=True)
    vinculo = Column(String(100))
    
    cedulatrabajador = Column('cedulatrabajador',String(12), ForeignKey('hospitalario.trabajador.cedula'))
    trabajador = relationship("Trabajador", foreign_keys=[cedulatrabajador])

    __mapper_args__ = {
        'polymorphic_identity':'beneficiario'
    }

#patologia_historiamedica_table = Table('hospitalario.patologiahistoriamedica', db.Model.metadata, 
#    Column('cedula', String, ForeignKey('hospitalario.historiamedica.cedula')),
#    Column('codigopatologia', String, ForeignKey('hospitalario.patologia.codigopatologia'))
#)


class Discapacidad(db.Model):
    __tablename__ = 'discapacidad'
    __table_args__ = {'schema' : 'hospitalario'}

    codigodiscapacidad = Column(String(12), primary_key=True)
    nombre = Column(String(100)) 


class DiscapacidadHistoriaMedica(db.Model):
    __tablename__ = 'discapacidadhistoriamedica'
    __table_args__ = {'schema' : 'hospitalario'}
    cedula = Column(String(12), ForeignKey('hospitalario.historiamedica.cedula'), primary_key = True)
    codigodiscapacidad = Column(String(12), ForeignKey('hospitalario.discapacidad.codigodiscapacidad'), primary_key = True)


class PatologiaHistoriaMedica(db.Model):
    __tablename__ = 'patologiahistoriamedica'
    __table_args__ = {'schema' : 'hospitalario'}
    cedula = Column(String(12), ForeignKey('hospitalario.historiamedica.cedula'), primary_key = True)
    codigopatologia = Column(String(12), ForeignKey('hospitalario.patologia.codigopatologia'), primary_key = True)

    
class Patologia(db.Model):
    __tablename__ = 'patologia'
    __table_args__ = {'schema' : 'hospitalario'}

    codigopatologia = Column(String(12), primary_key=True)
    nombre = Column(String(100)) 


class HistoriaMedica(db.Model):
    __tablename__ = 'historiamedica'
    __table_args__ = {'schema' : 'hospitalario'}

    cedula = Column(String(12), ForeignKey('hospitalario.persona.cedula'), primary_key=True)
    persona = relationship("Persona")
    gruposanguineo = Column(String(12))
    #discapacidad = Column(String(10)) 
    fecha = Column(Date()) 

    #patologias = relationship("Patologia", secondary=patologia_historiamedica_table, cascade="save-update")          
    patologias = relationship("Patologia", secondary='hospitalario.patologiahistoriamedica')          
    discapacidades = relationship("Discapacidad", secondary='hospitalario.discapacidadhistoriamedica')          


class Especialidad(db.Model):
    __tablename__ = 'especialidad'
    __table_args__ = {'schema' : 'hospitalario'}

    codigoespecialidad = Column(String(12), primary_key=True)
    nombre = Column(String(100))
    autogestionada = Column(Boolean)
    diasdeatencion = Column(String(100))
    cantidadmaximapacientes = Column(Integer)


class Cita(db.Model):
    __tablename__ = 'cita'
    __table_args__ = {'schema' : 'hospitalario'}

    id = Column(Integer, primary_key=True)
    cedula = Column(String(12), ForeignKey('hospitalario.persona.cedula'))
    persona = relationship("Persona")
    codigoespecialidad = Column(String(12), ForeignKey('hospitalario.especialidad.codigoespecialidad'))
    especialidad = relationship("Especialidad")

    fechadia = Column(DateTime()) 
    fechacita = Column(DateTime()) 
    fechaentradacola = Column(DateTime()) 
    fechapasaconsulta = Column(DateTime()) 
    fechafinconsulta = Column(DateTime()) 
    idbiostar = Column(String(100))
    estado = Column(String(50))
    
                          