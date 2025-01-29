from jose import jwt,JWTError
from datetime import datetime,timedelta,timezone
from app.config import settings
from app.models import User
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from starlette import status
from fastapi import HTTPException
from typing import Annotated
from fastapi import Depends
from fastapi.security import  OAuth2PasswordBearer

oauth_2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def create_access_token(data: dict,expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode,settings.JWT_SECRET_KEY,algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: Annotated[str, Depends(oauth_2_bearer)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        name: str = payload.get("name")
        if email is None:
            raise credentials_exception
        return {"email": email, "name": name}
    except JWTError:
        return credentials_exception
    
async def authenticate_user(email:str,password:str,db: AsyncSession):
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalars().first()
    if user is None:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    access_token = create_access_token(
        data={"sub": user.email, "name": user.name},
        expires_delta=timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES) )
    )
    return access_token

auth_dependency = Annotated[dict, Depends(get_current_user)]


