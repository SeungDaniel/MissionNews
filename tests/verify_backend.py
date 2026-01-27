import os
import sys
import time
import subprocess
import shutil

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config_loader import settings
from src.modules.media import MediaProcessor
from src.modules.gsheet import GSheetManager

def create_dummy_video(path):
    """Creates a 5-second blank video using ffmpeg."""
    print(f"[Setup] Creating dummy video at {path}...")
    try:
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=640x480:d=5',
            '-c:v', 'libx264', '-tune', 'stillimage', '-pix_fmt', 'yuv420p',
            path
        ]
        subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"[Setup] Failed to create dummy video: {e}")
        return False

def test_media_processor():
    print("\n>>> Testing MediaProcessor...")
    mp = MediaProcessor()
    dummy_path = os.path.join(settings.paths['temp'], "test_dummy.mp4")
    
    if not create_dummy_video(dummy_path):
        print("❌ Skipped Media Tests (FFmpeg missing?)")
        return

    # 1. Capture Frame (Dual Preview logic)
    print("   [1/3] Testing capture_frame (2.0s)...")
    p1 = mp.capture_frame(dummy_path, timestamp=2.0)
    if p1 and os.path.exists(p1) and "preview" in p1:
        print(f"      ✅ Success: {os.path.basename(p1)}")
    else:
        print(f"      ❌ Failed: {p1}")

    # 2. Candidate Generation (UUID check)
    print("   [2/3] Testing create_thumbnail_candidates...")
    candidates = mp.create_thumbnail_candidates(dummy_path)
    if candidates and len(candidates) == 5:
        print(f"      ✅ Success: Generated {len(candidates)} candidates")
        print(f"      ℹ️ Sample Filename: {os.path.basename(candidates[0])}")
    else:
        print(f"      ❌ Failed: Count={len(candidates) if candidates else 0}")

    # Cleanup
    if os.path.exists(dummy_path):
        os.remove(dummy_path)

def test_gsheet_connection():
    print("\n>>> Testing GSheetManager Connection...")
    try:
        gsheet = GSheetManager()
        # Test 1: Connect (implicit in init)
        print("   [1/2] Connection to Google API...")
        if gsheet.client:
            print("      ✅ Connected successfully")
        else:
            print("      ❌ Connection returned None")
            return

        # Test 2: Fetch Rows (Read Access)
        print("   [2/2] Fetching Pending Rows (Read Test)...")
        rows = gsheet.get_pending_rows('testimony')
        print(f"      ✅ Success: Found {len(rows)} pending rows in 'testimony'")
        
        # Optional: Check 'mission_news' tabs too
        rows_m = gsheet.get_pending_rows('mission_news')
        print(f"      ✅ Success: Found {len(rows_m)} pending rows in 'mission_news'")

    except Exception as e:
        print(f"      ❌ Failed with error: {e}")

if __name__ == "__main__":
    print("=== 🛠️ Backend Verification Tool 🛠️ ===")
    print(f"Environment: {settings.config.get('environment', 'UNKNOWN')}")
    
    test_media_processor()
    test_gsheet_connection()
    
    print("\n=== End of Test ===")
