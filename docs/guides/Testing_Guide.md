# MNAP 시스템 테스트 가이드 (Testing Guide)

이 문서는 **선교 소식 자동 아카이빙 시스템 (MNAP)**의 설치부터 실행, 문제 해결까지의 과정을 단계별로 안내합니다.

---

## 1. 🛠️ 환경 설정 (Installation)

시스템을 실행하기 위해 필요한 라이브러리와 프로그램을 설치합니다.

### 1-1. Python 패키지 설치
터미널에서 아래 명령어를 입력하여 필요한 파이썬 라이브러리를 한 번에 설치합니다.
(처음 한 번만 수행하면 됩니다)

```bash
pip install -r requirements.txt
```

> **설치되는 주요 라이브러리:**
> *   `gspread`, `oauth2client`: 구글 시트 연동
> *   `openai-whisper`: 음성 인식 (STT)
> *   `ffmpeg-python`: 영상/오디오 처리
> *   `requests`, `pyyaml`: API 통신 및 설정 관리

### 1-2. FFmpeg 설치 (필수)
영상 처리를 위해 `ffmpeg`가 시스템에 설치되어 있어야 합니다.
(맥북 기준)
1.  터미널에 `ffmpeg -version`을 입력해 봅니다.
2.  명령어를 찾을 수 없다고 나오면, [Homebrew](https://brew.sh/)를 이용해 설치합니다.
    ```bash
    brew install ffmpeg
    ```

---

## 2. ⚙️ 설정 및 준비 (Configuration)

### 2-1. 구글 API 키 준비
1.  `service_account.json` 파일을 준비합니다.
2.  `config/` 폴더 안에 넣어줍니다. (`config/service_account.json`)
3.  **[중요]** 키 파일 안에 있는 `client_email` 주소를 복사하여, 작업할 구글 시트에 **'편집자'** 권한으로 초대(공유)합니다.

### 2-2. Config 확인
`config/config.yaml` 파일이 올바르게 설정되어 있는지 확인합니다.
*   `environment`: `DEV` (테스트용) 또는 `PROD` (실사용)
*   **경로(Paths)**: `inbox`, `archive` 폴더 경로가 내 컴퓨터/NAS 경로와 맞는지 확인합니다.

---

## 3. 🧪 데이터 준비 (Data Prep)

테스트를 위해 가짜 데이터를 준비합니다.

### 3-1. Inbox에 영상 넣기
*   `data/Mission_Inbox` (또는 설정된 Inbox 경로)에 테스트할 영상 파일을 넣습니다.
*   예: `test_video.mp4`

### 3-2. 구글 시트 작성
구글 시트에 아래 내용을 입력합니다.

| M열 (원본 파일명) | N열 (처리 상태) |
| :--- | :--- |
| `test_video.mp4` | `대기` |

> **주의:** M열의 파일명은 Inbox에 넣은 파일명과 **토씨 하나 틀리지 않고 똑같아야** 합니다 (확장자 포함).

---

## 4. 🚀 실행 (Execution)

터미널에서 `main.py`를 실행합니다.

```bash
python main.py
```

### 정상 실행 로그 예시
```text
🚀 MNAP: 선교 소식 자동 아카이빙 시스템 시작
...
📋 총 1개의 대기 작업을 발견했습니다.

▶️ 작업 시작: test_video.mp4
   [1/6] 파일명 변경: test_video.mp4 -> 240101_KOR_Hong.mp4
   [2/6] 오디오 추출 중...
   [3/6] AI 분석 (STT -> Server)...
   [4/6] 썸네일 후보 5장 생성 중...
   [5/6] NAS로 이동 (Archive)...
✅ 모든 작업 완료!
```

---

## 5. ❓ 문제 해결 (Troubleshooting)

### Q1. `ModuleNotFoundError: No module named 'gspread'` 에러가 나요!
*   **원인**: 필수 라이브러리가 설치되지 않았습니다.
*   **해결**: `1-1. Python 패키지 설치` 단계를 다시 수행해 주세요. (`pip install -r requirements.txt`)

### Q2. `[WinError 2] 지정된 파일을 찾을 수 없습니다` (FFmpeg 에러)
*   **원인**: FFmpeg가 컴퓨터에 깔려있지 않거나, 환경 변수 설정이 안 되어 있습니다.
*   **해결**: `brew install ffmpeg`로 설치해 주세요.

### Q3. 시트가 업데이트되지 않아요.
*   **원인**: 봇 계정이 시트에 초대가 안 되었거나, 열(Column) 위치가 맞지 않을 수 있습니다.
*   **해결**:
    1.  `service_account.json`의 이메일이 시트에 공유되어 있는지 확인.
    2.  스크린샷과 현재 시트의 M, N 열 위치가 맞는지 확인.

### Q4. "파일 없음"이라고 뜨고 넘어가요.
*   **원인**: 시트에 적은 파일명과 실제 Inbox에 있는 파일명이 다릅니다. (공백, 대소문자 주의)
*   **해결**: 이름을 복사-붙여넣기해서 일치시켜 주세요.

### Q5. `APIError: [403]: Google Drive API has not been used...`
*   **원인**: 키는 맞는데, 구글 클라우드 콘솔에서 **Drive API** 사용 설정이 안 되어 있어서 그렇습니다.
*   **해결**:
    1.  에러 메시지에 나온 링크(https://console.developers.google.com/...)를 클릭합니다.
    2.  파란색 **"사용 설정(Enable)"** 버튼을 누릅니다.
    3.  1~2분 뒤에 다시 실행하면 됩니다.
