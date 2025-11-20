from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

class UserRole(str, enum.Enum):
    STUDENT = "student"
    LECTURER = "lecturer"
    ADMIN = "admin"

class AttendanceStatus(str, enum.Enum):
    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    classes_taught = relationship("Class", back_populates="lecturer", foreign_keys="Class.lecturer_id")
    attendance_records = relationship("Attendance", back_populates="student")

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius = Column(Float, nullable=False)  # in meters
    lecturer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    lecturer = relationship("User", back_populates="classes_taught", foreign_keys=[lecturer_id])
    attendance_records = relationship("Attendance", back_populates="class_")

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    distance = Column(Float, nullable=False)
    status = Column(SQLEnum(AttendanceStatus), nullable=False, default=AttendanceStatus.PENDING)
    marked_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("User", back_populates="attendance_records")
    class_ = relationship("Class", back_populates="attendance_records")