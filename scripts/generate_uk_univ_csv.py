#!/usr/bin/env python3
"""
generate_uk_institutions_csv.py

Scrapes:
  1. The first "wikitable sortable" of UK universities.
  2. The "Member institutions of the University of London" list.
  3. The "Other recognised bodies" list.
Resolves each to its official website & validated admissions page.
Emits: uk_institutions.csv (Name, AdminURL, Country)

If the detected admissions URL returns a non-200 status, the AdminURL field will fallback to the university's main site.
"""
import csv
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; UniversityAdmissionsBot/1.0)"
}
WIKI_BASE = "https://en.wikipedia.org"


def get_official_site(wiki_href):
    """Fetch a uni’s Wikipedia page and return its infobox Website link."""
    resp = requests.get(urljoin(WIKI_BASE, wiki_href), headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    infobox = soup.find("table", class_="infobox vcard")
    if not infobox:
        return ""
    header = infobox.find("th", string="Website")
    if not header:
        return ""
    link = header.find_next_sibling("td").find("a", class_="external")
    return link["href"] if link and link.has_attr("href") else ""


def find_admissions_page(base_url):
    """Scrape homepage for an 'admiss' link; fallback to /admissions."""
    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except Exception:
        # fallback candidate
        return base_url.rstrip("/") + "/admissions"
    soup = BeautifulSoup(resp.text, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        txt = a.get_text(" ").lower()
        if "admiss" in href.lower() or "admiss" in txt:
            return urljoin(base_url, href)
    return base_url.rstrip("/") + "/admissions"


def validate_url(url):
    """Return True if HEAD request gets status code 200, else False."""
    try:
        resp = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=10)
        return resp.status_code == 200
    except Exception:
        return False


def scrape_main_table(soup):
    table = soup.find(
        "table",
        class_=lambda cls: cls and "wikitable" in cls and "sortable" in cls
    )
    items = []
    if table:
        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue
            link = cols[1].find("a", href=True)
            if link:
                items.append((link.get_text(strip=True), link["href"]))
    else:
        print("❌ Main table not found")
    return items


def scrape_london_members(soup):
    header = soup.find(id="Member_institutions_of_the_University_of_London")
    items = []
    if header:
        ul = header.find_next("ul")
        if ul:
            for li in ul.find_all("li"):
                link = li.find("a", href=True)
                if link and link["href"].startswith("/wiki/"):
                    items.append((link.get_text(strip=True), link["href"]))
        else:
            print("❌ London members <ul> not found")
    else:
        print("❌ London members header not found")
    return items


def scrape_other_recognised(soup):
    header = soup.find(id="Other_recognised_bodies")
    items = []
    if header:
        ul = header.find_next("ul")
        if ul:
            for li in ul.find_all("li"):
                link = li.find("a", href=True)
                if link and link["href"].startswith("/wiki/"):
                    items.append((link.get_text(strip=True), link["href"]))
        else:
            print("❌ Other recognised bodies <ul> not found")
    else:
        print("❌ Other recognised bodies header not found")
    return items


def main():
    url = WIKI_BASE + "/wiki/List_of_universities_in_the_United_Kingdom"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # scrape all three sections
    entries = []
    entries += scrape_main_table(soup)
    entries += scrape_london_members(soup)
    entries += scrape_other_recognised(soup)

    # dedupe by name
    unis = {}
    for name, href in entries:
        if name not in unis:
            unis[name] = href

    out_path = "uk_institutions.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "AdminURL", "Country"])

        count = 0
        for name, href in sorted(unis.items()):
            print(f"→ {name} …", end=" ", flush=True)
            site = get_official_site(href)
            if not site:
                print("⚠️ no official site, skipping.")
                continue

            # find and validate admissions page
            adm_candidate = find_admissions_page(site)
            if validate_url(adm_candidate):
                adm = adm_candidate
                print("found valid admissions:", adm)
            else:
                adm = site  # fallback to main site if admissions invalid
                print("⚠️ admissions URL invalid, using main site:", adm)

            writer.writerow([name, adm, "UK"])
            count += 1
            time.sleep(0.5)

        print(f"\n✅ Done — wrote {count} institutions to {out_path}")

if __name__ == "__main__":
    main()
