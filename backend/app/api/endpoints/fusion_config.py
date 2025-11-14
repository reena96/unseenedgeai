"""API endpoints for managing fusion weight configuration."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Optional
from pathlib import Path

from app.api.endpoints.auth import get_current_user, TokenData
from app.models.assessment import SkillType
from app.core.fusion_config import get_fusion_config_manager, SkillWeights
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class SkillWeightsRequest(BaseModel):
    """Request model for updating skill weights."""

    ml_inference: float = Field(..., ge=0.0, le=1.0)
    linguistic_features: float = Field(..., ge=0.0, le=1.0)
    behavioral_features: float = Field(..., ge=0.0, le=1.0)
    confidence_adjustment: float = Field(..., ge=0.0, le=1.0)


class SkillWeightsResponse(BaseModel):
    """Response model for skill weights."""

    skill_type: str
    ml_inference: float
    linguistic_features: float
    behavioral_features: float
    confidence_adjustment: float


class AllWeightsResponse(BaseModel):
    """Response model for all skill weights."""

    version: str
    description: str
    weights: Dict[str, SkillWeightsResponse]


@router.get(
    "/weights",
    response_model=AllWeightsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all fusion weights",
    description="Get current fusion weight configuration for all skills",
)
async def get_all_weights(
    current_user: TokenData = Depends(get_current_user),
):
    """
    Get current fusion weight configuration for all skills.

    Returns:
        Current fusion weights configuration
    """
    config_manager = get_fusion_config_manager()
    config = config_manager.get_config()

    weights_dict = {}
    for skill_type in SkillType:
        try:
            skill_weights = config.get_weights(skill_type)
            weights_dict[skill_type.value] = SkillWeightsResponse(
                skill_type=skill_type.value,
                ml_inference=skill_weights.ml_inference,
                linguistic_features=skill_weights.linguistic_features,
                behavioral_features=skill_weights.behavioral_features,
                confidence_adjustment=skill_weights.confidence_adjustment,
            )
        except KeyError:
            logger.warning(f"No weights found for {skill_type.value}")

    return AllWeightsResponse(
        version=config.version,
        description=config.description,
        weights=weights_dict,
    )


@router.get(
    "/weights/{skill_type}",
    response_model=SkillWeightsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get weights for a skill",
    description="Get current fusion weights for a specific skill",
)
async def get_skill_weights(
    skill_type: str,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Get fusion weights for a specific skill.

    Args:
        skill_type: Skill type (empathy, problem_solving, self_regulation, resilience)

    Returns:
        Fusion weights for the skill
    """
    try:
        skill_enum = SkillType(skill_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid skill type: {skill_type}",
        )

    config_manager = get_fusion_config_manager()
    config = config_manager.get_config()

    try:
        skill_weights = config.get_weights(skill_enum)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No weights configured for skill: {skill_type}",
        )

    return SkillWeightsResponse(
        skill_type=skill_type,
        ml_inference=skill_weights.ml_inference,
        linguistic_features=skill_weights.linguistic_features,
        behavioral_features=skill_weights.behavioral_features,
        confidence_adjustment=skill_weights.confidence_adjustment,
    )


@router.put(
    "/weights/{skill_type}",
    response_model=SkillWeightsResponse,
    status_code=status.HTTP_200_OK,
    summary="Update weights for a skill",
    description="Update fusion weights for a specific skill",
)
async def update_skill_weights(
    skill_type: str,
    weights: SkillWeightsRequest,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Update fusion weights for a specific skill.

    Args:
        skill_type: Skill type (empathy, problem_solving, self_regulation, resilience)
        weights: New weight configuration

    Returns:
        Updated fusion weights

    Raises:
        HTTPException: If skill type invalid or weights don't sum to 1.0
    """
    try:
        skill_enum = SkillType(skill_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid skill type: {skill_type}",
        )

    # Create SkillWeights object (validates weights sum to 1.0)
    try:
        skill_weights = SkillWeights(
            ml_inference=weights.ml_inference,
            linguistic_features=weights.linguistic_features,
            behavioral_features=weights.behavioral_features,
            confidence_adjustment=weights.confidence_adjustment,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid weights: {str(e)}",
        )

    # Update configuration
    config_manager = get_fusion_config_manager()
    config = config_manager.get_config()
    config.update_weights(skill_enum, skill_weights)
    config_manager.update_config(config, save=True)

    logger.info(
        f"Updated fusion weights for {skill_type} by user {current_user.username}"
    )

    return SkillWeightsResponse(
        skill_type=skill_type,
        ml_inference=skill_weights.ml_inference,
        linguistic_features=skill_weights.linguistic_features,
        behavioral_features=skill_weights.behavioral_features,
        confidence_adjustment=skill_weights.confidence_adjustment,
    )


@router.post(
    "/weights/reload",
    status_code=status.HTTP_200_OK,
    summary="Reload weights from file",
    description="Reload fusion weight configuration from file",
)
async def reload_weights(
    current_user: TokenData = Depends(get_current_user),
):
    """
    Reload fusion weight configuration from file.

    Returns:
        Success message
    """
    config_manager = get_fusion_config_manager()
    config = config_manager.reload()

    logger.info(f"Reloaded fusion config by user {current_user.username}")

    return {
        "message": "Configuration reloaded successfully",
        "version": config.version,
        "description": config.description,
    }
