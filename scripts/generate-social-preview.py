#!/usr/bin/env python3
"""
Generate the 1200x630 GitHub social preview image for this repo.

Run from the repo root:
    python3 scripts/generate-social-preview.py

Writes:
    .github/social-preview.png

Upload via GitHub: Settings -> General -> Social preview -> "Edit" -> upload the PNG.
(No public API for this — must be uploaded through the web UI.)
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG_TOP = (13, 17, 23)
BG_BOTTOM = (22, 27, 34)
ACCENT = (94, 106, 210)
WHITE = (229, 231, 235)
MUTED = (139, 148, 158)
DIM = (48, 54, 61)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def gradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h), top)
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def main():
    img = gradient(W, H, BG_TOP, BG_BOTTOM)
    d = ImageDraw.Draw(img)

    for x in range(60, W, 40):
        for y in range(60, H, 40):
            d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=DIM)

    d.rectangle((0, 0, 8, H), fill=ACCENT)

    label = ImageFont.truetype(FONT_MONO, 22)
    d.text((80, 80), "AGENT MEMORY ARCHITECTURE", font=label, fill=MUTED)

    layers_font = ImageFont.truetype(FONT_BOLD, 148)
    d.text((80, 130), "6 Layers.", font=layers_font, fill=WHITE)

    tagline_font = ImageFont.truetype(FONT_REG, 38)
    d.text(
        (80, 320),
        "From CLAUDE.md to cognitive memory.",
        font=tagline_font,
        fill=WHITE,
    )
    d.text(
        (80, 370),
        "Model-agnostic, production-backed, opinionated.",
        font=tagline_font,
        fill=MUTED,
    )

    layer_y = 470
    for i in range(6):
        cx = 80 + i * 50
        d.ellipse((cx, layer_y, cx + 32, layer_y + 32), fill=ACCENT)
        num_font = ImageFont.truetype(FONT_BOLD, 20)
        bbox = d.textbbox((0, 0), str(i + 1), font=num_font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text(
            (cx + 16 - tw // 2, layer_y + 16 - th // 2 - 2),
            str(i + 1),
            font=num_font,
            fill=WHITE,
        )

    footer_font = ImageFont.truetype(FONT_MONO, 22)
    d.text(
        (80, H - 70),
        "github.com/futhgar/agent-memory-architecture   ·   @jmrlad   ·   MIT",
        font=footer_font,
        fill=MUTED,
    )

    out = Path(__file__).resolve().parent.parent / ".github" / "social-preview.png"
    out.parent.mkdir(exist_ok=True)
    img.save(out, "PNG", optimize=True)
    print(f"Wrote {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
