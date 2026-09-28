from datetime import datetime
from pathlib import Path
import re

from fpdf import FPDF
from PIL import Image

from app.config import EXPORTS_DIR


PAGE_WIDTH = 210
PAGE_HEIGHT = 297

LEFT_MARGIN = 15
RIGHT_MARGIN = 15
TOP_MARGIN = 15
BOTTOM_MARGIN = 15

CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN


def _fit_image(pdf, image_path, x, y, max_w, max_h):
    with Image.open(image_path) as img:
        w, h = img.size

    if w <= 0 or h <= 0:
        return

    ratio = min(
        max_w / w,
        max_h / h,
    )

    final_w = w * ratio
    final_h = h * ratio

    pdf.image(
        image_path,
        x=x,
        y=y,
        w=final_w,
        h=final_h,
    )


def _clean_text(value):
    """
    FPDF Helvetica uses a limited character set.
    Replace unsupported Unicode characters so PDF
    generation does not fail.
    """

    if value is None:
        return ""

    text = str(value)

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "\u2022": "-",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Keep basic printable characters.
    text = "".join(
        char
        if ord(char) < 256
        else "?"
        for char in text
    )

    return text.strip()


def _wrap_long_words(text, max_length=45):
    """
    Prevent FPDF from failing when a generated AI response
    contains one extremely long unbroken word/token.
    """

    words = text.split()

    fixed_words = []

    for word in words:
        if len(word) <= max_length:
            fixed_words.append(word)
            continue

        chunks = [
            word[i:i + max_length]
            for i in range(
                0,
                len(word),
                max_length,
            )
        ]

        fixed_words.extend(chunks)

    return " ".join(fixed_words)


def _safe_text(value, limit=None):
    text = _clean_text(value)

    if limit is not None:
        text = text[:limit]

    return _wrap_long_words(text)


def _write_text(
    pdf,
    text,
    font_size=11,
    style="",
    line_height=7,
):
    """
    Write text using a fixed content width.
    This avoids the FPDF 'not enough horizontal space'
    error caused by multi_cell(width=0).
    """

    text = _safe_text(text)

    if not text:
        return

    # Make sure text starts at the left margin.
    pdf.set_x(LEFT_MARGIN)

    pdf.set_font(
        "Helvetica",
        style,
        font_size,
    )

    pdf.multi_cell(
        CONTENT_WIDTH,
        line_height,
        text,
        border=0,
        align="L",
    )

    # Always restore left margin after multi_cell.
    pdf.set_x(LEFT_MARGIN)


def save_pdf(layout):
    filename = (
        f"comic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    output = EXPORTS_DIR / filename

    pdf = FPDF(
        "P",
        "mm",
        "A4",
    )

    pdf.set_margins(
        LEFT_MARGIN,
        TOP_MARGIN,
        RIGHT_MARGIN,
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=BOTTOM_MARGIN,
    )

    for panel in layout:
        pdf.add_page()

        # -------------------------------------------------
        # PANEL TITLE
        # -------------------------------------------------

        title = (
            f"Panel {panel.get('panel_number', '')}: "
            f"{panel.get('title', '')}"
        )

        _write_text(
            pdf,
            title,
            font_size=18,
            style="B",
            line_height=10,
        )

        # Small gap.
        pdf.ln(2)

        # -------------------------------------------------
        # SCENE DESCRIPTION
        # -------------------------------------------------

        scene_description = panel.get(
            "scene_description",
            "",
        )

        _write_text(
            pdf,
            scene_description[:900],
            font_size=10,
            style="I",
            line_height=6,
        )

        pdf.ln(3)

        # -------------------------------------------------
        # IMAGE
        # -------------------------------------------------

        image_path = Path(
            panel.get(
                "image_path",
                "",
            )
        )

        if image_path.exists():
            image_y = pdf.get_y()

            # Keep image inside the printable area.
            max_image_height = 105

            _fit_image(
                pdf,
                str(image_path),
                LEFT_MARGIN,
                image_y,
                CONTENT_WIDTH,
                max_image_height,
            )

            # Move cursor below image.
            pdf.set_y(
                image_y + max_image_height + 3
            )

            # If image pushed us too far down,
            # start a fresh page for the text.
            if pdf.get_y() > 250:
                pdf.add_page()

        # -------------------------------------------------
        # CAPTION
        # -------------------------------------------------

        caption = panel.get(
            "caption",
            "",
        )

        if caption:
            _write_text(
                pdf,
                "Caption: " + caption[:600],
                font_size=11,
                style="B",
                line_height=7,
            )

            pdf.ln(1)

        # -------------------------------------------------
        # NARRATION
        # -------------------------------------------------

        narration = panel.get(
            "narration",
            "",
        )

        if narration:
            _write_text(
                pdf,
                "Narration: " + narration[:1000],
                font_size=11,
                style="",
                line_height=7,
            )

            pdf.ln(1)

        # -------------------------------------------------
        # DIALOGUE
        # -------------------------------------------------

        dialogue = panel.get(
            "dialogue",
            "",
        )

        if dialogue:
            _write_text(
                pdf,
                "Dialogue: " + dialogue[:1000],
                font_size=11,
                style="B",
                line_height=7,
            )

    # -----------------------------------------------------
    # SAVE PDF
    # -----------------------------------------------------

    pdf.output(str(output))

    return str(output)