import json
import re
from typing import Any

import google.generativeai as genai

from app.config import (
    GEMINI_API_KEY,
    GEMINI_OUTLINE_MODEL,
    GEMINI_STORY_MODEL,
    MAX_PANELS,
)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


# ---------------------------------------------------------
# TEMPORARY TEST MODE
# ---------------------------------------------------------
# True  = Gemini API call pannama sample comic use pannum
# False = actual Gemini API use pannum
USE_MOCK_MODE = True


def _require_key():
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to .env.")


def _extract_json(text: str) -> Any:
    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        text.strip(),
        flags=re.I,
    )
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        starts = [
            i
            for i in (
                cleaned.find("["),
                cleaned.find("{"),
            )
            if i >= 0
        ]

        if not starts:
            raise

        start = min(starts)
        end = max(
            cleaned.rfind("]"),
            cleaned.rfind("}"),
        )

        return json.loads(
            cleaned[start:end + 1]
        )


# ---------------------------------------------------------
# MOCK OUTLINE
# ---------------------------------------------------------

def _mock_outline(
    prompt,
    character_name,
    setting,
    tone,
    art_style,
):
    return [
        {
            "panel_number": 1,
            "title": "The Discovery",
            "scene_description": (
                f"{character_name} is exploring a {setting} "
                "when they discover something unusual."
            ),
            "caption": "Something strange catches their attention...",
            "image_prompt": (
                f"{character_name} in a {setting}, "
                f"{art_style} comic style, "
                "discovering a mysterious glowing object, "
                "cinematic composition, detailed background"
            ),
        },
        {
            "panel_number": 2,
            "title": "The Mystery",
            "scene_description": (
                f"{character_name} carefully examines "
                "the mysterious object and notices a hidden clue."
            ),
            "caption": "There was more to it than first appeared.",
            "image_prompt": (
                f"{character_name} examining a mysterious object "
                f"in a {setting}, {art_style} comic style, "
                "dramatic lighting, expressive face"
            ),
        },
        {
            "panel_number": 3,
            "title": "The Secret",
            "scene_description": (
                f"{character_name} follows the clue and discovers "
                "a hidden secret."
            ),
            "caption": "The mystery was finally beginning to make sense.",
            "image_prompt": (
                f"{character_name} discovering a hidden secret "
                f"in a {setting}, {art_style} comic style, "
                "adventure atmosphere, cinematic scene"
            ),
        },
        {
            "panel_number": 4,
            "title": "The Challenge",
            "scene_description": (
                f"{character_name} faces an unexpected challenge "
                "while trying to understand the discovery."
            ),
            "caption": "But discovering the truth was only the beginning.",
            "image_prompt": (
                f"{character_name} facing a mysterious challenge "
                f"in a {setting}, {art_style} comic style, "
                "dynamic action scene, dramatic atmosphere"
            ),
        },
        {
            "panel_number": 5,
            "title": "A New Beginning",
            "scene_description": (
                f"{character_name} solves the mystery and looks "
                "toward a new adventure."
            ),
            "caption": "And so, a new adventure began.",
            "image_prompt": (
                f"{character_name} standing confidently in a {setting}, "
                f"{art_style} comic style, "
                "hopeful ending, cinematic composition"
            ),
        },
    ]


# ---------------------------------------------------------
# MOCK STORY
# ---------------------------------------------------------

def _mock_story(
    outline,
    character_name,
    tone,
):
    story = []

    dialogues = [
        "What is that?",
        "This can't be a coincidence.",
        "I think I've found the secret!",
        "I have to figure this out.",
        "This is only the beginning!",
    ]

    narrations = [
        "A strange discovery begins an unexpected adventure.",
        "A hidden clue reveals that something bigger is happening.",
        "The mystery slowly starts to unfold.",
        "A difficult challenge stands between the hero and the truth.",
        "The mystery is solved, but a new adventure awaits.",
    ]

    for index, panel in enumerate(outline):
        item = dict(panel)

        item["narration"] = narrations[index]
        item["dialogue"] = dialogues[index]

        story.append(item)

    return story


# ---------------------------------------------------------
# GEMINI OUTLINE
# ---------------------------------------------------------

def generate_outline(
    prompt,
    character_name,
    setting,
    tone,
    art_style,
):
    # Temporary bypass while Gemini quota is exhausted.
    if USE_MOCK_MODE:
        return _mock_outline(
            prompt,
            character_name,
            setting,
            tone,
            art_style,
        )

    _require_key()

    instruction = f"""
Create a structured five-panel comic outline.

Story prompt: {prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Return ONLY valid JSON: an array with exactly five objects.

Each object must contain:
panel_number, title, scene_description, caption, image_prompt.

Keep the same main character and visual identity across all panels.
"""

    response = genai.GenerativeModel(
        GEMINI_OUTLINE_MODEL
    ).generate_content(instruction)

    data = _extract_json(response.text)

    if not isinstance(data, list) or len(data) != MAX_PANELS:
        raise ValueError(
            f"Gemini outline must contain exactly {MAX_PANELS} panels."
        )

    return data


# ---------------------------------------------------------
# GEMINI STORY
# ---------------------------------------------------------

def generate_story(
    outline,
    character_name,
    tone,
):
    # Temporary bypass while Gemini quota is exhausted.
    if USE_MOCK_MODE:
        return _mock_story(
            outline,
            character_name,
            tone,
        )

    _require_key()

    instruction = f"""
Expand this five-panel comic outline into a coherent story.

Main character: {character_name}
Tone: {tone}

Outline:
{json.dumps(
    outline,
    ensure_ascii=False,
    indent=2,
)}

Return ONLY valid JSON: an array with exactly five objects.

For every panel return:
panel_number, title, scene_description, caption,
narration, dialogue, image_prompt.

Dialogue should be short and comic-friendly.
Narration should be concise enough for a comic panel.
Preserve panel order and visual continuity.
"""

    response = genai.GenerativeModel(
        GEMINI_STORY_MODEL
    ).generate_content(instruction)

    data = _extract_json(response.text)

    if not isinstance(data, list) or len(data) != len(outline):
        raise ValueError(
            "Gemini story response did not contain five panels."
        )

    return data