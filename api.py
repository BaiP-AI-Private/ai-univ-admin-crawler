from fastapi import FastAPI, Request
import torch
from transformers import BertTokenizer, BertModel
from bs4 import BeautifulSoup
from models.selector_agent import SelectorAgent  # Import RL model

# Initialize FastAPI
app = FastAPI()

# Load models
bert_model = BertModel.from_pretrained("bert-base-uncased")
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
agent = SelectorAgent()
agent.load_state_dict(torch.load("selector_model.pth"))
agent.eval()

@app.post("/predict")
async def predict_selector(request: Request):
    """API endpoint to predict CSS selectors for university websites."""
    data = await request.json()
    raw_html = data["html"]

    soup = BeautifulSoup(raw_html, "html.parser")
    elements = [tag.get_text() for tag in soup.find_all(True)]
    best_selector = max(elements, key=len)  # Basic ranking for selector candidates

    return {"predicted_selector": best_selector}

# Run API server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
