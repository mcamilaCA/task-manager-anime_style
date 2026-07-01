"""Regenerate app/assets/icon/AppIcon.icns: a wax-seal-style icon in the
app's own palette, lettermark set in the bundled Shippori Mincho font.

Requires Pillow (`pip install Pillow`) and macOS's `iconutil` (built in).
Run from anywhere: `python3 scripts/make_icon.py`.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
FONT_PATH = REPO / "app" / "assets" / "fonts" / "ShipporiMincho-Bold.ttf"
OUT_ICNS = REPO / "app" / "assets" / "icon" / "AppIcon.icns"

BACKGROUND = "#F4ECDC"
PANEL = "#FBF7EE"
ACCENT = "#B5563C"
SAGE = "#7C9473"
BORDER = "#D8CBB0"

SIZE = 1024


def render_base() -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = 48
    radius = 220
    draw.rounded_rectangle(
        [margin, margin, SIZE - margin, SIZE - margin],
        radius=radius,
        fill=BACKGROUND,
        outline=BORDER,
        width=10,
    )

    inset = margin + 56
    draw.rounded_rectangle(
        [inset, inset, SIZE - inset, SIZE - inset],
        radius=radius - 40,
        outline=SAGE,
        width=6,
    )

    seal_r = 300
    cx, cy = SIZE // 2, SIZE // 2 + 10
    draw.ellipse([cx - seal_r, cy - seal_r, cx + seal_r, cy + seal_r], fill=ACCENT)
    draw.ellipse(
        [cx - seal_r + 18, cy - seal_r + 18, cx + seal_r - 18, cy + seal_r - 18],
        outline=PANEL,
        width=8,
    )

    font = ImageFont.truetype(str(FONT_PATH), 360)
    text = "A"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1] - 14), text, font=font, fill=PANEL)

    return img


def main() -> None:
    base = render_base()

    with tempfile.TemporaryDirectory() as tmp:
        iconset = Path(tmp) / "AppIcon.iconset"
        iconset.mkdir()

        for size in (16, 32, 64, 128, 256, 512, 1024):
            base.resize((size, size), Image.LANCZOS).save(iconset / f"icon_{size}x{size}.png")
            if size <= 512:
                base.resize((size * 2, size * 2), Image.LANCZOS).save(
                    iconset / f"icon_{size}x{size}@2x.png"
                )

        OUT_ICNS.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(OUT_ICNS)], check=True)

    print(f"wrote {OUT_ICNS}")


if __name__ == "__main__":
    if not shutil.which("iconutil"):
        raise SystemExit("iconutil not found — this script only works on macOS.")
    main()
