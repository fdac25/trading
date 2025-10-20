"""
Monitors RSS feeds for new articles that mention Nvidia in their title or
summary. Logs date, title, and body of relevant articles to CSV.

Expandable for multiple feeds and domains.
"""

import feedparser
import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
from urllib.parse import urlparse
import os

FEED_URLS = [
    "https://www.forbes.com/investing/feed/",
    "https://www.forbes.com/innovation/feed/",
    "https://www.forbes.com/money/feed/",
    "https://www.forbes.com/business/feed/",
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "../data/nvidia_articles.csv")
CHECK_INTERVAL = 600 # check feeds every 10 minutes

seen_links = set()

def get_article_text_generic(url):
    """Fetch text inside <p> tags"""
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        body_text = " ".join(p.get_text() for p in paragraphs)
        return body_text.strip()
    except Exception as e:
        print(f"Error fetching article text: {e}")
        return ""

def get_article_text(url):
    """Decide which scraper to use based on domain"""

    # Example for later:
    # domain = urlparse(url).netloc
    # if "wired.com" in domain:
    #     return get_article_text_wired(url)
    # else:
    #     return get_article_text_generic(url)

    return get_article_text_generic(url)

def check_for_new_articles():
    """Parse RSS feeds and append new Nvidia articles to CSV"""
    global seen_links

    for feed_url in FEED_URLS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            summary = getattr(entry, "summary", "")

            # Get published date
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                # Standardize date for CSV
                published_csv = time.strftime("%Y-%m-%d", entry.published_parsed)

                # Pretty printing for console
                published_pretty = time.strftime("[%Y-%m-%d %a %H:%M]", entry.published_parsed)
            else:
                # If published date unavailable, use current time
                now = datetime.now()
                published_csv = now.strftime("%Y-%m-%d")
                published_pretty = now.strftime("[%Y-%m-%d %a %H:%M]")

            if "nvidia" in title.lower() or "nvidia" in summary.lower():
                if link not in seen_links:
                    print(f"\n{published_pretty} {title}\n{link}\n")
                    seen_links.add(link)
                    body = get_article_text(link)

                    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([published_csv, title, body])

def main():
    print("Monitoring feeds for Nvidia articles...")
    while True:
        check_for_new_articles()
        print(f"Checked all feeds at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
