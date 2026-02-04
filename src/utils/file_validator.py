"""
파일 검증 유틸리티
- 파일명 sanitize
- 경로 traversal 방지
- 파일 크기/확장자 검증
- 중복 파일 감지
"""
import os
import re
from typing import Optional, Tuple

# 허용되는 비디오 확장자
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv'}

# 최대 파일 크기 (바이트) - 2GB
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024 * 1024


def sanitize_filename(filename: str) -> str:
    """
    파일명에서 위험 문자 제거

    Args:
        filename: 원본 파일명

    Returns:
        안전한 파일명
    """
    # 경로 구분자 제거 (../ 공격 방지)
    filename = os.path.basename(filename)

    # 허용: 한글, 영문, 숫자, 하이픈, 언더스코어, 점
    # 그 외 문자는 언더스코어로 대체
    filename = re.sub(r'[^\w가-힣\-_.]', '_', filename)

    # 연속된 언더스코어 정리
    filename = re.sub(r'_+', '_', filename)

    # 앞뒤 언더스코어 제거
    filename = filename.strip('_')

    return filename


def validate_path_within_base(file_path: str, base_path: str) -> bool:
    """
    경로가 base_path 내에 있는지 검증 (Path Traversal 방지)

    Args:
        file_path: 검증할 파일 경로
        base_path: 허용된 기본 경로

    Returns:
        base_path 내에 있으면 True
    """
    # 절대 경로로 변환
    real_base = os.path.realpath(base_path)
    real_file = os.path.realpath(file_path)

    # file_path가 base_path로 시작하는지 확인
    return real_file.startswith(real_base + os.sep) or real_file == real_base


def validate_video_extension(filename: str) -> bool:
    """
    비디오 파일 확장자 검증

    Args:
        filename: 파일명

    Returns:
        허용된 확장자이면 True
    """
    ext = os.path.splitext(filename.lower())[1]
    return ext in ALLOWED_VIDEO_EXTENSIONS


def validate_file_size(size_bytes: int) -> Tuple[bool, str]:
    """
    파일 크기 검증

    Args:
        size_bytes: 파일 크기 (바이트)

    Returns:
        (유효 여부, 메시지)
    """
    if size_bytes > MAX_FILE_SIZE_BYTES:
        size_gb = size_bytes / (1024 ** 3)
        max_gb = MAX_FILE_SIZE_BYTES / (1024 ** 3)
        return False, f"파일 크기가 너무 큽니다: {size_gb:.2f}GB (최대 {max_gb:.0f}GB)"
    return True, "OK"


def check_duplicate(filename: str, target_dir: str) -> bool:
    """
    대상 디렉토리에 동일한 파일명이 있는지 확인

    Args:
        filename: 확인할 파일명
        target_dir: 대상 디렉토리

    Returns:
        중복이면 True
    """
    if not os.path.exists(target_dir):
        return False

    target_path = os.path.join(target_dir, filename)
    return os.path.exists(target_path)


def validate_upload(
    filename: str,
    size_bytes: int,
    target_dir: str
) -> Tuple[bool, str, Optional[str]]:
    """
    업로드 파일 종합 검증

    Args:
        filename: 파일명
        size_bytes: 파일 크기 (바이트)
        target_dir: 저장될 디렉토리

    Returns:
        (유효 여부, 메시지, 안전한 파일명 또는 None)
    """
    # 1. 파일명 sanitize
    safe_filename = sanitize_filename(filename)
    if not safe_filename:
        return False, "유효하지 않은 파일명입니다.", None

    # 2. 확장자 검증
    if not validate_video_extension(safe_filename):
        allowed = ', '.join(ALLOWED_VIDEO_EXTENSIONS)
        return False, f"허용되지 않은 파일 형식입니다. 허용: {allowed}", None

    # 3. 크기 검증
    size_valid, size_msg = validate_file_size(size_bytes)
    if not size_valid:
        return False, size_msg, None

    # 4. 중복 검사 (경고만, 차단하지 않음)
    is_duplicate = check_duplicate(safe_filename, target_dir)

    if is_duplicate:
        return True, f"경고: 동일한 이름의 파일이 이미 존재합니다. 덮어쓰기됩니다.", safe_filename

    return True, "OK", safe_filename
