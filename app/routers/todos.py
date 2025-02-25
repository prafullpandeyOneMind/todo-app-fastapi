from fastapi import  Depends, HTTPException, APIRouter

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from   app.schemas import *
from app.database import get_db
from app.models import TodoItem
from app.utils import auth_dependency
router = APIRouter()

# Create an item
@router.post("/items/", response_model=ItemGet)
async def create_item(
    user: auth_dependency,
    item: ItemCreate,  # Validates the request body using ItemCreate
    db: AsyncSession = Depends(get_db)  # Injects the database session
):
    print("The user Logged in is known as : ",user)
    db_item = TodoItem(**item.model_dump())  # Convert Pydantic model to SQLAlchemy model
    db.add(db_item)  # Add to session
    await db.commit()  # Save to database
    await db.refresh(db_item)  # Refresh to get the auto-generated ID
    return db_item  # Return the item (converted to JSON via schemas.Item)


# Get an item by ID
@router.get("/items", response_model=list[ItemGet])
async def read_item(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(TodoItem))
    items = result.scalars().all()  # Fetch all items
    return [ItemGet.model_validate(item) for item in items]

@router.delete("/items/delete/{item_id}")
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    db_item = await db.get(TodoItem, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    await db.delete(db_item)
    await db.commit()
    return {"message": "Item deleted"}

@router.patch("/items/update/{item_id}")
async def update_item(
    item_id: int,
    item: ItemUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_item = await db.get(TodoItem, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.status is not None:
        db_item.status = item.status
    if item.name is not None:
        db_item.name = item.name
    if item.description is not None:
        db_item.description = item.description

    await db.commit()
    return db_item


@router.get("/items/{item_id}", response_model=ItemGet)
async def read_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    db_item = await db.get(TodoItem, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item



