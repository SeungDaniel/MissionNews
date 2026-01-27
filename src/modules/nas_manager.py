import shutil
import os
import shutil
from src.config_loader import settings

class NASManager:
    def __init__(self):
        self.archive_root = settings.paths['archive']
        # Create mock archive root if in DEV mode and it doesn't exist
        if settings.env == 'DEV' and not os.path.exists(self.archive_root):
             os.makedirs(self.archive_root)

    def archive_file(self, source_path, metadata):
        """
        Moves file to: {ArchiveRoot}/YYYY/MM/{NewName}.mp4
        metadata: dict containing 'date' (YYMMDD), 'country', 'name', 'type'
        """
        # Parse Date: YYYY.MM.DD or YYMMDD -> YYYY/MM
        raw_date = str(metadata.get('방송 일자', '') or metadata.get('date', ''))
        # 2025.12.17 -> 20251217
        clean_date = raw_date.replace('.', '').replace('-', '')
        
        if len(clean_date) == 8: # 20251217
            year = clean_date[:4]
            month = clean_date[4:6]
            yymmdd = clean_date[2:]
        elif len(clean_date) == 6: # 251217
            year = "20" + clean_date[:2]
            month = clean_date[2:4]
            yymmdd = clean_date
        else:
            year = "Unknown"
            month = "Unknown"
            yymmdd = "000000"

        # Construct Target Directory
        target_dir = os.path.join(self.archive_root, year, month)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # Construct New Filename: YYMMDD_Country_Name_Type.mp4
        # Note: PRD says "YYMMDD_Country_Name_Topic.mp4", simplified here.
        new_name = f"{yymmdd}_{metadata.get('국가', 'Unknown')}_{metadata.get('이름(한글)', 'Unknown')}.mp4"
        target_path = os.path.join(target_dir, new_name)

        print(f"[NAS] Moving: {source_path} -> {target_path}")
        
        try:
            shutil.move(source_path, target_path)
            return target_path, new_name
        except Exception as e:
            print(f"Error moving file: {e}")
            raise e

    def save_thumbnail(self, thumb_path, video_target_path):
        """
        Saves thumbnail next to the archived video.
        """
        if not thumb_path or not os.path.exists(thumb_path):
            return None
            
        target_base = os.path.splitext(video_target_path)[0]
        target_thumb = target_base + ".jpg"
        
        print(f"[NAS] Saving Thumbnail: {target_thumb}")
        shutil.copy(thumb_path, target_thumb)
        return target_thumb
