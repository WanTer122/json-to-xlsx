"""从 skill 本地图标库加载 PNG 图标（供 CustomTkinter 使用）。"""

from __future__ import annotations

from pathlib import Path

import customtkinter as ctk
from PIL import Image

APP_DIR = Path(__file__).resolve().parent
ICONS_DIR = APP_DIR / "assets" / "icons"

ICON_MAP = {
    "upload": "file-text",
    "format": "code",
    "clear": "close",
    "mapping": "layout-grid",
    "validate": "check-circle",
    "preview": "eye",
    "generate": "file-text",
    "parse": "search",
    "theme": "settings",
    "folder": "building",
    "split": "layout-grid",
    "info": "info",
}

_cache: dict[tuple[str, int, str], ctk.CTkImage] = {}


def clear_icon_cache() -> None:
    _cache.clear()


def _load_png(name: str, size: int) -> Image.Image | None:
    path = ICONS_DIR / f"{name}.png"
    if path.exists():
        img = Image.open(path).convert("RGBA")
        return img.resize((size, size), Image.Resampling.LANCZOS)
    return None


def _tint_image(img: Image.Image, hex_color: str) -> Image.Image:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    tinted = img.copy()
    pixels = tinted.load()
    for y in range(tinted.height):
        for x in range(tinted.width):
            _, _, _, alpha = pixels[x, y]
            if alpha > 0:
                pixels[x, y] = (r, g, b, alpha)
    return tinted


def get_icon(key: str, size: int = 18, *, for_primary: bool = False) -> ctk.CTkImage | None:
    from ui_theme import button_palette, is_dark_mode

    icon_name = ICON_MAP.get(key, key)
    mode = "dark" if is_dark_mode() else "light"
    cache_key = (icon_name, size, mode, for_primary)
    if cache_key in _cache:
        return _cache[cache_key]

    img = _load_png(icon_name, size)
    if img is None:
        return None

    if is_dark_mode():
        if for_primary:
            color = button_palette()["primary_text"]
        else:
            color = "#cbd5e1"
        img = _tint_image(img, color)
    light_img = _load_png(icon_name, size) or img
    dark_img = img if is_dark_mode() else light_img

    ctk_img = ctk.CTkImage(light_image=light_img, dark_image=dark_img, size=(size, size))
    _cache[cache_key] = ctk_img
    return ctk_img


def apply_button_icon(button: ctk.CTkButton, key: str, style: str = "secondary", size: int = 18) -> None:
    icon = get_icon(key, size=size, for_primary=(style == "primary"))
    if icon is not None:
        button.configure(image=icon, compound="left")


def icon_button(
    parent,
    key: str,
    text: str,
    command,
    *,
    width: int | None = None,
    style: str = "secondary",
    size: int = 18,
) -> ctk.CTkButton:
    from ui_theme import apply_button_style, ghost_button, primary_button, secondary_button

    factories = {
        "primary": primary_button,
        "secondary": secondary_button,
        "ghost": ghost_button,
    }
    factory = factories.get(style, secondary_button)
    btn = factory(parent, text=text, command=command, width=width)
    apply_button_icon(btn, key, style=style, size=size)
    btn._icon_key = key  # noqa: SLF001
    btn._icon_style = style  # noqa: SLF001
    return btn
