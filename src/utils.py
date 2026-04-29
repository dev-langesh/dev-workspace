import subprocess
import sys
import shutil
from typing import List

class Logger:
    @staticmethod
    def log(message: str):
        print(f"[*] {message}")

    @staticmethod
    def info(message: str):
        print(f"[+] {message}")

    @staticmethod
    def warn(message: str):
        print(f"[!] {message}")

    @staticmethod
    def error(message: str, exit_code: int = 1):
        print(f"[ERROR] {message}")
        if exit_code is not None:
            sys.exit(exit_code)

class DependencyChecker:
    @staticmethod
    def check_all(dependencies: List[str]):
        Logger.log("Checking dependencies...")
        missing = []
        for dep in dependencies:
            if shutil.which(dep) is None:
                missing.append(dep)
        
        if missing:
            Logger.warn(f"Missing dependencies: {', '.join(missing)}")
            return missing
        
        Logger.info("All core dependencies found.")
        return []

    @staticmethod
    def ensure_apt_dependencies():
        """Attempts to install gocryptfs and openssh-client on Debian systems."""
        try:
            # Check if we are on a Debian-based system
            with open("/etc/os-release") as f:
                if "debian" in f.read().lower() or "ubuntu" in f.read().lower():
                    Logger.log("Debian-based system detected. Ensuring system dependencies...")
                    subprocess.run(["sudo", "apt", "update"], check=True)
                    subprocess.run(["sudo", "apt", "install", "-y", "gocryptfs", "openssh-client"], check=True)
                    Logger.info("System dependencies updated.")
        except Exception as e:
            Logger.warn(f"Could not automatically install dependencies: {e}")
            Logger.warn("Please ensure gocryptfs and openssh-client are installed manually.")
