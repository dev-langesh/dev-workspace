import os
import pytest
from src.config import Config
from pathlib import Path

def test_config_default_paths(monkeypatch):
    # Mock environment variables
    monkeypatch.setenv("ROOT_WORKSPACE_DIR", "/tmp/test_workspace")
    monkeypatch.setenv("CIPHER_DIR_NAME", "enc")
    monkeypatch.setenv("MOUNT_DIR_NAME", "dec")
    
    config = Config()
    
    assert config.root_dir == Path("/tmp/test_workspace").absolute()
    assert config.cipher_path == Path("/tmp/test_workspace/enc").absolute()
    assert config.mount_path == Path("/tmp/test_workspace/dec").absolute()

def test_config_env_expansion(monkeypatch):
    # Use a real home directory for expansion test
    fake_home = "/tmp/fake_home"
    monkeypatch.setenv("HOME", fake_home)
    monkeypatch.setenv("ROOT_WORKSPACE_DIR", "$HOME/my_work")
    
    config = Config()
    assert str(config.root_dir).startswith(fake_home)
    assert "my_work" in str(config.root_dir)

def test_config_docker_settings(monkeypatch):
    monkeypatch.setenv("CONTAINER_NAME", "custom_cont")
    monkeypatch.setenv("SSH_PORT", "9999")
    
    config = Config()
    assert config.container_name == "custom_cont"
    assert config.ssh_port == 9999

def test_config_repr(test_config):
    repr_str = repr(test_config)
    assert "Config" in repr_str
    assert "container=" in repr_str

