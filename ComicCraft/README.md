# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI + Jinja2 web application based on the supplied project specification. It accepts a story prompt, character, setting, tone, and art style; generates a 5-panel outline and story with Gemini; creates panel illustrations with Hugging Face Stable Diffusion (or local Diffusers); previews the comic; and exports it as PDF.

## Structure

```text
ComicCraft/
├── app/
│   ├── main.py
│   ├── routes.py
│   ├── config.py
│   ├── schemas.py
│   ├── ai_core/
│   │   ├── gemini_generator.py
│   │   └── image_generator.py
│   └── utils/
│       ├── layout_builder.py
│       └── exporters.py
├── templates/
├── static/
├── tests/
├── requirements.txt
└── .env.example
```

## Windows / VS Code

```powershell
py -3.11 -m venv .venv
.venv\Scriptsctivate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 and http://127.0.0.1:8000/docs.

Put your Gemini API key in `.env`. Put an HF token there too when using hosted image generation.

## API

- `POST /generate` — HTML form generation.
- `POST /generate-comic/json` — JSON API.
- `POST /test-image` — single image test.
- `GET /export/{filename}` — PDF download.
- `GET /export-success` — export confirmation.
- `GET /health` — health check.

## Test

```powershell
pytest
```

The tests do not call Gemini or Hugging Face.

## Image generation

The default provider is Hugging Face hosted inference. For local Diffusers:

```env
IMAGE_PROVIDER=diffusers
USE_LOCAL_DIFFUSION=true
```

Local Stable Diffusion is GPU/VRAM intensive.

The supplied document names Gemini 1.5 Flash, Gemini 1.5 Pro and Stable Diffusion v1.5; these are configurable because provider model availability can change.
