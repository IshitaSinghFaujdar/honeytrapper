import random
import pandas as pd
from faker import Faker
import os
from datetime import datetime
import logging

# ------------------- Logging Setup -------------------
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
os.makedirs("logs/data_sim", exist_ok=True)
log_file = f"logs/data_sim/{timestamp}.log"

handler = logging.FileHandler(log_file)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# ------------------- Faker Init -------------------
fake = Faker()
logger.info("Faker initialized")

# ------------------- Helper Functions -------------------

def generate_username(label):
    logger.debug(f"Generating username for: {label}")
    if label == "high_risk":
        return random.choice(["_cutie_", "priya_babe", "hot_model_", "dm_4_fun"]) + str(random.randint(1, 99))
    elif label == "suspicious":
        return random.choice(["tech_daily_", "botuser_", "free_follow_"]) + str(random.randint(100, 999))
    else:
        return fake.user_name()

def generate_bio(label):
    try:
        if label == "high_risk":
            return random.choice([
                "DM me if you wanna talk", "Model | 22 | Love to chat", "Follow for pics", "Army boys hit me up"])
        elif label == "suspicious":
            return random.choice([
                "Get 1k followers now", "Tech influencer | free tools", "Follow for updates"])
        else:
            return fake.sentence(nb_words=6)
    except Exception as e:
        logger.error(f"Bio generation failed: {e}")
        return ""

def determine_photo_source(label):
    return {
        "high_risk": "stock",
        "suspicious": "ai",
        "genuine": "user_selfie"
    }.get(label, "user_selfie")

def generate_profile(label):
    try:
        username = generate_username(label)
        bio = generate_bio(label)
        photo_source = determine_photo_source(label)

        # --- Simulated metadata ---
        if label == "high_risk":
            followers = random.randint(10, 200)
            following = random.randint(800, 2000)
            account_age = random.randint(3, 30)
            is_private = False
        elif label == "suspicious":
            followers = random.randint(3000, 6000)
            following = random.randint(2500, 7000)
            account_age = random.randint(30, 300)
            is_private = random.choice([True, False])
        else:  # genuine
            followers = random.randint(500, 5000)
            following = random.randint(300, 1000)
            account_age = random.randint(180, 1800)
            is_private = True

        profile = {
            "username": username,
            "bio": bio,
            "photo_source": photo_source,
            "followers": followers,
            "following": following,
            "account_age_days": account_age,
            "is_private": is_private,
            "is_verified": False,
            "risk_label": label
        }

        logger.debug(f"Generated profile: {profile}")
        return profile

    except Exception as e:
        logger.error(f"Profile generation error: {e}")
        return {}

# ------------------- Dataset Generation -------------------

try:
    logger.info("Starting dataset simulation")
    dataset = []

    label_distribution = ["genuine"] * 250 + ["suspicious"] * 125 + ["high_risk"] * 125
    random.shuffle(label_distribution)

    for label in label_distribution:
        profile = generate_profile(label)
        if profile:
            dataset.append(profile)

    df = pd.DataFrame(dataset)
    df.to_csv("simulated_instagram_profiles.csv", index=False)
    logger.info("Dataset saved: simulated_instagram_profiles.csv")

except Exception as e:
    logger.error(f"Simulation failed: {e}")
