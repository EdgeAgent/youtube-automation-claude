"""Thumbnail builder — a REAL frame of your own video, treated boldly.

Rules (see docs/packaging-playbook.md):

- The base image is a real frame extracted from the video itself with
  ffmpeg. Never AI-generated key art, never stock — viewers can smell it,
  and the frame is also a promise the video has to keep.
- Treatment is grade + type only: a saturated, high-contrast grade and
  big display text with a heavy outline. The frame stays truthful.
- Text lives inside the safe zone (a margin on every edge) and must stay
  legible when the thumbnail is shrunk to feed size (~320px wide).

Fonts: uses Pricedown if it is installed (the classic display face for
gaming niches), otherwise falls back to a bundled bold sans (DejaVu Sans
Bold on most Linux systems, Arial Bold on Windows/macOS paths below).
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

THUMB_W, THUMB_H = 1280, 720
SAFE_MARGIN = 48  # px on every edge — text never crosses this line
PREVIEW_W = 320  # feed-size preview used for the legibility check
MIN_PREVIEW_TEXT_PX = 14  # smallest legible text height at preview size

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/pricedown/PricedownBl-Regular.ttf",
    "/usr/share/fonts/TTF/PricedownBl-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]


def find_font() -> str | None:
    """Return the first usable display font on this machine, or None."""
    for candidate in _FONT_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    return None


def extract_frame(video_path: str | Path, timestamp_s: float, out_path: str | Path) -> Path:
    """Extract one real frame from a video with ffmpeg."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(timestamp_s), "-i", str(video_path),
         "-frames:v", "1", "-q:v", "2", str(out)],
        check=True, capture_output=True,
    )
    return out


@dataclass
class TextLayout:
    lines: list
    font_size: int
    box: tuple  # (x0, y0, x1, y1) of the whole text block
    in_safe_zone: bool
    preview_text_px: float
    legible_at_preview: bool


def plan_text_layout(lines: list[str], font_size: int, anchor: str = "bottom-left",
                     width: int = THUMB_W, height: int = THUMB_H,
                     margin: int = SAFE_MARGIN, line_spacing: float = 1.08) -> TextLayout:
    """Compute where the text block lands and whether it passes the checks.

    Uses a conservative per-character width estimate (0.62 x font size for
    bold display faces) so the layout logic is testable without a font
    file. ``build_thumbnail`` re-measures with the real font and shrinks
    the text until this plan passes.
    """
    est_char_w = 0.62 * font_size
    block_w = max((len(line) * est_char_w for line in lines), default=0)
    block_h = len(lines) * font_size * line_spacing

    if anchor == "bottom-left":
        x0, y1 = margin, height - margin
        box = (x0, y1 - block_h, x0 + block_w, y1)
    elif anchor == "top-left":
        box = (margin, margin, margin + block_w, margin + block_h)
    else:
        raise ValueError(f"Unknown anchor: {anchor}")

    in_safe = (
        box[0] >= margin and box[1] >= margin
        and box[2] <= width - margin and box[3] <= height - margin
    )
    preview_px = font_size * (PREVIEW_W / width)
    return TextLayout(
        lines=list(lines), font_size=font_size, box=box,
        in_safe_zone=in_safe, preview_text_px=preview_px,
        legible_at_preview=preview_px >= MIN_PREVIEW_TEXT_PX,
    )


def fit_text_layout(lines: list[str], start_size: int = 120, min_size: int = 40,
                    anchor: str = "bottom-left") -> TextLayout:
    """Shrink the font until the text block fits the safe zone legibly."""
    size = start_size
    while size >= min_size:
        layout = plan_text_layout(lines, size, anchor=anchor)
        if layout.in_safe_zone and layout.legible_at_preview:
            return layout
        size -= 4
    return plan_text_layout(lines, min_size, anchor=anchor)


@dataclass
class ThumbnailResult:
    out_path: str
    layout: TextLayout
    font_used: str
    warnings: list = field(default_factory=list)


def build_thumbnail(frame_path: str | Path, text_lines: list[str], out_path: str | Path,
                    anchor: str = "bottom-left") -> ThumbnailResult:
    """Grade a real frame and burn in bold outlined text. Returns checks."""
    from PIL import Image, ImageDraw, ImageEnhance, ImageFont

    img = Image.open(frame_path).convert("RGB")
    # Cover-crop to 1280x720 without distorting the frame.
    scale = max(THUMB_W / img.width, THUMB_H / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left = (img.width - THUMB_W) // 2
    top = (img.height - THUMB_H) // 2
    img = img.crop((left, top, left + THUMB_W, top + THUMB_H))

    # The grade: saturation + contrast + a touch of sharpness.
    img = ImageEnhance.Color(img).enhance(1.35)
    img = ImageEnhance.Contrast(img).enhance(1.15)
    img = ImageEnhance.Sharpness(img).enhance(1.4)

    font_path = find_font()
    warnings = []
    if font_path is None:
        warnings.append("No display font found — install Pricedown or DejaVu Sans Bold.")

    layout = fit_text_layout(text_lines, anchor=anchor)
    size = layout.font_size
    draw = ImageDraw.Draw(img)
    while size >= 40:
        font = ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()
        widths = [draw.textlength(line, font=font) for line in text_lines]
        block_w = max(widths, default=0)
        line_h = size * 1.08
        block_h = line_h * len(text_lines)
        if anchor == "bottom-left":
            x0, y0 = SAFE_MARGIN, THUMB_H - SAFE_MARGIN - block_h
        else:
            x0, y0 = SAFE_MARGIN, SAFE_MARGIN
        if x0 + block_w <= THUMB_W - SAFE_MARGIN and block_w > 0:
            break
        size -= 4
    else:
        warnings.append("Text did not fit the safe zone even at minimum size.")

    stroke = max(4, size // 14)
    y = y0
    for line in text_lines:
        draw.text((x0, y), line, font=font, fill=(255, 255, 255),
                  stroke_width=stroke, stroke_fill=(0, 0, 0))
        y += size * 1.08

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, quality=92)

    final_layout = fit_text_layout(text_lines, start_size=size, anchor=anchor)
    return ThumbnailResult(
        out_path=str(out), layout=final_layout,
        font_used=font_path or "PIL default", warnings=warnings,
    )
