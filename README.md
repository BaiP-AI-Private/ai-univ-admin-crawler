# University Admissions Crawler

This project is a web crawler built with Python that scrapes university admissions websites. The scraper extracts key information—including the courses offered, admissions requirements, and the application deadline—which will be used in AI-assisted webapp to match students' academic results and achievements.

## 🚀 Features

- **Asynchronous Web Crawling:** Uses `aiohttp` for non-blocking HTTP requests with built-in rate limiting
- **Structured Data Extraction:** Uses multiple strategies to extract relevant information, even from varied university websites
- **GitHub Actions Integration:** Automatically runs the scraper on a schedule or on-demand
- **Dashboard Visualization:** View and analyze the scraped data through an interactive web dashboard
- **Detailed Reporting:** Generate comprehensive reports on the data collection process
- **Robust Error Handling:** Handles network issues, rate limiting, and varied website structures
- **Docker Support:** Run the entire system in containers for easy deployment

## 📋 Project Structure

```
.
├── main.py                   # Web scraper with structured extraction and logging
├── config.py                 # Global settings (timeouts, headers, CSS selectors, data paths)
├── report_generator.py       # Generates detailed reports from scraped data
├── api.py                    # FastAPI-based API for real-time predictions (if applicable)
├── data/
│   ├── universities.json     # Source list of universities to scrape
│   └── admissions_data.json  # Output file with structured admissions data
├── dashboard/
│   └── dashboard.html        # Web dashboard for data visualization
├── .github/
│   └── workflows/
│       ├── ci_cd.yml             # CI/CD pipeline configuration
│       ├── docker-build-push.yml # Docker image build and push workflow
│       └── scraper-workflow.yml  # University scraper scheduled workflow
├── models/                   # AI models for data extraction and analysis
├── utils/                    # Utility functions for the scraper
├── tests/                    # Test suite for the scraper
├── k8s/                      # Kubernetes deployment configurations
├── scripts/                  # Helper scripts for setup and maintenance
├── docker-compose.yml        # Docker setup for running the scraper and dashboard
├── Dockerfile                # Container definition for the scraper
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment variables
├── LICENSE                   # MIT License file
└── README.md                 # Project documentation
```

## 🔧 Installation

### Option 1: Using the Setup Script (Recommended)

The easiest way to get started is using the provided setup script, which will create a virtual environment, install dependencies, and set up the necessary files:

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

### Option 2: Manual Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/YourUsername/ai-univ-admin-crawler.git
   cd ai-univ-admin-crawler
   ```

2. **Create and Activate a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🏃‍♀️ Usage

### Running the Scraper Locally

To run the scraper on your local machine:

```bash
python main.py
```

The structured data will be saved to `data/admissions_data.json`.

### Generating Reports

After running the scraper, you can generate a detailed report:

```bash
python report_generator.py --output data/report.md
```

### Viewing the Dashboard

The dashboard provides visualizations of the scraped data:

```bash
# Start a simple HTTP server
cd dashboard
python -m http.server 8080
```

Then visit http://localhost:8080 in your browser.

## 🤖 GitHub Actions Workflow

This project includes a GitHub Actions workflow that automates the scraping process. The workflow:

1. **Runs on a schedule** (Monday at 2 AM UTC) or can be triggered manually
2. **Executes the scraper** to collect admissions data
3. **Commits any changes** to the repository
4. **Uploads the results** as a workflow artifact

### Configuring the Workflow

The workflow is defined in `.github/workflows/scraper-workflow.yml`. You may want to customize:

- **Schedule:** Update the `cron` expression to run at different times
- **Notifications:** Uncomment the email or Slack notification steps and configure them
- **Additional Steps:** Add more steps for data processing or reporting

### Running the Workflow Manually

You can trigger the workflow manually from the GitHub interface:

1. Go to your repository on GitHub
2. Click on the "Actions" tab
3. Select "University Admissions Scraper" from the list of workflows
4. Click "Run workflow" button
5. Optionally, provide a reason for running the workflow
6. Click "Run workflow" to start the process

### Monitoring Workflow Runs

After a workflow runs, you can:

1. See the execution log in the "Actions" tab
2. Download the scraped data from the artifacts section
3. View the updated `data/admissions_data.json` file in your repository

## 🐳 Docker Support

To run the scraper and dashboard using Docker:

```bash
# Build and start the services
docker-compose up -d

# View the dashboard
# Open http://localhost:8080 in your browser

# Stop the services
docker-compose down
```

## 📊 Data Structure

The scraped data is stored in JSON format with the following structure:

```json
[
  {
    "name": "University Name",
    "url": "https://university-website.edu/admissions",
    "courses": ["Course 1 description", "Course 2 description"],
    "admissions_requirements": ["Requirement 1", "Requirement 2"],
    "application_deadlines": ["Deadline 1", "Deadline 2"],
    "scraped_at": "2025-05-11 12:34:56"
  },
  ...
]
```

## 🔍 Customizing the Scraper

### Adding More Universities

To add more universities to scrape, edit the `data/universities.json` file:

```json
[
  {
    "name": "New University",
    "url": "https://new-university.edu/admissions"
  },
  ...
]
```

### Adjusting Scraping Parameters

Edit `config.py` to customize:

- `DEFAULT_TIMEOUT`: HTTP request timeout in seconds
- `RATE_LIMIT`: Delay between requests to avoid overloading servers
- `DEFAULT_HEADERS`: HTTP headers to use for requests

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

- Adding AI-assisted data extraction for more complex web structures
- Implementing a database for historical data tracking
- Creating an admin panel for manual validation of scraped data
- Adding support for internationalization and multiple languages
- Implementing proxy rotation for handling IP blocking

## 📞 Support

If you encounter any issues or have questions, please file an issue on GitHub or contact the maintainers.

---

Happy scraping! 🎓
