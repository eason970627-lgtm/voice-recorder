from fastapi import FastAPI
from pydantic import BaseModel
import requests
import io
import speech_recognition as sr

app = FastAPI(
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

class AudioRequest(BaseModel):
    audio_path: str

@app.post("/api/stt")
async def stt_endpoint(data: AudioRequest):
    # To process SpeechRecognition needs WAV, so we retrieve the wav 
    # transcoded version from Cloudinary dynamically.
    download_url = data.audio_path.replace('.webm', '.wav')
    
    try:
        response = requests.get(download_url)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Failed to download audio: {str(e)}", "status": "error"}

    recognizer = sr.Recognizer()
    audio_io = io.BytesIO(response.content)

    try:
        with sr.AudioFile(audio_io) as source:
            audio_data = recognizer.record(source)
            
        print("⏳ 正在傳送至 Google 進行辨識...")
        text = recognizer.recognize_google(audio_data, language="zh-TW")
        print(f"✅ 辨識結果：{text}")
        return {"text": text, "status": "success"}
    
    except sr.UnknownValueError:
        return {"error": "❌ 聽不懂您說的話，請再試一次。", "status": "error"}
    except sr.RequestError:
        return {"error": "❌ 無法連線至語音辨識伺服器，請檢查網路。", "status": "error"}
    except ValueError as e:
        return {"error": f"Audio file formatting error: {str(e)}", "status": "error"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "status": "error"}

@app.get("/hello_world")
async def hello_world():
    return {
        "text": "Hello from FastAPI on Vercel!",
        "status": "success",
        "timestamp": "2026-04-11"
    }
