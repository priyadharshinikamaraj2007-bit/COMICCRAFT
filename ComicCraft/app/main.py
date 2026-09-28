from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import STATIC_DIR
from app.routes import router

app = FastAPI(
    title="ComicCraft",
    description="AI Comic Story Creator using Gemini and Stable Diffusion",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ComicCraft"}
