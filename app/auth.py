import datetime
import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import USERS

SECRET_KEY = "hallpa_yaku_secret_key_demo"
ALGORITHM = "HS256"

security = HTTPBearer()

def create_access_token(email: str, role: str) -> str:
    payload = {
        "sub": email,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None or email not in USERS:
            raise HTTPException(status_code=401, detail="Invalid token or user not found")
        user = USERS[email]
        return {
            "email": user["email"],
            "name": user["name"],
            "name_en": user["name_en"],
            "role": user["role"]
        }
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def check_role(required_roles: list):
    def dependency(user: dict = Depends(get_current_user)):
        if user["role"] not in required_roles:
            raise HTTPException(status_code=403, detail="Operation not permitted for this role")
        return user
    return dependency
