from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db

app = FastAPI()

# USUARIOS
@app.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# MODELOS
@app.post("/users/{user_id}/models", response_model=schemas.ModelResponse)
def create_model_for_user(
    user_id: int, 
    model: schemas.ModelCreate, 
    db: Session = Depends(get_db)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return crud.create_model(db, model, user_id)

@app.get("/users/{user_id}/models", response_model=list[schemas.ModelResponse])
def read_user_models(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_models(db, user_id)

@app.get("/models/{model_id}", response_model=schemas.ModelResponse)
def read_model(model_id: int, db: Session = Depends(get_db)):
    model = crud.get_model(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    return model

#  ORQUESTADORES
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

@app.get("/orchestrators/{orchestrator_id}", response_model=schemas.OrchestratorResponse)
def read_orchestrator(orchestrator_id: int, db: Session = Depends(get_db)):
    orchestrator = crud.get_orchestrator(db, orchestrator_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Orquestador no encontrado")
    return orchestrator


# RECURSOS
@app.post("/users/{user_id}/resources", response_model=schemas.ResourceResponse)
def create_resource_for_user(
    user_id: int, 
    resource: schemas.ResourceCreate, 
    db: Session = Depends(get_db)
):
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
