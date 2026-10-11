import os
import io
import emoji
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from gtts import gTTS

app = FastAPI(docs_url=None, redoc_url=None)

SECRET_KEY = os.getenv("AUDIO_API_SECRET", "xxxxxxxxxxx")

class AudioRequest(BaseModel):
    text: str
    voice: str = "female"

@app.get("/")
def home():
    return {"status": "Secure Server is Running!"}

@app.post("/generate-audio")
def generate_audio(request: AudioRequest, x_api_key: str = Header(None)):
    if x_api_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized Access! You are not KamAbhi's Server.")

    try:
        clean_text = emoji.replace_emoji(request.text, replace='')
        clean_text = clean_text.strip()
        
        if not clean_text:
            clean_text = "Hmm"

        tts = gTTS(text=clean_text, lang='hi', slow=False)
        audio_stream = io.BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0)
        
        return StreamingResponse(audio_stream, media_type="audio/mpeg")
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Server Error")
