# 🏗️ MNAP Project Architecture & Implementation Plan
# MNAP 프로젝트 아키텍처 및 구현 계획

## 1. Overview (개요)
**Project Name**: Mission News & Testimony Auto-Archiving System (MNAP)
**Goal**: Automate the renaming, AI analysis, and archiving of mission video files.
**목표**: 선교 영상 파일의 이름 변경, AI 분석(요약), 서버 아키이빙 과정을 자동화.

---

## 2. System Architecture (시스템 아키텍처)

The system operates on a **Hybrid Architecture** leveraging Local execution, NAS Storage, and GPU API.
본 시스템은 로컬 실행, NAS 스토리지, GPU API를 결합한 **하이브리드 아키텍처**로 동작합니다.

### 2.1 Component Flow (컴포넌트 흐름)
1.  **Local (Mac)**: Main Controller.
    *   Runs Python Script.
    *   Extracts Audio (`ffmpeg`).
    *   Manages Google Sheet Synchronization.
2.  **NAS (Storage)**: Synology NAS.
    *   Mounted via **SMB/WebDAV**.
    *   Acts as the final destination for Video/Thumbnail files.
3.  **GPU Server (Compute)**: Linux Server.
    *   Exposes **REST API** (e.g., FastAPI).
    *   Receives Audio -> Performs Whisper STT & LLM Summarization -> Returns Text.

---

## 3. Workflow Logic (워크플로우 로직)

### Step 1: Manual Trigger (수동 실행)
*   **User Action**: Downloads video to `Mission_Inbox` and fills Metadata in Google Sheet (including 'Original Filename').
*   **사용자 액션**: 영상을 `Mission_Inbox`에 다운로드하고 구글 시트에 메타데이터(원본 파일명 포함)를 입력.
*   **Execution**: User runs `python main.py`.
*   **실행**: 사용자가 스크립트 실행.

### Step 2: Processing (처리)
1.  **Match**: Script pairs Sheet rows (`Status=Pending`) with Local Files.
2.  **Audio Analysis**:
    *   Extract `.mp3` locally.
    *   Send to GPU API -> Receive Summary Text.
3.  **Thumbnail**: Generate 16:9 or Smart Crop image for AI Training dataset.
4.  **Rename & Move**:
    *   Rename file to `YYMMDD_Country_Type_Name.mp4`.
    *   Move to NAS Path (handled by `config.yaml` for Dev/Prod switching).

### Step 3: Reporting (리포팅)
*   Upload to YouTube (Unlisted).
*   Update Google Sheet (Status, URL).
*   Send Telegram Notification.

---

## 4. Technical Stack (기술 스택)

| Component | Technology | Note |
| :--- | :--- | :--- |
| **Language** | Python 3.9+ | |
| **Media Engine** | `ffmpeg` | Installed on Mac (Local) |
| **Database** | Google Sheets (`gspread`) | Metadata & State Management |
| **API Client** | `requests` | Communication with GPU Server |
| **Configuration** | `PyYAML` | Environment Management (Dev/Prod) |

---

## 5. Development Strategy (개발 전략)

*   **Phase 1: Skeleton**: Setup folder structure and config loader.
*   **Phase 2: Modules**: Implement G-Sheet, Media, and API modules independently.
*   **Phase 3: Integration**: Combine modules into `main.py` workflow.
*   **Phase 4: Testing**: Verify with "Mock NAS" (Local folder) before Prod deployment.
