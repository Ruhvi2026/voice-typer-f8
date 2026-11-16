"""
Voice Typer F8 for Antigravity IDE & Windows
==============================================
Author      : Ruhvi2026 (ruhvi.main@gmail.com)
Project     : Project Ruhvi (https://github.com/Ruhvi2026)
Repository  : https://github.com/Ruhvi2026/voice-typer-f8
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

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(os.path.abspath(sys.executable))
    BUNDLE_DIR = getattr(sys, '_MEIPASS', APP_DIR)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = APP_DIR

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

MUTEX_NAME = "Local\\VoiceTyperF8_SingleInstance_App_Mutex_2026"
_SINGLE_INSTANCE_MUTEX = None

def check_single_instance():
    """Ensures only one instance of Voice Typer F8 runs at a time."""
    global _SINGLE_INSTANCE_MUTEX
    _SINGLE_INSTANCE_MUTEX = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        logging.warning("Another instance of Voice Typer F8 is already active. Focusing existing window and exiting duplicate.")
        hwnd = user32.FindWindowW(None, "Voice Typer F8 — Desktop Speech Hub")
        if hwnd:
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            user32.SetForegroundWindow(hwnd)
        sys.exit(0)

def native_paste(text, target_hwnd=None):
    """Pastes text directly at the active cursor and restores previous clipboard."""
    if not text:
        return
    if target_hwnd and user32.IsWindow(target_hwnd):
        try:
            user32.SetForegroundWindow(target_hwnd)
            time.sleep(0.05)
        except Exception:
            pass

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


class FloatingMicWidget:
    """
    Always-on-top, draggable, click-to-talk floating mic widget for Windows.
    Applies WS_EX_NOACTIVATE so clicking it NEVER steals focus from active text box!
    Supports Auto-Stop, Push-to-Talk, and Toggle modes.
    """
    def __init__(self, parent_root, on_press_callback, on_release_callback=None, on_open_settings=None):
        self.root = parent_root
        self.on_press = on_press_callback
        self.on_release = on_release_callback
        self.on_open_settings = on_open_settings

        self.win = ctk.CTkToplevel(parent_root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.96)

        # Apply WS_EX_NOACTIVATE style so clicking NEVER steals text focus
        self._apply_no_activate()

        # Modern floating pill styling
        self.card = ctk.CTkFrame(
            self.win,
            corner_radius=20,
            border_width=2,
            border_color="#38bdf8",
            fg_color="#0f172a"
        )
        self.card.pack(fill="both", expand=True, padx=2, pady=2)

        # Mic Icon
        self.icon_label = ctk.CTkLabel(
            self.card,
            text="🎙️",
            font=ctk.CTkFont(family="Segoe UI Emoji", size=15),
            text_color="#38bdf8"
        )
        self.icon_label.pack(side="left", padx=(10, 3), pady=5)

        # Status text
        self.text_label = ctk.CTkLabel(
            self.card,
            text="Mic (F8)",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#f8fafc"
        )
        self.text_label.pack(side="left", padx=(0, 4), pady=5)

        # Sleek Close (✕) button on right
        self.close_btn = ctk.CTkLabel(
            self.card,
            text="✕",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#64748b",
            width=20,
            height=20,
            corner_radius=10,
            fg_color="transparent"
        )
        self.close_btn.pack(side="right", padx=(0, 6), pady=5)
        self.close_btn.bind("<Enter>", self._on_close_hover_enter)
        self.close_btn.bind("<Leave>", self._on_close_hover_leave)
        self.close_btn.bind("<Button-1>", self._on_close_clicked)

        # Dragging & Clicking states
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.win_x = 0
        self.win_y = 0
        self.moved = False
        self.target_hwnd = None
        self._reset_timer = None

        # Bind mouse events to all widgets in the card
        for widget in (self.win, self.card, self.icon_label, self.text_label):
            widget.bind("<ButtonPress-1>", self._on_mouse_down)
            widget.bind("<B1-Motion>", self._on_mouse_drag)
            widget.bind("<ButtonRelease-1>", self._on_mouse_up)
            widget.bind("<Button-3>", self._on_right_click)
            widget.bind("<Enter>", self._on_hover_enter)
            widget.bind("<Leave>", self._on_hover_leave)

        # Load position or default to top-right
        self._set_initial_position()

        if not SETTINGS.get("floating_mic", True):
            self.win.withdraw()
        else:
            self.win.deiconify()

    def _apply_no_activate(self):
        try:
            self.win.update_idletasks()
            hwnd = user32.GetParent(self.win.winfo_id())
            if not hwnd:
                hwnd = self.win.winfo_id()
            GWL_EXSTYLE = -20
            WS_EX_NOACTIVATE = 0x08000000
            WS_EX_TOPMOST = 0x00000008
            cur = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, cur | WS_EX_NOACTIVATE | WS_EX_TOPMOST)
        except Exception as e:
            logging.debug(f"Failed to apply WS_EX_NOACTIVATE: {e}")

    def _set_initial_position(self):
        sw = self.win.winfo_screenwidth()
        saved_x = SETTINGS.get("floating_mic_x", -1)
        saved_y = SETTINGS.get("floating_mic_y", -1)
        if saved_x > 0 and saved_y > 0 and saved_x < (sw - 50):
            x, y = saved_x, saved_y
        else:
            x = sw - 160
            y = 75
        self.win.geometry(f"140x42+{x}+{y}")

    def _on_close_hover_enter(self, event=None):
        self.close_btn.configure(text_color="#ef4444", fg_color="#1e293b")

    def _on_close_hover_leave(self, event=None):
        self.close_btn.configure(text_color="#64748b", fg_color="transparent")

    def _on_close_clicked(self, event=None):
        self.hide()
        return "break"

    def _on_mouse_down(self, event):
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        self.win_x = self.win.winfo_x()
        self.win_y = self.win.winfo_y()
        self.moved = False
        self.target_hwnd = user32.GetForegroundWindow()

        mode = SETTINGS.get("mode", "auto_stop")
        if mode == "push_to_talk":
            if self.on_press:
                self.on_press(source="floating_mic_mouse_down")

    def _on_mouse_drag(self, event):
        dx = event.x_root - self.drag_start_x
        dy = event.y_root - self.drag_start_y
        if abs(dx) > 4 or abs(dy) > 4:
            self.moved = True
            new_x = self.win_x + dx
            new_y = self.win_y + dy
            self.win.geometry(f"+{new_x}+{new_y}")

    def _on_mouse_up(self, event):
        if self.moved:
            SETTINGS["floating_mic_x"] = self.win.winfo_x()
            SETTINGS["floating_mic_y"] = self.win.winfo_y()
            save_settings(SETTINGS)
            return

        mode = SETTINGS.get("mode", "auto_stop")
        if mode == "push_to_talk":
            if self.on_release:
                self.on_release()
        else:
            if self.on_press:
                self.on_press(source="floating_mic_click")

    def _on_hover_enter(self, event=None):
        if self.card.cget("border_color") == "#38bdf8":
            self.card.configure(border_color="#2563eb")

    def _on_hover_leave(self, event=None):
        if self.card.cget("border_color") == "#2563eb":
            self.card.configure(border_color="#38bdf8")

    def _on_right_click(self, event):
        import tkinter as tk
        menu = tk.Menu(self.win, tearoff=0)
        menu.add_command(label="⚙️ Settings (কন্ট্রোল সেন্টার)", command=self.on_open_settings)
        menu.add_separator()
        menu.add_command(label="❌ Hide Floating Mic (লুকান)", command=self.hide)
        menu.post(event.x_root, event.y_root)

    def set_state(self, state, text=None):
        def _update():
            if self._reset_timer:
                self.win.after_cancel(self._reset_timer)
                self._reset_timer = None

            if state == "idle":
                self.card.configure(fg_color="#0f172a", border_color="#38bdf8")
                self.icon_label.configure(text="🎙️", text_color="#38bdf8")
                self.text_label.configure(text=text or "Mic (F8)", text_color="#f8fafc")
                self.close_btn.configure(text_color="#64748b")
            elif state == "recording":
                self.card.configure(fg_color="#450a0a", border_color="#ef4444")
                self.icon_label.configure(text="🔴", text_color="#ef4444")
                self.text_label.configure(text=text or "Listening...", text_color="#fecaca")
                self.close_btn.configure(text_color="#fca5a5")
            elif state == "transcribing":
                self.card.configure(fg_color="#451a03", border_color="#f59e0b")
                self.icon_label.configure(text="⏳", text_color="#f59e0b")
                self.text_label.configure(text=text or "Converting...", text_color="#fef3c7")
                self.close_btn.configure(text_color="#fde68a")
            elif state == "success":
                self.card.configure(fg_color="#052e16", border_color="#22c55e")
                self.icon_label.configure(text="✓", text_color="#22c55e")
                self.text_label.configure(text=text or "Typed!", text_color="#bbf7d0")
                self.close_btn.configure(text_color="#86efac")
                self._reset_timer = self.win.after(1600, lambda: self.set_state("idle"))
            elif state == "error":
                self.card.configure(fg_color="#450a0a", border_color="#ef4444")
                self.icon_label.configure(text="⚠️", text_color="#ef4444")
                self.text_label.configure(text=text or "Error", text_color="#fecaca")
                self.close_btn.configure(text_color="#fca5a5")
                self._reset_timer = self.win.after(2000, lambda: self.set_state("idle"))

        self.root.after(0, _update)

    def show(self):
        SETTINGS["floating_mic"] = True
        save_settings(SETTINGS)
        self.win.deiconify()
        self.win.lift()

    def hide(self):
        self.win.withdraw()
        SETTINGS["floating_mic"] = False
        save_settings(SETTINGS)


class HardwareKeyWatcher(threading.Thread):
    """
    Direct hardware keyboard poll for F8 using GetAsyncKeyState.
    Guarantees F8 press/release detection globally across all apps,
    even if RegisterHotKey is blocked, unhooked, or held by another app.
    """
    def __init__(self, on_press, on_release):
        super().__init__(daemon=True)
        self.on_press = on_press
        self.on_release = on_release
        self.running = True
        self.is_down = False

    def run(self):
        logging.info("HardwareKeyWatcher started for F8 (polling at 15ms)...")
        while self.running:
            try:
                down = bool(user32.GetAsyncKeyState(VK_F8) & 0x8000)
                if down and not self.is_down:
                    self.is_down = True
                    self.on_press("hardware_watcher")
                elif not down and self.is_down:
                    self.is_down = False
                    self.on_release()
            except Exception as e:
                logging.error(f"HardwareKeyWatcher error: {e}")
            time.sleep(0.015)

    def stop(self):
        self.running = False


class WindowsKernelHotkey(threading.Thread):
    """
    Native Windows RegisterHotKey listener.
    Captures F8 to prevent target app (e.g. IDE) from processing F8 keystroke.
    """
    def __init__(self, on_press):
        super().__init__(daemon=True)
        self.on_press = on_press
        self.thread_id = None
        self.running = True

    def run(self):
        self.thread_id = kernel32.GetCurrentThreadId()
        # Clean up any stale registration first
        user32.UnregisterHotKey(None, HOTKEY_ID)
        time.sleep(0.05)
        res = user32.RegisterHotKey(None, HOTKEY_ID, MOD_NOREPEAT, VK_F8)
        if not res:
            res = user32.RegisterHotKey(None, HOTKEY_ID, 0, VK_F8)

        logging.info(f"Native Windows RegisterHotKey F8 status: {bool(res)} (Thread: {self.thread_id})")

        msg = wintypes.MSG()
        while self.running and user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                try:
                    self.on_press("register_hotkey")
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
        logging.info("Starting Voice Typer F8...")
        self.root = ctk.CTk()
        self.badge = ModernFloatingPill(self.root)
        self.recognizer = sr.Recognizer()
        
        self.is_recording = False
        self.stop_requested = False
        self.recording_start_time = 0.0
        self.last_trigger_time = 0.0
        self.lock = threading.Lock()
        self.tray_icon = None

        self.settings_ui = SettingsUI(
            root=self.root, 
            on_save_callback=self.on_settings_saved,
            on_minimize_callback=self.on_minimized
        )

        # Always-on-top draggable floating mic widget
        self.floating_mic = FloatingMicWidget(
            parent_root=self.root,
            on_press_callback=self.on_f8_pressed,
            on_release_callback=self.on_f8_released,
            on_open_settings=self.open_settings_ui
        )

        # Dual engines for 100% resilient F8 detection
        self.hotkey_engine = WindowsKernelHotkey(self.on_f8_pressed)
        self.hotkey_engine.start()

        self.hardware_watcher = HardwareKeyWatcher(self.on_f8_pressed, self.on_f8_released)
        self.hardware_watcher.start()

        self.init_tray()
        self._heartbeat()

    def _t(self, key):
        return get_ui_text(SETTINGS.get("language", "bn-IN"), key)

    def _heartbeat(self):
        try:
            if not self.hotkey_engine.is_alive():
                logging.warning("Restarting kernel hotkey engine...")
                self.hotkey_engine = WindowsKernelHotkey(self.on_f8_pressed)
                self.hotkey_engine.start()
            if not self.hardware_watcher.is_alive():
                logging.warning("Restarting hardware key watcher...")
                self.hardware_watcher = HardwareKeyWatcher(self.on_f8_pressed, self.on_f8_released)
                self.hardware_watcher.start()
        except Exception:
            pass
        finally:
            self.root.after(2500, self._heartbeat)

    def on_settings_saved(self, new_settings):
        global SETTINGS
        SETTINGS = new_settings
        if new_settings.get("floating_mic", True):
            self.floating_mic.show()
        else:
            self.floating_mic.hide()
        msg = self._t("saved_msg")
        self.update_badge("#22c55e", msg, 2500)

    def on_minimized(self):
        self.update_badge("#3b82f6", "Voice Typer F8 Active", 3000)

    def update_badge(self, dot_color, text, auto_hide=None):
        self.root.after(0, lambda: self.badge.show(dot_color, text, auto_hide))

    def set_tray_icon(self, img):
        if self.tray_icon:
            try:
                self.tray_icon.icon = img
            except Exception:
                pass

    def on_f8_pressed(self, source="unknown"):
        now = time.time()
        # Debounce: prevent duplicate trigger from dual engines within 280ms
        if now - self.last_trigger_time < 0.28:
            return
        self.last_trigger_time = now
        logging.info(f"F8 Pressed [{source}] in mode: {SETTINGS.get('mode', 'auto_stop')}")

        mode = SETTINGS.get("mode", "auto_stop")
        with self.lock:
            if not self.is_recording:
                threading.Thread(target=self._record_worker, daemon=True).start()
            else:
                # If already recording and running for at least 0.4s, pressing F8 again stops recording
                if (now - self.recording_start_time) > 0.4:
                    logging.info("F8 pressed during active recording -> requested stop.")
                    self.stop_requested = True

    def on_f8_released(self):
        mode = SETTINGS.get("mode", "auto_stop")
        if mode == "push_to_talk" and self.is_recording:
            logging.info("Push-to-Talk: F8 physically released -> stopping recording.")
            self.stop_requested = True

    def _record_worker(self):
        self.is_recording = True
        self.stop_requested = False
        self.recording_start_time = time.time()
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
        self.floating_mic.set_state("recording", "Listening...")

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
            self.floating_mic.set_state("error", "Mic Error")
            self.is_recording = False
            return

        play_sound("stop")
        self.set_tray_icon(ICON_IDLE)
        # Amber dot for transcribing
        self.update_badge("#f59e0b", self._t("transcribing"))
        self.floating_mic.set_state("transcribing", "Converting...")

        if not frames or len(frames) < 3:
            self.update_badge("#64748b", self._t("no_speech"), 2000)
            self.floating_mic.set_state("idle")
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
                self.floating_mic.set_state("success", "Typed!")

                if SETTINGS.get("auto_paste", True):
                    native_paste(text + " ", target_hwnd=self.floating_mic.target_hwnd)
            else:
                self.update_badge("#64748b", self._t("unclear"), 2000)
                self.floating_mic.set_state("error", "Unclear")

        except sr.UnknownValueError:
            play_sound("error")
            self.update_badge("#ef4444", self._t("unclear"), 2200)
            self.floating_mic.set_state("error", "Unclear")
        except sr.RequestError:
            play_sound("error")
            self.update_badge("#f59e0b", self._t("network_err"), 3000)
            self.floating_mic.set_state("error", "Net Error")
        except Exception as e:
            play_sound("error")
            self.update_badge("#ef4444", f"Error: {str(e)[:25]}", 2500)
            self.floating_mic.set_state("error", "Error")
        finally:
            self.is_recording = False

    def open_settings_ui(self):
        self.settings_ui.settings = load_settings()
        self.root.after(0, self.settings_ui.show)

    def init_tray(self):
        def on_exit():
            if self.tray_icon:
                self.tray_icon.stop()
            self.hotkey_engine.stop()
            self.hardware_watcher.stop()
            self.root.after(0, self.root.destroy)

        def toggle_floating_mic(icon, item):
            current = SETTINGS.get("floating_mic", True)
            new_val = not current
            SETTINGS["floating_mic"] = new_val
            save_settings(SETTINGS)
            if new_val:
                self.root.after(0, self.floating_mic.show)
            else:
                self.root.after(0, self.floating_mic.hide)

        menu = pystray.Menu(
            pystray.MenuItem("🎙️ Voice Typer F8", None, enabled=False),
            pystray.MenuItem("✨ Created by Ruhvi2026", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(self._t("tray_open"), self.open_settings_ui, default=True),
            pystray.MenuItem("📌 Show Floating Mic", toggle_floating_mic, checked=lambda item: SETTINGS.get("floating_mic", True)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("⌨️ Hotkey: F8", None, enabled=False),
            pystray.MenuItem(self._t("tray_exit"), on_exit)
        )

        self.tray_icon = pystray.Icon(
            "voice_typer_f8", 
            ICON_IDLE, 
            "Voice Typer F8", 
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
            self.hardware_watcher.stop()

if __name__ == "__main__":
    check_single_instance()
    app = VoiceTyperApp()
    app.run()
