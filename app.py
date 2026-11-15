"""
Bangla Voice Typer for Antigravity IDE & Windows
================================================
Author      : Ruhvi2026 (ruhvi.main@gmail.com)
Project     : Project Ruhvi (https://github.com/Ruhvi2026)
Repository  : https://github.com/Ruhvi2026/bangla-voice-typer
Year        : 2026
Description : Ultra-reliable speech-to-text with 125+ languages, multilingual UI,
              Dark/Light theme switcher, and native Windows RegisterHotKey.
"""

import os
import sys
import time
import json
import io
import wave
import ctypes
import logging
import threading
import winsound
from ctypes import wintypes
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import pyperclip
from PIL import Image, ImageDraw
import pystray
import tkinter as tk

from settings_ui import SettingsUI, load_settings, save_settings, THEMES
from languages_data import get_ui_text

APP_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(APP_DIR, "app.log")

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)

SETTINGS = load_settings()

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = np.int16

# Win32 Constants
VK_CONTROL = 0x11
VK_V = 0x56
KEYEVENTF_KEYUP = 0x0002

VK_F8 = 0x77
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012
HOTKEY_ID = 1001

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

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
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(VK_V, 0, 0, 0)
        user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.35)
    except Exception as e:
        logging.error(f"Paste error: {e}")
    finally:
        try:
            if old_clipboard:
                pyperclip.copy(old_clipboard)
        except Exception:
            pass

def play_sound(sound_type):
    """Play pleasant audio chimes in non-blocking thread."""
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
    """A floating pill badge at bottom-right corner respecting active theme."""
    def __init__(self, parent_root):
        self.win = tk.Toplevel(parent_root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.94)

        theme_key = SETTINGS.get("theme", "dark")
        c = THEMES.get(theme_key, THEMES["dark"])
        self.win.configure(bg=c["card_bg"])

        self.frame = tk.Frame(
            self.win, 
            bg=c["card_bg"], 
            padx=16, 
            pady=10, 
            highlightthickness=1, 
            highlightbackground=c["border"]
        )
        self.frame.pack(fill="both", expand=True)

        self.label_icon = tk.Label(self.frame, text="🎙️", font=("Segoe UI Emoji", 14), bg=c["card_bg"], fg=c["text"])
        self.label_icon.pack(side="left", padx=(0, 8))

        self.label_text = tk.Label(self.frame, text="", font=("Segoe UI", 10, "bold"), bg=c["card_bg"], fg=c["text"])
        self.label_text.pack(side="left")

        self.win.withdraw()
        self._hide_timer = None

    def apply_theme(self):
        theme_key = SETTINGS.get("theme", "dark")
        c = THEMES.get(theme_key, THEMES["dark"])
        self.win.configure(bg=c["card_bg"])
        self.frame.configure(bg=c["card_bg"], highlightbackground=c["border"])
        self.label_icon.configure(bg=c["card_bg"], fg=c["text"])
        self.label_text.configure(bg=c["card_bg"], fg=c["text"])

    def show(self, icon, text, fg_color=None, auto_hide_ms=None):
        if not SETTINGS.get("floating_badge", True):
            return

        if self._hide_timer:
            self.win.after_cancel(self._hide_timer)
            self._hide_timer = None

        self.apply_theme()
        theme_key = SETTINGS.get("theme", "dark")
        c = THEMES.get(theme_key, THEMES["dark"])

        self.label_icon.config(text=icon)
        self.label_text.config(text=text, fg=fg_color or c["text"])

        self.win.update_idletasks()
        w = self.frame.winfo_reqwidth() + 20
        h = self.frame.winfo_reqheight() + 10
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()

        x = sw - w - 30
        y = sh - h - 60
        self.win.geometry(f"{w}x{h}+{x}+{y}")
        self.win.deiconify()

        if auto_hide_ms:
            self._hide_timer = self.win.after(auto_hide_ms, self.hide)

    def hide(self):
        self.win.withdraw()


class WindowsKernelHotkey(threading.Thread):
    def __init__(self, callback):
        super().__init__(daemon=True)
        self.callback = callback
        self.thread_id = None
        self.running = True

    def run(self):
        self.thread_id = kernel32.GetCurrentThreadId()
        res = user32.RegisterHotKey(None, HOTKEY_ID, MOD_NOREPEAT, VK_F8)
        if not res:
            res = user32.RegisterHotKey(None, HOTKEY_ID, 0, VK_F8)

        logging.info(f"Native Windows RegisterHotKey F8 status: {bool(res)} (Thread: {self.thread_id})")

        msg = wintypes.MSG()
        while self.running and user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                try:
                    self.callback()
                except Exception as e:
                    logging.error(f"Error in hotkey callback: {e}")
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        user32.UnregisterHotKey(None, HOTKEY_ID)

    def stop(self):
        self.running = False
        if self.thread_id:
            user32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)


class VoiceTyperApp:
    def __init__(self):
        logging.info("Starting Multi-language Voice Typer...")
        self.root = tk.Tk()
        self.badge = FloatingBadge(self.root)
        self.recognizer = sr.Recognizer()
        
        self.is_recording = False
        self.stop_requested = False
        self.lock = threading.Lock()
        self.tray_icon = None

        self.settings_ui = SettingsUI(
            root=self.root, 
            on_save_callback=self.on_settings_saved,
            on_minimize_callback=self.on_minimized
        )

        self.hotkey_engine = WindowsKernelHotkey(self.trigger_hotkey)
        self.hotkey_engine.start()

        self.init_tray()
        self._heartbeat()

    def _t(self, key):
        return get_ui_text(SETTINGS.get("language", "bn-IN"), key)

    def _heartbeat(self):
        try:
            if not self.hotkey_engine.is_alive():
                logging.warning("Restarting kernel hotkey engine...")
                self.hotkey_engine = WindowsKernelHotkey(self.trigger_hotkey)
                self.hotkey_engine.start()
        except Exception:
            pass
        finally:
            self.root.after(2500, self._heartbeat)

    def on_settings_saved(self, new_settings):
        global SETTINGS
        SETTINGS = new_settings
        self.badge.apply_theme()
        msg = self._t("saved_msg")
        self.update_badge("⚙️", msg, "#a6e3a1", 2500)

    def on_minimized(self):
        self.badge.apply_theme()
        self.update_badge("🎙️", "Voice Typer Active (F8)", "#89b4fa", 3000)

    def update_badge(self, icon, text, fg=None, auto_hide=None):
        self.root.after(0, lambda: self.badge.show(icon, text, fg, auto_hide))

    def set_tray_icon(self, img):
        if self.tray_icon:
            try:
                self.tray_icon.icon = img
            except Exception:
                pass

    def trigger_hotkey(self):
        mode = SETTINGS.get("mode", "auto_stop")
        with self.lock:
            if mode == "auto_stop":
                if not self.is_recording:
                    threading.Thread(target=self._record_worker, daemon=True).start()
                else:
                    self.stop_requested = True

            elif mode == "toggle":
                if not self.is_recording:
                    threading.Thread(target=self._record_worker, daemon=True).start()
                else:
                    self.stop_requested = True

            elif mode == "push_to_talk":
                if not self.is_recording:
                    threading.Thread(target=self._record_worker, daemon=True).start()
                    threading.Thread(target=self._watch_physical_release, daemon=True).start()

    def _watch_physical_release(self):
        time.sleep(0.15)
        while self.is_recording and not self.stop_requested:
            state = user32.GetAsyncKeyState(VK_F8)
            if not (state & 0x8000):
                self.stop_requested = True
                break
            time.sleep(0.03)

    def _record_worker(self):
        self.is_recording = True
        self.stop_requested = False
        self.set_tray_icon(ICON_RECORDING)
        play_sound("start")

        mode = SETTINGS.get("mode", "auto_stop")
        lang = SETTINGS.get("language", "bn-IN")
        sec = SETTINGS.get("silence_seconds", 3.2)

        if mode == "auto_stop":
            mode_hint = self._t("hint_auto").format(sec=sec)
        elif mode == "push_to_talk":
            mode_hint = self._t("hint_ptt")
        else:
            mode_hint = self._t("hint_toggle")

        self.update_badge("🎙️", mode_hint, "#89b4fa")

        frames = []
        chunk_duration = 0.1
        chunk_samples = int(SAMPLE_RATE * chunk_duration)
        has_spoken = False
        silence_time = 0.0
        max_duration = SETTINGS.get("max_seconds", 45)
        silence_limit = SETTINGS.get("silence_seconds", 3.2)

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

                    rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))

                    if mode == "auto_stop":
                        if rms > speech_threshold:
                            has_spoken = True
                            silence_time = 0.0
                        elif has_spoken:
                            silence_time += chunk_duration
                            if silence_time >= silence_limit:
                                break
                    else:
                        if rms > speech_threshold:
                            has_spoken = True

                    if (time.time() - start_time) >= max_duration:
                        break

        except Exception as e:
            play_sound("error")
            logging.error(f"Mic error: {e}")
            self.update_badge("❌", f"Mic: {str(e)[:25]}", "#f38ba8", 3000)
            self.set_tray_icon(ICON_IDLE)
            self.is_recording = False
            return

        play_sound("stop")
        self.set_tray_icon(ICON_IDLE)
        self.update_badge("⏳", self._t("transcribing"), "#f9e2af")

        if not frames or not has_spoken:
            self.update_badge("ℹ️", self._t("no_speech"), "#a6adc8", 2000)
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
            logging.info(f"Transcribed ({lang}): '{text}'")

            if text:
                play_sound("success")
                preview = text if len(text) <= 25 else text[:23] + "..."
                self.update_badge("✅", f"{self._t('typed')}{preview}", "#a6e3a1", 2500)

                if SETTINGS.get("auto_paste", True):
                    native_paste(text + " ")
            else:
                self.update_badge("ℹ️", self._t("unclear"), "#a6adc8", 2000)

        except sr.UnknownValueError:
            play_sound("error")
            self.update_badge("❓", self._t("unclear"), "#f38ba8", 2200)
        except sr.RequestError:
            play_sound("error")
            self.update_badge("⚠️", self._t("network_err"), "#fab387", 3000)
        except Exception as e:
            play_sound("error")
            self.update_badge("❌", f"Error: {str(e)[:25]}", "#f38ba8", 2500)
        finally:
            self.is_recording = False

    def open_settings_ui(self):
        self.root.after(0, self.settings_ui.show)

    def init_tray(self):
        def on_exit():
            if self.tray_icon:
                self.tray_icon.stop()
            self.hotkey_engine.stop()
            self.root.after(0, self.root.destroy)

        menu = pystray.Menu(
            pystray.MenuItem("🎙️ Voice Typer", None, enabled=False),
            pystray.MenuItem("✨ Created by Ruhvi2026", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(self._t("tray_open"), self.open_settings_ui, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("⌨️ Hotkey: F8", None, enabled=False),
            pystray.MenuItem(self._t("tray_exit"), on_exit)
        )

        self.tray_icon = pystray.Icon(
            "bangla_voice_typer", 
            ICON_IDLE, 
            "Voice Typer (F8)", 
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
            self.hotkey_engine.stop()

if __name__ == "__main__":
    app = VoiceTyperApp()
    app.run()
