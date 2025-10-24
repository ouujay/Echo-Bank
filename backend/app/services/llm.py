from openai import OpenAI
from app.core.config import settings
import json
from typing import Dict, Optional


class LLMService:
    """
    Service for parsing user intent from transcribed text using LLM
    """

    def __init__(self):
        # Use Together AI with new OpenAI client
        self.client = OpenAI(
            api_key=settings.TOGETHER_API_KEY,
            base_url="https://api.together.xyz/v1"
        )

    async def parse_intent(self, transcript: str, context: Optional[Dict] = None) -> Dict:
        """
        Parse user intent from transcript using LLM

        Args:
            transcript: Transcribed text from user
            context: Current conversation context (optional)

        Returns:
            {
                "intent": str,  # transfer, check_balance, add_recipient, cancel, confirm, unknown
                "confidence": float,  # 0.0 to 1.0
                "entities": {
                    "action": str,  # send, pay, transfer
                    "recipient": str,  # name of recipient
                    "amount": float,  # amount to send
                    "currency": str  # NGN
                },
                "next_step": str  # verify_recipient, verify_pin, confirm, complete
            }
        """

        # Create system prompt for banking assistant
        system_prompt = """You are a Nigerian banking voice assistant. Parse user commands for money transfers.

Extract these details:
- Intent: transfer, check_balance, add_recipient, cancel, confirm, unknown
- Recipient name (if mentioned)
- Amount (convert words to numbers: "five thousand" → 5000)
- Action type: send, pay, transfer

Common Nigerian phrases:
- "Send" = transfer money
- "Naira" or "N" = NGN currency
- Numbers can be spoken: "five thousand naira" = 5000 NGN

Respond ONLY with valid JSON in this exact format:
{
  "intent": "transfer",
  "confidence": 0.95,
  "entities": {
    "action": "send",
    "recipient": "John",
    "amount": 5000,
    "currency": "NGN"
  },
  "next_step": "verify_recipient"
}

If user says numbers like "1-2-3-4", assume it's a PIN, return intent: "provide_pin"
If user says "confirm", "yes", "proceed", return intent: "confirm"
If user says "cancel", "stop", "no", return intent: "cancel"
If unclear, return intent: "unknown"
"""

        user_prompt = f"User said: '{transcript}'"

        if context:
            user_prompt += f"\n\nContext: {json.dumps(context)}"

        try:
            response = self.client.chat.completions.create(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Low temperature for consistent parsing
                max_tokens=200
            )

            # Parse LLM response
            result_text = response.choices[0].message.content.strip()

            # Extract JSON from response (in case LLM adds extra text)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)

            # Validate required fields
            if "intent" not in result:
                result["intent"] = "unknown"
            if "confidence" not in result:
                result["confidence"] = 0.5
            if "entities" not in result:
                result["entities"] = {}
            if "next_step" not in result:
                result["next_step"] = "clarify"

            return result

        except json.JSONDecodeError as e:
            # LLM didn't return valid JSON
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": {},
                "next_step": "clarify",
                "error": "Failed to parse LLM response"
            }
        except Exception as e:
            # Other errors (API errors, etc.)
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": {},
                "next_step": "clarify",
                "error": str(e)
            }

    def convert_words_to_number(self, text: str) -> Optional[int]:
        """
        Convert spoken numbers to integers
        e.g., "five thousand" → 5000

        Args:
            text: Text containing number words

        Returns:
            Integer value or None if not found
        """
        text = text.lower()

        # Simple word-to-number mapping
        word_to_num = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "hundred": 100, "thousand": 1000, "million": 1000000
        }

        # Try to find numbers in text
        total = 0
        current = 0

        words = text.split()
        for word in words:
            if word in word_to_num:
                num = word_to_num[word]
                if num >= 100:
                    current *= num
                    total += current
                    current = 0
                else:
                    current += num

        total += current
        return total if total > 0 else None


# Singleton instance
llm_service = LLMService()
