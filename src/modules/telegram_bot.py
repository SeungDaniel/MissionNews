import requests
from src.config_loader import settings
import os

class TelegramBot:
    def __init__(self):
        self.config = settings.config.get('telegram', {})
        self.token = self.config.get('bot_token')
        self.chat_id = self.config.get('chat_id')
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, text):
        """
        Send a message to the configured chat_id.
        """
        if not self.token:
            print("⚠️ Telegram Token missing.")
            return
        
        if not self.chat_id:
            print("⚠️ Telegram Chat ID missing. Please check get_updates() to find your ID.")
            return

        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown" # Optional
        }
        
        try:
            res = requests.post(url, json=payload, timeout=10)
            if res.status_code == 200:
                print("     ㄴ 텔레그램 전송 완료")
            else:
                print(f"     ⚠️ 텔레그램 전송 실패: {res.text}")
        except Exception as e:
            print(f"     ⚠️ 텔레그램 통신 에러: {e}")
    def send_document(self, file_path):
        """
        Send a document (file) to the configured chat_id.
        """
        if not self.token or not self.chat_id:
            return

        url = f"{self.base_url}/sendDocument"
        
        try:
            with open(file_path, 'rb') as f:
                files = {'document': f}
                data = {'chat_id': self.chat_id}
                res = requests.post(url, data=data, files=files, timeout=30)
                
            if res.status_code == 200:
                print(f"     ㄴ 텔레그램 파일 전송 완료: {os.path.basename(file_path)}")
            else:
                print(f"     ⚠️ 텔레그램 파일 전송 실패: {res.text}")
        except Exception as e:
            print(f"     ⚠️ 텔레그램 파일 전송 에러: {e}")
    def get_updates(self):
        """
        Fetches recent updates to help user find their Chat ID.
        """
        if not self.token:
            return "Error: No Token"
            
        url = f"{self.base_url}/getUpdates"
        try:
            res = requests.get(url, timeout=10)
            return res.json()
        except Exception as e:
            return str(e)
