"""
Quick 5-Second Voice Test Script
Author: Ruhvi2026 (Project Ruhvi)
Run this to test your laptop's mic and Bengali speech recognition directly in terminal.
"""
import io
import wave
import numpy as np
import sounddevice as sd
import speech_recognition as sr

SAMPLE_RATE = 16000
CHANNELS = 1
DURATION = 5  # seconds

print("=" * 50)
print("🎤 Bangla Voice Recognition Test (5 Seconds)")
print("=" * 50)
print("📢 কথা বলুন (বাংলায়)... ল্যাপটপের মাইক শুনছে...")

audio_data = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=np.int16)
sd.wait()

max_vol = int(abs(audio_data).max())
print(f"✅ রেকর্ডিং সম্পন্ন! (সর্বোচ্চ সাউন্ড লেভেল: {max_vol})")

if max_vol < 200:
    print("⚠️ মাইকের ভলিউম খুবই কম পাওয়া গেছে! ল্যাপটপের মাইকের কাছাকাছি এসে কথা বলুন।")

print("⏳ গুগলে পাঠানো হচ্ছে এবং বাংলায় রূপান্তর করা হচ্ছে...")

wav_buffer = io.BytesIO()
with wave.open(wav_buffer, "wb") as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(audio_data.tobytes())
wav_buffer.seek(0)

recognizer = sr.Recognizer()
try:
    with sr.AudioFile(wav_buffer) as source:
        audio = recognizer.record(source)
    text = recognizer.recognize_google(audio, language="bn-IN")
    print("\n🎉 সফলভাবে রূপান্তরিত টেক্সট:")
    print(f"👉 \"{text}\"")
except sr.UnknownValueError:
    print("\n❌ কথাটি স্পষ্ট বোঝা যায়নি। দয়া করে স্পষ্ট উচ্চারণে আবার চেষ্টা করুন।")
except sr.RequestError as e:
    print(f"\n❌ ইন্টারনেট বা সার্ভিস ত্রুটি: {e}")
except Exception as e:
    print(f"\n❌ ত্রুটি: {e}")

print("=" * 50)
