# 🐳 Docker Deployment Guide

이 문서는 **Evangelical Mission Admin** 애플리케이션을 Docker를 사용하여 배포하고 실행하는 방법을 안내합니다.
Docker를 사용하면 로컬 개발 환경(Mac), 클라우드 서버(Ubuntu), 오라클 프리티어 등 어디서든 **동일한 환경**에서 안정적으로 실행할 수 있습니다.

---

## 📋 1. 준비 사항 (Prerequisites)

### 1) Docker 설치
가장 먼저 해당 OS에 맞는 Docker가 설치되어 있어야 합니다.

*   **Mac/Windows**: [Docker Desktop 다운로드](https://www.docker.com/products/docker-desktop/) (설치 후 프로그램 실행 필수)
*   **Linux (Ubuntu/Oracle Cloud)**:
    ```bash
    # Docker 설치
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    
    # 관리자 권한 없이 docker 실행 설정
    sudo usermod -aG docker $USER
    # (로그아웃 후 재로그인 필요)
    ```

### 2) 설정 파일 준비
프로젝트 루트의 `.env` 파일과 `config/` 폴더가 필요합니다.

1.  `.env.example`을 복사하여 `.env` 생성 (이미 있다면 패스)
    ```bash
    cp .env.example .env
    ```
2.  `.env` 파일 내용 채우기 (Google API Key, Admin 비밀번호 등)
3.  `config/google_key.json` 등의 인증 파일이 있다면 `config/` 폴더에 위치시킵니다.

---

## 🚀 2. 실행 (Run Command)

터미널에서 프로젝트 루트 경로로 이동한 뒤, 아래 명령어 **한 줄**이면 모든 게 실행됩니다.

```bash
docker-compose up --build -d
```

*   `--build`: 코드가 변경되었다면 이미지를 새로 빌드합니다.
*   `-d`: **Detached mode**. 백그라운드에서 실행합니다. (터미널을 꺼도 서버는 계속 돕니다)

### 정상 실행 확인
```bash
docker-compose ps
```
`State`가 `Up`으로 되어 있다면 성공입니다.
브라우저에서 `http://localhost:8501` (서버라면 `http://서버IP:8501`)로 접속하세요.

---

## 🛠 3. 유용한 관리 명령어

| 동작 | 명령어 | 설명 |
| :--- | :--- | :--- |
| **로그 보기** | `docker-compose logs -f` | 실시간으로 서버 로그를 확인합니다. (나가기: Ctrl+C) |
| **중지** | `docker-compose down` | 컨테이너를 중지하고 삭제합니다. (데이터는 보존됨) |
| **재시작** | `docker-compose restart` | 컨테이너를 단순히 재시작합니다. |
| **쉘 접속** | `docker exec -it evangelical_dev_app_1 /bin/bash` | 실행 중인 컨테이너 내부로 직접 들어갑니다. (디버깅용) |

---

## 📦 4. 파일 백업 및 유지보수

Docker를 사용하더라도 중요한 데이터는 로컬 컴퓨터(Host)에 안전하게 저장되도록 설정되어 있습니다 (`docker-compose.yml`의 volumes 설정 덕분입니다).

*   **설정 파일**: `./config`
*   **사용자 DB**: `./config/users.yaml`
*   **데이터 파일**: `./data` (Inbox, Archive 등)
*   **로그 파일**: `./logs`

따라서 컨테이너를 지우고 새로 만들어도(`down` -> `up`) **데이터는 사라지지 않습니다.**

---

## ☁️ 5. 클라우드 서버 배포 팁 (Oracle/AWS)

1.  **방화벽 해제**: 클라우드 콘솔(Security List)에서 **`8501` 포트**를 Inbound 규칙에 추가해야 외부에서 접속 가능합니다.
2.  **파일 전송**: `scp`나 `git clone`을 통해 프로젝트 소스를 서버로 옮깁니다. (주의: `.env`나 `google_key.json`은 보안상 git에 올리지 말고 별도로 전송하세요)
3.  **지속 실행**: `docker-compose up -d`로 실행하면 SSH 연결을 끊어도 서버는 24시간 돌아갑니다.

---

### ❓ 자주 묻는 질문 (FAQ)

**Q. 코드를 수정했어요. 어떻게 반영하나요?**
A. 코드를 수정하고 저장한 뒤, 다음 명령어를 실행하면 됩니다.
```bash
docker-compose up --build -d
```
Docker가 변경된 부분을 감지하고 이미지를 새로 만들어 재시작해줍니다.
