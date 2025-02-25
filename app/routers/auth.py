from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User
from app.schemas import UserCreateRequest, LoginRequest, AccessTokenResponse
from app.database import get_db
from app.utils import authenticate_user,auth_dependency
from passlib.context import CryptContext
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from passlib.context import CryptContext
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(
    prefix="/auth",
    tags=["Auth"]

)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_request: UserCreateRequest, db: AsyncSession = Depends(get_db)):
    user_created = User(
        name=user_request.name,
        email=user_request.email,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        role=user_request.role,
        hashed_password=bcrypt_context.hash(user_request.password),
        is_active=True
    )
    db.add(user_created)
    await db.commit()



@router.post("/login", status_code=200, response_model=AccessTokenResponse)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_db)):
    access_token = await authenticate_user(form_data.username, form_data.password, db)
    if not access_token:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.patch("/update-password", status_code=200)
async def update_password(form_data: dict, user: auth_dependency, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == user["email"])
    result = await db.execute(query)
    db_user = result.scalars().first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.hashed_password = bcrypt_context.hash(form_data["password"])
    await db.commit()
    return db_user



