from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# USER
class UserBase(BaseModel):
    name: str
    email: EmailStr  # Validación de email

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime] = None
    # resources: List["ResourceResponse"] = []  # Opcional
    
    class Config:
        orm_mode = True

# RESOURCES
class ResourceBase(BaseModel):
    nameResources: str

class ResourceCreate(ResourceBase):
    user_id: int  

class ResourceResponse(ResourceBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    owner: Optional[UserResponse] = None  # Incluye info del usuario
    
    class Config:
        orm_mode = True

# MODEL
class ModelBase(BaseModel):
    nameModel: str  # Manteniendo el nombre del campo

class ModelCreate(ModelBase):
    # user_id se obtendrá de la URL o del token JWT
    pass

class ModelResponse(ModelBase):
    id: int
    user_id_model: int
    owner: Optional[UserResponse] = None  # Info del dueño
    
    class Config:
        orm_mode = True

# ORCHESTRATOR
class OrchestratorBase(BaseModel):
    nameOrchestrator: str  
    agent: str

class OrchestratorCreate(OrchestratorBase):
    pass  # user_id_orches se obtiene del contexto

class OrchestratorResponse(OrchestratorBase):
    id: int
    user_id_orches: int
    owner: Optional[UserResponse] = None
    
    class Config:
        orm_mode = True

# Para evitar referencias circulares
UserResponse.update_forward_refs()
