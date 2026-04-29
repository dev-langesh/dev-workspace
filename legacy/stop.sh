#!/bin/bash

set -euo pipefail

# --- Utility Functions ---
log() { echo -e "\033[1;34m[*] $1\033[0m"; }
info() { echo -e "\033[1;32m[+] $1\033[0m"; }
warn() { echo -e "\033[1;33m[!] $1\033[0m"; }
error() { echo -e "\033[1;31m[X] $1\033[0m"; exit 1; }

# --- Load Configuration ---
if [ ! -f .env ]; then
    warn ".env file not found. Assuming defaults for unmount."
    MOUNT_DIR="$HOME/.workspace/decrypted_workspace"
    CONTAINER_NAME="dev_workspace"
else
    # Load variables from .env
    while IFS='=' read -r key value; do
        [[ "$key" =~ ^#.*$ ]] && continue
        [[ -z "$key" ]] && continue
        value=$(eval echo "$value")
        export "$key"="$value"
    done < .env
    
    ROOT_WORKSPACE_DIR="${ROOT_WORKSPACE_DIR:-$HOME/.workspace}"
    MOUNT_DIR="$ROOT_WORKSPACE_DIR/${MOUNT_DIR_NAME:-decrypted_workspace}"
    CONTAINER_NAME="${CONTAINER_NAME:-dev_workspace}"
fi



log "Shutting Down Secure Environment..."

# 1. Stop the Docker Container
# We use 'down' to remove the container and release network resources
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ] || [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    log "Stopping and removing Docker container..."
    docker compose down
else
    info "Container is not running."
fi

# 2. Unmount the Vault
if mountpoint -q "$MOUNT_DIR"; then
    log "Locking Vault (Unmounting)..."
    # -u for unmount, -z for lazy (cleans up even if a process is slow to exit)
    fusermount -uz "$MOUNT_DIR"
    
    if [ $? -eq 0 ]; then
        info "Vault locked. Data is now encrypted and invisible."
    else
        error "Failed to unmount. Check if any shells are still 'cd'd into the folder."
    fi
else
    info "Vault was not mounted."
fi

log "Done."