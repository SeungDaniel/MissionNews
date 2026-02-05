# 🚀 서버 배포 치트시트 (Deployment Cheat Sheet)

리눅스 서버에 접속하여 **코드를 내려받고 Docker로 실행하는** 전체 과정을 요약했습니다.

---

## 1. 코드 내려받기 (Git Pull)

### 1-1. 처음 설치할 때 (Clone)
```bash
# 원하는 폴더로 이동
cd /home/dev/projects

# 코드 복제
git clone https://github.com/SeungDaniel/MissionNews.git

# 폴더 입장
cd MissionNews
```

### 1-2. 업데이트할 때 (Pull)
```bash
# 프로젝트 폴더로 이동
cd /home/dev/projects/MissionNews

# 최신 코드 당겨오기
git pull origin main
```

---

## 2. 필수 설정 파일 준비 (Manual Copy)
**.env** 파일과 **config/users.yaml** 파일은 Git에 없으므로, 로컬에서 직접 복사하거나 서버에서 만들어야 합니다.

### 방법 A: 터미널에서 직접 생성 (nano 에디터 사용)
```bash
# 1. .env 생성
nano .env
# (내용 붙여넣기 후 Ctrl+X -> Y -> Enter)

# 2. users.yaml 생성
nano config/users.yaml
# (내용 붙여넣기 후 Ctrl+X -> Y -> Enter)
```

### 방법 B: 로컬에서 파일 전송 (scp)
*(로컬 맥북 터미널에서 실행)*
```bash
scp -P 13022 .env dev@aiteam.tplinkdns.com:~/projects/MissionNews/
scp -P 13022 config/users.yaml dev@aiteam.tplinkdns.com:~/projects/MissionNews/config/
```

---

## 3. 시놀로지/외부 서버 마운트 (Mount)

서버의 폴더와 외부 스토리지(NAS 등)를 연결합니다. (서버 관리자 권한 필요)

```bash
# 마운트 포인트 생성 (최초 1회)
sudo mkdir -p /mnt/synology/inbox

# 마운트 실행 (예시)
sudo mount -t cifs //192.168.0.50/Mission_Inbox /mnt/synology/inbox -o username=user,password=pass
```

> **확인**: `ls -al /mnt/synology/inbox` 했을 때 파일들이 보여야 합니다.

---

## 4. Docker 실행 (Build & Run)

이제 앱을 실행합니다.

```bash
# 기존 컨테이너 끄고 + 이미지 새로 빌드하고 + 백그라운드 실행
docker-compose up --build -d
```

### 실행 상태 확인
```bash
docker-compose ps
```

### 로그 실시간 확인
```bash
docker-compose logs -f
```
*(로그 보기를 끝내려면 `Ctrl + C`)*
