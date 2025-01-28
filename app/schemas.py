from pydantic import BaseModel

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
        orm_mode = True
        # model_cofig= True

# Schema for updating an item (request body validation)
class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None

    class Config:
        from_attributes = True
        orm_mode = True
