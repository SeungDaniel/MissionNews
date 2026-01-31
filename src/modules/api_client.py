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
        
        
        # [수정] 프롬프트 로드 로직 강화 (Retry + No Fallback)
        import time
        max_retries = 3
        
        target_file = prompt_files.get(prompt_type)
        if not target_file:
             # 파일 매핑 자체가 없는 경우 (치명적)
             raise ValueError(f"지원되지 않는 prompt_type 입니다: {prompt_type}")

        # 프로젝트 루트 경로 계산
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        prompt_path = os.path.join(project_root, "docs", "prompts", target_file)

        for attempt in range(max_retries):
            try:
                if os.path.exists(prompt_path):
                    with open(prompt_path, "r", encoding="utf-8") as f:
                        system_instruction = f.read()
                    print(f"[API] 시스템 프롬프트 로드 완료: {prompt_path}")
                    break # 성공 시 루프 탈출
                else:
                    raise FileNotFoundError(f"프롬프트 파일 없음: {prompt_path}")
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"[API] ⚠️ 프롬프트 로드 실패 (재시도 {attempt+1}/{max_retries}): {e}")
                    time.sleep(0.5)
                else:
                    # 최종 실패 시 에러 발생 (작업 중단 -> 미완료 상태 유지)
                    print(f"[API] ❌ 시스템 프롬프트 로드 최종 실패. 작업을 중단합니다.")
                    raise RuntimeError(f"시스템 프롬프트 파일 로드 실패: {target_file}")
        
        # [수정] Config의 'user' 프롬프트가 System Prompt와 충돌하는 문제를 방지하기 위해 
        # Config 값을 무시하고, 중립적인 지시문을 사용합니다.
        user_msg = "위 System Prompt의 지침에 따라, 아래 [원문 내용]을 분석 및 처리하여 지정된 포맷으로 출력해주세요."

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
