"""Configuration management for evidence fusion weights."""

import json
import logging
from typing import Dict, Optional
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum

from app.models.assessment import SkillType

logger = logging.getLogger(__name__)


class EvidenceSource(str, Enum):
    """Evidence source types."""

    ML_INFERENCE = "ml_inference"
    LINGUISTIC_FEATURES = "linguistic_features"
    BEHAVIORAL_FEATURES = "behavioral_features"
    CONFIDENCE_ADJUSTMENT = "confidence_adjustment"


@dataclass
class SkillWeights:
    """Weights for a specific skill."""

    ml_inference: float = 0.50
    linguistic_features: float = 0.20
    behavioral_features: float = 0.20
    confidence_adjustment: float = 0.10

    def __post_init__(self):
        """Validate weights sum to 1.0."""
        total = (
            self.ml_inference
            + self.linguistic_features
            + self.behavioral_features
            + self.confidence_adjustment
        )
        if not (0.99 <= total <= 1.01):  # Allow small floating point error
            raise ValueError(
                f"Weights must sum to 1.0, got {total:.3f}. "
                f"ML: {self.ml_inference}, Ling: {self.linguistic_features}, "
                f"Beh: {self.behavioral_features}, Conf: {self.confidence_adjustment}"
            )

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            EvidenceSource.ML_INFERENCE.value: self.ml_inference,
            EvidenceSource.LINGUISTIC_FEATURES.value: self.linguistic_features,
            EvidenceSource.BEHAVIORAL_FEATURES.value: self.behavioral_features,
            EvidenceSource.CONFIDENCE_ADJUSTMENT.value: self.confidence_adjustment,
        }


@dataclass
class FusionConfig:
    """Configuration for evidence fusion weights."""

    version: str = "1.0.0"
    description: str = "Default fusion weights"
    weights: Dict[str, SkillWeights] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize with default weights if not provided."""
        if not self.weights:
            self.weights = self._get_default_weights()

    @staticmethod
    def _get_default_weights() -> Dict[str, SkillWeights]:
        """Get default weights for all skills."""
        return {
            SkillType.EMPATHY.value: SkillWeights(
                ml_inference=0.50,
                linguistic_features=0.25,  # Higher for empathy (language indicators)
                behavioral_features=0.15,
                confidence_adjustment=0.10,
            ),
            SkillType.PROBLEM_SOLVING.value: SkillWeights(
                ml_inference=0.50,
                linguistic_features=0.20,
                behavioral_features=0.20,  # Balanced
                confidence_adjustment=0.10,
            ),
            SkillType.SELF_REGULATION.value: SkillWeights(
                ml_inference=0.50,
                linguistic_features=0.10,  # Lower for self-regulation
                behavioral_features=0.30,  # Higher (focus/distraction data)
                confidence_adjustment=0.10,
            ),
            SkillType.RESILIENCE.value: SkillWeights(
                ml_inference=0.50,
                linguistic_features=0.15,
                behavioral_features=0.25,  # Higher (retry/recovery patterns)
                confidence_adjustment=0.10,
            ),
        }

    def get_weights(self, skill_type: SkillType) -> SkillWeights:
        """
        Get weights for a specific skill.

        Args:
            skill_type: Skill type to get weights for

        Returns:
            SkillWeights for the skill

        Raises:
            KeyError: If skill type not found
        """
        if skill_type.value not in self.weights:
            raise KeyError(f"No weights configured for skill: {skill_type.value}")
        return self.weights[skill_type.value]

    def update_weights(self, skill_type: SkillType, weights: SkillWeights):
        """
        Update weights for a specific skill.

        Args:
            skill_type: Skill type to update
            weights: New weights

        Raises:
            ValueError: If weights invalid
        """
        # Validation happens in SkillWeights.__post_init__
        self.weights[skill_type.value] = weights
        logger.info(f"Updated fusion weights for {skill_type.value}")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "description": self.description,
            "weights": {
                skill: asdict(weights) for skill, weights in self.weights.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FusionConfig":
        """
        Create from dictionary.

        Args:
            data: Dictionary with config data

        Returns:
            FusionConfig instance
        """
        weights = {}
        for skill, weight_data in data.get("weights", {}).items():
            weights[skill] = SkillWeights(**weight_data)

        return cls(
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            weights=weights,
        )

    def save(self, path: Path):
        """
        Save config to JSON file.

        Args:
            path: Path to save to
        """
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

        logger.info(f"Saved fusion config to {path}")

    @classmethod
    def load(cls, path: Path) -> "FusionConfig":
        """
        Load config from JSON file.

        Args:
            path: Path to load from

        Returns:
            FusionConfig instance

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r") as f:
            data = json.load(f)

        logger.info(f"Loaded fusion config from {path}")
        return cls.from_dict(data)


class FusionConfigManager:
    """Manager for fusion configuration with file and in-memory storage."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize config manager.

        Args:
            config_path: Path to config file (optional)
        """
        self.config_path = config_path
        self._config: Optional[FusionConfig] = None

    def get_config(self) -> FusionConfig:
        """
        Get current configuration.

        Returns:
            FusionConfig instance
        """
        if self._config is None:
            if self.config_path and self.config_path.exists():
                try:
                    self._config = FusionConfig.load(self.config_path)
                    logger.info("Loaded fusion config from file")
                except Exception as e:
                    logger.warning(f"Failed to load config from {self.config_path}: {e}")
                    self._config = FusionConfig()
            else:
                logger.info("Using default fusion config")
                self._config = FusionConfig()

        return self._config

    def update_config(self, config: FusionConfig, save: bool = True):
        """
        Update configuration.

        Args:
            config: New configuration
            save: Whether to save to file
        """
        self._config = config

        if save and self.config_path:
            try:
                config.save(self.config_path)
            except Exception as e:
                logger.error(f"Failed to save config to {self.config_path}: {e}")

    def reload(self):
        """Reload configuration from file."""
        self._config = None
        return self.get_config()


# Global config manager instance
_config_manager: Optional[FusionConfigManager] = None


def get_fusion_config_manager(config_path: Optional[Path] = None) -> FusionConfigManager:
    """
    Get or create global fusion config manager.

    Args:
        config_path: Path to config file (only used on first call)

    Returns:
        FusionConfigManager instance
    """
    global _config_manager

    if _config_manager is None:
        _config_manager = FusionConfigManager(config_path)

    return _config_manager
