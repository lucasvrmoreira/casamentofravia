import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    uploaded = []

    for file in files:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail=f"'{file.filename}' não é uma imagem.")

        content = await file.read()

        result = cloudinary.uploader.upload(
            content,
            folder="casamento-fravia",
            resource_type="image",
        )

        uploaded.append({"url": result["secure_url"], "original": file.filename})

    return {"success": True, "uploaded": uploaded, "total": len(uploaded)}


app.mount("/", StaticFiles(directory="static", html=True), name="static")