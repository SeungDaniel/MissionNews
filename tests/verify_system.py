
import sys
import os
import shutil

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config_loader import settings

def check_structure():
    print("\n[1] Checking Directory Structure...")
    paths = settings.paths
    required_dirs = [paths['inbox'], paths['archive'], paths['temp']]
    
    for d in required_dirs:
        if os.path.exists(d):
            print(f"✅ Exists: {d}")
        else:
            print(f"⚠️ Missing: {d} (Will try to create if needed)")

def check_dependencies():
    print("\n[2] Checking Dependencies...")
    try:
        import streamlit_cropper
        print("✅ streamlit-cropper is installed.")
    except ImportError:
        print("❌ streamlit-cropper is MISSING!")
        
    try:
        from PIL import Image
        print("✅ Pillow is installed.")
    except ImportError:
        print("❌ Pillow is MISSING!")

def check_modules():
    print("\n[3] Checking Modules Initialization...")
    try:
        from src.services.job_processor import JobProcessor
        processor = JobProcessor()
        print("✅ JobProcessor initialized.")
        
        # Check speaker map externalization
        if "정경화" in processor.speaker_map:
             print("✅ Config Externalization Verified (Speaker Map loaded).")
        else:
             print("⚠️ Config Externalization Issue: Speaker Map empty?")
             
    except Exception as e:
        print(f"❌ Module Init Failed: {e}")

def main():
    print("=== System Verification Start ===")
    check_structure()
    check_dependencies()
    check_modules()
    print("=== System Verification End ===")

if __name__ == "__main__":
    main()
