# --- app.py ---
# The Streamlit UI for Project Sentinel (with enhanced file-based logging)

import streamlit as st
import pandas as pd
import os
import logging
from datetime import datetime
import time # For performance timing

# Import our backend modules
from profile_analyzer import calculate_profile_risk
from chat_analyzer import analyze_chat_history
from verdict_engine import calculate_final_verdict
from bot import get_gemini_reply, system_prompt

# --- Logger Initialization ---
# This setup correctly creates a new log file for each run in the 'logs/app' directory.
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Set to INFO to avoid overly verbose DEBUG messages for now

# Check if handlers are already configured to avoid duplication in Streamlit reruns
if not logger.handlers:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs("logs/app", exist_ok=True)
    log_file = f"logs/app/{timestamp}.log"

    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# --- App Configuration ---
st.set_page_config(page_title="Project Sentinel", layout="wide")
logger.info("started")
# --- Helper Functions ---
def read_chat_from_file(uploaded_file):
    logger.info("Function entered: read_chat_from_file")
    try:
        string_data = uploaded_file.getvalue().decode("utf-8")
        messages = [line.strip() for line in string_data.split('\n') if line.strip()]
        logger.info(f"Successfully read {len(messages)} messages from file.")
        return messages
    except Exception as e:
        # Log the DETAILED error to the file for debugging
        logger.error(f"Error reading uploaded file: {e}", exc_info=True)
        # Show a SIMPLE error to the user in the UI
        st.error("Could not read the file. Please ensure it's a valid .txt file and try again.")
        return None

# --- Main App UI ---
st.title("🛡️ Project Sentinel: Honeytrap Detector")
logger.info("title displayed")
# --- Initialize Session State ---
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'red_team_mode' not in st.session_state:
    st.session_state.red_team_mode = False
if 'messages' not in st.session_state:
    st.session_state.messages = []


# --- Sidebar for Inputs ---
with st.sidebar:
    st.header("1. Profile Analysis")
    with st.form("profile_form"):
        username = st.text_input("Username")
        bio = st.text_area("Bio")
        followers = st.number_input("Followers", min_value=0, step=1)
        # ... (rest of the form is the same)
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
    logger.info("Process started: Analyze button clicked.")
    start_time = time.time()

    st.session_state.analysis_complete = False
    st.session_state.red_team_mode = False

    profile_data = {
        'username': username, 'bio': bio, 'followers': followers,
        'following': following, 'account_age_days': account_age_days,
        'has_profile_picture': has_profile_picture, 'is_private': is_private,
        'is_verified': is_verified
    }
    
    logger.info("Process step: Calculating profile risk...")
    st.session_state.profile_risk, st.session_state.profile_reasons = calculate_profile_risk(profile_data)
    logger.info(f"Process step complete: Profile risk score is {st.session_state.profile_risk}.")
    
    if uploaded_file is not None:
        all_messages = read_chat_from_file(uploaded_file)
        if all_messages:
            logger.info("Process step: Starting chat analysis...")
            st.session_state.chat_analysis = analyze_chat_history(all_messages)
            logger.info("Process step complete: Chat analysis finished.")

            logger.info("Process step: Calculating final verdict...")
            st.session_state.final_verdict = calculate_final_verdict(
                st.session_state.profile_risk,
                st.session_state.chat_analysis["spam_confidence_score"]
            )
            logger.info(f"Process step complete: Final verdict score is {st.session_state.final_verdict:.2f}.")

            st.session_state.analysis_complete = True
            st.session_state.initial_chat = all_messages
    else:
        st.warning("Please upload a chat file to get a full analysis.")
        logger.warning("Analysis submitted without a chat file.")

    end_time = time.time()
    logger.info(f"--- Total analysis duration: {end_time - start_time:.2f} seconds ---")


# --- Display Results if Analysis is Complete ---
if st.session_state.analysis_complete:
    # ... (This entire display section remains the same as before)
    st.header("Threat Assessment Results")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Profile Risk Score", f"{st.session_state.profile_risk} / 10")
    col2.metric("Chat Spam Confidence", f"{st.session_state.chat_analysis['spam_confidence_score']:.2f}%")
    col3.metric("🚨 FINAL VERDICT", f"{st.session_state.final_verdict:.2f}%", 
                 delta_color="off" if st.session_state.final_verdict < 60 else "inverse")

    with st.expander("Show Detailed Analysis"):
        st.subheader("Profile Risk Factors:")
        for reason in st.session_state.profile_reasons:
            st.write(f"- {reason}")
        
        st.subheader("Chat Analysis:")
        st.write(f"- **Detected Intent:** {st.session_state.chat_analysis['intent']}")
        st.write(f"- **Suspicious Keywords Found:** {', '.join(st.session_state.chat_analysis['keywords'])}")
    
    # --- Action Nudge ---
    if st.session_state.final_verdict > 60:
        st.warning("HIGH RISK DETECTED!")
        
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
                st.session_state.messages = [{"role": "user", "parts": [system_prompt]}]
                st.session_state.messages.append({"role": "model", "parts": ["okay, i'm ready. what did they say back?"]})

# --- In app.py, replace the final 'if st.session_state.red_team_mode:' block ---

# --- Red Teaming Bot Chat Interface ---
if st.session_state.red_team_mode:
    st.divider()
    st.header("🤖 Red Teaming Bot Session")

    # The API key is now loaded from .env, so we don't need to ask for it.
    
    # Initialize the display history if it doesn't exist
    if "display_messages" not in st.session_state:
        st.session_state.display_messages = []

    # Display existing chat messages from our display history
    for message in st.session_state.display_messages:
        role = "You (Alex)" if message["role"] == "assistant" else "Scammer"
        with st.chat_message(name=role):
            st.markdown(message["content"])
    
    # The chat input widget
    if prompt := st.chat_input("You are scammer now, enter some messages to see how the bot will converse from your account after reporting..."):
        logger.info(f"Red Team Input (from scammer): '{prompt}'")

        # Add user's message to the display list and show it immediately
        st.session_state.display_messages.append({"role": "user", "content": prompt})
        with st.chat_message(name="Scammer"):
            st.markdown(prompt)

        # Get and display the bot's reply
        with st.spinner("User is typing..."):
            logger.info("Sending request to LangChain Gemini bot...")
            
            # --- THIS IS THE KEY CHANGE ---
            # We now call the new function with only the user's prompt.
            # LangChain handles the memory internally.
            reply = get_gemini_reply(prompt)
            # -----------------------------

            logger.info("Received reply from LangChain bot.")
            # Add bot's reply to the display list
            st.session_state.display_messages.append({"role": "assistant", "content": reply})
            with st.chat_message(name="You (Alex)"):
                st.markdown(reply)
            
            # Rerun to show the new message immediately
            st.rerun()