"""
Voice Typer Pro for Antigravity IDE & Windows
==============================================
Author      : Ruhvi2026 (ruhvi.main@gmail.com)
Project     : Project Ruhvi (https://github.com/Ruhvi2026)
Repository  : https://github.com/Ruhvi2026/bangla-voice-typer
Year        : 2026
Description : World-class Desktop Speech-to-Text with CustomTkinter UI,
              125+ languages, dynamic i18n, Dark/Light modes, and native Windows Kernel Hotkey.
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
import customtkinter as ctk
from PIL import Image, ImageDraw
import pystray

from settings_ui import SettingsUI, load_settings, save_settings
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
        except Exception as e:
            logging.debug(f"Sound error: {e}")

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


class ModernFloatingPill:
    """A sleek floating pill badge with glowing indicator dot."""
    def __init__(self, parent_root):
        self.win = ctk.CTkToplevel(parent_root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.95)

        self.card = ctk.CTkFrame(
            self.win,
            corner_radius=16,
            border_width=1,
            border_color=("#cbd5e1", "#334155"),
            fg_color=("white", "#1e293b")
        )
        self.card.pack(fill="both", expand=True, padx=2, pady=2)

        self.dot_label = ctk.CTkLabel(
            self.card,
            text="●",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#ef4444"
        )
        self.dot_label.pack(side="left", padx=(14, 6), pady=8)

        self.text_label = ctk.CTkLabel(
            self.card,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("gray10", "gray95")
        )
        self.text_label.pack(side="left", padx=(0, 16), pady=8)

        self.win.withdraw()
        self._hide_timer = None

    def show(self, dot_color, text, auto_hide_ms=None):
        if not SETTINGS.get("floating_badge", True):
            return

        if self._hide_timer:
            self.win.after_cancel(self._hide_timer)
            self._hide_timer = None

        self.dot_label.configure(text_color=dot_color)
        self.text_label.configure(text=text)

        self.win.update_idletasks()
        w = self.card.winfo_reqwidth() + 24
        h = self.card.winfo_reqheight() + 10
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()

        x = sw - w - 24
        y = sh - h - 55
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
        logging.info("Starting Voice Typer Pro...")
        self.root = ctk.CTk()
        self.badge = ModernFloatingPill(self.root)
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
        msg = self._t("saved_msg")
        self.update_badge("#22c55e", msg, 2500)

    def on_minimized(self):
        self.update_badge("#3b82f6", "Voice Typer Pro Active (F8)", 3000)

    def update_badge(self, dot_color, text, auto_hide=None):
        self.root.after(0, lambda: self.badge.show(dot_color, text, auto_hide))

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

        # Red pulsing dot for recording
        self.update_badge("#ef4444", mode_hint)

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
            self.update_badge("#ef4444", f"Mic: {str(e)[:25]}", 3000)
            self.set_tray_icon(ICON_IDLE)
            self.is_recording = False
            return

        play_sound("stop")
        self.set_tray_icon(ICON_IDLE)
        # Amber dot for transcribing
        self.update_badge("#f59e0b", self._t("transcribing"))

        if not frames or not has_spoken:
            self.update_badge("#64748b", self._t("no_speech"), 2000)
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
                preview = text if len(text) <= 26 else text[:24] + "..."
                # Green dot for pasted success
                self.update_badge("#22c55e", f"{self._t('typed')}{preview}", 2500)

                if SETTINGS.get("auto_paste", True):
                    native_paste(text + " ")
            else:
                self.update_badge("#64748b", self._t("unclear"), 2000)

        except sr.UnknownValueError:
            play_sound("error")
            self.update_badge("#ef4444", self._t("unclear"), 2200)
        except sr.RequestError:
            play_sound("error")
            self.update_badge("#f59e0b", self._t("network_err"), 3000)
        except Exception as e:
            play_sound("error")
            self.update_badge("#ef4444", f"Error: {str(e)[:25]}", 2500)
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
            pystray.MenuItem("🎙️ Voice Typer Pro", None, enabled=False),
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
            "Voice Typer Pro (F8)", 
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
