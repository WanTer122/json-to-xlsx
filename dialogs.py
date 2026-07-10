"""弹窗：字段映射编辑与 Sheet 拆分确认。"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

import customtkinter as ctk
from tkinter import messagebox

from app_icon import apply_window_icon
from ui_theme import card, font, ghost_button, muted_label, palette, primary_button, section_title


def _sanitize_sheet_name_input(name: str) -> str:
    text = re.sub(r"[\\/*?:\[\]]", "_", name.strip())
    return text[:31] if text else "空值"


class ColumnMappingWindow(ctk.CTkToplevel):
    def __init__(
        self,
        parent: ctk.CTk,
        mappings: list[tuple[str, str, str]],
        on_apply: Callable[[dict[str, str]], None],
    ) -> None:
        super().__init__(parent)
        apply_window_icon(self)
        self.title("字段映射")
        self.geometry("760x540")
        self.minsize(620, 380)
        self.transient(parent)
        self.grab_set()

        colors = palette()
        self.configure(fg_color=colors["app_bg"])

        self._on_apply = on_apply
        self._rows: list[tuple[str, str, ctk.CTkEntry]] = []

        wrapper = card(self)
        wrapper.pack(fill="both", expand=True, padx=20, pady=20)

        section_title(wrapper, "字段映射").pack(anchor="w", padx=16, pady=(16, 4))
        muted_label(wrapper, "可修改「中文列名」；仅保存与默认翻译不同的项。").pack(anchor="w", padx=16, pady=(0, 12))

        header = ctk.CTkFrame(wrapper, fg_color=colors["card_bg"], corner_radius=0)
        header.pack(fill="x", padx=16, pady=(0, 8))
        header.grid_columnconfigure(1, weight=1)
        header.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(header, text="英文字段", font=font(13, "bold"), text_color=colors["text_primary"]).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(header, text="默认中文", font=font(13, "bold"), text_color=colors["text_primary"]).grid(
            row=0, column=1, sticky="w", padx=(16, 0)
        )
        ctk.CTkLabel(header, text="中文列名（可编辑）", font=font(13, "bold"), text_color=colors["text_primary"]).grid(
            row=0, column=2, sticky="w", padx=(16, 0)
        )

        scroll = ctk.CTkScrollableFrame(wrapper, fg_color=colors["card_bg"], label_fg_color=colors["card_bg"])
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        scroll.grid_columnconfigure(1, weight=1)
        scroll.grid_columnconfigure(2, weight=1)

        for idx, (english, default_cn, current_cn) in enumerate(mappings):
            ctk.CTkLabel(scroll, text=english, anchor="w", font=font(13), text_color=colors["text_primary"]).grid(
                row=idx, column=0, sticky="ew", pady=4
            )
            ctk.CTkLabel(scroll, text=default_cn, anchor="w", font=font(13), text_color=colors["text_muted"]).grid(
                row=idx, column=1, sticky="ew", padx=(16, 0), pady=4
            )
            entry = ctk.CTkEntry(scroll, height=34, corner_radius=8)
            entry.grid(row=idx, column=2, sticky="ew", padx=(16, 0), pady=4)
            entry.insert(0, current_cn)
            self._rows.append((english, default_cn, entry))

        actions = ctk.CTkFrame(wrapper, fg_color=colors["card_bg"], corner_radius=0)
        actions.pack(fill="x", padx=16, pady=(0, 16))

        ghost_button(actions, text="恢复全部默认", command=self._reset_defaults).pack(side="left")
        ghost_button(actions, text="取消", command=self.destroy, width=100).pack(side="right", padx=(8, 0))
        primary_button(actions, text="应用", command=self._apply, width=100).pack(side="right")

    def _reset_defaults(self) -> None:
        for _, default_cn, entry in self._rows:
            entry.delete(0, "end")
            entry.insert(0, default_cn)

    def _apply(self) -> None:
        overrides: dict[str, str] = {}
        for english, default_cn, entry in self._rows:
            custom = entry.get().strip()
            if not custom:
                messagebox.showwarning("提示", f"字段「{english}」的中文列名不能为空", parent=self)
                return
            if custom != default_cn:
                overrides[english] = custom
        self._on_apply(overrides)
        self.destroy()


class SheetSplitConfirmWindow(ctk.CTkToplevel):
    def __init__(
        self,
        parent: ctk.CTk,
        groups: list[dict[str, Any]],
        on_confirm: Callable[[dict[str, str]], None],
    ) -> None:
        super().__init__(parent)
        apply_window_icon(self)
        self.title("确认 Sheet 拆分")
        self.geometry("720x500")
        self.minsize(580, 340)
        self.transient(parent)
        self.grab_set()

        colors = palette()
        self.configure(fg_color=colors["app_bg"])

        self._on_confirm = on_confirm
        self._rows: list[tuple[str, ctk.CTkEntry]] = []

        wrapper = card(self)
        wrapper.pack(fill="both", expand=True, padx=20, pady=20)

        section_title(wrapper, "确认 Sheet 拆分").pack(anchor="w", padx=16, pady=(16, 4))
        muted_label(wrapper, f"共 {len(groups)} 个工作表，可修改每个 Sheet 的名称后确认生成。").pack(
            anchor="w", padx=16, pady=(0, 12)
        )

        header = ctk.CTkFrame(wrapper, fg_color=colors["card_bg"], corner_radius=0)
        header.pack(fill="x", padx=16, pady=(0, 8))
        header.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(header, text="分组值", font=font(13, "bold"), text_color=colors["text_primary"]).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(header, text="行数", font=font(13, "bold"), text_color=colors["text_primary"]).grid(
            row=0, column=1, sticky="w", padx=(16, 0)
        )
        ctk.CTkLabel(header, text="Sheet 名称", font=font(13, "bold"), text_color=colors["text_primary"]).grid(
            row=0, column=2, sticky="w", padx=(16, 0)
        )

        scroll = ctk.CTkScrollableFrame(wrapper, fg_color=colors["card_bg"], label_fg_color=colors["card_bg"])
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        scroll.grid_columnconfigure(2, weight=1)

        for idx, group in enumerate(groups):
            ctk.CTkLabel(scroll, text=group["display_value"], anchor="w", font=font(13), text_color=colors["text_primary"]).grid(
                row=idx, column=0, sticky="ew", pady=4
            )
            ctk.CTkLabel(scroll, text=str(group["row_count"]), anchor="w", font=font(13), text_color=colors["text_muted"]).grid(
                row=idx, column=1, sticky="ew", padx=(16, 0), pady=4
            )
            entry = ctk.CTkEntry(scroll, height=34, corner_radius=8)
            entry.grid(row=idx, column=2, sticky="ew", padx=(16, 0), pady=4)
            entry.insert(0, group["sheet_name"])
            self._rows.append((group["value_key"], entry))

        actions = ctk.CTkFrame(wrapper, fg_color=colors["card_bg"], corner_radius=0)
        actions.pack(fill="x", padx=16, pady=(0, 16))

        ghost_button(actions, text="取消", command=self.destroy, width=100).pack(side="right", padx=(8, 0))
        primary_button(actions, text="确认生成", command=self._confirm, width=120).pack(side="right")

    def _confirm(self) -> None:
        sheet_names: dict[str, str] = {}
        sanitized_seen: set[str] = set()

        for value_key, entry in self._rows:
            raw = entry.get().strip()
            if not raw:
                messagebox.showwarning("提示", "Sheet 名称不能为空", parent=self)
                return
            sanitized = _sanitize_sheet_name_input(raw)
            if sanitized in sanitized_seen:
                messagebox.showwarning("提示", f"Sheet 名称「{sanitized}」重复，请修改", parent=self)
                return
            sanitized_seen.add(sanitized)
            sheet_names[value_key] = raw

        self._on_confirm(sheet_names)
        self.destroy()
