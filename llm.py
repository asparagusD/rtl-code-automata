import os
from openai import OpenAI

# Initialize the OpenAI client for Google AI Studio
client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

MODEL = "gemini-2.5-flash"

def chat_completion(messages, tools=None):
    """
    Wrapper for openai.chat.completions.create
    """
    kwargs = {
        "model": MODEL,
        "messages": messages,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
        
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message
