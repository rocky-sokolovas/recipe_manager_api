from dotenv import load_dotenv
import os

load_dotenv()

# Example usage
api_key = os.getenv("API_KEY")
print("API Key loaded:", api_key)
