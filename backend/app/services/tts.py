"""
Text-to-Speech Service

Converts text responses to audio for voice banking.
Uses pyttsx3 for offline text-to-speech (no API calls needed!)
"""

import pyttsx3
import io
import base64
from typing import Optional
import tempfile
import wave


class TTSService:
    """
    Text-to-Speech service for voice responses using pyttsx3 (offline)
    """

    def __init__(self):
        # Store voice preferences but don't initialize engine here
        # We'll create a fresh engine for each request to avoid blocking
        self.rate = 150
        self.volume = 1.0
        self.preferred_voice_id = None

        # Try to find a female voice ID on first init
        try:
            temp_engine = pyttsx3.init()
            voices = temp_engine.getProperty('voices')
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.preferred_voice_id = voice.id
                    break
            temp_engine.stop()
            del temp_engine
        except:
            pass

    async def text_to_speech(
        self,
        text: str,
        voice: str = "default",  # Ignored for pyttsx3, kept for compatibility
        speed: float = 1.0,
        return_format: str = "base64"  # base64 or file_path
    ) -> dict:
        """
        Convert text to speech audio using pyttsx3 (offline)

        Args:
            text: Text to convert to speech
            voice: Ignored (kept for API compatibility)
            speed: Speech speed multiplier
            return_format: "base64" returns base64 encoded audio, "file_path" returns temp file path

        Returns:
            {
                "success": bool,
                "audio_base64": str (if return_format="base64"),
                "audio_path": str (if return_format="file_path"),
                "text": str,
                "duration_estimate": float (seconds),
                "error": Optional[str]
            }
        """

        try:
            # Create a FRESH engine for this request to avoid blocking
            engine = pyttsx3.init()

            # Configure voice settings
            engine.setProperty('rate', self.rate)
            engine.setProperty('volume', self.volume)

            if self.preferred_voice_id:
                try:
                    engine.setProperty('voice', self.preferred_voice_id)
                except:
                    pass

            # Create a temporary file to save the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                audio_path = temp_audio.name

            # Generate speech and save to file
            engine.save_to_file(text, audio_path)
            engine.runAndWait()

            # Clean up engine
            engine.stop()
            del engine

            # Estimate duration (rough approximation: ~150 words per minute)
            word_count = len(text.split())
            duration_estimate = (word_count / 150) * 60 / speed

            if return_format == "base64":
                # Read the audio file and encode to base64
                with open(audio_path, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

                # Clean up temp file
                import os
                os.unlink(audio_path)

                return {
                    "success": True,
                    "audio_base64": audio_base64,
                    "text": text,
                    "duration_estimate": duration_estimate,
                    "format": "wav",
                    "error": None
                }

            else:  # file_path
                return {
                    "success": True,
                    "audio_path": audio_path,
                    "text": text,
                    "duration_estimate": duration_estimate,
                    "format": "wav",
                    "error": None
                }

        except Exception as e:
            return {
                "success": False,
                "audio_base64": None if return_format == "base64" else None,
                "audio_path": None if return_format == "file_path" else None,
                "text": text,
                "duration_estimate": 0,
                "error": str(e)
            }

    async def generate_banking_responses(self, response_type: str, **kwargs) -> str:
        """
        Generate contextual banking responses

        Args:
            response_type: Type of response (balance, transfer_confirm, transfer_success, etc.)
            **kwargs: Context-specific parameters

        Returns:
            Text response string
        """

        responses = {
            "balance": "Your account balance is {balance} naira.",

            "transfer_initiate": "You're about to send {amount} naira to {recipient}. The total with fees is {total} naira. Please say 'confirm' to proceed or 'cancel' to stop.",

            "transfer_confirm": "Please enter your 4-digit PIN to complete the transfer.",

            "transfer_success": "Transfer successful! You sent {amount} naira to {recipient}. Your new balance is {balance} naira.",

            "transfer_failed": "Sorry, the transfer failed. {reason}. Your balance remains {balance} naira.",

            "insufficient_balance": "You don't have enough money for this transfer. Your balance is {balance} naira but you're trying to send {amount} naira.",

            "limit_exceeded": "This transfer exceeds your daily limit of {limit} naira. Please try a smaller amount.",

            "invalid_pin": "The PIN you entered is incorrect. Please try again.",

            "recipient_not_found": "I couldn't find {recipient} in your saved recipients. Would you like to add them first?",

            "cancel": "Transfer cancelled. Your balance is {balance} naira. How else can I help you?",

            "unknown": "I didn't quite understand that. You can say things like 'check my balance' or 'send money to {example_recipient}'.",

            "error": "Sorry, something went wrong. Please try again or contact support.",

            "session_timeout": "Your session has timed out for security. Please start again.",

            "welcome": "Hello! I'm your voice banking assistant. You can check your balance, send money, or manage your recipients. What would you like to do?",

            "help": "I can help you with transfers, checking your balance, and managing recipients. Try saying 'send money' or 'check my balance'."
        }

        template = responses.get(response_type, responses["unknown"])
        return template.format(**kwargs)


# Singleton instance
tts_service = TTSService()
