from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from app.ai_core.gemini_generator import generate_outline, generate_story
from app.ai_core.image_generator import generate_image
from app.config import EXPORTS_DIR, TEMPLATES_DIR
from app.schemas import ComicRequest, ImageTestRequest
from app.utils.exporters import save_pdf
from app.utils.layout_builder import build_comic_layout


router = APIRouter()

templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)


def _public_image_path(path):
    """
    Convert a local static file path into a browser URL.

    Example:
    C:/.../ComicCraft/static/panels/panel_1.png
    ->
    /static/panels/panel_1.png
    """

    path_str = str(Path(path).as_posix())

    if "static/" in path_str:
        return "/static/" + path_str.split(
            "static/",
            1,
        )[1]

    return "/" + path_str.lstrip("/")


def create_comic(data):
    # -----------------------------------------------------
    # 1. CREATE COMIC OUTLINE
    # -----------------------------------------------------

    outline = generate_outline(
        data.prompt,
        data.character_name,
        data.setting,
        data.tone,
        data.art_style,
    )

    # -----------------------------------------------------
    # 2. EXPAND INTO STORY
    # -----------------------------------------------------

    story = generate_story(
        outline,
        data.character_name,
        data.tone,
    )

    # -----------------------------------------------------
    # 3. GENERATE PANEL IMAGES
    # -----------------------------------------------------

    image_paths = [
        generate_image(
            p["image_prompt"],
            int(p["panel_number"]),
        )
        for p in story
    ]

    # -----------------------------------------------------
    # 4. BUILD COMIC LAYOUT
    # -----------------------------------------------------

    layout = build_comic_layout(
        story,
        image_paths,
    )

    # -----------------------------------------------------
    # 5. CREATE PDF
    # -----------------------------------------------------

    pdf_path = save_pdf(layout)

    # -----------------------------------------------------
    # 6. CREATE BROWSER IMAGE URLS
    # -----------------------------------------------------

    for panel in layout:
        panel["image_url"] = _public_image_path(
            panel["image_path"]
        )

    # -----------------------------------------------------
    # 7. RETURN COMPLETE COMIC DATA
    # -----------------------------------------------------

    return {
        "prompt": data.prompt,
        "character_name": data.character_name,
        "setting": data.setting,
        "tone": data.tone,
        "art_style": data.art_style,
        "panels": layout,
        "pdf_url": "/export/" + Path(pdf_path).name,
    }


# =========================================================
# HOME
# =========================================================

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
        },
    )


# =========================================================
# GENERATE COMIC FROM FORM
# =========================================================

@router.post("/generate")
async def generate_form(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form("Alex"),
    setting: str = Form("forest"),
    tone: str = Form("dramatic"),
    art_style: str = Form("comic book"),
):
    form = {
        "prompt": prompt,
        "character_name": character_name,
        "setting": setting,
        "tone": tone,
        "art_style": art_style,
    }

    try:
        comic = create_comic(
            ComicRequest(**form)
        )

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "comic": comic,
            },
        )

    except Exception as exc:
        import traceback

        traceback.print_exc()

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(exc),
                "form": form,
            },
            status_code=500,
        )


# =========================================================
# GENERATE COMIC JSON API
# =========================================================

@router.post("/generate-comic/json")
async def generate_json(data: ComicRequest):
    try:
        return create_comic(data)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# TEST IMAGE
# =========================================================

@router.post("/test-image")
async def test_image(data: ImageTestRequest):
    try:
        path = generate_image(
            data.prompt,
            0,
        )

        return {
            "image_url": _public_image_path(path),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# PDF EXPORT
# =========================================================

@router.get("/export/{filename}")
async def export_file(filename: str):
    safe_name = Path(filename).name

    file_path = EXPORTS_DIR / safe_name

    if (
        not file_path.exists()
        or file_path.suffix.lower() != ".pdf"
    ):
        raise HTTPException(
            status_code=404,
            detail="PDF not found.",
        )

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=safe_name,
    )


# =========================================================
# EXPORT SUCCESS
# =========================================================

@router.get("/export-success")
async def export_success(request: Request):
    return templates.TemplateResponse(
        "export_success.html",
        {
            "request": request,
        },
    )