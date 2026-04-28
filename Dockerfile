# Use Ubuntu 24.04 as the base
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Build arguments for security
ARG SSH_PORT=2222
ARG SSH_PUB_PATH
ARG GIT_PRIV_PATH

# 1. Update and install core utilities + OpenSSH Server
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    software-properties-common curl wget unzip git \
    python3-pip python3-virtualenv iputils-ping net-tools sudo openssh-server && \
    apt-get remove -y docker.io docker-compose docker-compose-v2 docker-doc podman-docker containerd runc || true

# 2. Setup SSH Config
RUN mkdir /var/run/sshd && \
    sed -i "s/#Port 22/Port ${SSH_PORT}/" /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# 3. Install Node.js (LTS) and global tools
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g typescript ts-node nodemon pm2

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
    apt-get install -y docker-ce-cli docker-buildx-plugin docker-compose-plugin

# 5. Download and install VS Code CLI
RUN curl -Lk 'https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-x64' --output vscode_cli.tar.gz && \
    tar -xf vscode_cli.tar.gz && \
    mv code /usr/local/bin/ && \
    rm vscode_cli.tar.gz

# 6. Cleanup
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# 7. Create 'dev' user 
RUN useradd -m -s /bin/bash dev && \
    usermod -aG sudo dev && \
    echo "dev ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# 8. Inject Keys using ARGs
RUN mkdir -p /home/dev/.ssh && chmod 700 /home/dev/.ssh

# Use the ARGs to copy the specific files passed during build
COPY ${SSH_PUB_PATH} /home/dev/.ssh/authorized_keys
COPY ${GIT_PRIV_PATH} /home/dev/.ssh/id_ed25519

# 9. Finalize SSH Config
RUN echo "Host github.com\n\tHostName github.com\n\tUser git\n\tIdentityFile ~/.ssh/id_ed25519\n\tStrictHostKeyChecking no" > /home/dev/.ssh/config && \
    chown -R dev:dev /home/dev/.ssh && \
    chmod 600 /home/dev/.ssh/authorized_keys /home/dev/.ssh/id_ed25519 /home/dev/.ssh/config

# Generate Host Keys 
RUN ssh-keygen -A

# We must switch back to root to start the SSH daemon
USER root

WORKDIR /home/dev/workspace

# 10. Start SSH Agent for 'dev' user, then start sshd as root
CMD ["/bin/bash", "-c", "eval $(ssh-agent -s) && ssh-add /home/dev/.ssh/id_ed25519 && /usr/sbin/sshd -D"]