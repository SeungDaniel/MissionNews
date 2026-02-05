import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Ensure logs directory exists
# Ensure logs directory exists
LOG_DIR = os.getenv("MNAP_LOG_DIR", "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

APP_LOG_FILE = os.path.join(LOG_DIR, "app.log")

def get_logger(name="mnap_logger"):
    """
    Returns a logger instance that writes to both file and console.
    """
    logger = logging.getLogger(name)
    
    # If logger already has handlers, assume it's configured to avoid duplicate logs
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. File Handler (Rotating)
    # Max size 10MB, keep 5 backups
    file_handler = RotatingFileHandler(APP_LOG_FILE, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 2. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Helper to read logs for UI
def read_logs(lines=100):
    if not os.path.exists(APP_LOG_FILE):
        return ["Log file does not exist yet."]
    
    try:
        with open(APP_LOG_FILE, "r", encoding="utf-8") as f:
            # Efficiently read last N lines is harder in plain python without reading all, 
            # but for <10MB files, reading all is fine for now or use deque.
            all_lines = f.readlines()
            return all_lines[-lines:]
    except Exception as e:
        return [f"Error reading logs: {e}"]
