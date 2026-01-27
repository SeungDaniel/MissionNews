import os
import requests
import time
from src.config_loader import settings

class ServerSTT:
    def __init__(self):
        self.config = settings.config.get('stt_server', {})
        self.base_url = self.config.get('api_url')
        self.api_key = self.config.get('api_key')
        
        if not self.base_url or not self.api_key:
            print("❌ STT 설정(URL/Key)이 누락되었습니다. config.yaml을 확인해주세요.")
    
    def transcribe(self, audio_path):
        """
        Transcribe audio using the server API.
        1. Upload -> Job ID
        2. Poll Status -> Completed
        3. Get Result -> Text
        """
        if not os.path.exists(audio_path):
            return "Error: Audio file not found."

        if not self.base_url:
            return "Error: STT Server Configuration Missing."

        print(f"[STT] 서버로 변환 요청 중... ({os.path.basename(audio_path)})")
        
        # 1. File Upload
        upload_url = f"{self.base_url}/transcribe"
        headers = {"X-API-Key": self.api_key}
        
        try:
            with open(audio_path, 'rb') as f:
                files = {'file': f}
                # Optional: Add language='ko' if known, but auto-detect is default
                response = requests.post(upload_url, headers=headers, files=files)
                
            if response.status_code != 200:
                print(f"❌ Upload Failed: {response.status_code} - {response.text}")
                return f"Error: Upload Failed ({response.status_code})"
                
            job_data = response.json()
            job_id = job_data.get('job_id')
            print(f"     ㄴ Job ID 발급: {job_id} (대기열: {job_data.get('queue_position')}번째)")
            
            # 2. Polling
            status_url = f"{self.base_url}/transcribe/job/{job_id}"
            
            while True:
                time.sleep(2) # 2초 간격 확인
                res = requests.get(status_url, headers=headers)
                state_data = res.json()
                status = state_data.get('status')
                
                if status == 'completed':
                    print("     ㄴ 변환 완료!")
                    break
                elif status == 'failed':
                    err = state_data.get('error')
                    print(f"❌ 변환 실패: {err}")
                    return f"Error: Transcription Failed ({err})"
                else:
                    # queued or processing
                    print(f"     ... {status} ing", end='\r')
            
            # 3. Get Result
            result_url = f"{self.base_url}/transcribe/job/{job_id}/result"
            res = requests.get(result_url, headers=headers)
            final_data = res.json()
            
            # Return full data (text + segments) for SRT generation
            return final_data

        except Exception as e:
            print(f"❌ STT Exception: {e}")
            return f"Error: {str(e)}"

# 테스트용 코드
if __name__ == "__main__":
    stt = ServerSTT()
    # print(stt.transcribe("data/temp/test.mp3"))
