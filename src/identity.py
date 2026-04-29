import os
from pathlib import Path
from colorama import Fore, Style
from .utils import Logger

class IdentityManager:
    def __init__(self, config):
        self.config = config
        self.container_root = "/home/dev/workspace"

    def get_host_key_dir(self) -> Path:
        """Derives the host-side path for SSH keys based on container configuration."""
        ssh_key_dir_raw = os.getenv("SSH_KEY_DIR", f"{self.container_root}/.ssh_keys")
        
        if ssh_key_dir_raw.startswith(self.container_root):
            subpath = ssh_key_dir_raw.replace(self.container_root, "").lstrip("/")
        else:
            subpath = os.path.basename(ssh_key_dir_raw)
            
        return self.config.mount_path / subpath

    def display_keys(self):
        """Prints the SSH key paths and contents with professional formatting."""
        host_key_dir = self.get_host_key_dir()
        priv_path = host_key_dir / "id_ed25519"
        pub_path = host_key_dir / "id_ed25519.pub"
        
        print(f"\n{Fore.WHITE}{Style.BRIGHT}🔑 SSH IDENTITY DETAILS:{Style.RESET_ALL}")
        
        if not host_key_dir.exists():
            Logger.error("Vault is locked or keys haven't been generated yet. Run 'start' first.", exit_code=None)
            return

        print(f"{Fore.CYAN}Directory: {Fore.WHITE}{host_key_dir}")
        
        if pub_path.exists():
            print(f"\n{Fore.GREEN}[Public Key Path]: {pub_path}")
            print(f"{Fore.WHITE}{pub_path.read_text()}")
        
        if priv_path.exists():
            print(f"{Fore.GREEN}[Private Key Path]: {priv_path}")
            print(f"{Fore.WHITE}{priv_path.read_text()}")
        
        print(f"{Style.BRIGHT}--------------------------------------------------{Style.RESET_ALL}\n")

    def get_ssh_command(self) -> str:
        """Returns the formatted SSH command for accessing the workspace."""
        host_key_dir = self.get_host_key_dir()
        key_path = host_key_dir / "id_ed25519"
        return f"ssh -i {key_path} -p {self.config.ssh_port} dev@localhost"
