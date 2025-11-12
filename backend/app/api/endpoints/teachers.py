"""Teacher management endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from app.api.endpoints.auth import get_current_user, TokenData

router = APIRouter()


class Teacher(BaseModel):
    """Teacher model."""

    id: str
    first_name: str
    last_name: str
    email: str
    school_id: str
    is_active: bool = True


@router.get(
    "/teachers",
    response_model=List[Teacher],
    status_code=200,
    summary="List teachers",
    description="Get list of teachers (admin only)",
)
async def list_teachers(
    current_user: TokenData = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """List teachers."""
    # TODO: Implement actual database query with admin access control
    return []
