#!/usr/bin/env python3
"""
Claude API Integration

This script provides functions for interacting with Claude AI API to enhance 
university admissions data.
"""

import json
import os
import requests
import time
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class ClaudeAIClient:
    """Client for interacting with the Claude AI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Claude AI client.
        
        Args:
            api_key: API key for Claude AI. If not provided, tries to get from env.
        """
        self.api_key = api_key or os.environ.get("CLAUDE_API_KEY")
        if not self.api_key:
            logging.warning("No Claude API key provided. Using simulation mode.")
            self.simulation_mode = True
        else:
            self.simulation_mode = False
            
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-opus-20240229"  # Use the most capable model for accurate data
    
    def query_claude(self, university_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query Claude AI to enhance university data.
        
        Args:
            university_data: Dictionary containing the scraped university data
            
        Returns:
            Enhanced university data dictionary
        """
        # If in simulation mode, just organize the existing data
        if self.simulation_mode:
            return self._simulate_enrichment(university_data)
        
        # Extract data to construct the prompt
        university_name = university_data.get("name", "Unknown University")
        courses = university_data.get("courses", ["Not found"])
        requirements = university_data.get("admissions_requirements", ["Not found"])
        deadlines = university_data.get("application_deadlines", ["Not found"])
        early = university_data.get("early_admission", ["Not found"])
        regular = university_data.get("regular_admission", ["Not found"])
        
        # Build a detailed prompt for Claude
        prompt = f"""
I have scraped data about {university_name}'s academic programs and admissions requirements. 
I need you to organize this information into a clear, structured format with complete details.

Here's the data I have:

COURSES/PROGRAMS:
{json.dumps(courses, indent=2)}

ADMISSIONS REQUIREMENTS:
{json.dumps(requirements, indent=2)}

APPLICATION DEADLINES:
{json.dumps(deadlines, indent=2)}

EARLY ADMISSION:
{json.dumps(early, indent=2)}

REGULAR ADMISSION:
{json.dumps(regular, indent=2)}

Please organize this information into a well-structured JSON object with the following schema:
{{
  "name": "University Name",
  "programs": [
    {{
      "name": "Program Name",
      "description": "Program description",
      "degree_type": "Bachelor's/Master's/etc.",
      "department": "Department name if available"
    }}
  ],
  "application_process": {{
    "early_admission": {{
      "deadline": "Date",
      "notification_date": "Date",
      "restrictions": "Any restrictions for early applicants"
    }},
    "regular_admission": {{
      "deadline": "Date",
      "notification_date": "Date"
    }},
    "general_requirements": [
      "Requirement 1",
      "Requirement 2"
    ]
  }}
}}

If any information is missing or unclear, please indicate this in your response.
Please ensure any duplicated or similar items are merged or removed.
Focus on identifying real degree programs and majors, not generic links or other page content.
"""

        # Prepare the request
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000  # Limit response size
        }
        
        try:
            # Make the API request
            response = requests.post(self.api_url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                # Extract the content from the response
                if "content" in result and len(result["content"]) > 0:
                    enriched_text = result["content"][0]["text"]
                    
                    # Try to extract JSON from the response
                    try:
                        # Find JSON block in response
                        json_start = enriched_text.find("{")
                        json_end = enriched_text.rfind("}") + 1
                        if json_start >= 0 and json_end > json_start:
                            json_str = enriched_text[json_start:json_end]
                            enriched_data = json.loads(json_str)
                            
                            # Add additional metadata
                            enriched_data["url"] = university_data.get("url", "")
                            enriched_data["scraped_data"] = university_data
                            enriched_data["enriched_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                            
                            return enriched_data
                    except json.JSONDecodeError:
                        logging.warning(f"Failed to parse JSON from Claude response for {university_name}")
                
                # If we couldn't extract JSON, fall back to simulation mode
                logging.warning(f"Invalid response format from Claude API for {university_name}")
                return self._simulate_enrichment(university_data)
            else:
                logging.error(f"API request failed with status {response.status_code}: {response.text}")
                # Fall back to simulation mode
                return self._simulate_enrichment(university_data)
        except Exception as e:
            logging.error(f"Error querying Claude API: {e}")
            # Fall back to simulation mode
            return self._simulate_enrichment(university_data)
    
    def _simulate_enrichment(self, university_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate Claude enrichment by organizing existing data.
        Used when API key is not available or API call fails.
        
        Args:
            university_data: Dictionary containing the scraped university data
            
        Returns:
            Enhanced university data dictionary
        """
        # Extract the name and URL
        university_name = university_data.get("name", "Unknown University")
        university_url = university_data.get("url", "")
        
        logging.info(f"Simulating AI enrichment for {university_name}")
        
        # Create a template for the enriched output
        enriched = {
            "name": university_name,
            "url": university_url,
            "programs": [],
            "application_process": {
                "early_admission": {},
                "regular_admission": {},
                "general_requirements": []
            },
            "scraped_data": university_data,  # Keep the original data for reference
            "enriched_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Organize courses/programs
        courses = university_data.get("courses", ["Not found"])
        if courses and courses[0] != "Not found":
            # Process the courses
            for course in courses:
                if isinstance(course, str) and course.strip() and not course.startswith("* ["):
                    # Filter out some common non-course text
                    if any(skip in course.lower() for skip in ["accepts", "committed", "university is", "chart", "code of conduct"]):
                        continue
                        
                    # Try to identify the degree type
                    degree_type = "Bachelor's"  # Default
                    if "master" in course.lower():
                        degree_type = "Master's"
                    elif "phd" in course.lower() or "doctorate" in course.lower():
                        degree_type = "PhD"
                    
                    # Add to programs list
                    enriched["programs"].append({
                        "name": course.strip(),
                        "description": "",  # Would be filled by Claude API in real implementation
                        "degree_type": degree_type,
                        "department": ""  # Would be filled by Claude API in real implementation
                    })
        
        # Organize admission requirements
        req_texts = university_data.get("admissions_requirements", ["Not found"])
        if req_texts and req_texts[0] != "Not found":
            # Process requirements
            for req in req_texts:
                if isinstance(req, str) and req.strip() and "skip to" not in req.lower() and not req.startswith("* ["):
                    enriched["application_process"]["general_requirements"].append(req.strip())
        
        # Process early admission details
        early_texts = university_data.get("early_admission", ["Not found"])
        if early_texts and early_texts[0] != "Not found":
            # Extract deadline and notification date
            deadline = ""
            notification = ""
            restrictions = ""
            
            for text in early_texts:
                if isinstance(text, str):
                    if "november" in text.lower():
                        deadline = text.strip()
                    if "december" in text.lower() and "notified" in text.lower():
                        notification = text.strip()
                    if "restrictive" in text.lower():
                        restrictions = "Restrictive early action"
                    
            enriched["application_process"]["early_admission"] = {
                "deadline": deadline,
                "notification_date": notification,
                "restrictions": restrictions
            }
        
        # Process regular admission details
        regular_texts = university_data.get("regular_admission", ["Not found"])
        if regular_texts and regular_texts[0] != "Not found":
            # Extract deadline and notification date
            deadline = ""
            notification = ""
            
            for text in regular_texts:
                if isinstance(text, str):
                    if "january" in text.lower():
                        deadline = text.strip()
                    if "march" in text.lower() and "notified" in text.lower():
                        notification = text.strip()
                    
            enriched["application_process"]["regular_admission"] = {
                "deadline": deadline,
                "notification_date": notification
            }
        
        return enriched


def enrich_university_data(university_data: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Wrapper function to enrich university data using Claude AI.
    
    Args:
        university_data: Dictionary containing the scraped university data
        api_key: Optional API key for Claude AI
        
    Returns:
        Enhanced university data dictionary
    """
    client = ClaudeAIClient(api_key)
    return client.query_claude(university_data)
