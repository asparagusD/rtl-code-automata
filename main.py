import os
from dotenv import load_dotenv
from openai import OpenAI

def main():
    # Load environment variables from the .env file
    load_dotenv()

    # Get the Google API key
    google_api_key = os.getenv("GOOGLE_API_KEY")
    
    if not google_api_key or google_api_key == "your_key_here":
        print("Please set your GOOGLE_API_KEY in the .env file!")
        return

    print("Environment loaded successfully. API Key is ready.")

    # Example of setting up the OpenAI client to use Gemini's OpenAI-compatible API
    # client = OpenAI(
    #     api_key=google_api_key,
    #     base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    # )
    
    # response = client.chat.completions.create(
    #     model="gemini-2.5-flash",
    #     messages=[
    #         {"role": "user", "content": "Hello! Are you Gemini?"}
    #     ]
    # )
    # print(response.choices[0].message.content)

if __name__ == "__main__":
    main()
