# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

Mission News & Testimony Auto-Archiving System (MNAP) - 선교 소식과 간증 영상을 자동으로 수집, AI 분석(STT + LLM 요약), 아카이빙하고 텔레그램으로 공유하는 자동화 시스템.

## 개발 명령어

### 로컬 실행
```bash
# 웹 대시보드 (Streamlit) - 포트 8501
streamlit run app.py

# CLI 배치 모드 - 대화형 메뉴로 작업 선택
python main.py
```

### Docker 배포
```bash
docker-compose up --build -d    # 빌드 및 실행
docker-compose logs -f          # 로그 확인
docker-compose down             # 중지
docker exec -it evangelical_mission_bot /bin/bash  # 컨테이너 접속
```

### 테스트 및 검증
```bash
python tests/verify_system.py     # 환경 설정 검증
python tests/verify_backend.py    # 백엔드 연동 검증

# 개별 모듈 디버깅
python scripts/debug_server.py    # GPU 서버 연동
python scripts/debug_telegram.py  # 텔레그램 봇
```

### 유틸리티
```bash
python scripts/generate_hash.py   # 비밀번호 Bcrypt 해싱
python scripts/fix_filenames.py   # 파일명 일괄 수정
```

## 아키텍처

### 처리 파이프라인
```
비디오 업로드 → 파일 감지 → 메타데이터 등록 (Google Sheet)
    → FFmpeg (오디오/썸네일) → STT → LLM 요약
    → NAS 아카이빙 → 텔레그램 알림
```

### 핵심 모듈 (src/)
- `auth.py`, `user_manager.py`: Streamlit 인증, YAML 기반 사용자 관리, RBAC
- `config_loader.py`: YAML 설정 + 환경변수 오버라이드, DEV/PROD 모드 전환
- `job_manager.py`: 비동기 작업 큐, 백그라운드 처리
- `constants.py`: 공통 상수 정의 (파일 크기, 상태값, 형식 등)

### 유틸리티 (src/utils/)
- `file_validator.py`: 파일명 sanitize, 경로 traversal 방지, 크기/확장자 검증
- `input_validator.py`: 메타데이터 입력값 검증 (날짜, 이름, 국가 등)
- `date_parser.py`: 다양한 날짜 형식 파싱 및 통합 변환
- `filename_builder.py`: 시트 타입별 파일명 생성 규칙

### UI 컴포넌트 (src/components/)
- `video_uploader.py`: 드래그 앤 드롭 비디오 업로드 UI, 다중 파일 지원

### 비즈니스 로직 (src/modules/)
- `gsheet.py`: Google Sheets API 연동, 메타데이터 CRUD
- `media.py`: FFmpeg 래퍼 - 오디오 추출, 4:3 썸네일 생성
- `stt_module.py`: 외부 STT 서버 연동
- `api_client.py`: GPU 서버 LLM 요약 API
- `telegram_bot.py`: 처리 결과 알림 발송
- `nas_manager.py`: NAS 파일 아카이빙

### 데이터 디렉토리
- `data/Mission_Inbox/Testimony/`: 간증 영상 입력
- `data/Mission_Inbox/MissionNews/`: 선교 소식 입력
- `data/temp/`: 임시 파일 (오디오, 썸네일)
- `data/archive_mock/`: 개발 모드 아카이브

## 설정

### 환경 설정
```bash
cp .env.example .env
cp config/config_template.yaml config/config.yaml
```

### 필수 외부 서비스
- Google Service Account 키 (`config/readtogether-*.json`)
- GPU 서버 (LLM API)
- STT 서버 (Whisper API)
- 텔레그램 봇 토큰

### 설정 파일 (config/config.yaml)
- `environment`: DEV 또는 PROD
- `paths`: 입력/아카이브/임시 폴더 경로
- `google_sheet`: 시트 ID 및 탭 설정
- `gpu_server`, `stt_server`: API 엔드포인트 및 키
- `telegram`: 봇 토큰 및 채팅 ID
- `country_map`: 국가명 → 지역 태그 매핑

## 기술 스택

- **Python 3.10**, Streamlit (웹 UI)
- **streamlit-authenticator**, bcrypt (인증)
- **FFmpeg**, ffmpeg-python (미디어 처리)
- **gspread** (Google Sheets API)
- **Docker** (배포)

## 코드 컨벤션

### 스타일 가이드
- **PEP 8** 준수 (들여쓰기 4칸, 라인 길이 120자)
- **타입 힌트** 권장: 함수 시그니처에 타입 명시
- **Docstring**: Google 스타일 (모듈, 클래스, public 함수)

### 네이밍 규칙
- 모듈/파일: `snake_case.py`
- 클래스: `PascalCase`
- 함수/변수: `snake_case`
- 상수: `UPPER_SNAKE_CASE`

### 임포트 순서
1. 표준 라이브러리
2. 서드파티 패키지
3. 로컬 모듈 (`src.`, `src.modules.`)

### 에러 처리
- 외부 API 호출은 반드시 try-except로 감싸기
- 실패 시 로깅 후 None 반환 또는 적절한 기본값 사용
- 사용자에게 보여줄 에러는 한글로 작성

## API 엔드포인트

### GPU 서버 (LLM 요약)
- **URL**: `{gpu_server.api_url}` (config.yaml에서 설정)
- **Method**: POST
- **인증**: Bearer Token (`Authorization: Bearer {api_key}`)
- **포맷**: OpenAI Chat Completion API 호환

```json
{
  "model": "gpt-oss:120b",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "temperature": 0.7
}
```

### STT 서버 (음성인식)
| 엔드포인트 | Method | 설명 |
|-----------|--------|------|
| `/transcribe` | POST | 오디오 파일 업로드, job_id 반환 |
| `/transcribe/job/{job_id}` | GET | 작업 상태 조회 (queued/processing/completed/failed) |
| `/transcribe/job/{job_id}/result` | GET | 완료된 결과 조회 |

- **인증**: `X-API-Key` 헤더
- **폴링 간격**: 2초

### Telegram Bot
| 엔드포인트 | 용도 |
|-----------|------|
| `/sendMessage` | 마크다운 메시지 전송 |
| `/sendDocument` | 파일 첨부 전송 |

## 트러블슈팅

### Google Sheets 인증 오류
```
gspread.exceptions.APIError: 403 PERMISSION_DENIED
```
**해결:** Google Sheet에 서비스 계정 이메일(`*.iam.gserviceaccount.com`)을 편집자로 추가

### FFmpeg 오류
```
FileNotFoundError: ffmpeg not found
```
**해결:**
- macOS: `brew install ffmpeg`
- Linux: `apt install ffmpeg`
- Docker: Dockerfile에 포함됨

### STT 서버 타임아웃
**증상:** 긴 영상 처리 시 응답 없음
**해결:** `stt_module.py`의 폴링 로직이 자동 재시도함. 서버 상태 확인 필요.

### NAS 연결 실패 (PROD 모드)
**증상:** `archive` 경로 접근 불가
**해결:**
1. NAS 마운트 상태 확인: `mount | grep Archive`
2. DEV 모드로 전환하여 `archive_mock` 사용

### Streamlit 세션 만료
**증상:** 로그인 후 갑자기 로그아웃
**해결:** `config/users.yaml`의 `cookie.expiry_days` 값 확인

## 배포 체크리스트

### 배포 전 확인
- [ ] `config/config.yaml` 존재 및 `environment: PROD` 확인
- [ ] `config/readtogether-*.json` (Google 서비스 계정 키) 존재
- [ ] `config/users.yaml` (사용자 DB) 존재
- [ ] `.env` 파일 설정 완료
- [ ] NAS 볼륨 마운트 확인 (`/Volumes/Archive-Storage/Mission`)

### Docker 배포 순서
```bash
# 1. 설정 파일 확인
ls -la config/

# 2. 환경변수 확인
grep ENVIRONMENT .env  # PROD 여야 함

# 3. 빌드 및 실행
docker-compose up --build -d

# 4. 헬스체크
curl http://localhost:13002/_stcore/health

# 5. 로그 확인
docker-compose logs -f --tail=50
```

### 배포 후 확인
- [ ] 웹 대시보드 접속 (`http://서버IP:13002`)
- [ ] 로그인 동작 확인
- [ ] Google Sheet 연결 확인 (영상 목록 로드)
- [ ] 테스트 영상 처리 실행

## 기여 가이드

### 브랜치 전략
- `main`: 안정 버전 (직접 푸시 금지)
- `feature/*`: 새 기능 개발
- `fix/*`: 버그 수정
- `refactor/*`: 코드 개선

### 커밋 메시지 규칙
```
<type>(<scope>): <subject>

예시:
feat(stt): add retry logic for timeout handling
fix(gsheet): resolve duplicate entry issue
docs(readme): update deployment instructions
refactor(media): extract thumbnail logic to separate function
```

**타입:**
- `feat`: 새 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `refactor`: 코드 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드/설정 변경

### PR 작성 시
1. 변경 사항 요약
2. 테스트 방법 명시
3. 스크린샷 (UI 변경 시)

### 민감 정보 주의
- API 키, 토큰 등은 절대 커밋 금지
- `.gitignore`에 포함된 파일 확인:
  - `config/config.yaml`
  - `config/*.json`
  - `.env`

## 병렬 작업 가이드 (Multi-Terminal Claude Code)

여러 터미널에서 Claude Code를 동시에 실행하여 작업 속도를 높일 수 있습니다.
의존성 충돌을 방지하기 위해 아래 규칙을 따르세요.

### 파일 소유권 매트릭스

각 터미널 세션은 **자신이 소유한 파일만** 수정합니다. 다른 세션이 소유한 파일은 읽기만 가능합니다.

| 영역 | 담당 파일 | 의존성 |
|------|----------|--------|
| **Core** | `app.py`, `src/auth.py`, `src/config_loader.py` | 없음 (최상위) |
| **Utils** | `src/utils/*.py`, `src/constants.py` | 없음 |
| **Components** | `src/components/*.py` | Utils |
| **Modules** | `src/modules/*.py` | Utils, Constants |
| **Services** | `src/services/*.py` | Modules, Utils |
| **Pages** | `src/pages/*.py` | Components, Modules |
| **Tests** | `tests/*.py` | 모든 모듈 (읽기 전용) |
| **Docs** | `*.md`, `docs/` | 없음 |

### 병렬 작업 분배 예시

```
터미널 1 (Core/App)     터미널 2 (Utils)        터미널 3 (Modules)      터미널 4 (Tests/Docs)
─────────────────────   ─────────────────────   ─────────────────────   ─────────────────────
app.py 수정             file_validator.py       gsheet.py 수정          tests/ 작성
auth.py 수정            input_validator.py      media.py 수정           CLAUDE.md 업데이트
config_loader.py        date_parser.py          stt_module.py           README.md
                        filename_builder.py     api_client.py
```

### 충돌 방지 규칙

1. **락 파일 사용**: 작업 시작 시 `.claude_lock_<영역>` 파일 생성
   ```bash
   touch .claude_lock_utils  # Utils 영역 작업 시작
   rm .claude_lock_utils     # 작업 완료 후 삭제
   ```

2. **Import 추가 금지**: 다른 세션이 담당하는 모듈에 새 import를 추가하지 않음

3. **인터페이스 변경 시 알림**: 함수 시그니처 변경 시 다른 세션에 알림 필요
   ```bash
   echo "validate_upload() 반환값 변경: Tuple[bool, str] → Tuple[bool, str, Optional[str]]" >> .claude_changes.log
   ```

4. **Git 브랜치 분리**: 대규모 변경 시 각 세션별 브랜치 사용
   ```bash
   git checkout -b refactor/utils-session
   git checkout -b refactor/modules-session
   ```

### 현재 작업 상태 추적

작업 진행 상황을 `.claude_status.md`에 기록:
```markdown
## 진행 상태 (2025-01-15)
- [x] Phase 1: 동영상 업로드 기능 (완료)
- [x] Phase 2: 보안 강화 (완료)
- [x] Phase 3: 입력값 검증 (완료)
- [x] Phase 4: 공통 유틸리티 (완료)
- [ ] Phase 5: app.py 분리 (진행 중 - 터미널 1)
- [ ] Phase 6: 통합 테스트 (대기 - 터미널 4)
```

### 남은 리팩토링 작업

#### 터미널 1에서 진행 가능
- `src/pages/registration.py` 생성 (app.py Tab1 분리)
- `src/pages/processing.py` 생성 (app.py Tab2 분리)
- `src/pages/admin.py` 생성 (app.py Tab3 분리)

#### 터미널 2에서 진행 가능
- `src/utils/rate_limiter.py` 생성
- 기존 모듈에 유틸리티 함수 적용

#### 터미널 3에서 진행 가능
- `src/modules/gsheet.py`에 date_parser 적용
- `src/services/job_processor.py`에 filename_builder 적용

#### 터미널 4에서 진행 가능
- `tests/test_validators.py` 작성
- `tests/test_uploaders.py` 작성
- 문서 업데이트
