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
        # Check if file_path is a relative path and we need to check from the repo root
        # Try to find the file from the repo root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.abspath(os.path.join(script_dir, '..'))
        alt_path = os.path.join(repo_root, file_path)
        
        if os.path.exists(alt_path):
            print(f"Found file at alternate path: {alt_path}")
            with open(alt_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        # Try to diagnose the JSON issue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"File content (first 100 chars): {content[:100]}...")
                print(f"File size: {len(content)} bytes")
        except Exception as e:
            print(f"Could not read file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error loading {file_path}: {e}")
        sys.exit(1)

def display_statistics(data):
    """Display statistics about the scraped data."""
    total_universities = len(data)
    
    if total_universities == 0:
        print("No universities data found.")
        return
        
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
    
    print(f"Using data file: {file_path}")
    
    # Load the data
    try:
        data = load_data(file_path)
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)
    
    # List successfully scraped universities
    print("\nUniversities successfully scraped:")
    for uni in data:
        print(f"- {uni['name']}")
    
    # Print a sample of the data - not the whole thing which would be too verbose
    if data and len(data) > 0:
        print("\nSample data from first university:")
        first_uni = data[0]
        sample_data = {
            "name": first_uni["name"],
            "url": first_uni["url"],
            "courses": first_uni.get("courses", [])[:3] if first_uni.get("courses") else [],
            "course_descriptions": first_uni.get("course_descriptions", [])[:2] if first_uni.get("course_descriptions") else [],
            "admissions_requirements": first_uni.get("admissions_requirements", [])[:2] if first_uni.get("admissions_requirements") else [],
            "application_deadlines": first_uni.get("application_deadlines", [])[:2] if first_uni.get("application_deadlines") else []
        }
        print(json.dumps(sample_data, indent=2))
    
    # Display statistics
    print("\n")
    display_statistics(data)

if __name__ == "__main__":
    main()
