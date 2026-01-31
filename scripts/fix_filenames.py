import os
import re
import shutil

# Target Directory (Recursive Scan)
TARGET_DIR = "./data/archive_mock"

def fix_filenames():
    print("="*50)
    print(f"📂 파일명 일괄 변경 도구 (Date_Region -> Region_Date)")
    print(f"   Target: {TARGET_DIR} (Recursive)")
    print("="*50)

    if not os.path.exists(TARGET_DIR):
        print(f"❌ 폴더를 찾을 수 없습니다: {TARGET_DIR}")
        return

    count = 0
    # Regex: Starts with 6-digit date (e.g., 250101_...)
    pattern = re.compile(r"^(\d{6})_(.+)$")

    for root, dirs, files in os.walk(TARGET_DIR):
        for filename in files:
            if filename.startswith('.'): continue
            # Target media and artifacts
            if not filename.lower().endswith(('.mp4', '.jpg', '.jpeg', '.txt', '.png')): continue

            match = pattern.match(filename)
            if match:
                date_part = match.group(1)
                rest_part = match.group(2) # e.g., "인도_이름.mp4" or "해외선교소식_아프리카_이름.mp4"
                
                new_filename = None
                
                # Case 1: Mission News (Remove '해외선교소식' tag if present)
                if rest_part.startswith("해외선교소식_"):
                    # pattern: 250101_해외선교소식_Region_Name.mp4
                    # target: Region_250101_Name.mp4
                    remainder = rest_part.replace("해외선교소식_", "", 1)
                    parts = remainder.split('_', 1)
                    if len(parts) >= 2:
                        region = parts[0]
                        name = parts[1]
                        new_filename = f"{region}_{date_part}_{name}"
                    else:
                        # Fallback if split fails
                        new_filename = f"{remainder}_{date_part}.mp4"
                        
                # Case 2: Standard (Testimony or cleaned Mission News)
                else:
                    # pattern: 250101_Region_Name.mp4
                    # target: Region_250101_Name.mp4
                    parts = rest_part.split('_', 1)
                    if len(parts) >= 2:
                        region = parts[0]
                        name = parts[1]
                        new_filename = f"{region}_{date_part}_{name}"
                    else:
                        new_filename = f"{parts[0]}_{date_part}.mp4"

                if new_filename:
                    old_path = os.path.join(root, filename)
                    new_path = os.path.join(root, new_filename)
                    
                    if filename != new_filename:
                        try:
                            os.rename(old_path, new_path)
                            print(f"   ✅ Rename: {filename} -> {new_filename}")
                            count += 1
                        except Exception as e:
                            print(f"   ❌ Error renaming {filename}: {e}")

    print("-" * 50)
    print(f"🎉 총 {count}개 파일 변경 완료.")

if __name__ == "__main__":
    fix_filenames()
