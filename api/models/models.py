from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base  

class User(Base):
    __tablename__="User"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True,index=True)
    email = Column(String, unique=True,index=True)
    password = Column(String, index=True)

    resources = relationship("Resources", backref="owner", cascade="all, delete-orphan")
    model = relationship("Model", backref="owner", cascade="all, delete-orphan")
    orchestrator = relationship("Orchestrator", backref="owner",cascade= "all, delete-orphan") 



class Resources(Base):
    __tablename__="Resources"
    id = Column(Integer, primary_key=True, index=True)
    user_id_resources = Column(Integer, ForeignKey("User.id"), primary_key=True)
    nameResources= Column(String, unique=True, index=True)

class Model(Base):
    __tablename__="Model"
    id = Column(Integer, primary_key=True, index=True)
    user_id_model = Column(Integer, ForeignKey("User.id"), primary_key=True)
    nameModel = Column(String, unique=True, index=True)

class Orchestrator(Base):
    __tablename__="Orchestrator"
    id = Column(Integer, primary_key=True, index=True)
    user_id_orches = Column(Integer, ForeignKey("User.id"), primary_key=True)
    nameOrchestrator = Column(String, unique=True, index=True)
    agent = Column(String)


