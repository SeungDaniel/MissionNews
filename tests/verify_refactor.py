
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.job_processor import JobProcessor
from src.config_loader import settings

def test_refactor():
    print("1. Checking Config Loading...")
    speaker_map = settings.config.get('speaker_map')
    if speaker_map and "정경화" in speaker_map:
        print(f"✅ Config loaded successfully: {speaker_map['정경화']}")
    else:
        print("❌ Config loading failed or speaker_map missing!")
        return

    print("\n2. Instantiating JobProcessor...")
    try:
        processor = JobProcessor()
        print("✅ JobProcessor instantiated.")
        
        # Check if internal components are up
        if processor.gsheet and processor.telegram:
             print("✅ Internal modules (GSheet, Telegram) initialized.")
    except Exception as e:
        print(f"❌ JobProcessor instantiation failed: {e}")
        return

    print("\n🎉 Refactoring Verification Passed!")

if __name__ == "__main__":
    test_refactor()
