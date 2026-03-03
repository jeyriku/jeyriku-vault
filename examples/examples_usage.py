#!/usr/bin/env python3
"""
Real-world usage examples for Jeyriku Vault in different applications
"""

# Example 1: Simple credential retrieval
def example_basic_usage():
    """Most basic usage pattern"""
    from jeyriku_vault import VaultManager

    vault = VaultManager()
    vault.unlock()

    try:
        # Get a credential
        cred = vault.get_credential('jeysrv12')
        print(f"Username: {cred.username}")
        print(f"Password: {'*' * len(cred.password)}")
    finally:
        vault.lock()


# Example 2: NexusPush integration
def example_nexuspush():
    """How to use vault in NexusPush"""
    from jeyriku_vault import VaultManager

    vault = VaultManager()
    vault.unlock()

    try:
        # Get credentials for both services
        jeysrv12 = vault.get_credential('jeysrv12')
        nexus = vault.get_credential('nexus')

        # Use in your application
        config = {
            'jeysrv12': {
                'host': 'jeysrv12',
                'username': jeysrv12.username,
                'password': jeysrv12.password,
                'path': '/home/jeyriku/Nexus/net/tftp'
            },
            'nexus': {
                'url': nexus.metadata.get('url', 'http://jeysrv12:8081'),
                'username': nexus.username,
                'password': nexus.password,
                'repository': nexus.metadata.get('repository', 'network-binaries')
            }
        }

        return config
    finally:
        vault.lock()


# Example 3: NetAlps Probe with LibreNMS
def example_netalps_probe():
    """Integrate with NetAlps Probe for network discovery"""
    from jeyriku_vault import VaultManager

    vault = VaultManager()
    vault.unlock()

    try:
        # Get API tokens
        librenms = vault.get_credential('librenms')
        infrahub = vault.get_credential('infrahub')

        # Configure discovery
        discovery_config = {
            'librenms': {
                'url': librenms.metadata.get('url'),
                'token': librenms.token
            },
            'infrahub': {
                'url': infrahub.metadata.get('url'),
                'api_token': infrahub.token
            }
        }

        return discovery_config
    finally:
        vault.lock()


# Example 4: PyATS testbed credentials
def example_pyats_testbed():
    """Generate PyATS testbed with vault credentials"""
    from jeyriku_vault import VaultManager
    import yaml

    vault = VaultManager()
    vault.unlock()

    try:
        cisco = vault.get_credential('cisco_devices')

        testbed = {
            'devices': {
                'router1': {
                    'type': 'router',
                    'os': 'iosxe',
                    'connections': {
                        'cli': {
                            'protocol': 'ssh',
                            'ip': '192.168.1.1'
                        }
                    },
                    'credentials': {
                        'default': {
                            'username': cisco.username,
                            'password': cisco.password
                        },
                        'enable': {
                            'password': cisco.metadata.get('enable_password')
                        }
                    }
                }
            }
        }

        return testbed
    finally:
        vault.lock()


# Example 5: Ansible dynamic inventory
def example_ansible_inventory():
    """Generate Ansible inventory with vault credentials"""
    from jeyriku_vault import VaultManager
    import json

    vault = VaultManager()
    vault.unlock()

    try:
        jeysrv = vault.get_credential('jeysrv12')

        inventory = {
            'all': {
                'hosts': {
                    'jeysrv12': {
                        'ansible_host': 'jeysrv12',
                        'ansible_user': jeysrv.username,
                        'ansible_password': jeysrv.password,
                        'ansible_become': True,
                        'ansible_become_method': 'sudo'
                    }
                }
            }
        }

        return json.dumps(inventory, indent=2)
    finally:
        vault.lock()


# Example 6: Context manager for automatic lock/unlock
def example_context_manager():
    """Using vault with context manager (future feature)"""
    from jeyriku_vault import VaultManager

    vault = VaultManager()

    # Manual approach (current)
    vault.unlock()
    try:
        cred = vault.get_credential('librenms')
        # Use credential
    finally:
        vault.lock()

    # Future context manager approach
    # with vault.unlocked():
    #     cred = vault.get_credential('librenms')
    #     # Automatically locked when exiting context


# Example 7: Checking if credential exists
def example_check_credential():
    """Check if a credential exists before using it"""
    from jeyriku_vault import VaultManager
    from jeyriku_vault.exceptions import CredentialNotFoundError

    vault = VaultManager()
    vault.unlock()

    try:
        # List all services
        services = vault.list_services()
        print(f"Available services: {services}")

        # Check specific service
        if 'librenms' in services:
            cred = vault.get_credential('librenms')
            print(f"LibreNMS token: {cred.token[:10]}...")
        else:
            print("LibreNMS not configured")

        # Using exception handling
        try:
            cred = vault.get_credential('nonexistent')
        except CredentialNotFoundError:
            print("Credential not found - need to configure it")

    finally:
        vault.lock()


# Example 8: Updating credentials
def example_update_credential():
    """Update an existing credential"""
    from jeyriku_vault import VaultManager
    import getpass

    vault = VaultManager()
    vault.unlock()

    try:
        # Get existing credential
        cred = vault.get_credential('nexus')

        # Update with new password
        new_password = getpass.getpass("New Nexus password: ")

        vault.set_credential(
            service='nexus',
            username=cred.username,  # Keep existing username
            password=new_password,   # New password
            metadata=cred.metadata   # Keep existing metadata
        )

        print("✅ Credential updated")

    finally:
        vault.lock()


# Example 9: Export/Import for backup
def example_backup_restore():
    """Backup and restore credentials"""
    from jeyriku_vault import VaultManager
    import json
    from pathlib import Path

    vault = VaultManager()
    vault.unlock()

    try:
        # Export credentials
        exported = vault.export_credentials()

        # Save to file
        backup_file = Path.home() / 'vault_backup.json.enc'
        with open(backup_file, 'w') as f:
            json.dump(exported, f, indent=2)

        print(f"✅ Backup saved to {backup_file}")

        # Import credentials (on another machine or after reset)
        # with open(backup_file) as f:
        #     data = json.load(f)
        # vault.import_credentials(data)

    finally:
        vault.lock()


# Example 10: Multiple credential types
def example_multiple_types():
    """Store different types of credentials"""
    from jeyriku_vault import VaultManager

    vault = VaultManager()
    vault.unlock()

    try:
        # SSH credentials (username + password)
        vault.set_credential(
            'server1',
            username='admin',
            password='secret123'
        )

        # API token only
        vault.set_credential(
            'api_service',
            token='ghp_aBcD1234...'
        )

        # API key
        vault.set_credential(
            'cloud_service',
            api_key='sk-1234567890abcdef'
        )

        # Complex credential with metadata
        vault.set_credential(
            'cisco_router',
            username='admin',
            password='cisco123',
            metadata={
                'enable_password': 'enable123',
                'ssh_port': 22,
                'device_type': 'cisco_ios'
            }
        )

        print("✅ All credentials stored")

    finally:
        vault.lock()


if __name__ == '__main__':
    print("Jeyriku Vault - Usage Examples")
    print("=" * 70)
    print("\nRun individual examples:")
    print("  python examples_usage.py")
    print("\nOr import in your code:")
    print("  from examples_usage import example_nexuspush")
    print("  config = example_nexuspush()")
