#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Core Vault Manager for Jeyriku Vault

Provides secure credential storage and retrieval with multiple backend support.
"""

import os
import json
import getpass
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from .exceptions import (
    VaultError,
    VaultNotInitializedError,
    VaultLockedError,
    CredentialNotFoundError,
    InvalidCredentialError,
)
from .backends import get_backend, Backend


@dataclass
class Credential:
    """Represents a stored credential"""
    service: str
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    api_key: Optional[str] = None
    ssh_key: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        """Initialize timestamps and validate"""
        now = datetime.utcnow().isoformat()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now

        # At least one credential type must be provided
        if not any([self.username, self.password, self.token, self.api_key, self.ssh_key]):
            raise InvalidCredentialError(
                "At least one credential field (username, password, token, api_key, ssh_key) must be provided"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Credential':
        """Create from dictionary"""
        return cls(**data)

    def mask_sensitive(self) -> Dict[str, Any]:
        """Return credential with sensitive fields masked"""
        data = self.to_dict()
        if data.get('password'):
            data['password'] = '***MASKED***'
        if data.get('token'):
            data['token'] = '***MASKED***'
        if data.get('api_key'):
            data['api_key'] = '***MASKED***'
        if data.get('ssh_key'):
            data['ssh_key'] = '***MASKED***'
        return data


class VaultManager:
    """
    Centralized credential management system for Jeyriku applications.

    Features:
    - Multiple storage backends (SQLCipher, encrypted files, OS keyring)
    - Secure encryption using industry-standard algorithms
    - Master password protection
    - Credential versioning and audit trails
    - Import/Export capabilities
    - CLI and programmatic access

    Example:
        >>> vault = VaultManager()
        >>> vault.unlock("master_password")
        >>> vault.set_credential("librenms", token="abc123")
        >>> cred = vault.get_credential("librenms")
        >>> print(cred.token)
        abc123
    """

    def __init__(
        self,
        vault_path: Optional[str] = None,
        backend: str = "encrypted_file",
        auto_create: bool = True
    ):
        """
        Initialize Vault Manager.

        Args:
            vault_path: Path to vault storage. If None, uses default location
            backend: Storage backend to use ('sqlcipher', 'encrypted_file', 'keyring')
            auto_create: Automatically create vault if it doesn't exist
        """
        # Determine vault path
        if vault_path is None:
            vault_path = os.path.expanduser("~/.jeyriku/vault")

        self.vault_path = Path(vault_path)
        self.backend_name = backend
        self.backend: Optional[Backend] = None
        self._unlocked = False
        self._master_password: Optional[str] = None

        # Create vault directory if it doesn't exist
        if auto_create:
            self.vault_path.parent.mkdir(parents=True, exist_ok=True)

    def initialize(self, master_password: str) -> bool:
        """
        Initialize a new vault with a master password.

        Args:
            master_password: Master password for vault encryption

        Returns:
            True if successful

        Raises:
            VaultError: If vault already exists or initialization fails
        """
        if self.is_initialized():
            raise VaultError(f"Vault already initialized at {self.vault_path}")

        if len(master_password) < 8:
            raise InvalidCredentialError("Master password must be at least 8 characters")

        # Create backend
        self.backend = get_backend(self.backend_name, self.vault_path)

        # Initialize backend with master password
        result = self.backend.initialize(master_password)

        if result:
            self._master_password = master_password
            self._unlocked = True
            print(f"✅ Vault initialized successfully at {self.vault_path}")

        return result

    def is_initialized(self) -> bool:
        """Check if vault is initialized"""
        backend = get_backend(self.backend_name, self.vault_path)
        return backend.exists()

    def unlock(self, master_password: Optional[str] = None) -> bool:
        """
        Unlock the vault with master password.

        Args:
            master_password: Master password. If None, prompts user

        Returns:
            True if successfully unlocked

        Raises:
            VaultNotInitializedError: If vault not initialized
            AuthenticationError: If password is incorrect
        """
        if not self.is_initialized():
            raise VaultNotInitializedError(
                f"Vault not initialized. Run 'jeyriku-vault init' first"
            )

        if master_password is None:
            master_password = getpass.getpass("🔐 Master password: ")

        # Create and unlock backend
        self.backend = get_backend(self.backend_name, self.vault_path)

        if self.backend.unlock(master_password):
            self._master_password = master_password
            self._unlocked = True
            return True

        return False

    def lock(self):
        """Lock the vault"""
        if self.backend:
            self.backend.lock()
        self._unlocked = False
        self._master_password = None

    def is_unlocked(self) -> bool:
        """Check if vault is unlocked"""
        return self._unlocked

    def _ensure_unlocked(self):
        """Ensure vault is unlocked before operations"""
        if not self._unlocked:
            raise VaultLockedError("Vault is locked. Call unlock() first")

    def set_credential(
        self,
        service: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        api_key: Optional[str] = None,
        ssh_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Credential:
        """
        Store a credential in the vault.

        Args:
            service: Service name (e.g., 'librenms', 'nexus', 'jeysrv12')
            username: Username (optional)
            password: Password (optional)
            token: API token (optional)
            api_key: API key (optional)
            ssh_key: SSH private key (optional)
            metadata: Additional metadata (optional)

        Returns:
            Created Credential object

        Raises:
            VaultLockedError: If vault is locked
            InvalidCredentialError: If no credential data provided
        """
        self._ensure_unlocked()

        credential = Credential(
            service=service,
            username=username,
            password=password,
            token=token,
            api_key=api_key,
            ssh_key=ssh_key,
            metadata=metadata or {}
        )

        self.backend.store(service, credential.to_dict())
        return credential

    def get_credential(self, service: str) -> Credential:
        """
        Retrieve a credential from the vault.

        Args:
            service: Service name

        Returns:
            Credential object

        Raises:
            VaultLockedError: If vault is locked
            CredentialNotFoundError: If credential not found
        """
        self._ensure_unlocked()

        data = self.backend.retrieve(service)
        if data is None:
            raise CredentialNotFoundError(f"Credential for '{service}' not found")

        return Credential.from_dict(data)

    def delete_credential(self, service: str) -> bool:
        """
        Delete a credential from the vault.

        Args:
            service: Service name

        Returns:
            True if deleted, False if not found

        Raises:
            VaultLockedError: If vault is locked
        """
        self._ensure_unlocked()
        return self.backend.delete(service)

    def list_services(self) -> List[str]:
        """
        List all service names in the vault.

        Returns:
            List of service names

        Raises:
            VaultLockedError: If vault is locked
        """
        self._ensure_unlocked()
        return self.backend.list_services()

    def export_credentials(self, output_file: str, include_passwords: bool = False):
        """
        Export credentials to a JSON file.

        Args:
            output_file: Path to output file
            include_passwords: Whether to include sensitive data (default: False)

        Raises:
            VaultLockedError: If vault is locked
        """
        self._ensure_unlocked()

        credentials = {}
        for service in self.list_services():
            cred = self.get_credential(service)
            if include_passwords:
                credentials[service] = cred.to_dict()
            else:
                credentials[service] = cred.mask_sensitive()

        with open(output_file, 'w') as f:
            json.dump(credentials, f, indent=2)

        print(f"✅ Exported {len(credentials)} credentials to {output_file}")

    def import_credentials(self, input_file: str, overwrite: bool = False):
        """
        Import credentials from a JSON file.

        Args:
            input_file: Path to input file
            overwrite: Whether to overwrite existing credentials

        Raises:
            VaultLockedError: If vault is locked
        """
        self._ensure_unlocked()

        with open(input_file, 'r') as f:
            credentials = json.load(f)

        imported = 0
        skipped = 0

        for service, data in credentials.items():
            if not overwrite:
                try:
                    self.get_credential(service)
                    skipped += 1
                    continue
                except CredentialNotFoundError:
                    pass

            self.backend.store(service, data)
            imported += 1

        print(f"✅ Imported {imported} credentials ({skipped} skipped)")

    def change_master_password(self, old_password: str, new_password: str) -> bool:
        """
        Change the master password.

        Args:
            old_password: Current master password
            new_password: New master password

        Returns:
            True if successful

        Raises:
            AuthenticationError: If old password is incorrect
        """
        if len(new_password) < 8:
            raise InvalidCredentialError("New password must be at least 8 characters")

        # Verify old password
        if not self.unlock(old_password):
            return False

        # Export all credentials
        all_creds = {}
        for service in self.list_services():
            cred = self.get_credential(service)
            all_creds[service] = cred.to_dict()

        # Re-initialize with new password
        self.backend.delete_all()
        self.lock()

        self.initialize(new_password)

        # Restore all credentials
        for service, data in all_creds.items():
            self.backend.store(service, data)

        print("✅ Master password changed successfully")
        return True
