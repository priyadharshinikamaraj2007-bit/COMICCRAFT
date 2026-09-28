from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
MAX_PANELS = int(os.getenv("MAX_PANELS", "5"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_OUTLINE_MODEL = os.getenv("GEMINI_OUTLINE_MODEL", "gemini-1.5-flash")
GEMINI_STORY_MODEL = os.getenv("GEMINI_STORY_MODEL", "gemini-1.5-pro")

HF_API_KEY = os.getenv("HF_API_KEY", "")
HF_IMAGE_MODEL = os.getenv("HF_IMAGE_MODEL", "runwayml/stable-diffusion-v1-5")
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "huggingface").lower()
USE_LOCAL_DIFFUSION = os.getenv("USE_LOCAL_DIFFUSION", "false").lower() == "true"

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
PANELS_DIR = STATIC_DIR / "panels"
EXPORTS_DIR = STATIC_DIR / "exports"
PANELS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
