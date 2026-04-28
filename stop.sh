#!/bin/bash

# Configuration
MOUNT_DIR="$HOME/.workspace/dec"

echo "[*] Shutting Down Secure Environment..."

# 1. Stop the Docker Container
# We stop first so Docker releases the file handles on the mount
if [ "$(docker ps -q -f name=dev_workspace)" ]; then
    echo "[*] Stopping Docker container..."
    docker compose stop
else
    echo "[!] Container is not running."
fi

# 2. Unmount the Vault
if mountpoint -q "$MOUNT_DIR"; then
    echo "[*] Locking Vault (Unmounting)..."
    # -u for unmount, -z for lazy (cleans up even if a process is slow to exit)
    fusermount -uz "$MOUNT_DIR"
    
    if [ $? -eq 0 ]; then
        echo "[+] Vault locked. Data is now encrypted and invisible."
    else
        echo "[X] Failed to unmount. Check if any shells are still 'cd'd into the folder."
    fi
else
    echo "[!] Vault was not mounted."
fi

echo "[*] Done."