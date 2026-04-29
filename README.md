# 🛡️ Secure Development Workspace (Python CLI)

A modular, cross-platform CLI tool to manage a containerized, encrypted development environment.

## 🚀 Quick Start

### 1. Install Dependencies
Ensure you have Python 3.8+, Docker, and gocryptfs installed.

```bash
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

## 🛠️ Commands

| Command | Description |
| :--- | :--- |
| `init` | Checks dependencies, initializes the vault, and generates `docker-compose.yml`. |
| `start` | Mounts the vault (password required) and starts the workspace container. |
| `stop` | Gracefully shuts down the container and locks the vault. |
| `delete` | **Wipe everything**: Deletes data, images, and configuration. |
| `decrypt` | Only unlocks the vault (useful for host-side file access). |

## 📁 Project Structure

- `main.py`: Main CLI entry point.
- `src/vault.py`: Handles gocryptfs operations.
- `src/container.py`: Handles Docker Compose operations.
- `src/config.py`: Manages `.env` and path expansion.
- `src/utils.py`: Logging and dependency verification.

---
*Built for security and modularity.*
