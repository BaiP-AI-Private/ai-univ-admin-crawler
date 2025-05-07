import asyncio
import json
import aiohttp
import config
import logging
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def load_university_urls(filename=f"{config.DATA_DIR}/universities.json"):
    """Loads university URLs dynamically from JSON."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load universities JSON file: {e}")
        return []

async def fetch_html(session, url):
    """Fetches HTML content with error handling & fallback."""
    try:
        async with session.get(url, headers=config.DEFAULT_HEADERS, timeout=config.DEFAULT_TIMEOUT) as response:
            if response.status == 200:
                logging.info(f"Successfully fetched {url}")
                return await response.text()
            else:
                logging.error(f"Failed to fetch {url}, status code: {response.status}")
                return None
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        return None  # Fallback mechanism

def extract_details(soup):
    """
    Extract the required details:
      - Courses offered
      - Admissions requirements
      - Application deadline
    It searches for header tags containing target keywords and then extracts
    the text from the following paragraph.
    """
    def get_info(keyword):
        header = soup.find(lambda tag: tag.name in ["h1", "h2", "h3"] and keyword in tag.get_text().lower())
        if header:
            next_p = header.find_next("p")
            if next_p:
                return next_p.get_text(strip=True)
        return "Not found"

    courses_info    = get_info("course")
    adm_req_info    = get_info("requirement")
    deadline_info   = get_info("deadline")
    return courses_info, adm_req_info, deadline_info

async def structured_extraction(universities):
    """Extracts structured information for each university."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_html(session, uni["url"]) for uni in universities]
        results = await asyncio.gather(*tasks)

    university_data = []
    for uni, html in zip(universities, results):
        if html:
            soup = BeautifulSoup(html, "html.parser")
            courses, requirements, deadline = extract_details(soup)
            data = {
                "name": uni["name"],
                "url": uni["url"],
                "courses": courses,
                "admissions_requirements": requirements,
                "application_deadline": deadline
            }
            university_data.append(data)
            logging.info(f"Extracted data for {uni['name']}")
        else:
            logging.warning(f"No HTML retrieved for {uni['name']}, skipping extraction.")
    return university_data

async def main():
    universities = load_university_urls()
    if not universities:
        logging.error("No universities found to scrape. Exiting.")
        return

    data = await structured_extraction(universities)
    try:
        with open(config.OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logging.info(f"Saved structured data to {config.OUTPUT_FILE}")
    except Exception as e:
        logging.error(f"Error saving data: {e}")

if __name__ == "__main__":
    asyncio.run(main())
