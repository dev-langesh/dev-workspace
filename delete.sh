#!/bin/bash

# delete.sh - Complete cleanup of the Secure Development Workspace
# WARNING: This will delete your encrypted data and keys!

set -euo pipefail

# --- Logging Helpers ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[*] $1${NC}"; }
info() { echo -e "${NC}$1${NC}"; }
warn() { echo -e "${YELLOW}[!] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; }

# --- Confirmation ---
warn "CRITICAL WARNING: This script will PERMANENTLY DELETE:"
info "1. The Docker container and networks"
info "2. The Docker image"
info "3. The encrypted vault and all your source code"
info "4. All generated SSH keys"
echo ""
read -p "Are you absolutely sure you want to proceed? (type 'yes' to confirm): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    info "Cleanup cancelled."
    exit 0
fi

# --- Load Environment ---
if [ -f .env ]; then
    while IFS='=' read -r key value; do
        [[ "$key" =~ ^#.*$ ]] && continue
        [[ -z "$key" ]] && continue
        value=$(eval echo "$value")
        export "$key"="$value"
    done < .env
else
    error ".env file not found. Cannot determine paths safely."
    exit 1
fi

# Defaults if not set
ROOT_WORKSPACE_DIR="${ROOT_WORKSPACE_DIR:-$HOME/.workspace}"
MOUNT_DIR="$ROOT_WORKSPACE_DIR/${MOUNT_DIR_NAME:-decrypted_workspace}"
CONTAINER_NAME="${CONTAINER_NAME:-dev_workspace}"
IMAGE_NAME="${IMAGE_NAME:-dev_workspace_image}"

log "Starting complete cleanup..."

# 1. Stop and Remove Docker Container
if [ "$(docker ps -aq -f name=^/${CONTAINER_NAME}$)" ]; then
    log "Stopping and removing container..."
    docker compose down --volumes --remove-orphans || true
else
    info "Container not found."
fi

# 2. Remove Docker Image
if [ "$(docker images -q "$IMAGE_NAME" 2>/dev/null)" ]; then
    log "Removing Docker image: $IMAGE_NAME..."
    docker rmi "$IMAGE_NAME" || warn "Could not remove image. It might be in use."
fi

# 3. Unmount Vault
if mountpoint -q "$MOUNT_DIR"; then
    log "Unmounting Vault..."
    fusermount -uz "$MOUNT_DIR" || sudo umount -l "$MOUNT_DIR" || true
fi

# 4. Delete Workspace Data
if [ -d "$ROOT_WORKSPACE_DIR" ]; then
    log "Deleting workspace directory: $ROOT_WORKSPACE_DIR..."
    rm -rf "$ROOT_WORKSPACE_DIR"
    info "Workspace data wiped."
fi

# 5. Clean up generated files
log "Cleaning up local configuration..."
rm -f docker-compose.yml
# Note: We keep .env and .env.example unless you want them gone too.

log "Cleanup complete. The environment has been wiped."
