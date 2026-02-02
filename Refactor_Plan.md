# 🚀 Refactoring Execution Plan v2.0 (Enterprise Ready)
> **Goal**: Transition from a Personal Tool to a **Secure, Scalable, Multi-User Platform**.
> **목표**: 개인용 도구를 넘어 **보안이 강화되고, 확장이 용이하며, 협업이 가능한 엔터프라이즈급 플랫폼**으로 고도화.

---

## 🔒 Phase 1: Security & Auth (보안 및 인증 체계)
**Goal:** 누구나 접속 가능한 현재 상태를 차단하고, 안전한 접속 환경 구축.

1.  **Environment Variable Management (환경 변수 관리 강화)**
    *   **Task:** `.env` 파일 로딩 체계 정립 및 `.gitignore` 엄격 적용.
    *   **Detail:** API Key, DB 접속 정보 등 민감 정보를 코드에서 완전히 분리. `python-dotenv` 도입.
2.  **Basic Authentication (기본 인증)**
    *   **Task:** Streamlit Native Auth 또는 `streamlit-authenticator` 라이브러리 도입.
    *   **Detail:** 
        *   로그인 페이지 구현 (ID/PW).
        *   비밀번호 Hashing 저장 및 검증.
        *   세션 관리 (일정 시간 후 자동 로그아웃).

---

## 🐳 Phase 2: Docker & Infrastructure (인프라 컨테이너화)
**Goal:** 어떤 서버(AWS, Oracle Cloud, On-Premise)에서도 5분 안에 배포 가능한 상태.

1.  **Dockerization (도커 이미지 빌드)**
    *   **Task:** `Dockerfile` 작성.
    *   **Detail:**
        *   Python 3.9 Slim 베이스 이미지 사용 (경량화).
        *   OS Level 의존성 (`ffmpeg`, `git` 등) 설치 스크립트화.
        *   타임존(KST) 설정 포함.
2.  **Volume & Network (데이터 영속성)**
    *   **Task:** `docker-compose.yml` 구성.
    *   **Detail:**
        *   **Volumes:** 로그 파일, 업로드된 영상, DB(SQLite 등 사용 시) 데이터 영구 보존 설정.
        *   **Host Path Mapping:** NAS 경로와 컨테이너 내부 경로 매핑 전략 수립.

---

## 👥 Phase 3: Role-Based Access Control (RBAC, 역할 분리)
**Goal:** 관리자(Admin)와 일반 작업자(Operator)의 뷰(View)와 권한을 분리.

1.  **User Role Definition (역할 정의)**
    *   **Admin (관리자):**
        *   시스템 설정(Config) 변경 (프롬프트 수정, 경로 변경 등).
        *   사용자(User) 계정 관리 및 로그 조회.
        *   서버 상태 모니터링 (CPU, Memory, Disk Usage).
    *   **Operator (작업자):**
        *   영상 업로드 및 작업 요청.
        *   본인 작업 진행 상황 확인 및 결과 다운로드.
        *   (설정 변경 불가, 시스템 로그 조회 불가).
2.  **Dynamic UI Rendering (동적 UI 렌더링)**
    *   **Task:** 로그인한 사용자의 `role`에 따라 사이드바 메뉴 및 접근 가능 페이지 분기 처리.
    *   **Detail:** `if user.role == 'admin': show_admin_page()` 로직 구현.

---

## 🛠 Phase 4: Web Upload & Queue System (웹 업로드 및 큐 관리)
**Goal:** 로컬 파일 복사가 아닌, 웹 브라우저를 통한 작업 요청 및 비동기 처리.

1.  **Web File Uploader (웹 업로더)**
    *   **Task:** Streamlit `file_uploader` 위젯으로 대용량 파일 청크 업로드 구현.
2.  **Background Job Queue (백그라운드 큐 도입)**
    *   **Current Issue:** 영상 변환 중 브라우저를 끄면 작업이 중단됨.
    *   **Solution:** `Celery` + `Redis` 또는 파이썬 `multiprocessing` 큐 도입.
    *   **Benefit:** 업로드만 해두면 브라우저를 꺼도 서버 백그라운드에서 작업 완료 후 알림 전송.

---

## 📅 Roadmap Summary
| Phase | Focus | Key Tech | Expected Timeline |
| :--- | :--- | :--- | :--- |
| **Ph 1** | **Security** | `.env`, `Auth Lib` | 1 Week |
| **Ph 2** | **Docker** | `Docker`, `Compose` | 1 Week |
| **Ph 3** | **RBAC (Admin)** | `Session State` | 1.5 Weeks |
| **Ph 4** | **Async Queue** | `Redis/Celery` | 2 Weeks |
