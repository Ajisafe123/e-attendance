from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timedelta

from database import get_db
from models import Attendance, Class, User, AttendanceStatus
from schemas import AttendanceCreate, AttendanceResponse, AttendanceWithDetails
from auth import get_current_active_student, get_current_lecturer_or_admin, get_current_user
from utils.geofence import is_within_geofence

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/mark", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def mark_attendance(
    attendance_data: AttendanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_student)
):
    result = await db.execute(
        select(Class).where(Class.id == attendance_data.class_id)
    )
    class_ = result.scalar_one_or_none()
    
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    result = await db.execute(
        select(Attendance).where(
            Attendance.student_id == current_user.id,
            Attendance.class_id == attendance_data.class_id,
            Attendance.marked_at >= today_start,
            Attendance.marked_at < today_end
        )
    )
    existing_attendance = result.scalar_one_or_none()
    
    if existing_attendance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already marked attendance for this class today"
        )
    
    is_within, distance = is_within_geofence(
        attendance_data.latitude,
        attendance_data.longitude,
        class_.latitude,
        class_.longitude,
        class_.radius
    )
    
    attendance_status = AttendanceStatus.APPROVED if is_within else AttendanceStatus.DENIED
    
    new_attendance = Attendance(
        student_id=current_user.id,
        class_id=attendance_data.class_id,
        latitude=attendance_data.latitude,
        longitude=attendance_data.longitude,
        distance=distance,
        status=attendance_status
    )
    
    db.add(new_attendance)
    await db.commit()
    await db.refresh(new_attendance)
    
    return new_attendance

@router.get("/student/{student_id}", response_model=List[AttendanceWithDetails])
async def get_student_attendance(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_lecturer_or_admin)
):
    result = await db.execute(
        select(User).where(User.id == student_id)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    result = await db.execute(
        select(Attendance, User, Class)
        .join(User, Attendance.student_id == User.id)
        .join(Class, Attendance.class_id == Class.id)
        .where(Attendance.student_id == student_id)
        .order_by(Attendance.marked_at.desc())
    )
    
    attendance_records = []
    for attendance, user, class_ in result.all():
        attendance_records.append(
            AttendanceWithDetails(
                id=attendance.id,
                student_id=attendance.student_id,
                class_id=attendance.class_id,
                latitude=attendance.latitude,
                longitude=attendance.longitude,
                distance=attendance.distance,
                status=attendance.status,
                marked_at=attendance.marked_at,
                student_name=user.full_name,
                class_name=class_.name,
                class_code=class_.code
            )
        )
    
    return attendance_records

@router.get("/class/{class_id}", response_model=List[AttendanceWithDetails])
async def get_class_attendance(
    class_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_lecturer_or_admin)
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
    
    result = await db.execute(
        select(Attendance, User, Class)
        .join(User, Attendance.student_id == User.id)
        .join(Class, Attendance.class_id == Class.id)
        .where(Attendance.class_id == class_id)
        .order_by(Attendance.marked_at.desc())
    )
    
    attendance_records = []
    for attendance, user, class_ in result.all():
        attendance_records.append(
            AttendanceWithDetails(
                id=attendance.id,
                student_id=attendance.student_id,
                class_id=attendance.class_id,
                latitude=attendance.latitude,
                longitude=attendance.longitude,
                distance=attendance.distance,
                status=attendance.status,
                marked_at=attendance.marked_at,
                student_name=user.full_name,
                class_name=class_.name,
                class_code=class_.code
            )
        )
    
    return attendance_records

@router.get("/my-attendance", response_model=List[AttendanceWithDetails])
async def get_my_attendance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Attendance, User, Class)
        .join(User, Attendance.student_id == User.id)
        .join(Class, Attendance.class_id == Class.id)
        .where(Attendance.student_id == current_user.id)
        .order_by(Attendance.marked_at.desc())
    )
    
    attendance_records = []
    for attendance, user, class_ in result.all():
        attendance_records.append(
            AttendanceWithDetails(
                id=attendance.id,
                student_id=attendance.student_id,
                class_id=attendance.class_id,
                latitude=attendance.latitude,
                longitude=attendance.longitude,
                distance=attendance.distance,
                status=attendance.status,
                marked_at=attendance.marked_at,
                student_name=user.full_name,
                class_name=class_.name,
                class_code=class_.code
            )
        )
    
    return attendance_records