import os
from google import genai

def main():
    # It's best practice to use environment variables for your API key
    # or replace 'YOUR_API_KEY' with your actual key string
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyBClvj9a_32WbqbIeinn6aRZshOoozP-gM")

    # 1. Initialize the Client
    client = genai.Client(api_key=api_key)

    # 2. Start a Chat Session
    # The 'chats' attribute is a manager that creates sessions
    chat = client.chats.create(model="gemini-2.5-flash")

    print("--- Gemini Chat Started (Type 'exit' to stop) ---")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            # 3. Send message and get response
            response = chat.send_message(user_input)
            print(f"Gemini: {response.text}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()