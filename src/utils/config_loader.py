"""
Configuration Loader with Environment Variable Support

Safely loads YAML configuration files while substituting environment variables.
Ensures API keys are loaded from environment, not hardcoded in config files.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load YAML configuration file with environment variable substitution.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Configuration dictionary with environment variables resolved
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If required environment variables are missing
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Resolve environment variables
    config = _resolve_env_vars(config)
    
    # Validate required API key is present (only if this config actually has an API key)
    if 'api_key' in config:
        _validate_api_key(config)
    
    return config


def _resolve_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively resolve environment variables in configuration.
    
    Looks for 'api_key_env' keys and replaces with actual environment values.
    """
    if isinstance(config, dict):
        # Create a copy to avoid modifying dict during iteration
        config_copy = config.copy()
        for key, value in config_copy.items():
            if key == 'api_key_env' and isinstance(value, str):
                # Replace with actual environment variable value
                env_value = os.getenv(value)
                if env_value is None:
                    raise ValueError(
                        f"Environment variable '{value}' not found. "
                        f"Please set it in your .env file or environment."
                    )
                config['api_key'] = env_value
            elif isinstance(value, dict):
                config[key] = _resolve_env_vars(value)
    
    return config


def _validate_api_key(config: Dict[str, Any]) -> None:
    """
    Validate that API key is properly configured.
    """
    if 'api_key' not in config:
        raise ValueError(
            "API key not found in configuration. "
            "Please ensure your environment variables are set correctly."
        )
    
    if not config['api_key'] or config['api_key'].startswith('your_'):
        raise ValueError(
            "API key appears to be a placeholder. "
            "Please set your actual API key in the .env file."
        )


def load_env_file(env_path: str = ".env") -> None:
    """
    Load environment variables from .env file.
    
    Args:
        env_path: Path to .env file (default: .env in current directory)
    """
    env_file = Path(env_path)
    if not env_file.exists():
        print(f"No .env file found at {env_path}")
        print("Create one by copying .env.example and adding your API keys")
        return
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Only set if not already in environment (allows override)
                if key not in os.environ:
                    os.environ[key] = value 