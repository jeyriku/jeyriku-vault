# 🔐 Jeyriku Vault - Secure Credential Management

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Security: AES-256](https://img.shields.io/badge/security-AES--256-green.svg)](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard)

**Jeyriku Vault** is a centralized, encrypted credential storage system designed for network automation tools. It provides a unified, secure way to manage passwords, API tokens, SSH keys, and other sensitive credentials across all your Jeyriku applications.

> 🎯 **Perfect for**: Network engineers managing multiple devices, API tokens, and service credentials across tools like Ansible, PyATS, NetAlps Probe, and custom automation scripts.

## ✨ Features

- 🔒 **Strong Encryption**: AES-256 encryption with PBKDF2 key derivation (100,000 iterations)
- 💾 **Multiple Backends**: SQLCipher (encrypted SQLite) or encrypted file storage
- 🔑 **Master Password Protection**: Single password to unlock all credentials
- 📊 **Audit Trail**: Track credential access and modifications (SQLCipher backend)
- 🖥️ **CLI & Programmatic Access**: Use via command-line or Python API  
- 📦 **Import/Export**: Backup and restore credentials
- 🌍 **Cross-Platform**: Works on macOS, Linux, and Windows
- 🔌 **Integration Ready**: Easy to integrate with existing tools

## 🚀 Quick Start

### Installation

```bash
# Basic installation (encrypted file backend)
pip install git+https://github.com/jeyriku/jeyriku-vault.git

# With SQLCipher support (recommended)
pip install "git+https://github.com/jeyriku/jeyriku-vault.git#egg=jeyriku-vault[sqlcipher]"

# Or clone and install locally
git clone https://github.com/jeyriku/jeyriku-vault.git
cd jeyriku-vault
pip install ".[sqlcipher]"
```

### First Steps

```bash
# Initialize a new vault
jeyriku-vault init

# Store credentials
jeyriku-vault set librenms --token YOUR_LIBRENMS_TOKEN
jeyriku-vault set infrahub --token YOUR_INFRAHUB_TOKEN
jeyriku-vault set jeysrv12 --username jeyriku --password SECRET

# Retrieve credentials
jeyriku-vault get librenms --show-password
jeyriku-vault list --details
```

## 📚 Usage

### Command-Line Interface

#### Initialize Vault

```bash
jeyriku-vault init
# You'll be prompted for a master password
```

#### Store Credentials

**API Token:**
```bash
jeyriku-vault set librenms --token abc123xyz
```

**Username/Password:**
```bash
jeyriku-vault set nexus --username admin --password secret123
```

**Interactive Mode** (recommended for passwords):
```bash
jeyriku-vault set jeysrv12 --username jeyriku
# Password will be prompted securely
```

#### Retrieve Credentials

```bash
# View credential (passwords masked)
jeyriku-vault get librenms

# Show passwords
jeyriku-vault get librenms --show-password

# JSON output
jeyriku-vault get librenms --json --show-password
```

#### List All Credentials

```bash
# Simple list
jeyriku-vault list

# With details
jeyriku-vault list --details
```

#### Delete Credentials

```bash
# With confirmation
jeyriku-vault delete old-service

# Skip confirmation
jeyriku-vault delete old-service --yes
```

#### Export/Import

```bash
# Export (passwords masked for safety)
jeyriku-vault export backup.json

# Export with passwords (USE WITH CAUTION!)
jeyriku-vault export backup-full.json --include-passwords

# Import credentials
jeyriku-vault import backup.json

# Import and overwrite existing
jeyriku-vault import backup.json --overwrite
```

#### Change Master Password

```bash
jeyriku-vault change-password
```

### Programmatic Access (Python API)

Use Jeyriku Vault in your Python applications:

```python
from jeyriku_vault import VaultManager

# Initialize and unlock vault
vault = VaultManager()
vault.unlock("master_password")

# Store a credential
vault.set_credential(
    service="librenms",
    token="abc123xyz",
    metadata={"url": "https://librenms.example.com"}
)

# Retrieve a credential
cred = vault.get_credential("librenms")
print(f"Token: {cred.token}")
print(f"URL: {cred.metadata['url']}")

# List all services
services = vault.list_services()
print(f"Services: {services}")

# Lock vault when done
vault.lock()
```

## 🏗️ Architecture

### Storage Backends

#### 1. **Encrypted File** (Default)
- Uses AES-256 encryption via Fernet (cryptography library)
- Single encrypted JSON file
- Portable and simple
- Good for most use cases

#### 2. **SQLCipher** (Recommended for production)
- Encrypted SQLite database
- Built-in audit logging
- Better performance for large credential stores
- Requires `pysqlcipher3` package

### Credential Structure

Each credential can contain:
- **service**: Unique identifier (e.g., "librenms", "infrahub", "jeysrv12")
- **username**: Optional username
- **password**: Optional password
- **token**: Optional API token
- **api_key**: Optional API key
- **ssh_key**: Optional SSH private key
- **metadata**: Optional custom metadata (dict)
- **created_at**: Auto-generated timestamp
- **updated_at**: Auto-updated timestamp

## 🔧 Integration with Jeyriku Tools

### netalps_probe

```python
from jeyriku_vault import VaultManager

vault = VaultManager()
vault.unlock()

# Get LibreNMS credentials
librenms_cred = vault.get_credential("librenms")

# Use in discovery
from netalps_probe.discovery.librenms import LibreNMSDiscovery

discovery = LibreNMSDiscovery(
    base_url="https://librenms.example.com",
    token=librenms_cred.token
)
```

### nexuspush

```python
from jeyriku_vault import VaultManager

vault = VaultManager()
vault.unlock()

# Get server credentials
server_cred = vault.get_credential("jeysrv12")
nexus_cred = vault.get_credential("nexus")

# Use in SCP/Nexus managers
from nexuspush import SCPManager, NexusManager

scp = SCPManager(
    hostname="jeysrv12",
    username=server_cred.username,
    password=server_cred.password,
    base_path="/home/jeyriku/Nexus/net/tftp"
)
```

### Ansible/PyATS

```python
from jeyriku_vault import VaultManager

vault = VaultManager()
vault.unlock()

# Get device credentials
cisco_cred = vault.get_credential("cisco_devices")

# Use in PyATS testbed
testbed = {
    'devices': {
        'router1': {
            'credentials': {
                'default': {
                    'username': cisco_cred.username,
                    'password': cisco_cred.password
                }
            }
        }
    }
}
```

## 🛡️ Security Best Practices

1. **Master Password**
   - Use a strong master password (min 8 chars, preferably 16+)
   - Don't share or store the master password
   - Change it periodically

2. **Vault Storage**
   - Default location: `~/.jeyriku/vault`
   - Keep backups in a secure location
   - Don't commit vault to git repositories

3. **Export/Import**
   - Only export with `--include-passwords` when absolutely necessary
   - Encrypt exported files before transferring
   - Delete exported files after use

4. **Production Use**
   - Use SQLCipher backend for audit trail
   - Integrate with OS keyring for master password (future feature)
   - Consider hardware security modules (HSM) for sensitive environments

## 📖 Advanced Usage

### Custom Vault Location

```bash
# CLI
jeyriku-vault --vault-path /secure/location/vault init

# Python
vault = VaultManager(vault_path="/secure/location/vault")
```

### Choose Backend

```bash
# CLI (encrypted file)
jeyriku-vault --backend encrypted_file init

# CLI (SQLCipher)
jeyriku-vault --backend sqlcipher init

# Python
vault = VaultManager(backend="sqlcipher")
```

### Credential with Metadata

```python
vault.set_credential(
    service="production-db",
    username="admin",
    password="secret",
    metadata={
        "host": "db.example.com",
        "port": 5432,
        "database": "production",
        "ssl": True
    }
)

# Retrieve and use
cred = vault.get_credential("production-db")
connect_string = f"postgresql://{cred.username}:{cred.password}@{cred.metadata['host']}:{cred.metadata['port']}/{cred.metadata['database']}"
```

## 🐛 Troubleshooting

### ImportError: No module named 'pysqlcipher3'

```bash
# Install SQLCipher dependencies (macOS)
brew install sqlcipher

# Install Python package
pip install pysqlcipher3
```

### Vault is locked

Always call `vault.unlock()` before accessing credentials.

### Incorrect master password

The vault will raise `AuthenticationError` if the password is wrong. There is no password recovery - keep backups!

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Related Projects

- **nexuspush**: Binary management tool for network devices
- **netalps_probe**: Network discovery and topology mapping
- **jeysible**: Ansible automation for Jeyriku infrastructure

## 📞 Support

- **Issues**: https://github.com/jeyriku/jeyriku-vault/issues
- **Email**: contact@jeyriku.net
- **Documentation**: https://github.com/jeyriku/jeyriku-vault

---

**Copyright © 2026 Jeyriku.net - All rights reserved**
