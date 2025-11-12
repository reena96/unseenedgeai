"""User authentication and authorization models."""

import enum
from sqlalchemy import Boolean, Enum, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class UserRole(enum.Enum):
    """User roles for RBAC."""

    STUDENT = "student"
    TEACHER = "teacher"
    ADMINISTRATOR = "administrator"
    COUNSELOR = "counselor"
    SYSTEM_ADMIN = "system_admin"


class User(Base, UUIDMixin, TimestampMixin):
    """User account for authentication."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Foreign keys
    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"), nullable=False)

    # Relationships
    school = relationship("School", back_populates="users")

    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"
