"""应用窗口图标（与桌面快捷方式使用同一 app_icon.ico）。"""

from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path

ICON_PATH = Path(__file__).resolve().parent / "app_icon.ico"
_APP_ID_SET = False


def setup_windows_app_id() -> None:
    """Windows 任务栏图标需设置 AppUserModelID，否则会显示 Python 默认图标。"""
    global _APP_ID_SET
    if _APP_ID_SET or sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("json-to-xlsx.converter.1")
        _APP_ID_SET = True
    except Exception:
        pass


def apply_window_icon(window: tk.Misc) -> None:
    setup_windows_app_id()
    if not ICON_PATH.exists():
        return
    try:
        window.iconbitmap(str(ICON_PATH))
    except tk.TclError:
        pass
