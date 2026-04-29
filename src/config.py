import os
from pathlib import Path
from dotenv import load_dotenv

class Config:
    def __init__(self, env_path: str = ".env"):
        load_dotenv(env_path)
        
        # Workspace Paths
        self.root_dir = Path(os.path.expanduser(os.getenv("ROOT_WORKSPACE_DIR", "~/.workspace"))).resolve()
        self.cipher_dir_name = os.getenv("CIPHER_DIR_NAME", "encrypted_workspace")
        self.mount_dir_name = os.getenv("MOUNT_DIR_NAME", "decrypted_workspace")
        
        self.cipher_path = self.root_dir / self.cipher_dir_name
        self.mount_path = self.root_dir / self.mount_dir_name
        
        # SSH Config
        self.ssh_port = int(os.getenv("SSH_PORT", 2222))
        self.ssh_key_dir = Path(os.path.expanduser(os.getenv("SSH_KEY_DIR", "/home/dev/workspace/.ssh_keys"))).resolve()
        
        # Docker Config
        self.container_name = os.getenv("CONTAINER_NAME", "dev_workspace")
        self.image_name = os.getenv("IMAGE_NAME", "dev_workspace")

    def __repr__(self):
        return f"<Config root={self.root_dir} container={self.container_name}>"
