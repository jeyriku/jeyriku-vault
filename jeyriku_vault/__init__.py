#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Jeyriku Vault - Secure Credential Management System

A centralized, encrypted credential storage system for Jeyriku network automation tools.
Supports multiple backends (SQLCipher, encrypted files, OS keyring) and provides
a unified API for managing credentials across all applications.

Copyright (c) 2026 Jeyriku.net
"""

__version__ = '1.0.0'
__author__ = 'Jeremie Rouzet'
__email__ = 'contact@jeyriku.net'
__copyright__ = 'Copyright (c) 2026 Jeyriku.net'

from .vault import VaultManager, Credential
from .exceptions import (
    VaultError,
    VaultNotInitializedError,
    VaultLockedError,
    CredentialNotFoundError,
    InvalidCredentialError,
)

__all__ = [
    'VaultManager',
    'Credential',
    'VaultError',
    'VaultNotInitializedError',
    'VaultLockedError',
    'CredentialNotFoundError',
    'InvalidCredentialError',
]
