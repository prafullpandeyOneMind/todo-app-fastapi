from pydantic import BaseModel
from typing import Optional
from datetime import datetime
# Schema for creating an item (request body validation)
class ItemCreate(BaseModel):
    name: str
    description: str


# Schema for returning an item (response format)
class ItemGet(ItemCreate):
    id: int  # Includes the auto-generated ID
    status: str | None
    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy model
        # model_cofig= True

class EmployeesGet(BaseModel):
    id: int
    user_id: int
    date_joined: datetime
    total_experience_in_months: Optional[int] = 0
    designation: Optional[str] = "Majdur"
    class Config:
        from_attributes = True
        

class EmployeeCreate(BaseModel):
    user_id: int
    date_joined: datetime
    total_experience_in_months: int
    designation: str


# Schema for updating an item (request body validation)
class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None

    class Config:
        from_attributes = True
class UserCreateRequest(BaseModel):
    name: str
    email: str
    first_name: str
    last_name: str
    role: str
    password: str
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: str
    password: str

class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str
      