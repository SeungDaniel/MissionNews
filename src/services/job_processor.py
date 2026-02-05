import os
import shutil
import re
from datetime import datetime

from src.config_loader import settings
from src.modules import media, stt_module, api_client, nas_manager, telegram_bot
from src.modules.gsheet import GSheetManager
import traceback
import time

class JobProcessor:
    def __init__(self, log_callback=None, status_callback=None):
        """
        :param log_callback: Function to call for logging (e.g., st.write or print)
        :param status_callback: Function to call for updating status text
        """
        self.log_callback = log_callback if log_callback else print
        self.status_callback = status_callback if status_callback else lambda x: None
        
        # Initialize Modules
        self.gsheet = GSheetManager()
        self.stt = stt_module.ServerSTT()
        self.llm = api_client.APIClient()
        self.nas = nas_manager.NASManager()
        self.telegram = telegram_bot.TelegramBot()
        self.mp = media.MediaProcessor()
        
        # Load Configs
        self.inbox_base = settings.paths['inbox']
        self.subfolders = settings.config['google_sheet'].get('subfolders', {})
        self.speaker_map = settings.config.get('speaker_map', {}) # Refactoring: Read from Config

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_callback(f"[{timestamp}] {message}")

    def process_jobs(self, jobs, progress_callback=None):
        """
        Process a list of jobs.
        :param jobs: List of job dictionaries (from GSheet)
        :param progress_callback: Function accepting (current, total)
        """
        self.log("작업을 시작합니다... (Service Layer)")
        total = len(jobs)
        
        for i, job in enumerate(jobs):
            try:
                row_idx = job['index']
                original_filename = job['file_name']
                sheet_type = job['type']
                meta = job['data']
                
                self.status_callback(f"Processing ({i+1}/{total}): {original_filename}")
                self.process_single_job(job)
                
            except Exception as e:
                self.log(f"❌ 에러 발생 ({job.get('file_name')}): {e}")
                self.log(traceback.format_exc()) # 상세 에러 로그 출력
                self.gsheet.update_status(sheet_type, row_idx, "에러", error_msg=str(e))
                
            if progress_callback:
                progress_callback(i + 1, total)

    def process_single_job(self, job):
        row_idx = job['index']
        original_filename = job['file_name']
        sheet_type = job['type']
        meta = job['data']
        
        # 1. Path Setup
        folder_name = self.subfolders.get(sheet_type, "")
        inbox_dir = os.path.join(self.inbox_base, folder_name)
        inbox_path = os.path.join(inbox_dir, original_filename)
        
        if not os.path.exists(inbox_dir):
            self.log(f"❌ 폴더 없음: {inbox_dir}")
            return
            
        # 2. Filename Logic (Date Standardizing)
        raw_date = str(meta.get('방송 일자', ''))
        digits = re.sub(r'[^0-9]', '', raw_date)
        
        if len(digits) == 8: yymmdd = digits[2:]
        elif len(digits) == 6: yymmdd = digits
        else: yymmdd = '240101'
        
        country = meta.get('국가', 'Unknown')
        name = meta.get('이름(한글)', 'Unknown')
        region = meta.get('지역', country)
        
        # Mission News Speaker Map (From Config)
        if sheet_type == 'mission_news':
            if name in self.speaker_map:
                region = self.speaker_map[name]
                self.log(f"   ℹ️ 지역 자동 매핑 (Config): {name} -> {region}")

        # Construct New Filename
        if sheet_type == 'testimony':
            new_filename = f"{region}_{yymmdd}_{name}.mp4"
        elif sheet_type == 'mission_news':
            new_filename = f"{yymmdd}_해외선교소식_{region}_{name}.mp4"
        else:
            new_filename = f"{yymmdd}_기타_{country}_{name}.mp4"
            
        renamed_inbox_path = os.path.join(inbox_dir, new_filename)
        
        # Handling existing/renamed files
        file_to_process = inbox_path
        
        if not os.path.exists(inbox_path):
            if os.path.exists(renamed_inbox_path):
                self.log(f"   ℹ️ 이미 변경된 파일 발견: {new_filename}")
                file_to_process = renamed_inbox_path
            else:
                self.log(f"❌ 파일 없음: {original_filename}")
                self.gsheet.update_status(sheet_type, row_idx, "에러", error_msg="File Not Found")
                return
        else:
            # Rename if needed
            if inbox_path != renamed_inbox_path:
                os.rename(inbox_path, renamed_inbox_path)
                self.log(f"   파일명 변경: {new_filename}")
                file_to_process = renamed_inbox_path
                
        # 3. Audio Extraction
        self.log("   🔊 오디오 추출 중...")
        audio_path = self.mp.extract_audio(file_to_process)
        
        # 4. STT & Summary
        self.log("   🧠 AI 분석 중...")
        stt_result = self.stt.transcribe(audio_path)
        
        full_text = ""
        segments = []
        
        if isinstance(stt_result, dict):
            full_text = stt_result.get('text', "")
            segments = stt_result.get('segments', [])
        else:
            # Error string case
            full_text = str(stt_result)
            self.log(f"⚠️ STT 결과 형식이 예외적임: {str(stt_result)[:50]}...")

        summary_text = self.llm.analyze_text(full_text, prompt_type=sheet_type)
        
        # 5. Prepare Text Content & Save Temp File
        txt_filename = os.path.splitext(new_filename)[0] + ".txt"
        txt_path = os.path.join(settings.paths['temp'], txt_filename)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"방송일자: {yymmdd}\n")
            f.write(f"제목: {new_filename}\n")
            f.write("-" * 20 + "\n")
            f.write(summary_text + "\n")
            f.write("-" * 20 + "\n\n")
            f.write("[전체 자막]\n")
            f.write(full_text)

        # 5.5 Generate SRT (Lightweight)
        srt_path = None
        if segments:
            try:
                def seconds_to_srt_time(seconds):
                    millis = int((seconds % 1) * 1000)
                    seconds = int(seconds)
                    minutes = seconds // 60
                    hours = minutes // 60
                    minutes %= 60
                    seconds %= 60
                    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

                srt_content = ""
                for i, seg in enumerate(segments):
                    start = seconds_to_srt_time(seg.get('start', 0))
                    end = seconds_to_srt_time(seg.get('end', 0))
                    text = seg.get('text', '').strip()
                    srt_content += f"{i+1}\n{start} --> {end}\n{text}\n\n"
                
                srt_filename = os.path.splitext(new_filename)[0] + ".srt"
                srt_path = os.path.join(settings.paths['temp'], srt_filename)
                with open(srt_path, "w", encoding="utf-8") as f:
                    f.write(srt_content)
                self.log(f"   📜 자막(SRT) 생성 완료")
            except Exception as e:
                self.log(f"⚠️ SRT 생성 실패 (무시됨): {e}")

        
        # Helper for Telegram Markdown V1 Escaping
        def escape_md_field(text):
            # Escape: _ * [ ] `
            return str(text).replace('_', r'\_').replace('*', r'\*').replace('[', r'\[').replace(']', r'\]').replace('`', r'\`')
            
        safe_region = escape_md_field(region)
        safe_name = escape_md_field(name)
        
        # [수정] Summary는 LLM이 이미 Markdown 문법(*, - 등)을 사용해서 생성했으므로, 
        # 이를 이스케이프하면 포맷팅이 깨집니다. 따라서 Summary는 원본 그대로 보냅니다.
        # 단, LLM이 ** (V2 style) 대신 * (V1 style)을 쓰도록 프롬프트를 조정하는 것이 가장 좋습니다.
        # 지금은 우선 원본(summary_text)을 보냅니다.
        
        # Telegram V1 Markdown Bold is *text* not **text**
        if sheet_type == 'testimony':
            header = f"🕊️ *[간증] {yymmdd} {safe_region} - {safe_name}*"
        elif sheet_type == 'mission_news':
            header = f"🌍 *[선교소식] {yymmdd} {safe_region} - {safe_name}*"
        else:
            header = f"📢 *[{yymmdd} {safe_region} - {safe_name}]*"
            
        msg = f"{header}\n\n{summary_text}"
        self.telegram.send_message(msg)
        self.telegram.send_document(txt_path)
        
        # 7. Thumbnail
        self.log("   and 🖼 썸네일 가공 중 (자막 제거 + 4:3 크롭)...")
        
        # Check for pre-selected thumbnail
        pre_selected_thumb = os.path.splitext(file_to_process)[0] + ".jpg"
        if os.path.exists(pre_selected_thumb):
             self.log("   ✅ 사용자 선택 썸네일 사용")
             thumb_source = pre_selected_thumb
        else:
             self.log("   📸 2초 지점 자동 추출...")
             thumb_source = self.mp.capture_frame(file_to_process, timestamp=2.0)
        
        final_thumb_path = None
        if thumb_source:
            thumb_name = os.path.splitext(new_filename)[0] + ".jpg"
            final_thumb_path = os.path.join(settings.paths['temp'], thumb_name)
            
            shutil.copy(thumb_source, final_thumb_path)
            self.log(f"   ✨ 썸네일 준비 완료: {thumb_name}")

        # 8. Archive (NAS)
        self.log("   💾 아카이브 저장 중...")
        time.sleep(1.0) # 파일 잠금 해제 대기 (안전장치)
        
        dest_folder = os.path.join(settings.paths['archive'], f"20{yymmdd[:2]}", yymmdd[2:4]) # YYYY/MM
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder, exist_ok=True)
        
        # Save Text (Copy from Temp)
        shutil.copy(txt_path, os.path.join(dest_folder, txt_filename))
        
        # Save Video (Move to Archive)
        video_dest_path = os.path.join(dest_folder, new_filename)
        shutil.move(file_to_process, video_dest_path)
        self.log(f"   🚚 영상 이동 완료: Inbox -> Archive ({new_filename})")

        # Save Audio (Move/Copy .mp3)
        if audio_path and os.path.exists(audio_path):
            audio_dest_filename = os.path.splitext(new_filename)[0] + ".mp3"
            shutil.copy(audio_path, os.path.join(dest_folder, audio_dest_filename))
            # Optional: Remove temp audio if not needed elsewhere
            # os.remove(audio_path) 
        
        # Save SRT (Copy .srt)
        if srt_path and os.path.exists(srt_path):
            srt_dest_filename = os.path.splitext(new_filename)[0] + ".srt"
            shutil.copy(srt_path, os.path.join(dest_folder, srt_dest_filename))

        # Save Thumbnail
        if final_thumb_path and os.path.exists(final_thumb_path):
            thumb_dest_filename = os.path.splitext(new_filename)[0] + ".jpg"
            shutil.copy(final_thumb_path, os.path.join(dest_folder, thumb_dest_filename))
            
        self.log(f"   ✅ 저장 완료: {dest_folder}")
        
        # 8. Cleanup
        try:
            if final_thumb_path and os.path.exists(final_thumb_path):
                 os.remove(final_thumb_path)
            if txt_path and os.path.exists(txt_path):
                 os.remove(txt_path)
            if srt_path and os.path.exists(srt_path):
                 os.remove(srt_path)
            
            inbox_thumb_key = os.path.splitext(file_to_process)[0] + ".jpg"
            if os.path.exists(inbox_thumb_key):
                os.remove(inbox_thumb_key)
                
        except Exception as e:
            self.log(f"⚠️ 임시 파일 삭제 중 오류 (무시): {e}")
        
        # 9. Update Sheet
        self.gsheet.update_status(
            sheet_type,
            row_idx,
            "완료",
            new_filename=new_filename,
            summary_text=summary_text
        )

        self.log(f"✅ {name} 처리 완료!")

        # 10. Return result with file paths for download
        result_files = {
            'video': video_dest_path,
            'audio': os.path.join(dest_folder, os.path.splitext(new_filename)[0] + ".mp3"),
            'thumbnail': os.path.join(dest_folder, os.path.splitext(new_filename)[0] + ".jpg"),
            'text': os.path.join(dest_folder, txt_filename),
            'srt': os.path.join(dest_folder, os.path.splitext(new_filename)[0] + ".srt") if srt_path else None
        }
        return result_files
