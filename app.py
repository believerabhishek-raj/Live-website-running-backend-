import io
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from gtts import gTTS

# FastAPI ऐप बनाना
app = FastAPI()

# Request का स्ट्रक्चर (Server 1 से क्या डेटा आएगा)
class AudioRequest(BaseModel):
    text: str
    voice: str = "female"  # डिफ़ॉल्ट रूप से female

@app.get("/")
def home():
    return {"status": "Audio API is Live and Running 24/7! 🚀"}

@app.post("/generate-audio")
def generate_audio(request: AudioRequest):
    try:
        # gTTS का उपयोग करके टेक्स्ट को ऑडियो में बदलना
        # 'hi' का मतलब है कि यह हिंदी और हिंग्लिश दोनों को एकदम साफ़ और नेचुरल बोलेगा
        tts = gTTS(text=request.text, lang='hi', slow=False)
        
        # ऑडियो को हार्ड डिस्क पर सेव करने के बजाय सीधे RAM (Bytes) में रखना
        audio_stream = io.BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0)
        
        # Audio bytes को सीधे Server 1 को वापस भेजना
        return StreamingResponse(audio_stream, media_type="audio/mpeg")
    
    except Exception as e:
        print(f"Error generating audio: {e}")
        raise HTTPException(status_code=500, detail="Audio generation failed")
