from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from starlette import status
from app.schemas import *
from app.models import Employee
router = APIRouter(
    prefix="/employees",
    tags=["employees"]
)

@router.get("/",status_code=status.HTTP_200_OK, response_model=list[EmployeesGet])
async def get_employees(db: AsyncSession = Depends(get_db)):
    results = await db.execute(select(Employee))
    response = results.scalars().all()
    return [EmployeesGet.model_validate(item) for item in response]


@router.get("/{employee_id}",status_code=status.HTTP_200_OK, response_model=EmployeesGet)
async def get_employees(employee_id:int,db: AsyncSession = Depends(get_db)):
    results = await db.execute(select(Employee).where(Employee.id == employee_id))
    response = results.scalars().first()
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return EmployeesGet.model_validate(response)

@router.post("/create",status_code=status.HTTP_201_CREATED, response_model=EmployeeCreate)
async def create_employees(employee: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    await db.commit()
    await db.refresh(db_employee)
    return db_employee

@router.delete("/delete/{employee_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_employees(employee_id:int,db: AsyncSession = Depends(get_db)):
    employee = await db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    await db.delete(employee)
    await db.commit()
    return {"message": "Employee deleted"}
