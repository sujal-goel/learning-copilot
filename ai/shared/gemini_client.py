import asyncio
import os
import time
import json
import re
from google import genai
from google.genai import errors
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"[Gemini Client] Initialization warning: {e}")

MODEL_FALLBACKS = [
    "gemini-3.6-flash",
    "gemini-3.1-pro",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
]


def call_llm(prompt: str, system_instruction: str | None = None, max_retries: int = 3) -> str:
    """
    Calls Gemini LLM with dynamic model fallback and exponential backoff retry.
    """
    if not client:
        raise RuntimeError("GEMINI_API_KEY is not set or client failed to initialize.")

    config = {}
    if system_instruction:
        config["system_instruction"] = system_instruction

    last_error = None
    for model_name in MODEL_FALLBACKS:
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config if config else None,
                )
                if response and response.text:
                    return response.text.strip()
            except errors.APIError as e:
                last_error = e
                # Check for rate limit / overload error
                if getattr(e, "code", None) in [429, 503, 500] or "quota" in str(e).lower():
                    sleep_time = 0.5 * (2 ** attempt)
                    time.sleep(sleep_time)
                    continue
                else:
                    # Model specific error, try next model in fallback list
                    break
            except Exception as e:
                last_error = e
                sleep_time = 0.5 * (2 ** attempt)
                time.sleep(sleep_time)
                continue

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")


def call_llm_json(prompt: str, system_instruction: str | None = None) -> dict:
    """
    Calls call_llm and parses output as clean JSON object.
    """
    raw_text = call_llm(prompt, system_instruction)
    # Strip markdown code blocks
    cleaned = raw_text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback regex extraction if needed
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"Failed to parse LLM response as JSON: {raw_text[:200]}...")


async def call_llm_async(prompt: str, system_instruction: str | None = None) -> str:
    """Async wrapper — runs the blocking Gemini SDK in a thread pool so it doesn't block the event loop."""
    return await asyncio.to_thread(call_llm, prompt, system_instruction)


async def call_llm_json_async(prompt: str, system_instruction: str | None = None) -> dict:
    """Async JSON wrapper — runs call_llm_json in a thread pool."""
    return await asyncio.to_thread(call_llm_json, prompt, system_instruction)