"""
CSV Import Service for schools without SIS API access.

Supports importing student and teacher rosters from CSV files.
"""

import logging
import csv
from typing import List, Dict, Any, BinaryIO
from datetime import datetime
from sqlalchemy.orm import Session
import io

from app.models.student import Student
from app.models.teacher import Teacher

logger = logging.getLogger(__name__)


class CSVImportService:
    """Service for importing roster data from CSV files."""

    # Expected CSV columns
    STUDENT_COLUMNS = ["student_id", "first_name", "last_name", "email", "grade_level"]
    TEACHER_COLUMNS = ["teacher_id", "first_name", "last_name", "email"]

    def __init__(self, school_id: str):
        """
        Initialize CSV import service.

        Args:
            school_id: School identifier
        """
        self.school_id = school_id

    def validate_csv(self, file_content: bytes, record_type: str) -> Dict[str, Any]:
        """
        Validate CSV file structure.

        Args:
            file_content: CSV file content as bytes
            record_type: Type of records ('students' or 'teachers')

        Returns:
            Validation results with errors if any
        """
        try:
            text_content = file_content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(text_content))

            expected_columns = (
                self.STUDENT_COLUMNS if record_type == "students" else self.TEACHER_COLUMNS
            )

            # Check headers
            if not reader.fieldnames:
                return {"valid": False, "error": "CSV file is empty or missing headers"}

            missing_columns = set(expected_columns) - set(reader.fieldnames)
            if missing_columns:
                return {
                    "valid": False,
                    "error": f"Missing required columns: {', '.join(missing_columns)}",
                    "expected": expected_columns,
                    "found": list(reader.fieldnames),
                }

            # Count rows
            rows = list(reader)
            row_count = len(rows)

            # Validate data
            errors = []
            for i, row in enumerate(rows, start=2):  # Start at 2 (header is row 1)
                # Check for empty required fields
                id_field = (
                    "student_id" if record_type == "students" else "teacher_id"
                )
                if not row.get(id_field):
                    errors.append(f"Row {i}: Missing {id_field}")

                if not row.get("first_name") and not row.get("last_name"):
                    errors.append(f"Row {i}: Missing both first_name and last_name")

                if not row.get("email"):
                    errors.append(f"Row {i}: Missing email")

                # Limit error reporting
                if len(errors) >= 10:
                    errors.append(f"... and more errors (showing first 10)")
                    break

            return {
                "valid": len(errors) == 0,
                "row_count": row_count,
                "errors": errors if errors else None,
            }

        except UnicodeDecodeError:
            return {"valid": False, "error": "File must be UTF-8 encoded"}
        except Exception as e:
            return {"valid": False, "error": f"Failed to parse CSV: {str(e)}"}

    def import_students(self, db: Session, file_content: bytes) -> Dict[str, Any]:
        """
        Import students from CSV file.

        Args:
            db: Database session
            file_content: CSV file content as bytes

        Returns:
            Import statistics and results
        """
        logger.info(f"Starting CSV student import for school {self.school_id}")
        start_time = datetime.utcnow()

        # Validate first
        validation = self.validate_csv(file_content, "students")
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation.get("error"),
                "errors": validation.get("errors"),
            }

        stats = {"added": 0, "updated": 0, "skipped": 0, "errors": []}

        try:
            text_content = file_content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(text_content))

            for row_num, row in enumerate(reader, start=2):
                try:
                    student_id = row.get("student_id", "").strip()
                    if not student_id:
                        stats["skipped"] += 1
                        continue

                    # Check if student exists
                    student = (
                        db.query(Student)
                        .filter(Student.external_id == student_id)
                        .first()
                    )

                    first_name = row.get("first_name", "").strip()
                    last_name = row.get("last_name", "").strip()
                    name = f"{first_name} {last_name}".strip()

                    if not student:
                        # Create new student
                        student = Student(
                            external_id=student_id,
                            name=name,
                            email=row.get("email", "").strip(),
                            grade_level=row.get("grade_level", "").strip() or None,
                            school_id=self.school_id,
                        )
                        db.add(student)
                        stats["added"] += 1
                        logger.info(f"Created student: {name} ({student_id})")
                    else:
                        # Update existing student
                        student.name = name
                        student.email = row.get("email", "").strip()
                        student.grade_level = row.get("grade_level", "").strip() or None
                        stats["updated"] += 1
                        logger.info(f"Updated student: {name} ({student_id})")

                except Exception as e:
                    error_msg = f"Row {row_num}: {str(e)}"
                    logger.error(f"Error importing student row {row_num}: {e}")
                    stats["errors"].append(error_msg)

            db.commit()

            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                f"CSV student import completed in {duration:.2f}s: "
                f"{stats['added']} added, {stats['updated']} updated, "
                f"{stats['skipped']} skipped, {len(stats['errors'])} errors"
            )

            return {
                "success": True,
                "stats": stats,
                "duration_seconds": duration,
                "total_rows": validation["row_count"],
            }

        except Exception as e:
            logger.error(f"CSV student import failed: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}

    def import_teachers(self, db: Session, file_content: bytes) -> Dict[str, Any]:
        """
        Import teachers from CSV file.

        Args:
            db: Database session
            file_content: CSV file content as bytes

        Returns:
            Import statistics and results
        """
        logger.info(f"Starting CSV teacher import for school {self.school_id}")
        start_time = datetime.utcnow()

        # Validate first
        validation = self.validate_csv(file_content, "teachers")
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation.get("error"),
                "errors": validation.get("errors"),
            }

        stats = {"added": 0, "updated": 0, "skipped": 0, "errors": []}

        try:
            text_content = file_content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(text_content))

            for row_num, row in enumerate(reader, start=2):
                try:
                    teacher_id = row.get("teacher_id", "").strip()
                    if not teacher_id:
                        stats["skipped"] += 1
                        continue

                    # Check if teacher exists
                    teacher = (
                        db.query(Teacher)
                        .filter(Teacher.external_id == teacher_id)
                        .first()
                    )

                    first_name = row.get("first_name", "").strip()
                    last_name = row.get("last_name", "").strip()
                    name = f"{first_name} {last_name}".strip()

                    if not teacher:
                        # Create new teacher
                        teacher = Teacher(
                            external_id=teacher_id,
                            name=name,
                            email=row.get("email", "").strip(),
                            school_id=self.school_id,
                        )
                        db.add(teacher)
                        stats["added"] += 1
                        logger.info(f"Created teacher: {name} ({teacher_id})")
                    else:
                        # Update existing teacher
                        teacher.name = name
                        teacher.email = row.get("email", "").strip()
                        stats["updated"] += 1
                        logger.info(f"Updated teacher: {name} ({teacher_id})")

                except Exception as e:
                    error_msg = f"Row {row_num}: {str(e)}"
                    logger.error(f"Error importing teacher row {row_num}: {e}")
                    stats["errors"].append(error_msg)

            db.commit()

            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                f"CSV teacher import completed in {duration:.2f}s: "
                f"{stats['added']} added, {stats['updated']} updated, "
                f"{stats['skipped']} skipped, {len(stats['errors'])} errors"
            )

            return {
                "success": True,
                "stats": stats,
                "duration_seconds": duration,
                "total_rows": validation["row_count"],
            }

        except Exception as e:
            logger.error(f"CSV teacher import failed: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}

    def generate_template(self, record_type: str) -> str:
        """
        Generate CSV template for import.

        Args:
            record_type: Type of records ('students' or 'teachers')

        Returns:
            CSV template as string
        """
        columns = (
            self.STUDENT_COLUMNS if record_type == "students" else self.TEACHER_COLUMNS
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)

        # Add example row
        if record_type == "students":
            writer.writerow(
                ["STU001", "Jane", "Doe", "jane.doe@school.edu", "9"]
            )
        else:
            writer.writerow(
                ["TCH001", "John", "Smith", "john.smith@school.edu"]
            )

        return output.getvalue()
