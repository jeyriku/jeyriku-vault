#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Storage backends for Jeyriku Vault

Supports multiple secure storage mechanisms:
- SQLCipher: Encrypted SQLite database
- Encrypted File: AES-256 encrypted JSON file
- OS Keyring: Platform native keyring (macOS Keychain, Windows Credential Manager, etc.)
"""

import os
import json
import hashlib
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path

from .exceptions import BackendError, AuthenticationError


class Backend(ABC):
    """Abstract base class for storage backends"""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path

    @abstractmethod
    def exists(self) -> bool:
        """Check if vault exists"""
        pass

    @abstractmethod
    def initialize(self, master_password: str) -> bool:
        """Initialize the vault"""
        pass

    @abstractmethod
    def unlock(self, master_password: str) -> bool:
        """Unlock the vault"""
        pass

    @abstractmethod
    def lock(self):
        """Lock the vault"""
        pass

    @abstractmethod
    def store(self, service: str, data: Dict[str, Any]):
        """Store a credential"""
        pass

    @abstractmethod
    def retrieve(self, service: str) -> Optional[Dict[str, Any]]:
        """Retrieve a credential"""
        pass

    @abstractmethod
    def delete(self, service: str) -> bool:
        """Delete a credential"""
        pass

    @abstractmethod
    def list_services(self) -> List[str]:
        """List all service names"""
        pass

    @abstractmethod
    def delete_all(self):
        """Delete all credentials"""
        pass


class SQLCipherBackend(Backend):
    """
    SQLCipher-based backend using encrypted SQLite.
    Provides strong encryption with minimal dependencies.
    """

    def __init__(self, vault_path: Path):
        super().__init__(vault_path)
        self.db_path = vault_path.parent / f"{vault_path.name}.db"
        self.connection = None

    def exists(self) -> bool:
        return self.db_path.exists()

    def initialize(self, master_password: str) -> bool:
        try:
            import pysqlcipher3.dbapi2 as sqlcipher
        except ImportError:
            raise BackendError(
                "pysqlcipher3 not installed. Install with: pip install pysqlcipher3"
            )

        try:
            # Create encrypted database
            conn = sqlcipher.connect(str(self.db_path))
            conn.execute(f"PRAGMA key = '{master_password}'")

            # Create credentials table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS credentials (
                    service TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create audit log table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service TEXT,
                    action TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            self.connection = conn
            return True

        except Exception as e:
            raise BackendError(f"Failed to initialize SQLCipher backend: {e}")

    def unlock(self, master_password: str) -> bool:
        try:
            import pysqlcipher3.dbapi2 as sqlcipher
        except ImportError:
            raise BackendError("pysqlcipher3 not installed")

        try:
            conn = sqlcipher.connect(str(self.db_path))
            conn.execute(f"PRAGMA key = '{master_password}'")

            # Test if password is correct by trying to select
            conn.execute("SELECT count(*) FROM credentials")

            self.connection = conn
            return True

        except Exception:
            raise AuthenticationError("Incorrect master password")

    def lock(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def store(self, service: str, data: Dict[str, Any]):
        if not self.connection:
            raise BackendError("Vault not unlocked")

        try:
            data_json = json.dumps(data)

            self.connection.execute("""
                INSERT OR REPLACE INTO credentials (service, data, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (service, data_json))

            # Log action
            self.connection.execute(
                "INSERT INTO audit_log (service, action) VALUES (?, ?)",
                (service, "STORE")
            )

            self.connection.commit()

        except Exception as e:
            raise BackendError(f"Failed to store credential: {e}")

    def retrieve(self, service: str) -> Optional[Dict[str, Any]]:
        if not self.connection:
            raise BackendError("Vault not unlocked")

        try:
            cursor = self.connection.execute(
                "SELECT data FROM credentials WHERE service = ?",
                (service,)
            )
            row = cursor.fetchone()

            if row:
                # Log action
                self.connection.execute(
                    "INSERT INTO audit_log (service, action) VALUES (?, ?)",
                    (service, "RETRIEVE")
                )
                self.connection.commit()
                return json.loads(row[0])

            return None

        except Exception as e:
            raise BackendError(f"Failed to retrieve credential: {e}")

    def delete(self, service: str) -> bool:
        if not self.connection:
            raise BackendError("Vault not unlocked")

        try:
            cursor = self.connection.execute(
                "DELETE FROM credentials WHERE service = ?",
                (service,)
            )

            deleted = cursor.rowcount > 0

            if deleted:
                self.connection.execute(
                    "INSERT INTO audit_log (service, action) VALUES (?, ?)",
                    (service, "DELETE")
                )

            self.connection.commit()
            return deleted

        except Exception as e:
            raise BackendError(f"Failed to delete credential: {e}")

    def list_services(self) -> List[str]:
        if not self.connection:
            raise BackendError("Vault not unlocked")

        try:
            cursor = self.connection.execute("SELECT service FROM credentials ORDER BY service")
            return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            raise BackendError(f"Failed to list services: {e}")

    def delete_all(self):
        if not self.connection:
            raise BackendError("Vault not unlocked")

        try:
            self.connection.execute("DELETE FROM credentials")
            self.connection.execute(
                "INSERT INTO audit_log (service, action) VALUES (?, ?)",
                (None, "DELETE_ALL")
            )
            self.connection.commit()

        except Exception as e:
            raise BackendError(f"Failed to delete all credentials: {e}")


class EncryptedFileBackend(Backend):
    """
    Simple encrypted file backend using Fernet (AES-128 CBC).
    Good for portability and when SQLCipher is not available.
    """

    def __init__(self, vault_path: Path):
        super().__init__(vault_path)
        self.file_path = vault_path.parent / f"{vault_path.name}.enc"
        self.fernet = None
        self._data: Dict[str, Any] = {}

    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.backends import default_backend
        import base64

        # Use a fixed salt (in production, store this separately)
        salt = b'jeyriku_vault_salt_v1'

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )

        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def exists(self) -> bool:
        return self.file_path.exists()

    def initialize(self, master_password: str) -> bool:
        try:
            from cryptography.fernet import Fernet
        except ImportError:
            raise BackendError(
                "cryptography not installed. Install with: pip install cryptography"
            )

        try:
            key = self._derive_key(master_password)
            self.fernet = Fernet(key)
            self._data = {}
            self._save()
            return True

        except Exception as e:
            raise BackendError(f"Failed to initialize encrypted file backend: {e}")

    def unlock(self, master_password: str) -> bool:
        try:
            from cryptography.fernet import Fernet, InvalidToken
        except ImportError:
            raise BackendError("cryptography not installed")

        try:
            key = self._derive_key(master_password)
            self.fernet = Fernet(key)
            self._load()
            return True

        except InvalidToken:
            raise AuthenticationError("Incorrect master password")
        except Exception as e:
            raise BackendError(f"Failed to unlock vault: {e}")

    def lock(self):
        self.fernet = None
        self._data = {}

    def _save(self):
        """Save encrypted data to file"""
        if not self.fernet:
            raise BackendError("Vault not unlocked")

        try:
            data_json = json.dumps(self._data)
            encrypted = self.fernet.encrypt(data_json.encode())

            with open(self.file_path, 'wb') as f:
                f.write(encrypted)

        except Exception as e:
            raise BackendError(f"Failed to save vault: {e}")

    def _load(self):
        """Load encrypted data from file"""
        if not self.fernet:
            raise BackendError("Vault not unlocked")

        try:
            with open(self.file_path, 'rb') as f:
                encrypted = f.read()

            decrypted = self.fernet.decrypt(encrypted)
            self._data = json.loads(decrypted.decode())

        except Exception as e:
            raise BackendError(f"Failed to load vault: {e}")

    def store(self, service: str, data: Dict[str, Any]):
        if not self.fernet:
            raise BackendError("Vault not unlocked")

        self._data[service] = data
        self._save()

    def retrieve(self, service: str) -> Optional[Dict[str, Any]]:
        if not self.fernet:
            raise BackendError("Vault not unlocked")

        return self._data.get(service)

    def delete(self, service: str) -> bool:
        if not self.fernet:
            raise BackendError("Vault not unlocked")

        if service in self._data:
            del self._data[service]
            self._save()
            return True

        return False

    def list_services(self) -> List[str]:
        if not self.fernet:
            raise BackendError("Vault not unlocked")

        return sorted(self._data.keys())

    def delete_all(self):
        if not self.fernet:
            raise BackendError("Vault not unlocked")

        self._data = {}
        self._save()


def get_backend(backend_name: str, vault_path: Path) -> Backend:
    """
    Factory function to get the appropriate backend.

    Args:
        backend_name: Name of backend ('sqlcipher' or 'encrypted_file')
        vault_path: Path to vault storage

    Returns:
        Backend instance

    Raises:
        ValueError: If backend name is unknown
    """
    backends = {
        'sqlcipher': SQLCipherBackend,
        'encrypted_file': EncryptedFileBackend,
    }

    if backend_name not in backends:
        raise ValueError(
            f"Unknown backend '{backend_name}'. "
            f"Available backends: {', '.join(backends.keys())}"
        )

    return backends[backend_name](vault_path)
