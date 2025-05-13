#!/usr/bin/env python
"""
Display Scraping Results

This script reads the scraped data from the JSON file and displays it in a readable format.
"""

import json
import os
import sys
from datetime import datetime

def load_data(file_path):
    """Load the scraped data from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        sys.exit(1)

def display_statistics(data):
    """Display statistics about the scraped data."""
    total_universities = len(data)
    found_courses = sum(1 for uni in data if uni.get("courses") and uni["courses"][0] != "Not found")
    found_descriptions = sum(1 for uni in data if uni.get("course_descriptions") and uni["course_descriptions"][0] != "Not found")
    found_requirements = sum(1 for uni in data if uni.get("admissions_requirements") and uni["admissions_requirements"][0] != "Not found")
    found_deadlines = sum(1 for uni in data if uni.get("application_deadlines") and uni["application_deadlines"][0] != "Not found")
    found_early = sum(1 for uni in data if uni.get("early_admission") and uni["early_admission"][0] != "Not found")
    found_regular = sum(1 for uni in data if uni.get("regular_admission") and uni["regular_admission"][0] != "Not found")

    print("Scraping Statistics:")
    print(f"Total universities: {total_universities}")
    print(f"Universities with course info: {found_courses}/{total_universities} ({found_courses/total_universities*100:.1f}%)")
    print(f"Universities with course descriptions: {found_descriptions}/{total_universities} ({found_descriptions/total_universities*100:.1f}%)")
    print(f"Universities with requirements info: {found_requirements}/{total_universities} ({found_requirements/total_universities*100:.1f}%)")
    print(f"Universities with deadline info: {found_deadlines}/{total_universities} ({found_deadlines/total_universities*100:.1f}%)")
    print(f"Universities with early admission info: {found_early}/{total_universities} ({found_early/total_universities*100:.1f}%)")
    print(f"Universities with regular admission info: {found_regular}/{total_universities} ({found_regular/total_universities*100:.1f}%)")

def main():
    """Main function to display scraped data."""
    # Default output file from the scraper
    file_path = os.environ.get("OUTPUT_FILE", "data/admissions_data.json")
    
    # Load the data
    data = load_data(file_path)
    
    # Print header
    print("\nScraping results:")
    print(json.dumps(data, indent=1))
    
    # List successfully scraped universities
    print("\nUniversities successfully scraped:")
    for uni in data:
        print(f"- {uni['name']}")
    
    print("\n")
    # Display statistics
    display_statistics(data)

if __name__ == "__main__":
    main()
