from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from Database.database import Base  

class User(Base):
    __tablename__ = "users" 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    
    resources = relationship("Resources", back_populates="owner", cascade="all, delete-orphan")
    models = relationship("Model", back_populates="owner", cascade="all, delete-orphan")  
    orchestrators = relationship("Orchestrator", back_populates="owner", cascade="all, delete-orphan")  


class Resources(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="resources")


class Model(Base):
    __tablename__ = "models"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  
    name = Column(String, unique=True, index=True)

    owner = relationship("User", back_populates="models")


class Orchestrator(Base):
    __tablename__ = "orchestrators"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  
    name = Column(String, unique=True, index=True)
    agent = Column(String)

    owner = relationship("User", back_populates="orchestrators")