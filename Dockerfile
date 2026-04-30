# Use a build argument for the base image
ARG BASE_IMAGE=ubuntu:24.04
FROM ${BASE_IMAGE}


# Build arguments
ARG SSH_PORT=2222
ARG SSH_PUB_PATH

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# 1. Update and install core utilities + OpenSSH Server
# Combining commands to reduce layers and cleaning up cache
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    software-properties-common \
    curl \
    wget \
    unzip \
    git \
    python3-pip \
    python3-virtualenv \
    iputils-ping \
    net-tools \
    sudo \
    openssh-server \
    ca-certificates && \
    # Cleanup unnecessary packages
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 2. Setup SSH Config
RUN mkdir /var/run/sshd && \
    sed -i "s/#Port 22/Port ${SSH_PORT}/" /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    # Add security headers
    echo "AllowTcpForwarding yes" >> /etc/ssh/sshd_config && \
    echo "X11Forwarding no" >> /etc/ssh/sshd_config

# 3. Install Node.js (LTS) and global tools
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g typescript ts-node nodemon pm2 && \
    rm -rf /root/.npm

# 4. Setup Official Docker Repository and Install CLI
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo \
      "Types: deb \n\
URIs: https://download.docker.com/linux/ubuntu \n\
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") \n\
Components: stable \n\
Architectures: $(dpkg --print-architecture) \n\
Signed-By: /etc/apt/keyrings/docker.asc" | tee /etc/apt/sources.list.d/docker.sources > /dev/null && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli docker-buildx-plugin docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/*

# 5. Download and install VS Code CLI
RUN curl -Lk 'https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-x64' --output vscode_cli.tar.gz && \
    tar -xf vscode_cli.tar.gz && \
    mv code /usr/local/bin/ && \
    rm vscode_cli.tar.gz

# 6. Create 'dev' user 
RUN useradd -m -s /bin/bash dev && \
    usermod -aG sudo dev && \
    # Allow dev to use sudo without password for convenience in dev env,
    # but keep it restricted to 'dev' user.
    echo "dev ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# 7. Setup SSH for 'dev' user
USER dev
RUN mkdir -p /home/dev/.ssh && chmod 700 /home/dev/.ssh

# 8. Host Config for GitHub
RUN echo "Host github.com\n\tHostName github.com\n\tUser git\n\tIdentityFile ~/.ssh/id_ed25519\n\tStrictHostKeyChecking no" > /home/dev/.ssh/config && \
    chmod 600 /home/dev/.ssh/config

# Generate Host Keys (as root)
USER root
RUN ssh-keygen -A

WORKDIR /home/dev/workspace

# 9. Copy and set up the bootstrap script
COPY --chmod=755 <<'EOF' /usr/local/bin/bootstrap.sh
#!/bin/bash
set -e

# Use environment variable for key directory, fallback to default
KEY_DIR="${SSH_KEY_DIR:-/home/dev/workspace/.ssh_keys}"
mkdir -p "$KEY_DIR"
chown dev:dev "$KEY_DIR"

PRIVATE_KEY="$KEY_DIR/id_ed25519"
PUBLIC_KEY="$KEY_DIR/id_ed25519.pub"

if [ ! -f "$PRIVATE_KEY" ]; then
    echo "[*] No SSH keys found. Generating new ED25519 key pair..."
    ssh-keygen -t ed25519 -f "$PRIVATE_KEY" -N "" -C "dev@workspace" -q
    chown dev:dev "$PRIVATE_KEY" "$PUBLIC_KEY"
    
    echo "----------------------------------------------------------------"
    echo ""
    echo "[!] NEW SSH KEY GENERATED"
    echo "Public Key: $PUBLIC_KEY"
    echo ""
    echo "Private Key: $PRIVATE_KEY"
    echo ""
    echo "----------------------------------------------------------------"
else
    echo "[*] Existing SSH keys found in vault."
fi

# Link keys to the standard SSH location
ln -sf "$PRIVATE_KEY" /home/dev/.ssh/id_ed25519
ln -sf "$PUBLIC_KEY" /home/dev/.ssh/id_ed25519.pub

# Authorize the key for SSH access to the container
cat "$PUBLIC_KEY" > /home/dev/.ssh/authorized_keys
chmod 600 /home/dev/.ssh/authorized_keys
chown dev:dev /home/dev/.ssh/authorized_keys

# Start SSH Agent
eval $(ssh-agent -s)
ssh-add /home/dev/.ssh/id_ed25519

echo "[+] Workspace Ready."
exec /usr/sbin/sshd -D
EOF

EXPOSE ${SSH_PORT}

CMD ["/usr/local/bin/bootstrap.sh"]