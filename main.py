import os
import time
import hashlib
import zipfile
import io
import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from dotenv import load_dotenv
import cloudinary
import cloudinary.api

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
API_KEY    = os.getenv("CLOUDINARY_API_KEY")
API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
FOLDER     = "casamento-fravia"

_cache = {"data": None, "ts": 0}


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


@app.get("/fotos")
def listar_fotos(cursor: str = Query(default=None)):
    global _cache
    agora = time.time()
    if cursor is None and _cache["data"] and agora - _cache["ts"] < 60:
        return _cache["data"]

    kwargs = {
        "type": "upload",
        "prefix": FOLDER,
        "max_results": 50,
        "resource_type": "image",
    }
    if cursor:
        kwargs["next_cursor"] = cursor

    result = cloudinary.api.resources(**kwargs)

    fotos = [
        {
            "url": r["secure_url"],
            "thumb": r["secure_url"].replace("/upload/", "/upload/w_400,c_fill,q_auto,f_auto/"),
        }
        for r in result.get("resources", [])
    ]

    data = {
        "fotos": fotos,
        "next_cursor": result.get("next_cursor"),
    }

    if cursor is None:
        _cache = {"data": data, "ts": agora}

    return data


@app.post("/download-zip")
async def download_zip(body: dict):
    urls = body.get("urls", [])
    if not urls or len(urls) > 50:
        return {"error": "Selecione entre 1 e 50 fotos."}

    zip_buffer = io.BytesIO()

    async with httpx.AsyncClient(timeout=30) as client:
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_STORED) as zf:
            for i, url in enumerate(urls, 1):
                try:
                    res = await client.get(url)
                    ext = url.split(".")[-1].split("?")[0] or "jpg"
                    zf.writestr(f"foto_{i:03d}.{ext}", res.content)
                except Exception:
                    pass

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=fotos-casamento.zip"}
    )


@app.get("/galeria")
def galeria():
    return FileResponse("static/galeria.html")


app.mount("/", StaticFiles(directory="static", html=True), name="static")