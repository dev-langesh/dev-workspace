import os
from pathlib import Path
from dotenv import load_dotenv

class Config:
    def __init__(self, env_path: str = ".env"):
        load_dotenv(env_path)
        
        # Workspace Paths
        root_raw = os.getenv("ROOT_WORKSPACE_DIR", "$HOME/.workspace")
        # Ensure $HOME is expanded and the path is absolute
        expanded_root = os.path.expandvars(root_raw).replace("$HOME", os.path.expanduser("~"))
        self.root_dir = Path(os.path.expanduser(expanded_root)).absolute()

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
        self.base_image = os.getenv("BASE_IMAGE", "ubuntu:24.04")

        
        # System Config
        self.fuse_conf = Path(os.getenv("FUSE_CONF", "/etc/fuse.conf")).resolve()


    def __repr__(self):
        return f"<Config root={self.root_dir} container={self.container_name}>"
