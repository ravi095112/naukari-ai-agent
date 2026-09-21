import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Return a proposal for adding REST API as a skill.",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "object",
            "properties": {
                "skill": {"type": "string"},
                "action": {
                    "type": "string",
                    "enum": ["PROPOSE"]
                }
            },
            "required": ["skill", "action"]
        }
    )
)

print("Response:")
print(response.text)

print("\nParsed:")
print(json.loads(response.text))