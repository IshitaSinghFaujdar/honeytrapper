# --- app.py (Final Integrated Version with Auto-Concluding Bot) ---
import streamlit as st
import os
import logging
from datetime import datetime
import time

# Import our backend modules
from profile_analyzer import calculate_profile_risk
from chat_analyzer import analyze_chat_history
from verdict_engine import calculate_final_verdict
from bot import get_gemini_reply, system_prompt # Use capital SYSTEM_PROMPT from bot.py

# --- Logger Initialization ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs("logs", exist_ok=True) 
    log_file = f"logs/app_{timestamp}.log"

    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# --- App Configuration ---
st.set_page_config(page_title="Project Sentinel", layout="wide")
logger.info("Application session started.")

# --- Helper Functions ---
def read_chat_from_file(uploaded_file):
    logger.info("Function entered: read_chat_from_file")
    try:
        string_data = uploaded_file.getvalue().decode("utf-8")
        messages = [line.strip() for line in string_data.split('\n') if line.strip()]
        logger.info(f"Successfully read {len(messages)} messages from file.")
        return messages
    except Exception as e:
        logger.error(f"Error reading uploaded file: {e}", exc_info=True)
        st.error("Could not read the file. Please ensure it's a valid .txt file and try again.")
        return None

# --- Main App UI ---
st.title("🛡️ Project Sentinel: Honeytrap Detector")

# --- Initialize Session State ---
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'red_team_mode' not in st.session_state:
    st.session_state.red_team_mode = False
if 'display_messages' not in st.session_state:
    st.session_state.display_messages = []
if 'investigation_concluded' not in st.session_state:
    st.session_state.investigation_concluded = False


# --- Sidebar for Inputs ---
with st.sidebar:
    st.header("1. Profile Analysis")
    with st.form("profile_form"):
        username = st.text_input("Username")
        bio = st.text_area("Bio")
        followers = st.number_input("Followers", min_value=0, step=1)
        following = st.number_input("Following", min_value=0, step=1)
        account_age_days = st.number_input("Account Age (days)", min_value=0, step=1)
        has_profile_picture = st.selectbox("Has Profile Picture?", (True, False))
        is_private = st.selectbox("Is Account Private?", (True, False))
        is_verified = st.selectbox("Is Account Verified?", (True, False))

        st.header("2. Upload Chat Log")
        uploaded_file = st.file_uploader("Upload chat history (.txt)", type="txt")
        submit_button = st.form_submit_button("Analyze")

# --- Main Panel for Outputs ---
if submit_button:
    logger.info("="*20 + " NEW ANALYSIS STARTED " + "="*20)
    start_time = time.time()
    # Reset all relevant flags for a new analysis
    st.session_state.analysis_complete = False
    st.session_state.red_team_mode = False
    st.session_state.investigation_concluded = False
    st.session_state.display_messages = []


    profile_data = {
        'username': username, 'bio': bio, 'followers': followers,
        'following': following, 'account_age_days': account_age_days,
        'has_profile_picture': has_profile_picture, 'is_private': is_private,
        'is_verified': is_verified
    }
    
    logger.info("Calculating profile risk...")
    st.session_state.profile_risk, st.session_state.profile_reasons = calculate_profile_risk(profile_data)
    logger.info(f"Profile risk score is {st.session_state.profile_risk}.")
    
    if uploaded_file is not None:
        all_messages = read_chat_from_file(uploaded_file)
        if all_messages:
            logger.info("Starting tiered hybrid chat analysis...")
            st.session_state.chat_analysis = analyze_chat_history(all_messages)
            logger.info("Tiered hybrid chat analysis finished.")

            logger.info("Calculating final verdict...")
            st.session_state.final_verdict = calculate_final_verdict(
                st.session_state.profile_risk,
                st.session_state.chat_analysis
            )
            logger.info(f"Final verdict score is {st.session_state.final_verdict:.2f}.")

            st.session_state.analysis_complete = True
            st.session_state.initial_chat = all_messages
    else:
        st.warning("Please upload a chat file to get a full analysis.")
        logger.warning("Analysis submitted without a chat file.")

    end_time = time.time()
    logger.info(f"--- Total analysis duration: {end_time - start_time:.2f} seconds ---")


# --- Display Results if Analysis is Complete ---
if 'analysis_complete' in st.session_state and st.session_state.analysis_complete:
    analysis = st.session_state.chat_analysis
    st.header("Threat Assessment Results")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Profile Risk Score", f"{st.session_state.profile_risk} / 10")
    col2.metric("Primary Chat Threat", analysis.get('primary_intent', 'N/A'))
    col3.metric("🚨 FINAL VERDICT", f"{st.session_state.final_verdict:.2f}%", 
                 delta_color="off" if st.session_state.final_verdict < 60 else "inverse")

    with st.expander("Show Detailed Analysis"):
        st.subheader("Profile Risk Factors:")
        for reason in st.session_state.profile_reasons:
            st.write(f"- {reason}")
        
        st.subheader("Chat Analysis Confidence:")
        st.write(f"- **Sextortion/Blackmail:** {analysis.get('sextortion_confidence_score', 0):.0f}%")
        st.write(f"- **Tech Honeytrap/Scam:** {analysis.get('tech_honeytrap_score', 0):.0f}%")
        st.write(f"- **General Spam/Scam:** {analysis.get('spam_confidence_score', 0):.0f}%")
        
        st.subheader("⚠️ Psychological Tactic Analysis:")
        psych_results = analysis.get('psychological_analysis', {})
        if not psych_results or psych_results.get('total_risk_score', 0) == 0:
            st.success("No major psychological manipulation tactics detected.")
        else:
            for tactic, details in psych_results.items():
                if tactic != 'total_risk_score':
                    st.warning(f"**Detected Tactic: {tactic}**")
                    st.markdown("**Evidence Found:**")
                    for evidence_line in details['evidence']:
                        st.text(f'  - "{evidence_line}"')

    # --- Threat-specific action nudges ---
    primary_threat = analysis.get('primary_intent')
    if primary_threat == 'Sextortion/Blackmail':
        st.error("🚨 **CRITICAL SEXTORTION RISK DETECTED!**", icon="🚨")
        st.warning(...) # Your detailed warning text here
    elif primary_threat == 'Tech Honeytrap/Scam':
        st.error("🚨 **HIGH-RISK TECH SCAM DETECTED!**", icon="💻")
        st.warning(...) # Your detailed warning text here
    elif st.session_state.final_verdict > 60:
        st.warning("HIGH RISK DETECTED!")
    
    # --- Action buttons for high-risk scenarios ---
    if st.session_state.final_verdict > 60:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Action: Block & Report", use_container_width=True):
                logger.info("User action: Chose 'Block & Report'.")
                st.success("Recommendation noted. Please block and report the user on their platform.")
                st.session_state.red_team_mode = False

        with col2:
            if st.button("Engage Red Teaming Bot 🤖", use_container_width=True):
                logger.info("User action: Chose 'Engage Red Teaming Bot'.")
                st.session_state.red_team_mode = True
                st.session_state.display_messages = []
                st.session_state.investigation_concluded = False # Reset for new session


# --- Red Teaming Bot Chat Interface (UPGRADED) ---
if st.session_state.red_team_mode:
    st.divider()
    st.header("🤖 Red Teaming Bot Session")
    
    # --- NEW: Message display loop now handles system warnings ---
    for message in st.session_state.display_messages:
        if message["role"] == "system_warning":
            st.warning(message["content"], icon="🤖")
        else:
            role = "You (Alex)" if message["role"] == "assistant" else "Scammer"
            with st.chat_message(name=role):
                st.markdown(message["content"])

    # Check the session state flag to see if the investigation is over
    investigation_over = st.session_state.get("investigation_concluded", False)
    
    if prompt := st.chat_input("Enter the scammer's latest message...", disabled=investigation_over):
        logger.info(f"Red Team Input (from scammer): '{prompt}'")
        
        # We append the user message right away so it appears instantly
        st.session_state.display_messages.append({"role": "user", "content": prompt})

        with st.spinner("Alex is thinking and analyzing..."):
            logger.info("Sending request to Gemini bot...")
            
            # This now returns a richer dictionary
            bot_response_dict = get_gemini_reply(prompt)
            reply = bot_response_dict.get("reply", "Sorry, an error occurred.")
            status = bot_response_dict.get("status", "engaging")
            
            # --- FEATURES 1 & 2 ADDITION: Check for new flags from the bot ---
            ai_detected = bot_response_dict.get("ai_detected", False)
            mimicking_detected = bot_response_dict.get("mimicking_detected", False)

            if ai_detected:
                logger.warning("AI-like response pattern detected from user.")
                st.session_state.display_messages.append({
                    "role": "system_warning",
                    "content": "⚠️ **AI DETECTED:** The message pattern suggests you may be interacting with an automated bot, not a human."
                })
            
            if mimicking_detected:
                logger.warning("Deep behavioral mimicking detected from user.")
                st.session_state.display_messages.append({
                    "role": "system_warning",
                    "content": "🚨 **DEEP MIMICKING DETECTED:** The user is closely mirroring the language and style of your previous messages. This is a common manipulation tactic to build false rapport."
                })
            
            logger.info(f"Received reply from bot with status: {status}")
            
            # Append the bot's actual reply
            st.session_state.display_messages.append({"role": "assistant", "content": reply})
            
            # --- FEATURE 3 RE-CHECK: Logic for conclusion ---
            if status == "concluded":
                st.session_state.investigation_concluded = True
            
            st.rerun()

    # --- FEATURE 3 RE-CHECK: Enhanced conclusion display with balloons ---
    if st.session_state.get("investigation_concluded", False):
        st.success("🎉 **Investigation Concluded! A definitive trigger was found.** 🎉", icon="🎯")
        st.balloons()
        st.info("The chat input has been disabled. You can now Block & Report or start a new analysis.")