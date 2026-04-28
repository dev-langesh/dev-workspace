#!/bin/bash

# Configuration (Matching your previous setup)
ROOT_WORKSPACE_DIR="$HOME/.workspace"
CIPHER_DIR="$ROOT_WORKSPACE_DIR/.enc"
MOUNT_DIR="$ROOT_WORKSPACE_DIR/dec"

echo "[*] Starting Secure Environment..."

# 1. Check if already mounted
if mountpoint -q "$MOUNT_DIR"; then
    echo "[!] Vault is already mounted."
else
    # Force clean stale mounts if they exist
    fusermount -uz "$MOUNT_DIR" 2>/dev/null || true
    
    echo "[*] Mounting Encrypted Vault..."
    # -allow_other is critical for Docker visibility
    gocryptfs -allow_other "$CIPHER_DIR" "$MOUNT_DIR"
    
    if [ $? -ne 0 ]; then
        echo "[X] Mount failed. Check your password or /etc/fuse.conf"
        exit 1
    fi
fi

# 2. Start the container
echo "[*] Starting Docker Container..."
docker compose up -d --build

echo "[+] Success. Your workspace is decrypted and the container is running."
echo "[+] Access via: ssh -i ./keys/id_ed25519_ssh -p 2222 dev@localhost"