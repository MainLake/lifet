from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from Models import crud, schemas, auth
from Database.database import get_db
from Database.config import settings

app = FastAPI()

# CORS para conectar con React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Endpoint de salud que el frontend está buscando
@app.get("/api/health")
async def health_check():
    return JSONResponse(
        content={"status": "healthy", "message": "Backend is running"},
        status_code=200
    )

# También puedes agregar la ruta raíz para verificar
@app.get("/")
async def root():
    return {"message": "FastAPI Backend is running"}

# ========== AUTENTICACIÓN ==========
@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Verificar si el email ya existe
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    return crud.create_user(db, user)

@app.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": str(user.id)}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    return current_user

# ========== RUTAS PROTEGIDAS ==========
@app.post("/users/{user_id}/resources", response_model=schemas.ResourceResponse)
def create_resource_protected(
    user_id: int, 
    resource: schemas.ResourceCreate, 
    current_user: schemas.UserResponse = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar que el usuario solo cree recursos para sí mismo
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    return crud.create_resource(db, resource, user_id)

# ========== USUARIOS ==========
@app.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Verificar si el email ya existe
    existing_user = crud.get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    return crud.create_user(db, user)

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@app.get("/users", response_model=list[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

# ========== RECURSOS ==========
@app.post("/users/{user_id}/resources", response_model=schemas.ResourceResponse)
def create_resource_for_user(
    user_id: int, 
    resource: schemas.ResourceCreate, 
    db: Session = Depends(get_db)
):
    # Verificar que el usuario existe
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return crud.create_resource(db, resource, user_id)

@app.get("/users/{user_id}/resources", response_model=list[schemas.ResourceResponse])
def read_user_resources(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_resources(db, user_id)

@app.get("/resources", response_model=list[schemas.ResourceResponse])
def read_all_resources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all_resources(db, skip=skip, limit=limit)

@app.get("/resources/{resource_id}", response_model=schemas.ResourceResponse)
def read_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = crud.get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return resource

@app.delete("/resources/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = crud.delete_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return {"message": "Recurso eliminado correctamente"}

# ========== MODELOS ==========
@app.post("/users/{user_id}/models", response_model=schemas.ModelResponse)
def create_model_for_user(
    user_id: int, 
    model: schemas.ModelCreate, 
    db: Session = Depends(get_db)
):
    # Verificar que el usuario existe
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return crud.create_model(db, model, user_id)

@app.get("/users/{user_id}/models", response_model=list[schemas.ModelResponse])
def read_user_models(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_models(db, user_id)

@app.get("/models", response_model=list[schemas.ModelResponse])
def read_all_models(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all_models(db, skip=skip, limit=limit)

@app.get("/models/{model_id}", response_model=schemas.ModelResponse)
def read_model(model_id: int, db: Session = Depends(get_db)):
    model = crud.get_model(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    return model

@app.delete("/models/{model_id}")
def delete_model(model_id: int, db: Session = Depends(get_db)):
    model = crud.delete_model(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    return {"message": "Modelo eliminado correctamente"}

# ========== ORQUESTADORES ==========
@app.post("/users/{user_id}/orchestrators", response_model=schemas.OrchestratorResponse)
def create_orchestrator_for_user(
    user_id: int, 
    orchestrator: schemas.OrchestratorCreate, 
    db: Session = Depends(get_db)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return crud.create_orchestrator(db, orchestrator, user_id)

@app.get("/users/{user_id}/orchestrators", response_model=list[schemas.OrchestratorResponse])
def read_user_orchestrators(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_orchestrators(db, user_id)

@app.get("/orchestrators", response_model=list[schemas.OrchestratorResponse])
def read_all_orchestrators(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all_orchestrators(db, skip=skip, limit=limit)

@app.get("/orchestrators/{orchestrator_id}", response_model=schemas.OrchestratorResponse)
def read_orchestrator(orchestrator_id: int, db: Session = Depends(get_db)):
    orchestrator = crud.get_orchestrator(db, orchestrator_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Orquestador no encontrado")
    return orchestrator

@app.delete("/orchestrators/{orchestrator_id}")
def delete_orchestrator(orchestrator_id: int, db: Session = Depends(get_db)):
    orchestrator = crud.delete_orchestrator(db, orchestrator_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Orquestador no encontrado")
    return {"message": "Orquestador eliminado correctamente"}

# ========== ACTUALIZACIONES (PUT/PATCH) ==========
@app.put("/models/{model_id}", response_model=schemas.ModelResponse)
def update_model(
    model_id: int, 
    model_update: schemas.ModelUpdate, 
    db: Session = Depends(get_db)
):
    updated_model = crud.update_model(db, model_id, model_update)
    if not updated_model:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    return updated_model

@app.put("/orchestrators/{orchestrator_id}", response_model=schemas.OrchestratorResponse)
def update_orchestrator(
    orchestrator_id: int, 
    orchestrator_update: schemas.OrchestratorUpdate, 
    db: Session = Depends(get_db)
):
    updated_orchestrator = crud.update_orchestrator(db, orchestrator_id, orchestrator_update)
    if not updated_orchestrator:
        raise HTTPException(status_code=404, detail="Orquestador no encontrado")
    return updated_orchestrator

@app.put("/resources/{resource_id}", response_model=schemas.ResourceResponse)
def update_resource(
    resource_id: int, 
    resource_update: schemas.ResourceUpdate, 
    db: Session = Depends(get_db)
):
    updated_resource = crud.update_resource(db, resource_id, resource_update)
    if not updated_resource:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return updated_resource

# ========== RUTAS PÚBLICAS ==========
@app.get("/")
def read_root():
    return {"message": "API con autenticación JWT"}

@app.get("/public/models")
def get_public_models(db: Session = Depends(get_db)):
    # Ejemplo de ruta pública
    return crud.get_all_models(db, limit=10)

