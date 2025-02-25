from fastapi import FastAPI
from contextlib import asynccontextmanager
from .models import Base
from .database import  engine
from app.routers import auth,todos, employees

# Modern lifespan handler (replaces startup/shutdown events)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code before yield runs ON STARTUP
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    yield  # App runs here
    # Code after yield runs ON SHUTDOWN
    await engine.dispose()  # Clean up connections

app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(employees.router)


