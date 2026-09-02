"""
Cryptographic SHA-256 Hashing Utilities.

Provides deterministic SHA-256 hashing for raw bytes, strings, local files,
and structured dictionaries. Uses standard library hashlib only. Zero cloud dependencies.
"""

import hashlib
import json
from pathlib import Path
from typing import Union, Any


def hash_bytes(data: bytes) -> str:
    """Calculate hexadecimal SHA-256 hash of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def hash_text(text: str, encoding: str = "utf-8") -> str:
    """Calculate hexadecimal SHA-256 hash of a string."""
    return hashlib.sha256(text.encode(encoding)).hexdigest()


def hash_file(filepath: Union[str, Path], chunk_size: int = 65536) -> str:
    """
    Calculate hexadecimal SHA-256 hash of a local file in chunks.
    Efficient for files of any size.
    """
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"File not found for hashing: {filepath}")

    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()


def hash_dict(data: dict[str, Any]) -> str:
    """
    Deterministically hash a dictionary by sorting keys before JSON serialization.
    """
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hash_text(serialized)


def verify_integrity(actual_hash: str, expected_hash: str) -> bool:
    """
    Compare two SHA-256 hash strings (case-insensitive).
    """
    return actual_hash.strip().lower() == expected_hash.strip().lower()
