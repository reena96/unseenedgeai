"""Secret management using Google Cloud Secret Manager with fallback to environment variables."""

import os
import logging
from typing import Optional, Dict
from functools import lru_cache

logger = logging.getLogger(__name__)

# Try to import GCP Secret Manager
try:
    from google.cloud import secretmanager

    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    logger.warning(
        "Google Cloud Secret Manager not available. Using environment variables only."
    )


class SecretManager:
    """Manager for retrieving secrets from GCP Secret Manager or environment variables."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        use_gcp: bool = True,
    ):
        """
        Initialize secret manager.

        Args:
            project_id: GCP project ID (defaults to environment variable)
            use_gcp: Whether to use GCP Secret Manager (falls back to env vars if False or unavailable)
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.use_gcp = use_gcp and GCP_AVAILABLE and self.project_id is not None

        if self.use_gcp:
            try:
                self.client = secretmanager.SecretManagerServiceClient()
                logger.info(
                    f"Initialized GCP Secret Manager for project: {self.project_id}"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to initialize GCP Secret Manager: {e}. Using env vars."
                )
                self.use_gcp = False
                self.client = None
        else:
            self.client = None
            logger.info("Using environment variables for secrets")

        # Cache for secrets to avoid repeated API calls
        self._cache: Dict[str, str] = {}

    def _get_secret_from_gcp(
        self, secret_name: str, version: str = "latest"
    ) -> Optional[str]:
        """
        Get secret from GCP Secret Manager.

        Args:
            secret_name: Name of the secret
            version: Version of the secret (default: "latest")

        Returns:
            Secret value or None if not found
        """
        if not self.use_gcp or not self.client:
            return None

        try:
            # Build the resource name
            name = (
                f"projects/{self.project_id}/secrets/{secret_name}/versions/{version}"
            )

            # Access the secret version
            response = self.client.access_secret_version(request={"name": name})

            # Decode the secret payload
            secret_value = response.payload.data.decode("UTF-8")

            logger.info(f"Retrieved secret '{secret_name}' from GCP Secret Manager")
            return secret_value

        except Exception as e:
            logger.warning(f"Failed to retrieve secret '{secret_name}' from GCP: {e}")
            return None

    def get_secret(
        self,
        secret_name: str,
        env_var_name: Optional[str] = None,
        default: Optional[str] = None,
        required: bool = False,
    ) -> Optional[str]:
        """
        Get secret from GCP Secret Manager or environment variable.

        Lookup order:
        1. Check cache
        2. Try GCP Secret Manager (if enabled)
        3. Try environment variable
        4. Return default value

        Args:
            secret_name: Name of secret in GCP Secret Manager
            env_var_name: Name of environment variable (defaults to secret_name.upper())
            default: Default value if secret not found
            required: Whether to raise exception if secret not found

        Returns:
            Secret value

        Raises:
            ValueError: If required=True and secret not found
        """
        # Use secret_name as env var name if not specified
        if env_var_name is None:
            env_var_name = secret_name.upper()

        # Check cache first
        cache_key = f"{secret_name}:{env_var_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        secret_value = None

        # Try GCP Secret Manager
        if self.use_gcp:
            secret_value = self._get_secret_from_gcp(secret_name)

        # Fall back to environment variable
        if secret_value is None:
            secret_value = os.getenv(env_var_name)
            if secret_value:
                logger.debug(f"Using environment variable '{env_var_name}' for secret")

        # Use default if still not found
        if secret_value is None:
            secret_value = default

        # Raise exception if required and not found
        if secret_value is None and required:
            raise ValueError(
                f"Required secret '{secret_name}' not found in GCP Secret Manager "
                f"or environment variable '{env_var_name}'"
            )

        # Cache the result
        if secret_value is not None:
            self._cache[cache_key] = secret_value

        return secret_value

    def clear_cache(self):
        """Clear the secrets cache."""
        self._cache.clear()
        logger.info("Cleared secrets cache")


# Global secret manager instance
_secret_manager: Optional[SecretManager] = None


def get_secret_manager(
    project_id: Optional[str] = None,
    use_gcp: bool = True,
) -> SecretManager:
    """
    Get or create global secret manager instance.

    Args:
        project_id: GCP project ID (only used on first call)
        use_gcp: Whether to use GCP Secret Manager

    Returns:
        SecretManager instance
    """
    global _secret_manager

    if _secret_manager is None:
        _secret_manager = SecretManager(project_id=project_id, use_gcp=use_gcp)

    return _secret_manager


# Convenience functions for common secrets
@lru_cache(maxsize=1)
def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key from secrets."""
    manager = get_secret_manager()
    return manager.get_secret(
        secret_name="openai-api-key",
        env_var_name="OPENAI_API_KEY",
        required=False,
    )


@lru_cache(maxsize=1)
def get_database_url() -> str:
    """Get database URL from secrets."""
    manager = get_secret_manager()
    return manager.get_secret(
        secret_name="database-url",
        env_var_name="DATABASE_URL",
        required=True,
    )


@lru_cache(maxsize=1)
def get_redis_url() -> Optional[str]:
    """Get Redis URL from secrets."""
    manager = get_secret_manager()
    return manager.get_secret(
        secret_name="redis-url",
        env_var_name="REDIS_URL",
        required=False,
    )


@lru_cache(maxsize=1)
def get_jwt_secret() -> str:
    """Get JWT secret key from secrets."""
    manager = get_secret_manager()
    return manager.get_secret(
        secret_name="jwt-secret-key",
        env_var_name="SECRET_KEY",
        required=True,
    )


def refresh_secrets():
    """Refresh all cached secrets."""
    # Clear LRU caches
    get_openai_api_key.cache_clear()
    get_database_url.cache_clear()
    get_redis_url.cache_clear()
    get_jwt_secret.cache_clear()

    # Clear secret manager cache
    manager = get_secret_manager()
    manager.clear_cache()

    logger.info("Refreshed all cached secrets")
