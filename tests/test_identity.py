import os
from pathlib import Path
from src.identity import IdentityManager
from src.config import Config

def test_identity_path_mapping(monkeypatch):
    monkeypatch.setenv("ROOT_WORKSPACE_DIR", "/home/host/work")
    monkeypatch.setenv("MOUNT_DIR_NAME", "dec")
    monkeypatch.setenv("SSH_KEY_DIR", "/home/dev/workspace/.custom_keys")
    
    config = Config()
    identity = IdentityManager(config)
    
    host_key_dir = identity.get_host_key_dir()
    
    # On host, it should be under the mount path
    assert str(host_key_dir).endswith("dec/.custom_keys")
    assert "/home/host/work" in str(host_key_dir)

def test_ssh_command_generation(monkeypatch):
    monkeypatch.setenv("ROOT_WORKSPACE_DIR", "/tmp/work")
    monkeypatch.setenv("SSH_PORT", "2222")
    
    config = Config()
    identity = IdentityManager(config)
    
    cmd = identity.get_ssh_command()
    assert "ssh -i" in cmd
    assert "id_ed25519" in cmd
    assert "-p 2222" in cmd
    assert "dev@localhost" in cmd

def test_display_keys(tmp_path, test_config, capsys):
    identity = IdentityManager(test_config)
    
    # Create mock key files
    key_dir = identity.get_host_key_dir()
    key_dir.mkdir(parents=True, exist_ok=True)
    
    pub_key = key_dir / "id_ed25519.pub"
    priv_key = key_dir / "id_ed25519"
    
    pub_key.write_text("public content")
    priv_key.write_text("private content")
    
    # Test display
    identity.display_keys()
    captured = capsys.readouterr()
    assert "public content" in captured.out
    assert "private content" in captured.out

def test_display_keys_missing(test_config, capsys):
    identity = IdentityManager(test_config)
    # Ensure directory doesn't exist
    if test_config.mount_path.exists():
        import shutil
        shutil.rmtree(test_config.mount_path)
    
    # This should call Logger.error but with exit_code=None so it shouldn't exit
    identity.display_keys()
    captured = capsys.readouterr()
    assert "Vault is locked" in captured.out

def test_get_host_key_dir_external(monkeypatch, test_config):
    # Set SSH_KEY_DIR to a path that DOES NOT start with container_root
    monkeypatch.setenv("SSH_KEY_DIR", "/opt/external/keys")
    identity = IdentityManager(test_config)
    
    host_dir = identity.get_host_key_dir()
    # It should fallback to os.path.basename
    assert host_dir == test_config.mount_path / "keys"



