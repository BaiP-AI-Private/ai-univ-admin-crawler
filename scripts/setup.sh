#!/bin/bash
# University Admissions Scraper Setup Script
# This script sets up the environment and prepares the crawler for operation

# Text formatting
BOLD="\033[1m"
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
RESET="\033[0m"

# Print header
echo -e "${BOLD}${BLUE}========================================${RESET}"
echo -e "${BOLD}${BLUE}  University Admissions Scraper Setup   ${RESET}"
echo -e "${BOLD}${BLUE}========================================${RESET}\n"

# Check Python version
echo -e "${BOLD}Checking Python version...${RESET}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
        echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${RESET}"
        PYTHON_CMD="python3"
    else
        echo -e "${YELLOW}⚠ Python $PYTHON_VERSION detected, but Python 3.9+ is recommended${RESET}"
        echo -e "   Continuing, but you may encounter issues."
        PYTHON_CMD="python3"
    fi
else
    echo -e "${RED}✗ Python 3 not found!${RESET}"
    echo -e "Please install Python 3.9 or higher from https://www.python.org/downloads/"
    exit 1
fi

# Create virtual environment
echo -e "\n${BOLD}Setting up virtual environment...${RESET}"
if [ ! -d "venv" ]; then
    echo "Creating new virtual environment..."
    $PYTHON_CMD -m venv venv
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to create virtual environment!${RESET}"
        echo "Try installing venv with: sudo apt-get install python3-venv (Ubuntu/Debian)"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Virtual environment created${RESET}"
else
    echo -e "${YELLOW}⚠ Virtual environment already exists${RESET}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Unix/Linux/Mac
    source venv/bin/activate
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to activate virtual environment!${RESET}"
    exit 1
fi
echo -e "${GREEN}✓ Virtual environment activated${RESET}"

# Install dependencies
echo -e "\n${BOLD}Installing dependencies...${RESET}"
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to install dependencies!${RESET}"
    exit 1
fi
echo -e "${GREEN}✓ Dependencies installed successfully${RESET}"

# Create directories
echo -e "\n${BOLD}Setting up directory structure...${RESET}"
mkdir -p data
mkdir -p dashboard
mkdir -p logs

# Create the dashboard HTML file if it doesn't exist
if [ ! -f "dashboard/index.html" ]; then
    echo "Creating dashboard files..."
    cat > dashboard/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>University Admissions Scraper Dashboard</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
        }
        .card {
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            transition: transform 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .stats-card {
            height: 100%;
            border-left: 5px solid #0d6efd;
        }
        .progress {
            height: 10px;
            border-radius: 5px;
        }
        .university-card {
            border-left: 5px solid #20c997;
        }
        .university-card h5 {
            color: #0d6efd;
            font-weight: 600;
        }
        .issue-badge {
            font-size: 0.7rem;
            padding: 0.25rem 0.5rem;
            margin-right: 5px;
            margin-bottom: 5px;
        }
        .heading-with-line {
            display: flex;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        .heading-with-line h2 {
            margin-right: 1rem;
            white-space: nowrap;
            font-weight: 700;
            color: #212529;
        }
        .heading-line {
            flex-grow: 1;
            height: 1px;
            background-color: #dee2e6;
        }
        #last-update {
            font-style: italic;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <!-- Dashboard content will be added by the setup script -->
</body>
</html>
EOF
    echo -e "${GREEN}✓ Dashboard template created${RESET}"
else
    echo -e "${YELLOW}⚠ Dashboard file already exists, skipping creation${RESET}"
fi

# Copy the report generator script if provided
if [ ! -f "report_generator.py" ]; then
    # Create a placeholder report generator script
    cat > report_generator.py << 'EOF'
#!/usr/bin/env python
"""
Admissions Data Report Generator

This script analyzes the scraped university admissions data and generates
a comprehensive report.
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

def main():
    parser = argparse.ArgumentParser(description="Generate a report from university admissions data")
    parser.add_argument("--input", "-i", default="data/admissions_data.json", help="Path to the JSON data file")
    parser.add_argument("--output", "-o", help="Path to save the report (default: stdout)")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="Output format (text or json)")
    args = parser.parse_args()
    
    # Load the data
    data = load_data(args.input)
    
    # Generate a simple report
    report = []
    report.append("# University Admissions Scraper Report")
    report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append(f"Total Universities: {len(data)}")
    
    # Output the report
    report_text = "\n".join(report)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"Report saved to {args.output}")
    else:
        print(report_text)

if __name__ == "__main__":
    main()
EOF
    chmod +x report_generator.py
    echo -e "${GREEN}✓ Report generator script created${RESET}"
else
    echo -e "${YELLOW}⚠ Report generator script already exists, skipping creation${RESET}"
fi

# Create GitHub workflow directory if it doesn't exist
mkdir -p .github/workflows

# Create the GitHub workflow file
if [ ! -f ".github/workflows/scraper-workflow.yml" ]; then
    echo -e "\n${BOLD}Setting up GitHub Actions workflow...${RESET}"
    
    mkdir -p .github/workflows
    cat > .github/workflows/scraper-workflow.yml << 'EOF'
name: University Admissions Scraper

on:
  # Run on schedule (once a week on Monday at 2 AM UTC)
  schedule:
    - cron: '0 2 * * 1'
  
  # Allow manual trigger from GitHub UI
  workflow_dispatch:
    inputs:
      reason:
        description: 'Reason for running scraper'
        required: false
        default: 'Manual trigger'

jobs:
  scrape:
    name: Scrape University Admissions Pages
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          cache: 'pip'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          
      - name: Run scraper
        run: |
          python main.py
          
      - name: Check if data was collected
        id: check-data
        run: |
          if [ -f "data/admissions_data.json" ]; then
            FILESIZE=$(stat -c%s "data/admissions_data.json")
            echo "filesize=$FILESIZE" >> $GITHUB_OUTPUT
            if [ "$FILESIZE" -gt 100 ]; then
              echo "valid=true" >> $GITHUB_OUTPUT
            else
              echo "valid=false" >> $GITHUB_OUTPUT
            fi
          else
            echo "valid=false" >> $GITHUB_OUTPUT
          fi
          
      - name: List found universities
        if: steps.check-data.outputs.valid == 'true'
        run: |
          echo "Universities data successfully collected:"
          python -c "import json; data = json.load(open('data/admissions_data.json')); print('\n'.join([f\"- {uni['name']}\" for uni in data]))"
          
      - name: Commit and push if data changed
        run: |
          git config --global user.name 'GitHub Actions Bot'
          git config --global user.email 'actions@github.com'
          git add data/admissions_data.json
          git diff --quiet && git diff --staged --quiet || (git commit -m "Update admissions data [skip ci]" && git push)
          
      - name: Upload data as artifact
        uses: actions/upload-artifact@v3
        with:
          name: admissions-data
          path: data/admissions_data.json
          retention-days: 30
EOF
    echo -e "${GREEN}✓ GitHub Actions workflow created${RESET}"
else
    echo -e "${YELLOW}⚠ GitHub Actions workflow already exists, skipping creation${RESET}"
fi

# Final instructions
echo -e "\n${BOLD}${GREEN}✅ Setup completed successfully!${RESET}"
echo -e "\n${BOLD}Next steps:${RESET}"
echo -e "1. Run the scraper with: ${BOLD}python main.py${RESET}"
echo -e "2. Check the results in: ${BOLD}data/admissions_data.json${RESET}"
echo -e "3. For dashboard visualization, setup a simple HTTP server:"
echo -e "   ${BOLD}cd dashboard && python -m http.server 8080${RESET}"
echo -e "   Then visit ${BOLD}http://localhost:8080${RESET} in your browser"
echo -e "4. To push to GitHub and enable the workflow:"
echo -e "   ${BOLD}git add .${RESET}"
echo -e "   ${BOLD}git commit -m \"Initial setup\"${RESET}"
echo -e "   ${BOLD}git push${RESET}"

echo -e "\n${BOLD}${BLUE}Happy scraping!${RESET}"
echo -e "${BOLD}${BLUE}========================================${RESET}\n"