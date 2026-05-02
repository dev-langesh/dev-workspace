import shutil
from src.utils import DependencyChecker

def test_check_dependencies_pass():
    # In the docker environment, common tools like 'ls' and 'sh' must exist.
    # We also expect gocryptfs if the runner installed it correctly.
    checker = DependencyChecker()
    missing = checker.check_all(["ls", "sh"])
    assert missing == [], f"Expected no missing dependencies, but found: {missing}"


def test_check_dependencies_fail():
    checker = DependencyChecker()
    assert checker.check_all(["non_existent_binary_xyz"]) == ["non_existent_binary_xyz"]

def test_ensure_system_dependencies_real():
    checker = DependencyChecker()
    # On Ubuntu/Fedora/Arch, this should detect the manager and return without error
    # since dependencies are already installed by the runner.
    checker.ensure_system_dependencies()

import pytest
@pytest.mark.parametrize("manager_bin,expected_cmd", [
    ("apt", "apt"),
    ("dnf", "dnf"),
    ("pacman", "pacman"),
    ("zypper", "zypper")
])
def test_ensure_system_dependencies_parametrized(mocker, manager_bin, expected_cmd):
    checker = DependencyChecker()
    # Mock shutil.which to find the specific manager
    mocker.patch("shutil.which", side_effect=lambda x: f"/usr/bin/{manager_bin}" if x == manager_bin else None)
    mock_run = mocker.patch("subprocess.run")
    
    checker.ensure_system_dependencies()
    assert mock_run.called
    assert expected_cmd in str(mock_run.call_args_list[0])

def test_ensure_system_dependencies_none(mocker):
    checker = DependencyChecker()
    # Mock all managers as missing
    mocker.patch("shutil.which", return_value=None)
    # Mock binary install to return False to test the final failure path
    mocker.patch.object(DependencyChecker, "_install_gocryptfs_binary", return_value=False)
    assert checker.ensure_system_dependencies() is False

def test_ensure_system_dependencies_fail(mocker):
    checker = DependencyChecker()
    # Mock apt as existing but failing
    mocker.patch("shutil.which", side_effect=lambda x: "/usr/bin/apt" if x == "apt" else None)
    import subprocess
    mocker.patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "apt update"))
    # Mock binary install to return False
    mocker.patch.object(DependencyChecker, "_install_gocryptfs_binary", return_value=False)
    
    assert checker.ensure_system_dependencies() is False

def test_install_gocryptfs_binary_mocked(mocker):
    # Test the success path of _install_gocryptfs_binary with heavy mocking
    mocker.patch("urllib.request.urlretrieve")
    mocker.patch("tarfile.open")
    mocker.patch("os.makedirs")
    mocker.patch("subprocess.run")
    mocker.patch("os.getuid", return_value=0)
    
    assert DependencyChecker._install_gocryptfs_binary() is True







