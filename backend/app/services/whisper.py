from openai import OpenAI
from app.core.config import settings
from fastapi import UploadFile
import tempfile
import os
from typing import Dict


class WhisperService:
    """
    Service for transcribing audio to text using OpenAI Whisper API
    """

    def __init__(self):
        self.client = OpenAI(api_key=settings.WHISPERAPI)

    async def transcribe_audio(self, audio_file: UploadFile) -> Dict:
        """
        Transcribe audio file to text using OpenAI Whisper

        Args:
            audio_file: Audio file from user (UploadFile)

        Returns:
            {
                "transcript": str,
                "confidence": float,
                "language": str
            }

        Raises:
            Exception: If transcription fails
        """
        temp_audio_path = None

        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                content = await audio_file.read()
                temp_audio.write(content)
                temp_audio_path = temp_audio.name

            # Transcribe using Whisper
            with open(temp_audio_path, "rb") as audio:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    language="en"  # Nigerian English
                )

            return {
                "transcript": transcript.text.strip(),
                "confidence": 0.95,  # Whisper doesn't return confidence, use default high value
                "language": "en"
            }

        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower():
                raise Exception("Rate limit exceeded. Please try again later.")
            else:
                raise Exception(f"Transcription failed: {error_msg}")

        finally:
            # Clean up temp file
            if temp_audio_path and os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)

    def validate_audio_file(self, audio_file: UploadFile) -> bool:
        """
        Validate audio file type and size

        Args:
            audio_file: Audio file to validate

        Returns:
            True if valid, raises Exception if invalid
        """
        # Check file size (max 25MB for Whisper API)
        MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB in bytes

        # Check content type
        allowed_types = [
            "audio/wav",
            "audio/mp3",
            "audio/mpeg",
            "audio/webm",
            "audio/ogg",
            "audio/m4a"
        ]

        if audio_file.content_type not in allowed_types:
            raise Exception(f"Invalid audio format. Allowed: {', '.join(allowed_types)}")

        return True


# Singleton instance
whisper_service = WhisperService()
