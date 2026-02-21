Product Requirements Document (PRD): Automated News-to-Script Generator
1. Project Vision
To build a fully automated, zero-cost Python application that scrapes the top 5 trending news stories from Bloomberg Technoz, summarizes them with high accuracy, and formats them into a professional, non-clickbait script for TikTok/Reels.
2. Target Source & Data Extraction
* Target URL: https://www.bloombergtechnoz.com
* Scraping Target: The "Populer" (Popular/Trending) section.
* Quantity: Exactly 5 news items. No more, no less.
* Required Data Points: - Original Headline (Title).
    * Article URL (to fetch the full content for summarization).
* Tooling: Python BeautifulSoup4 and requests.
3. Core Functional Requirements
R1: Content Integrity Rules
* Headline Policy: The headlines in the final script must match the website exactly. Zero modifications, zero rewording, and zero dramatization.
* No Clickbait: The summary must be factual, professional, and grounded in the article's data. Avoid sensationalist adjectives or "shocking" reveals.
* Summarization Depth: Summaries must be detailed enough to be informative for the public but concise enough for a 60-90 second video.
R2: Scripting Engine (LLM Integration)
* Engine: Use a free-tier API (e.g., Groq API with Llama 3 or Google Gemini API).
* Script Structure:
    1. Professional Hook: A neutral introduction to the day's top financial/tech news.
    2. Body (News 1-5): Present the Original Headline followed by a 2-3 sentence factual summary.
    3. Professional Outro: A brief closing statement without "cringe" calls to action.
* Tone of Voice: Credible, authoritative, and straightforward (like a news anchor).
* The video will be 2-3 minutes
R3: Automation & Scheduling
* Trigger Time: Every day at 06:00 AM WIB (UTC+7).
* Environment: GitHub Actions (to ensure the solution remains 100% free and runs in the cloud).
* Cron Job: 0 23 * * * (UTC).
R4: Delivery System
* Channel: Telegram Bot API.
* Reasoning: Telegram is free, reliable, and allows the user to receive the formatted script directly on their phone as a message, ready to be copied for recording.
4. Technical Constraints
* Language: Python 3.10+.
* Zero Cost: The entire stack must use Free Tiers (GitHub Actions, Telegram, Free-tier LLM API).
* Error Handling: If the website structure changes, the script should log an error rather than sending a broken script.
5. System Workflow
1. GitHub Action wakes up at 23:00 UTC (06:00 AM WIB).
2. Scraper Module hits Bloomberg Technoz and identifies the Top 5 "Populer" links.
3. Detail Scraper visits each of the 5 links to extract the main article text.
4. AI Module sends the raw text to the LLM with a strict "News Script" prompt.
5. Format Module cleans the text into a readable script format.
6. Delivery Module sends the final script to the user's Telegram.
R5: Technical Best Practices & Scraping Ethics
User-Agent Header: The script must include a custom User-Agent header to emulate a modern web browser (e.g., Chrome or Firefox). This prevents the website from flagging the request as a basic, automated bot.

Request Timeout: Implement a mandatory timeout (e.g., 10-15 seconds) for every HTTP request. This ensures the script doesn't "hang" or get stuck indefinitely if the website is slow or temporarily down.

Request Throttling (Delay): Even though we are only fetching 5 articles, implement a short delay (e.g., 1-2 seconds) between each individual article request. This mimics human behavior and maintains a low profile on the server's traffic logs.

Error Handling: Use try-except blocks to handle potential connection errors or changes in the website's HTML structure gracefully.
