#!/usr/bin/env python3
"""
Fast voice response pipeline for Atlas
Transcribes input audio and generates TTS response in one shot
"""

import os
import sys
from pathlib import Path

# API key from environment or hardcoded fallback
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY must be set in environment")

from openai import OpenAI

# Voice settings
VOICE = "onyx"
SPEED = 1.25
MODEL = "tts-1"  # Faster than tts-1-hd

client = OpenAI()

def transcribe(audio_path: str) -> str:
    """Transcribe audio file to text."""
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    return result.text

def speak(text: str, output_path: str) -> str:
    """Generate speech from text."""
    response = client.audio.speech.create(
        model=MODEL,
        voice=VOICE,
        input=text,
        speed=SPEED
    )
    response.write_to_file(output_path)
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: voice_respond.py <input_audio> <output_audio>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # Transcribe
    transcript = transcribe(input_path)
    print(f"TRANSCRIPT: {transcript}")
    
    # If there's a response text provided as 3rd arg, use it
    if len(sys.argv) > 3:
        response_text = sys.argv[3]
        speak(response_text, output_path)
        print(f"AUDIO: {output_path}")
