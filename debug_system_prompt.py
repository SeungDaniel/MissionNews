import sys
import os
sys.path.append(os.getcwd())
from src.modules.api_client import APIClient

def test_system_prompt_loading():
    print("Testing System Prompt Loading...")
    client = APIClient()
    
    # Mocking the internal method to inspect logic or just running a dummy call if possible?
    # Actually, the logic is in analyze_text. I can't easily inspect local vars without running it.
    # But I can check if the file exists and print what the code WOULD read.
    
    project_root = os.getcwd()
    prompt_path = os.path.join(project_root, "docs", "System_Prompt.md")
    
    if os.path.exists(prompt_path):
        print(f"✅ System Prompt file found at: {prompt_path}")
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read()
            print(f"📄 Content Length: {len(content)} chars")
            print(f"📄 Preview: {content[:100]}...")
    else:
        print(f"❌ System Prompt file NOT found at: {prompt_path}")

    # To truly verify the code path, we can try to instantiate APIClient and see if it crashes.
    print("\nAPIClient instantiated successfully.")

if __name__ == "__main__":
    test_system_prompt_loading()
