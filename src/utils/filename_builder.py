"""
파일명 생성 유틸리티
- 시트 타입별 파일명 규칙 통합
"""
from datetime import date, datetime
from typing import Union, Optional

from src.constants import SHEET_TYPE_TESTIMONY, SHEET_TYPE_MISSION_NEWS
from src.utils.date_parser import format_date_for_filename
from src.utils.file_validator import sanitize_filename


def build_video_filename(
    sheet_type: str,
    region: str,
    date_val: Union[str, date, datetime],
    name: str,
    extension: str = ".mp4"
) -> Optional[str]:
    """
    시트 타입에 따른 비디오 파일명 생성

    Args:
        sheet_type: 'testimony' 또는 'mission_news'
        region: 지역명
        date_val: 날짜
        name: 이름
        extension: 파일 확장자 (기본 .mp4)

    Returns:
        생성된 파일명 또는 None

    파일명 규칙:
        - testimony: {지역}_{YYMMDD}_{이름}.mp4
        - mission_news: {YYMMDD}_해외선교소식_{지역}_{이름}.mp4
        - 기타: {YYMMDD}_기타_{지역}_{이름}.mp4
    """
    if not name or not region:
        return None

    # 날짜 포맷
    yymmdd = format_date_for_filename(date_val)
    if not yymmdd:
        return None

    # 확장자 정규화
    if not extension.startswith('.'):
        extension = '.' + extension

    # 시트 타입별 파일명 생성
    if sheet_type == SHEET_TYPE_TESTIMONY:
        filename = f"{region}_{yymmdd}_{name}{extension}"
    elif sheet_type == SHEET_TYPE_MISSION_NEWS:
        filename = f"{yymmdd}_해외선교소식_{region}_{name}{extension}"
    else:
        filename = f"{yymmdd}_기타_{region}_{name}{extension}"

    # 파일명 sanitize
    return sanitize_filename(filename)


def build_thumbnail_filename(video_filename: str, extension: str = ".jpg") -> str:
    """
    비디오 파일명으로부터 썸네일 파일명 생성

    Args:
        video_filename: 비디오 파일명
        extension: 썸네일 확장자 (기본 .jpg)

    Returns:
        썸네일 파일명
    """
    import os
    base_name = os.path.splitext(video_filename)[0]

    if not extension.startswith('.'):
        extension = '.' + extension

    return f"{base_name}{extension}"


def build_audio_filename(video_filename: str, extension: str = ".wav") -> str:
    """
    비디오 파일명으로부터 오디오 파일명 생성

    Args:
        video_filename: 비디오 파일명
        extension: 오디오 확장자 (기본 .wav)

    Returns:
        오디오 파일명
    """
    import os
    base_name = os.path.splitext(video_filename)[0]

    if not extension.startswith('.'):
        extension = '.' + extension

    return f"{base_name}{extension}"


def parse_filename_components(filename: str, sheet_type: str) -> Optional[dict]:
    """
    파일명에서 구성 요소 추출

    Args:
        filename: 파일명
        sheet_type: 시트 타입

    Returns:
        {'region': ..., 'date': ..., 'name': ...} 또는 None
    """
    import os
    import re

    # 확장자 제거
    base_name = os.path.splitext(filename)[0]

    if sheet_type == SHEET_TYPE_TESTIMONY:
        # 패턴: {지역}_{YYMMDD}_{이름}
        match = re.match(r'^(.+?)_(\d{6})_(.+)$', base_name)
        if match:
            return {
                'region': match.group(1),
                'date': match.group(2),
                'name': match.group(3)
            }

    elif sheet_type == SHEET_TYPE_MISSION_NEWS:
        # 패턴: {YYMMDD}_해외선교소식_{지역}_{이름}
        match = re.match(r'^(\d{6})_해외선교소식_(.+?)_(.+)$', base_name)
        if match:
            return {
                'date': match.group(1),
                'region': match.group(2),
                'name': match.group(3)
            }

    return None
