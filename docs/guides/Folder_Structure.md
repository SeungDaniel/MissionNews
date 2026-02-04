# 📂 Project Folder Structure & File Roles
# 프로젝트 폴더 구조 및 파일 역할 정의

The following structure is designed for modularity and scalability.
모듈화와 확장성을 고려하여 설계된 폴더 구조입니다.

```
MissionNews/
├── app.py                    # Streamlit 웹 대시보드 (메인 UI)
├── main.py                   # CLI 배치 모드 엔트리포인트
├── requirements.txt          # Python 의존성
├── Dockerfile               # Docker 빌드 설정
├── docker-compose.yaml      # Docker Compose 설정
├── .env                     # 환경변수 (Git 제외)
├── CLAUDE.md                # Claude Code 가이드
│
├── .streamlit/
│   └── config.toml          # Streamlit 설정 (업로드 크기 등)
│
├── config/
│   ├── config.yaml          # 전역 설정 (Git 제외)
│   ├── users.yaml           # 사용자 DB
│   └── *.json               # Google 서비스 계정 키 (Git 제외)
│
├── src/
│   ├── auth.py              # 인증 (Streamlit Authenticator)
│   ├── user_manager.py      # 사용자 CRUD
│   ├── config_loader.py     # 설정 로더 (YAML + 환경변수)
│   ├── job_manager.py       # 비동기 작업 큐
│   ├── logger.py            # 로깅 유틸리티
│   ├── constants.py         # 공통 상수 정의
│   │
│   ├── utils/               # 유틸리티 모듈
│   │   ├── file_validator.py    # 파일 검증, Path Traversal 방지
│   │   ├── input_validator.py   # 입력값 검증
│   │   ├── date_parser.py       # 날짜 파싱/변환
│   │   └── filename_builder.py  # 파일명 생성 규칙
│   │
│   ├── components/          # UI 컴포넌트
│   │   └── video_uploader.py    # 드래그앤드롭 업로더
│   │
│   ├── modules/             # 비즈니스 로직
│   │   ├── gsheet.py            # Google Sheets API
│   │   ├── media.py             # FFmpeg 래퍼
│   │   ├── stt_module.py        # STT 서버 연동
│   │   ├── api_client.py        # GPU LLM 서버 연동
│   │   ├── nas_manager.py       # NAS 파일 아카이빙
│   │   ├── telegram_bot.py      # 텔레그램 알림
│   │   └── youtube.py           # YouTube 업로드
│   │
│   ├── services/            # 서비스 레이어
│   │   └── job_processor.py     # 작업 처리 파이프라인
│   │
│   └── pages/               # (예정) Streamlit 페이지 분리
│       ├── registration.py      # Tab1: 신규 파일 등록
│       ├── processing.py        # Tab2: 작업 처리
│       └── admin.py             # Tab3: 시스템 관리
│
├── data/                    # 데이터 디렉토리 (Git 제외)
│   ├── Mission_Inbox/
│   │   ├── Testimony/           # 간증 영상 입력
│   │   └── MissionNews/         # 선교 소식 입력
│   ├── temp/                    # 임시 파일
│   └── archive_mock/            # DEV 모드 아카이브
│
├── tests/                   # 테스트
│   ├── verify_system.py         # 환경 검증
│   └── verify_backend.py        # 백엔드 연동 검증
│
├── scripts/                 # 유틸리티 스크립트
│   ├── generate_hash.py         # 비밀번호 해시 생성
│   ├── fix_filenames.py         # 파일명 일괄 수정
│   └── debug_*.py               # 디버깅 스크립트
│
├── docs/                    # 문서
│   ├── guides/                  # 가이드 문서
│   ├── prompts/                 # LLM 프롬프트 템플릿
│   └── legacy/                  # 레거시 문서
│
└── logs/                    # 로그 파일
```

---

## 1. Root Directory (루트 디렉토리)

*   **`app.py`**:
    *   **Role**: Streamlit web dashboard. Main UI for video registration and processing.
    *   **역할**: Streamlit 웹 대시보드. 영상 등록 및 처리를 위한 메인 UI.
*   **`main.py`**:
    *   **Role**: CLI batch mode entry point.
    *   **역할**: CLI 배치 모드 엔트리포인트.
*   **`requirements.txt`**:
    *   **Role**: List of Python dependencies (e.g., `gspread`, `ffmpeg-python`, `streamlit`).
    *   **역할**: 필요한 파이썬 라이브러리 목록.

## 2. `config/` (Settings)

*   **`config.yaml`**:
    *   **Role**: Global settings. Contains paths (Dev/Prod), API endpoints, and country mapping.
    *   **역할**: 전체 설정. 경로 설정(개발/운영), API 엔드포인트, 국가 매핑 등을 담습니다.
*   **`users.yaml`**:
    *   **Role**: User database for authentication.
    *   **역할**: 인증용 사용자 데이터베이스.
*   **`*.json`** (Ignored by Git):
    *   **Role**: Google Service Account keys.
    *   **역할**: Google 서비스 계정 키.

## 3. `src/` (Source Code)

### 3.1 Core Modules (핵심 모듈)
*   **`auth.py`**: Streamlit 인증 및 쿠키 관리
*   **`user_manager.py`**: 사용자 CRUD 및 권한 관리
*   **`config_loader.py`**: YAML 설정 + 환경변수 오버라이드
*   **`job_manager.py`**: 비동기 작업 큐 관리
*   **`constants.py`**: 공통 상수 (파일 크기, 상태값 등)

### 3.2 `src/utils/` (유틸리티)
*   **`file_validator.py`**: 파일명 sanitize, Path Traversal 방지, 크기/확장자 검증
*   **`input_validator.py`**: 메타데이터 입력값 검증 (날짜, 이름, 국가)
*   **`date_parser.py`**: 다양한 날짜 형식 파싱 및 변환
*   **`filename_builder.py`**: 시트 타입별 파일명 생성 규칙

### 3.3 `src/components/` (UI 컴포넌트)
*   **`video_uploader.py`**: 드래그앤드롭 비디오 업로더 (다중 파일 지원)

### 3.4 `src/modules/` (비즈니스 로직)
*   **`gsheet.py`**: Google Sheets API 연동, 메타데이터 CRUD
*   **`media.py`**: FFmpeg 래퍼 - 오디오 추출, 썸네일 생성
*   **`stt_module.py`**: 외부 STT 서버 연동
*   **`api_client.py`**: GPU LLM 서버 요약 API
*   **`nas_manager.py`**: NAS 파일 아카이빙
*   **`telegram_bot.py`**: 처리 결과 알림 발송
*   **`youtube.py`**: YouTube 업로드 API

### 3.5 `src/services/` (서비스 레이어)
*   **`job_processor.py`**: 작업 처리 파이프라인 (STT → LLM → Archive → Telegram)

## 4. `data/` (Local Storage)

*   **`Mission_Inbox/`** (Git Ignore):
    *   **Role**: Input folder for uploaded videos.
    *   **역할**: 업로드된 영상이 위치하는 입력 폴더.
*   **`temp/`**:
    *   **Role**: Temporary storage for audio files and thumbnails.
    *   **역할**: 오디오 파일 및 썸네일 임시 저장소.
*   **`archive_mock/`**:
    *   **Role**: DEV mode archive (simulates NAS).
    *   **역할**: 개발 모드용 아카이브 (NAS 시뮬레이션).
