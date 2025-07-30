from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

# NEW IMPORTS for updated LangChain memory and runnable history
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate # More modern way to define prompts
from langchain_core.messages import HumanMessage, AIMessage # For constructing history messages properly

load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_KEY")

# Ensure the API key is loaded
if not GOOGLE_API_KEY:
    raise ValueError("GEMINI_KEY environment variable not set. Please set it in your .env file or environment.")

# Define system prompt with red teaming tactics
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
# --- Updated Prompt Template ---
# Using ChatPromptTemplate is more robust for chat models
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt), # Your fixed system prompt
        ("placeholder", "{history}"), # Placeholder for past messages
        ("human", "{input}"), # Current user input
    ]
)

# Create a dictionary to store chat histories for different sessions/users
# In a real app with multiple users, you'd have a unique session_id for each user.
# For this simple test, we'll use a fixed 'test_session_id'.
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Retrieves or creates a ChatMessageHistory for a given session ID."""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Load Gemini model via LangChain
# Changed model to 'gemini-1.5-flash' - often more available and faster than 'gemini-pro'
# You can also try 'gemini-1.5-pro' for potentially higher quality responses.
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.8, google_api_key=GOOGLE_API_KEY)

# --- NEW CHAIN SETUP using RunnableWithMessageHistory ---
# 1. Create the core chain: Prompt | LLM
core_chain = prompt | llm

# 2. Wrap it with RunnableWithMessageHistory
#    - `chain`: The core LLM chain that takes input and history.
#    - `get_session_history`: Function to retrieve message history.
#    - `input_messages_key`: Key in the input dict for the *current* user message.
#    - `history_messages_key`: Key in the input dict where the *past* messages will be inserted by RunnableWithMessageHistory.
conversation_chain_with_history = RunnableWithMessageHistory(
    core_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# This function is what Streamlit will call
def get_bot_response(user_input: str, chat_history: list) -> str:
    """
    Given user input, returns a red teaming bot response.
    The `chat_history` parameter is present for Streamlit compatibility but
    is no longer used to populate the internal LangChain memory directly,
    as RunnableWithMessageHistory handles that.
    """
    session_id = "test_session_id" # Fixed session ID for local testing

    # Invoke the new chain.
    # The 'input' here corresponds to `input_messages_key`.
    # `config` is used to pass configurable parameters like the session_id.
    response = conversation_chain_with_history.invoke(
        {"input": user_input, "system_prompt": system_prompt}, # Pass system_prompt for the prompt template
        config={"configurable": {"session_id": session_id}}
    )
    
    # The response from the LLM is typically an AIMessage object. Extract its content.
    return response.content.strip()

if __name__ == "__main__":
    print("Bot activated. Type 'exit' to end the conversation.")
    # No need to manage current_chat_history manually for memory with RunnableWithMessageHistory.
    # It handles memory persistence using get_session_history and store.
    
    # We can still use a list for *displaying* the full conversation in the terminal
    # if you want to see all turns, but it's not strictly necessary for the bot's memory.
    display_chat_history = [] 

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Bot: Goodbye!")
            break

        # Get bot response using the updated function
        bot_response = get_bot_response(user_input, display_chat_history) # chat_history is passed but not used internally for memory

        # Update display_chat_history for terminal output
        display_chat_history.append(("user", user_input))
        display_chat_history.append(("bot", bot_response))

        print(f"Bot: {bot_response}")