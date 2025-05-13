#!/usr/bin/env python3
"""
Generate University Admissions Report

This script generates a human-readable report from the enriched university data.
"""

import json
import argparse
import os
import sys
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def load_enriched_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Load the enriched data from JSON file.
    
    Args:
        file_path: Path to the enriched data JSON file
        
    Returns:
        List of university data dictionaries
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Error: File not found at {file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error(f"Error: Invalid JSON in {file_path}")
        sys.exit(1)

def generate_report(university_data: Dict[str, Any]) -> str:
    """
    Generate a human-readable report for a university.
    
    Args:
        university_data: Dictionary containing the enriched university data
        
    Returns:
        Markdown-formatted report
    """
    university_name = university_data.get("name", "Unknown University")
    university_url = university_data.get("url", "")
    
    # Start the report
    report = f"# {university_name} Admissions Report\n\n"
    report += f"Website: [{university_name}]({university_url})\n\n"
    
    # Add programs section
    report += "## Academic Programs\n\n"
    programs = university_data.get("programs", [])
    if programs:
        for program in programs:
            program_name = program.get("name", "Unknown Program")
            program_type = program.get("degree_type", "")
            program_dept = program.get("department", "")
            program_desc = program.get("description", "")
            
            report += f"### {program_name}\n\n"
            if program_type:
                report += f"**Degree Type:** {program_type}\n\n"
            if program_dept:
                report += f"**Department:** {program_dept}\n\n"
            if program_desc:
                report += f"{program_desc}\n\n"
    else:
        report += "*No program information available.*\n\n"
    
    # Add application process section
    report += "## Application Process\n\n"
    app_process = university_data.get("application_process", {})
    
    # Early admission
    report += "### Early Admission\n\n"
    early_admission = app_process.get("early_admission", {})
    if early_admission:
        deadline = early_admission.get("deadline", "")
        notification = early_admission.get("notification_date", "")
        restrictions = early_admission.get("restrictions", "")
        
        if deadline:
            report += f"**Deadline:** {deadline}\n\n"
        if notification:
            report += f"**Notification Date:** {notification}\n\n"
        if restrictions:
            report += f"**Restrictions:** {restrictions}\n\n"
    else:
        report += "*No early admission information available.*\n\n"
    
    # Regular admission
    report += "### Regular Admission\n\n"
    regular_admission = app_process.get("regular_admission", {})
    if regular_admission:
        deadline = regular_admission.get("deadline", "")
        notification = regular_admission.get("notification_date", "")
        
        if deadline:
            report += f"**Deadline:** {deadline}\n\n"
        if notification:
            report += f"**Notification Date:** {notification}\n\n"
    else:
        report += "*No regular admission information available.*\n\n"
    
    # General requirements
    report += "### General Requirements\n\n"
    requirements = app_process.get("general_requirements", [])
    if requirements:
        for req in requirements:
            report += f"- {req}\n"
        report += "\n"
    else:
        report += "*No general requirements information available.*\n\n"
    
    # Add metadata
    report += "---\n\n"
    report += "*This report was generated from data enriched at " + university_data.get("enriched_at", "") + "*\n"
    
    return report

def main():
    """Main function to generate reports from enriched data"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate university admissions reports")
    parser.add_argument("--input", default="data/enriched_data.json", help="Path to enriched data JSON file")
    parser.add_argument("--output-dir", default="reports", help="Directory to save reports")
    args = parser.parse_args()
    
    # Load the enriched data
    enriched_data = load_enriched_data(args.input)
    logging.info(f"Loaded data for {len(enriched_data)} universities")
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate reports for each university
    for university in enriched_data:
        try:
            university_name = university.get("name", "Unknown University")
            
            # Generate a safe filename
            safe_name = university_name.replace(" ", "_").replace("'", "").replace("&", "and").lower()
            file_path = os.path.join(args.output_dir, f"{safe_name}_report.md")
            
            # Generate the report
            report = generate_report(university)
            
            # Save the report
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report)
                
            logging.info(f"Generated report for {university_name}")
        except Exception as e:
            logging.error(f"Error generating report for {university.get('name', 'Unknown University')}: {e}")
    
    # Create an index file
    index_path = os.path.join(args.output_dir, "index.md")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("# University Admissions Reports\n\n")
        f.write("## Available Reports\n\n")
        
        for university in sorted(enriched_data, key=lambda x: x.get("name", "Unknown")):
            university_name = university.get("name", "Unknown University")
            safe_name = university_name.replace(" ", "_").replace("'", "").replace("&", "and").lower()
            report_file = f"{safe_name}_report.md"
            
            f.write(f"- [{university_name}]({report_file})\n")
    
    logging.info(f"Generated {len(enriched_data)} reports in {args.output_dir}")
    logging.info(f"Index file created at {index_path}")

if __name__ == "__main__":
    main()
