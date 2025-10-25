"""
Voice Orchestration API

This is the main integration point for banks using EchoBank.
Banks call these endpoints to add voice intelligence to their apps.

Integration Flow:
    1. User speaks in bank app
    2. Bank sends audio to /voice/process
    3. EchoBank transcribes + recognizes intent + executes via bank API
    4. Returns what to say back + next action
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Header, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.services.whisper import whisper_service
from app.services.llm import llm_service
from app.services.tts import tts_service
from app.services.company_api_client import CompanyAPIClient
from app.core.database import get_db
from app.utils.session import session_store
import base64

router = APIRouter(prefix="/api/v1/voice", tags=["Voice Orchestration"])


class VoiceRequest(BaseModel):
    """Request for text-based voice command"""
    text: str
    account_number: str
    company_id: int  # Which bank/company is making the request
    session_id: Optional[str] = None
    token: Optional[str] = None  # User's auth token from the bank
    include_audio: bool = False  # Include TTS audio in response


class TTSRequest(BaseModel):
    """Request for text-to-speech conversion"""
    text: str
    voice: Optional[str] = "nova"  # nova, alloy, echo, fable, onyx, shimmer
    speed: Optional[float] = 1.0


class VoiceResponse(BaseModel):
    """Response from voice processing"""
    success: bool
    session_id: str
    intent: str
    response_text: str  # What to say back to user
    response_audio: Optional[str] = None  # Base64 encoded audio (if include_audio=True)
    action: Optional[str] = None  # next_action: confirm_transfer, input_pin, etc
    data: Optional[Dict[str, Any]] = None  # Additional context
    error: Optional[str] = None


@router.post("/process-audio", response_model=VoiceResponse)
async def process_voice_audio(
    audio: UploadFile = File(...),
    account_number: str = Header(..., alias="account-number"),
    company_id: int = Header(..., alias="company-id"),
    session_id: Optional[str] = Header(None, alias="session-id"),
    token: Optional[str] = Header(None),
    include_audio: Optional[str] = Header(None, alias="include-audio"),  # For TTS response
    db: Session = Depends(get_db)
):
    """
    Process voice audio and execute banking action

    Integration Example:
        ```
        const formData = new FormData();
        formData.append('audio', audioBlob);

        const response = await fetch('/api/v1/voice/process-audio', {
            method: 'POST',
            headers: {
                'account_number': '0123456789',
                'session_id': sessionId,
                'token': userAuthToken
            },
            body: formData
        });
        ```

    Returns:
        Voice response with what to say back and next action
    """
    import time
    request_start = time.time()

    try:
        # Step 1: Transcribe audio
        whisper_start = time.time()
        transcription = await whisper_service.transcribe_audio(audio)
        transcript_text = transcription["transcript"]
        whisper_time = time.time() - whisper_start
        print(f"[TIMING] Whisper transcription took: {whisper_time:.2f}s")

        # Step 2: Process as text
        # Convert include_audio header to boolean
        should_include_audio = include_audio and include_audio.lower() in ['true', '1', 'yes']

        print(f"[TTS DEBUG] include_audio header: {include_audio}")
        print(f"[TTS DEBUG] should_include_audio: {should_include_audio}")

        processing_start = time.time()
        result = await process_voice_text(
            request=VoiceRequest(
                text=transcript_text,
                account_number=account_number,
                company_id=company_id,
                session_id=session_id,
                token=token,
                include_audio=should_include_audio
            ),
            db=db
        )

        processing_time = time.time() - processing_start
        total_time = time.time() - request_start
        print(f"[TIMING] Processing (LLM + API + TTS) took: {processing_time:.2f}s")
        print(f"[TIMING] ⏱️  TOTAL REQUEST TIME: {total_time:.2f}s")

        return result

    except Exception as e:
        return VoiceResponse(
            success=False,
            session_id=session_id or "error",
            intent="error",
            response_text="Sorry, I couldn't understand that. Please try again.",
            error=str(e)
        )


@router.post("/process-text", response_model=VoiceResponse)
async def process_voice_text(request: VoiceRequest, db: Session = Depends(get_db)):
    """
    Process text command (for testing or text-based input)

    Integration Example:
        ```
        const response = await fetch('/api/v1/voice/process-text', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                text: "Send five thousand naira to John",
                account_number: "0123456789",
                company_id: 1,
                session_id: sessionId,
                token: userToken
            })
        });
        ```
    """
    try:
        # Initialize company API client with the bank's configured endpoints
        api_client = CompanyAPIClient(company_id=request.company_id, db=db)

        # Get or create session
        session_id = request.session_id or f"session_{request.account_number}"
        session_data = session_store.get(session_id) or {}

        # Check if we're in recipient disambiguation mode
        if session_data.get("pending_recipients"):
            pending_recipients = session_data["pending_recipients"]
            pending_amount = session_data.get("pending_amount")

            # Find which recipient the user selected
            selected_recipient = None
            user_input_lower = request.text.lower()

            for recipient in pending_recipients:
                if user_input_lower in recipient["name"].lower() or recipient["name"].lower() in user_input_lower:
                    selected_recipient = recipient
                    break

            if selected_recipient:
                # Clear disambiguation state
                session_data.pop("pending_recipients", None)

                # Initiate transfer with selected recipient
                transfer_result = await api_client.initiate_transfer(
                    sender_account=request.account_number,
                    recipient_account=selected_recipient["account_number"],
                    bank_code=selected_recipient["bank_code"],
                    amount=pending_amount,
                    narration=f"Transfer to {selected_recipient['name']}",
                    user_token=request.token or "demo_token"
                )

                if not transfer_result["success"]:
                    return VoiceResponse(
                        success=False,
                        session_id=session_id,
                        intent="transfer",
                        response_text=f"Sorry, I couldn't start the transfer. {transfer_result['error']}",
                        error=transfer_result["error"]
                    )

                # Save transfer info to session
                session_data["pending_transfer"] = {
                    "transfer_id": transfer_result["transfer_id"],
                    "recipient_name": selected_recipient["name"],
                    "amount": float(pending_amount),
                    "fee": float(transfer_result["fee"]),
                    "total": float(transfer_result["total"])
                }
                session_store.set(session_id, session_data)

                return VoiceResponse(
                    success=True,
                    session_id=session_id,
                    intent="transfer",
                    response_text=f"You're about to send {pending_amount} naira to {selected_recipient['name']}. The total with fees is {transfer_result['total']} naira. Please confirm by saying 'confirm' or enter your PIN.",
                    action="confirm_transfer",
                    data={
                        "transfer_id": transfer_result["transfer_id"],
                        "recipient_name": selected_recipient["name"],
                        "amount": float(pending_amount),
                        "fee": float(transfer_result["fee"]),
                        "total": float(transfer_result["total"])
                    }
                )
            else:
                # User didn't select a valid recipient
                names_list = ", ".join([r.get("recipient_name", r.get("name", "Unknown")) for r in pending_recipients])
                return VoiceResponse(
                    success=True,
                    session_id=session_id,
                    intent="disambiguate_recipient",
                    response_text=f"I didn't understand which recipient you meant. Please choose from: {names_list}",
                    action="select_recipient",
                    data={"recipients": pending_recipients}
                )

        # Step 1: Parse intent with LLM
        import time
        llm_start = time.time()
        intent_result = await llm_service.parse_intent(
            request.text,
            context=session_data
        )
        llm_time = time.time() - llm_start
        print(f"[TIMING] LLM intent parsing took: {llm_time:.2f}s")

        intent = intent_result.get("intent", "unknown")
        entities = intent_result.get("entities", {})
        confidence = intent_result.get("confidence", 0.0)

        # DEBUG LOGGING - Track intent recognition (no emojis for Windows compatibility)
        print(f"\n{'='*60}")
        print(f"[TRANSCRIPT] User said: '{request.text}'")
        print(f"[INTENT] LLM parsed as: {intent}")
        print(f"[CONFIDENCE] Score: {confidence}")
        print(f"[ENTITIES] Extracted: {entities}")
        print(f"{'='*60}\n")

        # Update session
        session_data["last_transcript"] = request.text
        session_data["last_intent"] = intent
        session_data["entities"] = entities

        # Step 2: Check for global interrupts first
        if intent == "cancel":
            response = await handle_cancel_intent(request, session_data, session_id, api_client)
        elif intent == "start_over" or request.text.lower() in ["start over", "restart", "begin again"]:
            response = await handle_start_over_intent(request, session_data, session_id, api_client)

        # Step 3: Execute based on intent
        elif intent == "transfer":
            response = await handle_transfer_intent(
                request, session_data, entities, session_id, api_client
            )

        elif intent == "check_balance":
            response = await handle_balance_intent(
                request, session_data, session_id, api_client
            )

        elif intent == "add_recipient":
            response = await handle_add_recipient_intent(
                request, session_data, entities, session_id, api_client
            )

        elif intent == "confirm":
            response = await handle_confirm_intent(
                request, session_data, session_id, api_client
            )

        elif intent == "provide_pin":
            response = await handle_pin_intent(
                request, session_data, entities, session_id, api_client
            )

        elif intent == "view_recipients":
            response = await handle_view_recipients_intent(
                request, session_data, session_id, api_client
            )

        elif intent == "view_transactions":
            response = await handle_view_transactions_intent(
                request, session_data, session_id, api_client
            )

        elif intent == "greeting":
            response = VoiceResponse(
                success=True,
                session_id=session_id,
                intent="greeting",
                response_text="Hello! I'm your voice banking assistant. I can help you check your balance, send money, view recipients, or check transactions. What would you like to do?",
                action="ready"
            )

        elif intent == "help":
            response = VoiceResponse(
                success=True,
                session_id=session_id,
                intent="help",
                response_text="I can help you with: checking your balance, sending money to saved recipients, viewing your recipients, checking transaction history, or adding new recipients. Just tell me what you'd like to do!",
                action="ready"
            )

        else:
            # Fallback: keyword matching when LLM returns unknown
            text_lower = request.text.lower()

            # Check for balance keywords
            if any(word in text_lower for word in ["balance", "money", "account", "how much"]):
                return await handle_check_balance(request, session_data, session_id, api_client)

            # Check for recipients keywords
            elif any(word in text_lower for word in ["recipient", "beneficiar", "people", "send to", "who can"]):
                return await handle_view_recipients(request, session_data, session_id, api_client)

            # Check for transactions keywords
            elif any(word in text_lower for word in ["transaction", "history", "spent", "payment"]):
                return await handle_view_transactions(request, session_data, session_id, api_client)

            # Check for transfer/send money keywords
            elif any(word in text_lower for word in ["send", "transfer", "pay", "give"]):
                # Try to extract recipient and amount from text
                entities = {}
                # Simple extraction - look for names and numbers
                words = request.text.split()
                for i, word in enumerate(words):
                    # Check if it's a number (amount)
                    if word.replace(',', '').replace('.', '').isdigit():
                        entities["amount"] = float(word.replace(',', ''))
                    # Check if it's a name (capitalized word after 'to')
                    elif i > 0 and words[i-1].lower() == "to" and word[0].isupper():
                        entities["recipient"] = word

                return await handle_transfer_intent(request, session_data, entities, session_id, api_client)

            # If no keywords match, return unknown
            response = VoiceResponse(
                success=True,
                session_id=session_id,
                intent="unknown",
                response_text="I didn't quite understand that. Could you please rephrase your request?",
                action="clarify"
            )

        # Step 4: Add audio to response if requested
        session_data["last_response_text"] = response.response_text
        session_store.set(session_id, session_data)

        print(f"[TTS DEBUG] request.include_audio = {request.include_audio}")
        if request.include_audio:
            import time
            tts_start = time.time()
            print(f"[TTS DEBUG] Generating TTS for: {response.response_text[:50]}...")
            response = await add_audio_to_response(response, True)
            tts_time = time.time() - tts_start
            print(f"[TIMING] TTS audio generation took: {tts_time:.2f}s")
            print(f"[TTS DEBUG] TTS generated, response_audio present: {response.response_audio is not None}")
        else:
            print(f"[TTS DEBUG] Skipping TTS - include_audio is False")

        return response

    except Exception as e:
        return VoiceResponse(
            success=False,
            session_id=request.session_id or "error",
            intent="error",
            response_text="Sorry, something went wrong. Please try again.",
            error=str(e)
        )


async def handle_transfer_intent(
    request: VoiceRequest,
    session_data: Dict,
    entities: Dict,
    session_id: str,
    api_client: CompanyAPIClient
) -> VoiceResponse:
    """Handle transfer intent"""

    recipient_name = entities.get("recipient")
    amount = entities.get("amount")

    if not recipient_name or not amount:
        session_store.set(session_id, session_data)
        return VoiceResponse(
            success=True,
            session_id=session_id,
            intent="transfer",
            response_text="I can help you with that transfer. Who would you like to send money to and how much?",
            action="clarify_transfer"
        )

    # Get recipients from bank's API using their configured endpoint
    recipients_result = await api_client.get_recipients(
        account_number=request.account_number,
        user_token=request.token or "demo_token"
    )

    if not recipients_result["success"]:
        return VoiceResponse(
            success=False,
            session_id=session_id,
            intent="transfer",
            response_text="I couldn't access your recipients. Please try again.",
            error=recipients_result["error"]
        )

    # Find matching recipients (may be multiple)
    recipients = recipients_result["recipients"]
    matched_recipients = []

    for r in recipients:
        name = r.get("recipient_name", r.get("name", ""))
        if recipient_name.lower() in name.lower():
            matched_recipients.append(r)

    # No matches found
    if not matched_recipients:
        return VoiceResponse(
            success=True,
            session_id=session_id,
            intent="transfer",
            response_text=f"I couldn't find {recipient_name} in your recipients. Would you like to add them first?",
            action="add_recipient"
        )

    # Multiple matches - need disambiguation
    if len(matched_recipients) > 1:
        session_data["pending_recipients"] = matched_recipients
        session_data["pending_amount"] = amount
        session_store.set(session_id, session_data)

        # Build list of names
        names_list = ", ".join([r.get("recipient_name", r.get("name", "Unknown")) for r in matched_recipients])
        return VoiceResponse(
            success=True,
            session_id=session_id,
            intent="disambiguate_recipient",
            response_text=f"I found multiple recipients: {names_list}. Which one would you like to send to?",
            action="select_recipient",
            data={"recipients": matched_recipients}
        )

    # Single match found
    matched_recipient = matched_recipients[0]

    # Initiate transfer using bank's API
    transfer_result = await api_client.initiate_transfer(
        sender_account=request.account_number,
        recipient_account=matched_recipient["account_number"],
        bank_code=matched_recipient["bank_code"],
        amount=amount,
        narration=f"Transfer to {matched_recipient['name']}",
        user_token=request.token or "demo_token"
    )

    if not transfer_result["success"]:
        return VoiceResponse(
            success=False,
            session_id=session_id,
            intent="transfer",
            response_text=f"Sorry, I couldn't start the transfer. {transfer_result['error']}",
            error=transfer_result["error"]
        )

    # Save transfer info to session
    session_data["pending_transfer"] = {
        "transfer_id": transfer_result["transfer_id"],
        "recipient_name": matched_recipient["name"],
        "amount": float(amount),
        "fee": float(transfer_result["fee"]),
        "total": float(transfer_result["total"])
    }
    session_store.set(session_id, session_data, expire_minutes=5)

    return VoiceResponse(
        success=True,
        session_id=session_id,
        intent="transfer",
        response_text=f"You're about to send {amount} naira to {matched_recipient['name']}. The total with fees is {transfer_result['total']} naira. Please confirm by saying 'confirm' or enter your PIN.",
        action="confirm_transfer",
        data=session_data["pending_transfer"]
    )


async def handle_balance_intent(
    request: VoiceRequest,
    session_data: Dict,
    session_id: str,
    api_client: CompanyAPIClient
) -> VoiceResponse:
    """Handle check balance intent"""

    balance_result = await api_client.get_balance(
        account_number=request.account_number,
        user_token=request.token or "demo_token"
    )

    if not balance_result["success"]:
        return VoiceResponse(
            success=False,
            session_id=session_id,
            intent="check_balance",
            response_text="Sorry, I couldn't check your balance. Please try again.",
            error=balance_result["error"]
        )

    balance = balance_result["balance"]

    session_store.set(session_id, session_data)

    return VoiceResponse(
        success=True,
        session_id=session_id,
        intent="check_balance",
        response_text=f"Your account balance is {balance:,.2f} naira.",
        action="complete",
        data={"balance": float(balance)}
    )


async def handle_confirm_intent(
    request: VoiceRequest,
    session_data: Dict,
    session_id: str,
    api_client: CompanyAPIClient
) -> VoiceResponse:
    """Handle confirmation"""

    pending_transfer = session_data.get("pending_transfer")

    if not pending_transfer:
        return VoiceResponse(
            success=True,
            session_id=session_id,
            intent="confirm",
            response_text="There's nothing to confirm. Would you like to make a transfer?",
            action="clarify"
        )

    # Ask for PIN
    session_data["awaiting_pin"] = True
    session_store.set(session_id, session_data, expire_minutes=2)

    return VoiceResponse(
        success=True,
        session_id=session_id,
        intent="confirm",
        response_text="Please enter your 4-digit PIN to complete the transfer.",
        action="request_pin",
        data=pending_transfer
    )


async def handle_pin_intent(
    request: VoiceRequest,
    session_data: Dict,
    entities: Dict,
    session_id: str,
    api_client: CompanyAPIClient
) -> VoiceResponse:
    """Handle PIN entry"""

    pending_transfer = session_data.get("pending_transfer")

    if not pending_transfer:
        return VoiceResponse(
            success=False,
            session_id=session_id,
            intent="provide_pin",
            response_text="No pending transfer found. Please start a new transfer.",
            action="clarify"
        )

    # Extract PIN from transcript (e.g., "1-2-3-4")
    pin = request.text.replace(" ", "").replace("-", "")

    # Confirm transfer with PIN using bank's API
    confirm_result = await api_client.confirm_transfer(
        transfer_id=pending_transfer["transfer_id"],
        pin=pin,
        user_token=request.token or "demo_token"
    )

    if not confirm_result["success"]:
        return VoiceResponse(
            success=False,
            session_id=session_id,
            intent="provide_pin",
            response_text=f"Transfer failed. {confirm_result['error']}",
            action="retry_pin",
            error=confirm_result["error"]
        )

    # Clear session
    session_data.pop("pending_transfer", None)
    session_data.pop("awaiting_pin", None)
    session_store.set(session_id, session_data)

    return VoiceResponse(
        success=True,
        session_id=session_id,
        intent="transfer_complete",
        response_text=f"Transfer successful! {pending_transfer['amount']} naira sent to {pending_transfer['recipient_name']}. Your new balance is {confirm_result['new_balance']:,.2f} naira.",
        action="complete",
        data={
            "transaction_ref": confirm_result["transaction_ref"],
            "new_balance": float(confirm_result["new_balance"])
        }
    )


async def handle_cancel_intent(
    request: VoiceRequest,
    session_data: Dict,
    session_id: str,
    api_client: CompanyAPIClient
) -> VoiceResponse:
    """Handle cancellation"""

    pending_transfer = session_data.get("pending_transfer")

    if pending_transfer:
        # Cancel the transfer using bank's API
        await api_client.cancel_transfer(
            transfer_id=pending_transfer["transfer_id"],
            token=request.token or "demo_token"
        )

    # Clear session
    session_store.delete(session_id)

    return VoiceResponse(
        success=True,
        session_id=session_id,
        intent="cancel",
        response_text="Transfer cancelled. How else can I help you?",
        action="complete"
    )


async def handle_start_over_intent(
    request: VoiceRequest,
    session_data: Dict,
    session_id: str,
    api_client: CompanyAPIClient
) -> VoiceResponse:
    """Handle start over / restart"""

    pending_transfer = session_data.get("pending_transfer")

    if pending_transfer:
        # Cancel any pending transfer using bank's API
        await api_client.cancel_transfer(
            transfer_id=pending_transfer["transfer_id"],
            token=request.token or "demo_token"
        )

    # Clear session but keep session_id
    session_store.delete(session_id)

    # Get balance for context using bank's API
    balance_result = await api_client.get_balance(
        account_number=request.account_number,
        user_token=request.token or "demo_token"
    )

    balance_text = ""
    if balance_result["success"]:
        balance_text = f" Your balance is {balance_result['balance']:,.2f} naira."

    return VoiceResponse(
        success=True,
        session_id=session_id,
        intent="start_over",
        response_text=f"Okay, let's start over.{balance_text} What would you like to do? You can check your balance, send money, or manage recipients.",
        action="welcome"
    )


async def handle_add_recipient_intent(
    request: VoiceRequest,
    session_data: Dict,
    entities: Dict,
    session_id: str,
    api_client: CompanyAPIClient
) -> VoiceResponse:
    """Handle adding recipient"""

    # This would require more conversation context
    # For now, guide user to add via regular UI

    return VoiceResponse(
        success=True,
        session_id=session_id,
        intent="add_recipient",
        response_text="To add a new recipient, please use the 'Add Recipient' option in your app. Then you can send money to them using voice.",
        action="redirect_to_ui"
    )


async def handle_view_recipients_intent(
    request: VoiceRequest,
    session_data: Dict,
    session_id: str,
    api_client: CompanyAPIClient
) -> VoiceResponse:
    """Handle viewing recipients/beneficiaries"""

    try:
        # Get recipients from company API
        recipients_result = await api_client.get_recipients(
            account_number=request.account_number,
            user_token=request.token or "demo_token"
        )

        if not recipients_result["success"]:
            return VoiceResponse(
                success=False,
                session_id=session_id,
                intent="view_recipients",
                response_text="Sorry, I couldn't fetch your recipients at the moment. Please try again.",
                error=recipients_result.get("error")
            )

        recipients = recipients_result.get("recipients", [])

        if not recipients:
            return VoiceResponse(
                success=True,
                session_id=session_id,
                intent="view_recipients",
                response_text="You don't have any saved recipients yet. You can add recipients in your app, then send money to them using voice.",
                action="complete",
                data={"recipients": []}
            )

        # Format recipient list for speech
        if len(recipients) == 1:
            name = recipients[0].get("recipient_name", recipients[0].get("name", "Unknown"))
            response_text = f"You have one saved recipient: {name}."
        elif len(recipients) <= 5:
            names = ", ".join([r.get("recipient_name", r.get("name", "Unknown")) for r in recipients[:-1]])
            last_name = recipients[-1].get("recipient_name", recipients[-1].get("name", "Unknown"))
            response_text = f"You have {len(recipients)} saved recipients: {names}, and {last_name}."
        else:
            names = ", ".join([r.get("recipient_name", r.get("name", "Unknown")) for r in recipients[:5]])
            response_text = f"You have {len(recipients)} saved recipients. The first few are: {names}, and {len(recipients) - 5} more."

        return VoiceResponse(
            success=True,
            session_id=session_id,
            intent="view_recipients",
            response_text=response_text,
            action="complete",
            data={"recipients": recipients}
        )

    except Exception as e:
        return VoiceResponse(
            success=False,
            session_id=session_id,
            intent="view_recipients",
            response_text="Sorry, I encountered an error fetching your recipients.",
            error=str(e)
        )


async def handle_view_transactions_intent(
    request: VoiceRequest,
    session_data: Dict,
    session_id: str,
    api_client: CompanyAPIClient
) -> VoiceResponse:
    """Handle viewing transaction history"""

    try:
        # Get transactions from company API
        transactions_result = await api_client.get_transactions(
            account_number=request.account_number,
            user_token=request.token or "demo_token"
        )

        if not transactions_result["success"]:
            return VoiceResponse(
                success=False,
                session_id=session_id,
                intent="view_transactions",
                response_text="Sorry, I couldn't fetch your transactions at the moment. Please try again.",
                error=transactions_result.get("error")
            )

        transactions = transactions_result.get("transactions", [])

        if not transactions:
            return VoiceResponse(
                success=True,
                session_id=session_id,
                intent="view_transactions",
                response_text="You don't have any transactions yet.",
                action="complete",
                data={"transactions": []}
            )

        # Get most recent transactions
        recent = transactions[:3]  # Last 3 transactions

        # Format transaction summary for speech
        transaction_summaries = []
        for txn in recent:
            txn_type = txn.get("transaction_type", "transaction")
            amount = txn.get("amount", 0)
            recipient = txn.get("recipient_name", "")

            if txn_type == "transfer" and recipient:
                transaction_summaries.append(f"Transfer of {amount} naira to {recipient}")
            elif txn_type == "credit":
                transaction_summaries.append(f"Credit of {amount} naira")
            else:
                transaction_summaries.append(f"{txn_type} of {amount} naira")

        summary_text = ". ".join(transaction_summaries)
        response_text = f"Your most recent transactions are: {summary_text}. You have {len(transactions)} total transactions."

        return VoiceResponse(
            success=True,
            session_id=session_id,
            intent="view_transactions",
            response_text=response_text,
            action="complete",
            data={"transactions": transactions[:10]}  # Return top 10
        )

    except Exception as e:
        return VoiceResponse(
            success=False,
            session_id=session_id,
            intent="view_transactions",
            response_text="Sorry, I encountered an error fetching your transactions.",
            error=str(e)
        )


@router.post("/session/clear")
async def clear_session(session_id: str):
    """Clear voice session"""
    session_store.delete(session_id)
    return {"success": True, "message": "Session cleared"}


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech audio

    Returns base64 encoded MP3 audio that can be played in the browser/app.

    Example usage:
        ```javascript
        const response = await fetch('/api/v1/voice/tts', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                text: "Your balance is 95,000 naira",
                voice: "nova",
                speed: 1.0
            })
        });

        const {audio_base64} = await response.json();

        // Play audio
        const audio = new Audio(`data:audio/mp3;base64,${audio_base64}`);
        audio.play();
        ```
    """
    result = await tts_service.text_to_speech(
        text=request.text,
        voice=request.voice,
        speed=request.speed,
        return_format="base64"
    )

    return result


@router.get("/tts/audio/{session_id}")
async def get_tts_audio(session_id: str):
    """
    Get TTS audio for last response in session

    Returns MP3 audio file directly (not base64).
    Useful for direct playback in audio players.
    """
    session_data = session_store.get(session_id)

    if not session_data or "last_response_text" not in session_data:
        raise HTTPException(status_code=404, detail="No response audio found for session")

    result = await tts_service.text_to_speech(
        text=session_data["last_response_text"],
        voice="nova",
        speed=1.0,
        return_format="base64"
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    # Decode base64 to binary
    audio_bytes = base64.b64decode(result["audio_base64"])

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f"inline; filename=response_{session_id}.mp3"
        }
    )


async def add_audio_to_response(response: VoiceResponse, include_audio: bool) -> VoiceResponse:
    """
    Helper function to add TTS audio to voice response

    Args:
        response: VoiceResponse object
        include_audio: Whether to generate and include audio

    Returns:
        VoiceResponse with audio_base64 field populated if include_audio=True
    """
    if not include_audio or not response.response_text:
        return response

    try:
        tts_result = await tts_service.text_to_speech(
            text=response.response_text,
            voice="nova",
            speed=1.0,
            return_format="base64"
        )

        if tts_result["success"]:
            response.response_audio = tts_result["audio_base64"]

    except Exception as e:
        # Don't fail the whole request if TTS fails
        print(f"TTS generation failed: {e}")

    return response
