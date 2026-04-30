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
        BASE_IMAGE: {self.config.base_image}
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

    def image_exists(self, image_name):
        """Checks if a docker image exists locally."""
        try:
            result = subprocess.run(["docker", "image", "inspect", image_name], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def pull_image(self, image_name):
        """Attempts to pull a docker image from a remote registry."""
        Logger.log(f"Attempting to pull '{image_name}'...")
        try:
            subprocess.run(["docker", "pull", image_name], check=True)
            return True
        except subprocess.CalledProcessError:
            return False



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
