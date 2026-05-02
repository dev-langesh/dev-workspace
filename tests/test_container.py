import os
from pathlib import Path
from src.container import ContainerManager
from src.config import Config

def test_generate_compose(tmp_path, monkeypatch):
    # Setup mock environment
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ROOT_WORKSPACE_DIR", str(tmp_path / "work"))
    
    config = Config()
    manager = ContainerManager(config)
    
    manager.generate_compose()
    
    compose_path = tmp_path / "docker-compose.yml"
    assert compose_path.exists()
    content = compose_path.read_text()
    assert config.container_name in content
    assert str(config.ssh_port) in content

def test_image_exists_check(mocker, test_config):
    manager = ContainerManager(test_config)
    
    # Mock successful inspect
    mocker.patch("subprocess.run", return_value=mocker.Mock(returncode=0))
    assert manager.image_exists("some-image") is True
    
    # Mock failed inspect
    mocker.patch("subprocess.run", return_value=mocker.Mock(returncode=1))
    assert manager.image_exists("non-existent") is False

def test_image_exists_exception(mocker, test_config):
    manager = ContainerManager(test_config)
    # Mock subprocess.run to raise a generic Exception
    mocker.patch("subprocess.run", side_effect=Exception("Docker error"))
    assert manager.image_exists("any-image") is False


def test_container_lifecycle_commands(mocker, test_config):
    manager = ContainerManager(test_config)
    mock_run = mocker.patch("subprocess.run")
    
    manager.up()
    assert "up" in mock_run.call_args_list[0][0][0]
    
    manager.down()
    assert "down" in mock_run.call_args_list[1][0][0]
    
    manager.remove_image()
    assert "rmi" in mock_run.call_args_list[2][0][0]

def test_container_error_cases(mocker, test_config):
    manager = ContainerManager(test_config)
    # Mock subprocess.run to raise CalledProcessError
    import subprocess
    mocker.patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "cmd"))
    
    # We need to mock Logger.error to prevent sys.exit in some cases
    # but container.py's up() calls Logger.error which exits.
    # So we mock sys.exit.
    mocker.patch("sys.exit")
    
    assert manager.up() is False
    assert manager.down() is False
    # remove_image doesn't return anything but we check it doesn't crash
    manager.remove_image()

def test_pull_image(mocker, test_config):
    manager = ContainerManager(test_config)
    mock_run = mocker.patch("subprocess.run")
    
    # Success
    mock_run.returncode = 0
    assert manager.pull_image("ubuntu:24.04") is True
    
    # Fail
    import subprocess
    mock_run.side_effect = subprocess.CalledProcessError(1, "docker pull")
    assert manager.pull_image("invalid-image") is False

