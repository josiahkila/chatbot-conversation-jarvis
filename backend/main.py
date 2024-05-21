import sys
import os
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
from openai import OpenAI, OpenAIError

# Add the config directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'config')))

from config.settings import DATABASE_URL, OPEN_AI_ORG, OPEN_AI_KEY
from functions.database import get_recent_messages, store_messages, reset_messages
from functions.text_to_speech import convert_text_to_speech
from functions.openai_requests import get_chat_response

# Ensure the current directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log the loaded settings for verification
logger.info(f"Loaded settings: {DATABASE_URL}, {OPEN_AI_ORG}, {OPEN_AI_KEY}")

# Initialize OpenAI client with your API key
try:
    openai = OpenAI(api_key=OPEN_AI_KEY)
    logger.info("OpenAI client initialized successfully.")
except OpenAIError as e:
    logger.error(f"Error initializing OpenAI client: {e}")
    raise

# Initiate App
app = FastAPI()

# CORS - Origins
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "http://localhost:3000",
]

# CORS - Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the API"}

# Check health
@app.get("/health")
async def check_health():
    return {"response": "healthy"}

# Reset Conversation
@app.get("/reset")
async def reset_conversation():
    reset_messages()
    return {"response": "conversation reset"}

# Get audio transcription
@app.get("/post-audio-get/")
async def get_audio():
    audio_file_path = "voice.mp3"  # Update this path if necessary
    with open(audio_file_path, "rb") as audio_file:
        response = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
    transcription = response.text
    logger.info(f"Transcription: {transcription}")
    return {"transcription": transcription}

# Post bot response
@app.post("/post-audio/")
async def post_audio(file: UploadFile = File(...)):
    try:
        # Save the file temporarily
        file_path = "voice.mp3"
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        
        with open(file_path, "rb") as audio_input:
            # Decode audio
            response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_input,
            )
            message_decoded = response.text
        
        if not message_decoded:
            raise HTTPException(status_code=400, detail="Failed to decode audio")
        logger.info("Decoded Message: %s", message_decoded)

        # Get chat response
        chat_response = get_chat_response(message_decoded)
        if not chat_response:
            logger.error("Failed to get chat response: %s", chat_response)
            raise HTTPException(status_code=400, detail="Failed to get chat response")
        logger.info("Chat Response: %s", chat_response)

        # Store messages
        store_messages(message_decoded, chat_response)

        # Convert chat response to audio
        audio_output = convert_text_to_speech(chat_response)
        if not audio_output:
            raise HTTPException(status_code=400, detail="Failed to generate audio output")
        logger.info("Audio Output: %s", audio_output)

        # Create a generator that yields chunks of data
        def iterfile():
            yield audio_output

        # Use for Post: Return output audio
        return StreamingResponse(iterfile(), media_type="application/octet-stream")

    except Exception as e:
        logger.error("Error processing audio: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
