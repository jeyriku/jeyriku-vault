#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Exception classes for Jeyriku Vault
"""


class VaultError(Exception):
    """Base exception for all vault-related errors"""
    pass


class VaultNotInitializedError(VaultError):
    """Raised when attempting to use a vault that hasn't been initialized"""
    pass


class VaultLockedError(VaultError):
    """Raised when attempting to access a locked vault"""
    pass


class CredentialNotFoundError(VaultError):
    """Raised when a requested credential is not found"""
    pass


class InvalidCredentialError(VaultError):
    """Raised when credential data is invalid"""
    pass


class BackendError(VaultError):
    """Raised when a storage backend encounters an error"""
    pass


class AuthenticationError(VaultError):
    """Raised when vault authentication fails"""
    pass
