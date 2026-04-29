#!/bin/bash

set -euo pipefail

# --- Utility Functions ---
log() { echo -e "\033[1;34m[*] $1\033[0m"; }
info() { echo -e "\033[1;32m[+] $1\033[0m"; }
warn() { echo -e "\033[1;33m[!] $1\033[0m"; }
error() { echo -e "\033[1;31m[X] $1\033[0m"; exit 1; }

# --- Load Configuration ---
if [ ! -f .env ]; then
    warn ".env file not found, creating from .env.example"
    cp .env.example .env
fi

# Load variables from .env
if [ -f .env ]; then
    # We use a while loop to read and export, allowing for simple variable expansion
    while IFS='=' read -r key value; do
        [[ "$key" =~ ^#.*$ ]] && continue
        [[ -z "$key" ]] && continue
        # Expand value if it contains $HOME
        value=$(eval echo "$value")
        export "$key"="$value"
    done < .env
fi


# Defaults if not set in .env
ROOT_WORKSPACE_DIR="${ROOT_WORKSPACE_DIR:-$HOME/.workspace}"
CIPHER_DIR="$ROOT_WORKSPACE_DIR/${CIPHER_DIR_NAME:-encrypted_workspace}"
MOUNT_DIR="$ROOT_WORKSPACE_DIR/${MOUNT_DIR_NAME:-decrypted_workspace}"
SSH_PORT="${SSH_PORT:-2222}"
CONTAINER_NAME="${CONTAINER_NAME:-dev_workspace}"
IMAGE_NAME="${IMAGE_NAME:-dev_workspace_image}"
SSH_KEY_DIR="${SSH_KEY_DIR:-/home/dev/workspace/.ssh_keys}"



log "Initializing Secure Workspace..."

# 1. Install Dependencies
log "Checking dependencies..."
if ! command -v gocryptfs &> /dev/null || ! command -v ssh &> /dev/null; then
    warn "Dependencies missing, attempting to install..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y gocryptfs openssh-client
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y gocryptfs openssh-clients
    elif command -v yum &> /dev/null; then
        sudo yum install -y gocryptfs openssh-clients
    elif command -v pacman &> /dev/null; then
        sudo pacman -Sy --noconfirm gocryptfs openssh
    elif command -v zypper &> /dev/null; then
        sudo zypper install -y gocryptfs openssh
    else
        error "Could not detect package manager. Please install gocryptfs and openssh-client manually."
    fi
else
    info "Core dependencies are already installed."
fi



# 2. Setup Environment
mkdir -p "$ROOT_WORKSPACE_DIR"

# 3. Handle Encryption & Mount Cleanup
log "Cleaning up stale mounts..."
fusermount -uz "$MOUNT_DIR" 2>/dev/null || true
# Only try sudo umount if fusermount failed and it's still mounted
if mountpoint -q "$MOUNT_DIR"; then
    warn "Attempting sudo umount as fallback..."
    sudo umount -l "$MOUNT_DIR" 2>/dev/null || true
fi

# Ensure directories exist
mkdir -p "$CIPHER_DIR"
mkdir -p "$MOUNT_DIR"

if [ ! -f "$CIPHER_DIR/gocryptfs.conf" ]; then
    warn "Initializing new gocryptfs vault..."
    gocryptfs -init "$CIPHER_DIR"
fi

# 4. Generate Docker Compose
log "Generating docker-compose.yml..."
cat <<EOF > docker-compose.yml
services:
  dev:
    build:
      context: .
      args:
        SSH_PORT: $SSH_PORT
    image: $IMAGE_NAME
    container_name: $CONTAINER_NAME

    network_mode: host
    environment:
      - SSH_KEY_DIR=$SSH_KEY_DIR
    volumes:
      - $MOUNT_DIR:/home/dev/workspace
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped
EOF

# user_allow_other is required for Docker to see files inside the mount
log "Enabling user_allow_other..."
if ! grep -q "^user_allow_other" /etc/fuse.conf 2>/dev/null; then
    if grep -q "^#user_allow_other" /etc/fuse.conf 2>/dev/null; then
        warn "Enabling user_allow_other in /etc/fuse.conf (requires sudo)..."
        sudo sed -i 's/#user_allow_other/user_allow_other/' /etc/fuse.conf
    else
        warn "Could not find user_allow_other in /etc/fuse.conf. You might need to add it manually if mounting fails."
    fi
fi

info "Setup complete."
warn "Start with: ./start.sh"
info "Keys will be generated inside the container on first start."