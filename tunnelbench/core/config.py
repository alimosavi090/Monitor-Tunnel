"""
Configuration management.
"""
import yaml
from pathlib import Path
from typing import Any, Dict
from tunnelbench.core.exceptions import ConfigurationError

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.settings: Dict[str, Any] = {}
        
    def load(self) -> None:
        """Load the YAML configuration file."""
        if not self.config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {self.config_path}")
            
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data is None:
                    data = {}
                self.settings = data
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Failed to parse YAML configuration: {e}")
        except Exception as e:
            raise ConfigurationError(f"Unexpected error loading config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        return self.settings.get(key, default)
