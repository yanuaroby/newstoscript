# News-to-Script Automation Tool

Automated Python application that scrapes top 5 trending news from Bloomberg Technoz, summarizes with Groq AI (Llama 3 - FREE), and sends TikTok/Reels script to Telegram.

## Features

- ✅ Scrapes 5 popular articles from bloombergtechnoz.com
- ✅ Uses Groq AI with Llama 3 (100% FREE)
- ✅ "No Clickbait" and "Original Headline" enforcement
- ✅ Daily automation at 06:00 AM WIB via GitHub Actions
- ✅ Polite scraping (User-Agent, timeouts, delays)

## Setup

### 1. Get Groq API Key (FREE)
1. Visit https://console.groq.com/keys
2. Sign up/Login (FREE)
3. Create API Key
4. Copy key (format: `gsk_...`)

**Free Tier:** 30 req/min, 14,400 req/day - No credit card needed

### 2. Create Telegram Bot
1. Open Telegram, search @BotFather
2. Send `/newbot`
3. Copy Bot Token

### 3. Get Chat ID
1. Open Telegram, search @userinfobot
2. Send `/start`
3. Copy Chat ID

### 4. Configure GitHub Secrets
Go to Settings > Secrets and variables > Actions:

| Secret | Value |
|--------|-------|
| `GROQ_API_KEY` | Groq API key |
| `TELEGRAM_BOT_TOKEN` | Bot token |
| `TELEGRAM_CHAT_ID` | Chat ID |

### 5. Enable Actions
Go to Actions tab → Enable workflows

## Test Locally

```bash
cd scriptPopular
pip install -r requirements.txt
export GROQ_API_KEY="your-key"
export TELEGRAM_BOT_TOKEN="your-token"
export TELEGRAM_CHAT_ID="your-id"
python main.py
```

## Files

- `main.py` - Main script (scraper, Groq AI, Telegram)
- `requirements.txt` - Dependencies
- `.github/workflows/main.yml` - Daily automation

## Troubleshooting

**No articles found:** Website structure changed  
**GROQ_API_KEY not set:** Check GitHub Secrets  
**Telegram error:** Verify bot token and chat ID
