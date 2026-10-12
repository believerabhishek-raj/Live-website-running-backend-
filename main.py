import os
import io
import emoji
import asyncio
import edge_tts
from gtts import gTTS
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI(docs_url=None, redoc_url=None)

SECRET_KEY = os.getenv("AUDIO_API_SECRET", "xxxxxxxxxxxxx123")

class AudioRequest(BaseModel):
    text: str
    voice: str = "hi-IN-SwaraNeural"  # Default Voice

@app.get("/")
def home():
    return {"status": "Secure Server is Running!"}

@app.post("/generate-audio")
async def generate_audio(request: AudioRequest, x_api_key: str = Header(None)):
    if x_api_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized Access!")

    try:
        # 1. Text Cleaning: Emoji aur Markdown (*, _, #) hatao
        clean_text = emoji.replace_emoji(request.text, replace='')
        clean_text = clean_text.replace("*", "").replace("_", "").replace("`", "").replace("#", "")
        clean_text = clean_text.strip()
        
        if not clean_text:
            clean_text = "Hmm"

        # 2. Main TTS: Edge-TTS Try karo (Real Human Voice)
        try:
            communicate = edge_tts.Communicate(clean_text, request.voice, rate="+5%", pitch="+2Hz")
            audio_stream = io.BytesIO()
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_stream.write(chunk["data"])
                    
            if audio_stream.tell() > 0:
                audio_stream.seek(0)
                return StreamingResponse(audio_stream, media_type="audio/mpeg")
            else:
                raise ValueError("Edge-TTS returned empty audio")

        # 3. Fallback: Agar Edge-TTS 403/500 error de, toh gTTS chalega
        except Exception as edge_err:
            print(f"⚠️ Edge-TTS Failed ({edge_err}), switching to gTTS fallback...")
            
            # gTTS default Hindi ('hi') voice female hoti hai aur kaafi natural lagti hai
            tts = gTTS(text=clean_text, lang='hi', slow=False)
            fallback_stream = io.BytesIO()
            tts.write_to_fp(fallback_stream)
            fallback_stream.seek(0)
            
            return StreamingResponse(fallback_stream, media_type="audio/mpeg")
    
    except Exception as e:
        print(f"❌ Server Error: {e}")
        raise HTTPException(status_code=500, detail="Server Error")
