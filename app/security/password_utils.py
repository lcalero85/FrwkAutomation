"""
Password hashing utilities for AutoTest Pro Framework.

This module intentionally avoids passlib/bcrypt to prevent compatibility issues
with Python 3.13 and bcrypt backend changes on Windows.

Format stored in DB:
pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
"""

from __future__ import annotations

import hashlib
import hmac
import os

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 260_000
SALT_BYTES = 16


def hash_password(password: str) -> str:
    """Return a secure PBKDF2-SHA256 hash for a plain password."""
    if password is None:
        raise ValueError("Password cannot be None")

    password_bytes = password.encode("utf-8")
    salt = os.urandom(SALT_BYTES)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password_bytes,
        salt,
        ITERATIONS,
    )
    return f"{ALGORITHM}${ITERATIONS}${salt.hex()}${password_hash.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Validate a plain password against a stored PBKDF2-SHA256 hash."""
    if not password or not password_hash:
        return False

    try:
        algorithm, iterations_str, salt_hex, stored_hash_hex = password_hash.split("$", 3)
        if algorithm != ALGORITHM:
            return False

        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        stored_hash = bytes.fromhex(stored_hash_hex)

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )
        return hmac.compare_digest(calculated_hash, stored_hash)
    except Exception:
        return False
