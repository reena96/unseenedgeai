"""Model versioning and metadata management."""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ModelMetadata:
    """Metadata for a trained model."""

    skill_type: str
    version: str
    training_date: str  # ISO format
    model_type: str  # e.g., "XGBRegressor"
    hyperparameters: Dict[str, Any]
    performance_metrics: Dict[str, float]
    feature_count: int
    training_samples: int
    model_checksum: str  # SHA256 hash of model file

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelMetadata":
        """Create from dictionary."""
        return cls(**data)


class ModelRegistry:
    """Registry for tracking model versions and metadata."""

    def __init__(self, models_dir: str = "./models"):
        """
        Initialize model registry.

        Args:
            models_dir: Directory containing models
        """
        self.models_dir = Path(models_dir)
        self.registry_file = self.models_dir / "model_registry.json"
        self.registry: Dict[str, ModelMetadata] = {}

        if self.registry_file.exists():
            self._load_registry()

    def _load_registry(self):
        """Load registry from disk."""
        try:
            with open(self.registry_file, "r") as f:
                data = json.load(f)

            for skill_type, metadata_dict in data.items():
                self.registry[skill_type] = ModelMetadata.from_dict(metadata_dict)
        except Exception as e:
            print(f"Warning: Failed to load model registry: {e}")
            self.registry = {}

    def _save_registry(self):
        """Save registry to disk."""
        self.models_dir.mkdir(parents=True, exist_ok=True)

        data = {
            skill_type: metadata.to_dict()
            for skill_type, metadata in self.registry.items()
        }

        with open(self.registry_file, "w") as f:
            json.dump(data, f, indent=2)

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def register_model(
        self,
        skill_type: str,
        version: str,
        model_type: str,
        hyperparameters: Dict[str, Any],
        performance_metrics: Dict[str, float],
        feature_count: int,
        training_samples: int,
    ):
        """
        Register a trained model.

        Args:
            skill_type: Skill type (e.g., "empathy")
            version: Model version (e.g., "1.0.0")
            model_type: Type of model (e.g., "XGBRegressor")
            hyperparameters: Model hyperparameters
            performance_metrics: Performance metrics from evaluation
            feature_count: Number of features
            training_samples: Number of training samples
        """
        model_path = self.models_dir / f"{skill_type}_model.pkl"

        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        # Calculate checksum
        checksum = self._calculate_checksum(model_path)

        # Create metadata
        metadata = ModelMetadata(
            skill_type=skill_type,
            version=version,
            training_date=datetime.utcnow().isoformat(),
            model_type=model_type,
            hyperparameters=hyperparameters,
            performance_metrics=performance_metrics,
            feature_count=feature_count,
            training_samples=training_samples,
            model_checksum=checksum,
        )

        # Store in registry
        self.registry[skill_type] = metadata
        self._save_registry()

    def get_model_metadata(self, skill_type: str) -> Optional[ModelMetadata]:
        """
        Get metadata for a model.

        Args:
            skill_type: Skill type

        Returns:
            ModelMetadata or None if not found
        """
        return self.registry.get(skill_type)

    def verify_model_integrity(self, skill_type: str) -> bool:
        """
        Verify model file integrity using checksum.

        Args:
            skill_type: Skill type

        Returns:
            True if checksum matches, False otherwise
        """
        metadata = self.get_model_metadata(skill_type)
        if not metadata:
            return False

        model_path = self.models_dir / f"{skill_type}_model.pkl"
        if not model_path.exists():
            return False

        current_checksum = self._calculate_checksum(model_path)
        return current_checksum == metadata.model_checksum

    def list_models(self) -> Dict[str, ModelMetadata]:
        """
        List all registered models.

        Returns:
            Dictionary mapping skill types to metadata
        """
        return self.registry.copy()

    def get_model_version(self, skill_type: str) -> Optional[str]:
        """
        Get version string for a model.

        Args:
            skill_type: Skill type

        Returns:
            Version string or None
        """
        metadata = self.get_model_metadata(skill_type)
        return metadata.version if metadata else None
