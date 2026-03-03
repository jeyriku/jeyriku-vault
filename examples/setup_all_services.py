#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Example: Configure Jeyriku Vault for all services

This script helps you set up the vault with all necessary credentials
for your Jeyriku applications.
"""

import getpass
from jeyriku_vault import VaultManager


def setup_vault():
    """Interactive setup for all Jeyriku services"""
    
    vault = VaultManager()
    
    # Initialize if needed
    if not vault.is_initialized():
        print("🔒 Vault not initialized. Let's create it!")
        master_password = getpass.getpass("Create master password (min 8 chars): ")
        confirm = getpass.getpass("Confirm master password: ")
        
        if master_password != confirm:
            print("❌ Passwords don't match")
            return
            
        vault.initialize(master_password)
        print("✅ Vault initialized successfully\n")
    
    # Unlock vault
    vault.unlock()
    
    try:
        print("\n" + "="*70)
        print("🔧 Jeyriku Vault Configuration")
        print("="*70)
        print("\nWe'll set up credentials for all your services.")
        print("Press ENTER to skip any service.\n")
        
        # 1. Server Credentials
        print("\n📡 Server Credentials")
        print("-" * 70)
        
        if input("Configure jeysrv12? (y/n): ").lower() == 'y':
            username = input("  Username [jeyriku]: ") or "jeyriku"
            password = getpass.getpass("  Password: ")
            vault.set_credential('jeysrv12', username=username, password=password,
                               metadata={'type': 'ssh', 'host': 'jeysrv12'})
            print("  ✅ jeysrv12 configured")
        
        if input("Configure jeymacsrv01? (y/n): ").lower() == 'y':
            username = input("  Username [jeyriku]: ") or "jeyriku"
            password = getpass.getpass("  Password: ")
            vault.set_credential('jeymacsrv01', username=username, password=password,
                               metadata={'type': 'ssh', 'host': 'jeymacsrv01'})
            print("  ✅ jeymacsrv01 configured")
        
        # 2. Network Management APIs
        print("\n🌐 Network Management APIs")
        print("-" * 70)
        
        if input("Configure LibreNMS? (y/n): ").lower() == 'y':
            url = input("  LibreNMS URL [http://192.168.0.249:8080]: ") or "http://192.168.0.249:8080"
            token = getpass.getpass("  API Token: ")
            vault.set_credential('librenms', token=token,
                               metadata={'url': url, 'type': 'api'})
            print("  ✅ LibreNMS configured")
        
        if input("Configure Infrahub? (y/n): ").lower() == 'y':
            url = input("  Infrahub URL: ")
            token = getpass.getpass("  API Token: ")
            vault.set_credential('infrahub', token=token,
                               metadata={'url': url, 'type': 'api'})
            print("  ✅ Infrahub configured")
        
        # 3. Repository Management
        print("\n📦 Repository Management")
        print("-" * 70)
        
        if input("Configure Nexus Repository? (y/n): ").lower() == 'y':
            username = input("  Username [admin]: ") or "admin"
            password = getpass.getpass("  Password: ")
            url = input("  Nexus URL [http://jeysrv12:8081]: ") or "http://jeysrv12:8081"
            vault.set_credential('nexus', username=username, password=password,
                               metadata={'url': url, 'repository': 'network-binaries'})
            print("  ✅ Nexus configured")
        
        # 4. Network Device Credentials
        print("\n🔌 Network Device Credentials")
        print("-" * 70)
        
        if input("Configure Cisco devices? (y/n): ").lower() == 'y':
            username = input("  Username: ")
            password = getpass.getpass("  Password: ")
            enable = getpass.getpass("  Enable password (optional): ") or None
            
            metadata = {'type': 'network_device', 'vendor': 'cisco'}
            if enable:
                metadata['enable_password'] = enable
                
            vault.set_credential('cisco_devices', username=username, password=password,
                               metadata=metadata)
            print("  ✅ Cisco devices configured")
        
        if input("Configure Juniper devices? (y/n): ").lower() == 'y':
            username = input("  Username: ")
            password = getpass.getpass("  Password: ")
            vault.set_credential('juniper_devices', username=username, password=password,
                               metadata={'type': 'network_device', 'vendor': 'juniper'})
            print("  ✅ Juniper devices configured")
        
        # 5. SNMP
        print("\n📊 SNMP Configuration")
        print("-" * 70)
        
        if input("Configure SNMP community strings? (y/n): ").lower() == 'y':
            read_community = input("  Read community [public]: ") or "public"
            write_community = input("  Write community (optional): ") or None
            
            vault.set_credential('snmp', 
                               password=read_community,
                               metadata={
                                   'type': 'snmp',
                                   'read_community': read_community,
                                   'write_community': write_community,
                                   'version': '2c'
                               })
            print("  ✅ SNMP configured")
        
        # 6. Git/GitHub
        print("\n🔑 Git/GitHub")
        print("-" * 70)
        
        if input("Configure GitHub token? (y/n): ").lower() == 'y':
            token = getpass.getpass("  GitHub Personal Access Token: ")
            username = input("  GitHub username: ")
            vault.set_credential('github', username=username, token=token,
                               metadata={'type': 'git', 'scopes': 'repo,workflow'})
            print("  ✅ GitHub configured")
        
        print("\n" + "="*70)
        print("✅ Vault configuration complete!")
        print("="*70)
        
        # Show summary
        print("\n📋 Configured services:")
        services = vault.list_services()
        for service in sorted(services):
            cred = vault.get_credential(service)
            cred_type = "password" if cred.password else ("token" if cred.token else "api_key")
            print(f"  • {service:20} ({cred_type})")
        
        print(f"\n💾 Vault location: {vault.vault_path}")
        print("\nTo use these credentials in your applications:")
        print("  from jeyriku_vault import VaultManager")
        print("  vault = VaultManager()")
        print("  vault.unlock()")
        print("  cred = vault.get_credential('service_name')")
        print("  vault.lock()")
        
    finally:
        vault.lock()


if __name__ == '__main__':
    try:
        setup_vault()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
