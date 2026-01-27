import sys
import os
import time
import shutil
import subprocess
import argparse

# 프로젝트 루트 경로를 path에 추가하여 모듈 import가 가능하게 함
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config_loader import settings
from src.modules.gsheet import GSheetManager, MockGSheetManager
from src.modules.media import MediaProcessor
from src.modules.api_client import APIClient
from src.modules.nas_manager import NASManager
from src.modules.stt_module import ServerSTT
from src.modules.telegram_bot import TelegramBot

def run_registration(settings, gsheet, media):
    # ---------------------------------------------------------
    # [Step 0] 신규 파일 등록 (Interactive Mode)
    # ---------------------------------------------------------
    print("\n🔍 신규 파일 스캔 중 (Inbox)...")
    
    # 서브폴더를 시트 유형에 매핑
    # config: subfolders: { testimony: "Testimony", ... }
    # 역으로 조회: "Testimony" -> "testimony"
    folder_to_sheet = {v: k for k, v in settings.gsheet_config.get('subfolders', {}).items()}
    
    for subfolder_name, sheet_type in folder_to_sheet.items():
        inbox_dir = os.path.join(settings.paths['inbox'], subfolder_name)
        if not os.path.exists(inbox_dir): continue
        
        # 1. 시트에 등록된 파일 목록 가져오기
        registered_files = gsheet.get_registered_files(sheet_type)
        
        # 2. 로컬 파일 스캔 (.mp4)
        local_files = [f for f in os.listdir(inbox_dir) if f.lower().endswith('.mp4')]
        
        for f in local_files:
            # 시트에 없으면 등록 대상
            if f not in registered_files:
                print(f"\n✨ 새로운 파일 발견: {f} ({sheet_type})")
                
                # (1) 미리보기 생성 및 열기
                video_path = os.path.join(inbox_dir, f)
                duration = media._get_duration(video_path) # 내부 메서드 호출
                
                # 2초, 10초 듀얼 프리뷰
                p1_path = media.capture_frame(video_path, timestamp=2.0)
                p2_path = media.capture_frame(video_path, timestamp=10.0)
                
                previews = [p for p in [p1_path, p2_path] if p]
                
                if previews:
                    try:
                        subprocess.run(['open'] + previews)
                    except Exception:
                        pass
                
                # (2) 사용자 입력 (상세 정보) - Type Selection First
                print(">> 정보를 입력해주세요.")
                print("   [1] 간증 영상 (상세 정보)")
                print("   [2] 선교 소식 (기본 정보)")
                mode = input("   🔹 선택 (1/2): ").strip()
                
                # 잘못된 입력이면 현재 폴더의 기본 유형으로 설정하거나 강제할 수 있음
                # 사용자의 입력을 우선하되 검증
                if mode == '1':
                    target_sheet_type = 'testimony'
                elif mode == '2':
                    target_sheet_type = 'mission_news'
                else:
                    # 감지된 폴더 유형으로 대체
                    target_sheet_type = sheet_type 
                
                print(f"   📝 입력 모드: {'간증 영상' if target_sheet_type == 'testimony' else '선교 소식'}")
                print(f">> (팝업된 미리보기를 참고하세요)")
                
                date = input("   📅 방송 날짜 (YYMMDD): ").strip()
                if not date: 
                    print("   ⚠️ 날짜 필수! 건너뜁니다.")
                    continue 
                
                country = input("   🌍 국가: ").strip()
                if not country: country = "Unknown"

                # 국가 매핑 조회
                country_map = settings.config.get('country_map', {})
                region_tag = country_map.get(country, country) # 시트에 없으면 국가명 그대로 사용
                
                name = input("   👤 이름(발표자): ").strip()
                if not name: name = "Unknown"

                # 추가 정보 입력 (간증만 해당 + 선교소식 일부)
                extra_data = {}
                
                # 공통: 러닝타임 계산 (분:초)
                try:
                    m, s = divmod(int(duration), 60)
                    extra_data['runtime'] = f"{m}:{s:02d}"
                    print(f"   ⏱️  러닝타임 자동계산: {extra_data['runtime']}")
                except:
                    extra_data['runtime'] = ""

                if target_sheet_type == 'testimony':
                    # [Fix] C열(분류)는 Region Tag 자동 입력
                    extra_data['region'] = region_tag 
                    
                    extra_data['city'] = input("   🏙️  도시: ").strip()
                    extra_data['age'] = input("   🔢 나이: ").strip()
                    extra_data['gender'] = input("   ⚧️  성별: ").strip()
                    extra_data['name_en'] = input("   🔤 이름(영문): ").strip()
                    extra_data['category'] = input("   🔖 구분: ").strip()
                elif target_sheet_type == 'mission_news':
                    extra_data['manager'] = input("   🙋 담당자: ").strip()
                    # C열 '국가분류'에 Region Tag 자동 입력
                    extra_data['region'] = region_tag

                # (3) 파일명 변경 (표준화)
                # 규칙: 지역태그_날짜_이름.mp4
                # (Testimony, Mission News 모두 동일한 포맷 적용)
                new_filename = f"{region_tag}_{date}_{name}.mp4"
                new_path = os.path.join(inbox_dir, new_filename)
                
                if f != new_filename:
                    if os.path.exists(new_path):
                         print(f"   ⚠️ 이미 존재하는 파일명입니다: {new_filename} (Skip)")
                         continue
                    os.rename(video_path, new_path)
                    print(f"   ↪️  파일명 변경: {f} -> {new_filename}")
                
                # (4) 시트 등록 (확장 데이터 포함)
                # 여기서 target_sheet_type 사용
                gsheet.add_new_row(target_sheet_type, date, country, name, new_filename, **extra_data)
                print(f"   ✅ 시트 등록 완료! ({target_sheet_type})")


def run_processing(settings, gsheet, media, api_client, stt, nas, telegram):
    # 2. 작업 스캔
    target_tabs = ['testimony', 'mission_news']
    pending_jobs = []

    for tab in target_tabs:
        jobs = gsheet.get_pending_rows(sheet_type=tab)
        pending_jobs.extend(jobs)
    
    print(f"📋 총 {len(pending_jobs)}개의 대기 작업을 발견했습니다.")

    # 3. 작업 루프
    for job in pending_jobs:
        row_idx = job['index']
        original_filename = job['file_name']
        sheet_type = job['type']
        meta = job['data']
        
        print(f"\n▶️ 작업 시작: {original_filename} (Row {row_idx})")
        
        # [변경] Inbox 내 서브폴더 적용 (Testimony / MissionNews)
        subfolders = settings.gsheet_config.get('subfolders', {})
        subfolder_name = subfolders.get(sheet_type, "")
        
        inbox_dir = os.path.join(settings.paths['inbox'], subfolder_name)
        inbox_path = os.path.join(inbox_dir, original_filename)

        if not os.path.exists(inbox_dir):
            print(f"❌ 폴더 없음: {inbox_dir}")
            continue
            
        inbox_path = os.path.join(inbox_dir, original_filename)

        # (1) Inbox 내에서 파일명 변경 ('240101_국가_이름.mp4' 형식)
        # 메타데이터 기반 새 이름 생성 (구글 시트 헤더: 방송 일자, 국가, 이름(한글))
        import re
        raw_date = str(meta.get('방송 일자', ''))
        # 숫자만 추출 (2025. 03. 22 (토) -> 20250322)
        digits = re.sub(r'[^0-9]', '', raw_date)
        
        if len(digits) == 8: # 20250322
            yymmdd = digits[2:] # 250322
        elif len(digits) == 6: # 250322
            yymmdd = digits
        else:
            yymmdd = '240101' # Default fallback

        # NAS Archive를 위해 meta 날짜 표준화
        meta['방송 일자'] = yymmdd 

        country = meta.get('국가', 'Unknown')
        name = meta.get('이름(한글)', 'Unknown')
        region = meta.get('지역', country) # Default to Country if Region is empty

        # [New] 스피커별 지역 매핑 규칙 (해외선교소식)
        if sheet_type == 'mission_news':
            speaker_map = {
                "정경화": "필리핀_루손",
                "배중기": "필리핀_비사야",
                "고엄수": "필리핀_민다나오",
                "정명준": "멕중남미"
            }
            if name in speaker_map:
                region = speaker_map[name]
                print(f"   ℹ️  지역 자동 매핑: {name} -> {region}")

        if sheet_type == 'testimony':
            new_filename = f"{region}_{yymmdd}_{name}.mp4"
        elif sheet_type == 'mission_news':
            new_filename = f"{yymmdd}_해외선교소식_{region}_{name}.mp4"
        else:
            new_filename = f"{yymmdd}_기타_{country}_{name}.mp4"

        renamed_inbox_path = os.path.join(inbox_dir, new_filename)

        # [Robust Check] 원본 파일이 없으면, 이미 변경된 파일이 있는지 확인
        if not os.path.exists(inbox_path):
            if os.path.exists(renamed_inbox_path):
                print(f"   ℹ️  이미 변경된 파일 발견: {new_filename} (Proceeding)")
                inbox_path = renamed_inbox_path # 포인터 변경
            else:
                print(f"❌ 파일 없음: {original_filename}")
                print(f"   (확인된 경로: {inbox_path})")
                print(f"   (대체 경로: {renamed_inbox_path})")
                
                gsheet.update_status(sheet_type, row_idx, "에러", error_msg="File Not Found (Inbox)")
                continue

        try:
            
            # [Safe Rename] 원본과 타겟이 다를 때만 이름 변경
            if inbox_path != renamed_inbox_path:
                print(f"   [1/6] 파일명 변경: {os.path.basename(inbox_path)} -> {new_filename}")
                os.rename(inbox_path, renamed_inbox_path)
            else:
                print(f"   [1/6] 파일명 변경 생략 (이미 일치): {new_filename}")
            
            # (2) 오디오 추출 (변경된 파일에서)
            print("   [2/6] 오디오 추출 중...")
            audio_path = media.extract_audio(renamed_inbox_path)
            
            # (3) STT & AI 요약
            print("   [3/6] AI 분석 (STT -> Server)...")
            full_text = stt.transcribe(audio_path)
            summary_text = api_client.analyze_text(full_text, prompt_type=sheet_type)
            print(f"     ㄴ 요약 완료: {summary_text[:30]}...")
            
            # 텔레그램 알림 발송
            # 텔레그램 알림 발송
            if sheet_type == 'testimony':
                header = f"🕊️ **[간증] {job['data'].get('방송 일자', '')} {region} - {name}**"
            elif sheet_type == 'mission_news':
                header = f"🌍 **[선교소식] {job['data'].get('방송 일자', '')} {region} - {name}**"
            else:
                header = f"📢 **[{job['data'].get('방송 일자', '')} {region} - {name}]**"

            msg = f"{header}\n\n{summary_text}"
            telegram.send_message(msg)

            # (4) 썸네일 생성 (4:3 크롭 & 자막 제거)
            print("   [4/6] 썸네일 생성 중 (4:3, 자막 제거)...")
            
            # 2초 지점(타이틀/인물) 다시 캡처 (원본 소스)
            thumb_source = media.capture_frame(renamed_inbox_path, timestamp=2.0)
            
            if thumb_source:
                # 썸네일도 파일명 규칙 따름 (.jpg)
                thumb_new_name = os.path.splitext(new_filename)[0] + ".jpg"
                final_thumb_path = os.path.join(settings.paths['temp'], thumb_new_name)
                
                # 4:3 크롭 & 하단 자막 제거 적용
                result = media.process_thumbnail_4_3(thumb_source, final_thumb_path)
                
                if result:
                    print(f"     ㄴ 썸네일 생성 완료: {thumb_new_name}")
                else:
                    print("     ⚠️ 썸네일 변환 실패")
                    final_thumb_path = None # 마킹
            else:
                print("     ⚠️ 썸네일 소스 캡처 실패")
                final_thumb_path = None

            # [복구] STT 결과 텍스트 파일 저장 (Archive Backup X, Temp Only O)
            txt_filename = os.path.splitext(new_filename)[0] + ".txt"
            txt_path = os.path.join(settings.paths['temp'], txt_filename)
            try:
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(f"방송일자: {yymmdd}\n")
                    f.write(f"제목: {new_filename}\n")
                    f.write("-" * 20 + "\n")
                    f.write(summary_text + "\n")
                    f.write("-" * 20 + "\n\n")
                    f.write("[전체 자막]\n")
                    f.write(full_text)
                print(f"     ㄴ 텍스트 생성 완료: {txt_filename}")
            except Exception as e:
                print(f"     ⚠️ 텍스트 저장 실패: {e}")

            # (5) NAS 아카이빙 (영상 + 썸네일 + 텍스트) -> [변경] archive_mock/20YYMMDD
            print("   [5/6] 아카이브 저장 (Mock)...")
            
            # Destination Folder
            dest_folder = os.path.join(settings.paths['archive'], f"20{yymmdd}")
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder, exist_ok=True)
            
            # 1. Text
            shutil.copy(txt_path, os.path.join(dest_folder, txt_filename))
            
            # 2. Video
            video_dest_path = os.path.join(dest_folder, new_filename)
            shutil.copy(renamed_inbox_path, video_dest_path)
            
            # 3. Thumbnail
            if final_thumb_path and os.path.exists(final_thumb_path):
                thumb_dest_filename = os.path.splitext(new_filename)[0] + ".jpg"
                shutil.copy(final_thumb_path, os.path.join(dest_folder, thumb_dest_filename))
            
            print(f"     ✅ 저장 완료: {dest_folder}")

            # (6) 상태 업데이트
            gsheet.update_status(sheet_type, row_idx, "완료", new_filename=new_filename, summary_text=summary_text)
            print("✅ 모든 작업 완료!")

        except Exception as e:
            print(f"❌ 에러 발생: {e}")
            gsheet.update_status(sheet_type, row_idx, "에러", error_msg=str(e))


def main():
    """
    MNAP (Mission News Auto-Archiving System) 메인 실행 함수
    User Workflow:
    1. Inbox 영상 이름 변경
    2. 썸네일 5장 추출 -> 1장 선택 (자동: 중간 지점)
    3. 영상/사진 NAS 업로드
    """
    print("="*50)
    print("🚀 MNAP: 선교 소식 자동 아카이빙 시스템 시작")
    print(f"🌍 환경 모드: {settings.env} (경로: {settings.paths['inbox']})")
    print("="*50)
    
    if not settings:
        sys.exit(1)

    # 1. 모듈 초기화
    print("\n[Init] 모듈 초기화 중...")
    if os.path.exists(settings.gsheet_config['json_key_path']):
        gsheet = GSheetManager()
    else:
        gsheet = MockGSheetManager()
        print("⚠️ GSheet: 테스트 모드 (Mock) 실행")

    media = MediaProcessor()
    # (3) API Client (GPU Server - LLM)
    api_client = APIClient()
    # (4) NAS Manager
    nas = NASManager()
    
    # (5) STT (Server-Side)
    print("   [Init] STT 모델 로딩 중 (Server STT)...")
    print("   [Init] STT 모델 로딩 중 (Server STT)...")
    stt = ServerSTT()
    
    # (6) Telegram Bot
    telegram = TelegramBot()

    # ---------------------------------------------------------
    # [Step 1] 실행 모드 선택
    # ---------------------------------------------------------
    print("\n🎛️  작업 모드를 선택해주세요:")
    print("   [1] 🚀 전체 실행 (등록 + 작업처리)")
    print("   [2] ⚡️ 작업 처리만 실행 (STT/Archive)")
    print("   [3] 📝 신규 등록만 실행")
    
    op_mode = input("   🔹 선택 (1~3): ").strip()
    
    if op_mode not in ['1', '2', '3']:
        op_mode = '1' # Default
    
    # [Step 2] 등록 절차 (Mode 1, 3)
    if op_mode in ['1', '3']:
        run_registration(settings, gsheet, media)
        
    # [Step 3] 작업 처리 절차 (Mode 1, 2)
    if op_mode in ['1', '2']:
        run_processing(settings, gsheet, media, api_client, stt, nas, telegram)

if __name__ == "__main__":
    main()
