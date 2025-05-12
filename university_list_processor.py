#!/usr/bin/env python
"""
University List Processor - AI Agent

This script processes a text file containing university names and converts it to a structured
JSON file with proper URLs for web scraping. It uses pattern matching, domain knowledge,
and web verification to generate accurate university admissions URLs.

Usage:
    python university_list_processor.py --input list_of_universities.txt --output data/universities.json
"""

import argparse
import json
import logging
import os
import re
import sys
import urllib.parse
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Common URL patterns for university admissions pages
ADMISSION_URL_PATTERNS = [
    "{base_url}/admissions",
    "{base_url}/admission",
    "{base_url}/apply",
    "{base_url}/undergraduate/admissions",
    "{base_url}/undergraduate/admission",
    "{base_url}/undergraduate/apply",
    "{base_url}/admissions/undergraduate",
    "{base_url}/admissions/apply",
    "{base_url}/admissions/freshman",
    "{base_url}/future-students",
]

# Common domain patterns for universities
DOMAIN_PATTERNS = [
    "{name_slug}.edu",
    "www.{name_slug}.edu",
    "{name_slug}.ac.uk",
    "www.{name_slug}.ac.uk",
    "{name_slug}.edu.au",
    "www.{name_slug}.edu.au",
    "{name_slug}.ca",
    "www.{name_slug}.ca",
]

# Known university domains that don't follow standard patterns
KNOWN_UNIVERSITIES = {
    "harvard": "college.harvard.edu/admissions",
    "harvard university": "college.harvard.edu/admissions",
    "mit": "www.admissions.mit.edu",
    "massachusetts institute of technology": "www.admissions.mit.edu",
    "stanford": "admission.stanford.edu/apply",
    "stanford university": "admission.stanford.edu/apply",
    "princeton": "admission.princeton.edu",
    "princeton university": "admission.princeton.edu",
    "yale": "admissions.yale.edu",
    "yale university": "admissions.yale.edu",
    "uc berkeley": "admissions.berkeley.edu",
    "berkeley": "admissions.berkeley.edu",
    "university of california berkeley": "admissions.berkeley.edu",
    "university of michigan": "admissions.umich.edu",
    "michigan": "admissions.umich.edu",
    "cornell": "admissions.cornell.edu",
    "cornell university": "admissions.cornell.edu",
    "columbia": "undergrad.admissions.columbia.edu",
    "columbia university": "undergrad.admissions.columbia.edu",
    "university of chicago": "college.uchicago.edu/admissions",
    "uchicago": "college.uchicago.edu/admissions",
    "caltech": "www.admissions.caltech.edu",
    "california institute of technology": "www.admissions.caltech.edu",
    "nyu": "www.nyu.edu/admissions/undergraduate-admissions",
    "new york university": "www.nyu.edu/admissions/undergraduate-admissions",
    "duke": "admissions.duke.edu",
    "duke university": "admissions.duke.edu",
}

def create_name_slug(university_name: str) -> str:
    """Generate a URL-friendly slug from a university name."""
    # Replace common words in university names
    replacements = {
        "university": "u",
        "institute": "inst",
        "technology": "tech",
        "college": "coll",
        "of": "",
        "and": "",
        "the": "",
    }
    
    # Apply replacements
    name_lower = university_name.lower()
    for old, new in replacements.items():
        name_lower = re.sub(r'\b' + old + r'\b', new, name_lower)
    
    # Remove special characters and create slug
    name_slug = re.sub(r'[^a-z0-9]+', '', name_lower)
    
    return name_slug

def guess_university_url(university_name: str) -> List[str]:
    """Generate potential URLs for a university based on its name."""
    potential_urls = []
    
    # Check if this is a known university
    name_lower = university_name.lower()
    if name_lower in KNOWN_UNIVERSITIES:
        return [f"https://{KNOWN_UNIVERSITIES[name_lower]}"]
    
    # Create name slug
    name_slug = create_name_slug(university_name)
    
    # Generate potential domains
    domains = []
    for pattern in DOMAIN_PATTERNS:
        domains.append(pattern.format(name_slug=name_slug))
    
    # Special case for universities with "University of X" format
    if "university of" in name_lower or "u of" in name_lower:
        location = re.sub(r'^.*university of\s+|^.*u of\s+', '', name_lower).strip()
        location_slug = create_name_slug(location)
        if location_slug:
            domains.append(f"{location_slug}.edu")
            domains.append(f"www.{location_slug}.edu")
    
    # Generate full URLs using domains and admission URL patterns
    for domain in domains:
        base_url = f"https://{domain}"
        for pattern in ADMISSION_URL_PATTERNS:
            potential_urls.append(pattern.format(base_url=base_url))
    
    return potential_urls

def verify_url(url: str, timeout: int = 5) -> Tuple[bool, Optional[str]]:
    """Verify if a URL exists and is an admissions page."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        
        # Check if redirected to a different URL
        final_url = response.url
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check if this is likely an admissions page
            title_text = soup.title.text.lower() if soup.title else ""
            body_text = " ".join([p.text.lower() for p in soup.find_all('p', limit=5)])
            
            admission_keywords = ['admission', 'apply', 'application', 'undergraduate', 'freshman', 'prospective', 'student']
            
            # Count how many admission-related keywords appear in the title and body
            keyword_count = sum(1 for keyword in admission_keywords if keyword in title_text)
            keyword_count += sum(1 for keyword in admission_keywords if keyword in body_text)
            
            if keyword_count >= 2:
                return True, final_url
            
            # Fallback - if URL contains admissions-related terms, return it anyway
            if any(keyword in final_url.lower() for keyword in ['admission', 'apply']):
                return True, final_url
                
            return False, None
        return False, None
    except Exception as e:
        logging.debug(f"Error verifying {url}: {e}")
        return False, None

def find_best_url(university_name: str) -> Optional[str]:
    """Find the best admissions URL for a university using multiple strategies."""
    potential_urls = guess_university_url(university_name)
    
    logging.info(f"Checking {len(potential_urls)} potential URLs for '{university_name}'")
    
    # Try each URL and return the first valid one
    for url in potential_urls:
        logging.debug(f"Checking URL: {url}")
        is_valid, final_url = verify_url(url)
        if is_valid:
            logging.info(f"Found valid URL for '{university_name}': {final_url}")
            return final_url
    
    # If no URL is valid, try a Google search (simplified version)
    try:
        search_query = f"{university_name} university admissions undergraduate"
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract links from search results
            links = []
            for a in soup.select('a'):
                href = a.get('href', '')
                if '/url?q=' in href and not 'google' in href:
                    # Extract URL from Google's redirect URL
                    url = href.split('/url?q=')[1].split('&')[0]
                    url = urllib.parse.unquote(url)
                    links.append(url)
            
            # Check each link
            for link in links[:3]:  # Check only first 3 links
                is_valid, final_url = verify_url(link)
                if is_valid:
                    logging.info(f"Found valid URL from search for '{university_name}': {final_url}")
                    return final_url
    except Exception as e:
        logging.warning(f"Error during search for '{university_name}': {e}")
    
    logging.warning(f"Could not find valid URL for '{university_name}', using fallback")
    
    # Fallback to a standard pattern if all else fails
    name_slug = create_name_slug(university_name)
    return f"https://www.{name_slug}.edu/admissions"

def process_university_list(input_file: str, output_file: str):
    """Process a text file of university names and create a JSON file with URLs."""
    universities = []
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Read input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        logging.error(f"Error reading input file: {e}")
        return False
    
    # Process each university
    for line in lines:
        university_name = line.strip()
        if not university_name:
            continue
        
        logging.info(f"Processing: {university_name}")
        
        # Find the best URL for this university
        url = find_best_url(university_name)
        
        if url:
            universities.append({
                "name": university_name,
                "url": url
            })
    
    # Save to JSON file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(universities, f, indent=2)
        logging.info(f"Successfully saved {len(universities)} universities to {output_file}")
        return True
    except Exception as e:
        logging.error(f"Error writing output file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Convert a list of universities to a JSON file with URLs")
    parser.add_argument("--input", "-i", required=False, help="Input text file with university names")
    parser.add_argument("--output", "-o", default="data/universities.json", help="Output JSON file path")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Use config values if available, otherwise use command line arguments
    try:
        import config
        input_file = args.input if args.input else config.UNIVERSITIES_LIST_FILE
        output_file = args.output if args.output else config.INPUT_FILE
    except (ImportError, AttributeError):
        # If config.py doesn't exist or doesn't have required attributes
        if not args.input:
            print("Error: --input parameter is required when config.py is not available")
            return 1
        input_file = args.input
        output_file = args.output
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    success = process_university_list(input_file, output_file)
    
    if success:
        print(f"Successfully processed {input_file} and created {output_file}")
        return 0
    else:
        print(f"Failed to process {input_file}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
