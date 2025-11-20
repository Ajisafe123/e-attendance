from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import timedelta

from database import get_db
from models import Class, User
from schemas import ClassCreate, ClassResponse
from auth import get_current_active_lecturer, get_current_user

router = APIRouter(prefix="/classes", tags=["Classes"])

@router.post("/create", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
async def create_class(
    class_data: ClassCreate,
    current_user: User = Depends(get_current_active_lecturer),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Class).where(Class.code == class_data.code)
    )
    existing_class = result.scalar_one_or_none()
    if existing_class:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Class code already exists"
        )
    
    new_class = Class(
        name=class_data.name,
        code=class_data.code,
        description=class_data.description,
        latitude=class_data.latitude,
        longitude=class_data.longitude,
        radius=class_data.radius,
        lecturer_id=current_user.id
    )
    
    db.add(new_class)
    await db.commit()
    await db.refresh(new_class)
    
    return new_class

@router.get("/", response_model=List[ClassResponse])
async def get_all_classes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Class))
    classes = result.scalars().all()
    return classes

@router.get("/{class_id}", response_model=ClassResponse)
async def get_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Class).where(Class.id == class_id)
    )
    class_ = result.scalar_one_or_none()
    
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    return class_

@router.get("/code/{class_code}", response_model=ClassResponse)
async def get_class_by_code(
    class_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Class).where(Class.code == class_code)
    )
    class_ = result.scalar_one_or_none()
    
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    return class_

@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class(
    class_id: int,
    current_user: User = Depends(get_current_active_lecturer),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Class).where(Class.id == class_id)
    )
    class_ = result.scalar_one_or_none()
    
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    if class_.lecturer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own classes"
        )
    
    await db.delete(class_)
    await db.commit()
    
    return None