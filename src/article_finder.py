# Article finder - scrapes google to find ~300 latest articles about a specified topic from a specified source

# Imports
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

# Find first occurance of a char in a string
def find_first(s, c):
  for i in range(len(s)):
    if(s[i] == c): return i
  return -1

base_url = "https://www.google.com/search?q=allintitle:+nvidia+site:forbes.com/sites&tbs=sbd:1&tbm=nws&start=0"
extracted_links = []
MAX_SEARCH = 30

# Iterate over multiple google search pages to find articles
for i in range(MAX_SEARCH):
  # Replace "start=X" in base url to iterate through pages
  url = base_url.replace("start=0", "start=" + str(i * 10))

  # Get html from url
  response = requests.get(url)
  soup = BeautifulSoup(response.content, 'html.parser')

  # Find all elements containing Forbes news article links
  links = soup.find_all(href=re.compile("https://www.forbes.com/sites"))

  # Convert links to text and remove extra data
  for link in links:
      href = link.get("href")
      href = href[find_first(href, '=')+1: find_first(href, '&')]
      text = link.get_text()
      if href: # Ensure the href attribute exists
          extracted_links.append(href)

  # Print status
  print(f"Extracted {len(links)} links from search page {i+1}")
  if len(links) == 0:
    print(" ! ZERO LINKS EXTRACTED - ENDING SEARCH")
    break
  # time.sleep(1)

# # Find and remove duplicates - will make list unordered
# num_links = len(extracted_links)
# extracted_links = set(extracted_links)
# num_dup = num_links - len(extracted_links)
# print(f"Removed {num_dup} duplicate links")

# Print results
# for link_data in extracted_links:
  # print(link_data['text'])
  # print("" + str(link_data))
  # print("")
print(f"Found {len(extracted_links)} links")

# Export links as CSV
df_final = pd.DataFrame(extracted_links, columns=['Link'])
df_final.to_csv('forbes_search.csv', index=True)
df_final.head(10)