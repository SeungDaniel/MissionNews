"""
동영상 업로드 컴포넌트
- Streamlit file_uploader 기반 드래그 앤 드롭 UI
- 다중 파일 업로드 지원
- 파일 검증 및 진행률 표시
- 청크 단위 저장 (메모리 효율)
"""
import os
import streamlit as st
from typing import List, Optional, Tuple

from src.utils.file_validator import (
    validate_upload,
    sanitize_filename,
    ALLOWED_VIDEO_EXTENSIONS,
    MAX_FILE_SIZE_BYTES
)


def get_allowed_extensions_display() -> str:
    """허용된 확장자를 사용자 친화적 문자열로 반환"""
    return ', '.join(ext.upper().replace('.', '') for ext in sorted(ALLOWED_VIDEO_EXTENSIONS))


def format_file_size(size_bytes: int) -> str:
    """파일 크기를 읽기 쉬운 형식으로 변환"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


def save_uploaded_file_chunked(
    uploaded_file,
    target_path: str,
    chunk_size: int = 8 * 1024 * 1024  # 8MB 청크
) -> bool:
    """
    청크 단위로 파일 저장 (메모리 효율)

    Args:
        uploaded_file: Streamlit UploadedFile 객체
        target_path: 저장할 경로
        chunk_size: 청크 크기 (기본 8MB)

    Returns:
        저장 성공 여부
    """
    try:
        # 디렉토리 존재 확인
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        with open(target_path, 'wb') as f:
            while True:
                chunk = uploaded_file.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)

        # 파일 포인터 리셋 (다시 읽을 수 있도록)
        uploaded_file.seek(0)
        return True

    except Exception as e:
        st.error(f"파일 저장 중 오류 발생: {e}")
        return False


def render_video_uploader(
    target_dir: str,
    sheet_type: str,
    key_suffix: str = ""
) -> Tuple[List[str], List[str]]:
    """
    동영상 업로드 UI 렌더링

    Args:
        target_dir: 파일이 저장될 디렉토리
        sheet_type: 'testimony' 또는 'mission_news'
        key_suffix: 위젯 키 중복 방지용 접미사

    Returns:
        (성공한 파일 경로 리스트, 에러 메시지 리스트)
    """
    max_gb = MAX_FILE_SIZE_BYTES / (1024 ** 3)

    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
        <h4 style="margin: 0 0 0.5rem 0;">📤 동영상 파일 업로드</h4>
        <p style="margin: 0; font-size: 0.9rem; color: #666;">
            파일을 드래그하거나 클릭하여 선택하세요<br>
            • 허용 형식: {get_allowed_extensions_display()}<br>
            • 최대 크기: {max_gb:.0f}GB (파일당)
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 파일 업로더 위젯
    uploaded_files = st.file_uploader(
        "동영상 파일 선택",
        type=[ext.replace('.', '') for ext in ALLOWED_VIDEO_EXTENSIONS],
        accept_multiple_files=True,
        key=f"video_uploader_{sheet_type}_{key_suffix}",
        help=f"여러 파일을 한 번에 선택할 수 있습니다. 최대 {max_gb:.0f}GB/파일"
    )

    success_paths = []
    error_messages = []

    if not uploaded_files:
        return success_paths, error_messages

    # 디렉토리 존재 확인
    os.makedirs(target_dir, exist_ok=True)

    # 각 파일 처리
    st.markdown("---")
    st.markdown("#### 📁 업로드 파일 목록")

    for idx, uploaded_file in enumerate(uploaded_files):
        file_name = uploaded_file.name
        file_size = uploaded_file.size

        # 검증
        is_valid, message, safe_filename = validate_upload(
            file_name, file_size, target_dir
        )

        # 파일 정보 표시
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.text(f"📹 {file_name}")
        with col2:
            st.text(format_file_size(file_size))
        with col3:
            if is_valid:
                if "경고" in message:
                    st.warning("⚠️ 중복")
                else:
                    st.success("✅ OK")
            else:
                st.error("❌ 실패")

        if not is_valid:
            error_messages.append(f"{file_name}: {message}")
            continue

        # 중복 경고 표시
        if "경고" in message:
            st.warning(f"⚠️ {message}")

    # 업로드 버튼
    if uploaded_files:
        valid_files = [
            (f, sanitize_filename(f.name))
            for f in uploaded_files
            if validate_upload(f.name, f.size, target_dir)[0]
        ]

        if valid_files:
            if st.button(
                f"📥 {len(valid_files)}개 파일 저장",
                type="primary",
                key=f"save_uploads_{sheet_type}_{key_suffix}"
            ):
                progress_bar = st.progress(0)
                status_text = st.empty()

                for idx, (uploaded_file, safe_filename) in enumerate(valid_files):
                    status_text.text(f"저장 중... {safe_filename} ({idx + 1}/{len(valid_files)})")

                    target_path = os.path.join(target_dir, safe_filename)

                    if save_uploaded_file_chunked(uploaded_file, target_path):
                        success_paths.append(target_path)
                        st.success(f"✅ {safe_filename} 저장 완료")
                    else:
                        error_messages.append(f"{safe_filename}: 저장 실패")

                    # 진행률 업데이트
                    progress_bar.progress((idx + 1) / len(valid_files))

                status_text.text("완료!")
                progress_bar.progress(1.0)

                if success_paths:
                    st.success(f"🎉 총 {len(success_paths)}개 파일 저장 완료!")
                    st.info("💡 아래 파일 목록에서 선택하여 메타데이터를 입력하세요.")

    return success_paths, error_messages


def render_compact_uploader(
    target_dir: str,
    sheet_type: str,
    key_suffix: str = ""
) -> Optional[str]:
    """
    간단한 단일 파일 업로드 UI

    Args:
        target_dir: 저장 디렉토리
        sheet_type: 시트 타입
        key_suffix: 키 접미사

    Returns:
        저장된 파일 경로 또는 None
    """
    uploaded_file = st.file_uploader(
        "동영상 파일 업로드 (드래그 앤 드롭)",
        type=[ext.replace('.', '') for ext in ALLOWED_VIDEO_EXTENSIONS],
        key=f"compact_uploader_{sheet_type}_{key_suffix}"
    )

    if not uploaded_file:
        return None

    is_valid, message, safe_filename = validate_upload(
        uploaded_file.name, uploaded_file.size, target_dir
    )

    if not is_valid:
        st.error(f"❌ {message}")
        return None

    if "경고" in message:
        st.warning(f"⚠️ {message}")

    # 저장
    target_path = os.path.join(target_dir, safe_filename)
    os.makedirs(target_dir, exist_ok=True)

    if save_uploaded_file_chunked(uploaded_file, target_path):
        st.success(f"✅ {safe_filename} 저장 완료")
        return target_path

    return None
