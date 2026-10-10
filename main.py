import os
import time
import hashlib
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
    params_to_sign = f"folder={FOLDER}&timestamp={timestamp}{API_SECRET}"
    signature = hashlib.sha1(params_to_sign.encode()).hexdigest()

    return {
        "timestamp": timestamp,
        "signature": signature,
        "api_key": API_KEY,
        "cloud_name": CLOUD_NAME,
        "folder": FOLDER,
    }


app.mount("/", StaticFiles(directory="static", html=True), name="static")