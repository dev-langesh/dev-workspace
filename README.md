# 🛡️ Secure Development Workspace

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)

A production-ready, modular CLI tool designed to manage a containerized and encrypted development environment. 

---

## 📖 Table of Contents
- [Why Secure Workspace?](#-why-secure-workspace)
- [Quick Start](#-quick-start)
- [Accessing Your Workspace](#-accessing-your-workspace)
- [Security & Identity](#-security--identity)
- [GitHub Integration](#-github-integration)
- [CLI Commands](#-cli-commands)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔒 Why Secure Workspace?

In many shared server environments, your source code and secrets are vulnerable to anyone with root or physical access. This project solves that by creating an **encrypted "vault"** that is only decrypted and mounted into a secure Docker container when you are actively working. 

By combining **AES-256 encryption** (via gocryptfs) with **container isolation**, your development workspace remains a "black box" to everyone else on the server, keeping your private keys, source code, and configurations safe from prying eyes.

---

## 🚀 Quick Start

### 1. Setup Environment
Ensure you have `Python 3.8+` and `Docker` installed. 

**Supported Linux Distributions:**
The CLI automatically handles system dependencies (`gocryptfs`, `openssh`) for:
- **Ubuntu / Debian** (`apt`)
- **Fedora / CentOS / RHEL** (`dnf` / `yum`)
- **Arch Linux** (`pacman`)
- **openSUSE** (`zypper`)


```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
python3 -m pip install -r requirements.txt
```

### 2. Initialize
Setup your encrypted vault and configuration:
```bash
python3 main.py init
```

### 3. Start Workspace
Unlock the vault and launch the container:
```bash
python3 main.py start
```

---

## 🔌 Accessing Your Workspace

Once your workspace is running, you have two primary ways to connect:

### 1. VS Code Tunnel (Recommended)
The workspace comes with the **VS Code CLI pre-installed**. This allows you to create a secure tunnel to your local VS Code instance without complex network configuration.

```bash
code tunnel
```

### 2. Standard SSH
If your IDE doesn't support tunnels, or you prefer a traditional workflow, you can connect via SSH:
```bash
ssh -i path/to/your/private_key -p 2222 dev@[IP_ADDRESS]
```

Run `python3 main.py keys` to get the key pairs and their paths on the host.

---

## 🔒 Security & Identity

### SSH Hardening
The workspace is configured with production-grade security:
- **No Password Authentication**: Only key-based access is allowed.
- **No Root Login**: SSH access is restricted to the non-root `dev` user.
- **Port Isolation**: SSH runs on a non-standard port (default: 2222).

### Key Storage
Your SSH keys are generated **inside the container** on first launch and are stored directly within your encrypted vault. They are never saved to the host's unencrypted filesystem, ensuring your identity is protected even if the server is compromised while the vault is locked.

---

## 🐙 GitHub Integration

One of the major benefits of this workspace is the **seamless GitHub integration**. You do **not** need to generate Personal Access Tokens (PATs) or use the `gh` CLI.

1. **Get your Public Key**: You can run `python3 main.py keys` to get your key pairs and their paths on the host.
2. **Configure GitHub**: Copy that public key and add it to your [GitHub SSH Keys](https://github.com/settings/keys).
3. **Clone & Push**: You can now clone any repository and push changes immediately using SSH URLs (`git@github.com:user/repo.git`).

---

## 🛠️ CLI Commands

| Command | Description |
| :--- | :--- |
| `init` | Checks dependencies, initializes the vault, and generates `docker-compose.yml`. |
| `start` | Mounts the vault (password required) and starts the workspace container. |
| `stop` | Gracefully shuts down the container and locks the vault. |
| `delete` | **Wipe everything**: Deletes data, images, and configuration. |
| `decrypt` | Only unlocks the vault (useful for host-side file access). |
| `encrypt` | Only locks the vault (useful for host-side file access). |
| `keys` | Show the SSH keys and their host-side paths (inside the decrypted vault). |

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for improvements or find any issues, feel free to open a Pull Request or create an Issue.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
