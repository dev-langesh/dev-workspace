import subprocess
import os
from .utils import Logger

class VaultManager:
    def __init__(self, cipher_path, mount_path):
        self.cipher_path = cipher_path
        self.mount_path = mount_path

    def init(self):
        if (self.cipher_path / "gocryptfs.conf").exists():
            Logger.info("Vault already initialized.")
            return True
        
        self.cipher_path.mkdir(parents=True, exist_ok=True)
        Logger.warn("Initializing new gocryptfs vault...")
        try:
            subprocess.run(["gocryptfs", "-init", str(self.cipher_path)], check=True)
            return True
        except subprocess.CalledProcessError:
            Logger.error("Failed to initialize vault.")
            return False

    def mount(self):
        if self.is_mounted():
            Logger.info("Vault is already mounted.")
            return True
        
        self.mount_path.mkdir(parents=True, exist_ok=True)
        Logger.log("Mounting Encrypted Vault...")
        try:
            # We use allow_other for Docker access
            subprocess.run([
                "gocryptfs", 
                "-allow_other", 
                str(self.cipher_path), 
                str(self.mount_path)
            ], check=True)
            return True
        except subprocess.CalledProcessError:
            Logger.error("Mount failed. Check your password and /etc/fuse.conf.")
            return False

    def unmount(self):
        if not self.is_mounted():
            Logger.info("Vault is not mounted.")
            return True
        
        Logger.log("Locking Vault (Unmounting)...")
        try:
            subprocess.run(["fusermount", "-uz", str(self.mount_path)], check=True)
            return True
        except subprocess.CalledProcessError:
            Logger.error("Failed to unmount vault.")
            return False

    def is_mounted(self):
        return os.path.ismount(str(self.mount_path))
