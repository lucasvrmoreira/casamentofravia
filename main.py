import os
import time
import hashlib
import hmac
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import cloudinary

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
API_KEY = os.getenv("CLOUDINARY_API_KEY")
API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
FOLDER = "casamento-fravia"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/sign")
def sign():
    timestamp = int(time.time())
    params = f"folder={FOLDER}&timestamp={timestamp}"
    signature = hmac.new(
        API_SECRET.encode(),
        params.encode(),
        hashlib.sha1
    ).hexdigest()

    return {
        "timestamp": timestamp,
        "signature": signature,
        "api_key": API_KEY,
        "cloud_name": CLOUD_NAME,
        "folder": FOLDER,
    }


app.mount("/", StaticFiles(directory="static", html=True), name="static")