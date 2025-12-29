from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
#from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from Models import crud, models, schemas
from Database.database import get_db
from Database.config import settings

# Configuración de hash de contraseñas
#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Funciones de hash
#def verify_password(plain_password, hashed_password):
 #   return pwd_context.verify(plain_password, hashed_password)

#def get_password_hash(password):
 #   return pwd_context.hash(password)

# Funciones de JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Autenticación de usuario
def authenticate_user(db: Session, email: str, password: str):
    user = crud.get_user_by_email(db, email)
    if not user:
        return False
    if password != user.password:
        return False
    return user



# Obtener usuario actual desde token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    return user

# Verificar si usuario es admin (si necesitas roles)
async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:  # Si añades este campo
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user

