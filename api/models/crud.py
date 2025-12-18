from sqlalchemy.orm import Session
from models import User,Model,Orchestrator,Resources
from schemas import UserCreate, ResourceCreate, ModelCreate, OrchestratorCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# USUARIOS
def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

# RECURSOS
def create_resource(db: Session, resource: ResourceCreate, user_id: int):
    db_resource = Resources(
        nameResources=resource.nameResources,
        user_id=user_id
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

def get_user_resources(db: Session, user_id: int):
    return db.query(Resources).filter(Resources.user_id == user_id).all()

def get_resource(db: Session, resource_id: int):
    return db.query(Resources).filter(Resources.id == resource_id).first()

def get_all_resources(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Resources).offset(skip).limit(limit).all()


# MODELOS
def create_model(db: Session, model: ModelCreate, user_id: int):
    db_model = Model(
        nameModel=model.nameModel,
        user_id_model=user_id
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

def get_user_models(db: Session, user_id: int):
    return db.query(Model).filter(Model.user_id_model == user_id).all()

def get_model(db: Session, model_id: int):
    return db.query(Model).filter(Model.id == model_id).first()

def get_all_models(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Model).offset(skip).limit(limit).all()

# ORQUESTADORES 
def create_orchestrator(db: Session, orchestrator: OrchestratorCreate, user_id: int):
    db_orchestrator = Orchestrator(
        nameOrchestrator=orchestrator.nameOrchestrator,
        agent=orchestrator.agent,
        user_id_orches=user_id
    )
    db.add(db_orchestrator)
    db.commit()
    db.refresh(db_orchestrator)
    return db_orchestrator

def get_user_orchestrators(db: Session, user_id: int):
    return db.query(Orchestrator).filter(Orchestrator.user_id_orches == user_id).all()

def get_orchestrator(db: Session, orchestrator_id: int):
    return db.query(Orchestrator).filter(Orchestrator.id == orchestrator_id).first()