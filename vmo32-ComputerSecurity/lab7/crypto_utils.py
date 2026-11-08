from __future__ import annotations

import base64
import hashlib
import hmac
import os
from pathlib import Path

try:
    from cryptography.fernet import Fernet  # type: ignore
except ImportError:  # pragma: no cover
    Fernet = None


def load_or_create_key(key_path: Path) -> bytes:
    """Load encryption key from disk or create a new one."""
    if key_path.exists():
        return key_path.read_bytes()

    if Fernet is not None:
        key = Fernet.generate_key()
    else:
        key = base64.urlsafe_b64encode(os.urandom(32))

    key_path.write_bytes(key)
    return key


def _keystream(raw_key: bytes, nonce: bytes, length: int) -> bytes:
    out = bytearray()
    counter = 0
    while len(out) < length:
        block = hashlib.sha256(raw_key + nonce + counter.to_bytes(4, "big")).digest()
        out.extend(block)
        counter += 1
    return bytes(out[:length])


def _fallback_encrypt(data: bytes, key: bytes) -> bytes:
    raw_key = base64.urlsafe_b64decode(key)
    nonce = os.urandom(16)
    stream = _keystream(raw_key, nonce, len(data))
    cipher = bytes(a ^ b for a, b in zip(data, stream))
    tag = hmac.new(raw_key, nonce + cipher, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(nonce + tag + cipher)


def _fallback_decrypt(data: bytes, key: bytes) -> bytes:
    raw_key = base64.urlsafe_b64decode(key)
    payload = base64.urlsafe_b64decode(data)
    nonce, tag, cipher = payload[:16], payload[16:48], payload[48:]
    calc_tag = hmac.new(raw_key, nonce + cipher, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, calc_tag):
        raise ValueError("Encrypted data integrity check failed")
    stream = _keystream(raw_key, nonce, len(cipher))
    return bytes(a ^ b for a, b in zip(cipher, stream))


def encrypt_bytes(data: bytes, key: bytes) -> bytes:
    if Fernet is not None:
        return Fernet(key).encrypt(data)
    return _fallback_encrypt(data, key)


def decrypt_bytes(data: bytes, key: bytes) -> bytes:
    if Fernet is not None:
        return Fernet(key).decrypt(data)
    return _fallback_decrypt(data, key)
