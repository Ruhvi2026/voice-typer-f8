"""
Voice Typer Pro - Professional Modern Control Center
Built with CustomTkinter for sleek macOS / Windows 11 Fluent aesthetic.
Supports 125+ Global Languages with Instant Search & Smooth Scrollable Palette.
Author: Ruhvi2026 (Project Ruhvi)
"""

import os
import json
import tkinter as tk
import customtkinter as ctk

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


class LanguagePickerModal(ctk.CTkToplevel):
    """
    A sleek, Raycast/Command-Palette style modal for browsing & searching 125+ languages.
    Provides instant live filtering and smooth mousewheel scrolling.
    """
    def __init__(self, parent, current_lang_code, on_select_callback):
        super().__init__(parent)
        self.on_select = on_select_callback
        self.current_code = current_lang_code
        self.all_languages = ALL_LANGUAGES

        self.title("🌐 Language Selector — 125+ Languages")
        self.geometry("500x580")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        # Center on parent window
        self.update_idletasks()
        try:
            px = parent.winfo_x()
            py = parent.winfo_y()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = px + max(0, (pw - 500) // 2)
            y = py + max(0, (ph - 580) // 2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

        self._build_modal()
        self.focus_force()

    def _build_modal(self):
        # Header container
        header = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray95", "#0f172a"))
        header.pack(fill="x", padx=16, pady=(16, 8))

        title = ctk.CTkLabel(
            header,
            text="🌐 Select Speech Recognition Language",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 2))

        subtitle = ctk.CTkLabel(
            header,
            text="Type any language, country, or code to filter instantly",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray50", "gray60")
        )
        subtitle.pack(anchor="w", pady=(0, 10))

        # Real-time search entry bar
        self.search_entry = ctk.CTkEntry(
            header,
            placeholder_text="🔍 Type to search (e.g. Bengali, Hindi, Spanish, Arabic, de, ja...)",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=38,
            corner_radius=8
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self._on_search_query_changed)
        self.search_entry.focus_set()

        # Results Count Label
        self.count_lbl = ctk.CTkLabel(
            self,
            text=f"Showing all {len(self.all_languages)} supported languages & dialects",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=("gray50", "gray60")
        )
        self.count_lbl.pack(anchor="w", padx=20, pady=(4, 6))

        # Smooth Mousewheel Scrollable Frame
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=10,
            fg_color=("white", "#1e293b")
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Populate initial list
        self._populate_list(self.all_languages)

    def _on_search_query_changed(self, event=None):
        query = self.search_entry.get().strip().lower()
        if not query:
            filtered = self.all_languages
        else:
            filtered = [
                (name, code) for name, code in self.all_languages
                if query in name.lower() or query in code.lower()
            ]
        self._populate_list(filtered)

    def _populate_list(self, languages):
        # Clear existing rows
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.count_lbl.configure(text=f"Showing {len(languages)} matching language(s)")

        if not languages:
            no_match = ctk.CTkLabel(
                self.scroll_frame,
                text="❌ No matching language found. Try another search term.",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=("gray50", "gray60"),
                pady=40
            )
            no_match.pack()
            return

        for name, code in languages:
            is_active = (code == self.current_code)
            
            # Row Container
            row_btn = ctk.CTkButton(
                self.scroll_frame,
                text=f"{name}  [{code}]",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold" if is_active else "normal"),
                anchor="w",
                fg_color=("#dcfce7", "#14532d") if is_active else "transparent",
                text_color=("#15803d", "#86efac") if is_active else ("gray15", "#f8fafc"),
                hover_color=("#e2e8f0", "#334155"),
                height=36,
                corner_radius=6,
                command=lambda c=code: self._pick_language(c)
            )
            row_btn.pack(fill="x", pady=2, padx=4)

    def _pick_language(self, code):
        self.on_select(code)
        self.destroy()


class SettingsUI:
    def __init__(self, root=None, on_save_callback=None, on_minimize_callback=None):
        self.settings = load_settings()
        self.on_save_cb = on_save_callback
        self.on_min_cb = on_minimize_callback

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

        self.all_languages = ALL_LANGUAGES
        self.code_to_name = {code: name for name, code in self.all_languages}

        # Active state
        self.current_mode = self.settings.get("mode", "auto_stop")
        self.current_lang = self.settings.get("language", "bn-IN")
        self.current_theme = initial_theme
        self.silence_val = self.settings.get("silence_seconds", 3.2)
        self.picker_modal = None

        self._build_ui()
        self._refresh_i18n()
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

    def _t(self, key):
        return get_ui_text(self.current_lang, key)

    def _build_ui(self):
        self.main_container = ctk.CTkFrame(self.win, corner_radius=0, fg_color=("gray95", "#0f172a"))
        self.main_container.pack(fill="both", expand=True)

        # --- 1. Top Header Bar ---
        header_frame = ctk.CTkFrame(self.main_container, corner_radius=12, fg_color=("white", "#1e293b"))
        header_frame.pack(fill="x", padx=16, pady=(16, 10))

        header_inner = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_inner.pack(fill="x", padx=16, pady=12)

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

        self.mode_segment = ctk.CTkSegmentedButton(
            mode_inner,
            values=["⚡ Auto-Stop", "🎙️ Push-to-Talk", "🔄 Toggle"],
            command=self._on_mode_segment_changed,
            corner_radius=8,
            height=34
        )
        seg_init = {
            "auto_stop": "⚡ Auto-Stop",
            "push_to_talk": "🎙️ Push-to-Talk",
            "toggle": "🔄 Toggle"
        }.get(self.current_mode, "⚡ Auto-Stop")
        self.mode_segment.set(seg_init)
        self.mode_segment.pack(fill="x", pady=(0, 10))

        # Explanation Banner
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

        # Silence Slider
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

        # --- 3. Card: Speech Language (125+ Languages Palette) ---
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

        # Active Language Display + Change Button
        lang_display_bar = ctk.CTkFrame(lang_inner, corner_radius=8, fg_color=("gray92", "#0f172a"))
        lang_display_bar.pack(fill="x", pady=(0, 8))

        active_lang_box = ctk.CTkFrame(lang_display_bar, fg_color="transparent")
        active_lang_box.pack(side="left", padx=12, pady=8)

        self.active_lang_tag = ctk.CTkLabel(
            active_lang_box,
            text=self._t("current_active"),
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=("gray50", "gray60")
        )
        self.active_lang_tag.pack(anchor="w")

        self.active_lang_title = ctk.CTkLabel(
            active_lang_box,
            text=self.code_to_name.get(self.current_lang, self.current_lang),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=("#16a34a", "#4ade80")
        )
        self.active_lang_title.pack(anchor="w")

        # Browse Modal Trigger Button
        self.btn_browse_lang = ctk.CTkButton(
            lang_display_bar,
            text=self._t("change_lang_btn"),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=("#2563eb", "#3b82f6"),
            hover_color=("#1d4ed8", "#2563eb"),
            height=34,
            corner_radius=6,
            command=self._open_language_modal
        )
        self.btn_browse_lang.pack(side="right", padx=10, pady=8)

        # Quick Select Chips Row
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

    def _open_language_modal(self):
        """Opens the full-featured searchable Language Picker Modal."""
        if self.picker_modal and self.picker_modal.winfo_exists():
            self.picker_modal.focus_force()
            return
        self.picker_modal = LanguagePickerModal(
            parent=self.win,
            current_lang_code=self.current_lang,
            on_select_callback=self._select_language_code
        )

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

    def _select_language_code(self, code):
        self.current_lang = code
        display_name = self.code_to_name.get(code, code)
        self.active_lang_title.configure(text=display_name)
        self._refresh_i18n()
        self._apply_data()

    def _refresh_i18n(self):
        """Dynamically re-renders all UI strings to match selected language."""
        self.title_label.configure(text=self._t("app_title"))
        self.subtitle_label.configure(text=self._t("subtitle"))
        self.mode_header_lbl.configure(text=self._t("sec_mode"))
        self._refresh_mode_description()
        self.silence_label.configure(text=f"{self._t('silence_lbl')} {self.silence_val} {self._t('sec_unit')}")
        self.lang_header_lbl.configure(text=self._t("sec_pref"))
        self.active_lang_tag.configure(text=self._t("current_active"))
        self.active_lang_title.configure(text=self.code_to_name.get(self.current_lang, self.current_lang))
        self.btn_browse_lang.configure(text=self._t("change_lang_btn"))
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
        self.active_lang_title.configure(text=self.code_to_name.get(self.current_lang, self.current_lang))
        self.silence_slider.set(self.silence_val)
        self._refresh_i18n()
        self.win.deiconify()
        self.win.lift()
        self.win.focus_force()

if __name__ == "__main__":
    app = SettingsUI()
    app.win.mainloop()
