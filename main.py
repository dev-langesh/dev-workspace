import click
import shutil
import sys
import os
from pathlib import Path
from src.config import Config
from src.utils import Logger, DependencyChecker
from src.vault import VaultManager
from src.container import ContainerManager
from src.identity import IdentityManager
from colorama import Fore, Style


BANNER = f"""
{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════════════════════════════╗
║  {Fore.WHITE}             🛡️  SECURE DEVELOPMENT WORKSPACE                {Fore.CYAN}║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""

@click.group()
def cli():
    """{Fore.WHITE}Secure Development Workspace Management Tool{Style.RESET_ALL}"""
    print(BANNER)


@cli.command()
def init():
    """Setup the encrypted vault and environment"""
    config = Config()
    checker = DependencyChecker()
    
    # Check dependencies first
    missing = checker.check_all(["docker", "gocryptfs", "ssh-keygen"])
    if "gocryptfs" in missing:
        checker.ensure_system_dependencies()

        
    vault = VaultManager(config.cipher_path, config.mount_path)
    container = ContainerManager(config)
    
    vault.init()
    container.generate_compose()
    
    print(f"\n{Fore.GREEN}{Style.BRIGHT}✨ INITIALIZATION COMPLETE{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Next step: {Fore.CYAN}python3 main.py start{Style.RESET_ALL}\n")


@cli.command()
def start():
    """Unlock the vault and start the workspace"""
    config = Config()
    vault = VaultManager(config.cipher_path, config.mount_path)
    container = ContainerManager(config)
    
    if vault.mount():
        if container.up():
            Logger.info("Workspace is ready.")
            identity = IdentityManager(config)
            
            print(f"\n{Fore.WHITE}{Style.BRIGHT}🚀 ACCESS YOUR WORKSPACE:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{identity.get_ssh_command()}{Style.RESET_ALL}\n")
            
            Logger.info("Use the command above or copy the key from 'docker logs dev_workspace'")


@cli.command()
def stop():
    """Shutdown the workspace and lock the vault"""
    config = Config()
    vault = VaultManager(config.cipher_path, config.mount_path)
    container = ContainerManager(config)
    
    container.down()
    vault.unmount()
    Logger.info("Workspace stopped and locked.")

@cli.command()
@click.option('--force', is_flag=True, help="Skip confirmation prompt")
def delete(force):
    """PERMANENTLY delete the workspace and all data"""
    if not force:
        click.confirm("CRITICAL WARNING: This will PERMANENTLY DELETE all your data and keys. Continue?", abort=True)
    
    config = Config()
    vault = VaultManager(config.cipher_path, config.mount_path)
    container = ContainerManager(config)
    
    container.down()
    container.remove_image()
    vault.unmount()
    
    if config.root_dir.exists():
        Logger.log(f"Deleting workspace data: {config.root_dir}")
        shutil.rmtree(config.root_dir)
        Logger.info("All data wiped.")
    
    if (Path("docker-compose.yml")).exists():
        os.remove("docker-compose.yml")

@cli.command()
def decrypt():
    """Unlock the vault (Manual)"""
    config = Config()
    vault = VaultManager(config.cipher_path, config.mount_path)
    vault.mount()

@cli.command()
def encrypt():
    """Lock the vault (Manual)"""
    config = Config()
    vault = VaultManager(config.cipher_path, config.mount_path)
    vault.unmount()

@cli.command()
def keys():
    """Show the SSH keys and their host-side paths"""
    config = Config()
    identity = IdentityManager(config)
    identity.display_keys()


if __name__ == "__main__":
    cli()
