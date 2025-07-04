#!/usr/bin/env python3
"""
University Admissions Scraper - CI Version
This script is optimized for running in CI environments.
"""

# Setup critical error handling for imports
try:
    import asyncio
    import json
    import logging
    import time
    import os
    import sys
    from typing import List, Dict, Any, Optional
    from pydantic import BaseModel, Field
except ImportError as e:
    # Write directly to stderr for critical import failures
    import sys
    sys.stderr.write(f"CRITICAL IMPORT ERROR: {e}\n")
    sys.stderr.write(f"Python version: {sys.version}\n")
    sys.stderr.write(f"Path: {sys.path}\n")
    sys.exit(1)

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
    from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
    # Note: We'll use markdown generation strategy to handle content filtering properly
    from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
    from crawl4ai.content_filter_strategy import PruningContentFilter
    import config
except ImportError as e:
    # Write directly to stderr for critical import failures
    sys.stderr.write(f"CRITICAL MODULE IMPORT ERROR: {e}\n")
    sys.stderr.write("Make sure crawl4ai and related packages are installed\n")
    sys.exit(1)

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

# Custom CSS Extraction Strategy with better error handling
class CustomJsonCssExtractionStrategy(JsonCssExtractionStrategy):
    """
    Enhanced JsonCssExtractionStrategy with improved error handling
    """
    def _select_elements(self, element, selector):
        """
        Select elements using a CSS selector.
        
        Args:
            element: The element to select from
            selector: The CSS selector to use
            
        Returns:
            List of selected elements
        """
        try:
            # Use the soup's select method to find elements matching the selector
            if hasattr(element, 'select'):
                return element.select(selector)
            return []
        except Exception as e:
            logging.warning(f"Error selecting elements with selector '{selector}': {str(e)}")
            return []
    
    def _get_element_text(self, element):
        """
        Get the text content of an element.
        
        Args:
            element: The element to get text from
            
        Returns:
            String of text content
        """
        try:
            # First try get_text() method (BeautifulSoup)
            if hasattr(element, 'get_text'):
                return element.get_text()
            # Then try text property
            elif hasattr(element, 'text'):
                return element.text
            # Finally just convert to string
            return str(element)
        except Exception as e:
            logging.warning(f"Error getting element text: {str(e)}")
            return ""
    
    def extract(self, url: str, html_content: str, **kwargs) -> Dict:
        """
        Extract data from HTML content using CSS selectors with improved error handling.
        
        Args:
            url (str): The URL of the page being extracted
            html_content (str): The HTML content to extract data from
            **kwargs: Additional keyword arguments
            
        Returns:
            Dict: A dictionary of extracted data.
        """
        try:
            # Parse the HTML
            parsed_html = self._parse_html(html_content)
            result = {}
            
            # Check if baseSelector exists in schema and handle it
            if hasattr(self, 'baseSelector') and self.baseSelector:
                try:
                    base_elements = self._get_base_elements(parsed_html, self.baseSelector)
                except Exception as e:
                    logging.warning(f"Error getting base elements: {str(e)}")
                    # Continue with document as base instead of failing
                    base_elements = [parsed_html]
            else:
                # Use the whole document as base if no baseSelector
                base_elements = [parsed_html]
            
            # Extract fields from first base element
            if base_elements and len(base_elements) > 0:
                base_element = base_elements[0]
                
                # Process each field in the schema
                for field_name, field_config in self.schema.items():
                    try:
                        # Extract the field data
                        if "selector" in field_config:
                            elements = self._select_elements(base_element, field_config["selector"])
                            if elements:
                                if field_config.get("type") == "list":
                                    result[field_name] = [self._get_element_text(el).strip() for el in elements if self._get_element_text(el).strip()]
                                else:
                                    result[field_name] = self._get_element_text(elements[0]).strip()
                            else:
                                if field_config.get("type") == "list":
                                    result[field_name] = []
                                else:
                                    result[field_name] = None
                    except Exception as e:
                        logging.warning(f"Error extracting field '{field_name}': {str(e)}")
                        # Set empty result for failed field
                        if field_config.get("type") == "list":
                            result[field_name] = []
                        else:
                            result[field_name] = None
            
            return result
        except Exception as e:
            logging.warning(f"CSS extraction error: {str(e)}")
            # Return empty result on failure
            return {}

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
    
    # Enhanced extraction schema with more detailed selectors for Harvard
    if "harvard" in url.lower():
        logging.info(f"Using Harvard-specific extraction schema")
        css_schema = {
            "courses": {
                "selector": ".degree-program-container, .concentrations-container, .field-item, div.programs, ul.course-list, .majors, .degrees, .academics, .course-listings, .field-items a, .field-content a, .main-container a, .main-content a, h3, h2 + ul li, h3 + ul li, .field-items li, .node-content li, #main-content li, .content li, .concentration-list li, #concentrations-list li, .academic-programs li, .academic-departments li",
                "type": "list"
            },
            "course_descriptions": {
                "selector": ".program-description, .concentration-description, .course-description, .field-item p, .field-content p, .main-content p, .academics p, .program-info p, .course-info p, .concentration-info p, .major-description p, .field-description p",
                "type": "list"
            },
            "admissions_requirements": {
                "selector": "div.requirements, .admission-requirements, #admissions-requirements, .requirements-content, .admission, .eligibility, ul.requirements, .application-requirements, .apply-requirements, #application-requirements, .admissions p, .application p, .apply p, #admissions p, #apply p, .admissions li, .application li, .apply li, #admissions li, #apply li",
                "type": "list"
            },
            "application_deadlines": {
                "selector": ".deadlines-container, .important-dates, #application-deadlines, .deadlines-content, div.deadlines, .dates, table.deadlines, .calendar, .timeline, .due-dates, .apply h3, .admissions h3, .deadlines h3, #deadlines h3, .application h3, #application h3, .admissions h4, .application h4, .deadlines h4, .apply h4, .dates h4, .admissions strong, .application strong, time, .date, .deadline-date, .apply p:contains('deadline'), .apply p:contains('January'), .apply p:contains('November'), .apply p:contains('December')",
                "type": "list"
            },
            "early_admission": {
                "selector": ".early-action, .early-decision, #early-admission, .early-admission-content, p:contains('Early Action'), p:contains('Early Decision'), h3:contains('Early Action'), h3:contains('Early Decision'), h4:contains('Early Action'), h4:contains('Early Decision'), div:contains('Early Action'), div:contains('Early Decision'), .apply p:contains('November'), .apply p:contains('December'), .apply li:contains('November'), .apply li:contains('December'), .deadlines p:contains('November'), .deadlines p:contains('December')",
                "type": "list"
            },
            "regular_admission": {
                "selector": ".regular-decision, .regular-admission, #regular-admission, .regular-admission-content, p:contains('Regular Decision'), p:contains('Regular Admission'), h3:contains('Regular Decision'), h3:contains('Regular Admission'), h4:contains('Regular Decision'), h4:contains('Regular Admission'), div:contains('Regular Decision'), div:contains('Regular Admission'), .apply p:contains('January'), .apply li:contains('January'), .deadlines p:contains('January')",
                "type": "list"
            }
        }
    else:
        # Improved default schema for other universities
        css_schema = {
            "courses": {
                "selector": "div.programs, ul.course-list, .majors, .degrees, .academics, .concentration, .field-of-study, .study-areas, .curriculum, .courses, .majors-list, .programs-list, .degrees-list, h3 + ul li, h2 + ul li, .main-content li, .content li, .academic-programs li, .academic-departments li",
                "type": "list"
            },
            "course_descriptions": {
                "selector": ".program-description, .course-description, .major-description, .degree-description, .academics p, .major-info p, .program-info p, .concentration-info p, .curriculum p, .courses p",
                "type": "list"
            },
            "admissions_requirements": {
                "selector": "div.requirements, .admission, .eligibility, ul.requirements, .application-requirements, .admissions-info, .criteria, .prerequisites, .qualifications, .admissions p, .apply p, .requirements p, .admissions li, .apply li, .requirements li",
                "type": "list"
            },
            "application_deadlines": {
                "selector": "div.deadlines, .dates, table.deadlines, .calendar, .timeline, .due-dates, .important-dates, .key-dates, .admissions-calendar, .application-timeline, .deadline, h3:contains('deadline'), h4:contains('deadline'), p:contains('deadline'), li:contains('deadline'), time, .date",
                "type": "list"
            },
            "early_admission": {
                "selector": ".early-action, .early-decision, #early-admission, p:contains('Early Action'), p:contains('Early Decision'), h3:contains('Early Action'), h3:contains('Early Decision'), h4:contains('Early Action'), h4:contains('Early Decision'), .dates:contains('November'), .dates:contains('December'), .deadlines:contains('November'), .deadlines:contains('December')",
                "type": "list"
            },
            "regular_admission": {
                "selector": ".regular-decision, .regular-admission, #regular-admission, p:contains('Regular Decision'), p:contains('Regular Admission'), h3:contains('Regular Decision'), h3:contains('Regular Admission'), h4:contains('Regular Decision'), h4:contains('Regular Admission'), .dates:contains('January'), .deadlines:contains('January')",
                "type": "list"
            }
        }
    
    # Use our custom extractor with better error handling
    css_extractor = CustomJsonCssExtractionStrategy(css_schema)
    
    # Create markdown generator with content filter
    # In Crawl4AI 0.6.3, we need to use markdown_generator instead of content_filter directly
    md_generator = DefaultMarkdownGenerator(
        content_filter=PruningContentFilter()
    )
    
    # Fixed: Use correct parameters for Crawl4AI 0.6.3
    run_config_css = CrawlerRunConfig(
        extraction_strategy=css_extractor,
        markdown_generator=md_generator,  # Use markdown generator with filter
        session_id=f"university-{name}-css",
        cache_mode=CacheMode.BYPASS,  # Use BYPASS instead of PREFER_CACHE
        wait_for="css:body",  # Use "css:" prefix instead of wait_for_selector
        page_timeout=config.DEFAULT_TIMEOUT * 1000  # Convert to milliseconds
    )
    
    # If it's Harvard, we'll also explore some specific pages for deeper data
    additional_pages = []
    if "harvard" in url.lower():
        additional_pages = [
            "https://college.harvard.edu/academics/fields-study",
            "https://college.harvard.edu/admissions/apply",
            "https://college.harvard.edu/admissions/apply/first-year-applicants",
            "https://college.harvard.edu/academics/liberal-arts-sciences/concentrations",
            "https://college.harvard.edu/academics/liberal-arts-sciences",
            "https://college.harvard.edu/admissions/why-harvard/academic-environment",
            "https://college.harvard.edu/admissions/admissions-statistics",
            "https://college.harvard.edu/admissions/why-harvard/affordability"
        ]
    
    try:
        # Use CSS extraction (more reliable in CI environments)
        logging.info(f"Attempting CSS-based extraction for {name}")
        result = await crawler.arun(url=url, config=run_config_css)
        
        # Check if extraction succeeded with CSS
        extracted = {}
        if result.extracted_content and isinstance(result.extracted_content, dict):
            extracted = result.extracted_content
            logging.info(f"CSS extraction successful for {name}")
        else:
            logging.warning(f"CSS extraction failed for {name}")
        
        # Process additional pages for Harvard to get more complete data
        additional_data = {}
        for additional_url in additional_pages:
            try:
                logging.info(f"Extracting additional data from {additional_url}")
                add_result = await crawler.arun(url=additional_url, config=run_config_css)
                
                if add_result.extracted_content and isinstance(add_result.extracted_content, dict):
                    # For each field, combine with existing data
                    for key, value in add_result.extracted_content.items():
                        if key in extracted and isinstance(extracted[key], list) and isinstance(value, list):
                            # Combine lists and remove duplicates
                            combined = extracted[key] + value
                            # Remove duplicates while preserving order
                            seen = set()
                            unique = []
                            for item in combined:
                                item_str = str(item).strip()
                                if item_str and item_str not in seen and item_str != "None" and item_str != "Not found":
                                    seen.add(item_str)
                                    unique.append(item)
                            extracted[key] = unique
                        elif key not in extracted or not extracted[key]:
                            extracted[key] = value
                    
                    logging.info(f"Successfully extracted additional data from {additional_url}")
                else:
                    logging.warning(f"No additional data found at {additional_url}")
            except Exception as e:
                logging.warning(f"Error extracting additional data from {additional_url}: {e}")
        
        # Format the data with cleaner structure
        data = {
            "name": name,
            "url": url,
            "courses": extracted.get("courses", ["Not found"]),
            "course_descriptions": extracted.get("course_descriptions", ["Not found"]),
            "admissions_requirements": extracted.get("admissions_requirements", ["Not found"]),
            "application_deadlines": extracted.get("application_deadlines", ["Not found"]),
            "early_admission": extracted.get("early_admission", ["Not found"]),
            "regular_admission": extracted.get("regular_admission", ["Not found"]),
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # If we got some markdown content but no structured data, we could use that as fallback
        if all(data[key][0] == "Not found" for key in ["courses", "admissions_requirements", "application_deadlines"]):
            logging.warning(f"No structured data found for {name}, using markdown fallback")
            if hasattr(result, 'markdown') and result.markdown:
                # Check if markdown is a string or an object with appropriate attributes
                markdown_text = result.markdown
                if hasattr(result.markdown, 'raw_markdown'):
                    markdown_text = result.markdown.raw_markdown
                elif hasattr(result.markdown, 'fit_markdown') and result.markdown.fit_markdown:
                    markdown_text = result.markdown.fit_markdown
                
                # Simple keyword-based extraction from markdown as last resort
                markdown_lines = markdown_text.split('\n')
                
                # Simple keyword matching
                course_lines = [line.strip() for line in markdown_lines if any(kw in line.lower() for kw in 
                                ['degree', 'course', 'program', 'major', 'bachelor', 'master', 'phd', 'concentration', 'field of study'])]
                if course_lines:
                    data["courses"] = course_lines[:10]  # Increased to capture more courses
                
                description_lines = [line.strip() for line in markdown_lines if len(line.strip()) > 80 and any(kw in line.lower() for kw in 
                                     ['program', 'study', 'academic', 'field', 'course', 'concentration'])]
                if description_lines:
                    data["course_descriptions"] = description_lines[:10]
                
                req_lines = [line.strip() for line in markdown_lines if any(kw in line.lower() for kw in 
                             ['requirement', 'admission', 'prerequisite', 'qualify', 'eligibility', 'gpa', 'test score', 'application process'])]
                if req_lines:
                    data["admissions_requirements"] = req_lines[:10]  # Increased to capture more requirements
                
                deadline_lines = [line.strip() for line in markdown_lines if any(kw in line.lower() for kw in 
                                 ['deadline', 'date', 'application period', 'apply by', 'due by', 'submit by', 'timeline'])]
                if deadline_lines:
                    data["application_deadlines"] = deadline_lines[:10]
                
                early_lines = [line.strip() for line in markdown_lines if any(kw in line.lower() for kw in 
                              ['early action', 'early decision', 'early admission', 'november', 'december'])]
                if early_lines:
                    data["early_admission"] = early_lines[:5]
                
                regular_lines = [line.strip() for line in markdown_lines if any(kw in line.lower() for kw in 
                                ['regular decision', 'regular admission', 'january', 'february', 'march', 'april'])]
                if regular_lines:
                    data["regular_admission"] = regular_lines[:5]
        
        logging.info(f"Successfully extracted data for {name}")
        return data
    except Exception as e:
        logging.error(f"Error extracting data for {name}: {e}")
        return {
            "name": name,
            "url": url,
            "courses": ["Not found"],
            "course_descriptions": ["Not found"],
            "admissions_requirements": ["Not found"],
            "application_deadlines": ["Not found"],
            "early_admission": ["Not found"],
            "regular_admission": ["Not found"],
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e)
        }

async def process_universities(universities: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Process multiple universities with rate limiting and concurrency control."""
    results = []
    
    # Configure the browser with correct parameters for v0.6.3
    browser_config = BrowserConfig(
        headless=True,  # Run in headless mode
        ignore_https_errors=True,  # Ignore HTTPS errors
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        verbose=True  # Enable verbose logging for debugging
    )
    
    # Create connection pool settings based on the number of universities
    # Adjust max_concurrent_tasks based on your system's capabilities
    max_tasks = min(1, len(universities))  # Ultra conservative for CI environment, just one at a time
    
    # Initialize the AsyncWebCrawler with the browser configuration
    async with AsyncWebCrawler(
        config=browser_config,
        max_concurrent_tasks=max_tasks  # This is correct in Crawl4AI 0.6.3
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
    # Double-check imports are available
    try:
        import os
        import sys
        import json
        import logging
        import time
        import asyncio
    except ImportError as e:
        print(f"Critical import error: {e}")
        sys.exit(1)
        
    # Ensure data directory exists
    try:
        os.makedirs(config.DATA_DIR, exist_ok=True)
        print(f"Successfully created/verified data directory: {config.DATA_DIR}")
    except Exception as e:
        print(f"Error creating data directory: {e}")
        # Try alternate approach
        try:
            data_dir = "data"
            os.makedirs(data_dir, exist_ok=True)
            print(f"Created alternate data directory: {data_dir}")
        except Exception as alt_e:
            print(f"Error creating alternate data directory: {alt_e}")
            # Fallback to current directory
            print("Using current directory as fallback")
            config.DATA_DIR = "."
    
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
        # Changed to process all universities in CI mode
        max_unis = len(valid_universities)  # Process all universities in CI mode
        logging.info(f"CI environment detected, processing all {max_unis} universities")
        valid_universities = valid_universities[:max_unis]
    
    # Extract data
    data = await process_universities(valid_universities)
    
    # Save results
    try:
        with open(config.OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logging.info(f"Saved structured data to {config.OUTPUT_FILE}")
        
        # Verify the data was saved correctly
        try:
            with open(config.OUTPUT_FILE, "r", encoding="utf-8") as f:
                test_data = json.load(f)
                logging.info(f"Successfully verified JSON data (contains {len(test_data)} universities)")
        except Exception as e:
            logging.error(f"Error verifying saved data: {e}")
            # Try writing a simplified version as fallback
            simplified_data = []
            for uni in data:
                simplified = {
                    "name": uni["name"],
                    "url": uni["url"],
                    "scraped_at": uni["scraped_at"]
                }
                simplified_data.append(simplified)
            
            # Write simplified data as fallback
            fallback_file = f"{config.DATA_DIR}/simplified_data.json"
            with open(fallback_file, "w", encoding="utf-8") as f:
                json.dump(simplified_data, f, indent=4)
            logging.info(f"Saved simplified data to {fallback_file}")
        
        # Print a summary
        found_courses = sum(1 for uni in data if uni["courses"] and uni["courses"][0] != "Not found")
        found_descriptions = sum(1 for uni in data if uni.get("course_descriptions") and uni["course_descriptions"][0] != "Not found")
        found_requirements = sum(1 for uni in data if uni["admissions_requirements"] and uni["admissions_requirements"][0] != "Not found")
        found_deadlines = sum(1 for uni in data if uni["application_deadlines"] and uni["application_deadlines"][0] != "Not found")
        found_early = sum(1 for uni in data if uni.get("early_admission") and uni["early_admission"][0] != "Not found")
        found_regular = sum(1 for uni in data if uni.get("regular_admission") and uni["regular_admission"][0] != "Not found")
        
        logging.info(f"Scraping Summary:")
        logging.info(f"- Universities processed: {len(data)}/{len(valid_universities)}")
        logging.info(f"- Found course info: {found_courses}/{len(data)}")
        logging.info(f"- Found course descriptions: {found_descriptions}/{len(data)}")
        logging.info(f"- Found requirements info: {found_requirements}/{len(data)}")
        logging.info(f"- Found deadline info: {found_deadlines}/{len(data)}")
        logging.info(f"- Found early admission info: {found_early}/{len(data)}")
        logging.info(f"- Found regular admission info: {found_regular}/{len(data)}")
        
    except Exception as e:
        logging.error(f"Error saving data: {e}")
        # Emergency save using a more direct approach
        try:
            # Re-import os in case there was an issue with the global import
            import os
            import json as emergency_json
            temp_file = os.path.join(os.path.dirname(os.path.abspath(config.OUTPUT_FILE)), "emergency_data.json")
            with open(temp_file, "w", encoding="utf-8") as f:
                for uni in data:
                    f.write(f"{{\"name\": \"{uni['name']}\", \"url\": \"{uni['url']}\"}}\n")
            logging.info(f"Emergency data saved to {temp_file}")
        except Exception as emergency_error:
            logging.error(f"Emergency save also failed: {emergency_error}")

if __name__ == "__main__":
    try:
        print("Starting university scraper script...")
        # Setup basic logging to console first in case config fails
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        logging.info("Initialized logging")
        
        # Run the main async function with proper error handling
        asyncio.run(main())
        logging.info("Script completed successfully")
    except Exception as e:
        # Handle any unexpected top-level exceptions
        error_msg = f"CRITICAL ERROR: {e}"
        # Try to log it properly first
        try:
            logging.error(error_msg)
            logging.error(f"Error type: {type(e).__name__}")
            # Get traceback info
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
        except:
            # If logging fails, print directly to stderr
            sys.stderr.write(f"{error_msg}\n")
            import traceback
            sys.stderr.write(f"Traceback: {traceback.format_exc()}\n")
        
        # Exit with error code
        sys.exit(1)