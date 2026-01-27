import requests
import json
import os
from src.config_loader import settings

class APIClient:
    """
    GPU 서버(Ollama/Local LLM)와 통신하는 클라이언트 모듈입니다.
    오디오 파일(현재는 텍스트 프롬프트 시뮬레이션)을 전송하여 요약을 받아옵니다.
    """
    def __init__(self):
        self.config = settings.gpu_config
        self.base_url = self.config.get('api_url') # 예: http://aiteam.tplinkdns.com:10001/ollama/v1
        self.base_url = self.config.get('api_url') # 예: http://aiteam.tplinkdns.com:10001/ollama/v1
        self.api_key = self.config.get('api_key')
        self.model = self.config.get('model', 'gpt-oss:120b').strip() # 공백 제거 안전장치

    def analyze_text(self, input_text, prompt_type="testimony"):
        """
        [2단계: LLM] 변환된 텍스트(input_text)를 받아 요약문을 반환합니다.
        """
        
        # 현재 API 주소는 'ollama/v1' --> OpenAI Chat Completion API 규격일 가능성이 높습니다.
        # Chat Completion 엔드포인트 구성
        if self.base_url.endswith("/chat/completions"):
            url = self.base_url
        else:
            url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 프롬프트 설정 (Config에서 로드)
        prompts_config = self.config.get('prompts', {})
        # Fallback to default if not in config
        if not prompts_config:
            # Config에 없는 경우를 대비한 하드코딩 기본값 (안전장치)
            prompts_config = settings.config.get('prompts', {})
        
        # prompt_type에 맞는 설정 가져오기 (testimony / mission_news)
        target_prompt = prompts_config.get(prompt_type, {})
        
        system_instruction = ""
        
        # 파일 매핑: prompt_type -> filename
        prompt_files = {
            "testimony": "System_Prompt_Testimony.md",
            "mission_news": "System_Prompt_Mission.md"
        }
        
        target_file = prompt_files.get(prompt_type)
        
        # 1. 파일에서 로드 시도
        if target_file:
            try:
                # 프로젝트 루트 경로 계산 (현재 파일 위치 기준)
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(current_dir))
                prompt_path = os.path.join(project_root, "docs", target_file)
                
                if os.path.exists(prompt_path):
                    with open(prompt_path, "r", encoding="utf-8") as f:
                        system_instruction = f.read()
                    print(f"[API] 시스템 프롬프트 로드 완료: {prompt_path}")
            except Exception as e:
                print(f"[API] ⚠️ 시스템 프롬프트 파일 로드 실패 ({target_file}): {e}")

        # 2. 파일 로드 실패하거나 파일 매핑이 없는 경우 Config 사용
        if not system_instruction:
            system_instruction = target_prompt.get('system', "당신은 선교 소식을 요약하는 AI입니다.")
            
        user_msg = target_prompt.get('user', "내용을 요약해주세요.")

        # 텍스트가 너무 길면 잘라야 할 수도 있음 (Token Limit)
        # 1시간 분량(약 2~3만자)을 충분히 커버하기 위해 40,000자로 상향
        safe_text = input_text[:40000] 

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"{user_msg}\n\n[원문 내용]: {safe_text}"}
            ],
            "temperature": 0.7
        }

        print(f"[API] 요청 전송: {url} (Text Length: {len(safe_text)})")
        
        try:
            # 타임아웃 설정: (Connect Timeout, Read Timeout)
            # Connect: 10초 내에 서버 연결 안되면 즉시 에러 (서버 꺼짐 판별)
            # Read: 30분(1800초) 내에 응답 없으면 에러 (모델 처리 지연)
            TIMEOUT_CONFIG = (10, 1800)
            
            # 실제 요청 전송
            response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT_CONFIG)
            
            if response.status_code == 200:
                result = response.json()
                # OpenAI 포맷 응답 파싱
                content = result['choices'][0]['message']['content']
                return content
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                print(error_msg)
                return f"[단순 요약] 서버 통신 실패. (Status: {response.status_code} - 내부 에러)"

        except requests.exceptions.ConnectTimeout:
             print(f"[API] ❌ 서버 연결 실패 (Connect Timeout)")
             return f"[에러] 서버가 꺼져있거나 응답하지 않습니다. (Connect Timeout)"

        except requests.exceptions.ReadTimeout:
            print(f"[API] ⏳ 모델 처리 시간 초과 (1800s)")
            return f"[에러] AI 모델 처리 시간이 초과되었습니다. (Read Timeout)"
            
        except requests.exceptions.ConnectionError:
            print(f"[API] ❌ 연결 거부됨 (Connection Error)")
            return f"[에러] 서버 연결이 거부되었습니다. (서버 다운 추정)"

        except Exception as e:
            print(f"[API] ⚠️ 통신 중 예외 발생: {str(e)}")
            return f"[에러] 통신 오류: {str(e)}"
