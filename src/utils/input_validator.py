"""
입력값 검증 유틸리티
- 날짜 검증
- 이름 검증
- 국가 검증
"""
import re
from datetime import datetime
from typing import Tuple, Optional


def validate_date(date_str: str) -> Tuple[bool, str, Optional[datetime]]:
    """
    날짜 문자열 검증

    Args:
        date_str: 검증할 날짜 문자열

    Returns:
        (유효 여부, 메시지, 파싱된 datetime 또는 None)
    """
    if not date_str or not date_str.strip():
        return False, "날짜를 입력해주세요.", None

    # 지원하는 날짜 형식들
    formats = [
        "%Y-%m-%d",      # 2025-01-15
        "%Y. %m. %d",    # 2025. 01. 15
        "%Y.%m.%d",      # 2025.01.15
        "%y%m%d",        # 250115
        "%Y/%m/%d",      # 2025/01/15
        "%d/%m/%Y",      # 15/01/2025
        "%m/%d/%Y",      # 01/15/2025
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str.strip(), fmt)
            return True, "OK", parsed
        except ValueError:
            continue

    return False, "날짜 형식이 올바르지 않습니다. (예: 2025-01-15)", None


def validate_name(name: str, max_length: int = 50) -> Tuple[bool, str, Optional[str]]:
    """
    이름 검증

    Args:
        name: 검증할 이름
        max_length: 최대 길이

    Returns:
        (유효 여부, 메시지, 정제된 이름 또는 None)
    """
    if not name or not name.strip():
        return False, "이름을 입력해주세요.", None

    name = name.strip()

    if len(name) > max_length:
        return False, f"이름은 {max_length}자 이내로 입력해주세요.", None

    # 허용: 한글, 영문, 숫자, 공백, 하이픈
    if not re.match(r'^[\w가-힣\s\-]+$', name):
        return False, "이름에 특수문자를 사용할 수 없습니다.", None

    return True, "OK", name


def validate_country(country: str, country_map: dict = None) -> Tuple[bool, str, Optional[str]]:
    """
    국가명 검증

    Args:
        country: 검증할 국가명
        country_map: 국가 매핑 딕셔너리 (선택)

    Returns:
        (유효 여부, 메시지, 정제된 국가명 또는 None)
    """
    if not country or not country.strip():
        return False, "국가를 입력해주세요.", None

    country = country.strip()

    if len(country) > 30:
        return False, "국가명은 30자 이내로 입력해주세요.", None

    # 허용: 한글, 영문, 숫자, 공백
    if not re.match(r'^[\w가-힣\s]+$', country):
        return False, "국가명에 특수문자를 사용할 수 없습니다.", None

    # 매핑 딕셔너리가 제공된 경우, 존재 여부 경고 (차단하지 않음)
    if country_map and country not in country_map:
        return True, f"경고: '{country}'는 등록된 국가 목록에 없습니다. 지역이 자동 입력되지 않을 수 있습니다.", country

    return True, "OK", country


def validate_city(city: str, max_length: int = 50) -> Tuple[bool, str, Optional[str]]:
    """
    도시명 검증

    Args:
        city: 검증할 도시명
        max_length: 최대 길이

    Returns:
        (유효 여부, 메시지, 정제된 도시명 또는 None)
    """
    if not city:
        return True, "OK", ""  # 도시는 선택 필드

    city = city.strip()

    if len(city) > max_length:
        return False, f"도시명은 {max_length}자 이내로 입력해주세요.", None

    if not re.match(r'^[\w가-힣\s\-]+$', city):
        return False, "도시명에 특수문자를 사용할 수 없습니다.", None

    return True, "OK", city


def validate_age(age: str) -> Tuple[bool, str, Optional[str]]:
    """
    나이 검증

    Args:
        age: 검증할 나이

    Returns:
        (유효 여부, 메시지, 정제된 나이 또는 None)
    """
    if not age:
        return True, "OK", ""  # 나이는 선택 필드

    age = age.strip()

    # 숫자만 허용
    if not age.isdigit():
        return False, "나이는 숫자만 입력해주세요.", None

    age_int = int(age)
    if age_int < 1 or age_int > 150:
        return False, "유효한 나이를 입력해주세요.", None

    return True, "OK", age


def validate_metadata_form(
    name: str,
    country: str,
    date_val,  # datetime.date or str
    city: str = "",
    age: str = "",
    country_map: dict = None
) -> Tuple[bool, list, dict]:
    """
    메타데이터 폼 전체 검증

    Args:
        name: 이름
        country: 국가
        date_val: 날짜 (datetime.date 또는 문자열)
        city: 도시 (선택)
        age: 나이 (선택)
        country_map: 국가 매핑 딕셔너리

    Returns:
        (전체 유효 여부, 에러 메시지 리스트, 정제된 값 딕셔너리)
    """
    errors = []
    cleaned = {}

    # 이름 검증
    is_valid, msg, clean_name = validate_name(name)
    if not is_valid:
        errors.append(f"이름: {msg}")
    else:
        cleaned['name'] = clean_name

    # 국가 검증
    is_valid, msg, clean_country = validate_country(country, country_map)
    if not is_valid:
        errors.append(f"국가: {msg}")
    else:
        cleaned['country'] = clean_country
        if "경고" in msg:
            errors.append(msg)  # 경고도 표시

    # 날짜 처리
    if hasattr(date_val, 'strftime'):
        # datetime.date 객체인 경우
        cleaned['date'] = date_val
    else:
        # 문자열인 경우
        is_valid, msg, clean_date = validate_date(str(date_val))
        if not is_valid:
            errors.append(f"날짜: {msg}")
        else:
            cleaned['date'] = clean_date

    # 도시 검증 (선택)
    if city:
        is_valid, msg, clean_city = validate_city(city)
        if not is_valid:
            errors.append(f"도시: {msg}")
        else:
            cleaned['city'] = clean_city
    else:
        cleaned['city'] = ""

    # 나이 검증 (선택)
    if age:
        is_valid, msg, clean_age = validate_age(age)
        if not is_valid:
            errors.append(f"나이: {msg}")
        else:
            cleaned['age'] = clean_age
    else:
        cleaned['age'] = ""

    # 치명적 에러만 필터 (경고 제외)
    critical_errors = [e for e in errors if "경고" not in e]

    return len(critical_errors) == 0, errors, cleaned
