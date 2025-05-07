# DeepSeek University Admissions Crawler

This project is a web crawler built with Python that scrapes university admissions websites. The scraper extracts key information—including the courses offered, admissions requirements, and the application deadline—which will be used in our AI-assisted webapp to match students’ academic results and achievements during high school.

## Features
- **Asynchronous Web Crawling:** Uses `aiohttp` for non-blocking HTTP requests.
- **Structured Data Extraction:** Leverages `BeautifulSoup` to extract courses, admissions requirements, and deadlines.
- **Logging:** Detailed logs (using Python's logging module) help track errors and allow further AI-assisted review.
- **Configurable Global Parameters:** Manage settings like timeouts, HTTP headers, and file paths via `config.py`.
- **Containerization & Deployment:** Build Docker images and deploy via Kubernetes.

---

## Project Structure
```
.
├── main.py                 # Web scraper with structured extraction and logging
├── api.py                  # FastAPI-based API for real-time predictions (if applicable)
├── config.py               # Global settings (timeouts, headers, CSS selectors, data paths)
├── models
│   ├── selector_agent.py   # AI model for CSS selector detection using Reinforcement Learning
│   └── rewards.py          # Defines reward system for AI model training
├── utils
│   ├── data_utils.py       # Utility functions for processing and saving data
│   └── scraper_utils.py    # Web scraping utility functions
├── data
│   └── universities.json   # University-specific data (names & admissions URLs)
├── k8s/
│   ├── deployment.yaml     # Kubernetes deployment file
│   ├── service.yaml        # Kubernetes service file
│   └── helm-chart/         # Helm chart for easier deployment
├── Dockerfile              # Containerization setup for the API/web scraper
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (API keys)
├── .gitignore              # Ignores env & compiled files
└── README.md               # This file (Deployment instructions)
```

---

## Installation
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/BaiP-ai/ai-univ-admin-crawler.git
   cd ai-univ-admin-crawler
   ```

2. **Ensure Python 3.12 is Installed**
   Before proceeding, verify your Python version:
   ```bash
   python --version
   ```
   If it's not Python 3.12, install it from [python.org](https://www.python.org/downloads/).

3. **Create and Activate a Virtual Environment:**

   You can use either **Conda** or **venv** to set up the environment.

   _Option 1: Using Conda_
   ```bash
   conda create -n deep-seek-crawler python=3.12 -y
   conda activate deep-seek-crawler  # On Windows: activate deep-seek-crawler
   ```

   _Option 2: Using Virtualenv (venv)_
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Upgrade Pip and Install Dependencies:**
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Set Up Environment Variables:**
   Create a `.env` file in the root directory with your API keys as needed.
   ```bash
   GROQ_API_KEY=your_groq_api_key_here
   ```

---

## Usage
### Running the Web Scraper
Execute the scraper to extract courses, admissions requirements, and application deadlines:
```bash
python main.py
```
The structured data will be saved to the file defined in `config.OUTPUT_FILE`.

### Running the AI-Powered Prediction API
If you want to serve scraped data or run real-time predictions, start the FastAPI API:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```
This starts the API server with endpoints available for data retrieval.

---

## Hosting the Web Application
### GitHub Pages
GitHub Pages is ideal for static front-end hosting:
1. Build your front-end (e.g., using React, Vue, or plain HTML/CSS/JS).
2. Place the static files in a `docs` (or `build`) folder.
3. Push to your main branch and enable GitHub Pages under the repository settings (choose the `docs` folder as source).

### Vercel
For dynamic front-ends or if you require serverless functions:
1. Connect your repository to [Vercel](https://vercel.com/).
2. Configure the project (set the appropriate build command and output directory).
3. Deploy your project on Vercel, which also supports API routes if needed.

---

## Logging and Troubleshooting
The application uses Python’s logging module. Check the console or log files for:
- Successful HTTP requests and data extraction
- Error messages from failed requests or file operations
- Debug information to assist any AI agent reviewing the logs

---

## Deployment with Kubernetes
For containerized deployments:
1. **Build the Docker image:**
   ```bash
   docker build -t ai-univ-admin-crawler .
   ```
2. **Push the image to Docker Hub:**
   ```bash
   docker tag ai-univ-admin-crawler baipai/ai-univ-admin-crawler:latest
   docker push baipai/ai-univ-admin-crawler:latest
   ```
3. **Deploy to Kubernetes:**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```

---

## Scaling with Helm
For easier deployments, use **Helm charts**:

### Install Helm
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Deploy using Helm
```bash
helm install deepseek-crawler ./k8s/helm-chart/
```

### Verify Pods
```bash
kubectl get pods
```

---

## Continuous Integration / Deployment
Set up GitHub Actions (see `.github/workflows/ci_cd.yml`) for running tests, building Docker images, and deploying to Kubernetes.

---

## License
MIT License
