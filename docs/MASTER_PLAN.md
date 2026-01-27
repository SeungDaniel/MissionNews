# 🗺️ MASTER_PLAN.md
> **One-Pager for Evangelical Mission Automation**
> *Last Updated: 2026. 01. 26*

## 1. Problem Definition (가장 중요)
- **The Problem**: 매주 쏟아지는 선교 소식과 간증 영상을 수동으로 수집, 요약, 분류, 공유하는 과정에서 **담당자의 피로도 증가 및 휴먼 에러(파일명 실수, 누락)**가 지속적으로 발생함.
- **Why it matters**: 단순 반복 업무를 제거하여 본질적인 사역에 집중해야 하며, **"무너지지 않는 시스템"**을 통해 데이터의 정합성과 공유의 신속성을 보장해야 함.
- **Success Metrics**:
  - ✅ **Zero Manual Renaming**: 파일명 표준화 자동화율 100%
  - 🚀 **Efficiency**: 영상 입수 후 텔레그램 공유까지 소요 시간 < 30분
  - 🛡️ **Reliability**: 에러 발생 시 자동 복구 및 명확한 로그 남기기

## 2. Scope & Strategy
### In-Scope (이번 MVP 핵심)
- **Watch Folder Automation**: Inbox 폴더에 영상이 들어오면 자동으로 작업 시작
- **Multi-Modal Processing**: Audio Extraction -> STT -> LLM Summarization
- **Metadata Management**: Google Spreadsheets(DB) 양방향 동기화 (상태 업데이트, 정보 조회)
- **Notification**: 텔레그램(Telegram) 봇을 통한 요약문 및 썸네일/파일 전송
- **Archiving**: 처리 완료된 파일의 NAS/Local Archive 자동 이동 및 분류

### Out-of-Scope (제외 대상)
- 복잡한 영상 컷 편집 (Intro/Outro 붙이기 등)
- 모바일 전용 앱 개발
- 웹 기반 관리자 페이지 (현재는 Streamlit 대시보드로 대체)

## 3. Solution & Tech
- **Core Stack**: Python 3.x
- **UI/Dashboard**: Streamlit (운영 상황 모니터링 및 수동 트리거)
- **Database**: Google Sheets (via `gspread`)
- **AI/ML**:
  - **STT**: Local API / OpenAI Whisper
  - **LLM**: Custom Local LLM (OpenAI Compatible API)
- **Infrastructure**: Mac Mini (Local Server), NAS (Storage)
- **Key Library**: `moviepy` (영상 처리), `python-telegram-bot` (알림)

## 4. Roadmap & Status
### Phase 1: Foundation (Current)
- [x] **Core Pipeline**: 파일 감지 -> STT -> 요약 -> 전송 구현 완료
- [ ] **Stabilization**: 긴 영상 처리 시 타임아웃(Timeout) 및 메모리 이슈 해결
- [ ] **Error Handling**: 텔레그램 전송 실패(특수문자 등) 및 GSheet 연동 에러 방어 로직 적용

### Phase 2: Refinement
- [ ] **Performance**: LLM 응답 속도 최적화 및 비동기 처리 강화
- [ ] **Dashboard Upgrade**: Streamlit UI 직관성 개선 및 진행률(Progress Bar) 세분화
- [ ] **Feedback Loop**: 결과물에 대한 사용자 피드백(수정 요청) 반영 기능

### Phase 3: Expansion
- [ ] **Multi-Platform**: 카카오톡 등 추가 채널 연동 고려
- [ ] **Global Search**: 과거 데이터(요약, 영상) 검색 가능한 웹 아카이브 구축
