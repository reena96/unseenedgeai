"""Role-Based Access Control (RBAC) implementation."""

from enum import Enum
from typing import List, Optional
from functools import wraps
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.api.endpoints.auth import get_current_user
from app.core.database import get_db


class Role(str, Enum):
    """User roles in the system."""

    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"
    SCHOOL_ADMIN = "school_admin"
    SYSTEM_ADMIN = "system_admin"
    RESEARCHER = "researcher"


class Permission(str, Enum):
    """System permissions."""

    # Assessment permissions
    ASSESSMENTS_READ_OWN = "assessments.read.own"
    ASSESSMENTS_READ_CLASS = "assessments.read.class"
    ASSESSMENTS_READ_SCHOOL = "assessments.read.school"
    ASSESSMENTS_READ_ALL = "assessments.read.all"
    ASSESSMENTS_WRITE = "assessments.write"

    # Student data permissions
    STUDENTS_READ_OWN = "students.read.own"
    STUDENTS_READ_CLASS = "students.read.class"
    STUDENTS_READ_SCHOOL = "students.read.school"
    STUDENTS_READ_ALL = "students.read.all"
    STUDENTS_WRITE = "students.write"

    # Telemetry permissions
    TELEMETRY_READ = "telemetry.read"
    TELEMETRY_WRITE = "telemetry.write"

    # User management
    USERS_READ = "users.read"
    USERS_WRITE = "users.write"

    # System configuration
    SYSTEM_CONFIG = "system.config"

    # Dashboard access
    DASHBOARD_VIEW = "dashboard.view"

    # Data export
    DATA_EXPORT_ANONYMIZED = "data.export.anonymized"
    DATA_EXPORT_FULL = "data.export.full"


# Role-Permission mapping
ROLE_PERMISSIONS = {
    Role.STUDENT: [
        Permission.ASSESSMENTS_READ_OWN,
        Permission.STUDENTS_READ_OWN,
        Permission.TELEMETRY_READ,
    ],
    Role.PARENT: [
        Permission.ASSESSMENTS_READ_OWN,  # Own child only
        Permission.STUDENTS_READ_OWN,  # Own child only
        Permission.DASHBOARD_VIEW,
    ],
    Role.TEACHER: [
        Permission.ASSESSMENTS_READ_CLASS,
        Permission.STUDENTS_READ_CLASS,
        Permission.TELEMETRY_READ,
        Permission.DASHBOARD_VIEW,
    ],
    Role.SCHOOL_ADMIN: [
        Permission.ASSESSMENTS_READ_SCHOOL,
        Permission.STUDENTS_READ_SCHOOL,
        Permission.TELEMETRY_READ,
        Permission.USERS_READ,
        Permission.USERS_WRITE,
        Permission.DASHBOARD_VIEW,
        Permission.DATA_EXPORT_ANONYMIZED,
    ],
    Role.SYSTEM_ADMIN: [
        Permission.ASSESSMENTS_READ_ALL,
        Permission.ASSESSMENTS_WRITE,
        Permission.STUDENTS_READ_ALL,
        Permission.STUDENTS_WRITE,
        Permission.TELEMETRY_READ,
        Permission.TELEMETRY_WRITE,
        Permission.USERS_READ,
        Permission.USERS_WRITE,
        Permission.SYSTEM_CONFIG,
        Permission.DASHBOARD_VIEW,
        Permission.DATA_EXPORT_FULL,
    ],
    Role.RESEARCHER: [
        Permission.DATA_EXPORT_ANONYMIZED,
        Permission.DASHBOARD_VIEW,  # Anonymized data only
    ],
}


def has_permission(user: User, permission: Permission) -> bool:
    """
    Check if user has a specific permission.

    Args:
        user: User object
        permission: Permission to check

    Returns:
        True if user has permission, False otherwise
    """
    if not user or not user.role:
        return False

    user_permissions = ROLE_PERMISSIONS.get(Role(user.role), [])
    return permission in user_permissions


def require_permission(permission: Permission):
    """
    Decorator to require a specific permission for an endpoint.

    Usage:
        @router.get("/protected")
        @require_permission(Permission.ASSESSMENTS_READ_ALL)
        async def protected_endpoint(current_user: User = Depends(get_current_user)):
            ...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs (injected by Depends)
            current_user = kwargs.get("current_user")

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            if not has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission.value} required",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_role(*allowed_roles: Role):
    """
    Decorator to require specific role(s) for an endpoint.

    Usage:
        @router.get("/admin")
        @require_role(Role.SYSTEM_ADMIN, Role.SCHOOL_ADMIN)
        async def admin_endpoint(current_user: User = Depends(get_current_user)):
            ...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            if Role(current_user.role) not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Requires one of: {[r.value for r in allowed_roles]}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def can_access_student(
    user: User, student_id: str, db: AsyncSession
) -> bool:
    """
    Check if user can access specific student's data.

    Args:
        user: Current user
        student_id: Target student ID
        db: Database session

    Returns:
        True if access allowed, False otherwise
    """
    # System admin can access all
    if user.role == Role.SYSTEM_ADMIN.value:
        return True

    # Student can only access own data
    if user.role == Role.STUDENT.value:
        # Assuming user has student_id field
        return getattr(user, "student_id", None) == student_id

    # Parent can access own child's data
    if user.role == Role.PARENT.value:
        # Check parent-child relationship in database
        return await is_parent_of(user.id, student_id, db)

    # Teacher can access students in their classes
    if user.role == Role.TEACHER.value:
        return await is_in_teacher_class(user.id, student_id, db)

    # School admin can access students in their school
    if user.role == Role.SCHOOL_ADMIN.value:
        return await is_in_school(user.school_id, student_id, db)

    # Researcher cannot access individual student data
    if user.role == Role.RESEARCHER.value:
        return False

    return False


async def is_parent_of(
    parent_id: str, student_id: str, db: AsyncSession
) -> bool:
    """Check if user is parent of student."""
    # This would query parent-student relationship table
    # For now, placeholder implementation
    from app.models.student import Student

    stmt = select(Student).where(
        Student.id == student_id, Student.parent_id == parent_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def is_in_teacher_class(
    teacher_id: str, student_id: str, db: AsyncSession
) -> bool:
    """Check if student is in teacher's class."""
    # This would query class enrollment
    # For now, placeholder implementation
    from app.models.student import Student
    from app.models.teacher import Teacher

    # Get teacher's classes
    stmt = select(Teacher).where(Teacher.user_id == teacher_id)
    result = await db.execute(stmt)
    teacher = result.scalar_one_or_none()

    if not teacher:
        return False

    # Check if student is in any of teacher's classes
    stmt = select(Student).where(
        Student.id == student_id,
        Student.class_id.in_(teacher.class_ids or [])
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def is_in_school(
    school_id: str, student_id: str, db: AsyncSession
) -> bool:
    """Check if student is in school."""
    from app.models.student import Student

    stmt = select(Student).where(
        Student.id == student_id, Student.school_id == school_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def filter_accessible_students(
    user: User, student_ids: List[str], db: AsyncSession
) -> List[str]:
    """
    Filter list of student IDs to only those user can access.

    Args:
        user: Current user
        student_ids: List of student IDs to filter
        db: Database session

    Returns:
        Filtered list of accessible student IDs
    """
    accessible = []

    for student_id in student_ids:
        if await can_access_student(user, student_id, db):
            accessible.append(student_id)

    return accessible


def anonymize_student_data(data: dict) -> dict:
    """
    Remove PII from student data for researchers.

    Args:
        data: Student data dictionary

    Returns:
        Anonymized data dictionary
    """
    anonymized = data.copy()

    # Remove PII fields
    pii_fields = [
        "name",
        "email",
        "phone",
        "address",
        "date_of_birth",
        "student_id",
        "parent_name",
        "parent_email",
        "parent_phone",
    ]

    for field in pii_fields:
        anonymized.pop(field, None)

    # Replace ID with anonymous hash
    if "id" in anonymized:
        import hashlib

        anonymized["anonymous_id"] = hashlib.sha256(
            anonymized["id"].encode()
        ).hexdigest()[:16]
        anonymized.pop("id")

    return anonymized
