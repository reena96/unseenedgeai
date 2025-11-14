"""Data encryption service for PII protection."""

import os
import base64
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)


class EncryptionService:
    """Service for encrypting/decrypting sensitive data."""

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption service.

        Args:
            encryption_key: Base64-encoded encryption key. If not provided,
                          will use ENCRYPTION_KEY from environment.
        """
        if encryption_key is None:
            encryption_key = os.getenv("ENCRYPTION_KEY")

        if not encryption_key:
            # For development only - generate a key
            logger.warning(
                "No ENCRYPTION_KEY set. Generating temporary key. "
                "DO NOT USE IN PRODUCTION!"
            )
            encryption_key = Fernet.generate_key().decode()

        try:
            self.cipher = Fernet(encryption_key.encode())
        except Exception as e:
            raise ValueError(f"Invalid encryption key: {e}")

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string.

        Args:
            plaintext: String to encrypt

        Returns:
            Base64-encoded encrypted string
        """
        if not plaintext:
            return ""

        try:
            encrypted_bytes = self.cipher.encrypt(plaintext.encode())
            return base64.b64encode(encrypted_bytes).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a string.

        Args:
            ciphertext: Base64-encoded encrypted string

        Returns:
            Decrypted plaintext string
        """
        if not ciphertext:
            return ""

        try:
            encrypted_bytes = base64.b64decode(ciphertext.encode())
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise

    @staticmethod
    def generate_key() -> str:
        """
        Generate a new encryption key.

        Returns:
            Base64-encoded encryption key
        """
        return Fernet.generate_key().decode()

    @staticmethod
    def derive_key_from_password(password: str, salt: bytes = None) -> tuple:
        """
        Derive an encryption key from a password using PBKDF2.

        Args:
            password: Password to derive key from
            salt: Salt for key derivation (generated if not provided)

        Returns:
            Tuple of (key, salt)
        """
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )

        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key.decode(), salt


# Global encryption service instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """Get or create global encryption service instance."""
    global _encryption_service

    if _encryption_service is None:
        _encryption_service = EncryptionService()

    return _encryption_service


def encrypt_field(value: str) -> str:
    """
    Convenience function to encrypt a field value.

    Args:
        value: Value to encrypt

    Returns:
        Encrypted value
    """
    service = get_encryption_service()
    return service.encrypt(value)


def decrypt_field(value: str) -> str:
    """
    Convenience function to decrypt a field value.

    Args:
        value: Encrypted value

    Returns:
        Decrypted value
    """
    service = get_encryption_service()
    return service.decrypt(value)


# SQLAlchemy custom type for encrypted fields
from sqlalchemy.types import TypeDecorator, String


class EncryptedString(TypeDecorator):
    """SQLAlchemy type for automatically encrypting/decrypting string fields."""

    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Encrypt value before storing in database."""
        if value is None:
            return None
        return encrypt_field(value)

    def process_result_value(self, value, dialect):
        """Decrypt value when reading from database."""
        if value is None:
            return None
        return decrypt_field(value)


# Example usage in models:
"""
from app.core.encryption import EncryptedString

class Student(Base):
    __tablename__ = "students"

    id = Column(String(36), primary_key=True)
    name = Column(EncryptedString(255), nullable=False)  # Automatically encrypted
    email = Column(EncryptedString(255), nullable=True)  # Automatically encrypted
    grade_level = Column(Integer, nullable=False)  # Not encrypted (not PII)
"""
