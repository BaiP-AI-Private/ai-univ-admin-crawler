#!/usr/bin/env python3
"""
Data Enhancement with Claude AI

This script takes the scraped university data and enriches it using Claude AI.
It focuses on organizing and filling in missing details about majors, programs, 
and admission requirements.
"""

import json
import os
import sys
import logging
import argparse
import time
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Import the config file
try:
    import config
    from claude_api import enrich_university_data
except ImportError as e:
    logging.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def load_scraped_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Load the scraped data from JSON file.
    
    Args:
        file_path: Path to the scraped data JSON file
        
    Returns:
        List of university data dictionaries
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Error: File not found at {file_path}")
        
        # Try an alternate path
        alt_path = os.path.join(os.path.dirname(os.path.dirname(file_path)), file_path)
        if os.path.exists(alt_path):
            logging.info(f"Found file at alternate path: {alt_path}")
            with open(alt_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error(f"Error: Invalid JSON in {file_path}")
        sys.exit(1)

def main():
    """Main function to enrich scraped data with Claude AI"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Enrich university data with Claude AI")
    parser.add_argument("--input", default=config.OUTPUT_FILE, help="Path to scraped data JSON file")
    parser.add_argument("--output", default="data/enriched_data.json", help="Path to output JSON file")
    parser.add_argument("--api-key", default=None, help="Claude API key (if not using environment variable)")
    args = parser.parse_args()
    
    # Get API key from arguments or environment variable
    api_key = args.api_key or os.environ.get("CLAUDE_API_KEY")
    if not api_key:
        logging.warning("No Claude API key provided. Using simulation mode.")
    
    # Load the scraped data
    scraped_data = load_scraped_data(args.input)
    logging.info(f"Loaded data for {len(scraped_data)} universities")
    
    # Enrich each university's data
    enriched_data = []
    for university in scraped_data:
        try:
            enriched = enrich_university_data(university, api_key)
            enriched_data.append(enriched)
            logging.info(f"Successfully enriched data for {university.get('name', 'Unknown University')}")
            
            # Add a small delay to avoid rate limiting
            time.sleep(1)
        except Exception as e:
            logging.error(f"Error enriching data for {university.get('name', 'Unknown University')}: {e}")
            # Still add the university to the output, but with minimal enhancement
            enriched_data.append({
                "name": university.get("name", "Unknown University"),
                "url": university.get("url", ""),
                "error": str(e),
                "scraped_data": university,
                "enriched_at": time.strftime("%Y-%m-%d %H:%M:%S")
            })
        
    # Save the enriched data
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(enriched_data, f, indent=2)
        logging.info(f"Saved enriched data to {args.output}")
    except Exception as e:
        logging.error(f"Error saving enriched data: {e}")
        # Try alternate save location
        try:
            alt_output = "enriched_data.json"
            with open(alt_output, 'w', encoding='utf-8') as f:
                json.dump(enriched_data, f, indent=2)
            logging.info(f"Saved enriched data to alternate location: {alt_output}")
        except Exception as e2:
            logging.error(f"Error saving to alternate location: {e2}")
            sys.exit(1)
        
    # Print summary
    logging.info("Enrichment Summary:")
    logging.info(f"- Universities processed: {len(enriched_data)}")
    programs_count = sum(len(uni.get("programs", [])) for uni in enriched_data)
    logging.info(f"- Total programs identified: {programs_count}")
    
if __name__ == "__main__":
    main()
