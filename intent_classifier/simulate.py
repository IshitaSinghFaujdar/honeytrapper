import pandas as pd
import random
from faker import Faker
import os
import logging
from datetime import datetime

# === Logging Setup ===
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
os.makedirs("logs/simulate", exist_ok=True)
log_file = f"logs/simulate/{timestamp}.log"

handler = logging.FileHandler(log_file)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# === Faker Setup ===
fake = Faker()

# === Intent Templates ===
INTENTS = {
    "probing": [
        ["What do you do?", "Where do you work?", "Do you have access to internal data?", "Who are your clients?", "Is your project public?"],
        ["Can I see your GitHub repo?", "Is your system hosted on AWS?", "Are you in cybersecurity?"]
    ],
    "technical": [
        ["What tools do you use for deployment?", "Can you access the production server?", "Is your team using Docker?", "What’s the admin panel like?"],
        ["Do you know how to bypass 2FA?", "Can you override system access?", "Do you use VPN or proxy?"]
    ],
    "casual": [
        ["Hey, how was your day?", "What’s your favorite movie?", "Do you play games?", "What’s your weekend plan?"],
        ["I made lasagna today!", "Just chilling at home", "Thinking of going to the beach"]
    ],
    "flirty": [
        ["Hey cutie 😘", "You look amazing today", "Wanna video call?", "Are you single?", "You’re charming 😍"],
        ["Let’s meet sometime?", "I can’t stop thinking about you", "Do you believe in love at first sight?"]
    ]
}

ANOMALOUS_INTENTS = ["probing", "technical"]

# === Message Generator ===
def generate_messages(intent, use_faker=False):
    base_msgs = random.choice(INTENTS[intent])
    random.shuffle(base_msgs)
    
    if use_faker and intent == "casual":
        base_msgs += [fake.sentence() for _ in range(1)]  # Add 1 casual random message
    if use_faker and intent == "flirty":
        pickup_lines = [
            "Are you a magician? Because whenever I look at you, everyone else disappears.",
            "Do you have a map? I just got lost in your eyes.",
            "If you were a vegetable, you’d be a cute-cumber.",
            "Do you believe in love at first sight—or should I walk by again?",
            "Are you French? Because Eiffel for you.",
            "Is your name Google? Because you’ve got everything I’m searching for.",
        ]
        base_msgs += [random.choice(pickup_lines)]


    return base_msgs[:5]

# === Simulation Function ===
def simulate_dataset(n=1000, save_path="classification_sample_dataset.csv", use_faker=True):
    logger.info(f"Generating {n} samples into {save_path}")
    data = []

    for i in range(n):
        intent = random.choice(list(INTENTS.keys()))
        anomaly = intent in ANOMALOUS_INTENTS

        messages = generate_messages(intent, use_faker=use_faker)
        record = {
            "messages": "|".join(messages),
            "intent": intent,
            "anomaly": anomaly
        }
        logger.debug(f"Sample {i+1}: {record}")
        data.append(record)

    df = pd.DataFrame(data)
    df.to_csv(save_path, index=False)
    logger.info(f"✅ Dataset saved to {save_path}")

# === Main ===
if __name__ == "__main__":
    try:
        simulate_dataset(n=1000, save_path="classification_sample_dataset.csv", use_faker=True)
    except Exception as e:
        logger.error(f"Dataset simulation failed: {e}")
