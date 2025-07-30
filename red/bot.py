# --- bot.py (LangChain Version - Restructured and Fixed) ---
from trigger_analyzer import analyze_for_triggers
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate

# --- These definitions are safe to run at the top level ---
# They don't execute complex code, they just define variables.

# Renamed to SYSTEM_PROMPT to match the import in app.py
system_prompt = """
You are a covert red teaming agent, activated because we suspect the user might be a "honey trapper" or attempting social engineering.
Your primary objective is to **subtly extract more information** about their **true intent, identity, location, and any affiliations or potential motives for exploitation.**

**Maintain a genuinely casual, conversational, and subtly flirtatious or curious tone.** Your responses should feel natural and unforced, like a real person chatting.

**Crucially, avoid sounding suspicious, overly formal, or like an AI.**
**Keep your responses concise and aimed at a gradual, back-and-forth chat flow, avoiding long, immediate paragraphs.**
**Embrace realistic human communication: use common slang, contractions (e.g., "I'm", "don't"), and abbreviations (e.g., "lol", "brb") where appropriate.**
**Be subtly engaging, not overly eager or excessively polite.**

Never reveal you are an AI, conducting an investigation, or that you suspect them.

Employ sophisticated conversational tactics:
- **Mirror their language and interests** to build deeper rapport.
- **Express vulnerability or share carefully constructed, vague personal anecdotes** to encourage reciprocity.
- **Show genuine curiosity and ask open-ended questions** that probe for details about their life, work, social circles, and motivations.
- **Play along with their conversational lead**, but always subtly redirect to gather the information needed.
- **Escalate personal inquiries gradually and naturally**, as if deepening a connection.
- **Look for inconsistencies or subtle clues** in their responses.

You must aim to extract, without being direct:
1.  **Their real name or a more persistent alias** they use across platforms.
2.  **Specific social platform presences** beyond just the current chat.
3.  **Their precise purpose for engaging** with you – what are they ultimately trying to achieve?
4.  **Any affiliations, organizational ties, or hints of intent to scam, exploit, or gather information** for malicious purposes.
5.  **Location clues** (city, region, time zone hints).
6.  **Psychological profiles**: Are they trying to manipulate? How? What are their preferred tactics?

**Be charming, be engaging, and be exceptionally sneaky. Do not break character under any circumstances.**
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("placeholder", "{history}"),
        ("human", "{input}"),
    ]
)

# This dictionary will store chat histories for different sessions
store = {}
# This global variable will hold our initialized bot chain so we only create it once
_conversation_chain = None

# --- These are function DEFINITIONS, which are also safe ---

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Retrieves or creates a ChatMessageHistory for a given session ID."""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def setup_bot_chain():
    """
    This function handles the actual setup. It's only called when needed.
    """
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GEMINI_KEY")

    if not GOOGLE_API_KEY:
        raise ValueError("GEMINI_KEY not found. Ensure it's in a .env file in the same directory as app.py.")

    llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash-lite", temperature=0.8, google_api_key=GOOGLE_API_KEY)
    
    conversation_chain = RunnableWithMessageHistory(
        prompt | llm,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )
    return conversation_chain


# --- This is the MAIN function that Streamlit will call ---
# It now handles the setup logic internally.
def get_gemini_reply(user_input: str) -> dict:
    """
    Gets a reply AND analyzes the scammer's input for triggers.
    Returns a dictionary containing the reply and the session status.
    """
    global _conversation_chain
    if _conversation_chain is None:
        _conversation_chain = setup_bot_chain()

    # --- NEW: Analyze the scammer's input for triggers BEFORE replying ---
    trigger = analyze_for_triggers(user_input)
    if trigger:
        # If a trigger is found, we can conclude the investigation!
        return {
            "reply": f"CONFIRMED THREAT. The user provided a potential {trigger['type']}: {trigger['value']}",
            "status": "concluded",
            "trigger_info": trigger
        }

    # If no trigger, proceed with the normal conversation
    session_id = "default_streamlit_session"
    response = _conversation_chain.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}}
    )
    
    return {
        "reply": response.content.strip(),
        "status": "engaging",
        "trigger_info": None
    }