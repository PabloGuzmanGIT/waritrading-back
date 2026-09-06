import datetime
import sys

import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db, settings, DEV_SECRET_KEY
from app import models

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

if SECRET_KEY == DEV_SECRET_KEY:
    print(
        "\n*** ADVERTENCIA: SECRET_KEY no configurada, usando clave de desarrollo. "
        "Setea SECRET_KEY como variable de entorno antes de producción. ***\n",
        file=sys.stderr,
    )

security = HTTPBearer()

def create_access_token(email: str, role: str) -> str:
    payload = {
        "sub": email,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(models.User).filter(models.User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
            
        return {
            "email": user.email,
            "name": user.name,
            "name_en": user.name_en,
            "role": user.role
        }
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def check_role(required_roles: list):
    def dependency(user: dict = Depends(get_current_user)):
        if user["role"] not in required_roles:
            raise HTTPException(status_code=403, detail="Operation not permitted for this role")
        return user
    return dependency
