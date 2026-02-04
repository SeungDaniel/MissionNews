"""
MNAP 공통 상수 정의
"""

# === 파일 관련 ===
THUMBNAIL_COUNT = 9  # AI 썸네일 후보 수
MAX_VIDEO_SIZE_GB = 2  # 최대 업로드 크기 (GB)
MAX_VIDEO_SIZE_BYTES = MAX_VIDEO_SIZE_GB * 1024 * 1024 * 1024

# 허용되는 비디오 확장자
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv'}

# 허용되는 이미지 확장자
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

# === STT 관련 ===
STT_POLL_INTERVAL = 2  # 폴링 간격 (초)
STT_MAX_RETRIES = 180  # 최대 재시도 횟수 (2초 * 180 = 6분)
STT_TIMEOUT_SECONDS = 600  # 타임아웃 (초)

# === 썸네일 관련 ===
THUMBNAIL_ASPECT_RATIO = (4, 3)  # 가로:세로 비율
THUMBNAIL_CROP_BOTTOM_PERCENT = 25  # 자막 제거 시 하단 자르기 비율 (%)

# === UI 관련 ===
LOG_DISPLAY_COUNT = 20  # 로그 표시 개수
FILE_LIST_PAGE_SIZE = 50  # 파일 목록 페이지 크기

# === 날짜 형식 ===
DATE_FORMAT_DISPLAY = "%Y. %m. %d"  # 시트 표시용 (2025. 01. 15)
DATE_FORMAT_FILENAME = "%y%m%d"  # 파일명용 (250115)
DATE_FORMAT_LOG = "%H:%M:%S"  # 로그 타임스탬프

# === 시트 타입 ===
SHEET_TYPE_TESTIMONY = "testimony"
SHEET_TYPE_MISSION_NEWS = "mission_news"

SHEET_TYPES = {
    SHEET_TYPE_TESTIMONY: "간증영상 (Testimony)",
    SHEET_TYPE_MISSION_NEWS: "해외선교소식 (Mission News)"
}

# === 작업 상태 ===
JOB_STATUS_QUEUED = "queued"
JOB_STATUS_PROCESSING = "processing"
JOB_STATUS_COMPLETED = "completed"
JOB_STATUS_FAILED = "failed"

JOB_STATUS_ORDER = {
    JOB_STATUS_PROCESSING: 0,
    JOB_STATUS_QUEUED: 1,
    JOB_STATUS_FAILED: 2,
    JOB_STATUS_COMPLETED: 3
}

# === 사용자 역할 ===
ROLE_ADMIN = "admin"
ROLE_OPERATOR = "operator"

# === 청크 크기 ===
FILE_CHUNK_SIZE = 8 * 1024 * 1024  # 8MB (파일 저장 청크)
