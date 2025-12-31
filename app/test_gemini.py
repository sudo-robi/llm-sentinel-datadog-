import os
import sys
from google import genai

def main():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print(" ERROR: GEMINI_API_KEY environment variable not set.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    chat = client.chats.create(model="gemini-2.0-flash")

    print("\n✨ Gemini Chat Started (Type 'exit' to stop)")
    print("-" * 40)

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            response = chat.send_message(user_input)
            
            if response.text:
                print(f"Gemini: {response.text}")
            else:
                print("Gemini: [No response text returned]")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()