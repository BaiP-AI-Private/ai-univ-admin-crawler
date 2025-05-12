import asyncio
import json
import logging
import time
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai.content_filter_strategy import PruningContentFilter
import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Define the extraction schema using Pydantic v2
class UniversityData(BaseModel):
    """Schema for university data extraction"""
    courses: List[str] = Field(default_factory=list, description="List of courses or programs offered")
    admissions_requirements: List[str] = Field(default_factory=list, description="List of admissions requirements")
    application_deadlines: List[str] = Field(default_factory=list, description="List of application deadlines")

def load_university_urls(filename=config.INPUT_FILE):
    """Loads university URLs dynamically from JSON."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load universities JSON file: {e}")
        return []

async def extract_university_data(crawler: AsyncWebCrawler, uni: Dict[str, str]) -> Dict[str, Any]:
    """Extract data from a university website using Crawl4AI."""
    url = uni["url"]
    name = uni["name"]
    
    logging.info(f"Processing {name} at {url}")
    
    # Configure the extraction strategy using CSS since we're in CI
    css_schema = {
        "courses": {
            "selector": "div.programs, ul.course-list, .majors, .degrees, .academics",
            "type": "list"
        },
        "admissions_requirements": {
            "selector": "div.requirements, .admission, .eligibility, ul.requirements",
            "type": "list"
        },
        "application_deadlines": {
            "selector": "div.deadlines, .dates, table.deadlines, .calendar",
            "type": "list"
        }
    }
    
    css_extractor = JsonCssExtractionStrategy(css_schema)
    
    # First try with CSS extractor which is more reliable in CI environments
    run_config_css = CrawlerRunConfig(
        extraction_strategy=css_extractor,
        content_filter=PruningContentFilter(),
        session_id=f"university-{name}-css",
        cache_mode=CacheMode.PREFER_CACHE,
        wait_for_selector="body",
        follow_redirects=True,
        # Set timeout in CrawlerRunConfig instead of BrowserConfig
        page_timeout=config.DEFAULT_TIMEOUT * 1000  # Convert to milliseconds
    )
    
    try:
        # Use CSS extraction (more reliable in CI environments)
        logging.info(f"Attempting CSS-based extraction for {name}")
        result = await crawler.arun(url=url, config=run_config_css)
        
        # Check if extraction succeeded with CSS
        if result.extracted_content and isinstance(result.extracted_content, dict):
            extracted = result.extracted_content
            logging.info(f"CSS extraction successful for {name}")
        else:
            logging.warning(f"CSS extraction failed for {name}")
            extracted = {}
        
        # Format the data with cleaner structure
        data = {
            "name": name,
            "url": url,
            "courses": extracted.get("courses", ["Not found"]),
            "admissions_requirements": extracted.get("admissions_requirements", ["Not found"]),
            "application_deadlines": extracted.get("application_deadlines", ["Not found"]),
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # If we got some markdown content but no structured data, we could use that as fallback
        if all(data[key] == ["Not found"] for key in ["courses", "admissions_requirements", "application_deadlines"]):
            logging.warning(f"No structured data found for {name}, using markdown fallback")
            if result.markdown:
                # Very simple keyword-based extraction from markdown as last resort
                markdown_lines = result.markdown.split('\n')
                
                # Simple keyword matching
                course_lines = [line.strip() for line in markdown_lines if any(kw in line.lower() for kw in 
                                ['degree', 'course', 'program', 'major', 'bachelor', 'master', 'phd'])]
                if course_lines:
                    data["courses"] = course_lines[:5]  # Limit to first 5 matches
                
                req_lines = [line.strip() for line in markdown_lines if any(kw in line.lower() for kw in 
                             ['requirement', 'admission', 'prerequisite', 'qualify', 'eligibility', 'gpa', 'test score'])]
                if req_lines:
                    data["admissions_requirements"] = req_lines[:5]
                
                deadline_lines = [line.strip() for line in markdown_lines if any(kw in line.lower() for kw in 
                                 ['deadline', 'date', 'application period', 'apply by', 'due by', 'submit by'])]
                if deadline_lines:
                    data["application_deadlines"] = deadline_lines[:5]
        
        logging.info(f"Successfully extracted data for {name}")
        return data
    except Exception as e:
        logging.error(f"Error extracting data for {name}: {e}")
        return {
            "name": name,
            "url": url,
            "courses": ["Not found"],
            "admissions_requirements": ["Not found"],
            "application_deadlines": ["Not found"],
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e)
        }

async def process_universities(universities: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Process multiple universities with rate limiting and concurrency control."""
    results = []
    
    # Configure the browser
    browser_config = BrowserConfig(
        headless=True,  # Run in headless mode
        ignore_https_errors=True,  # Ignore HTTPS errors
        # Remove timeout from here - it's not a valid parameter for BrowserConfig
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    )
    
    # Create connection pool settings based on the number of universities
    # Adjust max_concurrent_tasks based on your system's capabilities
    max_tasks = min(2, len(universities))  # Very conservative setting for CI environment
    
    # Initialize the AsyncWebCrawler with the browser configuration
    async with AsyncWebCrawler(
        config=browser_config,
        verbose=True,
        max_concurrent_tasks=max_tasks
    ) as crawler:
        # Process universities in batches to control concurrency
        for i in range(0, len(universities), max_tasks):
            batch = universities[i:i+max_tasks]
            logging.info(f"Processing batch {i//max_tasks + 1} with {len(batch)} universities")
            
            # Create tasks for the batch
            tasks = [extract_university_data(crawler, uni) for uni in batch]
            
            # Run tasks concurrently
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            
            # Add a small delay between batches to avoid overwhelming the system
            if i + max_tasks < len(universities):
                await asyncio.sleep(config.RATE_LIMIT)
    
    return results

async def main():
    # Ensure data directory exists
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
    
    # Use a smaller sample for CI to make sure it completes faster
    if os.environ.get('CI'):
        max_unis = min(2, len(valid_universities))
        logging.info(f"CI environment detected, limiting to {max_unis} universities")
        valid_universities = valid_universities[:max_unis]
    
    # Extract data
    data = await process_universities(valid_universities)
    
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
