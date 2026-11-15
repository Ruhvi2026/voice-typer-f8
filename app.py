"""
Bangla Voice Typer for Antigravity IDE & Windows
================================================
Author      : Ruhvi2026 (ruhvi.main@gmail.com)
Project     : Project Ruhvi (https://github.com/Ruhvi2026)
Repository  : https://github.com/Ruhvi2026/bangla-voice-typer
Year        : 2026
Description : Ultra-lightweight Bengali speech-to-text with 3 customizable recording modes:
              1. Push-to-Talk (Hold key to record, release to paste)
              2. Toggle Mode (Manual Start & Stop - unlimited thinking time)
              3. Auto-Stop Mode (Configurable smart silence pause)
"""

import os
import sys
import time
import json
import io
import wave
import ctypes
import threading
import winsound
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import pyperclip
from pynput import keyboard
from PIL import Image, ImageDraw
import pystray
import tkinter as tk

from settings_ui import SettingsUI, load_settings, save_settings, SETTINGS_PATH

APP_DIR = os.path.dirname(os.path.abspath(__file__))

SETTINGS = load_settings()

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = np.int16

VK_CONTROL = 0x11
VK_V = 0x56
KEYEVENTF_KEYUP = 0x0002

def native_paste(text):
    """Pastes text directly at the active cursor and restores previous clipboard."""
    if not text:
        return
    old_clipboard = ""
    try:
        old_clipboard = pyperclip.paste()
    except Exception:
        pass

    try:
        pyperclip.copy(text)
        time.sleep(0.06)
        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
        ctypes.windll.user32.keybd_event(VK_V, 0, 0, 0)
        ctypes.windll.user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.35)
    finally:
        try:
            if old_clipboard:
                pyperclip.copy(old_clipboard)
        except Exception:
            pass

def play_sound(sound_type):
    """Play non-blocking pleasant audio chimes."""
    if not SETTINGS.get("sound_effects", True):
        return

    def _play():
        try:
            if sound_type == "start":
                winsound.Beep(900, 80)
                winsound.Beep(1200, 100)
            elif sound_type == "stop":
                winsound.Beep(750, 90)
            elif sound_type == "success":
                winsound.Beep(1200, 80)
                winsound.Beep(1600, 120)
            elif sound_type == "error":
                winsound.Beep(450, 180)
        except Exception:
            pass

    threading.Thread(target=_play, daemon=True).start()

def create_icon_image(color="#38bdf8"):
    """Draws a clean, modern microphone tray icon."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([4, 4, 60, 60], fill="#1e1e2e", outline=color, width=3)
    d.rounded_rectangle([26, 16, 38, 38], radius=6, fill=color)
    d.arc([20, 24, 44, 44], start=0, end=180, fill=color, width=3)
    d.line([32, 44, 32, 52], fill=color, width=3)
    d.line([24, 52, 40, 52], fill=color, width=3)
    return img

ICON_IDLE = create_icon_image("#38bdf8")
ICON_RECORDING = create_icon_image("#f38ba8")


class FloatingBadge:
    """A floating pill badge at bottom-right corner showing live status."""
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.94)
        self.root.configure(bg="#181825")

        self.frame = tk.Frame(
            self.root, 
            bg="#181825", 
            padx=16, 
            pady=10, 
            highlightthickness=1, 
            highlightbackground="#313244"
        )
        self.frame.pack(fill="both", expand=True)

        self.label_icon = tk.Label(self.frame, text="🎙️", font=("Segoe UI Emoji", 14), bg="#181825", fg="#cdd6f4")
        self.label_icon.pack(side="left", padx=(0, 8))

        self.label_text = tk.Label(self.frame, text="", font=("Segoe UI", 10, "bold"), bg="#181825", fg="#cdd6f4")
        self.label_text.pack(side="left")

        self.root.withdraw()
        self._hide_timer = None

    def show(self, icon, text, fg_color="#cdd6f4", auto_hide_ms=None):
        if not SETTINGS.get("floating_badge", True):
            return

        if self._hide_timer:
            self.root.after_cancel(self._hide_timer)
            self._hide_timer = None

        self.label_icon.config(text=icon)
        self.label_text.config(text=text, fg=fg_color)

        self.root.update_idletasks()
        w = self.frame.winfo_reqwidth() + 20
        h = self.frame.winfo_reqheight() + 10
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        x = sw - w - 30
        y = sh - h - 60
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.deiconify()

        if auto_hide_ms:
            self._hide_timer = self.root.after(auto_hide_ms, self.hide)

    def hide(self):
        self.root.withdraw()


class VoiceTyperApp:
    def __init__(self):
        self.root = tk.Tk()
        self.badge = FloatingBadge(self.root)
        self.recognizer = sr.Recognizer()
        
        self.is_recording = False
        self.stop_requested = False
        self.is_holding = False
        self.lock = threading.Lock()
        self.tray_icon = None

        # Start Global Key Listener for F8 (Press and Release)
        self.listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.listener.start()

        # Start Tray Icon
        self.init_tray()

        # Initial launch toast with author signature
        self.update_badge("🎙️", "Bangla Voice Typer রেডি! • by Ruhvi2026 (F8)", "#a6e3a1", 3200)

    def update_badge(self, icon, text, fg="#cdd6f4", auto_hide=None):
        self.root.after(0, lambda: self.badge.show(icon, text, fg, auto_hide))

    def set_tray_icon(self, img):
        if self.tray_icon:
            try:
                self.tray_icon.icon = img
            except Exception:
                pass

    def on_key_press(self, key):
        if key == keyboard.Key.f8:
            mode = SETTINGS.get("mode", "push_to_talk")
            with self.lock:
                if mode == "push_to_talk":
                    # While holding key, ignore repeat presses
                    if not self.is_holding:
                        self.is_holding = True
                        if not self.is_recording:
                            threading.Thread(target=self._record_worker, daemon=True).start()
                elif mode == "toggle":
                    # Single press starts, single press stops
                    if not self.is_recording:
                        threading.Thread(target=self._record_worker, daemon=True).start()
                    else:
                        self.stop_requested = True
                elif mode == "auto_stop":
                    # Single press starts (silence stops), or press again to stop
                    if not self.is_recording:
                        threading.Thread(target=self._record_worker, daemon=True).start()
                    else:
                        self.stop_requested = True

    def on_key_release(self, key):
        if key == keyboard.Key.f8:
            mode = SETTINGS.get("mode", "push_to_talk")
            with self.lock:
                if mode == "push_to_talk":
                    self.is_holding = False
                    if self.is_recording:
                        self.stop_requested = True

    def _record_worker(self):
        self.is_recording = True
        self.stop_requested = False
        self.set_tray_icon(ICON_RECORDING)
        play_sound("start")

        mode = SETTINGS.get("mode", "push_to_talk")
        lang = SETTINGS.get("language", "bn-IN")
        
        mode_hint = {
            "push_to_talk": "F8 চেপে রাখুন, শেষে ছেড়ে দিন",
            "toggle": "কথা শেষে আবার F8 চাপুন",
            "auto_stop": f"কথা শেষে {SETTINGS.get('silence_seconds', 3.5)} সে. বিরতি"
        }.get(mode, "মুখে বলুন")

        self.update_badge("🎙️", f"শুনছি... ({mode_hint})", "#89b4fa")

        frames = []
        chunk_duration = 0.1
        chunk_samples = int(SAMPLE_RATE * chunk_duration)
        has_spoken = False
        silence_time = 0.0
        max_duration = SETTINGS.get("max_seconds", 45)
        silence_limit = SETTINGS.get("silence_seconds", 3.5)

        try:
            with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE) as stream:
                calib_chunks, _ = stream.read(int(SAMPLE_RATE * 0.15))
                calib_rms = float(np.sqrt(np.mean(calib_chunks.astype(np.float32) ** 2)))
                noise_floor = max(260.0, calib_rms * 1.5)
                speech_threshold = noise_floor * 1.3

                start_time = time.time()
                while not self.stop_requested:
                    chunk, _ = stream.read(chunk_samples)
                    frames.append(chunk)

                    # Silence check only in auto_stop mode!
                    if mode == "auto_stop":
                        rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
                        if rms > speech_threshold:
                            has_spoken = True
                            silence_time = 0.0
                        elif has_spoken:
                            silence_time += chunk_duration
                            if silence_time >= silence_limit:
                                break
                    else:
                        # In push_to_talk and toggle, we just track if speech occurred
                        rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
                        if rms > speech_threshold:
                            has_spoken = True

                    if (time.time() - start_time) >= max_duration:
                        break

        except Exception as e:
            play_sound("error")
            self.update_badge("❌", f"মাইক্রোফোন ত্রুটি: {str(e)[:25]}", "#f38ba8", 3000)
            self.set_tray_icon(ICON_IDLE)
            self.is_recording = False
            return

        play_sound("stop")
        self.set_tray_icon(ICON_IDLE)
        self.update_badge("⏳", "টেক্সটে রূপান্তর হচ্ছে...", "#f9e2af")

        if not frames or not has_spoken:
            self.update_badge("ℹ️", "কোনো কথা শোনা যায়নি", "#a6adc8", 2000)
            self.is_recording = False
            return

        try:
            audio_data = np.concatenate(frames, axis=0)
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_data.tobytes())
            wav_buffer.seek(0)

            with sr.AudioFile(wav_buffer) as source:
                sr_audio = self.recognizer.record(source)

            text = self.recognizer.recognize_google(sr_audio, language=lang)
            text = text.strip()

            if text:
                play_sound("success")
                preview = text if len(text) <= 25 else text[:23] + "..."
                self.update_badge("✅", f"টাইপ হলো: {preview}", "#a6e3a1", 2500)

                if SETTINGS.get("auto_paste", True):
                    native_paste(text + " ")
            else:
                self.update_badge("ℹ️", "কিছু বোঝা যায়নি, আবার বলুন", "#a6adc8", 2000)

        except sr.UnknownValueError:
            play_sound("error")
            self.update_badge("❓", "কথাটি স্পষ্ট বোঝা যায়নি", "#f38ba8", 2200)
        except sr.RequestError:
            play_sound("error")
            self.update_badge("⚠️", "ইন্টারনেট কানেকশন সমস্যা", "#fab387", 3000)
        except Exception as e:
            play_sound("error")
            self.update_badge("❌", f"ত্রুটি: {str(e)[:25]}", "#f38ba8", 2500)
        finally:
            self.is_recording = False

    def open_settings_ui(self):
        """Open modern Settings GUI window."""
        def on_saved(new_settings):
            global SETTINGS
            SETTINGS = new_settings
            mode_name = {
                "push_to_talk": "Push-to-Talk (চেপে রাখা)",
                "toggle": "Toggle (ম্যানুয়াল স্টার্ট/স্টপ)",
                "auto_stop": "Auto-Stop (স্মার্ট নীরবতা)"
            }.get(SETTINGS.get("mode"), "কাস্টম")
            self.update_badge("⚙️", f"মোড পরিবর্তিত: {mode_name}", "#89b4fa", 2500)

        self.root.after(0, lambda: SettingsUI(parent=self.root, on_save_callback=on_saved))

    def init_tray(self):
        def set_mode(m):
            SETTINGS["mode"] = m
            save_settings(SETTINGS)
            mode_name = {
                "push_to_talk": "Push-to-Talk",
                "toggle": "Toggle Mode",
                "auto_stop": "Auto-Stop Mode"
            }.get(m, m)
            self.update_badge("🎯", f"মোড সিলেক্টেড: {mode_name}", "#89b4fa", 2000)

        def set_lang(code, name):
            SETTINGS["language"] = code
            save_settings(SETTINGS)
            self.update_badge("🌐", f"ভাষা: {name}", "#89b4fa", 2000)

        def on_exit():
            if self.tray_icon:
                self.tray_icon.stop()
            self.listener.stop()
            self.root.after(0, self.root.destroy)

        menu = pystray.Menu(
            pystray.MenuItem("🎙️ Bangla Voice Typer", None, enabled=False),
            pystray.MenuItem("✨ Created by Ruhvi2026", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("⚙️ সেটিংস ও কন্ট্রোল প্যানেল (UI)...", self.open_settings_ui),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "🎯 মোড ১: Push-to-Talk (চেপে ধরে রাখা)", 
                lambda: set_mode("push_to_talk"), 
                checked=lambda item: SETTINGS.get("mode") == "push_to_talk"
            ),
            pystray.MenuItem(
                "🎯 মোড ২: Toggle (একবার চেপে শুরু ও শেষ)", 
                lambda: set_mode("toggle"), 
                checked=lambda item: SETTINGS.get("mode") == "toggle"
            ),
            pystray.MenuItem(
                "🎯 মোড ৩: Auto-Stop (নীরবতায় থামা)", 
                lambda: set_mode("auto_stop"), 
                checked=lambda item: SETTINGS.get("mode") == "auto_stop"
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "🌐 বাংলা (ভারত)", 
                lambda: set_lang("bn-IN", "বাংলা ভারত"), 
                checked=lambda item: SETTINGS.get("language") == "bn-IN"
            ),
            pystray.MenuItem(
                "🌐 বাংলা (বাংলাদেশ)", 
                lambda: set_lang("bn-BD", "বাংলা বাংলাদেশ"), 
                checked=lambda item: SETTINGS.get("language") == "bn-BD"
            ),
            pystray.MenuItem(
                "🌐 English (India)", 
                lambda: set_lang("en-IN", "English"), 
                checked=lambda item: SETTINGS.get("language") == "en-IN"
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("⌨️ হটকি: F8", None, enabled=False),
            pystray.MenuItem("❌ বন্ধ করুন (Exit)", on_exit)
        )

        self.tray_icon = pystray.Icon(
            "bangla_voice_typer", 
            ICON_IDLE, 
            "Bangla Voice Typer (F8)", 
            menu=menu
        )
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            if self.tray_icon:
                try:
                    self.tray_icon.stop()
                except Exception:
                    pass
            self.listener.stop()

if __name__ == "__main__":
    app = VoiceTyperApp()
    app.run()
