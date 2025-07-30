# --- main_sentinel_app.py ---
# Project Sentinel: Main Application (File-based Input Version)

from profile_analyzer import get_profile_data_from_user, calculate_profile_risk
from chat_analyzer import analyze_chat_history
from verdict_engine import calculate_final_verdict
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def read_chat_from_file(file_path: str):
    """
    Reads a chat log from a .txt file.
    Assumes each message is on a new line.
    
    Args:
        file_path: The full path to the .txt file.
        
    Returns:
        A list of strings, where each string is a message.
        Returns None if the file is not found.
    """
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read all lines, and strip any leading/trailing whitespace (like newlines)
            messages = [line.strip() for line in f.readlines() if line.strip()]
        return messages
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None

def run_sentinel():
    """The main orchestrator for the Sentinel application."""
    clear_screen()
    
    # --- STAGE 1: PROFILE ANALYSIS ---
    profile_data = get_profile_data_from_user()
    profile_risk_score, profile_reasons = calculate_profile_risk(profile_data)
    
    clear_screen()
    print("--- Profile Analysis Complete ---")
    print(f"Profile Risk Score: {profile_risk_score} / 10")
    for reason in profile_reasons:
        print(f"  - {reason}")
    print("-" * 30)

    # --- STAGE 2: GET AND READ CHAT FILE ---
    all_messages = None
    while all_messages is None:
        file_path = input("\nEnter the full path to the chat log file (.txt): \n> ")
        all_messages = read_chat_from_file(file_path)
        if all_messages is None:
            print(f"Error: File not found at '{file_path}'. Please try again.")

    print(f"\nSuccessfully loaded {len(all_messages)} messages. Analyzing...")

    # --- STAGE 3: ANALYZE THE FULL CONVERSATION ---
    # We send the entire list of messages to the chat analyzer
    chat_analysis = analyze_chat_history(all_messages)
    
    # --- STAGE 4: CALCULATE & DISPLAY FINAL VERDICT ---
    final_verdict_score = calculate_final_verdict(
        profile_risk_score=profile_risk_score,
        chat_confidence_score=chat_analysis["spam_confidence_score"]
    )
    
    clear_screen()
    print("--- Final Threat Assessment ---")
    print(f"Profile Risk Score: {profile_risk_score} / 10")
    print("-" * 30)
    print("Chat Analysis (based on entire conversation):")
    print(f"  - Spam Confidence: {chat_analysis['spam_confidence_score']:.2f}%")
    print(f"  - Detected Intent: {chat_analysis['intent']}")
    print(f"  - Detected Keywords: {chat_analysis['keywords']}")
    print("-" * 30)
    print(f"FINAL VERDICT SCORE: {final_verdict_score:.2f}%")
    print("-" * 30)

    # --- STAGE 5: THE NUDGE ---
    if final_verdict_score > 60:
        print("\n🚨 HIGH RISK DETECTED! 🚨")
        print("This conversation is likely a honeytrap/scam based on the overall analysis.")
        print("Suggested Actions:")
        print("  [1] Block and Report (Recommended)")
        print("  [2] Engage Red Teaming Bot (Coming Soon!)")
    else:
        print("\n✅ Low to moderate risk detected.")
        print("Continue with caution, but no immediate high-threat indicators found.")

if __name__ == "__main__":
    run_sentinel()