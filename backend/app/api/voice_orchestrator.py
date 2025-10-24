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

from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.whisper import whisper_service
from app.services.llm import llm_service
from app.integrations.mock_bank import mock_bank_client
from app.utils.session import session_store

router = APIRouter(prefix="/api/v1/voice", tags=["Voice Orchestration"])


class VoiceRequest(BaseModel):
    """Request for text-based voice command"""
    text: str
    account_number: str
    session_id: Optional[str] = None
    token: Optional[str] = None  # Bank's auth token


class VoiceResponse(BaseModel):
    """Response from voice processing"""
    success: bool
    session_id: str
    intent: str
    response_text: str  # What to say back to user
    action: Optional[str] = None  # next_action: confirm_transfer, input_pin, etc
    data: Optional[Dict[str, Any]] = None  # Additional context
    error: Optional[str] = None


@router.post("/process-audio", response_model=VoiceResponse)
async def process_voice_audio(
    audio: UploadFile = File(...),
    account_number: str = Header(...),
    session_id: Optional[str] = Header(None),
    token: Optional[str] = Header(None)
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
    try:
        # Step 1: Transcribe audio
        transcription = await whisper_service.transcribe_audio(audio)
        transcript_text = transcription["transcript"]

        # Step 2: Process as text
        return await process_voice_text(VoiceRequest(
            text=transcript_text,
            account_number=account_number,
            session_id=session_id,
            token=token
        ))

    except Exception as e:
        return VoiceResponse(
            success=False,
            session_id=session_id or "error",
            intent="error",
            response_text="Sorry, I couldn't understand that. Please try again.",
            error=str(e)
        )


@router.post("/process-text", response_model=VoiceResponse)
async def process_voice_text(request: VoiceRequest):
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
                session_id: sessionId,
                token: userToken
            })
        });
        ```
    """
    try:
        # Get or create session
        session_id = request.session_id or f"session_{request.account_number}"
        session_data = session_store.get(session_id) or {}

        # Step 1: Parse intent with LLM
        intent_result = await llm_service.parse_intent(
            request.text,
            context=session_data
        )

        intent = intent_result.get("intent", "unknown")
        entities = intent_result.get("entities", {})
        confidence = intent_result.get("confidence", 0.0)

        # Update session
        session_data["last_transcript"] = request.text
        session_data["last_intent"] = intent
        session_data["entities"] = entities

        # Step 2: Execute based on intent
        if intent == "transfer":
            return await handle_transfer_intent(
                request, session_data, entities, session_id
            )

        elif intent == "check_balance":
            return await handle_balance_intent(
                request, session_data, session_id
            )

        elif intent == "add_recipient":
            return await handle_add_recipient_intent(
                request, session_data, entities, session_id
            )

        elif intent == "confirm":
            return await handle_confirm_intent(
                request, session_data, session_id
            )

        elif intent == "cancel":
            return await handle_cancel_intent(
                request, session_data, session_id
            )

        elif intent == "provide_pin":
            return await handle_pin_intent(
                request, session_data, entities, session_id
            )

        else:
            return VoiceResponse(
                success=True,
                session_id=session_id,
                intent="unknown",
                response_text="I didn't quite understand that. You can say things like 'check my balance' or 'send money to John'.",
                action="clarify"
            )

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
    session_id: str
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

    # Get recipients from bank
    recipients_result = await mock_bank_client.get_recipients(
        request.account_number,
        request.token or "demo_token"
    )

    if not recipients_result["success"]:
        return VoiceResponse(
            success=False,
            session_id=session_id,
            intent="transfer",
            response_text="I couldn't access your recipients. Please try again.",
            error=recipients_result["error"]
        )

    # Find matching recipient
    recipients = recipients_result["recipients"]
    matched_recipient = None

    for r in recipients:
        if recipient_name.lower() in r["name"].lower():
            matched_recipient = r
            break

    if not matched_recipient:
        return VoiceResponse(
            success=True,
            session_id=session_id,
            intent="transfer",
            response_text=f"I couldn't find {recipient_name} in your recipients. Would you like to add them first?",
            action="add_recipient"
        )

    # Initiate transfer
    transfer_result = await mock_bank_client.initiate_transfer(
        sender_account=request.account_number,
        recipient_account=matched_recipient["account_number"],
        bank_code=matched_recipient["bank_code"],
        amount=amount,
        narration=f"Transfer to {matched_recipient['name']}",
        token=request.token or "demo_token"
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
    session_id: str
) -> VoiceResponse:
    """Handle check balance intent"""

    balance_result = await mock_bank_client.get_balance(
        request.account_number,
        request.token or "demo_token"
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
    session_id: str
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
    session_id: str
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

    # Confirm transfer with PIN
    confirm_result = await mock_bank_client.confirm_transfer(
        transfer_id=pending_transfer["transfer_id"],
        pin=pin,
        token=request.token or "demo_token"
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
    session_id: str
) -> VoiceResponse:
    """Handle cancellation"""

    pending_transfer = session_data.get("pending_transfer")

    if pending_transfer:
        # Cancel the transfer
        await mock_bank_client.cancel_transfer(
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


async def handle_add_recipient_intent(
    request: VoiceRequest,
    session_data: Dict,
    entities: Dict,
    session_id: str
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


@router.post("/session/clear")
async def clear_session(session_id: str):
    """Clear voice session"""
    session_store.delete(session_id)
    return {"success": True, "message": "Session cleared"}
