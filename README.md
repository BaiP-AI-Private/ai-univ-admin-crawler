# University Admissions Crawler with Crawl4AI

This project is an advanced web crawler built with Python that scrapes university admissions websites using Crawl4AI. The scraper extracts key information—including the courses offered, admissions requirements, and the application deadline—which will be used in an AI-assisted webapp to match students' academic results and achievements.

## 🚀 Features

- **AI-powered Web Crawling:** Uses Crawl4AI with Playwright for intelligent web crawling and extraction
- **LLM-based Extraction:** Automatically parses and extracts structured data from complex university websites
- **AI Enrichment:** Uses Claude or GROQ AI to enhance and structure the extracted data
- **Human-Readable Reports:** Generates Markdown reports from the enriched data
- **Browser Automation:** Handles JavaScript-rendered content (unlike traditional scrapers)
- **Asynchronous Processing:** Concurrent processing with smart rate limiting
- **CI/CD Integration:** GitHub Actions workflow for automated scraping and reporting
- **RESTful API:** FastAPI-based API for triggering and monitoring crawl jobs
- **Caching Support:** Efficient request management with caching to reduce server load
- **Docker Support:** Run the entire system in containers for easy deployment

## 📋 Project Structure

```
.
├── main.py                   # Primary crawler logic using Crawl4AI
├── main_ci.py                # CI-friendly version of the crawler
├── api.py                    # FastAPI-based API for crawler management
├── enrich_with_ai.py         # Script to enhance data with Claude or GROQ AI
├── claude_api.py             # Client for Claude AI API interaction
├── groq_api.py               # Client for GROQ AI API interaction
├── generate_reports.py       # Script to generate human-readable reports
├── config.py                 # Global settings (timeouts, headers, data paths)
├── Dockerfile                # Container definition with Crawl4AI and browser dependencies
├── docker-compose.yml        # Docker setup for crawler and API services
├── data/
│   ├── universities.json     # Source list of universities to scrape
│   ├── admissions_data.json  # Output file with structured admissions data
│   └── enriched_data.json    # AI-enhanced admissions data
├── reports/                  # Directory for generated Markdown reports
│   ├── index.md              # Index of all university reports
│   └── university_name_report.md  # Individual university reports
├── .github/workflows/        # GitHub Actions workflow definitions
├── requirements.txt          # Python dependencies with Crawl4AI
└── README.md                 # Project documentation
```

## 🔍 Data Pipeline

This project follows a multi-stage data pipeline:

1. **Web Scraping:** Extract raw data from university websites using Crawl4AI
2. **Data Structuring:** Organize the raw data into consistent JSON format
3. **AI Enrichment:** Use Claude or GROQ to enhance and clean the structured data
4. **Report Generation:** Create human-readable Markdown reports from the enriched data

## 🔧 Installation (Local Development)

### Prerequisites

- Python 3.10 or higher
- Git
- Docker and Docker Compose (optional, for containerized deployment)

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd ai-univ-admin-crawler
```

### Step 2: Create and Activate a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the Crawl4AI post-installation setup to install browser binaries
python -m playwright install chromium
```

## 🏃‍♀️ Usage

### Option 1: Running the Complete Pipeline Locally

```bash
# Step 1: Run the crawler to extract data
python main.py

# Step 2: Enrich the data with AI (using Claude or GROQ)
# With Claude API
export CLAUDE_API_KEY="your-claude-api-key"
python enrich_with_ai.py --provider claude

# Or with GROQ API
export GROQ_API_KEY="your-groq-api-key"
python enrich_with_ai.py --provider groq

# Or in simulation mode (no API key needed)
python enrich_with_ai.py --provider auto

# Step 3: Generate human-readable reports
python generate_reports.py
```

### Option 2: Running with GitHub Actions

The project includes a GitHub Actions workflow that runs the entire pipeline automatically:

1. Configure the following secrets in your GitHub repository:
   - `CLAUDE_API_KEY` (optional): Your Claude API key for AI enrichment
   - `GROQ_API_KEY` (optional): Your GROQ API key for AI enrichment

2. The workflow can be triggered:
   - Automatically on a weekly schedule (Wednesday at 2 AM UTC)
   - Manually from the Actions tab in GitHub

3. After the workflow runs, reports are available as artifacts in the GitHub Actions interface.

### Option 3: Running with Docker (Recommended for API)

Using Docker Compose is the easiest way to run the crawler and API:

```bash
# Build and start the services
docker-compose up --build

# Or run in detached mode
docker-compose up -d

# To stop the services
docker-compose down
```

## 🌐 API Endpoints

The crawler exposes the following API endpoints:

- `GET /` - Basic API information
- `POST /crawl` - Start a new crawling job
- `GET /crawl/{job_id}` - Get the status of a crawling job
- `GET /crawl/{job_id}/results` - Get the results of a completed crawling job

### Example API Usage

```bash
# Start a new crawl job
curl -X POST http://localhost:8000/crawl

# Check job status (replace JOB_ID with the actual job ID)
curl http://localhost:8000/crawl/JOB_ID

# Get job results when complete
curl http://localhost:8000/crawl/JOB_ID/results
```

## 📊 Data Input/Output Format

### Input: Universities List

Create a file at `data/universities.json` with the following structure:

```json
[
  {
    "name": "University of Example",
    "url": "https://example.edu/admissions"
  },
  {
    "name": "Another University",
    "url": "https://another-university.edu/apply"
  }
]
```

### Output: Scraped Admissions Data

The crawler generates structured data in the following format:

```json
[
  {
    "name": "University of Example",
    "url": "https://example.edu/admissions",
    "courses": ["Bachelor of Science in Computer Science", "Master of Business Administration"],
    "admissions_requirements": ["High school diploma or equivalent", "Minimum GPA of 3.0"],
    "application_deadlines": ["Fall Semester: January 15", "Spring Semester: October 1"],
    "early_admission": ["Early Action Deadline: November 1", "Notification: December 15"],
    "regular_admission": ["Regular Decision Deadline: January 5", "Notification: April 1"],
    "scraped_at": "2025-05-13 15:30:45"
  },
  ...
]
```

### Output: AI-Enriched Data

The AI enrichment process produces a more structured and detailed format:

```json
[
  {
    "name": "University of Example",
    "url": "https://example.edu/admissions",
    "programs": [
      {
        "name": "Computer Science",
        "description": "A comprehensive program covering algorithms, programming languages, and software development.",
        "degree_type": "Bachelor's",
        "department": "School of Engineering"
      }
    ],
    "application_process": {
      "early_admission": {
        "deadline": "November 1",
        "notification_date": "December 15",
        "restrictions": "Restrictive Early Action"
      },
      "regular_admission": {
        "deadline": "January 5",
        "notification_date": "April 1"
      },
      "general_requirements": [
        "High school diploma or equivalent",
        "Minimum GPA of 3.0"
      ]
    },
    "enriched_at": "2025-05-13 16:45:23",
    "enriched_by": "Claude AI"
  },
  ...
]
```

## 🤖 AI Integration

This project supports two AI providers for data enrichment:

### Claude AI

[Claude](https://www.anthropic.com/claude) is an AI assistant by Anthropic that can enhance the scraped data.

To use Claude:
```bash
export CLAUDE_API_KEY="your-claude-api-key"
python enrich_with_ai.py --provider claude
```

### GROQ AI

[GROQ](https://groq.com/) is a fast inference API for LLM models that can be used as an alternative to Claude.

To use GROQ:
```bash
export GROQ_API_KEY="your-groq-api-key"
python enrich_with_ai.py --provider groq
```

### Auto-Selection Mode

If you have multiple API keys set up, the script can automatically choose the best available:

```bash
python enrich_with_ai.py --provider auto
```

Priority order:
1. GROQ API (if GROQ_API_KEY is available)
2. Claude API (if CLAUDE_API_KEY is available)
3. Simulation mode (if no API keys are available)

## ⚙️ Configuration

The crawler behavior can be customized through the `config.py` file:

- `DEFAULT_TIMEOUT`: HTTP request timeout in seconds
- `RATE_LIMIT`: Delay between requests to avoid overloading servers
- `INPUT_FILE`: Path to the input universities JSON file
- `OUTPUT_FILE`: Path to save the extracted data

## 🔄 Switching Between Extraction Strategies

Crawl4AI supports multiple extraction strategies:

1. **CSS-based Extraction (Default in CI)**: Uses CSS selectors for reliable extraction
   - The CSS selectors are defined in `main_ci.py`
   - Custom selectors can be added for specific universities

2. **LLM-based Extraction**: Uses language models to extract data intelligently
   - Edit `main.py` to change the provider (e.g., from "ollama/llama3" to "openai/gpt-4")
   - For OpenAI, add your API key: `provider="openai/gpt-4", api_token="your_token"`

## 📄 Report Generation

The project includes a report generation module that creates human-readable Markdown documents from the enriched data.

To generate reports:
```bash
python generate_reports.py --input data/enriched_data.json --output-dir reports
```

Reports include:
- University overview
- Program/major details
- Application processes and deadlines
- Admission requirements

## 🐛 Troubleshooting

### Common Issues:

1. **Browser Initialization Fails**:
   - Ensure you ran `python -m playwright install chromium` after installing dependencies
   - Check browser dependencies in the Dockerfile are correctly installed

2. **Rate Limiting or Blocking**:
   - Adjust `RATE_LIMIT` in `config.py` to a higher value
   - Consider implementing proxy rotation

3. **AI API Issues**:
   - Check API key validity
   - Try using the simulation mode with `--provider auto` flag
   - Check for rate limiting on the AI provider's side

4. **CI Environment Issues**:
   - Look for environment variable inconsistencies
   - Check GitHub Actions logs for detailed error messages

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License

---

## 🔮 Future Improvements

Some potential future enhancements:

- Web dashboard for visualizing the enriched data
- Integration with more AI models for specialized tasks
- Multi-language support for international universities
- PDF document parsing for admission guidebooks
- Interactive question-answering about university data
- Comparative analysis between universities
- Support for graduate program specific information

## 📞 Support

If you encounter any issues or have questions, please file an issue on GitHub or contact the maintainers.

---

Happy university crawling! 🎓
