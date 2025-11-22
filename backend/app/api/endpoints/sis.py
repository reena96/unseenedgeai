"""
SIS (Student Information System) Integration Endpoints.

Supports:
- OneRoster API v1.1
- Clever Secure Sync
- ClassLink Roster Server
- CSV file import/export
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.sis.oneroster_client import OneRosterClient
from app.services.sis.csv_import import CSVImportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sis", tags=["SIS Integration"])


@router.post("/oneroster/sync")
async def sync_oneroster_roster(
    base_url: str = Query(..., description="OneRoster API base URL"),
    client_id: str = Query(..., description="OAuth 2.0 client ID"),
    client_secret: str = Query(..., description="OAuth 2.0 client secret"),
    school_id: str = Query(..., description="School/org sourcedId"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Synchronize roster from OneRoster API v1.1.

    This endpoint:
    - Authenticates with OneRoster API using OAuth 2.0
    - Fetches students, teachers, and classes
    - Syncs data to local database
    - Returns sync statistics

    Example:
        POST /api/v1/sis/oneroster/sync?base_url=https://api.school.com/ims/oneroster/v1p1&client_id=xxx&client_secret=xxx&school_id=ORG123
    """
    try:
        client = OneRosterClient(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            school_id=school_id,
        )

        result = await client.sync_roster(db)

        if result.get("success"):
            return {
                "status": "success",
                "message": "Roster synchronized successfully",
                "statistics": {
                    "students_added": result.get("students_added", 0),
                    "students_updated": result.get("students_updated", 0),
                    "teachers_added": result.get("teachers_added", 0),
                    "teachers_updated": result.get("teachers_updated", 0),
                    "classes_synced": result.get("classes_synced", 0),
                    "duration_seconds": result.get("duration_seconds", 0),
                },
                "errors": result.get("errors", []),
            }
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Roster sync failed",
                    "errors": result.get("errors", []),
                },
            )

    except Exception as e:
        logger.error(f"OneRoster sync error: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.post("/csv/upload/students")
async def upload_students_csv(
    school_id: str = Query(..., description="School identifier"),
    file: UploadFile = File(..., description="CSV file with student data"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Import students from CSV file.

    Expected CSV format:
    ```
    student_id,first_name,last_name,email,grade_level
    STU001,Jane,Doe,jane.doe@school.edu,9
    STU002,John,Smith,john.smith@school.edu,10
    ```

    Returns:
        Import statistics including added, updated, and error counts
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV file")

    try:
        content = await file.read()

        csv_service = CSVImportService(school_id=school_id)
        result = csv_service.import_students(db, content)

        if result.get("success"):
            return {
                "status": "success",
                "message": f"Imported {result['stats']['added']} students",
                "statistics": {
                    "added": result["stats"]["added"],
                    "updated": result["stats"]["updated"],
                    "skipped": result["stats"]["skipped"],
                    "total_rows": result["total_rows"],
                    "duration_seconds": result["duration_seconds"],
                },
                "errors": result["stats"]["errors"] if result["stats"]["errors"] else [],
            }
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": result.get("error", "Import failed"),
                    "errors": result.get("errors", []),
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CSV student import error: {e}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/csv/upload/teachers")
async def upload_teachers_csv(
    school_id: str = Query(..., description="School identifier"),
    file: UploadFile = File(..., description="CSV file with teacher data"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Import teachers from CSV file.

    Expected CSV format:
    ```
    teacher_id,first_name,last_name,email
    TCH001,Jane,Doe,jane.doe@school.edu
    TCH002,John,Smith,john.smith@school.edu
    ```

    Returns:
        Import statistics including added, updated, and error counts
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV file")

    try:
        content = await file.read()

        csv_service = CSVImportService(school_id=school_id)
        result = csv_service.import_teachers(db, content)

        if result.get("success"):
            return {
                "status": "success",
                "message": f"Imported {result['stats']['added']} teachers",
                "statistics": {
                    "added": result["stats"]["added"],
                    "updated": result["stats"]["updated"],
                    "skipped": result["stats"]["skipped"],
                    "total_rows": result["total_rows"],
                    "duration_seconds": result["duration_seconds"],
                },
                "errors": result["stats"]["errors"] if result["stats"]["errors"] else [],
            }
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": result.get("error", "Import failed"),
                    "errors": result.get("errors", []),
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CSV teacher import error: {e}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.get("/csv/template/students", response_class=PlainTextResponse)
async def download_students_csv_template() -> str:
    """
    Download CSV template for student import.

    Returns a CSV file with headers and an example row.
    """
    csv_service = CSVImportService(school_id="example")
    return csv_service.generate_template("students")


@router.get("/csv/template/teachers", response_class=PlainTextResponse)
async def download_teachers_csv_template() -> str:
    """
    Download CSV template for teacher import.

    Returns a CSV file with headers and an example row.
    """
    csv_service = CSVImportService(school_id="example")
    return csv_service.generate_template("teachers")


@router.post("/csv/validate")
async def validate_csv_file(
    record_type: str = Query(..., description="Type of records: 'students' or 'teachers'"),
    file: UploadFile = File(..., description="CSV file to validate"),
) -> Dict[str, Any]:
    """
    Validate CSV file structure before import.

    Checks:
    - File format and encoding
    - Required columns present
    - Data format correctness
    - Empty or invalid rows

    Returns:
        Validation results with any errors found
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV file")

    if record_type not in ["students", "teachers"]:
        raise HTTPException(
            status_code=400, detail="record_type must be 'students' or 'teachers'"
        )

    try:
        content = await file.read()
        csv_service = CSVImportService(school_id="validation")
        result = csv_service.validate_csv(content, record_type)

        return {
            "valid": result["valid"],
            "row_count": result.get("row_count"),
            "error": result.get("error"),
            "errors": result.get("errors"),
            "expected_columns": result.get("expected"),
            "found_columns": result.get("found"),
        }

    except Exception as e:
        logger.error(f"CSV validation error: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")
