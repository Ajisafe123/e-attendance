from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from models import UserRole, AttendanceStatus

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    role: UserRole

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None

class ClassBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius: float = Field(..., gt=0, description="Radius in meters")

class ClassCreate(ClassBase):
    pass

class ClassResponse(ClassBase):
    id: int
    lecturer_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class AttendanceBase(BaseModel):
    class_id: int
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    class_id: int
    latitude: float
    longitude: float
    distance: float
    status: AttendanceStatus
    marked_at: datetime
    
    class Config:
        from_attributes = True

class AttendanceWithDetails(AttendanceResponse):
    student_name: str
    class_name: str
    class_code: str
    
    class Config:
        from_attributes = True