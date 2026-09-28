from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont

from app.config import (
    HF_API_KEY,
    HF_IMAGE_MODEL,
    IMAGE_PROVIDER,
    PANELS_DIR,
    USE_LOCAL_DIFFUSION,
)


def _safe_name(value):
    return (
        re.sub(
            r"[^a-zA-Z0-9_-]+",
            "_",
            value,
        )
        .strip("_")[:60]
        or "panel"
    )


def _placeholder(prompt, output):
    """
    Creates a simple local image so the complete
    ComicCraft pipeline can be tested even when
    Hugging Face is unavailable.
    """

    image = Image.new(
        "RGB",
        (1024, 768),
        "white",
    )

    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (18, 18, 1006, 750),
        outline="black",
        width=8,
    )

    draw.text(
        (50, 50),
        "ComicCraft",
        fill="black",
    )

    draw.text(
        (50, 100),
        "AI image placeholder",
        fill="black",
    )

    # Wrap long prompt text.
    words = prompt[:700].split()
    lines = []
    current = ""

    for word in words:
        test = f"{current} {word}".strip()

        if len(test) > 65:
            lines.append(current)
            current = word
        else:
            current = test

    if current:
        lines.append(current)

    y = 160

    for line in lines:
        draw.text(
            (50, y),
            line,
            fill="black",
        )
        y += 28

        if y > 700:
            break

    image.save(
        output,
        "PNG",
    )

    return str(output)


def _huggingface(prompt, output):
    if not HF_API_KEY:
        raise RuntimeError(
            "HF_API_KEY is missing for Hugging Face image generation."
        )

    from huggingface_hub import InferenceClient

    client = InferenceClient(
        api_key=HF_API_KEY
    )

    image = client.text_to_image(
        prompt,
        model=HF_IMAGE_MODEL,
    )

    image.save(output)

    return str(output)


def _diffusers(prompt, output):
    import torch
    from diffusers import StableDiffusionPipeline

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    dtype = (
        torch.float16
        if device == "cuda"
        else torch.float32
    )

    pipe = StableDiffusionPipeline.from_pretrained(
        HF_IMAGE_MODEL,
        torch_dtype=dtype,
    )

    pipe = pipe.to(device)

    result = pipe(
        prompt,
        num_inference_steps=25,
        guidance_scale=7.0,
    )

    result.images[0].save(output)

    return str(output)


def generate_image(prompt, panel_number):
    output = (
        PANELS_DIR
        / f"panel_{panel_number}_{_safe_name(prompt)}.png"
    )

    enhanced = (
        "comic panel illustration, "
        "expressive characters, "
        "clean line art, "
        "cinematic lighting, "
        "detailed background, "
        "consistent character design, "
        + prompt
    )

    # -----------------------------------------------------
    # HUGGING FACE
    # -----------------------------------------------------

    if IMAGE_PROVIDER == "huggingface":
        try:
            return _huggingface(
                enhanced,
                output,
            )

        except Exception as exc:
            print(
                "Hugging Face image generation failed:"
            )
            print(exc)

            # If local diffusion is enabled,
            # try it next.
            if USE_LOCAL_DIFFUSION:
                try:
                    return _diffusers(
                        enhanced,
                        output,
                    )
                except Exception as diffusers_error:
                    print(
                        "Local Diffusers generation failed:"
                    )
                    print(diffusers_error)

            # IMPORTANT:
            # Don't crash the whole comic generation.
            # Use a local placeholder instead.
            print(
                "Using local placeholder image instead."
            )

            return _placeholder(
                prompt,
                output,
            )

    # -----------------------------------------------------
    # LOCAL DIFFUSERS
    # -----------------------------------------------------

    if (
        IMAGE_PROVIDER == "diffusers"
        or USE_LOCAL_DIFFUSION
    ):
        try:
            return _diffusers(
                enhanced,
                output,
            )
        except Exception as exc:
            print(
                "Diffusers image generation failed:"
            )
            print(exc)

            return _placeholder(
                prompt,
                output,
            )

    # -----------------------------------------------------
    # DEFAULT PLACEHOLDER
    # -----------------------------------------------------

    return _placeholder(
        prompt,
        output,
    )