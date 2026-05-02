import os
import shutil
import pytest
from src.vault import VaultManager
from src.config import Config
from pathlib import Path




def test_vault_lifecycle(test_config, monkeypatch):
    from src.utils import DependencyChecker
    DependencyChecker.ensure_system_dependencies()
    
    monkeypatch.setenv("TEST_PASSWORD", "testpassword123")
    vault = VaultManager(test_config)

    
    # 1. Init
    assert vault.init() is True
    assert (test_config.cipher_path / "gocryptfs.conf").exists()
    
    # 2. Mount
    assert vault.mount() is True
    assert vault.is_mounted() is True
    
    # 3. Write data
    test_file = test_config.mount_path / "test.txt"
    test_file.write_text("secure data")
    
    # 4. Unmount
    assert vault.unmount() is True
    assert vault.is_mounted() is False
    assert not test_file.exists()




def test_vault_init_already_exists(test_config, mocker):
    vault = VaultManager(test_config)
    # Create the config file to simulate already initialized
    test_config.cipher_path.mkdir(parents=True, exist_ok=True)
    (test_config.cipher_path / "gocryptfs.conf").touch()
    
    assert vault.init() is True

def test_enable_allow_other(test_config, mocker):
    vault = VaultManager(test_config)
    fuse_path = test_config.root_dir / "fuse.conf"
    test_config.fuse_conf = fuse_path
    
    # 1. File doesn't exist
    vault._enable_allow_other() # Should just return
    
    # 2. File exists but commented
    fuse_path.write_text("#user_allow_other")
    mock_run = mocker.patch("subprocess.run")
    vault._enable_allow_other()
    assert mock_run.called
    assert "sed" in mock_run.call_args[0][0]

    # 3. File exists and already enabled
    fuse_path.write_text("user_allow_other")
    mock_run.reset_mock()
    vault._enable_allow_other()
    assert not mock_run.called

def test_mount_unmount_logic(test_config, mocker):
    vault = VaultManager(test_config)
    mock_run = mocker.patch("subprocess.run")
    
    # Mock is_mounted to simulate different states
    mocker.patch("os.path.ismount", side_effect=[False, True, True, False])
    
    # Mount
    assert vault.mount() is True
    assert "gocryptfs" in mock_run.call_args_list[0][0][0]
    
    # Already mounted
    assert vault.mount() is True
    
    # Unmount
    assert vault.unmount() is True
    assert "fusermount" in mock_run.call_args_list[1][0][0]
    
    # Already unmounted
    assert vault.unmount() is True

def test_mount_already_mounted(test_config, mocker):
    vault = VaultManager(test_config)
    mocker.patch("os.path.ismount", return_value=True)
    assert vault.mount() is True

def test_enable_allow_other_error(test_config, mocker):
    vault = VaultManager(test_config)
    fuse_path = test_config.root_dir / "fuse.conf"
    test_config.fuse_conf = fuse_path
    fuse_path.write_text("#user_allow_other")
    
    # Mock subprocess.run to fail
    import subprocess
    mocker.patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "sed"))
    
    vault._enable_allow_other() # Should log error and return

def test_enable_allow_other_append(test_config, mocker):
    vault = VaultManager(test_config)
    fuse_path = test_config.root_dir / "fuse.conf"
    test_config.fuse_conf = fuse_path
    
    # File exists but doesn't have the string at all
    fuse_path.write_text("other_config=1")
    mock_run = mocker.patch("subprocess.run")
    vault._enable_allow_other()
    assert mock_run.called
    assert "echo 'user_allow_other'" in str(mock_run.call_args)

def test_init_fail(test_config, mocker):
    vault = VaultManager(test_config)
    import subprocess
    mocker.patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "gocryptfs"))
    mocker.patch("sys.exit")
    
    assert vault.init() is False

def test_vault_errors(test_config, mocker):

    vault = VaultManager(test_config)
    import subprocess
    mocker.patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "cmd"))
    mocker.patch("os.path.ismount", return_value=False)
    mocker.patch("sys.exit")
    
    assert vault.mount() is False
    
    # Mock is_mounted to be True for unmount test
    mocker.patch("os.path.ismount", return_value=True)
    assert vault.unmount() is False



