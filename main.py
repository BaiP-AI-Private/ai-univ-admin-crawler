import asyncio
import json
import aiohttp
import config
from bs4 import BeautifulSoup

def load_university_urls(filename=f"{config.DATA_DIR}/universities.json"):
    """Loads university URLs dynamically from JSON."""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

async def fetch_html(session, url):
    """Fetches HTML content with error handling & fallback."""
    try:
        async with session.get(url, headers=config.DEFAULT_HEADERS, timeout=config.DEFAULT_TIMEOUT) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"Failed to fetch {url}, status code: {response.status}")
                return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None  # Fallback mechanism for request failure

async def structured_extraction(universities):
    """Extracts structured text using BeautifulSoup."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_html(session, uni["url"]) for uni in universities]
        results = await asyncio.gather(*tasks)

    university_data = []
    for uni, html in zip(universities, results):
        if html:
            soup = BeautifulSoup(html, "html.parser")

            # Extract specific structured elements
            title = soup.title.string if soup.title else "No Title Found"
            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
            headers = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]

            university_data.append({
                "name": uni["name"],
                "url": uni["url"],
                "title": title,
                "headers": headers[:5],  # Limiting for relevance
                "paragraphs": paragraphs[:10],  # Limiting for readability
            })

    return university_data

async def main():
    universities = load_university_urls()
    data = await structured_extraction(universities)

    with open(config.OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"Saved structured university data to {config.OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
