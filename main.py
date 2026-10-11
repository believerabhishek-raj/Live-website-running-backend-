import os
import io
import emoji
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from gtts import gTTS

# docs_url=None और redoc_url=None से कोई भी आपके API का स्ट्रक्चर/डिटेल्स नहीं देख पाएगा (Zero Data Leak)
app = FastAPI(docs_url=None, redoc_url=None)

# 🔐 API Secret Key (इसे हम Render के Environment Variable में डालेंगे)
SECRET_KEY = os.getenv("AUDIO_API_SECRET", "xxxxxxxxxxxxx")

class AudioRequest(BaseModel):
    text: str
    voice: str = "female"

@app.get("/")
def home():
    return {"status": "Secure Server is Running!"}

@app.post("/generate-audio")
def generate_audio(request: AudioRequest, x_api_key: str = Header(None)):
    
    # 🛡️ SECURITY CHECK: अगर पासवर्ड मैच नहीं हुआ, तो तुरंत बाहर निकालो (Access Denied)
    if x_api_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized Access! You are not KamAbhi's Server.")

    try:
        # 🧹 EMOJI REMOVER: टेक्स्ट से सारे इमोजी और फालतू सिंबल्स साफ़ करना
        clean_text = emoji.replace_emoji(request.text, replace='')
        clean_text = clean_text.strip()
        
        # अगर यूज़र ने सिर्फ इमोजी भेजे थे (जैसे "❤️❤️") तो टेक्स्ट खाली हो जाएगा। 
        # ऐसे में क्रैश से बचने के लिए बॉट सिर्फ "Hmm" बोलेगा।
        if not clean_text:
            clean_text = "Hmm"

        # 🔊 AUDIO GENERATION
        tts = gTTS(text=clean_text, lang='hi', slow=False)
        audio_stream = io.BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0)
        
        return StreamingResponse(audio_stream, media_type="audio/mpeg")
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Server Error")
