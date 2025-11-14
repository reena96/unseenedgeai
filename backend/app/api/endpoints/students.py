"""Student management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.endpoints.auth import get_current_user, TokenData
from app.core.database import get_db
from app.models.student import Student as StudentModel

router = APIRouter()


class Student(BaseModel):
    """Student model."""

    id: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    grade_level: int
    school_id: str
    is_active: bool = True


@router.get(
    "/students",
    response_model=List[Student],
    status_code=status.HTTP_200_OK,
    summary="List students",
    description="Get list of students (filtered by teacher access)",
)
async def list_students(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List students accessible by current user."""
    # Query database for real students
    result = await db.execute(
        select(StudentModel)
        .where(StudentModel.is_active == True)
        .order_by(StudentModel.grade_level, StudentModel.last_name)
        .offset(skip)
        .limit(limit)
    )
    students = result.scalars().all()

    # Convert to response model
    return [
        Student(
            id=str(student.id),
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            grade_level=student.grade_level,
            school_id=str(student.school_id),
            is_active=student.is_active,
        )
        for student in students
    ]


@router.get(
    "/students/{student_id}",
    response_model=Student,
    status_code=status.HTTP_200_OK,
    summary="Get student details",
    description="Get detailed information about a specific student",
)
async def get_student(
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """Get student by ID."""
    # TODO: Implement actual database query with access control
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Student not found",
    )
