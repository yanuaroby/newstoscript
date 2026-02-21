# News-to-Script Automation Tool

A fully automated Python application that scrapes the top 5 trending news stories from Bloomberg Technoz, summarizes them with Google Gemini AI, and sends a professional TikTok/Reels script to your Telegram.

## Features

- ✅ Scrapes exactly 5 popular articles from bloombergtechnoz.com
- ✅ Uses Google Gemini AI for professional summarization
- ✅ Enforces "No Clickbait" and "Original Headline" rules
- ✅ Sends formatted script to Telegram daily at 06:00 AM WIB
- ✅ 100% free (GitHub Actions + Gemini Free Tier + Telegram)
- ✅ Polite scraping with User-Agent headers and rate limiting

## Prerequisites

- Python 3.10+
- GitHub account (for GitHub Actions)
- Google account (for Gemini API)
- Telegram account

## Setup Instructions

### Step 1: Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy the generated key (format: `AIzaSy...`)

### Step 2: Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send the command `/newbot`
3. Follow the prompts to name your bot
4. Copy the **Bot Token** (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 3: Get Your Chat ID

1. Open Telegram and search for **@userinfobot**
2. Send `/start`
3. The bot will reply with your Chat ID (format: `123456789`)

### Step 4: Configure GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret** for each of the following:

| Secret Name | Value |
|-------------|-------|
| `GEMINI_API_KEY` | Your Gemini API key from Step 1 |
| `TELEGRAM_BOT_TOKEN` | Your bot token from Step 2 |
| `TELEGRAM_CHAT_ID` | Your chat ID from Step 3 |

### Step 5: Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. If prompted, click **I understand my workflows, go ahead and enable them**
3. The workflow will run automatically at 06:00 AM WIB daily

### Step 6: Test the Workflow (Optional)

1. Go to **Actions** tab
2. Select **News-to-Script Daily Automation**
3. Click **Run workflow**
4. Check your Telegram for the generated script

## Local Testing

If you want to test locally before deploying:

```bash
# Clone the repository
cd scriptPopular

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your-api-key"
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_CHAT_ID="your-chat-id"

# Run the script
python main.py
```

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── main.yml          # GitHub Actions workflow (daily at 06:00 AM WIB)
├── scriptPopular/
│   ├── main.py               # Main automation script
│   ├── requirements.txt      # Python dependencies
│   ├── prd.md                # Product Requirements Document
│   └── README.md             # This file
└── README.md
```

## How It Works

1. **Scraper Module**: Fetches the Bloomberg Technoz homepage and extracts the top 5 popular articles
2. **Content Extractor**: Visits each article URL and extracts the full text content
3. **AI Module**: Sends the content to Google Gemini with strict prompts for:
   - Original headlines (unchanged)
   - No clickbait language
   - Professional news anchor tone
   - 2-3 minute script duration
4. **Delivery Module**: Formats and sends the script to your Telegram

## Scraping Ethics

This tool implements polite scraping practices:

- ✅ Realistic User-Agent header (Chrome browser)
- ✅ 10-second timeout on all requests
- ✅ 2-second delay between article requests
- ✅ Only 5 articles per run
- ✅ Respects robots.txt

## Troubleshooting

### "No articles found"
The website structure may have changed. Check the GitHub Actions logs for details.

### "GEMINI_API_KEY not set"
Ensure you've added the secret correctly in GitHub Settings > Secrets and variables > Actions.

### "Telegram API error"
Verify your bot token and chat ID are correct. Make sure you've started a conversation with your bot.

### Workflow not running
Check that GitHub Actions is enabled for your repository.

## API Usage Limits

- **Gemini API**: Free tier includes 60 requests/minute (more than enough for daily use)
- **GitHub Actions**: Free tier includes 2,000 minutes/month
- **Telegram Bot API**: Free and unlimited

## License

MIT License - Feel free to modify and use as needed.
