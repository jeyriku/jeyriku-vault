# Examples Directory

This directory contains practical examples for using Jeyriku Vault in different scenarios.

## Available Examples

### 1. `setup_all_services.py`
Interactive script to configure the vault with all your services in one go.

**Usage:**
```bash
python examples/setup_all_services.py
```

**Configures:**
- Server credentials (jeysrv12, jeymacsrv01)
- Network management APIs (LibreNMS, Infrahub)
- Repository management (Nexus)
- Network device credentials (Cisco, Juniper)
- SNMP community strings
- Git/GitHub tokens

### 2. `examples_usage.py`
Real-world usage examples showing how to integrate Jeyriku Vault into your applications.

**Examples included:**
- Basic credential retrieval
- NexusPush integration
- NetAlps Probe with LibreNMS
- PyATS testbed generation
- Ansible dynamic inventory
- Context manager usage
- Credential existence checking
- Updating credentials
- Backup and restore
- Multiple credential types

**Usage:**
```python
# Import and use in your code
from examples.examples_usage import example_nexuspush

config = example_nexuspush()
print(config)
```

## Quick Test

To quickly test the vault:

```bash
# 1. Initialize vault
jeyriku-vault init

# 2. Run setup
python examples/setup_all_services.py

# 3. Test retrieval
jeyriku-vault list
jeyriku-vault get librenms
```

## Integration Examples

### For NexusPush

```python
from jeyriku_vault import VaultManager

vault = VaultManager()
vault.unlock()

try:
    jeysrv12 = vault.get_credential('jeysrv12')
    nexus = vault.get_credential('nexus')
    
    # Use credentials in your app
    # ...
finally:
    vault.lock()
```

### For NetAlps Probe

```python
from jeyriku_vault import VaultManager

vault = VaultManager()
vault.unlock()

try:
    librenms = vault.get_credential('librenms')
    
    # Use in discovery
    discovery = LibreNMSDiscovery(
        base_url=librenms.metadata['url'],
        token=librenms.token
    )
finally:
    vault.lock()
```

### For PyATS

```python
from jeyriku_vault import VaultManager

vault = VaultManager()
vault.unlock()

try:
    cisco = vault.get_credential('cisco_devices')
    
    testbed_dict = {
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
finally:
    vault.lock()
```

## Environment Variable for Master Password

For automated scripts, you can set the master password as environment variable:

```bash
export JEYRIKU_VAULT_PASSWORD="your_master_password"

# Then unlock works automatically
jeyriku-vault list
```

**⚠️ Security Warning**: Only use environment variables in secure, controlled environments. For interactive use, always enter the password manually.

## Next Steps

1. Review the examples
2. Adapt them to your specific use case
3. Integrate into your applications
4. See [INTEGRATION.md](../INTEGRATION.md) for detailed integration guides

## Contributing

Have a useful example? Feel free to contribute by:
1. Adding your example to `examples_usage.py`
2. Documenting it here
3. Submitting a pull request

## Support

For issues or questions:
- GitHub Issues: https://github.com/jeyriku/jeyriku-vault/issues
- Main README: [../README.md](../README.md)
