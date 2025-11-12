"""School and district models."""

from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from app.models.base import Base, TimestampMixin, UUIDMixin


class School(Base, UUIDMixin, TimestampMixin):
    """School entity."""

    __tablename__ = "schools"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    district: Mapped[str] = mapped_column(String(255), nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(2), nullable=True)
    zip_code: Mapped[str] = mapped_column(String(10), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    student_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="school")
    students: Mapped[List["Student"]] = relationship("Student", back_populates="school")
    teachers: Mapped[List["Teacher"]] = relationship("Teacher", back_populates="school")

    def __repr__(self):
        return f"<School {self.name}>"
