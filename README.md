# Evangelical Mission Automation Project

## 📌 Project Overview
선교 소식과 간증 영상을 자동으로 수집, 요약, 분류하고 텔레그램으로 공유하는 자동화 시스템입니다.

## 📂 Project Structure
```
Evangelical/
├── app.py                  # Streamlit Dashboard (Main Entry)
├── scripts/                # Utility Tools (Debug, Fix, etc.)
├── config/                 # Configuration Files
├── src/                    # Source Code (Modules, Services)
└── docs/                   # Documentation
    ├── prompts/            # AI System Prompts
    ├── guides/             # User Manuals & Guides
    └── legacy/             # Archived Documents
```

## 🚀 Getting Started
1. **Installation**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configuration**
   - Copy `config/config_template.yaml` to `config/config.yaml`
   - Fill in your API keys and paths.
3. **Run Application**
   ```bash
   streamlit run app.py
   ```

## 🛠 Features
- **Watch Folder**: Automatically detects new videofiles in Inbox.
- **Audio Processing**: Extracts audio and performs STT (Speech-to-Text).
- **AI Summary**: Summarizes content using Local LLM with custom prompts.
- **Telegram Notification**: Sends formatted messages and files to the channel.
- **Archiving**: Organizes processed files into `YYYY/MM` folders.

## 📝 Documentation
- **[Folder Structure](docs/guides/Folder_Structure.md)**: Detailed file organization.
- **[Architecture](docs/guides/Project_Architecture.md)**: System design and data flow.
