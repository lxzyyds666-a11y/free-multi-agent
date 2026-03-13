import json
import os
from google import genai

MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY")
    return genai.Client(api_key=api_key)


def ask_json(system_prompt: str, user_prompt: str) -> dict:
    client = get_client()
    response = client.models.generate_content(
        model=MODEL,
        contents=f"{system_prompt}\n\n---\n\n{user_prompt}",
    )
    text = (response.text or "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        cleaned = text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
