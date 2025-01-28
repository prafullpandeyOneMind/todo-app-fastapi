from fastapi import FastAPI, Depends, HTTPException
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session
from sqlalchemy.future import select
from contextlib import asynccontextmanager
from . import models, schemas
from .database import get_db, engine
from .models import TodoItem

# Modern lifespan handler (replaces startup/shutdown events)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code before yield runs ON STARTUP
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield  # App runs here
    # Code after yield runs ON SHUTDOWN
    await engine.dispose()  # Clean up connections

app = FastAPI(lifespan=lifespan)

# Create an item
@app.post("/items/", response_model=schemas.ItemGet)
async def create_item(
    item: schemas.ItemCreate,  # Validates the request body using ItemCreate
    db: AsyncSession = Depends(get_db)  # Injects the database session
):
    db_item = TodoItem(**item.model_dump())  # Convert Pydantic model to SQLAlchemy model
    db.add(db_item)  # Add to session
    await db.commit()  # Save to database
    await db.refresh(db_item)  # Refresh to get the auto-generated ID
    return db_item  # Return the item (converted to JSON via schemas.Item)



# Get an item by ID
@app.get("/items", response_model=list[schemas.ItemGet])
async def read_item(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(TodoItem))
    items = result.scalars().all()  # Fetch all items
    return [schemas.ItemGet.model_validate(item) for item in items]

@app.delete("/items/delete/{item_id}")
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

@app.patch("/items/update/{item_id}")
async def update_item(
    item_id: int,
    item: schemas.ItemUpdate,
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


@app.get("/items/{item_id}", response_model=schemas.ItemGet)
async def read_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    db_item = await db.get(TodoItem, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item





# class ModelName(str, Enum):
#     alexnet = "alexnet"
#     resnet = "resnet"
#     lenet = "lenet"


# # app = FastAPI()


# @app.get("/models/{model_name}")
# async def get_model(model_name: ModelName):

#     print("This is going to be model name : ",model_name)
#     if model_name is ModelName.alexnet:
#         return {"model_name": model_name, "message": "Deep Learning FTW!"}

#     if model_name.value == "lenet":
#         return {"model_name": model_name, "message": "LeCNN all the images"}

#     return {"model_name": model_name, "message": "Have some residuals"}

