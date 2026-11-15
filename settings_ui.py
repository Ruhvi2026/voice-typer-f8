"""
Voice Typer Pro - Professional Modern Control Center
Built with CustomTkinter for sleek macOS / Windows 11 Fluent aesthetic.
Supports 125+ Global Languages, Dynamic i18n, and Dark/Light Modes.
Author: Ruhvi2026 (Project Ruhvi)
"""

import os
import json
import tkinter as tk
import customtkinter as ctk
from PIL import Image

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

        # Set initial appearance mode
        initial_theme = self.settings.get("theme", "dark")
        ctk.set_appearance_mode(initial_theme)
        ctk.set_default_color_theme("blue")

        if root:
            self.win = root
        else:
            self.win = ctk.CTk()

        self.win.title("Voice Typer Pro — Desktop Speech Hub")
        self.win.geometry("560x710")
        self.win.resizable(False, False)

        icon_path = os.path.join(APP_DIR, "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.win.iconbitmap(icon_path)
            except Exception:
                pass

        # Language catalogs
        self.all_languages = ALL_LANGUAGES
        self.lang_map = {name: code for name, code in self.all_languages}
        self.code_to_name = {code: name for name, code in self.all_languages}

        # Active settings state
        self.current_mode = self.settings.get("mode", "auto_stop")
        self.current_lang = self.settings.get("language", "bn-IN")
        self.current_theme = initial_theme
        self.silence_val = self.settings.get("silence_seconds", 3.2)

        self._build_ui()
        self._refresh_i18n()
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

    def _t(self, key):
        return get_ui_text(self.current_lang, key)

    def _build_ui(self):
        # Main container with padding
        self.main_container = ctk.CTkFrame(self.win, corner_radius=0, fg_color=("gray95", "#0f172a"))
        self.main_container.pack(fill="both", expand=True)

        # --- 1. Top Header Bar ---
        header_frame = ctk.CTkFrame(self.main_container, corner_radius=12, fg_color=("white", "#1e293b"))
        header_frame.pack(fill="x", padx=16, pady=(16, 10))

        header_inner = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_inner.pack(fill="x", padx=16, pady=12)

        # Branding
        brand_left = ctk.CTkFrame(header_inner, fg_color="transparent")
        brand_left.pack(side="left")

        title_row = ctk.CTkFrame(brand_left, fg_color="transparent")
        title_row.pack(anchor="w")

        self.title_label = ctk.CTkLabel(
            title_row,
            text=self._t("app_title"),
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        )
        self.title_label.pack(side="left", padx=(0, 8))

        # Version Pill
        ver_pill = ctk.CTkLabel(
            title_row,
            text="v2.0 PRO",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color=("#e2e8f0", "#334155"),
            text_color=("#475569", "#94a3b8"),
            corner_radius=6,
            padx=6,
            pady=2
        )
        ver_pill.pack(side="left")

        self.subtitle_label = ctk.CTkLabel(
            brand_left,
            text=self._t("subtitle"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray50", "gray60")
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0))

        # Theme Selector Segmented
        self.theme_seg = ctk.CTkSegmentedButton(
            header_inner,
            values=["🌙 Dark", "☀️ Light"],
            command=self._on_theme_toggle,
            width=140,
            corner_radius=8
        )
        self.theme_seg.set("🌙 Dark" if self.current_theme == "dark" else "☀️ Light")
        self.theme_seg.pack(side="right")

        # --- 2. Card: Recording Mode ---
        self.mode_card = ctk.CTkFrame(self.main_container, corner_radius=12, fg_color=("white", "#1e293b"))
        self.mode_card.pack(fill="x", padx=16, pady=6)

        mode_inner = ctk.CTkFrame(self.mode_card, fg_color="transparent")
        mode_inner.pack(fill="x", padx=16, pady=12)

        self.mode_header_lbl = ctk.CTkLabel(
            mode_inner,
            text=self._t("sec_mode"),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=("#2563eb", "#60a5fa")
        )
        self.mode_header_lbl.pack(anchor="w", pady=(0, 8))

        # Modern Segmented Mode Button
        self.mode_segment = ctk.CTkSegmentedButton(
            mode_inner,
            values=["⚡ Auto-Stop", "🎙️ Push-to-Talk", "🔄 Toggle"],
            command=self._on_mode_segment_changed,
            corner_radius=8,
            height=34
        )
        # Map internal mode to label
        seg_init = {
            "auto_stop": "⚡ Auto-Stop",
            "push_to_talk": "🎙️ Push-to-Talk",
            "toggle": "🔄 Toggle"
        }.get(self.current_mode, "⚡ Auto-Stop")
        self.mode_segment.set(seg_init)
        self.mode_segment.pack(fill="x", pady=(0, 10))

        # Interactive Mode Explanation Banner
        self.mode_info_box = ctk.CTkFrame(mode_inner, corner_radius=8, fg_color=("gray92", "#0f172a"))
        self.mode_info_box.pack(fill="x", pady=(0, 6))

        self.mode_desc_lbl = ctk.CTkLabel(
            self.mode_info_box,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            justify="left",
            wraplength=480
        )
        self.mode_desc_lbl.pack(anchor="w", padx=12, pady=8)

        # Silence Slider (visible in auto_stop)
        self.slider_container = ctk.CTkFrame(mode_inner, fg_color="transparent")
        self.slider_container.pack(fill="x", pady=(4, 0))

        self.silence_label = ctk.CTkLabel(
            self.slider_container,
            text=f"{self._t('silence_lbl')} {self.silence_val} {self._t('sec_unit')}",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")
        )
        self.silence_label.pack(side="left")

        self.silence_slider = ctk.CTkSlider(
            self.slider_container,
            from_=2.0,
            to=5.5,
            number_of_steps=18,
            command=self._on_slider_change,
            width=220
        )
        self.silence_slider.set(self.silence_val)
        self.silence_slider.pack(side="right")

        # --- 3. Card: Speech Language (125+ Languages) ---
        self.lang_card = ctk.CTkFrame(self.main_container, corner_radius=12, fg_color=("white", "#1e293b"))
        self.lang_card.pack(fill="x", padx=16, pady=6)

        lang_inner = ctk.CTkFrame(self.lang_card, fg_color="transparent")
        lang_inner.pack(fill="x", padx=16, pady=12)

        self.lang_header_lbl = ctk.CTkLabel(
            lang_inner,
            text=self._t("sec_pref"),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=("#2563eb", "#60a5fa")
        )
        self.lang_header_lbl.pack(anchor="w", pady=(0, 6))

        # Search / Filter Bar + OptionMenu
        lang_select_row = ctk.CTkFrame(lang_inner, fg_color="transparent")
        lang_select_row.pack(fill="x", pady=(0, 8))

        self.lang_search_entry = ctk.CTkEntry(
            lang_select_row,
            placeholder_text=self._t("search_placeholder"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            height=32,
            width=210
        )
        self.lang_search_entry.pack(side="left", padx=(0, 8))
        self.lang_search_entry.bind("<KeyRelease>", self._filter_languages)

        current_lang_display = self.code_to_name.get(self.current_lang, self.all_languages[0][0])
        self.lang_dropdown = ctk.CTkOptionMenu(
            lang_select_row,
            values=[name for name, _ in self.all_languages[:35]],
            command=self._on_dropdown_selected,
            height=32,
            dynamic_resizing=False,
            width=270
        )
        self.lang_dropdown.set(current_lang_display)
        self.lang_dropdown.pack(side="right", fill="x", expand=True)

        # Quick Select Chips
        chips_frame = ctk.CTkFrame(lang_inner, fg_color="transparent")
        chips_frame.pack(fill="x")

        self.quick_lbl = ctk.CTkLabel(
            chips_frame,
            text=self._t("quick_label"),
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=("gray50", "gray60")
        )
        self.quick_lbl.pack(side="left", padx=(0, 6))

        quick_presets = [
            ("বাংলা (ভারত)", "bn-IN"),
            ("বাংলা (BD)", "bn-BD"),
            ("English", "en-IN"),
            ("हिन्दी", "hi-IN"),
            ("Español", "es-ES"),
            ("Français", "fr-FR")
        ]
        for label, code in quick_presets:
            btn = ctk.CTkButton(
                chips_frame,
                text=label,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                fg_color=("gray85", "#334155"),
                text_color=("gray10", "#f8fafc"),
                hover_color=("#2563eb", "#3b82f6"),
                height=22,
                width=55,
                corner_radius=6,
                command=lambda c=code: self._select_language_code(c)
            )
            btn.pack(side="left", padx=2)

        # --- 4. Card: Switches (Preferences) ---
        self.pref_card = ctk.CTkFrame(self.main_container, corner_radius=12, fg_color=("white", "#1e293b"))
        self.pref_card.pack(fill="x", padx=16, pady=6)

        pref_inner = ctk.CTkFrame(self.pref_card, fg_color="transparent")
        pref_inner.pack(fill="x", padx=16, pady=10)

        self.sound_switch = ctk.CTkSwitch(
            pref_inner,
            text=self._t("sound_cb"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            onvalue=True,
            offvalue=False,
            command=self._apply_data
        )
        if self.settings.get("sound_effects", True):
            self.sound_switch.select()
        else:
            self.sound_switch.deselect()
        self.sound_switch.pack(anchor="w", pady=2)

        self.badge_switch = ctk.CTkSwitch(
            pref_inner,
            text=self._t("badge_cb"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            onvalue=True,
            offvalue=False,
            command=self._apply_data
        )
        if self.settings.get("floating_badge", True):
            self.badge_switch.select()
        else:
            self.badge_switch.deselect()
        self.badge_switch.pack(anchor="w", pady=2)

        self.paste_switch = ctk.CTkSwitch(
            pref_inner,
            text=self._t("paste_cb"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            onvalue=True,
            offvalue=False,
            command=self._apply_data
        )
        if self.settings.get("auto_paste", True):
            self.paste_switch.select()
        else:
            self.paste_switch.deselect()
        self.paste_switch.pack(anchor="w", pady=2)

        # --- 5. Bottom Action & Status Footer ---
        footer_frame = ctk.CTkFrame(self.main_container, corner_radius=12, fg_color=("white", "#1e293b"))
        footer_frame.pack(fill="x", padx=16, pady=(6, 16))

        footer_inner = ctk.CTkFrame(footer_frame, fg_color="transparent")
        footer_inner.pack(fill="x", padx=16, pady=12)

        # Status indicator
        status_box = ctk.CTkFrame(footer_inner, fg_color="transparent")
        status_box.pack(side="left")

        self.status_lbl = ctk.CTkLabel(
            status_box,
            text=self._t("status_ready"),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("#16a34a", "#4ade80")
        )
        self.status_lbl.pack(anchor="w")

        credit_lbl = ctk.CTkLabel(
            status_box,
            text="Developed by Ruhvi2026 • Project Ruhvi",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=("gray50", "gray55")
        )
        credit_lbl.pack(anchor="w")

        # Primary Launch Button
        self.btn_start = ctk.CTkButton(
            footer_inner,
            text=self._t("start_btn"),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=("#22c55e", "#16a34a"),
            hover_color=("#16a34a", "#15803d"),
            height=38,
            corner_radius=8,
            command=self._start_and_minimize
        )
        self.btn_start.pack(side="right")

    def _on_theme_toggle(self, selected):
        theme = "dark" if "Dark" in selected else "light"
        self.current_theme = theme
        ctk.set_appearance_mode(theme)
        self._apply_data()

    def _on_mode_segment_changed(self, selected):
        if "Auto" in selected:
            self.current_mode = "auto_stop"
        elif "Push" in selected:
            self.current_mode = "push_to_talk"
        else:
            self.current_mode = "toggle"

        self._refresh_mode_description()
        self._apply_data()

    def _refresh_mode_description(self):
        if self.current_mode == "auto_stop":
            desc = self._t("mode_auto_desc")
            self.slider_container.pack(fill="x", pady=(4, 0))
        elif self.current_mode == "push_to_talk":
            desc = self._t("mode_ptt_desc")
            self.slider_container.pack_forget()
        else:
            desc = self._t("mode_toggle_desc")
            self.slider_container.pack_forget()
        self.mode_desc_lbl.configure(text=desc)

    def _on_slider_change(self, val):
        self.silence_val = round(float(val), 1)
        self.silence_label.configure(text=f"{self._t('silence_lbl')} {self.silence_val} {self._t('sec_unit')}")
        self._apply_data()

    def _on_dropdown_selected(self, selected_name):
        code = self.lang_map.get(selected_name, "bn-IN")
        self._select_language_code(code)

    def _select_language_code(self, code):
        self.current_lang = code
        display_name = self.code_to_name.get(code, code)
        self.lang_dropdown.set(display_name)
        self._refresh_i18n()
        self._apply_data()

    def _filter_languages(self, event=None):
        query = self.lang_search_entry.get().strip().lower()
        if not query:
            filtered = [name for name, _ in self.all_languages[:40]]
        else:
            filtered = [name for name, code in self.all_languages if query in name.lower() or query in code.lower()]
            if not filtered:
                filtered = [self.code_to_name.get(self.current_lang, "No match")]
        self.lang_dropdown.configure(values=filtered[:50])

    def _refresh_i18n(self):
        """Dynamically re-renders all UI strings to match selected language."""
        self.title_label.configure(text=self._t("app_title"))
        self.subtitle_label.configure(text=self._t("subtitle"))
        self.mode_header_lbl.configure(text=self._t("sec_mode"))
        self._refresh_mode_description()
        self.silence_label.configure(text=f"{self._t('silence_lbl')} {self.silence_val} {self._t('sec_unit')}")
        self.lang_header_lbl.configure(text=self._t("sec_pref"))
        self.lang_search_entry.configure(placeholder_text=self._t("search_placeholder"))
        self.quick_lbl.configure(text=self._t("quick_label"))
        self.sound_switch.configure(text=self._t("sound_cb"))
        self.badge_switch.configure(text=self._t("badge_cb"))
        self.paste_switch.configure(text=self._t("paste_cb"))
        self.status_lbl.configure(text=self._t("status_ready"))
        self.btn_start.configure(text=self._t("start_btn"))

    def _apply_data(self):
        self.settings["mode"] = self.current_mode
        self.settings["language"] = self.current_lang
        self.settings["theme"] = self.current_theme
        self.settings["sound_effects"] = bool(self.sound_switch.get())
        self.settings["floating_badge"] = bool(self.badge_switch.get())
        self.settings["auto_paste"] = bool(self.paste_switch.get())
        self.settings["silence_seconds"] = self.silence_val
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
        self.current_mode = self.settings.get("mode", "auto_stop")
        self.current_lang = self.settings.get("language", "bn-IN")
        self.current_theme = self.settings.get("theme", "dark")
        self.silence_val = self.settings.get("silence_seconds", 3.2)
        ctk.set_appearance_mode(self.current_theme)
        self.theme_seg.set("🌙 Dark" if self.current_theme == "dark" else "☀️ Light")
        seg_init = {
            "auto_stop": "⚡ Auto-Stop",
            "push_to_talk": "🎙️ Push-to-Talk",
            "toggle": "🔄 Toggle"
        }.get(self.current_mode, "⚡ Auto-Stop")
        self.mode_segment.set(seg_init)
        self.lang_dropdown.set(self.code_to_name.get(self.current_lang, self.all_languages[0][0]))
        self.silence_slider.set(self.silence_val)
        self._refresh_i18n()
        self.win.deiconify()
        self.win.lift()
        self.win.focus_force()

if __name__ == "__main__":
    app = SettingsUI()
    app.win.mainloop()
