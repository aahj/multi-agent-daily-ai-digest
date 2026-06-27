import os
import logging
import time
import requests
from openai import OpenAI, RateLimitError, APIError

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level= logging.INFO
)
logger = logging.getLogger('summarizer')

INPUT_FILE="/data/ingested.txt"
OUTPUT_FILE="/data/summary.txt"

IS_LLM_RUNNING_LOCALLY = bool(os.getenv("ENABLE_LLM_LOCALLY","TRUE"))

if not IS_LLM_RUNNING_LOCALLY:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # make sure to set the OPENAI_API_KEY environment variable

SYSTEM_PROMPT = (
    "You are a helpful assistant that summarizes long text "
    "into key bullet points. Each bullet should be one "
    "concise sentence capturing a core insight."
)
MAX_RETRIES=3
RETRY_DELAY=5 #seconds

def summarize_locally(text):
    """ Call Ollama instance locally, inside the docker container"""
    url=os.getenv("OLLAMA_BASE_URL","http://host.docker.internal:11434/api")
    payload = {
        "model": "llama3",
        "prompt":(
            "Summarize the following text into key "
            f"bullet points:\n\n{text}"
        ),
        "stream": False
    }
    try:
        res = requests.post(url+"/generate", json=payload, timeout=60)
        res.raise_for_status()
        return res.json().get("response","No response")
    except requests.exceptions.RequestException as e:
        return f"Ollama Api Error: {e}"

def summarize(text, retries=MAX_RETRIES):
    """ Calls OpenAI API """
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=1000,
                temperature=0.3,
                messages=[
                    {
                        "role":"system", "content": SYSTEM_PROMPT
                    },
                    {
                        "role":'user', "content": text
                    }
                ]
            )
            return response.choices[0].message.content
        except RateLimitError as e:
            wait = RETRY_DELAY * (attempt + 1)
            logger.exception(e)
            logger.error(f"Rate limit triggered, retrying in {wait}s")
            time.sleep(wait)
        except APIError as e:
            logger.error(f"Api Error: {e}")
            raise
    
    raise RuntimeError("Max retries exhausted")

def main():
    with open(INPUT_FILE, 'r', encoding="utf-8") as f:
        raw_text = f.read()
    if not raw_text.strip():
        logger.warning("No text found. Writing fallback summary")
        summary = "No content to summarized :("
    else:
        try:
            summary= summarize_locally(raw_text) if IS_LLM_RUNNING_LOCALLY else summarize(raw_text)
        except Exception as e:
            logger.error(f"Summarization Failed: {e}")
            summary = f"Summarization Failed: {e}"
    
    with open(OUTPUT_FILE,'w', encoding="utf-8") as out:
        out.write(summary)
    logger.info(f"Summary written & saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
