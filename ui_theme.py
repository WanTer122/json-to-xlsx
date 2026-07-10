"""UI 设计令牌 — 基于 frontend-page-generator ui-design 子技能。"""

from __future__ import annotations

from pathlib import Path

import customtkinter as ctk

APP_DIR = Path(__file__).resolve().parent
THEME_JSON = APP_DIR / "assets" / "theme" / "professional-blue.json"

# 专业蓝配色方案（浅色模式主色）
COLORS = {
    "primary": "#3b82f6",
    "primary_hover": "#2563eb",
    "primary_dark": "#1d4ed8",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",
}

FONT_UI = "Microsoft YaHei UI"
FONT_CODE = "Consolas"

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
    "2xl": 32,
}


def setup_appearance() -> None:
    ctk.set_appearance_mode("light")
    if THEME_JSON.exists():
        ctk.set_default_color_theme(str(THEME_JSON))
    else:
        ctk.set_default_color_theme("blue")
    ctk.set_widget_scaling(1.0)


def is_dark_mode() -> bool:
    return ctk.get_appearance_mode() == "Dark"


def palette() -> dict[str, str]:
    dark = is_dark_mode()
    if dark:
        return {
            "app_bg": "#0f172a",
            "card_bg": "#1e293b",
            "card_border": "#334155",
            "text_primary": "#f1f5f9",
            "text_secondary": "#94a3b8",
            "text_muted": "#64748b",
            "input_bg": "#0f172a",
            "status_bg": "#1e293b",
            "accent_soft": "#334155",
            "header_subtitle": "#94a3b8",
        }
    return {
        "app_bg": "#f8fafc",
        "card_bg": "#ffffff",
        "card_border": "#e2e8f0",
        "text_primary": "#1e293b",
        "text_secondary": "#64748b",
        "text_muted": "#94a3b8",
        "input_bg": "#f8fafc",
        "status_bg": "#ffffff",
        "accent_soft": "#eff6ff",
        "header_subtitle": "#64748b",
    }


def font(size: int, weight: str = "normal", family: str | None = None) -> ctk.CTkFont:
    return ctk.CTkFont(family=family or FONT_UI, size=size, weight=weight)


def code_font(size: int = 13) -> ctk.CTkFont:
    return ctk.CTkFont(family=FONT_CODE, size=size)


def card(parent, **kwargs) -> ctk.CTkFrame:
    colors = palette()
    options = {
        "fg_color": colors["card_bg"],
        "border_width": 1,
        "border_color": colors["card_border"],
        "corner_radius": 12,
    }
    options.update(kwargs)
    return ctk.CTkFrame(parent, **options)


def section_title(parent, text: str, **grid) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent,
        text=text,
        font=font(15, "bold"),
        text_color=palette()["text_primary"],
        anchor="w",
        **grid,
    )


def muted_label(parent, text: str, **kwargs) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent,
        text=text,
        font=font(13),
        text_color=palette()["text_secondary"],
        **kwargs,
    )


def button_palette() -> dict[str, str]:
    """按钮配色：暗色模式使用低饱和、与背景融合的色调。"""
    if is_dark_mode():
        return {
            "primary_fg": "#1e3a5f",
            "primary_hover": "#234876",
            "primary_text": "#dbeafe",
            "primary_border": "#3b5998",
            "secondary_fg": "#334155",
            "secondary_hover": "#3f4f63",
            "secondary_text": "#e2e8f0",
            "ghost_fg": "#1e293b",
            "ghost_hover": "#334155",
            "ghost_text": "#cbd5e1",
            "ghost_border": "#475569",
        }
    return {
        "primary_fg": COLORS["primary"],
        "primary_hover": COLORS["primary_hover"],
        "primary_text": "#ffffff",
        "primary_border": COLORS["primary"],
        "secondary_fg": "#e2e8f0",
        "secondary_hover": "#cbd5e1",
        "secondary_text": "#1e293b",
        "ghost_fg": "#f8fafc",
        "ghost_hover": "#eff6ff",
        "ghost_text": "#64748b",
        "ghost_border": "#e2e8f0",
    }


def apply_button_style(button: ctk.CTkButton, style: str = "secondary") -> None:
    bp = button_palette()
    if style == "primary":
        button.configure(
            fg_color=bp["primary_fg"],
            hover_color=bp["primary_hover"],
            text_color=bp["primary_text"],
            border_width=1 if is_dark_mode() else 0,
            border_color=bp["primary_border"],
        )
    elif style == "ghost":
        button.configure(
            fg_color=bp["ghost_fg"],
            hover_color=bp["ghost_hover"],
            text_color=bp["ghost_text"],
            border_width=1,
            border_color=bp["ghost_border"],
        )
    else:
        button.configure(
            fg_color=bp["secondary_fg"],
            hover_color=bp["secondary_hover"],
            text_color=bp["secondary_text"],
            border_width=0,
        )


def primary_button(parent, text: str, command, **kwargs) -> ctk.CTkButton:
    btn = ctk.CTkButton(
        parent,
        text=text,
        command=command,
        font=font(15, "bold"),
        corner_radius=8,
        height=40,
        **kwargs,
    )
    apply_button_style(btn, "primary")
    return btn


def secondary_button(parent, text: str, command, **kwargs) -> ctk.CTkButton:
    btn = ctk.CTkButton(
        parent,
        text=text,
        command=command,
        font=font(13),
        corner_radius=8,
        height=36,
        **kwargs,
    )
    apply_button_style(btn, "secondary")
    return btn


def ghost_button(parent, text: str, command, **kwargs) -> ctk.CTkButton:
    btn = ctk.CTkButton(
        parent,
        text=text,
        command=command,
        font=font(13),
        corner_radius=8,
        height=36,
        **kwargs,
    )
    apply_button_style(btn, "ghost")
    return btn
