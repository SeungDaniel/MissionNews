import yaml
import os
import sys

class ConfigLoader:
    def __init__(self, config_path="config/config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            print(f"Error: Config file not found at {self.config_path}")
            sys.exit(1)
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"Error parsing config file: {e}")
                sys.exit(1)

    @property
    def env(self):
        return self.config.get('environment', 'DEV').upper()

    @property
    def paths(self):
        # Select paths based on environment
        env_key = self.env.lower()
        if env_key not in self.config['paths']:
            print(f"Warning: Environment '{self.env}' not defined in paths. Defaulting to 'dev'.")
            env_key = 'dev'
        return self.config['paths'][env_key]

    @property
    def gsheet_config(self):
        return self.config.get('google_sheet', {})

    @property
    def gpu_config(self):
        return self.config.get('gpu_server', {})

    @property
    def youtube_config(self):
        return self.config.get('youtube', {})

    def save_config(self, new_config):
        """Save the updated configuration to the YAML file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(new_config, f, allow_unicode=True, default_flow_style=False)
            self.config = new_config # Update in-memory
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

# Global instance for easy import
# Usage: from src.config_loader import settings
try:
    settings = ConfigLoader()
except Exception as e:
    settings = None
    print(f"Failed to initialize settings: {e}")
