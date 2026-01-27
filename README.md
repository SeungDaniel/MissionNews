# 🎬 Evangelical Mission News Automation

**Evangelical Mission News Automation** is a system designed to streamline the processing, summarization, and archiving of mission news and testimony videos. It automates the workflow from file ingestion to AI-powered summarization and distribution via Telegram.

## 🚀 Key Features

*   **Automated Pipeline**: Detects new videos, extracts audio, and performs Speech-to-Text (STT).
*   **AI Summarization**: Generates specialized summaries using Local LLM (or OpenAI API) for Mission News and Testimonies.
*   **Multi-Format Output**: Produces `.mp4` (Video), `.mp3` (Audio), `.txt` (Summary), `.srt` (Subtitle), and `.jpg` (Thumbnail).
*   **Telegram Integration**: Automatically sends the summary, subtitle file, and notifications to a designated Telegram channel.
*   **UI Dashboard**: Provides a [Streamlit](https://streamlit.io/) web interface for monitoring jobs, manual registration, and thumbnail editing.
*   **Smart Archiving**: Automatically organizes processed files into `YYYY/MM` folder structures on NAS or local storage.

## 🛠 Tech Stack

*   **Language**: Python 3.9+
*   **Web Framework**: Streamlit
*   **AI/ML**:
    *   **STT**: Custom Server / OpenAI Whisper
    *   **LLM**: Ollama / OpenAI Compatible API
*   **Database**: Google Sheets (via `gspread`)
*   **Media Processing**: `moviepy`, `ffmpeg`
*   **Notification**: `python-telegram-bot`

## 📂 Project Structure

```bash
Evangelical/
├── app.py                  # Streamlit Web Dashboard Entry Point
├── main.py                 # (Alternative) CLI Entry Point
├── config/                 # Configuration Files
│   ├── config.yaml         # Main Config (Not committed)
│   └── config_template.yaml# Template for Config
├── src/
│   ├── modules/            # Core Modules (GSheet, STT, Telegram, etc.)
│   └── services/           # Business Logic (Job Processor)
├── docs/                   # System Prompts & Documentation
└── requirements.txt        # Python Dependencies
```

## ⚡️ Quick Start

### 1. Prerequisites
*   Python 3.9+ installed.
*   `ffmpeg` installed on the system.
*   Google Service Account JSON key (for GSheet access).

### 2. Installation
```bash
git clone https://github.com/SeungDaniel/MissionNews.git
cd MissionNews
pip install -r requirements.txt
```

### 3. Configuration
Copy the template and fill in your API keys and paths.
```bash
cp config/config_template.yaml config/config.yaml
# Edit config/config.yaml with your actual keys
```

### 4. Run Dashboard
```bash
streamlit run app.py
```

## 🔒 Security
*   Sensitive files like `config.yaml`, `.env`, and private keys are **excluded** from the repository via `.gitignore`.

## 📜 License
This project is for internal use by the Evangelical Mission Team.
