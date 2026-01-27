from src.modules.telegram_bot import TelegramBot
import sys
import os

sys.path.append(os.getcwd())

def test_telegram():
    print("Testing Telegram Bot...")
    bot = TelegramBot()
    print(f"Token: {bot.token[:5]}..." if bot.token else "Token: None")
    print(f"Chat ID: {bot.chat_id}")
    
    bot.send_message("🔔 [Test] Telegram Connectivity Check from MNAP System.")

if __name__ == "__main__":
    test_telegram()
