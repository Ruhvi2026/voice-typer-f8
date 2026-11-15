"""
Settings UI for Bangla Voice Typer
Author: Ruhvi2026 (Project Ruhvi)
"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(APP_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "mode": "push_to_talk",  # "push_to_talk", "toggle", "auto_stop"
    "language": "bn-IN",     # "bn-IN", "bn-BD", "en-IN", "en-US", "hi-IN"
    "sound_effects": True,
    "floating_badge": True,
    "silence_seconds": 3.5,
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
    def __init__(self, parent=None, on_save_callback=None):
        self.settings = load_settings()
        self.on_save_cb = on_save_callback

        if parent:
            self.win = tk.Toplevel(parent)
        else:
            self.win = tk.Tk()

        self.win.title("🎙️ Bangla Voice Typer — সেটিংস")
        self.win.geometry("480x620")
        self.win.resizable(False, False)
        self.win.configure(bg="#181825")

        # Set window icon if available
        icon_path = os.path.join(APP_DIR, "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.win.iconbitmap(icon_path)
            except Exception:
                pass

        # Variables
        self.mode_var = tk.StringVar(value=self.settings.get("mode", "push_to_talk"))
        self.lang_var = tk.StringVar(value=self.settings.get("language", "bn-IN"))
        self.sound_var = tk.BooleanVar(value=self.settings.get("sound_effects", True))
        self.badge_var = tk.BooleanVar(value=self.settings.get("floating_badge", True))
        self.paste_var = tk.BooleanVar(value=self.settings.get("auto_paste", True))
        self.silence_var = tk.DoubleVar(value=self.settings.get("silence_seconds", 3.5))

        self._build_ui()
        self.win.focus_set()

    def _build_ui(self):
        # Header
        header = tk.Frame(self.win, bg="#11111b", padx=20, pady=16)
        header.pack(fill="x")

        title = tk.Label(
            header, 
            text="🎙️ Bangla Voice Typer", 
            font=("Segoe UI", 15, "bold"), 
            bg="#11111b", 
            fg="#cdd6f4"
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header, 
            text="কনফিগারেশন ও রেকর্ডিং মোড কন্ট্রোল প্যানেল", 
            font=("Segoe UI", 9), 
            bg="#11111b", 
            fg="#a6adc8"
        )
        subtitle.pack(anchor="w")

        content = tk.Frame(self.win, bg="#181825", padx=20, pady=14)
        content.pack(fill="both", expand=True)

        # Section 1: Modes
        sec_modes = tk.LabelFrame(
            content, 
            text=" 🎯 রেকর্ডিং মোড নির্বাচন করুন (Recording Modes) ", 
            font=("Segoe UI", 10, "bold"), 
            bg="#181825", 
            fg="#89b4fa", 
            padx=12, 
            pady=10,
            highlightthickness=1,
            highlightbackground="#313244"
        )
        sec_modes.pack(fill="x", pady=(0, 14))

        # Mode 1: Push-to-Talk
        rb1 = tk.Radiobutton(
            sec_modes,
            text="1️⃣  Push-to-Talk (Hold-to-Talk)",
            value="push_to_talk",
            variable=self.mode_var,
            font=("Segoe UI", 10, "bold"),
            bg="#181825",
            fg="#cdd6f4",
            selectcolor="#11111b",
            activebackground="#181825",
            activeforeground="#89b4fa"
        )
        rb1.pack(anchor="w")
        desc1 = tk.Label(
            sec_modes,
            text="      👉 F8 কি চেপে ধরে রাখুন, বলা শেষ হলে ছেড়ে দিন।",
            font=("Segoe UI", 8),
            bg="#181825",
            fg="#a6adc8"
        )
        desc1.pack(anchor="w", pady=(0, 6))

        # Mode 2: Toggle / Manual
        rb2 = tk.Radiobutton(
            sec_modes,
            text="2️⃣  Toggle Mode (Manual Start & Stop)",
            value="toggle",
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
            text="      👉 একবার F8 চাপলে শুরু, কথা শেষে আবার F8 চাপলে পেস্ট হবে।\n         (মাঝপথে ভাবার জন্য সীমাহীন সময় পাবেন, নিজে থেকে কাটবে না)।",
            font=("Segoe UI", 8),
            justify="left",
            bg="#181825",
            fg="#a6adc8"
        )
        desc2.pack(anchor="w", pady=(0, 6))

        # Mode 3: Auto-Stop
        rb3 = tk.Radiobutton(
            sec_modes,
            text="3️⃣  Auto-Stop (Smart Silence Detection)",
            value="auto_stop",
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
            text="      👉 একবার F8 চাপবেন, কথা বলা শেষ করে থামলে স্বয়ংক্রিয়ভাবে পেস্ট।",
            font=("Segoe UI", 8),
            bg="#181825",
            fg="#a6adc8"
        )
        desc3.pack(anchor="w", pady=(0, 4))

        # Silence slider for Auto-Stop
        silence_frame = tk.Frame(sec_modes, bg="#181825", padx=20)
        silence_frame.pack(fill="x", pady=(2, 4))
        
        lbl_silence = tk.Label(
            silence_frame, 
            text="অটো-স্টপে থামার বিরতি:", 
            font=("Segoe UI", 8), 
            bg="#181825", 
            fg="#cdd6f4"
        )
        lbl_silence.pack(side="left")

        self.slider = tk.Scale(
            silence_frame, 
            from_=1.5, 
            to=6.0, 
            resolution=0.5, 
            orient="horizontal", 
            variable=self.silence_var,
            bg="#181825",
            fg="#a6e3a1",
            highlightthickness=0,
            troughcolor="#313244",
            length=160
        )
        self.slider.pack(side="left", padx=8)

        lbl_sec = tk.Label(silence_frame, text="সেকেন্ড", font=("Segoe UI", 8), bg="#181825", fg="#a6adc8")
        lbl_sec.pack(side="left")

        # Section 2: Language & Options
        sec_opt = tk.LabelFrame(
            content, 
            text=" 🌐 ভাষা ও অপশনস ", 
            font=("Segoe UI", 10, "bold"), 
            bg="#181825", 
            fg="#89b4fa", 
            padx=12, 
            pady=10,
            highlightthickness=1,
            highlightbackground="#313244"
        )
        sec_opt.pack(fill="x", pady=(0, 10))

        # Language dropdown
        lang_row = tk.Frame(sec_opt, bg="#181825")
        lang_row.pack(fill="x", pady=(0, 8))

        lbl_lang = tk.Label(lang_row, text="প্রাথমিক ভাষা:", font=("Segoe UI", 9, "bold"), bg="#181825", fg="#cdd6f4")
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
            width=24
        )
        combo.pack(side="right")

        # Toggles
        cb1 = tk.Checkbutton(
            sec_opt, 
            text="🔊 সাউন্ড ইফেক্ট ও মিষ্টি বিং অডিও (Beep Chime)", 
            variable=self.sound_var, 
            font=("Segoe UI", 9), 
            bg="#181825", 
            fg="#cdd6f4", 
            selectcolor="#11111b",
            activebackground="#181825"
        )
        cb1.pack(anchor="w")

        cb2 = tk.Checkbutton(
            sec_opt, 
            text="💬 স্ক্রিনে ভাসমান নোটিফিকেশন ব্যাজ (Floating Pill)", 
            variable=self.badge_var, 
            font=("Segoe UI", 9), 
            bg="#181825", 
            fg="#cdd6f4", 
            selectcolor="#11111b",
            activebackground="#181825"
        )
        cb2.pack(anchor="w")

        cb3 = tk.Checkbutton(
            sec_opt, 
            text="📋 কার্সরে স্বয়ংক্রিয় পেস্ট (Auto-Paste)", 
            variable=self.paste_var, 
            font=("Segoe UI", 9), 
            bg="#181825", 
            fg="#cdd6f4", 
            selectcolor="#11111b",
            activebackground="#181825"
        )
        cb3.pack(anchor="w")

        # Save Button & Footer
        btn_frame = tk.Frame(self.win, bg="#11111b", padx=20, pady=12)
        btn_frame.pack(fill="x", side="bottom")

        btn_save = tk.Button(
            btn_frame, 
            text="💾 সেটিংস সংরক্ষণ করুন (Save)", 
            font=("Segoe UI", 10, "bold"), 
            bg="#89b4fa", 
            fg="#11111b", 
            activebackground="#b4befe", 
            relief="flat", 
            padx=16, 
            pady=6,
            command=self._save
        )
        btn_save.pack(side="right")

        credit = tk.Label(
            btn_frame, 
            text="by Ruhvi2026 • Project Ruhvi", 
            font=("Segoe UI", 8), 
            bg="#11111b", 
            fg="#6c7086"
        )
        credit.pack(side="left")

    def _save(self):
        new_lang_code = self.lang_map.get(self.lang_combo_var.get(), "bn-IN")
        self.settings["mode"] = self.mode_var.get()
        self.settings["language"] = new_lang_code
        self.settings["sound_effects"] = self.sound_var.get()
        self.settings["floating_badge"] = self.badge_var.get()
        self.settings["auto_paste"] = self.paste_var.get()
        self.settings["silence_seconds"] = float(self.silence_var.get())

        if save_settings(self.settings):
            if self.on_save_cb:
                self.on_save_cb(self.settings)
            messagebox.showinfo("সফল", "সেটিংস সফলভাবে সংরক্ষিত হয়েছে!")
            self.win.destroy()
        else:
            messagebox.showerror("ত্রুটি", "সেটিংস সংরক্ষণ করা সম্ভব হয়নি।")

if __name__ == "__main__":
    app = SettingsUI()
    app.win.mainloop()
