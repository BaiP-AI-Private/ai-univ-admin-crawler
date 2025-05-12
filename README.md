# University Admissions Crawler with Crawl4AI

This project is an advanced web crawler built with Python that scrapes university admissions websites using Crawl4AI. The scraper extracts key information—including the courses offered, admissions requirements, and the application deadline—which will be used in an AI-assisted webapp to match students' academic results and achievements.

## 🚀 Features

- **AI-powered Web Crawling:** Uses Crawl4AI with Playwright for intelligent web crawling and extraction
- **LLM-based Extraction:** Automatically parses and extracts structured data from complex university websites
- **Browser Automation:** Handles JavaScript-rendered content (unlike traditional scrapers)
- **Asynchronous Processing:** Concurrent processing with smart rate limiting
- **RESTful API:** FastAPI-based API for triggering and monitoring crawl jobs
- **Caching Support:** Efficient request management with caching to reduce server load
- **Docker Support:** Run the entire system in containers for easy deployment

## 📋 Project Structure

```
.
├── main.py                   # Primary crawler logic using Crawl4AI
├── api.py                    # FastAPI-based API for crawler management
├── config.py                 # Global settings (timeouts, headers, data paths)
├── Dockerfile                # Container definition with Crawl4AI and browser dependencies
├── docker-compose.yml        # Docker setup for crawler and API services
├── data/
│   ├── universities.json     # Source list of universities to scrape
│   └── admissions_data.json  # Output file with structured admissions data
├── requirements.txt          # Python dependencies with Crawl4AI
└── README.md                 # Project documentation
```

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

# Check out the Crawl4AI implementation branch
git checkout crawl4ai-implementation
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
crawl4ai-setup
```

## 🏃‍♀️ Usage

### Option 1: Running Locally without Docker

#### Running the Crawler Directly

To run the crawler on your local machine:

```bash
# Make sure you have sample data in data/universities.json
python main.py
```

The structured data will be saved to `data/admissions_data.json`.

#### Running the API

To start the API server:

```bash
# Start the FastAPI server
python api.py
```

The API will be available at http://localhost:8000

You can access the interactive API documentation at http://localhost:8000/docs

### Option 2: Running with Docker (Recommended)

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

### Output: Admissions Data

The crawler generates structured data in the following format:

```json
[
  {
    "name": "University of Example",
    "url": "https://example.edu/admissions",
    "courses": ["Bachelor of Science in Computer Science", "Master of Business Administration"],
    "admissions_requirements": ["High school diploma or equivalent", "Minimum GPA of 3.0"],
    "application_deadlines": ["Fall Semester: January 15", "Spring Semester: October 1"],
    "scraped_at": "2025-05-12 15:30:45"
  },
  ...
]
```

## ⚙️ Configuration

The crawler behavior can be customized through the `config.py` file:

- `DEFAULT_TIMEOUT`: HTTP request timeout in seconds
- `RATE_LIMIT`: Delay between requests to avoid overloading servers
- `INPUT_FILE`: Path to the input universities JSON file
- `OUTPUT_FILE`: Path to save the extracted data

## 🔄 Switching Between Extraction Strategies

Crawl4AI supports multiple extraction strategies:

1. **LLM-based Extraction (Default)**: Uses language models to extract data intelligently
   - Edit `main.py` to change the provider (e.g., from "ollama/llama3" to "openai/gpt-4")
   - For OpenAI, add your API key: `provider="openai/gpt-4", api_token="your_token"`

2. **CSS-based Extraction**: For more traditional, rule-based extraction
   - Implement a `JsonCssExtractionStrategy` in `main.py` if preferred

## 🐛 Troubleshooting

### Common Issues:

1. **Browser Initialization Fails**:
   - Ensure you ran `crawl4ai-setup` after installing dependencies
   - Check browser dependencies in the Dockerfile are correctly installed

2. **Rate Limiting or Blocking**:
   - Adjust `RATE_LIMIT` in `config.py` to a higher value
   - Consider implementing proxy rotation

3. **Memory Issues**:
   - Reduce `max_tasks` in `process_universities()` in `main.py`
   - Increase container memory limits if using Docker

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

- Link following for deeper crawling of university websites
- Implementing database storage instead of JSON files
- Adding authentication to the API
- Creating a web dashboard for visualizing the data
- Adding support for multi-language university websites
- Implementing distributed crawling for massive scale

## 📞 Support

If you encounter any issues or have questions, please file an issue on GitHub or contact the maintainers.

---

Happy crawling! 🎓
