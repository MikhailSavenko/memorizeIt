import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

def transcription_by_wordsapi(word: str) -> dict:
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "wordsapiv1.p.rapidapi.com",
        "Accept": "application/json"
    }

    
    response = requests.get(f"https://wordsapiv1.p.rapidapi.com/words/{word}/pronunciation",
                            headers=headers)
    data = response.json()
    pronunciation = data.get("pronunciation").get("all")
    
    return pronunciation


transcription_by_wordsapi("plain")