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
from colorama import init, Fore, Style

from ensemble_sentiment_analysis import analyze_sentiment

FEED_URLS = [
    "https://www.forbes.com/investing/feed/",
    "https://www.forbes.com/innovation/feed/",
    "https://www.forbes.com/money/feed/",
    "https://www.forbes.com/business/feed/",
    "./testfeed.xml"
]

init(autoreset=True)
def print_colored_sentiment(sentiment):
    """Prints the text in color based on sentiment"""
    color_map = {
            "UP": Fore.GREEN + Style.BRIGHT,
            "DOWN": Fore.RED + Style.BRIGHT,
            "NEUTRAL": Fore.LIGHTBLACK_EX + Style.BRIGHT
    }

    print(f"[{color_map[sentiment]}{sentiment}{Style.RESET_ALL}]", end="")

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
            summary = getattr(entry, "summary", "").strip()

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
                    seen_links.add(link)

                    body = get_article_text(link)
                    sentiment = analyze_sentiment(body)

                    print(f"╠{published_pretty}", end="")
                    print_colored_sentiment(sentiment)
                    print(f"[{Fore.BLUE}{Style.BRIGHT}\033]8;;{link}\033\\{title}\033]8;;\033\\{Style.RESET_ALL}]\n║")

                    # with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                    #   writer = csv.writer(f)
                    #   writer.writerow([published_csv, title, body])

def main():
    print(f"╔[{datetime.now().strftime('%Y-%m-%d %a %H:%M')}][Checking feeds for Nvidia articles]\n║")
    while True:
        check_for_new_articles()
        print(f"╚[{datetime.now().strftime('%Y-%m-%d %a %H:%M')}][Checked all feeds]\n")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
