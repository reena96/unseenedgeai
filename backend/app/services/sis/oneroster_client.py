"""
OneRoster API v1.1 Client for roster synchronization.

Implements the OneRoster REST API specification for syncing:
- Students (orgs, users with role=student)
- Teachers (users with role=teacher)
- Classes (courses and classes)
- Enrollments (user-to-class relationships)
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.teacher import Teacher
from app.core.database import get_db

logger = logging.getLogger(__name__)


class OneRosterClient:
    """OneRoster API v1.1 client for roster synchronization."""

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        school_id: str,
        timeout: int = 30,
    ):
        """
        Initialize OneRoster client.

        Args:
            base_url: OneRoster API base URL (e.g., https://api.school.com/ims/oneroster/v1p1)
            client_id: OAuth 2.0 client ID
            client_secret: OAuth 2.0 client secret
            school_id: School/org sourcedId
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.school_id = school_id
        self.timeout = timeout
        self.access_token: Optional[str] = None

    async def authenticate(self) -> str:
        """
        Authenticate with OneRoster API using OAuth 2.0.

        Returns:
            Access token
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            return self.access_token

    async def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated GET request to OneRoster API."""
        if not self.access_token:
            await self.authenticate()

        headers = {"Authorization": f"Bearer {self.access_token}"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}{endpoint}", headers=headers, params=params or {}
            )
            response.raise_for_status()
            return response.json()

    async def get_students(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Fetch students from OneRoster API.

        Args:
            limit: Maximum number of students to fetch
            offset: Pagination offset

        Returns:
            List of student records
        """
        logger.info(f"Fetching students from OneRoster (limit={limit}, offset={offset})")

        data = await self._get(
            f"/orgs/{self.school_id}/users",
            params={
                "filter": "role='student'",
                "limit": limit,
                "offset": offset,
            },
        )

        students = data.get("users", [])
        logger.info(f"Fetched {len(students)} students")
        return students

    async def get_teachers(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Fetch teachers from OneRoster API.

        Returns:
            List of teacher records
        """
        logger.info(f"Fetching teachers from OneRoster (limit={limit}, offset={offset})")

        data = await self._get(
            f"/orgs/{self.school_id}/users",
            params={
                "filter": "role='teacher'",
                "limit": limit,
                "offset": offset,
            },
        )

        teachers = data.get("users", [])
        logger.info(f"Fetched {len(teachers)} teachers")
        return teachers

    async def get_classes(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Fetch classes from OneRoster API.

        Returns:
            List of class records
        """
        logger.info(f"Fetching classes from OneRoster (limit={limit}, offset={offset})")

        data = await self._get(
            f"/orgs/{self.school_id}/classes", params={"limit": limit, "offset": offset}
        )

        classes = data.get("classes", [])
        logger.info(f"Fetched {len(classes)} classes")
        return classes

    async def get_enrollments(
        self, class_id: str, limit: int = 1000, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Fetch enrollments for a specific class.

        Args:
            class_id: Class sourcedId
            limit: Maximum number of enrollments to fetch
            offset: Pagination offset

        Returns:
            List of enrollment records
        """
        logger.info(f"Fetching enrollments for class {class_id}")

        data = await self._get(
            f"/classes/{class_id}/enrollments", params={"limit": limit, "offset": offset}
        )

        enrollments = data.get("enrollments", [])
        logger.info(f"Fetched {len(enrollments)} enrollments")
        return enrollments

    async def sync_roster(self, db: Session) -> Dict[str, Any]:
        """
        Synchronize complete roster from OneRoster API.

        Args:
            db: Database session

        Returns:
            Sync statistics and results
        """
        logger.info(f"Starting OneRoster roster sync for school {self.school_id}")
        start_time = datetime.utcnow()

        stats = {
            "students_added": 0,
            "students_updated": 0,
            "teachers_added": 0,
            "teachers_updated": 0,
            "classes_synced": 0,
            "errors": [],
        }

        try:
            # Sync students
            students = await self.get_students()
            for student_data in students:
                try:
                    student = self._sync_student(db, student_data)
                    if student:
                        stats["students_added" if student.id else "students_updated"] += 1
                except Exception as e:
                    logger.error(f"Error syncing student {student_data.get('sourcedId')}: {e}")
                    stats["errors"].append(
                        {"type": "student", "id": student_data.get("sourcedId"), "error": str(e)}
                    )

            # Sync teachers
            teachers = await self.get_teachers()
            for teacher_data in teachers:
                try:
                    teacher = self._sync_teacher(db, teacher_data)
                    if teacher:
                        stats["teachers_added" if teacher.id else "teachers_updated"] += 1
                except Exception as e:
                    logger.error(f"Error syncing teacher {teacher_data.get('sourcedId')}: {e}")
                    stats["errors"].append(
                        {"type": "teacher", "id": teacher_data.get("sourcedId"), "error": str(e)}
                    )

            db.commit()

            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                f"OneRoster sync completed in {duration:.2f}s: "
                f"{stats['students_added']} students added, "
                f"{stats['students_updated']} students updated, "
                f"{stats['teachers_added']} teachers added, "
                f"{stats['teachers_updated']} teachers updated"
            )

            stats["duration_seconds"] = duration
            stats["success"] = True

        except Exception as e:
            logger.error(f"OneRoster sync failed: {e}")
            db.rollback()
            stats["success"] = False
            stats["errors"].append({"type": "sync", "error": str(e)})

        return stats

    def _sync_student(self, db: Session, student_data: Dict[str, Any]) -> Optional[Student]:
        """Sync individual student record."""
        sourced_id = student_data.get("sourcedId")
        if not sourced_id:
            return None

        # Check if student exists
        student = db.query(Student).filter(Student.external_id == sourced_id).first()

        if not student:
            # Create new student
            student = Student(
                external_id=sourced_id,
                name=f"{student_data.get('givenName', '')} {student_data.get('familyName', '')}".strip(),
                email=student_data.get("email"),
                grade_level=student_data.get("grades", [None])[0],
                school_id=self.school_id,
            )
            db.add(student)
            logger.info(f"Created new student: {student.name} ({sourced_id})")
        else:
            # Update existing student
            student.name = (
                f"{student_data.get('givenName', '')} {student_data.get('familyName', '')}".strip()
            )
            student.email = student_data.get("email")
            student.grade_level = student_data.get("grades", [None])[0]
            logger.info(f"Updated student: {student.name} ({sourced_id})")

        return student

    def _sync_teacher(self, db: Session, teacher_data: Dict[str, Any]) -> Optional[Teacher]:
        """Sync individual teacher record."""
        sourced_id = teacher_data.get("sourcedId")
        if not sourced_id:
            return None

        # Check if teacher exists
        teacher = db.query(Teacher).filter(Teacher.external_id == sourced_id).first()

        if not teacher:
            # Create new teacher
            teacher = Teacher(
                external_id=sourced_id,
                name=f"{teacher_data.get('givenName', '')} {teacher_data.get('familyName', '')}".strip(),
                email=teacher_data.get("email"),
                school_id=self.school_id,
            )
            db.add(teacher)
            logger.info(f"Created new teacher: {teacher.name} ({sourced_id})")
        else:
            # Update existing teacher
            teacher.name = (
                f"{teacher_data.get('givenName', '')} {teacher_data.get('familyName', '')}".strip()
            )
            teacher.email = teacher_data.get("email")
            logger.info(f"Updated teacher: {teacher.name} ({sourced_id})")

        return teacher
