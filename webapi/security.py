from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user_login")
SECRET_KEY = os.getenv("SECRET")  
ALGORITHM = os.getenv("ALGORITHM")

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
def authorize(token: str = Depends(oauth2_scheme)):
    return verify_token(token)