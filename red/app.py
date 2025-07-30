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

# --- Logger Initialization (Unchanged) ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs("logs/app", exist_ok=True)
    log_file = f"logs/app/{timestamp}.log"
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# --- App Configuration (Unchanged) ---
st.set_page_config(page_title="Project Sentinel", layout="wide")
logger.info("Application session started.")

# --- Helper Functions (Unchanged) ---
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

# --- Main App UI (Unchanged) ---
st.title("🛡️ Project Sentinel: Honeytrap Detector")

# --- Initialize Session State (Unchanged) ---
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'red_team_mode' not in st.session_state:
    st.session_state.red_team_mode = False
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- Sidebar for Inputs (Unchanged) ---
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

# --- Main Panel for Outputs (MODIFIED) ---
if submit_button:
    logger.info("="*20 + " NEW ANALYSIS STARTED " + "="*20)
    start_time = time.time()
    st.session_state.analysis_complete = False
    st.session_state.red_team_mode = False

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
            logger.info("Starting tiered chat analysis...")
            st.session_state.chat_analysis = analyze_chat_history(all_messages)
            logger.info("Chat analysis finished.")

            # --- MODIFIED: Pass the entire analysis dictionary to the verdict engine ---
            logger.info("Calculating final verdict based on tiered analysis...")
            st.session_state.final_verdict = calculate_final_verdict(
                st.session_state.profile_risk,
                st.session_state.chat_analysis  # Pass the whole object now
            )
            logger.info(f"Final verdict score is {st.session_state.final_verdict:.2f}.")

            st.session_state.analysis_complete = True
            st.session_state.initial_chat = all_messages
    else:
        st.warning("Please upload a chat file to get a full analysis.")
        logger.warning("Analysis submitted without a chat file.")

    end_time = time.time()
    logger.info(f"--- Total analysis duration: {end_time - start_time:.2f} seconds ---")


# --- Display Results if Analysis is Complete (COMPLETELY OVERHAULED) ---
if st.session_state.analysis_complete:
    analysis = st.session_state.chat_analysis
    st.header("Threat Assessment Results")
    
    # --- NEW: More informative metrics ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Profile Risk Score", f"{st.session_state.profile_risk} / 10")
    col2.metric("Primary Chat Threat", analysis.get('primary_intent', 'N/A'))
    col3.metric("🚨 FINAL VERDICT", f"{st.session_state.final_verdict:.2f}%", 
                 delta_color="off" if st.session_state.final_verdict < 60 else "inverse")

    # --- NEW: More detailed expander ---
    with st.expander("Show Detailed Analysis"):
        st.subheader("Profile Risk Factors:")
        for reason in st.session_state.profile_reasons:
            st.write(f"- {reason}")
        
        st.subheader("Chat Analysis Confidence:")
        st.write(f"- **Sextortion/Blackmail:** {analysis.get('sextortion_confidence_score', 0)}%")
        st.write(f"- **Tech Honeytrap/Scam:** {analysis.get('tech_honeytrap_score', 0)}%")
        st.write(f"- **General Spam/Scam:** {analysis.get('spam_confidence_score', 0)}%")
        
        st.subheader("Suspicious Keywords Found:")
        st.write(f"- **Sextortion:** {', '.join(analysis['keywords_found']['sextortion']) or 'None'}")
        st.write(f"- **Tech:** {', '.join(analysis['keywords_found']['tech']) or 'None'}")
        st.write(f"- **General Spam:** {', '.join(analysis['keywords_found']['spam']) or 'None'}")

    # --- NEW: Threat-specific action nudges ---
    primary_threat = analysis.get('primary_intent')
    if primary_threat == 'Sextortion/Blackmail':
        st.error("🚨 **CRITICAL SEXTORTION RISK DETECTED!**")
        st.warning(
            """
            **Immediate Recommended Actions:**
            1. **DO NOT PAY OR SEND ANYTHING.** This will likely lead to more demands.
            2. **Stop all communication.** Block the user on all platforms immediately.
            3. **Preserve all evidence.** Take screenshots of the chat, profile, and any payment requests.
            4. **Report the user** to the platform and consider reporting to law enforcement. Sextortion is a serious crime.
            """
        )
    elif primary_threat == 'Tech Honeytrap/Scam':
        st.error("🚨 **HIGH-RISK TECH SCAM DETECTED!**")
        st.warning(
            """
            **Immediate Recommended Actions:**
            - **DO NOT download or run any files.** They may contain malware.
            - **DO NOT provide credentials, API keys, or personal information.**
            - **Verify any job offers** through the company's official website or official LinkedIn page.
            - **Be skeptical** of any "guaranteed returns" on investments.
            """
        )
    elif st.session_state.final_verdict > 60:
        st.warning("HIGH RISK DETECTED!")
    
    # Action buttons are now relevant for any high-risk scenario
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
                st.session_state.display_messages = [] # Initialize display messages for the new bot
                # The LangChain bot now handles its own history, so we don't need to prime it.


# --- Red Teaming Bot Chat Interface (REPLACED AS REQUESTED) ---
if st.session_state.red_team_mode:
    st.divider()
    st.header("🤖 Red Teaming Bot Session")
    
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
            
            # Call the new function with only the user's prompt. LangChain handles memory.
            reply = get_gemini_reply(prompt)
            
            logger.info("Received reply from LangChain bot.")
            # Add bot's reply to the display list
            st.session_state.display_messages.append({"role": "assistant", "content": reply})
            with st.chat_message(name="You (Alex)"):
                st.markdown(reply)
            
            # Rerun to show the new message immediately
            st.rerun()