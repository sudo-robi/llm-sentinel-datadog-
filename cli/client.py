# cli.py
import requests

API_URL = "http://127.0.0.1:8000/chat"

def main():
    print("=== LLM Sentinel CLI ===")
    while True:
        prompt = input("\nEnter prompt (or 'exit' to quit): ")
        if prompt.lower() == "exit":
            print("Exiting CLI.")
            break

        try:
            response = requests.post(API_URL, json={"prompt": prompt})
            response.raise_for_status()
            data = response.json()
            print(f"\n[LLM Response]: {data.get('response')}")
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with server: {e}")

if __name__ == "__main__":
    main()
