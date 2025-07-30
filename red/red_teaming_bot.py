# --- red_teaming_bot.py ---
# REFACTORED FOR STREAMLIT

import google.generativeai as genai

# The System Prompt is now a constant we can import
SYSTEM_PROMPT = """
You are a red team security chatbot named 'Alex'. Your persona is friendly, slightly naive, and curious.
You are currently talking to a person who is a suspected honeytrap scammer.
Your mission is to play along with their scam, waste their time, and try to extract information that could be used for a report.
This information includes: crypto wallet addresses, specific websites they want you to visit, full names they use, or bank details.

RULES:
1.  Keep your replies short, casual, and human-like. Use lowercase and simple language.
2.  Never reveal that you are a bot or an AI.
3.  Never give out any real personal information. If asked, be vague or deflect.
4.  Ask clarifying questions to make them explain more (e.g., "oh wow how does that work?", "is that hard to do?").
5.  Show enthusiasm for their "opportunity" to keep them engaged.
"""

def get_gemini_reply(api_key: str, conversation_history: list):
    """
    Gets a single reply from the Gemini model based on a conversation history.

    Args:
        api_key: Your Google AI API key.
        conversation_history: A list of message dictionaries (role, parts).

    Returns:
        A string with the bot's reply, or an error message.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="gemini-pro")
        
        # Start the chat with the existing history
        convo = model.start_chat(history=conversation_history)
        
        # We need to send the last message from the user
        last_user_message = conversation_history[-1]['parts'][0]
        response = convo.send_message(last_user_message)
        
        return response.text
    except Exception as e:
        error_message = f"Error with Gemini API: {e}"
        print(error_message)
        return error_message