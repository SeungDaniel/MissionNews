import streamlit as st
import os
import time
import pandas as pd
from datetime import datetime
import sys


# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config_loader import settings
from src.modules.gsheet import GSheetManager
from src.modules import media, stt_module, api_client, nas_manager, telegram_bot
from PIL import Image
from streamlit_cropper import st_cropper

# Page Config
st.set_page_config(
    page_title="Evangelical Mission Admin",
    page_icon="🎬",
    layout="wide"
)

# Initialize Session State
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'data_editor_key' not in st.session_state:
    st.session_state.data_editor_key = 0

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {message}")
    # Also print to terminal for debugging
    print(f"[{timestamp}] {message}")

def get_inbox_files(sheet_type):
    # Mapping sheet_type to subfolder name
    subfolders = settings.config['google_sheet']['subfolders']
    folder_name = subfolders.get(sheet_type)
    if not folder_name:
        return []
    
    inbox_path = os.path.join(settings.paths['inbox'], folder_name)
    if not os.path.exists(inbox_path):
        os.makedirs(inbox_path, exist_ok=True)
        return []
    
    files = sorted([f for f in os.listdir(inbox_path) if f.startswith('.') is False and f.lower().endswith('.mp4')])
    return files

def main():
    st.title("🎬 Evangelical Mission Admin")
    
    # Sidebar: Mode Selection via Tabs is better, but let's put global settings here if needed
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # 1. Environment Selection
        current_env = settings.config.get('environment', 'DEV')
        env_options = ["DEV", "PROD"]
        try:
            env_index = env_options.index(current_env)
        except ValueError:
            env_index = 0
            
        selected_env = st.selectbox("Environment", env_options, index=env_index)
        
        # 2. Path Configuration (for current env)
        st.divider()
        st.subheader("📂 Path Settings")
        
        # Get paths for selected env (safe fallback)
        env_lower = selected_env.lower()
        current_paths = settings.config.get('paths', {}).get(env_lower, {})
        
        inbox_val = st.text_input("Inbox Path", value=current_paths.get('inbox', ''))
        
        # 3. Save Button
        if st.button("💾 설정 저장 (Save Config)"):
            new_config = settings.config.copy()
            new_config['environment'] = selected_env
            
            # Update paths for this specific env
            if 'paths' not in new_config:
                new_config['paths'] = {}
            if env_lower not in new_config['paths']:
                new_config['paths'][env_lower] = {}
                
            new_config['paths'][env_lower]['inbox'] = inbox_val
            # Preserve other keys if any
            new_config['paths'][env_lower]['archive'] = current_paths.get('archive', '')
            new_config['paths'][env_lower]['temp'] = current_paths.get('temp', '')
            
            if settings.save_config(new_config):
                st.success("✅ 저장되었습니다! 새로고침합니다.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ 저장 실패")

        st.divider()
        st.info(f"Current Mode: **{selected_env}**")
        st.code(f"Inbox: {inbox_val}")
    
    tab1, tab2 = st.tabs(["📝 신규 파일 등록", "⚡️ 작업 처리"])
    
    # ==========================================
    # Tab 1: 신규 파일 등록 (Registration)
    # ==========================================
    with tab1:
        st.header("신규 영상 등록")
        
        col_type, col_file = st.columns([1, 2])
        
        with col_type:
            sheet_type_options = {
                'testimony': '간증영상 (Testimony)', 
                'mission_news': '해외선교소식 (Mission News)'
            }
            selected_type_key = st.radio(
                "작업 유형 선택", 
                list(sheet_type_options.keys()), 
                format_func=lambda x: sheet_type_options[x]
            )
            
        with col_file:
            # Refresh button (Streamlit auto-reruns on click, so just a button is enough to trigger script re-execution)
            if st.button("🔄 파일 목록 새로고침"):
                pass
                
            inbox_files = get_inbox_files(selected_type_key)
            if not inbox_files:
                st.warning("📥 Inbox에 파일이 없습니다.")
                selected_file = None
            else:
                selected_file = st.selectbox("파일 선택", inbox_files)
        
        if selected_file:
            st.divider()
            
            # Initialize MediaProcessor
            mp = media.MediaProcessor()
            
            # 2-Column Layout for Preview & Meta Input
            meta_col, preview_col = st.columns([1.5, 1])
            
            with preview_col:
                st.subheader("📺 미리보기 (2초 지점)")
                # Show thumbnail logic
                folder_name = settings.config['google_sheet']['subfolders'][selected_type_key]
                file_path = os.path.join(settings.paths['inbox'], folder_name, selected_file)
                
                if st.button("📸 미리보기 생성 (2초 / 10초)"):
                    with st.spinner("미리보기 추출 중..."):
                        p1_path = mp.capture_frame(file_path, timestamp=2.0)
                        p2_path = mp.capture_frame(file_path, timestamp=10.0)
                        st.session_state['preview_paths'] = [p1_path, p2_path]
                        st.session_state['preview_idx'] = 0 # Reset to first image
                
                # Render Previews (Carousel Style)
                if 'preview_paths' in st.session_state and st.session_state['preview_paths']:
                    paths = st.session_state['preview_paths']
                    if 'preview_idx' not in st.session_state:
                         st.session_state['preview_idx'] = 0
                    
                    p_idx = st.session_state['preview_idx']
                    max_p = len(paths) - 1
                    
                    # Navigation Callbacks
                    def prev_preview(): st.session_state['preview_idx'] -= 1
                    def next_preview(): st.session_state['preview_idx'] += 1
                    
                    # Nav UI
                    pc1, pc2, pc3 = st.columns([1, 2, 1])
                    with pc1:
                        st.button("⬅️", key="p_prev", disabled=(p_idx <= 0), on_click=prev_preview)
                    with pc3:
                        st.button("➡️", key="p_next", disabled=(p_idx >= max_p), on_click=next_preview)
                        
                    # Display Image
                    current_p = paths[p_idx]
                    captions = ["2초 지점 (인트로)", "10초 지점 (본문)"]
                    
                    with pc2:
                        st.caption(f"{captions[p_idx]} ({p_idx+1}/{len(paths)})")

                    if current_p and os.path.exists(current_p):
                        st.image(current_p, use_column_width=True)
                    else:
                        st.error("이미지 로드 실패")

                st.divider()
                st.subheader("🖼️ AI 썸네일 추천 (9장)")
                if st.button("🤖 썸네일 후보 생성 (AI 추천)"):
                    with st.spinner("영상 전체를 분석하여 최적의 프레임을 추출합니다..."):
                        candidates = mp.create_thumbnail_candidates(file_path)
                        if candidates:
                            # Store in session state to persist selection
                            st.session_state['thumb_candidates'] = candidates
                        else:
                            st.error("썸네일 후보 생성 실패")
                            
                # Display Candidates if they exist
                # Display Candidates (Carousel Style)
                if 'thumb_candidates' in st.session_state:
                    candidates = st.session_state['thumb_candidates']
                    if 'thumb_idx' not in st.session_state:
                        st.session_state['thumb_idx'] = 0
                        
                    current_idx = st.session_state['thumb_idx']
                    max_idx = len(candidates) - 1
                    
                    # Navigation Callbacks
                    def prev_thumb():
                        st.session_state['thumb_idx'] -= 1
                    def next_thumb():
                        st.session_state['thumb_idx'] += 1
                        
                    # Navigation Buttons
                    col_prev, col_info, col_next = st.columns([1, 2, 1])
                    with col_prev:
                        st.button("⬅️ 이전", key="btn_prev", disabled=(current_idx <= 0), on_click=prev_thumb)
                    with col_next:
                        st.button("다음 ➡️", key="btn_next", disabled=(current_idx >= max_idx), on_click=next_thumb)
                    with col_info:
                        st.markdown(f"<h4 style='text-align: center;'>후보 {current_idx + 1} / {len(candidates)}</h4>", unsafe_allow_html=True)

                    # Large Image Display
                    current_path = candidates[current_idx]
                    if os.path.exists(current_path):
                        # Force refresh by reading file manually or just rely on Streamlit
                        
                        # Web-Based Cropper Integration
                        st.write("---")
                        st.markdown("#### ✂️ 썸네일 편집 (크롭)")
                        

                        
                        # Load image for cropping
                        img = Image.open(current_path)
                        
                        # Cropper
                        # aspect_ratio=(4, 3) enforces the ratio
                        cropped_img = st_cropper(img, realtime_update=True, box_color='#0000FF', aspect_ratio=(4, 3), key=f"cropper_{current_idx}")
                        
                        # Preview Result
                        st.markdown("##### 🖼️ 편집 결과 미리보기")
                        st.image(cropped_img, use_column_width=True)
                        
                        if st.button("💾 편집본 저장 & 선택", key=f"save_crop_{current_idx}", type="primary"):
                            # Save cropped image
                            crop_save_path = os.path.join(settings.paths['temp'], f"cropped_{os.path.basename(current_path)}")
                            cropped_img.save(crop_save_path)
                            
                            st.session_state['selected_thumb'] = crop_save_path
                            st.session_state['use_uploaded_thumb'] = True # Treat as manual upload/override
                            st.success("✅ 편집된 썸네일이 선택되었습니다!")
                            st.balloons()
                            
                        st.info("💡 파란색 박스를 조절하여 원하는 영역을 선택하세요. 비율은 4:3으로 고정됩니다.")

                        # Selection Button
                        st.divider()
                        if st.button(f"✅ 이 사진 선택 (후보 {current_idx+1})", key="btn_select_current", type="primary", use_container_width=True):
                            st.session_state['selected_thumb'] = current_path
                            st.session_state['use_uploaded_thumb'] = False 
                            st.success(f"후보 {current_idx + 1}번이 선택되었습니다!")
                    else:
                        st.warning("이미지 파일을 찾을 수 없습니다.")

                st.divider()
                st.subheader("📤 직접 수정본 업로드 (옵션)")
                uploaded_thumb = st.file_uploader("수정된 썸네일이 있다면 업로드하세요 (JPG/PNG)", type=['jpg', 'jpeg', 'png'])
                
                # Auto-Crop Option
                auto_crop = st.checkbox("자동 자르기 (자막 제거 + 4:3) 적용", value=False, help="체크하면 하단 25%를 잘라냅니다. 자막 위치가 일정하지 않다면 체크 해제하세요.")
                st.session_state['auto_crop_enabled'] = auto_crop

                if uploaded_thumb:
                    # Save Uploaded File
                    temp_up_path = os.path.join(settings.paths['temp'], f"upload_{uploaded_thumb.name}")
                    with open(temp_up_path, "wb") as f:
                        f.write(uploaded_thumb.getbuffer())
                    
                    st.image(temp_up_path, caption="업로드된 썸네일", width=300)
                    st.session_state['selected_thumb'] = temp_up_path
                    st.session_state['use_uploaded_thumb'] = True
                    st.success("업로드된 파일을 썸네일로 사용합니다.")
                                
                if 'selected_thumb' in st.session_state:
                    st.info(f"선택됨: {os.path.basename(st.session_state['selected_thumb'])}")
            with meta_col:
                st.subheader("📋 메타데이터 입력")
                
                # Common Fields
                date_val = st.date_input("방송 일자", datetime.now())
                
                # Country / Region
                country_map = settings.config.get('country_map', {})
                country_list = sorted(list(set(country_map.keys())))
                
                c_col1, c_col2 = st.columns(2)
                with c_col1:
                    country_input = st.selectbox("국가 선택", ["직접 입력"] + country_list)
                    if country_input == "직접 입력":
                        country_final = st.text_input("국가명 직접 입력")
                    else:
                        country_final = country_input
                
                with c_col2:
                    # Auto-detect region
                    region_detected = country_map.get(country_final, country_final)
                    region_final = st.text_input("지역 (자동입력)", value=region_detected)

                name_val = st.text_input("이름 (또는 발표자)")
                
                # Type Specific Fields
                extra_data = {}
                if selected_type_key == 'testimony':
                    with st.expander("추가 정보 (간증)", expanded=True):
                        ec1, ec2 = st.columns(2)
                        extra_data['city'] = ec1.text_input("도시")
                        extra_data['age'] = ec2.text_input("나이")
                        extra_data['gender'] = ec1.selectbox("성별", ["남", "여", "기타"])
                        extra_data['name_en'] = ec2.text_input("이름(영문)")
                elif selected_type_key == 'mission_news':
                    with st.expander("추가 정보 (선교소식)", expanded=True):
                        extra_data['manager'] = st.text_input("담당자")

                # Register Button with Debounce Logic
                if 'is_registering' not in st.session_state:
                    st.session_state['is_registering'] = False
                
                def on_register_click():
                    st.session_state['is_registering'] = True

                if st.button("✅ 등록하기 (이름변경 + 시트추가)", type="primary", disabled=st.session_state['is_registering'], on_click=on_register_click):
                    # Logic is handled below, driven by the session state flag 
                    pass
                
                if st.session_state['is_registering']:
                    if not name_val:
                        st.error("이름을 입력해주세요!")
                        st.session_state['is_registering'] = False
                    else:
                        try:
                            # 1. Rename File Logic
                            formatted_date = date_val.strftime("%y%m%d") # 250101
                            
                            # Apply Naming Rules (Unified)
                            if selected_type_key == 'testimony':
                                new_filename = f"{region_final}_{formatted_date}_{name_val}.mp4"
                            elif selected_type_key == 'mission_news':
                                new_filename = f"{formatted_date}_해외선교소식_{region_final}_{name_val}.mp4"
                            else:
                                new_filename = f"{formatted_date}_기타_{country_final}_{name_val}.mp4"
                                
                            # Perform Rename
                            inbox_dir = os.path.dirname(file_path)
                            new_path = os.path.join(inbox_dir, new_filename)
                            
                            if file_path != new_path:
                                os.rename(file_path, new_path)
                                log(f"기존 파일명 변경 완료: {new_filename}")
                            
                            # 1.5 Auto-Save Thumbnail (if selected)
                            if 'selected_thumb' in st.session_state and st.session_state['selected_thumb']:
                                thumb_src = st.session_state['selected_thumb']
                                thumb_dst = os.path.splitext(new_path)[0] + ".jpg"
                                
                                # Check Auto-Crop Preference
                                do_crop = st.session_state.get('auto_crop_enabled', False)
                                use_uploaded = st.session_state.get('use_uploaded_thumb', False)
                                
                                import shutil
                                if do_crop and not use_uploaded:
                                    log(f"썸네일 자동 가공 적용 중... ({thumb_dst})")
                                    processed_path = mp.process_thumbnail_4_3(thumb_src, thumb_dst)
                                    if not processed_path:
                                        shutil.copy(thumb_src, thumb_dst)
                                else:
                                    shutil.copy(thumb_src, thumb_dst)
                                    
                                log(f"썸네일 저장 완료: {os.path.basename(thumb_dst)}")
                            
                            # 2. Upload to Sheet
                            gsheet = get_gsheet_manager()
                            
                            # Prepare Args
                            args = {
                                'date': date_val.strftime("%Y. %m. %d"),
                                'country': country_final,
                                'region': region_final, 
                                'name': name_val,
                                'filename': new_filename
                            }
                            # Merge Extra
                            args.update(extra_data)
                            
                            # Pass as kwargs
                            gsheet.add_new_row(selected_type_key, **args)
                            st.success(f"🎉 등록 완료! ({new_filename})")
                            st.balloons()
                            
                            # Completion Reset
                            st.session_state['is_registering'] = False
                            time.sleep(1)
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"오류 발생: {e}")
                            st.session_state['is_registering'] = False
                            log(f"Error details: {e}") # Log error for debugging


    # ==========================================
    # Tab 2: 작업 처리 (Processing)
    # ==========================================
    with tab2:
        st.header("⏳ 대기 중인 작업")
        
        col_refresh, col_process = st.columns([1, 4])
        with col_refresh:
            if st.button("🔄 목록 불러오기"):
                st.session_state.pending_jobs = load_pending_jobs()

        if 'pending_jobs' in st.session_state and st.session_state.pending_jobs:
            # Sync selection state to session data if needed (skip for now, rely on force reset)
            
            # Helper to ensure 'selected' key exists
            if 'selected' not in st.session_state.pending_jobs[0]:
                for job in st.session_state.pending_jobs:
                    job['selected'] = job.get('selected', True)

            
            # Helper: Toggle All Callback
            def toggle_all():
                new_val = st.session_state.select_all_checkbox
                for job in st.session_state.pending_jobs:
                    job['selected'] = new_val
                st.session_state.data_editor_key += 1
            
            # Checkbox for Select All (Placed above the table)
            # Default value is True, but we sync it with the first item if available to be somewhat smart, 
            # or just default to True. Let's default to True as per user workflow.
            st.checkbox("전체 선택 (Select All)", value=True, key="select_all_checkbox", on_change=toggle_all)

            # Convert to DataFrame
            df = pd.DataFrame(st.session_state.pending_jobs)
            
            # Map 'selected' -> '선택' for UI
            df.rename(columns={'selected': '선택'}, inplace=True)
            
            # Define column config for better display
            column_config = {
                "선택": st.column_config.CheckboxColumn("선택", width="small"),
                "data": st.column_config.TextColumn("메타데이터 (JSON)", help="전체 데이터"),
                "file_name": "파일명",
                "type": "유형",
                "status": "상태",
                "index": "Sheet Row"
            }
            
            # Reorder cols to put '선택' first
            cols = ['선택'] + [c for c in df.columns if c != '선택']
            df = df[cols]

            # Show Data Editor
            edited_df = st.data_editor(
                df,
                column_config=column_config,
                disabled=["index", "type", "file_name", "status", "data"], # Only '선택' is editable
                hide_index=True,
                use_container_width=True,
                key=f"editor_{st.session_state.data_editor_key}"
            )
            
            with col_process:
                # Count selected
                selected_rows = edited_df[edited_df['선택']]
                count = len(selected_rows)
                
                st.divider()
                if st.button(f"🚀 작업 시작 ({count}개 선택됨)", type="primary", disabled=(count == 0)):
                    # Extract original job objects based on selection
                    # (To preserve original data types and structure)
                    # We assume DataFrame index matches list index 0..N
                    selected_indices = selected_rows.index.tolist()
                    
                    # Filter pending_jobs list
                    original_jobs = st.session_state.pending_jobs
                    jobs_to_run = [original_jobs[i] for i in selected_indices if i < len(original_jobs)]
                    
                    if not jobs_to_run:
                        st.warning("선택된 작업이 없습니다.")
                    else:
                        process_jobs(jobs_to_run)
        else:
            st.info("목록을 불러와주세요.")
            
        # Log Window
        st.subheader("📜 실행 로그")
        log_container = st.container()
        if st.session_state.logs:
            st.code("\n".join(st.session_state.logs[-20:])) # Show last 20 logs

# ...


# Caching GSheet Connection
@st.cache_resource
def get_gsheet_manager():
    return GSheetManager()

def load_pending_jobs():
    gsheet = get_gsheet_manager()
    
    jobs = []
    # Fetch Testimony
    rows_t = gsheet.get_pending_rows('testimony')
    for r in rows_t:
        r['type'] = 'testimony'
        r['selected'] = True
        jobs.append(r)
        
    # Fetch Mission News
    rows_m = gsheet.get_pending_rows('mission_news')
    for r in rows_m:
        r['type'] = 'mission_news'
        r['selected'] = True
        jobs.append(r)
        
    log(f"총 {len(jobs)}개의 대기 작업을 찾았습니다.")
    return jobs

def process_jobs(jobs):
    # Initialize Service with Callbacks
    from src.services.job_processor import JobProcessor
    
    # Define Callbacks to update Streamlit UI
    def log_callback(msg):
        log(msg)
        
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    def status_callback(msg):
        status_text.text(msg)
        
    def progress_callback(current, total):
        progress_bar.progress(current / total)

    processor = JobProcessor(log_callback=log_callback, status_callback=status_callback)
    
    # Run
    processor.process_jobs(jobs, progress_callback=progress_callback)
    
    status_text.text("모든 작업이 완료되었습니다.")
    st.balloons()


if __name__ == "__main__":
    main()
