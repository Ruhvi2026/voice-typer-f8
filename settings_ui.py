"""
Bangla Voice Typer - Settings & Control Center
Author: Ruhvi2026 (Project Ruhvi)
"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(APP_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "mode": "auto_stop",     # "auto_stop" (Default), "push_to_talk", "toggle"
    "language": "bn-IN",     # "bn-IN", "bn-BD", "en-IN", "en-US", "hi-IN"
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

        if root:
            self.win = root
        else:
            self.win = tk.Tk()

        self.win.title("🎙️ Bangla Voice Typer — কন্ট্রোল সেন্টার")
        self.win.geometry("520x680")
        self.win.resizable(False, False)
        self.win.configure(bg="#181825")

        # Set window icon
        icon_path = os.path.join(APP_DIR, "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.win.iconbitmap(icon_path)
            except Exception:
                pass

        # Variables
        self.mode_var = tk.StringVar(value=self.settings.get("mode", "auto_stop"))
        self.lang_var = tk.StringVar(value=self.settings.get("language", "bn-IN"))
        self.sound_var = tk.BooleanVar(value=self.settings.get("sound_effects", True))
        self.badge_var = tk.BooleanVar(value=self.settings.get("floating_badge", True))
        self.paste_var = tk.BooleanVar(value=self.settings.get("auto_paste", True))
        self.silence_var = tk.DoubleVar(value=self.settings.get("silence_seconds", 3.2))

        self._build_ui()
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        # Header banner
        header = tk.Frame(self.win, bg="#11111b", padx=24, pady=18)
        header.pack(fill="x")

        title = tk.Label(
            header, 
            text="🎙️ Bangla Voice Typer", 
            font=("Segoe UI", 16, "bold"), 
            bg="#11111b", 
            fg="#cdd6f4"
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header, 
            text="যেভাবে কথা বলতে চান সেই মোডটি সিলেক্ট করুন এবং স্টার্ট করুন", 
            font=("Segoe UI", 9), 
            bg="#11111b", 
            fg="#a6adc8"
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        content = tk.Frame(self.win, bg="#181825", padx=24, pady=16)
        content.pack(fill="both", expand=True)

        # Section 1: Modes (Prominent Selection Cards)
        sec_modes = tk.LabelFrame(
            content, 
            text=" 🎯 ব্যবহার করার নিয়ম (৩টি মোড) ", 
            font=("Segoe UI", 10, "bold"), 
            bg="#181825", 
            fg="#89b4fa", 
            padx=14, 
            pady=12,
            highlightthickness=1,
            highlightbackground="#313244"
        )
        sec_modes.pack(fill="x", pady=(0, 14))

        # Mode 1: Auto-Stop (Default)
        rb1 = tk.Radiobutton(
            sec_modes,
            text="⭐ মোড ১: Auto-Stop (ডিফল্ট ও সহজতম)",
            value="auto_stop",
            variable=self.mode_var,
            font=("Segoe UI", 10, "bold"),
            bg="#181825",
            fg="#a6e3a1",
            selectcolor="#11111b",
            activebackground="#181825",
            activeforeground="#a6e3a1"
        )
        rb1.pack(anchor="w")
        desc1 = tk.Label(
            sec_modes,
            text="   👉 একবার F8 চাপবেন, কথা বলবেন। আপনি কথা শেষ করে থামলে\n      স্বয়ংক্রিয়ভাবে রেকর্ড বন্ধ হয়ে টেক্সটে কনভার্ট ও পেস্ট হয়ে যাবে।",
            font=("Segoe UI", 8),
            justify="left",
            bg="#181825",
            fg="#cdd6f4"
        )
        desc1.pack(anchor="w", pady=(0, 4))

        # Silence slider for Auto-Stop
        silence_frame = tk.Frame(sec_modes, bg="#181825", padx=16)
        silence_frame.pack(fill="x", pady=(0, 8))
        
        lbl_silence = tk.Label(
            silence_frame, 
            text="থামার জন্য নীরবতা বিরতি:", 
            font=("Segoe UI", 8, "italic"), 
            bg="#181825", 
            fg="#a6adc8"
        )
        lbl_silence.pack(side="left")

        self.slider = tk.Scale(
            silence_frame, 
            from_=2.0, 
            to=5.5, 
            resolution=0.2, 
            orient="horizontal", 
            variable=self.silence_var,
            bg="#181825",
            fg="#a6e3a1",
            highlightthickness=0,
            troughcolor="#313244",
            length=140
        )
        self.slider.pack(side="left", padx=8)

        lbl_sec = tk.Label(silence_frame, text="সেকেন্ড", font=("Segoe UI", 8), bg="#181825", fg="#a6adc8")
        lbl_sec.pack(side="left")

        tk.Frame(sec_modes, height=1, bg="#313244").pack(fill="x", pady=6)

        # Mode 2: Push-to-Talk (Hold-to-Talk)
        rb2 = tk.Radiobutton(
            sec_modes,
            text="🔘 মোড ২: Push-to-Talk (টিপে ধরে রেখে কথা বলা)",
            value="push_to_talk",
            variable=self.mode_var,
            font=("Segoe UI", 10, "bold"),
            bg="#181825",
            fg="#cdd6f4",
            selectcolor="#11111b",
            activebackground="#181825",
            activeforeground="#89b4fa"
        )
        rb2.pack(anchor="w")
        desc2 = tk.Label(
            sec_modes,
            text="   👉 কীবোর্ডের F8 কি চেপে ধরে রেখে কথা বলুন।\n      কথা বলা শেষ হলে F8 ছেড়ে দিন—সাথে সাথে পেস্ট হবে।",
            font=("Segoe UI", 8),
            justify="left",
            bg="#181825",
            fg="#a6adc8"
        )
        desc2.pack(anchor="w", pady=(0, 8))

        tk.Frame(sec_modes, height=1, bg="#313244").pack(fill="x", pady=6)

        # Mode 3: Toggle Mode
        rb3 = tk.Radiobutton(
            sec_modes,
            text="🔘 মোড ৩: Toggle Mode (ম্যানুয়াল অন ও অফ)",
            value="toggle",
            variable=self.mode_var,
            font=("Segoe UI", 10, "bold"),
            bg="#181825",
            fg="#cdd6f4",
            selectcolor="#11111b",
            activebackground="#181825",
            activeforeground="#89b4fa"
        )
        rb3.pack(anchor="w")
        desc3 = tk.Label(
            sec_modes,
            text="   👉 একবার F8 চাপলে রেকর্ডিং শুরু হবে। যত ইচ্ছা ভাবুন, কাটবে না।\n      সব কথা শেষ হলে আবার F8 চাপলে বন্ধ হবে ও পেস্ট হবে।",
            font=("Segoe UI", 8),
            justify="left",
            bg="#181825",
            fg="#a6adc8"
        )
        desc3.pack(anchor="w", pady=(0, 4))

        # Section 2: Language & Preferences
        sec_opt = tk.LabelFrame(
            content, 
            text=" 🌐 ভাষা ও সাউন্ড ", 
            font=("Segoe UI", 10, "bold"), 
            bg="#181825", 
            fg="#89b4fa", 
            padx=14, 
            pady=10,
            highlightthickness=1,
            highlightbackground="#313244"
        )
        sec_opt.pack(fill="x", pady=(0, 10))

        lang_row = tk.Frame(sec_opt, bg="#181825")
        lang_row.pack(fill="x", pady=(0, 6))

        lbl_lang = tk.Label(lang_row, text="ভাষা নির্বাচন:", font=("Segoe UI", 9, "bold"), bg="#181825", fg="#cdd6f4")
        lbl_lang.pack(side="left")

        languages = [
            ("বাংলা (ভারত)", "bn-IN"),
            ("বাংলা (বাংলাদেশ)", "bn-BD"),
            ("English (India)", "en-IN"),
            ("English (United States)", "en-US"),
            ("हिन्दी (Hindi)", "hi-IN")
        ]
        self.lang_map = {name: code for name, code in languages}
        self.code_to_name = {code: name for name, code in languages}

        current_lang_name = self.code_to_name.get(self.lang_var.get(), "বাংলা (ভারত)")
        self.lang_combo_var = tk.StringVar(value=current_lang_name)

        combo = ttk.Combobox(
            lang_row, 
            textvariable=self.lang_combo_var, 
            values=list(self.lang_map.keys()),
            state="readonly",
            width=22
        )
        combo.pack(side="right")

        cb_sound = tk.Checkbutton(
            sec_opt, 
            text="🔊 মিষ্টি বিং সাউন্ড ইফেক্ট বাজবে", 
            variable=self.sound_var, 
            font=("Segoe UI", 9), 
            bg="#181825", 
            fg="#cdd6f4", 
            selectcolor="#11111b",
            activebackground="#181825"
        )
        cb_sound.pack(anchor="w")

        cb_badge = tk.Checkbutton(
            sec_opt, 
            text="💬 স্ক্রিনে ভাসমান নোটিফিকেশন ব্যাজ দেখাবে", 
            variable=self.badge_var, 
            font=("Segoe UI", 9), 
            bg="#181825", 
            fg="#cdd6f4", 
            selectcolor="#11111b",
            activebackground="#181825"
        )
        cb_badge.pack(anchor="w")

        # Bottom Bar: Start Button & Minimize
        btn_frame = tk.Frame(self.win, bg="#11111b", padx=24, pady=14)
        btn_frame.pack(fill="x", side="bottom")

        btn_start = tk.Button(
            btn_frame, 
            text="🚀 শুরু করুন ও ব্যাকগ্রাউন্ডে রাখুন", 
            font=("Segoe UI", 10, "bold"), 
            bg="#a6e3a1", 
            fg="#11111b", 
            activebackground="#94e2d5", 
            relief="flat", 
            padx=16, 
            pady=7,
            command=self._start_and_minimize
        )
        btn_start.pack(side="right")

        credit = tk.Label(
            btn_frame, 
            text="by Ruhvi2026 • F8 কী চাপুন", 
            font=("Segoe UI", 8), 
            bg="#11111b", 
            fg="#6c7086"
        )
        credit.pack(side="left")

    def _apply_data(self):
        new_lang_code = self.lang_map.get(self.lang_combo_var.get(), "bn-IN")
        self.settings["mode"] = self.mode_var.get()
        self.settings["language"] = new_lang_code
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
        # When clicking 'X', minimize to tray instead of closing app
        self._apply_data()
        self.win.withdraw()
        if self.on_min_cb:
            self.on_min_cb()

    def show(self):
        self.settings = load_settings()
        self.mode_var.set(self.settings.get("mode", "auto_stop"))
        self.lang_var.set(self.settings.get("language", "bn-IN"))
        self.lang_combo_var.set(self.code_to_name.get(self.settings.get("language", "bn-IN"), "বাংলা (ভারত)"))
        self.silence_var.set(self.settings.get("silence_seconds", 3.2))
        self.sound_var.set(self.settings.get("sound_effects", True))
        self.badge_var.set(self.settings.get("floating_badge", True))
        self.win.deiconify()
        self.win.lift()
        self.win.focus_force()

if __name__ == "__main__":
    app = SettingsUI()
    app.win.mainloop()
