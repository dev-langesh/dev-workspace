import subprocess
import sys
import shutil
from typing import List
from colorama import Fore, Style, init

# Initialize colorama for cross-platform support
init(autoreset=True)

class Logger:
    @staticmethod
    def log(message: str):
        print(f"{Fore.CYAN}{Style.BRIGHT}[*] {Style.NORMAL}{message}")

    @staticmethod
    def info(message: str):
        print(f"{Fore.GREEN}{Style.BRIGHT}[+] {Style.NORMAL}{message}")

    @staticmethod
    def warn(message: str):
        print(f"{Fore.YELLOW}{Style.BRIGHT}[!] {Style.NORMAL}{message}")

    @staticmethod
    def error(message: str, exit_code: int = 1):
        print(f"{Fore.RED}{Style.BRIGHT}[X] {message}")
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
    def ensure_system_dependencies():
        """Detects the Linux package manager and attempts to install dependencies."""
        managers = {
            "apt": {
                "update": ["sudo", "apt", "update"],
                "install": ["sudo", "apt", "install", "-y"],
                "packages": ["gocryptfs", "openssh-client"]
            },
            "dnf": {
                "update": [],
                "install": ["sudo", "dnf", "install", "-y"],
                "packages": ["gocryptfs", "openssh-clients"]
            },
            "yum": {
                "update": [],
                "install": ["sudo", "yum", "install", "-y"],
                "packages": ["gocryptfs", "openssh-clients"]
            },
            "pacman": {
                "update": ["sudo", "pacman", "-Sy"],
                "install": ["sudo", "pacman", "-S", "--noconfirm"],
                "packages": ["gocryptfs", "openssh"]
            },
            "zypper": {
                "update": [],
                "install": ["sudo", "zypper", "install", "-y"],
                "packages": ["gocryptfs", "openssh"]
            }
        }

        for manager, cmd in managers.items():
            if shutil.which(manager):
                try:
                    Logger.log(f"Detected package manager: {manager}. Ensuring dependencies...")
                    if cmd["update"]:
                        subprocess.run(cmd["update"], check=True)
                    
                    install_cmd = cmd["install"] + cmd["packages"]
                    subprocess.run(install_cmd, check=True)
                    Logger.info("System dependencies updated successfully.")
                    return True
                except subprocess.CalledProcessError as e:
                    Logger.warn(f"Failed to install dependencies via {manager}: {e}")
                    break
        
        Logger.warn("Could not automatically install dependencies. Please ensure gocryptfs and openssh-client are installed manually.")
        return False

