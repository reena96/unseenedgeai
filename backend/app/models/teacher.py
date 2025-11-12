"""Teacher model."""

from sqlalchemy import String, Boolean, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from app.models.base import Base, TimestampMixin, UUIDMixin

# Association table for teacher-student relationships
teacher_student_association = Table(
    "teacher_student",
    Base.metadata,
    Column("teacher_id", String(36), ForeignKey("teachers.id"), primary_key=True),
    Column("student_id", String(36), ForeignKey("students.id"), primary_key=True),
)


class Teacher(Base, UUIDMixin, TimestampMixin):
    """Teacher entity."""

    __tablename__ = "teachers"

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    department: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Foreign keys
    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    # Relationships
    school = relationship("School", back_populates="teachers")
    user = relationship("User")
    students: Mapped[List["Student"]] = relationship(
        "Student",
        secondary=teacher_student_association,
        backref="teachers",
    )
    rubric_assessments: Mapped[List["RubricAssessment"]] = relationship("RubricAssessment", back_populates="teacher")

    def __repr__(self):
        return f"<Teacher {self.first_name} {self.last_name}>"
