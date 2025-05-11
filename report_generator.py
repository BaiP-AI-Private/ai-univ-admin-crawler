#!/usr/bin/env python
"""
Admissions Data Report Generator

This script analyzes the scraped university admissions data and generates
a comprehensive report, including:
- Overall statistics
- Success rates by data category
- Comparative analysis between universities
- Data quality assessment
"""

import json
import os
import sys
import argparse
from datetime import datetime
from collections import Counter

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

def analyze_completion(data):
    """Analyze the completion rate for each data category."""
    total = len(data)
    courses_found = sum(1 for uni in data if uni.get("courses") and uni["courses"][0] != "Not found")
    req_found = sum(1 for uni in data if uni.get("admissions_requirements") and uni["admissions_requirements"][0] != "Not found")
    deadlines_found = sum(1 for uni in data if uni.get("application_deadlines") and uni["application_deadlines"][0] != "Not found")
    
    all_found = sum(1 for uni in data if 
                   uni.get("courses") and uni["courses"][0] != "Not found" and
                   uni.get("admissions_requirements") and uni["admissions_requirements"][0] != "Not found" and
                   uni.get("application_deadlines") and uni["application_deadlines"][0] != "Not found")
    
    return {
        "total_universities": total,
        "courses_completion": (courses_found / total) * 100 if total else 0,
        "requirements_completion": (req_found / total) * 100 if total else 0,
        "deadlines_completion": (deadlines_found / total) * 100 if total else 0,
        "all_data_completion": (all_found / total) * 100 if total else 0,
        "courses_count": courses_found,
        "requirements_count": req_found,
        "deadlines_count": deadlines_found,
        "complete_data_count": all_found
    }

def analyze_data_quality(data):
    """Assess the quality of extracted data."""
    quality_metrics = {
        "avg_course_length": 0,
        "avg_requirements_length": 0,
        "avg_deadlines_length": 0,
        "detailed_courses": 0,
        "detailed_requirements": 0,
        "detailed_deadlines": 0
    }
    
    # Calculate average lengths
    course_lengths = [len(str(c)) for uni in data for c in uni.get("courses", []) if c != "Not found"]
    req_lengths = [len(str(r)) for uni in data for r in uni.get("admissions_requirements", []) if r != "Not found"]
    deadline_lengths = [len(str(d)) for uni in data for d in uni.get("application_deadlines", []) if d != "Not found"]
    
    quality_metrics["avg_course_length"] = sum(course_lengths) / len(course_lengths) if course_lengths else 0
    quality_metrics["avg_requirements_length"] = sum(req_lengths) / len(req_lengths) if req_lengths else 0
    quality_metrics["avg_deadlines_length"] = sum(deadline_lengths) / len(deadline_lengths) if deadline_lengths else 0
    
    # Calculate detailed vs sparse content
    quality_metrics["detailed_courses"] = sum(1 for l in course_lengths if l > 100)
    quality_metrics["detailed_requirements"] = sum(1 for l in req_lengths if l > 100)
    quality_metrics["detailed_deadlines"] = sum(1 for l in deadline_lengths if l > 100)
    
    return quality_metrics

def find_universities_with_issues(data):
    """Identify universities with missing or problematic data."""
    universities_with_issues = []
    
    for uni in data:
        issues = []
        
        # Check for missing data categories
        if not uni.get("courses") or uni["courses"][0] == "Not found":
            issues.append("Missing course information")
        
        if not uni.get("admissions_requirements") or uni["admissions_requirements"][0] == "Not found":
            issues.append("Missing admissions requirements")
            
        if not uni.get("application_deadlines") or uni["application_deadlines"][0] == "Not found":
            issues.append("Missing application deadlines")
        
        # Check for potentially low-quality data
        if uni.get("courses") and uni["courses"][0] != "Not found":
            course_text = " ".join([str(c) for c in uni["courses"]])
            if len(course_text) < 50:
                issues.append("Very brief course information")
        
        if uni.get("admissions_requirements") and uni["admissions_requirements"][0] != "Not found":
            req_text = " ".join([str(r) for r in uni["admissions_requirements"]])
            if len(req_text) < 50:
                issues.append("Very brief admissions requirements")
        
        if issues:
            universities_with_issues.append({
                "name": uni["name"],
                "url": uni["url"],
                "issues": issues
            })
    
    return universities_with_issues

def generate_report(data, output_format="text"):
    """Generate the full report in the specified format."""
    completion_metrics = analyze_completion(data)
    quality_metrics = analyze_data_quality(data)
    universities_with_issues = find_universities_with_issues(data)
    
    report_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "completion_metrics": completion_metrics,
        "quality_metrics": quality_metrics,
        "universities_with_issues": universities_with_issues
    }
    
    if output_format == "json":
        # Output as structured JSON
        return json.dumps(report_data, indent=2)
    else:
        # Output as human-readable text report
        report = []
        report.append("# University Admissions Scraper Report")
        report.append(f"Generated on: {report_data['timestamp']}")
        report.append("")
        report.append("## Summary Statistics")
        report.append(f"- Total Universities: {completion_metrics['total_universities']}")
        report.append(f"- Universities with Complete Data: {completion_metrics['complete_data_count']} ({completion_metrics['all_data_completion']:.1f}%)")
        report.append("")
        report.append("## Data Completion Rates")
        report.append(f"- Courses Information: {completion_metrics['courses_count']} universities ({completion_metrics['courses_completion']:.1f}%)")
        report.append(f"- Admissions Requirements: {completion_metrics['requirements_count']} universities ({completion_metrics['requirements_completion']:.1f}%)")
        report.append(f"- Application Deadlines: {completion_metrics['deadlines_count']} universities ({completion_metrics['deadlines_completion']:.1f}%)")
        report.append("")
        report.append("## Data Quality Metrics")
        report.append(f"- Average Course Description Length: {quality_metrics['avg_course_length']:.1f} characters")
        report.append(f"- Average Requirements Description Length: {quality_metrics['avg_requirements_length']:.1f} characters")
        report.append(f"- Average Deadlines Description Length: {quality_metrics['avg_deadlines_length']:.1f} characters")
        report.append(f"- Detailed Course Descriptions: {quality_metrics['detailed_courses']}")
        report.append(f"- Detailed Requirements Descriptions: {quality_metrics['detailed_requirements']}")
        report.append(f"- Detailed Deadlines Descriptions: {quality_metrics['detailed_deadlines']}")
        report.append("")
        
        if universities_with_issues:
            report.append("## Universities with Data Issues")
            for uni in universities_with_issues:
                report.append(f"- {uni['name']}")
                for issue in uni['issues']:
                    report.append(f"  * {issue}")
                report.append("")
        
        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Generate a report from university admissions data")
    parser.add_argument("--input", "-i", default="data/admissions_data.json", help="Path to the JSON data file")
    parser.add_argument("--output", "-o", help="Path to save the report (default: stdout)")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="Output format (text or json)")
    args = parser.parse_args()
    
    # Load the data
    data = load_data(args.input)
    
    # Generate the report
    report = generate_report(data, args.format)
    
    # Output the report
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)

if __name__ == "__main__":
    main()
