from sqlalchemy import create_engine, Column,Table, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

import settings


DeclarativeBase = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))

def create_data_table(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine) 


class StudyModel(DeclarativeBase):
    """Sqlalchemy study model"""
    __tablename__ = 'study'
    id = Column(Integer, primary_key=True) 
    name = Column(String)
    description = Column(String)
    disciplines = relationship(
        'DisciplineModel',
        secondary='study_discipline'
    )

class DisciplineModel(DeclarativeBase): 
    __tablename__ = 'discipline'
    id = Column(Integer,primary_key=True)
    name = Column(String)
    studies = relationship(
        'StudyModel',
        secondary='study_discipline'
    )
    majors = relationship(
        'MajorModel',
        secondary='discipline_major'
    )
    
class MajorModel(DeclarativeBase):
    __tablename__ = 'major'
    id = Column(Integer,primary_key=True)
    name = Column(String)
    description = Column(String)
    disciplines = relationship(
        'DisciplineModel',
        secondary='discipline_major'
    )
    university_id = Column(
        Integer,
        ForeignKey('university.id')
    )
    university = relationship('UniversityModel')

class UniversityModel(DeclarativeBase):
    __tablename__ = 'university'
    id = Column(Integer,primary_key=True)
    abbrev = Column(String)
    name = Column(String)
    majors = relationship('MajorModel')

class ComCollegeModel(DeclarativeBase):
    __tablename__ = 'community_college'
    id = Column(Integer,primary_key=True)
    name = Column(String)

class StudyDisciplineModel(DeclarativeBase):
    __tablename__ = 'study_discipline'
    study_id = Column(
        Integer,
        ForeignKey('study.id'),
        primary_key=True
    )
    discipline_id = Column(
        Integer,
        ForeignKey('discipline.id'),
        primary_key=True
    )

class DisciplineMajorModel(DeclarativeBase):
    __tablename__ = 'discipline_major'
    discipline_id = Column(
        Integer,
        ForeignKey('discipline.id'),
        primary_key=True
    )
    major_id = Column(
        Integer,
        ForeignKey('major.id'),
        primary_key=True
    )

class ArticulationModel(DeclarativeBase):
    __tablename__ = 'articulation'
    major_id = Column(
        Integer,
        ForeignKey('major.id'),
        primary_key=True
    )
    community_college_id = Column(
        Integer,
        ForeignKey('community_college.id'),
        primary_key=True
    )
    major = relationship(
        'MajorModel',
        backref='articulations'
    )
    community_college = relationship(
        'ComCollegeModel',
        backref='articulations'
    )
    link = Column(String)






