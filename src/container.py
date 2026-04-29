import subprocess
import os
from .utils import Logger

class ContainerManager:
    def __init__(self, config):
        self.config = config

    def generate_compose(self):
        Logger.log("Generating docker-compose.yml...")
        compose_content = f"""services:
  dev:
    build:
      context: .
      args:
        SSH_PORT: {self.config.ssh_port}
    image: {self.config.image_name}
    container_name: {self.config.container_name}
    network_mode: host
    environment:
      - SSH_KEY_DIR={self.config.ssh_key_dir}
    volumes:
      - {self.config.mount_path}:/home/dev/workspace
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped
"""
        with open("docker-compose.yml", "w") as f:
            f.write(compose_content)

    def up(self):
        Logger.log("Starting Docker Container...")
        try:
            # We use DOCKER_BUILDKIT=1 as an env var for the subprocess
            env = os.environ.copy()
            env["DOCKER_BUILDKIT"] = "1"
            subprocess.run(["docker", "compose", "up", "-d", "--build"], env=env, check=True)
            return True
        except subprocess.CalledProcessError:
            Logger.error("Failed to start container.")
            return False

    def down(self):
        Logger.log("Stopping and removing container...")
        try:
            subprocess.run(["docker", "compose", "down"], check=True)
            return True
        except subprocess.CalledProcessError:
            Logger.warn("Failed to stop container cleanly.")
            return False

    def remove_image(self):
        Logger.log(f"Removing image: {self.config.image_name}...")
        try:
            subprocess.run(["docker", "rmi", self.config.image_name], check=True)
        except subprocess.CalledProcessError:
            Logger.warn("Could not remove image.")
