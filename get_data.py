#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv

# 1. Configuration
INDEX_URL = "https://www.cs.utexas.edu/~scottm/cs307/codingSamples.htm"
BASE_URL  = "https://www.cs.utexas.edu/~scottm/cs307/"

# 2. Fetch and parse the index page
resp = requests.get(INDEX_URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# 3. Find all .java links
java_links = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    if href.lower().endswith(".java"):
        full_url = urljoin(BASE_URL, href)
        java_links.append((a.get_text(strip=True), full_url))

print(f"Found {len(java_links)} Java files.")

# 4. Download each Java file and collect its source
samples = []
for name, url in java_links:
    print(f"  ↳ downloading {name} …")
    r = requests.get(url)
    r.raise_for_status()
    code = r.text
    samples.append({
        "name": name,
        "url": url,
        "code": code
    })

# 5. Write out to CSV
with open("java_samples.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["name", "url", "code"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    for row in samples:
        writer.writerow(row)

print("Done. → java_samples.csv")
