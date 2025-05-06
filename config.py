# Global Configuration File

# Web Scraper Settings
DEFAULT_TIMEOUT = 10  # Timeout for HTTP requests
DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0"}
RATE_LIMIT = 2  # Delay in seconds between requests to avoid overloading servers

# Default CSS Selectors (Used if AI model isn't available)
DEFAULT_CSS_SELECTORS = {
    "courses": "div.course-listing",
    "admissions": "div.admission-details"
}

# Paths for Data Storage
DATA_DIR = "data"
OUTPUT_FILE = f"{DATA_DIR}/universities.json"

# Reinforcement Learning Settings
REWARD_VALUES = {
    "correct": 1,   # Positive reward for correct selector
    "incorrect": -1, # Negative reward for incorrect choice
    "uncertain": -0.5 # Small penalty for low-confidence predictions
}
