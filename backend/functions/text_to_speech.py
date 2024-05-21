import requests
import logging
from decouple import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ELEVEN_LABS_API_KEY = config("ELEVEN_LABS_API_KEY")

def convert_text_to_speech(message, voice_id="21m00Tcm4TlvDq8ikWAM"):  # Default to Rachel's voice
    body = {
        "text": message,
        "voice_settings": {
            "stability": 0,
            "similarity_boost": 0
        }
    }

    # Construct request headers and URL
    headers = {
        "xi-api-key": ELEVEN_LABS_API_KEY,
        "Content-Type": "application/json",
        "accept": "audio/mpeg"
    }
    endpoint = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    try:
        response = requests.post(endpoint, json=body, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            logger.error(f"Failed to generate audio: Status code {response.status_code}, Response {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in sending request to Eleven Labs API: {e}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None
