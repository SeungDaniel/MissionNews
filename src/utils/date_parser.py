"""
날짜 파싱 유틸리티
- 다양한 형식의 날짜를 통합 처리
"""
from datetime import datetime, date
from typing import Optional, Union

from src.constants import DATE_FORMAT_DISPLAY, DATE_FORMAT_FILENAME


def parse_date(raw_date: Union[str, date, datetime]) -> Optional[datetime]:
    """
    다양한 형식의 날짜를 datetime 객체로 파싱

    Args:
        raw_date: 날짜 (문자열, date, datetime)

    Returns:
        datetime 객체 또는 None
    """
    if isinstance(raw_date, datetime):
        return raw_date

    if isinstance(raw_date, date):
        return datetime.combine(raw_date, datetime.min.time())

    if not raw_date or not str(raw_date).strip():
        return None

    raw_date = str(raw_date).strip()

    # 지원하는 날짜 형식들
    formats = [
        "%Y-%m-%d",       # 2025-01-15
        "%Y. %m. %d",     # 2025. 01. 15
        "%Y.%m.%d",       # 2025.01.15
        "%y%m%d",         # 250115
        "%Y/%m/%d",       # 2025/01/15
        "%d/%m/%Y",       # 15/01/2025
        "%m/%d/%Y",       # 01/15/2025
        "%Y%m%d",         # 20250115
        "%Y. %m. %d.",    # 2025. 01. 15. (후행 점 포함)
    ]

    for fmt in formats:
        try:
            return datetime.strptime(raw_date, fmt)
        except ValueError:
            continue

    return None


def to_yymmdd(raw_date: Union[str, date, datetime]) -> Optional[str]:
    """
    날짜를 YYMMDD 형식 문자열로 변환

    Args:
        raw_date: 날짜 (문자열, date, datetime)

    Returns:
        YYMMDD 형식 문자열 (예: "250115") 또는 None
    """
    parsed = parse_date(raw_date)
    if parsed:
        return parsed.strftime(DATE_FORMAT_FILENAME)
    return None


def to_display_format(raw_date: Union[str, date, datetime]) -> Optional[str]:
    """
    날짜를 표시용 형식으로 변환

    Args:
        raw_date: 날짜 (문자열, date, datetime)

    Returns:
        "YYYY. MM. DD" 형식 문자열 또는 None
    """
    parsed = parse_date(raw_date)
    if parsed:
        return parsed.strftime(DATE_FORMAT_DISPLAY)
    return None


def format_date_for_sheet(raw_date: Union[str, date, datetime]) -> str:
    """
    Google Sheet용 날짜 형식 변환

    Args:
        raw_date: 날짜 (문자열, date, datetime)

    Returns:
        "YYYY. MM. DD" 형식 문자열 (실패 시 빈 문자열)
    """
    result = to_display_format(raw_date)
    return result if result else ""


def format_date_for_filename(raw_date: Union[str, date, datetime]) -> str:
    """
    파일명용 날짜 형식 변환

    Args:
        raw_date: 날짜 (문자열, date, datetime)

    Returns:
        "YYMMDD" 형식 문자열 (실패 시 빈 문자열)
    """
    result = to_yymmdd(raw_date)
    return result if result else ""
