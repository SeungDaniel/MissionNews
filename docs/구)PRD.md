## 🚀 PRD: 선교 소식 및 간증 자동 아카이빙 시스템 (MNAP)

**프로젝트명:** Mission News & Testimony Auto-Archiving System
**역할:** 선교 소식(현지 소식)과 간증 영상의 파일명 변경, 업로드, 아카이빙 및 AI 콘텐츠 생성(요약) 자동화

### 1. 프로젝트 배경 및 목표

*   **현재의 문제점:** 영상 내용을 확인하며 수동으로 파일명을 변경하고, 여러 서버(유튜브, NAS 등)에 중복 업로드하는 과정이 번거로움.
*   **목표:** Python 기반의 자동화 파이프라인을 구축하여 다음을 수행한다.
    1.  **구글 시트(Multi-Sheet)** 동기화: 간증과 선교소식을 개별 시트로 관리.
    2.  **Hub & Spoke 아키텍처 (Server-Side Execution):**
        *   **프로그램 실행:** 모든 로직은 **GPU 서버**에서 구동됨.
        *   **데이터 흐름:** 사용자가 **NAS 폴더(Inbox)**에 파일을 넣으면, 서버가 이를 감지하여 처리.
        *   **AI 처리:** GPU 서버 로컬 자원 활용 (API 호출 불필요).
    3.  **사용자 편의성:** 사용자는 영상 다운로드 후 '공유 폴더'에 넣기만 하면 됨.
*   **핵심 철학:** **"NAS를 공유 우체통으로 사용한다."** 복잡한 업로드 과정 없이, 공유 폴더에 파일을 넣는 행위가 곧 입력이 된다.

### 2. 사용자 플로우 (Updated Workflow)

1.  **입력 (Input / Drop):**
    *   사용자가 방송실 서버에서 영상을 다운로드.
    *   내 맥북에 마운트된 **NAS의 `Mission_Inbox` 폴더**에 파일을 저장(또는 복사)한다.
2.  **등록 (Register):** 구글 시트의 해당 탭에 메타데이터 기입.
3.  **실행 (Trigger):**
    *   **옵션:** GPU 서버에 구축된 간단한 **웹 페이지(Web UI)** 접속 -> "작업 시작" 버튼 클릭.
    *   (또는 10분마다 자동 감지)
4.  **처리 (Process - On Server):**
    *   GPU 서버가 NAS(`Mission_Inbox`)에 있는 파일을 읽음.
    *   **AI 분석:** 로컬 GPU를 사용하여 STT 및 요약 수행 (속도 극대화).
    *   **썸네일:** AI 학습 데이터용 크롭 생성.
    *   **아카이빙:** 처리된 영상을 `Mission_Archive` 폴더(같은 NAS 내)로 이동.
    *   **업로드:** 서버에서 유튜브로 직접 업로드 (가정용 인터넷보다 업로드 속도 빠름).
5.  **출력 (Output):** 시트 업데이트 및 텔레그램 알림.

### 3. 기능 요구사항 (Functional Requirements)

#### 기능 A: 서버 구동 방식 (Server-Side)

*   **배포 위치:** Linux GPU Server.
*   **필수 조건:** GPU 서버가 **NAS를 마운트(SMB/NFS)** 하고 있어야 함.
*   **장점:** 사용자가 맥북을 꺼도 작업은 서버에서 계속됨.

#### 기능 B: AI & 썸네일

*   GPU 직접 사용 (`whisper` 라이브러리 직접 import). API 통신 오버헤드 없음.
*   썸네일: 학습용 데이터셋 구축을 위한 Smart Crop.

#### 기능 C: 하이브리드 업로드

*   **YouTube:** 서버 IP에서 업로드 수행. (서버 대역폭 활용)

#### 기능 D: 리포팅

*   웹 UI(Streamlit 등)를 통해 진행 상황 실시간 모니터링 가능.

### 4. 기술적 제약 및 환경

*   **Client:** macOS (Intel i5) - 단순 파일 복사 역할.
*   **Server:** Linux GPU Server - **Main Controller**.
*   **Infrastructure:** NAS must be mounted on BOTH Client and Server.

### 5. 데이터 구조 (Legacy-Safe)

*   A~P 컬럼 유지, Q열 이후 시스템 컬럼 사용.
