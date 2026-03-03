# Integration Guide: Using Jeyriku Vault in Your Applications

## Installation

```bash
# Install jeyriku-vault with SQLCipher support
pip install "git+https://github.com/jeyriku/jeyriku-vault.git#egg=jeyriku-vault[sqlcipher]"
```

## Quick Integration Examples

### 1. NexusPush Integration

Replace the simple `VaultManager` in nexuspush with Jeyriku Vault:

```python
from jeyriku_vault import VaultManager

# In nexuspush/cli.py
class NexusPushCLI:
    def __init__(self):
        # Use centralized vault
        self.vault = VaultManager()
        
    def initialize_connections(self):
        # Get credentials from vault
        try:
            self.vault.unlock()
            
            # Get jeysrv12 credentials
            jeysrv12_cred = self.vault.get_credential('jeysrv12')
            
            # Get Nexus credentials
            nexus_cred = self.vault.get_credential('nexus')
            
            # Use credentials
            self.scp_manager = SCPManager(
                self.config['jeysrv12_host'],
                jeysrv12_cred.username,
                jeysrv12_cred.password,
                self.config['jeysrv12_path']
            )
            
        finally:
            self.vault.lock()
```

### 2. NetAlps Probe Integration

Use vault for LibreNMS and Infrahub tokens:

```python
from jeyriku_vault import VaultManager

def run_discovery(args):
    vault = VaultManager()
    
    try:
        vault.unlock()
        
        # Get tokens from vault
        librenms_cred = vault.get_credential('librenms')
        infrahub_cred = vault.get_credential('infrahub')
        
        discovery = LibreNMSDiscovery(
            base_url=args.url,
            token=librenms_cred.token,
            site_filter=args.site
        )
        
        # Export to Infrahub
        exporter = InfrahubExporter(
            infrahub_url=os.getenv('INFRAHUB_ADDRESS'),
            api_token=infrahub_cred.token
        )
        
    finally:
        vault.lock()
```

### 3. PyATS/Ansible Integration

Store device credentials in vault:

```python
from jeyriku_vault import VaultManager

def get_testbed_credentials():
    """Get device credentials from vault for PyATS testbed"""
    vault = VaultManager()
    
    try:
        vault.unlock()
        
        # Get credentials for different device types
        cisco_cred = vault.get_credential('cisco_devices')
        juniper_cred = vault.get_credential('juniper_devices')
        
        return {
            'cisco': {
                'username': cisco_cred.username,
                'password': cisco_cred.password,
                'enable': cisco_cred.metadata.get('enable_password')
            },
            'juniper': {
                'username': juniper_cred.username,
                'password': juniper_cred.password
            }
        }
    finally:
        vault.lock()
```

## Setup Instructions

### Step 1: Initialize the vault

```bash
# Create and configure vault
jeyriku-vault init

# Store all your credentials
jeyriku-vault set jeysrv12 --username jeyriku --password YOUR_PASSWORD
jeyriku-vault set nexus --username admin --password YOUR_PASSWORD
jeyriku-vault set librenms --token YOUR_LIBRENMS_TOKEN
jeyriku-vault set infrahub --token YOUR_INFRAHUB_TOKEN
jeyriku-vault set cisco_devices --username admin --password YOUR_PASSWORD
jeyriku-vault set juniper_devices --username admin --password YOUR_PASSWORD
```

### Step 2: Add metadata for complex credentials

```bash
# Add enable password as metadata
jeyriku-vault set cisco_devices --username admin --password PASS --description "Cisco network devices with enable password"

# Then add enable password via Python API:
from jeyriku_vault import VaultManager
vault = VaultManager()
vault.unlock()
cred = vault.get_credential('cisco_devices')
if not cred.metadata:
    cred.metadata = {}
cred.metadata['enable_password'] = 'ENABLE_PASS'
vault.set_credential('cisco_devices', **cred.to_dict())
vault.lock()
```

### Step 3: Update your applications

Add `jeyriku-vault` to requirements.txt of each app:

```txt
# requirements.txt for nexuspush, netalps_probe, etc.
jeyriku-vault @ git+https://github.com/jeyriku/jeyriku-vault.git
```

## Environment Variable Alternative

For scripts, you can also use environment variable for master password:

```bash
export JEYRIKU_VAULT_PASSWORD="your_master_password"

# Then your app can unlock automatically
vault = VaultManager()
vault.unlock()  # Will use env var if available
```

## Migration from Current Implementation

### Before (nexuspush/vault.py)
```python
def get_credential(self, service: str, username: str = None) -> Dict[str, str]:
    # Prompts every time
    print(f"\n🔐 Credentials required for {service}")
    username = input(f"Username for {service}: ")
    password = getpass.getpass(f"Password for {username}@{service}: ")
    return {'username': username, 'password': password}
```

### After (using jeyriku-vault)
```python
from jeyriku_vault import VaultManager

def get_credential(self, service: str) -> Dict[str, str]:
    # Gets from encrypted vault with single master password
    cred = self.vault.get_credential(service)
    return {
        'username': cred.username,
        'password': cred.password or cred.token
    }
```

## Security Benefits

✅ **One master password** instead of typing credentials every time  
✅ **Encrypted storage** with AES-256 encryption  
✅ **Centralized** credential management across all tools  
✅ **Audit trail** when using SQLCipher backend  
✅ **Backup/restore** with export/import functionality  

## Next Steps

1. Install jeyriku-vault in each application
2. Initialize vault and store all credentials
3. Update application code to use VaultManager
4. Test with `vault.unlock()` / `vault.lock()` pattern
5. Remove hardcoded credentials from configs

For full documentation, see: https://github.com/jeyriku/jeyriku-vault
