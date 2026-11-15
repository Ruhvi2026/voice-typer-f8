"""
Bangla Voice Typer - Settings & Control Center
Supports 125+ Languages, Dynamic UI Translation, and Dark/Light Themes
Author: Ruhvi2026 (Project Ruhvi)
"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox

from languages_data import ALL_LANGUAGES, get_ui_text

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(APP_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "mode": "auto_stop",     # "auto_stop", "push_to_talk", "toggle"
    "language": "bn-IN",     # Default: Bengali (India)
    "theme": "dark",         # "dark" or "light"
    "sound_effects": True,
    "floating_badge": True,
    "silence_seconds": 3.2,
    "max_seconds": 45,
    "auto_paste": True,
    "hotkey": "f8"
}

THEMES = {
    "dark": {
        "bg": "#181825",
        "header_bg": "#11111b",
        "card_bg": "#1e1e2e",
        "border": "#313244",
        "text": "#cdd6f4",
        "subtext": "#a6adc8",
        "accent": "#89b4fa",
        "success": "#a6e3a1",
        "btn_bg": "#a6e3a1",
        "btn_fg": "#11111b",
        "trough": "#313244",
        "select": "#11111b",
        "sep": "#313244"
    },
    "light": {
        "bg": "#f1f5f9",
        "header_bg": "#ffffff",
        "card_bg": "#ffffff",
        "border": "#cbd5e1",
        "text": "#0f172a",
        "subtext": "#475569",
        "accent": "#2563eb",
        "success": "#16a34a",
        "btn_bg": "#2563eb",
        "btn_fg": "#ffffff",
        "trough": "#e2e8f0",
        "select": "#f8fafc",
        "sep": "#e2e8f0"
    }
}

def load_settings():
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_SETTINGS, **data}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False


class SettingsUI:
    def __init__(self, root=None, on_save_callback=None, on_minimize_callback=None):
        self.settings = load_settings()
        self.on_save_cb = on_save_callback
        self.on_min_cb = on_minimize_callback

        if root:
            self.win = root
        else:
            self.win = tk.Tk()

        self.win.title("🎙️ Voice Typer — কন্ট্রোল সেন্টার")
        self.win.geometry("540x720")
        self.win.resizable(False, False)

        # Set window icon
        icon_path = os.path.join(APP_DIR, "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.win.iconbitmap(icon_path)
            except Exception:
                pass

        # Language maps
        self.lang_map = {name: code for name, code in ALL_LANGUAGES}
        self.code_to_name = {code: name for name, code in ALL_LANGUAGES}

        # Active state variables
        self.mode_var = tk.StringVar(value=self.settings.get("mode", "auto_stop"))
        self.lang_var = tk.StringVar(value=self.settings.get("language", "bn-IN"))
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "dark"))
        self.sound_var = tk.BooleanVar(value=self.settings.get("sound_effects", True))
        self.badge_var = tk.BooleanVar(value=self.settings.get("floating_badge", True))
        self.paste_var = tk.BooleanVar(value=self.settings.get("auto_paste", True))
        self.silence_var = tk.DoubleVar(value=self.settings.get("silence_seconds", 3.2))

        # Widget tracking for dynamic theme/i18n updates
        self.themed_widgets = {}

        self._build_ui()
        self._apply_theme()
        self._refresh_i18n()
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

    def _t(self, key):
        return get_ui_text(self.lang_var.get(), key)

    def _build_ui(self):
        # Header banner
        self.header = tk.Frame(self.win, padx=24, pady=16)
        self.header.pack(fill="x")

        self.title_lbl = tk.Label(self.header, text=self._t("app_title"), font=("Segoe UI", 16, "bold"))
        self.title_lbl.pack(anchor="w")

        self.sub_lbl = tk.Label(self.header, text=self._t("subtitle"), font=("Segoe UI", 9))
        self.sub_lbl.pack(anchor="w", pady=(2, 0))

        # Main content
        self.content = tk.Frame(self.win, padx=24, pady=14)
        self.content.pack(fill="both", expand=True)

        # --- Section 1: Modes ---
        self.sec_modes = tk.LabelFrame(
            self.content, 
            text=self._t("sec_mode"), 
            font=("Segoe UI", 10, "bold"), 
            padx=14, 
            pady=10,
            highlightthickness=1
        )
        self.sec_modes.pack(fill="x", pady=(0, 12))

        # Mode 1: Auto-Stop
        self.rb1 = tk.Radiobutton(
            self.sec_modes,
            text=self._t("mode_auto"),
            value="auto_stop",
            variable=self.mode_var,
            font=("Segoe UI", 10, "bold")
        )
        self.rb1.pack(anchor="w")

        self.desc1 = tk.Label(
            self.sec_modes,
            text="   " + self._t("mode_auto_desc"),
            font=("Segoe UI", 8),
            justify="left",
            wraplength=460
        )
        self.desc1.pack(anchor="w", pady=(0, 4))

        # Silence slider
        self.silence_frame = tk.Frame(self.sec_modes, padx=16)
        self.silence_frame.pack(fill="x", pady=(0, 6))

        self.lbl_silence = tk.Label(self.silence_frame, text=self._t("silence_lbl"), font=("Segoe UI", 8, "italic"))
        self.lbl_silence.pack(side="left")

        self.slider = tk.Scale(
            self.silence_frame, 
            from_=2.0, 
            to=5.5, 
            resolution=0.2, 
            orient="horizontal", 
            variable=self.silence_var,
            highlightthickness=0,
            length=140
        )
        self.slider.pack(side="left", padx=8)

        self.lbl_sec = tk.Label(self.silence_frame, text=self._t("sec_unit"), font=("Segoe UI", 8))
        self.lbl_sec.pack(side="left")

        self.sep1 = tk.Frame(self.sec_modes, height=1)
        self.sep1.pack(fill="x", pady=5)

        # Mode 2: Push-to-Talk
        self.rb2 = tk.Radiobutton(
            self.sec_modes,
            text=self._t("mode_ptt"),
            value="push_to_talk",
            variable=self.mode_var,
            font=("Segoe UI", 10, "bold")
        )
        self.rb2.pack(anchor="w")

        self.desc2 = tk.Label(
            self.sec_modes,
            text="   " + self._t("mode_ptt_desc"),
            font=("Segoe UI", 8),
            justify="left",
            wraplength=460
        )
        self.desc2.pack(anchor="w", pady=(0, 6))

        self.sep2 = tk.Frame(self.sec_modes, height=1)
        self.sep2.pack(fill="x", pady=5)

        # Mode 3: Toggle
        self.rb3 = tk.Radiobutton(
            self.sec_modes,
            text=self._t("mode_toggle"),
            value="toggle",
            variable=self.mode_var,
            font=("Segoe UI", 10, "bold")
        )
        self.rb3.pack(anchor="w")

        self.desc3 = tk.Label(
            self.sec_modes,
            text="   " + self._t("mode_toggle_desc"),
            font=("Segoe UI", 8),
            justify="left",
            wraplength=460
        )
        self.desc3.pack(anchor="w", pady=(0, 4))

        # --- Section 2: Language, Theme & Options ---
        self.sec_opt = tk.LabelFrame(
            self.content, 
            text=self._t("sec_pref"), 
            font=("Segoe UI", 10, "bold"), 
            padx=14, 
            pady=10,
            highlightthickness=1
        )
        self.sec_opt.pack(fill="x", pady=(0, 10))

        # Language Row
        lang_row = tk.Frame(self.sec_opt)
        lang_row.pack(fill="x", pady=(0, 8))
        self.lang_row = lang_row

        self.lbl_lang = tk.Label(lang_row, text=self._t("lang_lbl"), font=("Segoe UI", 9, "bold"))
        self.lbl_lang.pack(side="left")

        current_name = self.code_to_name.get(self.lang_var.get(), ALL_LANGUAGES[0][0])
        self.combo_var = tk.StringVar(value=current_name)

        self.combo = ttk.Combobox(
            lang_row,
            textvariable=self.combo_var,
            values=[name for name, _ in ALL_LANGUAGES],
            state="readonly",
            width=28
        )
        self.combo.pack(side="right")
        self.combo.bind("<<ComboboxSelected>>", self._on_language_changed)

        # Theme Row (Dark / Light Switcher)
        theme_row = tk.Frame(self.sec_opt)
        theme_row.pack(fill="x", pady=(0, 8))
        self.theme_row = theme_row

        self.lbl_theme = tk.Label(theme_row, text=self._t("theme_lbl"), font=("Segoe UI", 9, "bold"))
        self.lbl_theme.pack(side="left")

        theme_btn_box = tk.Frame(theme_row)
        theme_btn_box.pack(side="right")
        self.theme_btn_box = theme_btn_box

        self.rb_dark = tk.Radiobutton(
            theme_btn_box,
            text=self._t("theme_dark"),
            value="dark",
            variable=self.theme_var,
            font=("Segoe UI", 9),
            command=self._apply_theme
        )
        self.rb_dark.pack(side="left", padx=(0, 8))

        self.rb_light = tk.Radiobutton(
            theme_btn_box,
            text=self._t("theme_light"),
            value="light",
            variable=self.theme_var,
            font=("Segoe UI", 9),
            command=self._apply_theme
        )
        self.rb_light.pack(side="left")

        # Sound & Badge Checkboxes
        self.cb_sound = tk.Checkbutton(
            self.sec_opt, 
            text=self._t("sound_cb"), 
            variable=self.sound_var, 
            font=("Segoe UI", 9)
        )
        self.cb_sound.pack(anchor="w", pady=(0, 2))

        self.cb_badge = tk.Checkbutton(
            self.sec_opt, 
            text=self._t("badge_cb"), 
            variable=self.badge_var, 
            font=("Segoe UI", 9)
        )
        self.cb_badge.pack(anchor="w")

        # --- Bottom Action Bar ---
        self.btn_frame = tk.Frame(self.win, padx=24, pady=14)
        self.btn_frame.pack(fill="x", side="bottom")

        self.btn_start = tk.Button(
            self.btn_frame, 
            text=self._t("start_btn"), 
            font=("Segoe UI", 10, "bold"), 
            relief="flat", 
            padx=18, 
            pady=7,
            command=self._start_and_minimize
        )
        self.btn_start.pack(side="right")

        self.credit_lbl = tk.Label(
            self.btn_frame, 
            text="by Ruhvi2026 • F8", 
            font=("Segoe UI", 8)
        )
        self.credit_lbl.pack(side="left")

    def _on_language_changed(self, event=None):
        selected_name = self.combo_var.get()
        code = self.lang_map.get(selected_name, "bn-IN")
        self.lang_var.set(code)
        # Dynamically refresh all UI strings to match selected language!
        self._refresh_i18n()

    def _refresh_i18n(self):
        """Refreshes all on-screen text to match the active language."""
        self.title_lbl.config(text=self._t("app_title"))
        self.sub_lbl.config(text=self._t("subtitle"))
        self.sec_modes.config(text=self._t("sec_mode"))
        self.rb1.config(text=self._t("mode_auto"))
        self.desc1.config(text="   " + self._t("mode_auto_desc"))
        self.lbl_silence.config(text=self._t("silence_lbl"))
        self.lbl_sec.config(text=self._t("sec_unit"))
        self.rb2.config(text=self._t("mode_ptt"))
        self.desc2.config(text="   " + self._t("mode_ptt_desc"))
        self.rb3.config(text=self._t("mode_toggle"))
        self.desc3.config(text="   " + self._t("mode_toggle_desc"))
        self.sec_opt.config(text=self._t("sec_pref"))
        self.lbl_lang.config(text=self._t("lang_lbl"))
        self.lbl_theme.config(text=self._t("theme_lbl"))
        self.rb_dark.config(text=self._t("theme_dark"))
        self.rb_light.config(text=self._t("theme_light"))
        self.cb_sound.config(text=self._t("sound_cb"))
        self.cb_badge.config(text=self._t("badge_cb"))
        self.btn_start.config(text=self._t("start_btn"))

    def _apply_theme(self):
        """Applies active Dark or Light theme palette across all components."""
        theme_key = self.theme_var.get()
        c = THEMES.get(theme_key, THEMES["dark"])

        self.win.configure(bg=c["bg"])
        self.header.configure(bg=c["header_bg"])
        self.title_lbl.configure(bg=c["header_bg"], fg=c["text"])
        self.sub_lbl.configure(bg=c["header_bg"], fg=c["subtext"])

        self.content.configure(bg=c["bg"])

        # Section 1
        self.sec_modes.configure(bg=c["bg"], fg=c["accent"], highlightbackground=c["border"])
        self.rb1.configure(bg=c["bg"], fg=c["success"], selectcolor=c["select"], activebackground=c["bg"])
        self.desc1.configure(bg=c["bg"], fg=c["text"])
        self.silence_frame.configure(bg=c["bg"])
        self.lbl_silence.configure(bg=c["bg"], fg=c["subtext"])
        self.slider.configure(bg=c["bg"], fg=c["success"], troughcolor=c["trough"])
        self.lbl_sec.configure(bg=c["bg"], fg=c["subtext"])
        self.sep1.configure(bg=c["sep"])

        self.rb2.configure(bg=c["bg"], fg=c["text"], selectcolor=c["select"], activebackground=c["bg"])
        self.desc2.configure(bg=c["bg"], fg=c["subtext"])
        self.sep2.configure(bg=c["sep"])

        self.rb3.configure(bg=c["bg"], fg=c["text"], selectcolor=c["select"], activebackground=c["bg"])
        self.desc3.configure(bg=c["bg"], fg=c["subtext"])

        # Section 2
        self.sec_opt.configure(bg=c["bg"], fg=c["accent"], highlightbackground=c["border"])
        self.lang_row.configure(bg=c["bg"])
        self.lbl_lang.configure(bg=c["bg"], fg=c["text"])

        self.theme_row.configure(bg=c["bg"])
        self.lbl_theme.configure(bg=c["bg"], fg=c["text"])
        self.theme_btn_box.configure(bg=c["bg"])
        self.rb_dark.configure(bg=c["bg"], fg=c["text"], selectcolor=c["select"], activebackground=c["bg"])
        self.rb_light.configure(bg=c["bg"], fg=c["text"], selectcolor=c["select"], activebackground=c["bg"])

        self.cb_sound.configure(bg=c["bg"], fg=c["text"], selectcolor=c["select"], activebackground=c["bg"])
        self.cb_badge.configure(bg=c["bg"], fg=c["text"], selectcolor=c["select"], activebackground=c["bg"])

        # Footer
        self.btn_frame.configure(bg=c["header_bg"])
        self.btn_start.configure(bg=c["btn_bg"], fg=c["btn_fg"])
        self.credit_lbl.configure(bg=c["header_bg"], fg=c["subtext"])

    def _apply_data(self):
        new_lang_code = self.lang_map.get(self.combo_var.get(), "bn-IN")
        self.settings["mode"] = self.mode_var.get()
        self.settings["language"] = new_lang_code
        self.settings["theme"] = self.theme_var.get()
        self.settings["sound_effects"] = self.sound_var.get()
        self.settings["floating_badge"] = self.badge_var.get()
        self.settings["auto_paste"] = self.paste_var.get()
        self.settings["silence_seconds"] = round(float(self.silence_var.get()), 1)
        save_settings(self.settings)
        if self.on_save_cb:
            self.on_save_cb(self.settings)

    def _start_and_minimize(self):
        self._apply_data()
        self.win.withdraw()
        if self.on_min_cb:
            self.on_min_cb()

    def _on_close(self):
        self._apply_data()
        self.win.withdraw()
        if self.on_min_cb:
            self.on_min_cb()

    def show(self):
        self.settings = load_settings()
        self.mode_var.set(self.settings.get("mode", "auto_stop"))
        self.lang_var.set(self.settings.get("language", "bn-IN"))
        self.theme_var.set(self.settings.get("theme", "dark"))
        self.combo_var.set(self.code_to_name.get(self.settings.get("language", "bn-IN"), ALL_LANGUAGES[0][0]))
        self.silence_var.set(self.settings.get("silence_seconds", 3.2))
        self.sound_var.set(self.settings.get("sound_effects", True))
        self.badge_var.set(self.settings.get("floating_badge", True))
        self._apply_theme()
        self._refresh_i18n()
        self.win.deiconify()
        self.win.lift()
        self.win.focus_force()

if __name__ == "__main__":
    app = SettingsUI()
    app.win.mainloop()
