# **Deep Seek Crawler - Kubernetes Deployment Guide** 🚀

This project is a scalable web crawler built with Python that extracts **university admission and course data** asynchronously using Crawl4AI. It utilizes a **BERT-powered AI model** for CSS selector detection and Reinforcement Learning to refine predictions dynamically.

## **Features**
✅ Asynchronous web crawling with [Crawl4AI](https://pypi.org/project/Crawl4AI/)  
✅ AI-powered CSS selector detection using BERT  
✅ Reinforcement Learning for improving accuracy over time  
✅ JSON-based university configuration for easy updates  
✅ Kubernetes deployment for **scalability**

---

## **Project Structure**
```
.
├── main.py                 # Web scraper using AI-powered CSS selector detection
├── api.py                  # FastAPI-based API for real-time predictions
├── config.py               # Global settings (timeouts, selectors, reward values)
├── models
│   ├── selector_agent.py   # AI model for CSS selector detection using Reinforcement Learning
│   ├── rewards.py          # Defines reward system for AI model training
├── utils
│   ├── data_utils.py       # Utility functions for saving extracted data
│   ├── scraper_utils.py    # Web scraping utility functions
├── data
│   ├── universities.json   # List of university URLs for the scraper
├── k8s/
│   ├── deployment.yaml     # Kubernetes deployment file
│   ├── service.yaml        # Kubernetes service file
│   ├── helm-chart/         # Helm chart for easier deployment
├── Dockerfile              # Containerization setup
├── requirements.txt        # Python dependencies (Also at root)
├── .env                    # Environment variables (API keys)
├── .gitignore              # Ignores env & compiled files
└── README.md               # Deployment instructions

```

## **Installation Steps**
### **1️⃣ Create & Activate a Conda Environment**
```bash
conda create -n deep-seek-crawler python=3.12 -y
conda activate deep-seek-crawler
```

### **2️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3️⃣ Set Up Environment Variables**
Create a `.env` file in the root directory:
```
GROQ_API_KEY=your_groq_api_key_here
```
*(Note: The `.env` file is included in `.gitignore`, so it won’t be pushed to version control.)*

---

## **🚀 Running the Web Scraper**
```bash
python main.py
```
This script extracts **course listings and admissions information** from university websites dynamically.

---

## **🚀 Running the AI-Powered Prediction API**
Start the FastAPI API that predicts CSS selectors dynamically:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

### **Example API Request**
```python
import requests

html_data = "<html><body><div class='course-list'>Machine Learning</div></body></html>"
response = requests.post("http://127.0.0.1:8000/predict", json={"html": html_data})
print(response.json())  # Returns predicted CSS selector
```

---

## **🚀 Deployment with Kubernetes**
### **1️⃣ Build the Docker Image**
```bash
docker build -t deepseek-crawler .
```

### **2️⃣ Push to Docker Hub**
Replace `your-docker-username` with your Docker Hub username:
```bash
docker tag deepseek-crawler your-docker-username/deepseek-crawler:v1
docker push your-docker-username/deepseek-crawler:v1
```

### **3️⃣ Apply Kubernetes Deployment**
Ensure your Kubernetes cluster is running (`kubectl get nodes`):
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### **4️⃣ Verify Deployment**
```bash
kubectl get pods
kubectl get services
```

---

## **🚀 Scaling with Helm**
For easier deployments, use **Helm charts**:

### **1️⃣ Install Helm**
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### **2️⃣ Deploy using Helm**
```bash
helm install deepseek-crawler ./k8s/helm-chart/
```

### **3️⃣ Verify Pods**
```bash
kubectl get pods
```

---

## **License**
MIT License (or update with the appropriate license)
