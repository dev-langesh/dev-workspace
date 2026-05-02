import pytest
from src.config import Config
from pathlib import Path

@pytest.fixture
def test_config(tmp_path, monkeypatch):
    root = tmp_path / "workspace"
    root.mkdir()
    # Define subdirs to avoid FileNotFoundError during Path expansion if needed
    (root / "encrypted_workspace").mkdir()
    (root / "decrypted_workspace").mkdir()
    
    monkeypatch.setenv("ROOT_WORKSPACE_DIR", str(root))
    monkeypatch.setenv("CIPHER_DIR_NAME", "encrypted_workspace")
    monkeypatch.setenv("MOUNT_DIR_NAME", "decrypted_workspace")
    
    return Config()
