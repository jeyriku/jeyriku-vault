#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Command-line interface for Jeyriku Vault
"""

import sys
import argparse
import getpass
import json
from typing import Optional
from pathlib import Path

from .vault import VaultManager, Credential
from .exceptions import (
    VaultError,
    VaultNotInitializedError,
    VaultLockedError,
    CredentialNotFoundError,
)


def cmd_init(args):
    """Initialize a new vault"""
    vault = VaultManager(vault_path=args.vault_path, backend=args.backend)

    if vault.is_initialized():
        print(f"❌ Vault already initialized at {vault.vault_path}")
        return 1

    print("🔒 Creating new vault")
    password = getpass.getpass("Master password (min 8 chars): ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("❌ Passwords don't match")
        return 1

    try:
        vault.initialize(password)
        return 0
    except VaultError as e:
        print(f"❌ Error: {e}")
        return 1


def cmd_set(args):
    """Store a credential"""
    vault = VaultManager(vault_path=args.vault_path, backend=args.backend)

    try:
        vault.unlock()

        # Gather credential data
        username = args.username or (input("Username (optional): ") or None)

        password = None
        token = None
        api_key = None

        if args.password:
            password = args.password
        elif args.token:
            token = args.token
        elif args.api_key:
            api_key = args.api_key
        else:
            # Interactive mode
            choice = input("Credential type (1=password, 2=token, 3=api_key): ")
            if choice == '1':
                password = getpass.getpass("Password: ")
            elif choice == '2':
                token = getpass.getpass("Token: ")
            elif choice == '3':
                api_key = getpass.getpass("API Key: ")

        vault.set_credential(
            service=args.service,
            username=username,
            password=password,
            token=token,
            api_key=api_key,
            metadata={'description': args.description} if args.description else None
        )

        print(f"✅ Credential for '{args.service}' stored successfully")
        return 0

    except VaultError as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        vault.lock()


def cmd_get(args):
    """Retrieve a credential"""
    vault = VaultManager(vault_path=args.vault_path, backend=args.backend)

    try:
        vault.unlock()

        cred = vault.get_credential(args.service)

        if args.json:
            if args.show_password:
                print(json.dumps(cred.to_dict(), indent=2))
            else:
                print(json.dumps(cred.mask_sensitive(), indent=2))
        else:
            print(f"\n📋 Credential for: {cred.service}")
            print("=" * 50)

            if cred.username:
                print(f"Username: {cred.username}")

            if cred.password and args.show_password:
                print(f"Password: {cred.password}")
            elif cred.password:
                print("Password: ***MASKED***")

            if cred.token and args.show_password:
                print(f"Token: {cred.token}")
            elif cred.token:
                print("Token: ***MASKED***")

            if cred.api_key and args.show_password:
                print(f"API Key: {cred.api_key}")
            elif cred.api_key:
                print("API Key: ***MASKED***")

            if cred.metadata:
                print(f"Metadata: {json.dumps(cred.metadata, indent=2)}")

            print(f"\nCreated: {cred.created_at}")
            print(f"Updated: {cred.updated_at}")
            print()

        return 0

    except CredentialNotFoundError:
        print(f"❌ Credential for '{args.service}' not found")
        return 1
    except VaultError as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        vault.lock()


def cmd_list(args):
    """List all services"""
    vault = VaultManager(vault_path=args.vault_path, backend=args.backend)

    try:
        vault.unlock()

        services = vault.list_services()

        if not services:
            print("📭 No credentials stored in vault")
            return 0

        print(f"\n📋 Stored credentials ({len(services)}):")
        print("=" * 50)

        for service in services:
            if args.details:
                try:
                    cred = vault.get_credential(service)
                    types = []
                    if cred.username:
                        types.append("username")
                    if cred.password:
                        types.append("password")
                    if cred.token:
                        types.append("token")
                    if cred.api_key:
                        types.append("api_key")

                    print(f"  • {service} ({', '.join(types)})")
                except:
                    print(f"  • {service}")
            else:
                print(f"  • {service}")

        print()
        return 0

    except VaultError as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        vault.lock()


def cmd_delete(args):
    """Delete a credential"""
    vault = VaultManager(vault_path=args.vault_path, backend=args.backend)

    try:
        vault.unlock()

        if not args.yes:
            confirm = input(f"⚠️  Delete credential for '{args.service}'? (yes/no): ")
            if confirm.lower() != 'yes':
                print("Cancelled")
                return 0

        if vault.delete_credential(args.service):
            print(f"✅ Credential for '{args.service}' deleted")
            return 0
        else:
            print(f"❌ Credential for '{args.service}' not found")
            return 1

    except VaultError as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        vault.lock()


def cmd_export(args):
    """Export credentials to file"""
    vault = VaultManager(vault_path=args.vault_path, backend=args.backend)

    try:
        vault.unlock()
        vault.export_credentials(args.output, include_passwords=args.include_passwords)
        return 0

    except VaultError as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        vault.lock()


def cmd_import(args):
    """Import credentials from file"""
    vault = VaultManager(vault_path=args.vault_path, backend=args.backend)

    try:
        vault.unlock()
        vault.import_credentials(args.input, overwrite=args.overwrite)
        return 0

    except VaultError as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        vault.lock()


def cmd_change_password(args):
    """Change master password"""
    vault = VaultManager(vault_path=args.vault_path, backend=args.backend)

    try:
        old_password = getpass.getpass("Current master password: ")
        new_password = getpass.getpass("New master password (min 8 chars): ")
        confirm = getpass.getpass("Confirm new password: ")

        if new_password != confirm:
            print("❌ Passwords don't match")
            return 1

        if vault.change_master_password(old_password, new_password):
            return 0
        else:
            print("❌ Incorrect current password")
            return 1

    except VaultError as e:
        print(f"❌ Error: {e}")
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Jeyriku Vault - Secure Credential Management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize a new vault
  jeyriku-vault init

  # Store a credential with username/password
  jeyriku-vault set librenms --username admin --password secret123

  # Store an API token
  jeyriku-vault set infrahub --token abc123xyz

  # Retrieve a credential
  jeyriku-vault get librenms --show-password

  # List all stored credentials
  jeyriku-vault list --details

  # Export credentials (without passwords)
  jeyriku-vault export backup.json

  # Export with passwords (USE WITH CAUTION!)
  jeyriku-vault export backup.json --include-passwords
        """
    )

    parser.add_argument(
        '--vault-path',
        help='Path to vault (default: ~/.jeyriku/vault)'
    )

    parser.add_argument(
        '--backend',
        choices=['sqlcipher', 'encrypted_file'],
        default='encrypted_file',
        help='Storage backend (default: encrypted_file)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize a new vault')

    # Set command
    set_parser = subparsers.add_parser('set', help='Store a credential')
    set_parser.add_argument('service', help='Service name')
    set_parser.add_argument('--username', '-u', help='Username')
    set_parser.add_argument('--password', '-p', help='Password (not recommended, prompts if not provided)')
    set_parser.add_argument('--token', '-t', help='API token')
    set_parser.add_argument('--api-key', '-k', help='API key')
    set_parser.add_argument('--description', '-d', help='Description/notes')

    # Get command
    get_parser = subparsers.add_parser('get', help='Retrieve a credential')
    get_parser.add_argument('service', help='Service name')
    get_parser.add_argument('--show-password', '-s', action='store_true', help='Show password/token')
    get_parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')

    # List command
    list_parser = subparsers.add_parser('list', help='List all services')
    list_parser.add_argument('--details', '-d', action='store_true', help='Show credential types')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a credential')
    delete_parser.add_argument('service', help='Service name')
    delete_parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export credentials to file')
    export_parser.add_argument('output', help='Output file path')
    export_parser.add_argument('--include-passwords', action='store_true', help='Include sensitive data')

    # Import command
    import_parser = subparsers.add_parser('import', help='Import credentials from file')
    import_parser.add_argument('input', help='Input file path')
    import_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing credentials')

    # Change password command
    change_pw_parser = subparsers.add_parser('change-password', help='Change master password')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Command routing
    commands = {
        'init': cmd_init,
        'set': cmd_set,
        'get': cmd_get,
        'list': cmd_list,
        'delete': cmd_delete,
        'export': cmd_export,
        'import': cmd_import,
        'change-password': cmd_change_password,
    }

    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
