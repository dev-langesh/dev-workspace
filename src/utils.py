import subprocess
import sys
import os
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

    @classmethod
    def ensure_system_dependencies(cls):
        """Detects the Linux package manager and attempts to install dependencies."""
        managers = {
            "apt": {
                "update": ["sudo", "apt", "update"],
                "install": ["sudo", "apt", "install", "-y"],
                "packages": ["gocryptfs", "openssh-client", "fuse3"]
            },
            "dnf": {
                "update": ["sudo", "dnf", "check-update"],
                "install": ["sudo", "dnf", "install", "-y"],
                "packages": ["gocryptfs", "openssh-clients", "fuse"],
                "pre_install": ["sudo", "dnf", "install", "-y", "dnf-plugins-core"],
                "copr": ["sudo", "dnf", "copr", "enable", "-y", "svenko70/gocryptfs"]
            },
            "yum": {
                "update": [],
                "install": ["sudo", "yum", "install", "-y"],
                "packages": ["gocryptfs", "openssh-clients", "fuse"]
            },
            "pacman": {
                "update": ["sudo", "pacman", "-Sy"],
                "install": ["sudo", "pacman", "-S", "--noconfirm"],
                "packages": ["gocryptfs", "openssh"]
            },
            "zypper": {
                "update": [],
                "install": ["sudo", "zypper", "install", "-y"],
                "packages": ["gocryptfs", "openssh", "fuse"]
            }
        }

        for manager, cmd in managers.items():
            if shutil.which(manager):
                try:
                    Logger.log(f"Detected package manager: {manager}. Ensuring dependencies...")
                    if cmd.get("pre_install"):
                        pre_cmd = cmd["pre_install"]
                        if os.getuid() == 0 and pre_cmd[0] == "sudo":
                            pre_cmd = pre_cmd[1:]
                        subprocess.run(pre_cmd, check=True)
                    
                    if cmd.get("copr"):
                        copr_cmd = cmd["copr"]
                        if os.getuid() == 0 and copr_cmd[0] == "sudo":
                            copr_cmd = copr_cmd[1:]
                        subprocess.run(copr_cmd, check=True)

                    if cmd["update"]:
                        # dnf check-update returns 100 if updates are available, which is not an error
                        update_cmd = cmd["update"]
                        if os.getuid() == 0 and update_cmd[0] == "sudo":
                            update_cmd = update_cmd[1:]
                        subprocess.run(update_cmd, check=False)
                    
                    install_cmd = cmd["install"] + cmd["packages"]
                    if os.getuid() == 0 and install_cmd[0] == "sudo":
                        install_cmd = install_cmd[1:]
                    subprocess.run(install_cmd, check=True)


                    Logger.info("System dependencies updated successfully.")
                    return True
                except subprocess.CalledProcessError as e:
                    Logger.warn(f"Failed to install dependencies via {manager}: {e}")
                    # If it's gocryptfs that's missing on Fedora/others, try binary download
                    if manager == "dnf" or manager == "yum":
                         return cls._install_gocryptfs_binary()
                    break
        
        # Final fallback for any distro
        if not shutil.which("gocryptfs"):
            return cls._install_gocryptfs_binary()

        Logger.warn("Could not automatically install dependencies. Please ensure gocryptfs and openssh-client are installed manually.")
        return False

    @classmethod
    def _install_gocryptfs_binary(cls):
        """Downloads and installs the gocryptfs static binary as a fallback."""
        Logger.warn("Attempting to install gocryptfs static binary from GitHub...")
        version = "v2.4.0"
        url = f"https://github.com/rfjakob/gocryptfs/releases/download/{version}/gocryptfs_{version}_linux-static_amd64.tar.gz"
        tar_path = "/tmp/gocryptfs.tar.gz"
        
        try:
            import urllib.request
            import tarfile
            
            Logger.info(f"Downloading {url}...")
            urllib.request.urlretrieve(url, tar_path)
            
            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extract("gocryptfs", path="/tmp")
            
            # Ensure target directory exists
            os.makedirs("/usr/local/bin", exist_ok=True)
            
            install_cmd = ["sudo", "mv", "/tmp/gocryptfs", "/usr/local/bin/gocryptfs"]

            if os.getuid() == 0:
                install_cmd = install_cmd[1:]
            
            subprocess.run(install_cmd, check=True)
            subprocess.run(["sudo", "chmod", "+x", "/usr/local/bin/gocryptfs"] if os.getuid() != 0 else ["chmod", "+x", "/usr/local/bin/gocryptfs"], check=True)
            
            Logger.info("gocryptfs static binary installed successfully to /usr/local/bin/gocryptfs")
            return True
        except Exception as e:
            Logger.error(f"Failed to install gocryptfs binary: {e}")
            return False

