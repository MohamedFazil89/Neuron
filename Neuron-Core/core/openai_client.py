import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY not found in environment variables")

def call_openai(prompt, max_tokens=1500, temperature=0.2, system_prompt=None):
    """
    Call OpenAI and return raw text output.
    This is a LOW-LEVEL function.
    It does NOT parse JSON.
    It does NOT validate output.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # cheap + reliable for structured work or gpt-5.1-codex for coding
            messages=[
                {
                    "role": "system",
                    "content": system_prompt or "You are a precise software engineering assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"OpenAI call failed: {str(e)}")

def call_openai_json(prompt, max_tokens=1500, system_prompt=None):
    """
    Call OpenAI and FORCE JSON output.
    This is what agents should use.
    If JSON is invalid, this function FAILS loudly.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt or "You are a precise software engineering assistant. You output ONLY valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=max_tokens,
            temperature=0.2,
            response_format={"type": "json_object"}  # FORCE JSON MODE
        )
        
        raw = response.choices[0].message.content.strip()
        
        # Strip markdown if model disobeys (shouldn't happen with json_object mode)
        if "```" in raw:
            raw = raw.split("```")[1]
            raw = raw.replace("json", "").strip()
        
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise Exception(
            "Failed to parse JSON from OpenAI response.\n"
            f"Raw response:\n{raw}\n"
            f"Error: {str(e)}"
        )
    except Exception as e:
        raise Exception(f"OpenAI JSON call failed: {str(e)}")
