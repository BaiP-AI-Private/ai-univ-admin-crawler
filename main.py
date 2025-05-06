import asyncio
import json
import aiohttp
import config  # Import global settings
from bs4 import BeautifulSoup

def load_university_urls(filename=f"{config.DATA_DIR}/universities.json"):
    """Loads university URLs dynamically from JSON."""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

async def fetch_html(session, url):
    """Fetches HTML content using global headers & timeout."""
    try:
        async with session.get(url, headers=config.DEFAULT_HEADERS, timeout=config.DEFAULT_TIMEOUT) as response:
            return await response.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

async def scrape_universities(universities):
    """Scrapes university websites asynchronously."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_html(session, uni["url"]) for uni in universities]
        results = await asyncio.gather(*tasks)

    university_data = [{"name": uni["name"], "url": uni["url"], "html": html} for uni, html in zip(universities, results)]
    return university_data

async def main():
    universities = load_university_urls()
    data = await scrape_universities(universities)

    with open(config.OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"Saved university HTML data to {config.OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
