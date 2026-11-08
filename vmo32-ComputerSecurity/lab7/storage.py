from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from crypto_utils import decrypt_bytes, encrypt_bytes, load_or_create_key


class UserStorage:
    def __init__(self, users_file: Path, key_file: Path):
        self.users_file = users_file
        self.key_file = key_file

    def load_users(self) -> Dict[str, str]:
        """Return user -> key fingerprint mapping."""
        if not self.users_file.exists():
            return {}

        key = load_or_create_key(self.key_file)
        encrypted = self.users_file.read_bytes()
        if not encrypted:
            return {}

        decrypted = decrypt_bytes(encrypted, key)
        data = json.loads(decrypted.decode("utf-8"))
        return data if isinstance(data, dict) else {}

    def save_users(self, users: Dict[str, str]) -> None:
        key = load_or_create_key(self.key_file)
        serialized = json.dumps(users, ensure_ascii=False, indent=2).encode("utf-8")
        encrypted = encrypt_bytes(serialized, key)
        self.users_file.write_bytes(encrypted)
