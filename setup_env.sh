#!/bin/bash

# Configuration
ROOT_WORKSPACE_DIR="$HOME/.workspace"
CIPHER_DIR="$ROOT_WORKSPACE_DIR/.enc"
MOUNT_DIR="$ROOT_WORKSPACE_DIR/dec"

# Local key paths
LOCAL_KEY_DIR="./keys"
SSH_KEY_NAME="id_ed25519_ssh"
GIT_KEY_NAME="id_ed25519_github"

SSH_PORT=2222
EMAIL="example@example.com" 

echo "[*] Initializing ED25519 Secure Workspace..."

# 1. Install Dependencies
sudo apt update && sudo apt install -y gocryptfs openssh-client

# 2. Key Generation Logic
mkdir -p "$LOCAL_KEY_DIR"
[ ! -f "$LOCAL_KEY_DIR/$SSH_KEY_NAME" ] && ssh-keygen -t ed25519 -C "$EMAIL" -f "$LOCAL_KEY_DIR/$SSH_KEY_NAME" -N "" -q
[ ! -f "$LOCAL_KEY_DIR/$GIT_KEY_NAME" ] && ssh-keygen -t ed25519 -C "$EMAIL" -f "$LOCAL_KEY_DIR/$GIT_KEY_NAME" -N "" -q

# 3. Handle Encryption & Mount Cleanup
echo "[*] Cleaning up stale mounts..."
# Lazy unmount to clear any 'Device Busy' or 'd???????' states
fusermount -uz "$MOUNT_DIR" 2>/dev/null || true
sudo umount -l "$MOUNT_DIR" 2>/dev/null || true

# Ensure directories exist and are owned by you
mkdir -p "$CIPHER_DIR"
if [ ! -d "$MOUNT_DIR" ]; then
    mkdir -p "$MOUNT_DIR"
fi

if [ ! -f "$CIPHER_DIR/gocryptfs.conf" ]; then
    echo "[!] Initializing new gocryptfs vault..."
    gocryptfs -init "$CIPHER_DIR"
fi

# IMPORTANT: -allow_other is required for Docker to see files inside the mount
echo "[*] Mounting Vault..."
sudo sed -i 's/#user_allow_other/user_allow_other/' /etc/fuse.conf
gocryptfs -allow_other "$CIPHER_DIR" "$MOUNT_DIR"

# 4. Generate Docker Compose
cat <<EOF > docker-compose.yml
services:
  dev:
    build:
      context: .
      args:
        SSH_PORT: $SSH_PORT
        SSH_PUB_PATH: "$LOCAL_KEY_DIR/${SSH_KEY_NAME}.pub"
        GIT_PRIV_PATH: "$LOCAL_KEY_DIR/${GIT_KEY_NAME}"
    container_name: dev_workspace
    network_mode: host
    volumes:
      - $MOUNT_DIR:/home/dev/workspace
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped
EOF

echo "----------------------------------------------------------------"
echo "[+] Done. Key paths are mapped dynamically."
echo "[!] IMPORTANT: Ensure 'user_allow_other' is uncommented in /etc/fuse.conf"
echo "[!] Build: docker compose up -d --build"
echo "[!] SSH Access: ssh -i $LOCAL_KEY_DIR/$SSH_KEY_NAME -p $SSH_PORT dev@localhost"