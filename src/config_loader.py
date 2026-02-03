import yaml
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ConfigLoader:
    def __init__(self, config_path="config/config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self._override_with_env()

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

    def _override_with_env(self):
        """Override configuration with environment variables."""
        # Environment
        if os.getenv('ENVIRONMENT'):
            self.config['environment'] = os.getenv('ENVIRONMENT')
        
        # Google Sheet - Json Key Path
        if os.getenv('GOOGLE_SHEET_JSON_KEY_PATH'):
            if 'google_sheet' not in self.config: self.config['google_sheet'] = {}
            self.config['google_sheet']['json_key_path'] = os.getenv('GOOGLE_SHEET_JSON_KEY_PATH')

        # Google Sheet - IDs
        if os.getenv('GOOGLE_SHEET_ID_TESTIMONY') or os.getenv('GOOGLE_SHEET_ID_MISSION_NEWS'):
            if 'ids' not in self.config.get('google_sheet', {}):
                if 'google_sheet' not in self.config: self.config['google_sheet'] = {}
                self.config['google_sheet']['ids'] = {}
            
            if os.getenv('GOOGLE_SHEET_ID_TESTIMONY'):
                self.config['google_sheet']['ids']['testimony'] = os.getenv('GOOGLE_SHEET_ID_TESTIMONY')
            if os.getenv('GOOGLE_SHEET_ID_MISSION_NEWS'):
                self.config['google_sheet']['ids']['mission_news'] = os.getenv('GOOGLE_SHEET_ID_MISSION_NEWS')

        # GPU Server
        if os.getenv('GPU_API_KEY'):
            if 'gpu_server' not in self.config: self.config['gpu_server'] = {}
            self.config['gpu_server']['api_key'] = os.getenv('GPU_API_KEY')
            if os.getenv('GPU_API_URL'):
                self.config['gpu_server']['api_url'] = os.getenv('GPU_API_URL')
            if os.getenv('GPU_MODEL'):
                self.config['gpu_server']['model'] = os.getenv('GPU_MODEL')

        # STT Server
        if os.getenv('STT_API_KEY'):
            if 'stt_server' not in self.config: self.config['stt_server'] = {}
            self.config['stt_server']['api_key'] = os.getenv('STT_API_KEY')
            if os.getenv('STT_API_URL'):
                self.config['stt_server']['api_url'] = os.getenv('STT_API_URL')

        # Telegram
        if os.getenv('TELEGRAM_BOT_TOKEN'):
            if 'telegram' not in self.config: self.config['telegram'] = {}
            self.config['telegram']['bot_token'] = os.getenv('TELEGRAM_BOT_TOKEN')
            if os.getenv('TELEGRAM_CHAT_ID'):
                self.config['telegram']['chat_id'] = os.getenv('TELEGRAM_CHAT_ID')

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
    
    @property
    def stt_config(self):
        return self.config.get('stt_server', {})

    @property
    def telegram_config(self):
        return self.config.get('telegram', {})

    def save_config(self, new_config):
        """Save the updated configuration to the YAML file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(new_config, f, allow_unicode=True, default_flow_style=False)
            self.config = new_config # Update in-memory
            # Re-apply env vars to ensure they still take precedence in memory
            self._override_with_env()
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
