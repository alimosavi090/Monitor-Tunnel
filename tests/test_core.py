import pytest
from tunnelbench.core.config import Config
from tunnelbench.core.exceptions import TunnelBenchError, ConfigurationError
import tempfile
import os

def test_exception_hierarchy():
    assert issubclass(ConfigurationError, TunnelBenchError)

def test_config_load_success():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
        f.write("servers:\n  - name: TestServer\n    host: 1.2.3.4\n")
        temp_path = f.name
        
    try:
        cfg = Config(config_path=temp_path)
        cfg.load()
        servers = cfg.get("servers")
        assert len(servers) == 1
        assert servers[0]["name"] == "TestServer"
    finally:
        os.unlink(temp_path)

def test_config_load_file_not_found():
    cfg = Config(config_path="/does/not/exist.yaml")
    with pytest.raises(ConfigurationError):
        cfg.load()
