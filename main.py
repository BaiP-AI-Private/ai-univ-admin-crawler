import asyncio
import json
import aiohttp
import config
import logging
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def load_university_urls(filename=config.INPUT_FILE):
    """Loads university URLs dynamically from JSON."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load universities JSON file: {e}")
        return []

async def fetch_html(session, url, retry_count=3):
    """Fetches HTML content with error handling, retries & fallback."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    ]
    
    for attempt in range(retry_count):
        try:
            # Rotate user agents for each retry attempt
            headers = {
                "User-Agent": user_agents[attempt % len(user_agents)],
                "Accept": "text/html,application/xhtml+xml,application/xml",
                "Accept-Language": "en-US,en;q=0.9"
            }
            
            async with session.get(url, headers=headers, timeout=config.DEFAULT_TIMEOUT) as response:
                if response.status == 200:
                    logging.info(f"Successfully fetched {url}")
                    return await response.text()
                elif response.status == 403 or response.status == 429:
                    # Rate limiting or access denied - wait longer and retry
                    wait_time = (attempt + 1) * 5  # Incremental backoff
                    logging.warning(f"Rate limited (status {response.status}) for {url}, waiting {wait_time}s before retry")
                    await asyncio.sleep(wait_time)
                else:
                    logging.error(f"Failed to fetch {url}, status code: {response.status}")
                    # Only retry on server errors (5xx)
                    if response.status < 500 or response.status >= 600:
                        return None
                    await asyncio.sleep(2 * (attempt + 1))  # Wait before retry
        except asyncio.TimeoutError:
            logging.warning(f"Timeout fetching {url}, attempt {attempt+1}/{retry_count}")
            await asyncio.sleep(2)  # Wait before retry
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
            await asyncio.sleep(1)  # Wait before retry
    
    logging.error(f"All retry attempts failed for {url}")
    return None  # Fallback mechanism

def extract_details(soup, university_url):
    """
    Extract the required details using a more comprehensive approach:
      - Courses offered
      - Admissions requirements
      - Application deadline
    
    This enhanced function uses multiple strategies:
    1. Looks for relevant sections by headers and keywords
    2. Checks for common CSS classes and IDs
    3. Extracts structured content like lists and tables
    4. Follows links to dedicated pages if main content isn't found
    """
    result = {
        "courses": [],
        "requirements": [],
        "deadlines": []
    }
    
    # Helper function to clean text
    def clean_text(text):
        if not text:
            return ""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    # Helper to get text from a section
    def extract_section_text(section_elem, max_elements=5):
        texts = []
        current = section_elem.find_next()
        count = 0
        
        # Stop conditions: hit another header, or collected enough elements
        while current and count < max_elements and not (current.name in ['h1', 'h2', 'h3', 'h4'] and len(texts) > 0):
            if current.name in ['p', 'li', 'div'] and current.get_text(strip=True):
                text = clean_text(current.get_text())
                if text and len(text) > 15:  # Minimum meaningful length
                    texts.append(text)
                    count += 1
            current = current.find_next()
            
        return texts
    
    # 1. Course information extraction
    course_keywords = ['course', 'program', 'degree', 'major', 'academic']
    course_headers = []
    
    # Find headers related to courses
    for keyword in course_keywords:
        headers = soup.find_all(lambda tag: tag.name in ['h1', 'h2', 'h3', 'h4'] and 
                               keyword in tag.get_text().lower())
        course_headers.extend(headers)
    
    # Extract course information from relevant sections
    for header in course_headers:
        course_texts = extract_section_text(header)
        if course_texts:
            result["courses"].extend(course_texts)
    
    # Look for lists of courses or programs
    course_lists = soup.select('ul.programs, ul.courses, .program-list, .course-listing, .majors-list')
    for course_list in course_lists:
        items = course_list.find_all('li')
        for item in items:
            text = clean_text(item.get_text())
            if text and text not in result["courses"]:
                result["courses"].append(text)
    
    # 2. Admissions requirements extraction
    req_keywords = ['requirement', 'admission', 'prerequisite', 'qualification', 'eligibility', 'criteria']
    req_headers = []
    
    # Find headers related to requirements
    for keyword in req_keywords:
        headers = soup.find_all(lambda tag: tag.name in ['h1', 'h2', 'h3', 'h4'] and 
                               keyword in tag.get_text().lower())
        req_headers.extend(headers)
    
    # Extract requirement information
    for header in req_headers:
        req_texts = extract_section_text(header)
        if req_texts:
            result["requirements"].extend(req_texts)
    
    # Look for requirement lists
    req_lists = soup.select('ul.requirements, .admission-details, .admission-requirements, .eligibility-criteria')
    for req_list in req_lists:
        items = req_list.find_all('li')
        for item in items:
            text = clean_text(item.get_text())
            if text and text not in result["requirements"]:
                result["requirements"].append(text)
    
    # 3. Application deadline extraction
    deadline_keywords = ['deadline', 'important date', 'application date', 'due date', 'submission', 'calendar']
    deadline_headers = []
    
    # Find headers related to deadlines
    for keyword in deadline_keywords:
        headers = soup.find_all(lambda tag: tag.name in ['h1', 'h2', 'h3', 'h4'] and 
                               keyword in tag.get_text().lower())
        deadline_headers.extend(headers)
    
    # Extract deadline information
    for header in deadline_headers:
        deadline_texts = extract_section_text(header, max_elements=3)  # Deadlines usually shorter
        if deadline_texts:
            result["deadlines"].extend(deadline_texts)
            
    # Look for tables with dates
    date_tables = soup.select('table.dates, table.deadlines, .date-table, .calendar-table')
    for table in date_tables:
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header row
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:  # Need at least two cells for date-description pair
                date_text = clean_text(" - ".join([cell.get_text() for cell in cells]))
                if date_text and date_text not in result["deadlines"]:
                    result["deadlines"].append(date_text)
    
    # Look for any text containing specific date patterns near deadline keywords
    date_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}'
    deadline_paragraphs = soup.find_all('p')
    for p in deadline_paragraphs:
        text = p.get_text().lower()
        if any(keyword in text for keyword in ['deadline', 'due date', 'application']) and re.search(date_pattern, p.get_text(), re.IGNORECASE):
            clean = clean_text(p.get_text())
            if clean and clean not in result["deadlines"]:
                result["deadlines"].append(clean)
    
    # 4. Look for links to dedicated pages if main content isn't found
    if not any([result["courses"], result["requirements"], result["deadlines"]]):
        # Find links to dedicated pages
        admission_links = []
        for a in soup.find_all('a', href=True):
            link_text = a.get_text().lower()
            if any(keyword in link_text for keyword in ['admission', 'apply', 'course', 'program']):
                href = a['href']
                full_url = urljoin(university_url, href)
                admission_links.append((link_text, full_url))
        
        # Return the relevant links for further processing
        if admission_links:
            result["follow_links"] = admission_links
    
    # Clean up and format the results
    return (
        result["courses"] if result["courses"] else ["Not found"],
        result["requirements"] if result["requirements"] else ["Not found"], 
        result["deadlines"] if result["deadlines"] else ["Not found"]
    )

async def structured_extraction(universities):
    """Extracts structured information for each university with rate limiting."""
    university_data = []
    
    async with aiohttp.ClientSession() as session:
        for uni in universities:
            # Rate limiting
            await asyncio.sleep(config.RATE_LIMIT)
            logging.info(f"Processing {uni['name']} at {uni['url']}")
            
            # Fetch the HTML
            html = await fetch_html(session, uni["url"])
            
            if not html:
                logging.warning(f"No HTML retrieved for {uni['name']}, skipping extraction.")
                continue
                
            soup = BeautifulSoup(html, "html.parser")
            courses, requirements, deadlines = extract_details(soup, uni["url"])
            
            # Handle follow-up links if needed (for example if main content wasn't found)
            if isinstance(courses, list) and len(courses) == 1 and courses[0] == "Not found":
                # Check if we have follow-up links from extract_details
                follow_links = getattr(courses, "follow_links", None)
                if follow_links and isinstance(follow_links, list):
                    for link_text, link_url in follow_links[:2]:  # Limit to first 2 links to avoid too many requests
                        logging.info(f"Following secondary link for {uni['name']}: {link_text} -> {link_url}")
                        await asyncio.sleep(config.RATE_LIMIT)  # Rate limiting for secondary requests
                        
                        secondary_html = await fetch_html(session, link_url)
                        if secondary_html:
                            secondary_soup = BeautifulSoup(secondary_html, "html.parser")
                            sec_courses, sec_requirements, sec_deadlines = extract_details(secondary_soup, link_url)
                            
                            # Update with any new information found
                            if sec_courses and sec_courses[0] != "Not found":
                                courses = sec_courses
                            if sec_requirements and sec_requirements[0] != "Not found":
                                requirements = sec_requirements
                            if sec_deadlines and sec_deadlines[0] != "Not found":
                                deadlines = sec_deadlines
            
            # Format the data with cleaner structure
            data = {
                "name": uni["name"],
                "url": uni["url"],
                "courses": courses,
                "admissions_requirements": requirements,
                "application_deadlines": deadlines,
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            university_data.append(data)
            logging.info(f"Extracted data for {uni['name']}")
            
    return university_data

async def main():
    # Ensure data directory exists
    import os
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    # Load university data
    universities = load_university_urls()
    if not universities:
        logging.error("No universities found to scrape. Exiting.")
        return
    
    logging.info(f"Starting scraping for {len(universities)} universities")
    
    # Validate URLs before processing
    valid_universities = []
    for uni in universities:
        if not uni.get("url"):
            logging.warning(f"Missing URL for {uni.get('name', 'unknown university')}, skipping")
            continue
            
        # Ensure URL has proper format
        url = uni["url"]
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            uni["url"] = url
            logging.info(f"Fixed URL format for {uni['name']}: {url}")
            
        valid_universities.append(uni)
    
    # Extract data
    data = await structured_extraction(valid_universities)
    
    # Save results
    try:
        with open(config.OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logging.info(f"Saved structured data to {config.OUTPUT_FILE}")
        
        # Print a summary
        found_courses = sum(1 for uni in data if uni["courses"] and uni["courses"][0] != "Not found")
        found_requirements = sum(1 for uni in data if uni["admissions_requirements"] and uni["admissions_requirements"][0] != "Not found")
        found_deadlines = sum(1 for uni in data if uni["application_deadlines"] and uni["application_deadlines"][0] != "Not found")
        
        logging.info(f"Scraping Summary:")
        logging.info(f"- Universities processed: {len(data)}/{len(valid_universities)}")
        logging.info(f"- Found course info: {found_courses}/{len(data)}")
        logging.info(f"- Found requirements info: {found_requirements}/{len(data)}")
        logging.info(f"- Found deadline info: {found_deadlines}/{len(data)}")
        
    except Exception as e:
        logging.error(f"Error saving data: {e}")

if __name__ == "__main__":
    asyncio.run(main())
