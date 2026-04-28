#!/bin/bash

set -euo pipefail

# --- Utility Functions ---
log() { echo -e "\033[1;34m[*] $1\033[0m"; }
info() { echo -e "\033[1;32m[+] $1\033[0m"; }
warn() { echo -e "\033[1;33m[!] $1\033[0m"; }
error() { echo -e "\033[1;31m[X] $1\033[0m"; exit 1; }

# --- Load Configuration ---
if [ ! -f .env ]; then
    error ".env file not found. Please run ./setup_env.sh first."
fi

# Load variables from .env
while IFS='=' read -r key value; do
    [[ "$key" =~ ^#.*$ ]] && continue
    [[ -z "$key" ]] && continue
    value=$(eval echo "$value")
    export "$key"="$value"
done < .env


ROOT_WORKSPACE_DIR="${ROOT_WORKSPACE_DIR:-$HOME/.workspace}"
CIPHER_DIR="$ROOT_WORKSPACE_DIR/${CIPHER_DIR_NAME:-encrypted_workspace}"
MOUNT_DIR="$ROOT_WORKSPACE_DIR/${MOUNT_DIR_NAME:-decrypted_workspace}"
SSH_PORT="${SSH_PORT:-2222}"

log "Starting Secure Environment..."

# 1. Check if already mounted
if mountpoint -q "$MOUNT_DIR"; then
    info "Vault is already mounted."
else
    # Force clean stale mounts if they exist
    fusermount -uz "$MOUNT_DIR" 2>/dev/null || true
    
    log "Mounting Encrypted Vault..."
    # -allow_other is critical for Docker visibility
    gocryptfs -allow_other "$CIPHER_DIR" "$MOUNT_DIR"
    
    if [ $? -ne 0 ]; then
        error "Mount failed. Check your password or /etc/fuse.conf"
    fi
fi

# 2. Start the container
log "Starting Docker Container..."
# Use Buildkit for secret support during build if needed
docker compose up -d --build

info "Success. Your workspace is decrypted and the container is running."
info "Access via: ssh -i private_key -p $SSH_PORT dev@localhost"
info "(Use the private key printed during the first container start)"