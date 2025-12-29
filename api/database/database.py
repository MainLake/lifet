from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import Depends


DATABASE_URL = "postgresql://postgres:041130@localhost:5432/orquestador"

engine = create_engine(DATABASE_URL)
sessionMLocal = sessionmaker(autocommit=False, autoflush= False, bind=engine)

Base = declarative_base()

def get_db():
    db = sessionMLocal()
    try: 
        yield db
    finally:
        db.close
        