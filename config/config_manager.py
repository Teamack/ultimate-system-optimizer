"""Configuration manager for Ultimate System Optimizer."""

import json
import os
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    """Manages application configuration with safe defaults."""

    DEFAULT_CONFIG = {
        # Cleanup settings
        'cleanup_temp_files': True,
        'memory_cleanup': True,
        'optimize_registry': True,  # Windows only
        'cleanup_downloads': False,  # Safer to leave off by default
        'temp_file_age_days': 7,  # Only delete files older than 7 days

        # Monitoring settings
        'monitoring_interval': 2.0,  # seconds
        'enable_graphs': True,
        'graph_history_points': 60,

        # Optimization settings
        'deep_clean': False,
        'create_backup': True,
        'auto_optimize': False,
        'auto_optimize_schedule': '02:00',  # 2 AM by default

        # Context-aware settings
        'enable_context_aware': True,
        'gaming_mode_enabled': True,
        'work_mode_enabled': True,

        # Privacy settings
        'send_analytics': False,
        'local_processing_only': True,

        # Performance settings
        'max_cpu_usage': 80,  # Don't let optimizer use more than this
        'priority_mode': 'balanced',  # balanced, performance, efficiency
    }

    def __init__(self, config_path: str = None):
        """Initialize configuration manager.

        Args:
            config_path: Path to config file. If None, uses default location.
        """
        if config_path is None:
            # Use user's home directory
            home = Path.home()
            self.config_dir = home / '.ultimate_system_optimizer'
            self.config_dir.mkdir(exist_ok=True)
            self.config_path = self.config_dir / 'config.json'
        else:
            self.config_path = Path(config_path)
            self.config_dir = self.config_path.parent

        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)

                # Merge with defaults (in case new settings were added)
                config = self.DEFAULT_CONFIG.copy()
                config.update(loaded_config)
                return config
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            config = self.DEFAULT_CONFIG.copy()
            self.save_config()
            return config

    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key doesn't exist

        Returns:
            Configuration value
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value and save.

        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
        self.save_config()

    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
