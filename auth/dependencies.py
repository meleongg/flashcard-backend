from fastapi import HTTPException, Header
from jose import JWTError, jwt
import os

SECRET_KEY = os.getenv("NEXTAUTH_SECRET")
ALGORITHM = "HS256"

async def get_current_user(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split("Bearer ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing user ID")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")