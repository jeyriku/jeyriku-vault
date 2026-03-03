# Jeyriku Vault - Quick Start

## Installation (2 minutes)

```bash
pip install "git+https://github.com/jeyriku/jeyriku-vault.git#egg=jeyriku-vault[sqlcipher]"
```

## Setup (1 minute)

```bash
# Initialize vault
jeyriku-vault init
# Enter a master password when prompted
```

## Store Your First Credentials (30 seconds)

```bash
# Store an API token
jeyriku-vault set librenms --token YOUR_TOKEN_HERE

# Store username/password (password will be prompted)
jeyriku-vault set jeysrv12 --username jeyriku
```

## Retrieve Credentials (30 seconds)

```bash
# View credentials (passwords masked)
jeyriku-vault get librenms

# Show passwords
jeyriku-vault get librenms --show-password

# List all stored credentials
jeyriku-vault list --details
```

## Use in Python (2 minutes)

```python
from jeyriku_vault import VaultManager

# Unlock vault
vault = VaultManager()
vault.unlock("your_master_password")

# Get credentials
cred = vault.get_credential("librenms")
print(f"Token: {cred.token}")

# Store new credential
vault.set_credential(
    service="infrahub",
    token="abc123xyz"
)

# Lock vault
vault.lock()
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `jeyriku-vault init` | Initialize new vault |
| `jeyriku-vault set SERVICE` | Store credential |
| `jeyriku-vault get SERVICE` | Retrieve credential |
| `jeyriku-vault list` | List all services |
| `jeyriku-vault delete SERVICE` | Delete credential |
| `jeyriku-vault export FILE` | Export to backup |
| `jeyriku-vault import FILE` | Import from backup |
| `jeyriku-vault change-password` | Change master password |

## Common Credentials to Store

```bash
# Network Services
jeyriku-vault set librenms --token YOUR_LIBRENMS_TOKEN
jeyriku-vault set infrahub --token YOUR_INFRAHUB_TOKEN

# Servers
jeyriku-vault set jeysrv12 --username jeyriku
jeyriku-vault set jeymacsrv01 --username jeyriku

# Repository Managers
jeyriku-vault set nexus --username admin

# Network Devices (for automation)
jeyriku-vault set cisco_devices --username admin --password SECRET
jeyriku-vault set juniper_devices --username admin --password SECRET

# SNMP Communities
jeyriku-vault set snmp_read --token public
jeyriku-vault set snmp_write --token private
```

## Integration Examples

### With netalps_probe

```python
from jeyriku_vault import VaultManager
from netalps_probe.discovery.librenms import LibreNMSDiscovery

vault = VaultManager()
vault.unlock()

cred = vault.get_credential("librenms")

discovery = LibreNMSDiscovery(
    base_url="https://librenms.example.com",
    token=cred.token
)
```

### With nexuspush

```python
from jeyriku_vault import VaultManager
from nexuspush import SCPManager, NexusManager

vault = VaultManager()
vault.unlock()

server = vault.get_credential("jeysrv12")
nexus = vault.get_credential("nexus")

scp = SCPManager(
    hostname="jeysrv12",
    username=server.username,
    password=server.password,
    base_path="/home/jeyriku/Nexus/net/tftp"
)
```

## Tips

- 💡 **Master Password**: Use a strong, unique password
- 💾 **Backups**: Export regularly with `jeyriku-vault export backup.json`
- 🔒 **Security**: Never commit vault files to git
- 📝 **Metadata**: Use for storing extra info like URLs, ports, etc.

## Need Help?

- Full documentation: [README.md](README.md)
- Issues: https://github.com/jeyriku/jeyriku-vault/issues

---

Happy securing! 🔐
