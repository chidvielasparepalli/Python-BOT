# Python-BOT
An ultra-fast, state-aware automated bot powered by Gemini AI that solves CCBP programming assignments, bypasses paste protection, and handles multiple languages (Python, JS, Java, C++, SQL, HTML/CSS) with zero manual intervention.

# NIAT CCBP Assignment Solver Bot 🚀

An intelligent, high-speed automation bot designed to solve programming assignments on the CCBP portal. Powered by Google Gemini AI, it automatically extracts coding problems, generates correct solutions in any target language, bypasses paste protection, submits, and tracks progress across thousands of assignments.

## ✨ Features

- ⚡ **Turbo Speed Mode**: State-aware filter checks prevent redundant navigation delays, enabling rapid completion of 1800+ assignments.
- 🧠 **Multi-Language AI Engine**: Automatically detects the expected programming language (Python, JavaScript, Java, C++, SQL, HTML/CSS) and solves the questions with high accuracy.
- 🔓 **6-Method Paste Bypass**: Overcomes paste restrictions via Monaco Editor APIs, Chrome DevTools Protocol (CDP) direct injection, execCommand, and fallback keystroke typing.
- 📊 **State-Aware Filters**: Automatically checks and keeps `In Progress` and `Not Attempted` assignments active without toggling them off.
- 💾 **Progress Persistence**: Tracks completed and failed assignments in a local JSON state, allowing seamless restarts.

## 🛠️ Tech Stack

- **Automation**: Playwright (Python)
- **AI Model**: Google Gemini API (`gemini-2.5-flash`, `gemini-2.0-flash`)
- **Backend/Scripting**: Python 3.10+
- **Environment**: Chrome DevTools Protocol (CDP)

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.10+ and Chrome browser installed.

### 2. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/your-username/niat-assignment-bot.git
cd niat-assignment-bot
python -m venv venv
source venv/Scripts/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
playwright install chrome
