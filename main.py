import click
import shutil
import sys
import os
from pathlib import Path
from src.config import Config
from src.utils import Logger, DependencyChecker
from src.vault import VaultManager
from src.container import ContainerManager

@click.group()
def cli():
    """Secure Development Workspace CLI"""
    pass

@cli.command()
def init():
    """Setup the encrypted vault and environment"""
    config = Config()
    checker = DependencyChecker()
    
    # Check dependencies first
    missing = checker.check_all(["docker", "gocryptfs", "ssh-keygen"])
    if "gocryptfs" in missing:
        checker.ensure_apt_dependencies()
        
    vault = VaultManager(config.cipher_path, config.mount_path)
    container = ContainerManager(config)
    
    vault.init()
    container.generate_compose()
    Logger.info("Initialization complete. Run 'python3 main.py start' to begin.")

@cli.command()
def start():
    """Unlock the vault and start the workspace"""
    config = Config()
    vault = VaultManager(config.cipher_path, config.mount_path)
    container = ContainerManager(config)
    
    if vault.mount():
        if container.up():
            Logger.info("Workspace is ready.")
            host_key_path = str(config.ssh_key_dir).replace("/home/dev/workspace", str(config.mount_path))
            Logger.info(f"Access via: ssh -i {host_key_path}/id_ed25519 -p {config.ssh_port} dev@localhost")

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
    """Manual trigger to mount the vault without starting the container"""
    config = Config()
    vault = VaultManager(config.cipher_path, config.mount_path)
    vault.mount()

if __name__ == "__main__":
    cli()
