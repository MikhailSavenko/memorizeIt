import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

API_KEY = os.getenv("API_KEY")


def transcription_by_wordsapi(word: str) -> dict:
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "wordsapiv1.p.rapidapi.com",
        "Accept": "application/json"
    }
    try:
        response = requests.get(f"https://wordsapiv1.p.rapidapi.com/words/{word}/pronunciation",
                                headers=headers)
        data = response.json()
        pronunciation = data.get("pronunciation", {"all": ""}).get("all")
    except Exception as e:
        logger.error(f"Ошибка при получении транскрипции {e}.")
    finally:
        pronunciation = ""
        return pronunciation

