import subprocess
import os
from pathlib import Path
from .utils import Logger

class VaultManager:
    def __init__(self, config):
        self.config = config
        self.cipher_path = config.cipher_path
        self.mount_path = config.mount_path


    def _enable_allow_other(self):
        """Ensures user_allow_other is enabled in FUSE configuration"""
        fuse_conf = self.config.fuse_conf
        if not fuse_conf.exists():
            return

        try:
            content = fuse_conf.read_text()
            if "user_allow_other" not in [line.strip() for line in content.splitlines() if not line.startswith("#")]:
                Logger.warn(f"Enabling user_allow_other in {fuse_conf}...")
                # We use sed via sudo to uncomment or add the line
                if "#user_allow_other" in content:
                    subprocess.run(["sudo", "sed", "-i", "s/#user_allow_other/user_allow_other/", str(fuse_conf)], check=True)
                else:
                    subprocess.run(["sudo", "sh", "-c", f"echo 'user_allow_other' >> {fuse_conf}"], check=True)
                Logger.info("user_allow_other enabled.")
        except Exception as e:
            Logger.warn(f"Could not automatically enable user_allow_other in {fuse_conf}: {e}")


    def init(self):
        self._enable_allow_other()
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
