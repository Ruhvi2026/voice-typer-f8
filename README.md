# 🎙️ Voice Typer F8

<div align="center">

![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Languages](https://img.shields.io/badge/Languages-125%2B%20Global-success)
![Memory Footprint](https://img.shields.io/badge/RAM-~35MB-blueviolet)
![Hotkeys](https://img.shields.io/badge/Hotkey-F8%20%7C%20Floating%20Mic-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

**World-Class Desktop Speech-to-Text Application for Windows & Antigravity IDE**  
*Ultra-lightweight • Zero-Lag • 125+ Languages • Modern Fluent UI • Draggable Floating Mic*

[English](#-english-overview) • [বাংলা বিবরণ](#-বাংলা-বিবরণ) • [Key Features](#-key-features) • [Installation](#-installation--setup) • [Modes](#-recording-modes) • [Architecture](#-architecture)

---

</div>

## 🌐 English Overview

**Voice Typer F8** is an ultra-fast, professional desktop speech-to-text (dictation) tool engineered specifically for developers, writers, and power users on Windows 10 & 11. It captures audio directly through your laptop or desktop's built-in microphone, recognizes speech via high-accuracy Google Cloud STT across **125+ global languages & dialects**, and automatically pastes the transcribed text directly at your active text cursor.

Whether you are dictating code comments in **Antigravity IDE / VS Code**, typing emails in Chrome, or composing documents in Word or Notepad, Voice Typer F8 operates silently in the background with **near-zero RAM consumption (~35 MB)** and **zero idle CPU usage**.

---

## 🇧🇩 বাংলা বিবরণ

**Voice Typer F8** হলো উইন্ডোজের জন্য একটি বিশ্বমানের প্রফেশনাল স্পিচ-টু-টেক্সট ডেস্কটপ অ্যাপ্লিকেশন। এটি কোনো বাড়তি ফোন বা থার্ড-পার্টি ডিভাইস ছাড়াই সরাসরি আপনার ল্যাপটপ বা কম্পিউটারের বিল্ট-ইন মাইক্রোফোন দিয়ে মুখে বলা কথা শুনে পলকের মধ্যে যেকোনো অ্যাপে (Antigravity IDE, VS Code, Browser, Notepad) স্বয়ংক্রিয়ভাবে টাইপ করে দেয়।

এতে রয়েছে **১২৫টিরও বেশি আন্তর্জাতিক ভাষা**, সম্পূর্ণ কাস্টমাইজযোগ্য ৩টি রেকর্ডিং মোড, আধুনিক **Fluent UI**, এবং একটি **ক্লিকযোগ্য ভাসমান মাইক উইজেট (Floating Mic)**—যা কীবোর্ড ছাড়াও শুধু মাউস দিয়েই কাজ করে।

---

## ✨ Key Features

### 1. 🎙️ Dual Input: Hardware Hotkey (`F8`) + Draggable Floating Mic
* **Global F8 Hotkey:** Trigger dictation from anywhere in Windows with a single press of `F8`.
* **Clickable Floating Mic Widget:** An always-on-top, draggable floating pill widget. Built with Windows **`WS_EX_NOACTIVATE`** architecture so clicking the mic **never steals focus** from your active text cursor! Perfect if your keyboard is inaccessible or you prefer mouse-only control.

### 2. 🎯 3 Adaptive Recording Modes
| Mode | How it Works | Best For |
| :--- | :--- | :--- |
| **⚡ Auto-Stop (Default)** | Press `F8` (or click Mic), speak naturally. Stop talking for a short pause (default `3.2s`) and it auto-converts and pastes. | Long thought dictation, paragraphs, coding. |
| **🎙️ Push-to-Talk** | Hold down `F8` (or click & hold the Floating Mic) while speaking. Release to paste instantly. | Short commands, quick chat replies, terminal commands. |
| **🔄 Manual Toggle** | Press `F8` once to start (take as long as you want). Press `F8` again to stop and paste. | Brainstorming, drafting without timing pressure. |

### 3. 🌍 125+ Global Languages with Dynamic Multilingual UI (i18n)
* **Comprehensive Dialect Support:**
  * **Bengali:** বাংলা (ভারত `bn-IN`, বাংলাদেশ `bn-BD`)
  * **English:** English (India `en-IN`, US `en-US`, UK `en-GB`, Canada `en-CA`, Australia `en-AU`)
  * **Indian Languages:** हिन्दी (Hindi), தமிழ் (Tamil), తెలుగు (Telugu), मराठी (Marathi), ગુજરાતી (Gujarati), ಕನ್ನಡ (Kannada), മലയാളം (Malayalam), ਪੰਜਾਬੀ (Punjabi), اردو (Urdu)
  * **East Asian:** 中文 (Mandarin Simplified `zh-CN`, Traditional `zh-TW`, Cantonese `zh-HK`), 日本語 (Japanese `ja-JP`), 한국어 (Korean `ko-KR`)
  * **Middle Eastern & European:** العربية (Arabic), Español (Spanish), Français (French), Deutsch (German), Русский (Russian), Português (Portuguese), Türkçe (Turkish), and 80+ more.
* **Full Native UI Translation:** When you select Japanese, Chinese, Urdu, Bengali, Hindi, or Russian, the entire application interface (buttons, settings, labels, status badges) instantly switches to that native language.

### 4. 🎨 macOS & Windows 11 Fluent Design System
* **Curved Surface Cards:** Modern rounded cards with soft borders and elevated depths.
* **Segmented Controls:** Sleek iOS-style segmented mode switchers.
* **Dark & Light Themes:** Toggle between deep slate dark mode (`#0f172a`) and crisp daylight mode.
* **Glowing Status Badges:** Floating status pill displaying real-time feedback dots:
  * 🔴 **Red:** Listening / Recording active
  * 🟡 **Amber:** Acoustic processing & Google Cloud transcription
  * 🟢 **Green:** Transcribed & auto-pasted successfully

### 5. ⚡ Kernel-Level Stability & Single-Instance Mutex
* **Dual-Engine F8 Detection:** Combines native Windows `user32.RegisterHotKey` with a low-level `GetAsyncKeyState` hardware polling thread (15ms cycle). Windows never unhooks or disables it, even during high system loads or idle states.
* **Single-Instance Mutex Protection:** Win32 Named Mutex ensures only one instance runs at a time. Launching the shortcut again simply restores focus to the active window without hotkey conflicts.

---

## 🛠️ Architecture

```
                      ┌──────────────────────────────────────────┐
                      │             Voice Typer F8               │
                      └────────────────────┬─────────────────────┘
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
       ┌───────────────────────────┐                 ┌───────────────────────────┐
       │   Dual-Engine Hotkey      │                 │    Floating Mic Widget    │
       │  • RegisterHotKey (Win32) │                 │  • WS_EX_NOACTIVATE       │
       │  • GetAsyncKeyState (15ms)│                 │  • Mouse Drag & Click     │
       └────────────┬──────────────┘                 └─────────────┬─────────────┘
                    │                                             │
                    └──────────────────────┬──────────────────────┘
                                           ▼
                            ┌────────────────────────────┐
                            │    Audio Engine (PyAudio)  │
                            │  • 16 kHz Mono PCM         │
                            │  • Silence Detector (RMS)  │
                            └──────────────┬─────────────┘
                                           ▼
                            ┌────────────────────────────┐
                            │      Google Cloud STT      │
                            │  • 125+ Global Dialects    │
                            │  • Low-Latency Acoustic AI │
                            └──────────────┬─────────────┘
                                           ▼
                            ┌────────────────────────────┐
                            │     Direct Text Inject     │
                            │  • Active Cursor Ctrl+V    │
                            │  • Clipboard Preserved     │
                            └────────────────────────────┘
```

---

## 🚀 Installation & Setup

### Prerequisites
* Windows 10 or Windows 11 (64-bit)
* Python 3.10, 3.11, 3.12, or 3.13
* Working microphone (built-in laptop mic or external headset)
* Active internet connection for Google Speech-to-Text

### 1. Clone the Repository
```bash
git clone https://github.com/Ruhvi2026/voice-typer-f8.git
cd voice-typer-f8
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
* **Standard Launch (with console):**
  ```bash
  python app.py
  ```
* **Silent Background Launch (No Console, System Tray Only):**
  Double-click `start_silent.vbs` or run:
  ```bash
  wscript.exe start_silent.vbs
  ```

---

## 🎮 Controls & Usage

| Action | Control | Function |
| :--- | :--- | :--- |
| **Start / Stop Dictation** | Press `F8` on Keyboard | Toggles voice dictation based on active mode. |
| **Click to Dictate** | Left-Click Floating Mic | Starts dictation without touching the keyboard. |
| **Move Floating Mic** | Left-Click & Drag | Moves the floating mic anywhere on screen. |
| **Quick Menu** | Right-Click Floating Mic | Opens Control Center or hides the mic. |
| **Open Settings** | Tray Icon Double-Click | Opens the Fluent Control Center GUI. |
| **Close / Exit** | Tray Icon Right-Click ➔ Exit | Safely closes the background process. |

---

## ⚙️ Configuration (`settings.json`)

Settings are automatically saved in `settings.json`:

```json
{
  "mode": "auto_stop",
  "language": "bn-IN",
  "theme": "dark",
  "sound_effects": true,
  "floating_badge": true,
  "floating_mic": true,
  "floating_mic_x": 1775,
  "floating_mic_y": 75,
  "silence_seconds": 3.2,
  "max_seconds": 45,
  "auto_paste": true,
  "hotkey": "f8"
}
```

* `mode`: `"auto_stop"`, `"push_to_talk"`, or `"toggle"`.
* `language`: Any supported locale code (e.g., `"bn-IN"`, `"en-US"`, `"hi-IN"`, `"zh-CN"`, `"ja-JP"`).
* `theme`: `"dark"` or `"light"`.
* `silence_seconds`: Pause duration in seconds before auto-stopping (recommended `2.5` – `3.5`).
* `floating_mic`: `true` to display the on-screen clickable mic widget.

---

## 📦 Project Structure

```
voice-typer-f8/
├── app.py                # Main background runner, audio engine & hotkey listeners
├── settings_ui.py        # CustomTkinter Fluent Control Center & Language Picker
├── languages_data.py     # 125+ language catalog and native multi-language translations
├── requirements.txt      # Python dependencies
├── start_silent.vbs      # VBScript runner for silent background execution
├── icon.ico              # High-resolution application icon
├── icon.png              # PNG icon asset
├── settings.json         # User preferences and geometry configuration
└── README.md             # Complete project documentation
```

---

## 💡 Troubleshooting

* **F8 Key Conflict with Laptop Function Keys:**  
  On some laptops, function keys (F1–F12) default to media controls (Volume, Brightness). If pressing F8 adjusts screen settings, press `Fn + Esc` to enable **Fn-Lock**, or simply click the **Floating Mic Widget** with your mouse!
* **Microphone Permissions:**  
  Ensure Windows Settings ➔ *Privacy & Security* ➔ *Microphone* has **"Let desktop apps access your microphone"** toggled **ON**.
* **Audio Not Recognizing:**  
  Check if your input microphone is active in Windows Sound Settings. Voice Typer F8 auto-calibrates ambient room noise within 150ms of activation.

---

## ✍️ Author & Credits

**Designed & Developed with ❤️ by [Ruhvi2026](https://github.com/Ruhvi2026)**  
*Project Ruhvi • 2026*  
*GitHub Repository: [https://github.com/Ruhvi2026/voice-typer-f8](https://github.com/Ruhvi2026/voice-typer-f8)*
