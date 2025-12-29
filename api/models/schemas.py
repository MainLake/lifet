from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime

# ========== TOKEN Y AUTENTICACIÓN ==========
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ========== USER ==========
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime] = None
    is_active: Optional[bool] = True
    
    # Para Pydantic v2 (reemplaza orm_mode)
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

# ========== RESOURCES ==========
class ResourceBase(BaseModel):
    nameResources: str

class ResourceCreate(ResourceBase):
    # user_id se obtiene del token o URL
    pass

class ResourceUpdate(BaseModel):
    nameResources: Optional[str] = None

class ResourceResponse(ResourceBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    owner: Optional["UserResponse"] = None
    
    model_config = ConfigDict(from_attributes=True)

# ========== MODEL ==========
class ModelBase(BaseModel):
    nameModel: str

class ModelCreate(ModelBase):
    pass  # user_id_model se obtiene del token

class ModelUpdate(BaseModel):
    nameModel: Optional[str] = None

class ModelResponse(ModelBase):
    id: int
    user_id_model: int
    created_at: Optional[datetime] = None
    owner: Optional["UserResponse"] = None
    
    model_config = ConfigDict(from_attributes=True)

# ========== ORCHESTRATOR ==========
class OrchestratorBase(BaseModel):
    nameOrchestrator: str  
    agent: str

class OrchestratorCreate(OrchestratorBase):
    pass  # user_id_orches se obtiene del token

class OrchestratorUpdate(BaseModel):
    nameOrchestrator: Optional[str] = None
    agent: Optional[str] = None

class OrchestratorResponse(OrchestratorBase):
    id: int
    user_id_orches: int
    created_at: Optional[datetime] = None
    owner: Optional["UserResponse"] = None
    
    model_config = ConfigDict(from_attributes=True)

# ========== RESPUESTAS CON RELACIONES ==========
class UserWithResources(UserResponse):
    resources: List[ResourceResponse] = []
    models: List[ModelResponse] = []
    orchestrators: List[OrchestratorResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# ========== RESPUESTAS PARA DASHBOARD ==========
class DashboardStats(BaseModel):
    total_resources: int
    total_models: int
    total_orchestrators: int
    last_created: Optional[datetime] = None

class UserDashboardResponse(BaseModel):
    user: UserResponse
    stats: DashboardStats
    recent_resources: List[ResourceResponse] = []
    recent_models: List[ModelResponse] = []
    recent_orchestrators: List[OrchestratorResponse] = []

# ========== RESPUESTAS PAGINADAS ==========
class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    size: int
    pages: int

# ========== VALIDACIÓN DE PASSWORD ==========
class PasswordChange(BaseModel):
    current_password: str
    new_password: str

# ========== RESOLUCIÓN DE REFERENCIAS CIRCULARES ==========
# Esto debe estar al final del archivo
UserResponse.update_forward_refs()
ResourceResponse.update_forward_refs()
ModelResponse.update_forward_refs()
OrchestratorResponse.update_forward_refs()
UserWithResources.update_forward_refs()

# ========== ALIAS PARA COMPATIBILIDAD ==========
# Si necesitas mantener orm_mode para código existente
def with_orm_mode():
    #Decorador para compatibilidad con orm_mode
    def decorator(cls):
        if not hasattr(cls, 'model_config'):
            cls.model_config = ConfigDict(from_attributes=True)
        return cls
    return decorator

