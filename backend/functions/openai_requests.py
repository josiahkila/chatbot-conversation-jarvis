from openai import OpenAI
from functions.database import get_recent_messages
import os

# Get the OpenAI API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set or invalid")

# Initialize the OpenAI client with the API key
openai = OpenAI(api_key=api_key)

def get_chat_response(message_input):
    messages = get_recent_messages()
    user_message = {
        "role": "user",
        "content": message_input + " Only say two or 3 words in Spanish if speaking in Spanish. The remaining words should be in English"
    }
    messages.append(user_message)
    print("Current message context:", messages)

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        message_text = response.choices[0].message.content
        return message_text
    except Exception as e:
        print(f"Error getting chat response: {e}")
        return None
