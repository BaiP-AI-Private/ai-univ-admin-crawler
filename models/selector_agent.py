import torch
import torch.nn as nn
import torch.optim as optim
import config  # Import global reward values
from transformers import BertModel, BertTokenizer

# Load pre-trained BERT model
bert_model = BertModel.from_pretrained("bert-base-uncased")
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# Define Reinforcement Learning Selector Model
class SelectorAgent(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(768, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, 2)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

agent = SelectorAgent()
optimizer = optim.Adam(agent.parameters(), lr=1e-4)
loss_fn = nn.CrossEntropyLoss()

def train_agent(training_data):
    """Train RL agent using rewards from `config.py`."""
    for epoch in range(5):
        for entry in training_data:
            text = entry["html"]
            tokens = tokenizer(text, return_tensors="pt")
            embedding = bert_model(**tokens)["last_hidden_state"][:, 0, :]
            prediction = agent(embedding)

            # Simulated feedback
            true_selector = "courses" if "course" in text.lower() else "admissions"
            target = torch.tensor([0] if true_selector == "courses" else [1])

            # Reward Calculation
            reward = config.REWARD_VALUES["correct"] if prediction.argmax().item() == target.item() else config.REWARD_VALUES["incorrect"]
            loss = loss_fn(prediction, target) * reward

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        print(f"Epoch {epoch+1}, Loss: {loss.item()}")

print("Selector Agent trained successfully!")
torch.save(agent.state_dict(), "selector_model.pth")
