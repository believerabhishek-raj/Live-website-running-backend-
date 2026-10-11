import os
import io
import emoji
import asyncio
import edge_tts
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI(docs_url=None, redoc_url=None)

SECRET_KEY = os.getenv("AUDIO_API_SECRET", "xxxxxxxxxxx123")

class AudioRequest(BaseModel):
    text: str

@app.get("/")
def home():
    return {"status": "Secure Server is Running!"}

@app.post("/generate-audio")
async def generate_audio(request: AudioRequest, x_api_key: str = Header(None)):
    if x_api_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized Access!")

    try:
        clean_text = emoji.replace_emoji(request.text, replace='')
        clean_text = clean_text.strip()
        
        if not clean_text:
            clean_text = "Hmm"

        # 🔊 100% LOCKED TO FEMALE VOICE (Swara - Best Indian Female Voice)
        voice_name = "hi-IN-SwaraNeural"

        communicate = edge_tts.Communicate(clean_text, voice_name)
        audio_stream = io.BytesIO()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])
                
        audio_stream.seek(0)
        return StreamingResponse(audio_stream, media_type="audio/mpeg")
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Server Error")
