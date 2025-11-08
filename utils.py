"""
Betty Phipps

11/08/2025

Module 11: Build Role Based Access Control

Due Sunday September 9

explanation of file: Cryptographic utilities and validation helpers.
"""

import os
import pathlib
from datetime import datetime
from typing import Optional

from cryptography.fernet import Fernet

# Module-level cache so we do not reload the key repeatedly.
_FERNET_INSTANCE: Optional[Fernet] = None


def get_project_root() -> pathlib.Path:
    """
    Return the absolute path of the project root directory.
    This helper supports locating files while keeping code tidy.
    """
    return pathlib.Path(__file__).resolve().parent


def _load_fernet_key() -> bytes:
    """
    Retrieve the Fernet key either from the environment or from a key file.

    Priority order:
        1. Environment variable FERNET_KEY.
        2. File named key.key at the project root.

    Raises:
        RuntimeError: if the key cannot be located from either source.
    """
    env_key = os.environ.get("FERNET_KEY")
    if env_key:
        # Environment variables are str; encode to bytes for Fernet.
        return env_key.encode("utf-8")

    key_path = get_project_root() / "key.key"
    if key_path.exists():
        return key_path.read_bytes()

    raise RuntimeError(
        "Fernet key not found. Set FERNET_KEY or run init_db.py to generate key.key."
    )


def get_fernet() -> Fernet:
    """
    Return a singleton Fernet instance, loading the key as needed.
    """
    global _FERNET_INSTANCE
    if _FERNET_INSTANCE is None:
        _FERNET_INSTANCE = Fernet(_load_fernet_key())
    return _FERNET_INSTANCE


def encrypt_text(plain: str) -> bytes:
    """
    Encrypt the provided plain-text string, returning ciphertext bytes.
    """
    if plain is None:
        raise ValueError("Cannot encrypt None value.")
    fernet = get_fernet()
    # Fernet expects bytes; encode using UTF-8.
    return fernet.encrypt(plain.strip().encode("utf-8"))


def decrypt_text(cipher: bytes) -> str:
    """
    Decrypt ciphertext bytes back into a UTF-8 string.
    """
    if cipher is None:
        raise ValueError("Cannot decrypt None value.")
    fernet = get_fernet()
    return fernet.decrypt(cipher).decode("utf-8")


def is_valid_date(date_str: str) -> bool:
    """
    Validate that the supplied string is a non-empty date in YYYY-MM-DD format.
    """
    if not date_str or not date_str.strip():
        return False
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_positive_number(value: str) -> bool:
    """
    Validate that the string represents a positive numeric value.
    """
    if not value or not value.strip():
        return False
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False

