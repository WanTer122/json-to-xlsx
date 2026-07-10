"""将 skill 图标风格预渲染为 PNG（纯 PIL，无 cairo 依赖）。"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

APP_DIR = Path(__file__).resolve().parent.parent
OUT = APP_DIR / "assets" / "icons"

COLOR = "#1e293b"
SIZE = 48
STROKE = 2


def _new() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def _save(img: Image.Image, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / f"{name}.png")
    print(f"saved {name}.png")


def draw_file_text() -> None:
    img, d = _new()
    d.rounded_rectangle((12, 8, 36, 40), radius=4, outline=COLOR, width=STROKE)
    d.line((20, 8, 20, 16), fill=COLOR, width=STROKE)
    d.line((20, 16, 28, 16), fill=COLOR, width=STROKE)
    for y in (22, 28, 34):
        d.line((16, y, 32, y), fill=COLOR, width=STROKE)
    _save(img, "file-text")


def draw_code() -> None:
    img, d = _new()
    d.line((18, 16, 12, 24), fill=COLOR, width=STROKE)
    d.line((12, 24, 18, 32), fill=COLOR, width=STROKE)
    d.line((30, 16, 36, 24), fill=COLOR, width=STROKE)
    d.line((36, 24, 30, 32), fill=COLOR, width=STROKE)
    d.line((22, 34, 26, 14), fill=COLOR, width=STROKE)
    _save(img, "code")


def draw_close() -> None:
    img, d = _new()
    d.line((14, 14, 34, 34), fill=COLOR, width=STROKE)
    d.line((34, 14, 14, 34), fill=COLOR, width=STROKE)
    _save(img, "close")


def draw_layout_grid() -> None:
    img, d = _new()
    d.rounded_rectangle((10, 10, 38, 38), radius=4, outline=COLOR, width=STROKE)
    d.line((24, 10, 24, 38), fill=COLOR, width=STROKE)
    d.line((10, 24, 38, 24), fill=COLOR, width=STROKE)
    _save(img, "layout-grid")


def draw_check_circle() -> None:
    img, d = _new()
    d.ellipse((10, 10, 38, 38), outline=COLOR, width=STROKE)
    d.line((16, 24, 22, 30), fill=COLOR, width=STROKE)
    d.line((22, 30, 34, 18), fill=COLOR, width=STROKE)
    _save(img, "check-circle")


def draw_eye() -> None:
    img, d = _new()
    d.ellipse((10, 18, 38, 30), outline=COLOR, width=STROKE)
    d.ellipse((21, 21, 27, 27), outline=COLOR, width=STROKE)
    _save(img, "eye")


def draw_search() -> None:
    img, d = _new()
    d.ellipse((12, 12, 30, 30), outline=COLOR, width=STROKE)
    d.line((28, 28, 36, 36), fill=COLOR, width=STROKE)
    _save(img, "search")


def draw_settings() -> None:
    img, d = _new()
    cx, cy, r = 24, 24, 10
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=COLOR, width=STROKE)
    d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), outline=COLOR, width=STROKE)
    for angle in (0, 60, 120, 180, 240, 300):
        rad = math.radians(angle)
        x1 = cx + math.cos(rad) * 12
        y1 = cy + math.sin(rad) * 12
        x2 = cx + math.cos(rad) * 16
        y2 = cy + math.sin(rad) * 16
        d.line((x1, y1, x2, y2), fill=COLOR, width=STROKE)
    _save(img, "settings")


def draw_building() -> None:
    img, d = _new()
    d.rectangle((14, 12, 34, 38), outline=COLOR, width=STROKE)
    for x in (18, 26):
        for y in (18, 26, 34):
            d.rectangle((x, y, x + 4, y + 4), outline=COLOR, width=1)
    _save(img, "building")


def draw_info() -> None:
    img, d = _new()
    d.ellipse((10, 10, 38, 38), outline=COLOR, width=STROKE)
    d.line((24, 22, 24, 22), fill=COLOR, width=STROKE)
    d.ellipse((22, 14, 26, 18), fill=COLOR)
    d.line((24, 26, 24, 34), fill=COLOR, width=STROKE)
    _save(img, "info")


def main() -> None:
    draw_file_text()
    draw_code()
    draw_close()
    draw_layout_grid()
    draw_check_circle()
    draw_eye()
    draw_search()
    draw_settings()
    draw_building()
    draw_info()


if __name__ == "__main__":
    main()
