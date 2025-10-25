"""
Quick TTS Test Script
Tests if pyttsx3 TTS is working
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from app.services.tts import tts_service

async def test_tts():
    print("Testing pyttsx3 TTS...")
    print("-" * 50)

    # Test text
    test_text = "Your account balance is 150,000 naira."

    print(f"Converting to speech: {test_text}")

    # Generate TTS
    result = await tts_service.text_to_speech(
        text=test_text,
        return_format="base64"
    )

    print("\nResult:")
    print(f"  Success: {result['success']}")
    print(f"  Text: {result['text']}")
    print(f"  Format: {result.get('format', 'N/A')}")
    print(f"  Duration: {result.get('duration_estimate', 0):.2f} seconds")

    if result['success']:
        audio_len = len(result['audio_base64']) if result['audio_base64'] else 0
        print(f"  Audio Base64 Length: {audio_len} chars")
        if audio_len > 0:
            print("  ✅ TTS AUDIO GENERATED SUCCESSFULLY!")
        else:
            print("  ❌ TTS audio is empty")
    else:
        print(f"  ❌ ERROR: {result.get('error', 'Unknown error')}")

    print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_tts())
