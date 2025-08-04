from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import getpass
import os

# --- This imports from story_engine.py, which is in the same folder ---
from story_engine import StoryEngine, StoryProfile, Character, StoryGenre, StoryTone, StoryLength

# --- Basic Configuration ---
app = FastAPI(
    title="Magical Story Creator API",
    description="The API for generating therapeutic children's stories.",
    version="1.0.0"
)

# --- Initialize Your Story Engine ---
API_KEY = os.environ.get("GEMINI_API_KEY") 
if not API_KEY:
    try:
        API_KEY = getpass.getpass("🔑 Enter your Google AI API Key (hidden): ")
    except Exception:
        print("API Key not found. Please set the GEMINI_API_KEY environment variable.")
        API_KEY = "MISSING_API_KEY"

try:
    story_engine = StoryEngine(api_key=API_KEY)
except Exception as e:
    raise RuntimeError(f"Failed to initialize StoryEngine. Check your API key. Error: {e}") from e


# --- Define the data structures for our API ---
class StoryRequest(BaseModel):
    character_name: str
    character_age: int
    character_gender: str # <-- Add this line
    character_personality: str = "curious and kind"
    character_loves: str = "exploring new places"
    challenge: str = "learning to be brave"
    genre: StoryGenre = StoryGenre.FANTASY
    tone: StoryTone = StoryTone.GENTLE
    length: StoryLength = StoryLength.SHORT


# --- Create the API Endpoint ---
from fastapi import Body

@app.post("/generate_story")
def generate_story(request: StoryRequest = Body(...)):
    try:
        # 1. Create a Character object from the request data
        main_character = Character(
            name=request.character_name,
            age=request.character_age,
            gender=request.character_gender,
            personality=request.character_personality,
            favorites=request.character_loves
        )

        profile = StoryProfile(
            characters=[main_character],
            genre=request.genre,
            tone=request.tone,
            length=request.length,
            challenge=request.challenge,
            magic="friendship and courage"
        )

        story_output = story_engine.generate_story(profile)
        if not story_output or not story_output.text:
            raise HTTPException(status_code=500, detail="Story generation failed.")

        return {
            "title": story_output.title,
            "text": story_output.text,
            "wisdom_gem": story_output.wisdom_gem,
            "key_items": story_output.key_items
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")