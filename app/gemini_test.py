import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing")

client = genai.Client(api_key=api_key)

print("Testing Gemini...")

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Reply with exactly: GEMINI_OK",
)

print("\nResponse:")
print(response.text)