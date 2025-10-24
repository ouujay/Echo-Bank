"""
Text-to-Speech Service

Converts text responses to audio for voice banking.
Uses OpenAI TTS API for natural-sounding Nigerian English.
"""

from openai import OpenAI
from app.core.config import settings
from typing import Optional
import tempfile
import base64


class TTSService:
    """
    Text-to-Speech service for voice responses
    """

    def __init__(self):
        self.client = OpenAI(api_key=settings.WHISPERAPI)

    async def text_to_speech(
        self,
        text: str,
        voice: str = "nova",  # nova, alloy, echo, fable, onyx, shimmer
        speed: float = 1.0,
        return_format: str = "base64"  # base64 or file_path
    ) -> dict:
        """
        Convert text to speech audio

        Args:
            text: Text to convert to speech
            voice: Voice to use (nova is good for Nigerian English)
            speed: Speech speed (0.25 to 4.0)
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
            # Generate speech using OpenAI TTS
            response = self.client.audio.speech.create(
                model="tts-1",  # tts-1 or tts-1-hd (HD is higher quality, slower)
                voice=voice,
                input=text,
                speed=speed
            )

            # Estimate duration (rough approximation: ~150 words per minute at speed 1.0)
            word_count = len(text.split())
            duration_estimate = (word_count / 150) * 60 / speed

            if return_format == "base64":
                # Return base64 encoded audio
                audio_bytes = response.content
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

                return {
                    "success": True,
                    "audio_base64": audio_base64,
                    "text": text,
                    "duration_estimate": duration_estimate,
                    "format": "mp3",
                    "error": None
                }

            else:  # file_path
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                    temp_audio.write(response.content)
                    audio_path = temp_audio.name

                return {
                    "success": True,
                    "audio_path": audio_path,
                    "text": text,
                    "duration_estimate": duration_estimate,
                    "format": "mp3",
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
