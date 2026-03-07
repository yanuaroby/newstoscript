News-to-Script Automation Engine 🎬🤖
An automated Python pipeline that transforms daily trending news into production-ready video scripts for creators and motion designers.

Overview
As a Video Editor and Motion Graphic Designer, I realized that the biggest bottleneck in content creation isn't the editing—it's the research and scripting.

This project automates the "pre-production" phase. It fetches the top 5 trending news stories, synthesizes them into a structured 5-minute video script using AI, and delivers the final result to your pocket every morning.

Key Features
Smart Scraper: Target high-authority news sources for the top 5 trending topics.

AI Script Synthesis: Transforms raw articles into engaging, 5-minute video scripts (optimized for TikTok, Reels, or YouTube).

Headless Automation: Runs entirely on GitHub Actions—no local server required.

Telegram Integration: Delivers the finished script to your mobile device at 06:00 AM daily.

Creative-First Design: Built by a designer, for designers.

Tech Stack
Language: Python 3.x

Environment: Zed Editor (Development) & GitHub Actions (Production)

AI Engine: Prototyped with Qwen 3.5 Plus (Integration ready for Claude)

Communication: Telegram Bot API

Automation: YAML-based GitHub Workflows

The Workflow
Trigger: GitHub Actions triggers a cron job every morning.

Scrape: Python scripts fetch the latest news data.

Process: The AI model analyzes the data and writes a conversational script.

Notify: The script is formatted and sent via Telegram.

Getting Started
Prerequisites
A Telegram Bot Token (from @BotFather)

GitHub Repository Secrets (for API keys and tokens)

Installation
Clone the repository:

Bash
git clone https://github.com/your-username/news-script-automation.git
Install dependencies:

Bash
pip install -r requirements.txt
Why This Exists
I am a newcomer to programming, but I am a veteran in the creative industry. This project is my contribution to the Automation Era of content creation. I believe that by automating the tedious parts of our workflow, we can focus more on the "Art" and less on the "Admin."

Contributing
I am actively looking for ways to improve the script's nuance and logical flow. If you have ideas or want to collaborate, feel free to open an issue or a Pull Request!

Author: [Robbi Yanuar]

Role: Video Editor | Motion Designer | Emerging Developer

How to add this to your GitHub:
Go to your repository on GitHub.

Click "Add file" -> "Create new file".

Name the file README.md.

Paste the text above.

Click "Commit changes".
