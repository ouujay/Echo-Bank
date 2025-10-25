from openai import OpenAI
from app.core.config import settings
import json
from typing import Dict, Optional


class LLMService:
    """
    Service for parsing user intent from transcribed text using LLM
    Updated: 2025-10-25
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
        system_prompt = """You are an intelligent Nigerian banking voice assistant with natural language understanding.

CRITICAL: You MUST accurately identify these intents. Do NOT return "unknown" unless absolutely necessary.

SUPPORTED INTENTS:
1. check_balance - User wants to know their account balance
   Examples: "What's my balance?", "How much do I have?", "Check balance", "How much money?", "show me my account balance", "what is my balance", "balance"

2. view_recipients - User wants to see saved beneficiaries (IMPORTANT!)
   Examples: "Show recipients", "show my recipients", "Who can I send to?", "List beneficiaries", "Show my people", "display recipients", "view recipients", "see recipients", "my recipients", "recipients list", "who are my beneficiaries"

3. view_transactions - User wants transaction history
   Examples: "Show transactions", "Recent transfers", "Transaction history", "What did I spend?", "view transactions", "my transactions"

4. transfer - User wants to send money
   Examples: "Send 5000 to John", "Transfer money to Mary", "Pay Sarah", "Give John 10000"
   Extract: recipient name, amount

5. add_recipient - User wants to add new beneficiary
   Examples: "Add recipient", "Save new person", "Add John", "Save beneficiary"
   Extract: recipient name, account number (if mentioned)

6. provide_pin - User is saying their PIN (numbers)
   Examples: "1234", "one two three four", "my pin is 5678"
   Extract: PIN as string

7. confirm - User agrees/confirms action
   Examples: "Yes", "Confirm", "Proceed", "Go ahead", "Do it", "Okay", "Correct", "That's right"

8. cancel - User wants to stop/cancel
   Examples: "Cancel", "Stop", "No", "Never mind", "Don't do it", "Abort"

9. greeting - User greets or makes small talk
   Examples: "Hello", "Hi", "Good morning", "How are you?", "Thanks", "Thank you"

10. help - User needs assistance
    Examples: "Help", "What can you do?", "How does this work?", "Commands"

11. unknown - Cannot understand user request

NATURAL LANGUAGE UNDERSTANDING:
- Parse ALL variations of commands naturally
- "Send John 5000" = transfer, recipient: John, amount: 5000
- "Can you send 10000 to Mary" = transfer, recipient: Mary, amount: 10000
- "I want to transfer five thousand naira to John" = transfer, recipient: John, amount: 5000
- "Check my account" = check_balance
- "show me my account balance" = check_balance
- "Who are my recipients" = view_recipients
- "show my recipients" = view_recipients (IMPORTANT!)
- "show recipients" = view_recipients (IMPORTANT!)
- "What transactions have I made" = view_transactions
- "view transactions" = view_transactions

KEY MATCHING RULES:
- If user says ANY variation of "show/view/display/list/see" + "recipient/beneficiary/people" = view_recipients
- If user says ANY variation of "show/view/display" + "transaction/transfer/history" = view_transactions
- If user says ANY variation of "check/show/what is" + "balance/money/account" = check_balance

NIGERIAN CONTEXT:
- Currency: NGN/Naira
- Convert spoken numbers: "five thousand" → 5000, "ten k" → 10000
- Names are case-insensitive: john, John, JOHN all same
- "Send" = "Transfer" = "Pay" = "Give" all mean transfer

CONTEXT AWARENESS:
- If context shows pending_transfer, look for: confirm, cancel, or provide_pin
- If context shows awaiting_pin, user saying numbers = provide_pin
- If context has recipient_name but no amount, extract amount from new input
- If context has amount but no recipient, extract recipient from new input

OUTPUT FORMAT - CRITICAL: Return ONLY valid JSON, NO explanations or extra text:
{
  "intent": "transfer",
  "confidence": 0.95,
  "entities": {
    "recipient": "John",
    "amount": 5000,
    "currency": "NGN",
    "pin": null,
    "account_number": null
  },
  "next_step": "verify_recipient"
}

DO NOT add any explanation text after the JSON. ONLY return the JSON object above.

NEXT_STEP values:
- verify_recipient: Found recipient, need to check if exists
- request_amount: Have recipient, need amount
- request_pin: Ready to transfer, need PIN
- confirm_transfer: Have all details, need user confirmation
- complete: Action complete
- clarify: Need more information
"""

        user_prompt = f"User said: '{transcript}'"

        if context:
            user_prompt += f"\n\nContext: {json.dumps(context)}"

        try:
            response = self.client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Low temperature for consistent parsing
                max_tokens=200
            )

            # Parse LLM response
            result_text = response.choices[0].message.content.strip()

            print(f"[LLM DEBUG] Raw LLM response: {result_text}")

            # Extract JSON from response (in case LLM adds extra text)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            else:
                # Handle case where LLM returns JSON followed by explanation text
                # Find the first { and the last } to extract just the JSON
                start_idx = result_text.find('{')
                if start_idx != -1:
                    # Count braces to find matching closing brace
                    brace_count = 0
                    end_idx = -1
                    for i in range(start_idx, len(result_text)):
                        if result_text[i] == '{':
                            brace_count += 1
                        elif result_text[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i + 1
                                break

                    if end_idx != -1:
                        result_text = result_text[start_idx:end_idx]

            result = json.loads(result_text)

            print(f"[LLM DEBUG] Parsed JSON result: {result}")

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
            print(f"[LLM ERROR] JSON parsing failed: {e}")
            print(f"[LLM ERROR] Raw response was: {result_text}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": {},
                "next_step": "clarify",
                "error": f"Failed to parse LLM response: {str(e)}"
            }
        except Exception as e:
            # Other errors (API errors, etc.)
            print(f"[LLM ERROR] Exception occurred: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"[LLM ERROR] Full traceback: {traceback.format_exc()}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": {},
                "next_step": "clarify",
                "error": f"{type(e).__name__}: {str(e)}"
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
