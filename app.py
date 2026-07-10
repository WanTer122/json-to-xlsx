"""JSON to Excel desktop application."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

from app_icon import apply_window_icon, setup_windows_app_id
from converter import (
    ConversionError,
    convert_json_to_excel,
    get_available_fields,
    get_column_mappings,
    get_preview_info,
    get_split_preview,
    parse_field_label,
    validate_json,
)
from dialogs import ColumnMappingWindow, SheetSplitConfirmWindow
from ui_icons import apply_button_icon, clear_icon_cache, get_icon, icon_button
from ui_theme import (
    COLORS,
    apply_button_style,
    card,
    code_font,
    font,
    ghost_button,
    is_dark_mode,
    muted_label,
    palette,
    primary_button,
    secondary_button,
    section_title,
    setup_appearance,
)

def _default_save_dir() -> str:
    desktop = Path.home() / "Desktop"
    if desktop.is_dir():
        return str(desktop)
    return str(Path.home() / "Documents")


DEFAULT_SAVE_DIR = _default_save_dir()
APP_DIR = Path(__file__).resolve().parent


class PreviewWindow(ctk.CTkToplevel):
    def __init__(self, parent: ctk.CTk, df) -> None:
        super().__init__(parent)
        apply_window_icon(self)
        self.title("数据预览")
        self.geometry("920x460")
        self.minsize(680, 360)

        colors = palette()
        self.configure(fg_color=colors["app_bg"])

        wrapper = card(self)
        wrapper.pack(fill="both", expand=True, padx=20, pady=20)

        section_title(wrapper, "数据预览").pack(anchor="w", padx=16, pady=(16, 8))
        muted_label(wrapper, f"显示前 {min(20, len(df))} 行，共 {len(df)} 行 × {len(df.columns)} 列").pack(
            anchor="w", padx=16, pady=(0, 8)
        )

        header = " | ".join(str(col) for col in df.columns)
        rows = [header]
        for _, row in df.head(20).iterrows():
            rows.append(" | ".join(str(v) for v in row.tolist()))

        textbox = ctk.CTkTextbox(wrapper, font=code_font(13), corner_radius=8)
        textbox.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        textbox.insert("1.0", "\n".join(rows))
        textbox.configure(state="disabled")


class JsonToExcelApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        apply_window_icon(self)
        self.title("JSON → Excel 转换工具")
        self.geometry("960x720")
        self.minsize(780, 600)

        self._save_dir = DEFAULT_SAVE_DIR
        self._column_overrides: dict[str, str] = {}
        self._status_dot: ctk.CTkLabel | None = None
        self._body: ctk.CTkFrame | None = None
        self._styled_buttons: list[tuple[ctk.CTkButton, str, str | None]] = []
        self._build_ui()
        self._apply_theme_colors()

    def _track_button(self, button: ctk.CTkButton, style: str, icon_key: str | None = None) -> ctk.CTkButton:
        self._styled_buttons.append((button, style, icon_key))
        return button

    def _refresh_theme_buttons(self) -> None:
        clear_icon_cache()
        for button, style, icon_key in self._styled_buttons:
            apply_button_style(button, style)
            if icon_key:
                apply_button_icon(button, icon_key, style=style)
        if getattr(self, "_title_icon_label", None) is not None:
            code_icon = get_icon("format", size=18)
            if code_icon:
                self._title_icon_label.configure(image=code_icon, compound="left")

    def _apply_theme_colors(self) -> None:
        colors = palette()
        self.configure(fg_color=colors["app_bg"])
        if self._body is not None:
            self._body.configure(fg_color=colors["app_bg"])
        for attr in ("_header_card", "_editor_card", "_export_card", "_split_card"):
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.configure(fg_color=colors["card_bg"], border_color=colors["card_border"])
        if getattr(self, "_status_bar", None) is not None:
            self._status_bar.configure(fg_color=colors["status_bg"], border_color=colors["card_border"])
        if getattr(self, "_title_label", None) is not None:
            self._title_label.configure(text_color="#93c5fd" if is_dark_mode() else COLORS["primary"])
        for attr in ("_editor_header", "_toolbar", "_options_row", "_actions"):
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.configure(fg_color=colors["app_bg"])

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        colors = palette()

        self._header_card = card(self)
        self._header_card.grid(row=0, column=0, sticky="ew", padx=24, pady=(16, 8))
        self._header_card.grid_columnconfigure(1, weight=1)

        logo_img = None
        logo_path = APP_DIR / "app_icon.png"
        if logo_path.exists():
            logo = Image.open(logo_path).resize((40, 40), Image.Resampling.LANCZOS)
            logo_img = ctk.CTkImage(light_image=logo, dark_image=logo, size=(40, 40))

        if logo_img:
            ctk.CTkLabel(self._header_card, text="", image=logo_img).grid(
                row=0, column=0, rowspan=2, padx=(20, 12), pady=16, sticky="w"
            )
            title_col = 1
        else:
            title_col = 0

        self._title_label = ctk.CTkLabel(
            self._header_card,
            text="JSON → Excel",
            font=font(28, "bold"),
            text_color="#93c5fd" if is_dark_mode() else COLORS["primary"],
            anchor="w",
        )
        self._title_label.grid(row=0, column=title_col, sticky="w", pady=(16, 0))

        muted_label(
            self._header_card,
            "将 JSON 数据快速转换为精美的 Excel 表格",
            anchor="w",
        ).grid(row=1, column=title_col, sticky="w", pady=(4, 16))

        theme_icon = get_icon("theme", size=16)
        self.theme_btn = self._track_button(
            ghost_button(
                self._header_card,
                text="切换主题",
                command=self._toggle_theme,
                width=110,
            ),
            "ghost",
            "theme",
        )
        if theme_icon:
            self.theme_btn.configure(image=theme_icon, compound="left")
        self.theme_btn.grid(row=0, column=2, rowspan=2, padx=20, pady=16, sticky="e")

        self._body = ctk.CTkFrame(self, fg_color=colors["app_bg"], corner_radius=0)
        self._body.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 8))
        self._body.grid_columnconfigure(0, weight=1)
        self._body.grid_rowconfigure(0, weight=1)

        self._editor_card = card(self._body)
        self._editor_card.grid(row=0, column=0, sticky="nsew", pady=(0, 12))
        self._editor_card.grid_columnconfigure(0, weight=1)
        self._editor_card.grid_rowconfigure(1, weight=1)

        self._editor_header = ctk.CTkFrame(self._editor_card, fg_color=colors["app_bg"], corner_radius=0)
        self._editor_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))
        self._editor_header.grid_columnconfigure(0, weight=1)

        code_icon = get_icon("format", size=18)
        self._title_icon_label = section_title(self._editor_header, "JSON 数据")
        self._title_icon_label.grid(row=0, column=0, sticky="w")
        if code_icon:
            self._title_icon_label.configure(image=code_icon, compound="left")

        self.json_text = ctk.CTkTextbox(
            self._editor_card,
            font=code_font(13),
            wrap="none",
            corner_radius=8,
        )
        self.json_text.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 8))

        self._toolbar = ctk.CTkFrame(self._editor_card, fg_color=colors["app_bg"], corner_radius=0)
        self._toolbar.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 12))
        for i in range(5):
            self._toolbar.grid_columnconfigure(i, weight=1 if i == 4 else 0)

        self._track_button(
            icon_button(self._toolbar, "upload", "上传 JSON", self._upload_json, width=120),
            "secondary",
            "upload",
        ).grid(row=0, column=0, padx=(0, 8))
        self._track_button(
            icon_button(self._toolbar, "format", "格式化", self._format_json, width=100),
            "secondary",
            "format",
        ).grid(row=0, column=1, padx=(0, 8))
        self._track_button(
            icon_button(self._toolbar, "clear", "清空", self._clear_json, style="ghost", width=80),
            "ghost",
            "clear",
        ).grid(row=0, column=2, padx=(0, 8))
        self._track_button(
            icon_button(self._toolbar, "mapping", "字段映射", self._edit_column_mapping, width=110),
            "secondary",
            "mapping",
        ).grid(row=0, column=3, padx=(0, 8))
        self._track_button(
            icon_button(self._toolbar, "validate", "校验 JSON", self._validate, style="primary", width=110),
            "primary",
            "validate",
        ).grid(row=0, column=4, sticky="e")

        self._options_row = ctk.CTkFrame(self._body, fg_color=colors["app_bg"], corner_radius=0)
        self._options_row.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self._options_row.grid_columnconfigure(0, weight=3)
        self._options_row.grid_columnconfigure(1, weight=2)

        self._export_card = card(self._options_row)
        self._export_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._export_card.grid_columnconfigure(1, weight=1)

        section_title(self._export_card, "导出设置").grid(
            row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(12, 8)
        )

        muted_label(self._export_card, "文件名").grid(row=1, column=0, padx=(16, 8), pady=4, sticky="w")
        self.filename_entry = ctk.CTkEntry(self._export_card, placeholder_text="report.xlsx", height=34)
        self.filename_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(0, 16), pady=4)
        self.filename_entry.insert(0, "report.xlsx")

        muted_label(self._export_card, "保存到").grid(row=2, column=0, padx=(16, 8), pady=(4, 12), sticky="w")
        self.save_dir_entry = ctk.CTkEntry(self._export_card, height=34)
        self.save_dir_entry.grid(row=2, column=1, sticky="ew", padx=(0, 8), pady=(4, 12))
        self.save_dir_entry.insert(0, self._save_dir)
        browse_btn = self._track_button(
            icon_button(self._export_card, "folder", "浏览", self._browse_dir, width=80),
            "secondary",
            "folder",
        )
        browse_btn.grid(row=2, column=2, padx=(0, 16), pady=(4, 12))

        self._split_card = card(self._options_row)
        self._split_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._split_card.grid_columnconfigure(1, weight=1)

        section_title(self._split_card, "Sheet 拆分").grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(12, 8))

        self.split_checkbox = ctk.CTkCheckBox(
            self._split_card,
            text="按字段拆分 Sheet",
            font=font(13),
            command=self._toggle_split_field,
        )
        self.split_checkbox.grid(row=1, column=0, columnspan=2, padx=16, pady=(0, 6), sticky="w")

        self._track_button(
            icon_button(self._split_card, "parse", "解析字段", self._parse_fields, width=110),
            "secondary",
            "parse",
        ).grid(row=2, column=0, padx=16, pady=(0, 6), sticky="w")

        muted_label(self._split_card, "拆分字段").grid(row=3, column=0, padx=(16, 8), pady=(0, 12), sticky="w")
        self.split_field_combo = ctk.CTkComboBox(
            self._split_card,
            values=["请先解析字段"],
            state="disabled",
            height=34,
        )
        self.split_field_combo.grid(row=3, column=1, sticky="ew", padx=(0, 16), pady=(0, 12))
        self.split_field_combo.set("请先解析字段")

        self._actions = ctk.CTkFrame(self._body, fg_color=colors["app_bg"], corner_radius=0)
        self._actions.grid(row=2, column=0, sticky="ew")
        self._actions.grid_columnconfigure(0, weight=1)

        preview_btn = self._track_button(
            icon_button(self._actions, "preview", "预览数据", self._preview, width=140, style="secondary"),
            "secondary",
            "preview",
        )
        preview_btn.configure(height=40)
        preview_btn.grid(row=0, column=0, sticky="w")

        self.generate_btn = self._track_button(
            primary_button(self._actions, "生成 Excel", self._generate, width=180),
            "primary",
            "generate",
        )
        apply_button_icon(self.generate_btn, "generate", style="primary")
        self.generate_btn.grid(row=0, column=1, sticky="e")

        self._status_bar = card(self, corner_radius=8)
        self._status_bar.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 16))
        self._status_bar.grid_columnconfigure(1, weight=1)

        self._status_dot = ctk.CTkLabel(
            self._status_bar,
            text="●",
            font=font(10),
            text_color=COLORS["success"],
            width=20,
        )
        self._status_dot.grid(row=0, column=0, padx=(16, 4), pady=10)

        self.status_label = ctk.CTkLabel(
            self._status_bar,
            text="就绪",
            anchor="w",
            font=font(13),
            text_color=colors["text_secondary"],
        )
        self.status_label.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=10)

    def _get_json_text(self) -> str:
        return self.json_text.get("1.0", "end").strip()

    def _set_status(self, text: str, ok: bool = True) -> None:
        colors = palette()
        self.status_label.configure(text=text, text_color=colors["text_secondary"] if ok else COLORS["error"])
        if self._status_dot:
            self._status_dot.configure(text_color=COLORS["success"] if ok else COLORS["error"])

    def _toggle_theme(self) -> None:
        mode = "light" if ctk.get_appearance_mode() == "Dark" else "dark"
        ctk.set_appearance_mode(mode)
        self._apply_theme_colors()
        self._refresh_theme_buttons()

    def _upload_json(self) -> None:
        path = filedialog.askopenfilename(
            title="选择 JSON 文件",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")],
        )
        if not path:
            return
        try:
            content = Path(path).read_text(encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("读取失败", str(exc))
            return
        self.json_text.delete("1.0", "end")
        self.json_text.insert("1.0", content)
        self._validate()

    def _format_json(self) -> None:
        text = self._get_json_text()
        ok, message, data = validate_json(text)
        if not ok:
            messagebox.showerror("格式化失败", message)
            return
        formatted = json.dumps(data, ensure_ascii=False, indent=2)
        self.json_text.delete("1.0", "end")
        self.json_text.insert("1.0", formatted)
        self._set_status("JSON 已格式化")

    def _clear_json(self) -> None:
        self.json_text.delete("1.0", "end")
        self._set_status("已清空")

    def _validate(self) -> None:
        message, _ = get_preview_info(self._get_json_text(), self._column_overrides)
        ok = "错误" not in message and "失败" not in message and "为空" not in message and "不支持" not in message
        self._set_status(message, ok=ok)

    def _edit_column_mapping(self) -> None:
        message, mappings = get_column_mappings(self._get_json_text(), self._column_overrides)
        if mappings is None:
            messagebox.showerror("解析失败", message)
            self._set_status(message, ok=False)
            return

        def on_apply(overrides: dict[str, str]) -> None:
            self._column_overrides = overrides
            custom_count = len(overrides)
            self._set_status(
                f"{message} | 已自定义 {custom_count} 个字段" if custom_count else f"{message} | 使用默认翻译"
            )
            if self.split_field_combo.cget("values") != ["请先解析字段"]:
                self._parse_fields()

        ColumnMappingWindow(self, mappings, on_apply)

    def _toggle_split_field(self) -> None:
        enabled = bool(self.split_checkbox.get())
        if enabled and self.split_field_combo.cget("values") == ["请先解析字段"]:
            self.split_field_combo.configure(state="disabled")
            return
        self.split_field_combo.configure(state="normal" if enabled else "disabled")

    def _parse_fields(self) -> None:
        message, labels = get_available_fields(self._get_json_text(), self._column_overrides)
        if labels is None:
            messagebox.showerror("解析失败", message)
            self._set_status(message, ok=False)
            return

        self.split_field_combo.configure(values=labels, state="normal")
        self.split_field_combo.set(labels[0])
        self._set_status(message)

    def _browse_dir(self) -> None:
        path = filedialog.askdirectory(title="选择保存目录", initialdir=self._save_dir)
        if path:
            self._save_dir = path
            self.save_dir_entry.delete(0, "end")
            self.save_dir_entry.insert(0, path)

    def _preview(self) -> None:
        message, df = get_preview_info(self._get_json_text(), self._column_overrides)
        if df is None:
            messagebox.showerror("预览失败", message)
            self._set_status(message, ok=False)
            return
        self._set_status(message)
        PreviewWindow(self, df)

    def _generate(self) -> None:
        text = self._get_json_text()
        filename = self.filename_entry.get().strip()
        save_dir = self.save_dir_entry.get().strip()

        if not filename:
            messagebox.showwarning("提示", "请输入文件名")
            return
        if not save_dir:
            messagebox.showwarning("提示", "请选择保存目录")
            return

        output_path = Path(save_dir) / filename
        split_by: str | None = None
        if self.split_checkbox.get():
            selected = self.split_field_combo.get().strip()
            if not selected or selected == "请先解析字段":
                messagebox.showwarning("提示", "请先点击「解析字段」并选择要拆分的字段")
                return
            split_by = parse_field_label(selected)

            message, groups = get_split_preview(text, split_by, self._column_overrides)
            if groups is None:
                messagebox.showerror("拆分预览失败", message)
                self._set_status(message, ok=False)
                return

            SheetSplitConfirmWindow(self, groups, lambda names: self._do_generate(text, output_path, split_by, names))
            return

        self._do_generate(text, output_path, split_by=None, sheet_names=None)

    def _do_generate(
        self,
        text: str,
        output_path: Path,
        split_by: str | None,
        sheet_names: dict[str, str] | None,
    ) -> None:
        self.generate_btn.configure(state="disabled", text="生成中...")
        self.update_idletasks()

        try:
            result = convert_json_to_excel(
                text,
                output_path,
                split_by=split_by,
                sheet_names=sheet_names,
                column_overrides=self._column_overrides or None,
            )
        except ConversionError as exc:
            messagebox.showerror("生成失败", str(exc))
            self._set_status(str(exc), ok=False)
        except OSError as exc:
            messagebox.showerror("保存失败", str(exc))
            self._set_status(f"保存失败: {exc}", ok=False)
        else:
            self._set_status(result)
            if messagebox.askyesno("生成成功", f"{result}\n\n是否打开所在文件夹？"):
                self._open_folder(output_path.parent)
        finally:
            self.generate_btn.configure(state="normal", text="生成 Excel")
            apply_button_style(self.generate_btn, "primary")
            apply_button_icon(self.generate_btn, "generate", style="primary")

    @staticmethod
    def _open_folder(path: Path) -> None:
        folder = str(path)
        if sys.platform == "win32":
            os.startfile(folder)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.run(["open", folder], check=False)
        else:
            subprocess.run(["xdg-open", folder], check=False)


def main() -> None:
    setup_windows_app_id()
    setup_appearance()
    app = JsonToExcelApp()
    app.mainloop()


if __name__ == "__main__":
    main()
