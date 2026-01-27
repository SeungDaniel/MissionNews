import requests
import time
import sys
import os

# 현재 디렉토리를 경로에 추가하여 config 로드
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.config_loader import settings

def test_server_connection():
    config = settings.gpu_config
    base_url = config.get('api_url')
    api_key = config.get('api_key')
    model = config.get('model', 'gpt-oss:120b')

    print("="*50)
    print(f"📡 GPU 서버 연결 테스트")
    print(f"   URL: {base_url}")
    print(f"   Model: {model}")
    print("="*50)

    # 1. Ping / Health Check (if available) or Simple Chat
    # Chat Completion 엔드포인트 구성
    if base_url.endswith("/chat/completions"):
        url = base_url
    else:
        url = f"{base_url}/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 간단한 테스트 메시지
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Hello! Are you alive? Reply in one word."}
        ],
        "temperature": 0.7
    }

    print("\n[1] 테스트 요청 보내는 중... (Timeout: 10s)")
    start_time = time.time()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        elapsed = time.time() - start_time
        
        print(f"   ⏱️  소요 시간: {elapsed:.2f}초")
        print(f"   📦 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"   ✅ 응답 성공: {content}")
        else:
            print(f"   ❌ 응답 실패: {response.text}")

    except requests.exceptions.Timeout:
        print("   ❌ 타임아웃! (10초 내 응답 없음 -> 서버 부하 심함 or 다운)")
    except requests.exceptions.ConnectionError:
        print("   ❌ 연결 실패! (서버 주소 틀림 or 꺼짐)")
    except Exception as e:
        print(f"   ❌ 에러 발생: {e}")

if __name__ == "__main__":
    test_server_connection()
