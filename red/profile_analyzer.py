# --- profile_analyzer.py ---
# Milestone 1 of Project Sentinel

def get_profile_data_from_user():
    """
    Interactively prompts the user for the target's profile information.
    Includes basic validation for numeric and boolean inputs.
    Returns a dictionary containing all the profile data.
    """
    profile_data = {}
    print("--- Sentinel: Profile Analyzer ---")
    print("Please provide the following details about the target account.")

    # Get textual information
    profile_data['username'] = input("Enter the username: ")
    profile_data['bio'] = input("Paste the bio text: ")

    # Get numeric information with validation
    while True:
        try:
            profile_data['followers'] = int(input("Enter follower count: "))
            profile_data['following'] = int(input("Enter following count: "))
            profile_data['account_age_days'] = int(input("Enter account age (in days): "))
            break
        except ValueError:
            print("Invalid input. Please enter whole numbers for counts and age.")

    # Get boolean (yes/no) information with validation
    def get_yes_no_input(prompt):
        while True:
            answer = input(prompt + " (y/n): ").lower()
            if answer in ['y', 'yes']:
                return True
            elif answer in ['n', 'no']:
                return False
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    profile_data['has_profile_picture'] = get_yes_no_input("Does it have a profile picture?")
    profile_data['is_private'] = get_yes_no_input("Is the account private?")
    profile_data['is_verified'] = get_yes_no_input("Is the account verified?")
    
    return profile_data

def calculate_profile_risk(profile_data: dict):
    """
    Calculates a risk score from 0-10 based on a set of rules.

    Args:
        profile_data: A dictionary containing the target's profile info.

    Returns:
        A tuple containing the integer risk score (0-10) and a list of
        reasons (strings) for the score.
    """
    score = 0
    risk_factors_found = []
    
    # --- Rule Engine ---

    # Rule 0: Verified accounts are considered safe. This overrides all other rules.
    if profile_data['is_verified']:
        return 0, ["Account is officially verified."]

    # Rule 1: Suspicious Follower/Following Ratio (e.g., following many, few followers)
    # A high ratio is a classic bot/spam indicator.
    if profile_data['followers'] < 100 and profile_data['following'] > profile_data['followers'] * 5:
        score += 3
        risk_factors_found.append("High following-to-follower ratio (potential bot/spam behavior).")

    # Rule 2: New Account Age
    if profile_data['account_age_days'] < 30:
        score += 2
        risk_factors_found.append("Very new account (less than 30 days old).")

    # Rule 3: Missing Profile Picture
    if not profile_data['has_profile_picture']:
        score += 2
        risk_factors_found.append("No profile picture.")

    # Rule 4: Suspicious Keywords in Bio
    suspicious_words = ["crypto", "forex", "invest", "trader", "DM for rates", "cashapp"]
    bio_lower = profile_data['bio'].lower()
    if any(word in bio_lower for word in suspicious_words):
        score += 3
        risk_factors_found.append("Bio contains suspicious keywords (e.g., crypto, invest).")

    # Rule 5: Extremely low follower count
    if profile_data['followers'] < 15:
        score += 1
        risk_factors_found.append("Extremely low follower count.")

    # Cap the final score at 10 to keep it on a consistent scale
    final_score = min(score, 10)
    
    if not risk_factors_found:
        risk_factors_found.append("No major risk factors detected in profile.")

    return final_score, risk_factors_found

def run_profile_analyzer():
    """Main function to run the profile analysis module. """
    profile_info = get_profile_data_from_user()
    
    print("\n--- Analyzing Profile ---")
    
    risk_score, reasons = calculate_profile_risk(profile_info)
    
    print("\n--- Analysis Complete ---")
    print(f"Profile Risk Score: {risk_score} / 10")
    print("Reasons:")
    for reason in reasons:
        print(f"  - {reason}")

# This makes the script runnable from the command line
if __name__ == "__main__":
    run_profile_analyzer()