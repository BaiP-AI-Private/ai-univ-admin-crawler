# Define rewards for reinforcement learning selector agent
REWARDS = {
    "correct": 1,  # Correct selector choice → Positive reward
    "incorrect": -1,  # Incorrect selector choice → Negative reward
    "uncertain": -0.5  # Uncertain selector choice → Small penalty
}

def get_reward(predicted_selector, true_selector):
    """Returns a reward value based on accuracy of predicted selector."""
    if predicted_selector == true_selector:
        return REWARDS["correct"]
    elif predicted_selector is None:
        return REWARDS["uncertain"]
    else:
        return REWARDS["incorrect"]
