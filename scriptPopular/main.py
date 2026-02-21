"""
News-to-Script Automation Tool
Scrapes 5 popular articles from bloombergtechnoz.com, summarizes with Groq AI,
and sends the script to Telegram.

=============================================================================
API KEY CONFIGURATION (Set these as GitHub Secrets):
=============================================================================
1. GROQ_API_KEY:
   - Get from: https://console.groq.com/keys
   - Add to GitHub: Settings > Secrets and variables > Actions > New repository secret
   - Name: GROQ_API_KEY

2. TELEGRAM_BOT_TOKEN:
   - Get from: @BotFather on Telegram (send /newbot command)
   - Add to GitHub: Settings > Secrets and variables > Actions > New repository secret
   - Name: TELEGRAM_BOT_TOKEN

3. TELEGRAM_CHAT_ID:
   - Get from: @userinfobot on Telegram (send /start)
   - Add to GitHub: Settings > Secrets and variables > Actions > New repository secret
   - Name: TELEGRAM_CHAT_ID
=============================================================================
"""

import os
import time
import requests
from bs4 import BeautifulSoup

# =============================================================================
# CONFIGURATION
# =============================================================================

# Target website
BASE_URL = "https://www.bloombergtechnoz.com"
POPULAR_URL = f"{BASE_URL}/"

# Scraping settings
ARTICLE_COUNT = 5
REQUEST_TIMEOUT = 10
REQUEST_DELAY = 2

# Groq API endpoint
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# User-Agent header
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# =============================================================================
# SCRAPER MODULE
# =============================================================================


def fetch_page_content(url: str) -> str:
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""


def get_popular_articles() -> list[dict]:
    print(f"Fetching popular articles from {POPULAR_URL}...")

    html_content = fetch_page_content(POPULAR_URL)
    if not html_content:
        raise Exception("Failed to fetch homepage content")

    soup = BeautifulSoup(html_content, "lxml")
    articles = []

    popular_list = soup.find("ul", class_="list-terpopuler")
    
    if not popular_list:
        print("Warning: Could not find popular section")
        article_elements = soup.select("article")[:ARTICLE_COUNT]
    else:
        article_elements = popular_list.find_all("li", limit=ARTICLE_COUNT)

    print(f"Found {len(article_elements)} article elements")

    for element in article_elements:
        title_tag = element.find("h5", class_="title")
        if not title_tag:
            title_tag = element.find(["h2", "h3", "h4", "h5", "h6"])
        if not title_tag:
            title_tag = element.find("a")

        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        if not title:
            continue

        link_tag = element.find("a", href=True)
        if not link_tag:
            link_tag = title_tag if title_tag.name == "a" else None

        if not link_tag:
            continue

        article_url = link_tag["href"]

        if article_url.startswith("/"):
            article_url = f"{BASE_URL}{article_url}"
        elif article_url.startswith("./"):
            article_url = f"{BASE_URL}{article_url[1:]}"
        elif not article_url.startswith("http"):
            article_url = f"{BASE_URL}/{article_url}"

        articles.append({"title": title, "url": article_url})
        print(f"  - Found: {title[:50]}...")

    return articles[:ARTICLE_COUNT]


def scrape_article_content(article_url: str) -> str:
    print(f"  Scraping: {article_url}")

    html_content = fetch_page_content(article_url)
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, "lxml")

    for tag in soup(["script", "style", "noscript", "iframe", "nav", "footer", "header"]):
        tag.decompose()

    content_tag = soup.find("div", class_="detail-in")
    
    if not content_tag:
        content_selectors = [".article-content", ".post-content", ".entry-content", "article", ".content", "main"]
        for selector in content_selectors:
            content_tag = soup.select_one(selector)
            if content_tag:
                break

    if not content_tag:
        paragraphs = soup.find_all("p")
    else:
        paragraphs = content_tag.find_all("p")

    content_parts = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if text and len(text) > 20:
            content_parts.append(text)

    return " ".join(content_parts)


def scrape_all_articles(articles: list[dict]) -> list[dict]:
    scraped_articles = []

    for i, article in enumerate(articles):
        print(f"Scraping article {i + 1}/{len(articles)}...")

        content = scrape_article_content(article["url"])

        if content:
            scraped_articles.append({
                "title": article["title"],
                "url": article["url"],
                "content": content,
            })
        else:
            print(f"  Warning: Could not extract content from {article['url']}")
            scraped_articles.append({
                "title": article["title"],
                "url": article["url"],
                "content": "",
            })

        if i < len(articles) - 1:
            print(f"  Waiting {REQUEST_DELAY} seconds before next request...")
            time.sleep(REQUEST_DELAY)

    return scraped_articles


# =============================================================================
# AI MODULE (Groq API - FREE Tier)
# =============================================================================


def generate_script(articles: list[dict], api_key: str) -> str:
    print("Generating script with Groq AI (Llama 3)...")
    
    try:
        articles_text = ""
        for i, article in enumerate(articles, 1):
            articles_text += f"""
ARTICLE {i}:
HEADLINE: {article['title']}
CONTENT: {article['content'][:2000] if article['content'] else 'Content not available'}
---
"""

        system_prompt = """You are a professional news script writer for TikTok/Reels financial news content.

CRITICAL RULES:
1. ORIGINAL HEADLINES: Use EXACT headlines. Do NOT modify them.
2. NO CLICKBAIT: Write factually, professionally. No sensationalism.
3. SCRIPT STRUCTURE:
   - Hook: 1-2 sentence neutral introduction
   - Body: 5 news items (headline + 2-3 sentence summary each)
   - Outro: Brief professional closing
4. TONE: Like Bloomberg/Reuters anchor
5. DURATION: 2-3 minutes (350-450 words)
6. LANGUAGE: Match headline language

Format with: HOOK:, NEWS 1-5:, OUTRO:"""

        user_prompt = f"""Create TikTok/Reels script from these 5 Bloomberg Technoz articles.
Use EXACT headlines. Professional tone. No clickbait.

{articles_text}

Generate script:"""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1024,
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            script = result["choices"][0]["message"]["content"]
            if script:
                return script.strip()
        
        return "Error: Groq returned empty response."
            
    except requests.RequestException as e:
        print(f"Error calling Groq API: {e}")
        return None
    except Exception as e:
        print(f"Error generating script: {e}")
        return None


# =============================================================================
# DELIVERY MODULE (Telegram Bot)
# =============================================================================


def send_to_telegram(text: str, bot_token: str, chat_id: str, is_error: bool = False) -> bool:
    if not text:
        print("Skip Telegram: No content to send.")
        return False

    print("Sending script to Telegram...")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Truncate if too long (Telegram limit is 4096 chars)
    max_length = 4000
    if len(text) > max_length:
        text = text[:max_length] + "\n\n...(truncated)"

    if is_error:
        message = f"❌ Automation Error\n\n{text}\n\nCheck GitHub Actions logs."
    else:
        message = f"""📰 NEWS-TO-SCRIPT - Daily Tech News
📅 {time.strftime('%A, %B %d, %Y')}

{text}

---
Generated by News-to-Script Automation"""

    payload = {
        "chat_id": chat_id,
        "text": message,
    }

    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        
        # Print response for debugging
        print(f"Telegram response status: {response.status_code}")
        print(f"Telegram response: {response.text[:200]}")
        
        response.raise_for_status()

        result = response.json()
        if result.get("ok"):
            print("Script sent to Telegram successfully!")
            return True
        else:
            print(f"Telegram API error: {result}")
            return False

    except requests.RequestException as e:
        print(f"Error sending to Telegram: {e}")
        return False


# =============================================================================
# MAIN EXECUTION
# =============================================================================


def main():
    print("=" * 60)
    print("News-to-Script Automation Tool")
    print("=" * 60)

    groq_api_key = os.getenv("GROQ_API_KEY")
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not groq_api_key:
        print("ERROR: GROQ_API_KEY not set")
        return False

    if not telegram_bot_token:
        print("ERROR: TELEGRAM_BOT_TOKEN not set")
        return False

    if not telegram_chat_id:
        print("ERROR: TELEGRAM_CHAT_ID not set")
        return False

    try:
        print("\n[Step 1] Scraping popular articles...")
        articles = get_popular_articles()

        if not articles:
            raise Exception("No articles found")

        print(f"\n[Step 2] Scraping full content from {len(articles)} articles...")
        scraped_articles = scrape_all_articles(articles)

        valid_articles = [a for a in scraped_articles if a["content"]]
        if not valid_articles:
            valid_articles = scraped_articles

        print(f"\n[Step 3] Generating script with Groq AI...")
        script = generate_script(valid_articles, groq_api_key)

        if not script or script.startswith("Error:"):
            raise Exception(f"Script generation failed: {script}")

        print(f"\n[Step 4] Sending to Telegram...")
        success = send_to_telegram(script, telegram_bot_token, telegram_chat_id)

        print("\n" + "=" * 60)
        print("Execution completed!" if success else "Execution completed with errors")
        print("=" * 60)

        return success

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        send_to_telegram(str(e) + "\n\nCheck GitHub Actions logs.", telegram_bot_token, telegram_chat_id, is_error=True)
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
