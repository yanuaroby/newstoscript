"""
News-to-Script Automation Tool
Scrapes 5 popular articles from bloombergtechnoz.com, summarizes with Gemini AI,
and sends the script to Telegram.

=============================================================================
API KEY CONFIGURATION (Set these as GitHub Secrets):
=============================================================================
1. GEMINI_API_KEY:
   - Get from: https://makersuite.google.com/app/apikey
   - Add to GitHub: Settings > Secrets and variables > Actions > New repository secret
   - Name: GEMINI_API_KEY

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
import html
import requests
from bs4 import BeautifulSoup

# =============================================================================
# CONFIGURATION
# =============================================================================

# Target website
BASE_URL = "https://www.bloombergtechnoz.com"
POPULAR_URL = f"{BASE_URL}/"  # Homepage contains the "Populer" section

# Scraping settings
ARTICLE_COUNT = 5  # Exactly 5 articles as per PRD
REQUEST_TIMEOUT = 10  # 10-second timeout for all requests
REQUEST_DELAY = 2  # 2-second delay between requests (polite scraping)

# User-Agent header (mimics Chrome browser on macOS)
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
    """
    Fetch HTML content from a URL with proper headers and timeout.
    Returns empty string on failure.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""


def get_popular_articles() -> list[dict]:
    """
    Scrape the top 5 popular articles from Bloomberg Technoz homepage.
    Returns list of dicts with 'title' and 'url' keys.
    """
    print(f"Fetching popular articles from {POPULAR_URL}...")

    html = fetch_page_content(POPULAR_URL)
    if not html:
        raise Exception("Failed to fetch homepage content")

    soup = BeautifulSoup(html, "lxml")
    articles = []

    # Find the popular section using the correct selector: ul.list-terpopuler > li
    popular_list = soup.find("ul", class_="list-terpopuler")
    
    if not popular_list:
        # Fallback: try to find any popular/trending section
        popular_selectors = [
            ".popular-posts ul",
            ".trending ul",
            "[class*='popular'] ul",
            "[class*='trending'] ul",
        ]
        for selector in popular_selectors:
            popular_list = soup.select_one(selector)
            if popular_list:
                break

    if not popular_list:
        print("Warning: Could not find popular section, trying fallback...")
        # Last resort: find all article links
        article_elements = soup.select("article")[:ARTICLE_COUNT]
    else:
        article_elements = popular_list.find_all("li", limit=ARTICLE_COUNT)

    print(f"Found {len(article_elements)} article elements")

    for element in article_elements:
        # Find the title - it's in h5.title inside the card-box
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

        # Extract URL - find the anchor tag wrapping the card-box
        link_tag = element.find("a", href=True)
        if not link_tag:
            link_tag = title_tag if title_tag.name == "a" else None

        if not link_tag:
            continue

        article_url = link_tag["href"]

        # Make URL absolute if it's relative
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
    """
    Scrape the full content of a single article.
    Returns the article text content.
    """
    print(f"  Scraping: {article_url}")

    html = fetch_page_content(article_url)
    if not html:
        return ""

    soup = BeautifulSoup(html, "lxml")

    # Remove script and style elements
    for tag in soup(["script", "style", "noscript", "iframe", "nav", "footer", "header"]):
        tag.decompose()

    # Bloomberg Technoz specific: content is in div.detail-in
    content_tag = soup.find("div", class_="detail-in")
    
    if not content_tag:
        # Fallback selectors
        content_selectors = [
            ".article-content",
            ".post-content",
            ".entry-content",
            "article",
            ".content",
            "main",
        ]
        for selector in content_selectors:
            content_tag = soup.select_one(selector)
            if content_tag:
                break

    if not content_tag:
        # Fallback: get all paragraphs
        paragraphs = soup.find_all("p")
    else:
        paragraphs = content_tag.find_all("p")

    # Extract text from paragraphs
    content_parts = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if text and len(text) > 20:  # Skip very short paragraphs
            content_parts.append(text)

    return " ".join(content_parts)


def scrape_all_articles(articles: list[dict]) -> list[dict]:
    """
    Scrape full content from all articles with polite delays.
    """
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
            # Still include with empty content for fallback
            scraped_articles.append({
                "title": article["title"],
                "url": article["url"],
                "content": "",
            })

        # Add delay between requests (except for the last one)
        if i < len(articles) - 1:
            print(f"  Waiting {REQUEST_DELAY} seconds before next request...")
            time.sleep(REQUEST_DELAY)

    return scraped_articles


# =============================================================================
# AI MODULE (Gemini API)
# =============================================================================


def generate_script(articles: list[dict], api_key: str) -> str:
    """
    Generate a professional news script using Gemini AI.
    Enforces 'No Clickbait' and 'Original Headline' rules from PRD.
    """
    print("Generating script with Gemini AI...")

    # Build the prompt with strict rules
    system_instruction = """
You are a professional news script writer for TikTok/Reels financial news content.

CRITICAL RULES - MUST FOLLOW EXACTLY:

1. ORIGINAL HEADLINES: Use the EXACT headlines from the articles. Do NOT modify, 
   reword, paraphrase, or dramatize them in ANY way. Copy them character-for-character.

2. NO CLICKBAIT: Write in a factual, professional, and authoritative tone like a 
   news anchor. Avoid sensationalist adjectives, shocking reveals, or exaggerated 
   language. No "You won't believe..." or "This changes everything!" type phrases.

3. SCRIPT STRUCTURE:
   - Hook: A neutral 1-2 sentence introduction about today's top tech/financial news
   - Body: For each of the 5 news items:
     * State the ORIGINAL headline exactly as provided
     * Provide a 2-3 sentence factual summary based ONLY on the article content
   - Outro: A brief, professional closing statement (no cringe calls to action)

4. TONE: Credible, authoritative, straightforward. Like a Bloomberg or Reuters anchor.

5. DURATION: The script should be 2-3 minutes when read aloud (approximately 350-450 words).

6. LANGUAGE: Write in English unless the headlines are in another language, then match.

Format the output clearly with:
- "HOOK:" section
- "NEWS 1:" through "NEWS 5:" sections (each with headline and summary)
- "OUTRO:" section
"""

    # Prepare article data for the prompt
    articles_text = ""
    for i, article in enumerate(articles, 1):
        articles_text += f"""
ARTICLE {i}:
HEADLINE: {article['title']}
URL: {article['url']}
CONTENT: {article['content'][:2000] if article['content'] else 'Content not available'}
---
"""

    user_prompt = f"""
Generate a professional TikTok/Reels news script based on these 5 trending articles
from Bloomberg Technoz.

{articles_text}

Remember:
- Use EXACT headlines (no modifications)
- No clickbait language
- Professional news anchor tone
- 2-3 minute duration (350-450 words)
"""

    # Call Gemini API directly using requests
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": user_prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1024,
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        result = response.json()
        
        if "candidates" in result and len(result["candidates"]) > 0:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            raise Exception(f"Gemini API returned no candidates: {result}")
            
    except requests.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        raise


# =============================================================================
# DELIVERY MODULE (Telegram Bot)
# =============================================================================


def send_to_telegram(script: str, bot_token: str, chat_id: str, is_error: bool = False) -> bool:
    """
    Send the generated script to Telegram using the Bot API.
    Returns True on success, False on failure.
    """
    print("Sending script to Telegram...")

    # Telegram Bot API endpoint
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    if is_error:
        # Error notification
        message = f"""
❌ <b>Automation Error</b>

{script}

Please check the GitHub Actions logs.
"""
    else:
        # Success - send the script (escape HTML in script content)
        escaped_script = html.escape(script)
        message = f"""
📰 <b>NEWS-TO-SCRIPT - Daily Tech News</b>
📅 {time.strftime('%A, %B %d, %Y')}

{escaped_script}

---
<i>Generated by News-to-Script Automation</i>
"""

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
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
    """Main execution function."""
    print("=" * 60)
    print("News-to-Script Automation Tool")
    print("=" * 60)

    # Get API keys from environment variables (set by GitHub Actions)
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    # Validate required environment variables
    if not gemini_api_key:
        print("ERROR: GEMINI_API_KEY not set in environment variables")
        return False

    if not telegram_bot_token:
        print("ERROR: TELEGRAM_BOT_TOKEN not set in environment variables")
        return False

    if not telegram_chat_id:
        print("ERROR: TELEGRAM_CHAT_ID not set in environment variables")
        return False

    try:
        # Step 1: Scrape popular articles
        print("\n[Step 1] Scraping popular articles...")
        articles = get_popular_articles()

        if len(articles) < ARTICLE_COUNT:
            print(f"Warning: Only found {len(articles)} articles (expected {ARTICLE_COUNT})")

        if not articles:
            raise Exception("No articles found on the website")

        # Step 2: Scrape full article content
        print(f"\n[Step 2] Scraping full content from {len(articles)} articles...")
        scraped_articles = scrape_all_articles(articles)

        # Filter out articles with no content
        valid_articles = [a for a in scraped_articles if a["content"]]
        if not valid_articles:
            valid_articles = scraped_articles  # Use all if no content available

        # Step 3: Generate script with AI
        print(f"\n[Step 3] Generating script with Gemini AI...")
        script = generate_script(valid_articles, gemini_api_key)

        # Step 4: Send to Telegram
        print(f"\n[Step 4] Sending to Telegram...")
        success = send_to_telegram(script, telegram_bot_token, telegram_chat_id)

        print("\n" + "=" * 60)
        print("Execution completed!" if success else "Execution completed with errors")
        print("=" * 60)

        return success

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        # Optionally send error notification to Telegram (escape HTML chars)
        send_to_telegram(
            html.escape(str(e)) + "\n\nPlease check the GitHub Actions logs.",
            telegram_bot_token,
            telegram_chat_id,
            is_error=True,
        )
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
