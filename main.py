import os
import io
import emoji
import asyncio
import edge_tts
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# FastAPI setup (Docs hidden for security)
app = FastAPI(docs_url=None, redoc_url=None)

# 🔐 API Secret Key (Render me set karein)
SECRET_KEY = os.getenv("AUDIO_API_SECRET", "xxxxxxxxxxx")

class AudioRequest(BaseModel):
    text: str
    voice: str = "female"  # Default 'female'

@app.get("/")
def home():
    # UptimeRobot ke liye Green Signal
    return {"status": "Secure Server is Running!"}

@app.post("/generate-audio")
async def generate_audio(request: AudioRequest, x_api_key: str = Header(None)):
    
    # 🛡️ SECURITY CHECK
    if x_api_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized Access!")

    try:
        # 🧹 EMOJI REMOVER
        clean_text = emoji.replace_emoji(request.text, replace='')
        clean_text = clean_text.strip()
        
        if not clean_text:
            clean_text = "Hmm"

        # 🔊 VOICE SELECTION (Edge TTS)
        # Male ke liye 'Madhur', Female ke liye 'Swara'
        voice_name = "hi-IN-MadhurNeural" if request.voice.lower() == "male" else "hi-IN-SwaraNeural"

        # 🎧 AUDIO GENERATION (RAM me)
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
