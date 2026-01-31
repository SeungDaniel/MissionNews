# 🚀 Refactoring Execution Plan (리팩토링 실행 계획)
> **Goal**: Transition from a Local-Only script to a Server-Deployable Web Application.
> **목표**: 개인 PC용 스크립트 구조에서, 서버 배포 및 웹 업로드가 가능한 웹 애플리케이션 구조로 전환.

---

## 📅 Phase 1: Web Upload Feature (웹 업로드 기능 구현)

**Current Problem (현재 문제점):**
- Users must manually copy files to the server's local `Inbox` folder via Finder/SMB.
- 사용자가 직접 서버의 로컬 폴더(`Inbox`)에 파일 탐색기를 통해 파일을 복사해 넣어야 함.

**Action Items (실행 항목):**
1.  **UI Update (`app.py`)**:
    - Add `st.file_uploader` widget to the "Register New Video" tab.
    - "신규 영상 등록" 탭에 드래그 앤 드롭이 가능한 파일 업로더 위젯 추가.
2.  **Backend Logic (`media.py` / `app.py`)**:
    - Implement a handler to save uploaded binary streams to the server's `Mission_Inbox` directory.
    - 업로드된 바이너리 스트림을 서버의 실제 `Inbox` 폴더에 물리적 파일로 저장하는 핸들러 구현.
3.  **Auto-Registration (자동 등록 연동)**:
    - Automatically pre-fill metadata fields based on the uploaded filename.
    - 업로드된 파일명을 분석하여 메타데이터(날짜, 국가 등) 자동 입력 기능 연동.

---

## 🛠 Phase 2: Server Deployment Optimization (서버 배포 최적화)

**Current Problem (현재 문제점):**
- The app relies on local paths (`/Users/namseunghyeon/...`) and requires the terminal to be open.
- 로컬 절대 경로에 의존하고 있으며, 터미널이 켜져 있어야만 앱이 실행됨.

**Action Items (실행 항목):**
1.  **Dockerization (도커 컨테이너화)**:
    - Create a `Dockerfile` to package Python 3.9, ffmpeg, and all dependencies.
    - Python 3.9, ffmpeg 및 라이브러리 일체를 포함한 Docker 이미지 생성.
2.  **Path Abstraction (경로 추상화)**:
    - Replace hardcoded local paths with environment variables (e.g., `os.getenv('INBOX_PATH')`).
    - 하드코딩된 로컬 경로를 환경 변수 기반으로 교체하여 어떤 서버에서든 동작하도록 수정.
3.  **Service Management (서비스 관리)**:
    - Create a `docker-compose.yml` for easy startup/restart policies (always-on).
    - 서버 재부팅 시에도 자동 실행되도록 `docker-compose` 설정.

---

## ✨ Phase 3: UI/UX Improvements (사용자 경험 개선)

**Current Problem (현재 문제점):**
- The processing logs are text-only and scrolling is manual.
- 작업 로그가 텍스트로만 쌓여서 가독성이 떨어짐.

**Action Items (실행 항목):**
1.  **Real-time Progress Bar (실시간 진행률)**:
    - Show detailed progress (e.g., "STT 40%...", "Summarizing...") per job.
    - 작업별 상세 진행률(STT 중, 요약 중 등)을 시각적으로 표시.
2.  **Job History Tab (작업 이력 탭)**:
    - View past completed jobs and download links.
    - 과거 완료된 작업 목록 조회 및 결과물 다운로드 기능 추가.

---

## 📝 Next Steps (다음 단계)
- [ ] **Approve this plan** and create a specific task for Phase 1.
- [ ] **이 계획을 승인**하고, 1단계(웹 업로드) 작업을 위한 구체적 테스크 생성.
