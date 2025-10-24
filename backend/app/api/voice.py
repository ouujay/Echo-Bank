from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.services.whisper import whisper_service
from app.services.llm import llm_service
from app.utils.session import session_store
from typing import Optional
import uuid
from datetime import datetime


router = APIRouter(prefix="/api/v1/voice", tags=["voice"])


# Request/Response Models
class IntentRequest(BaseModel):
    transcript: str
    session_id: Optional[str] = None


class TranscribeResponse(BaseModel):
    success: bool
    data: dict


class IntentResponse(BaseModel):
    success: bool
    data: dict


class SessionResponse(BaseModel):
    success: bool
    data: dict


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    session_id: Optional[str] = None
):
    """
    Transcribe audio to text using Whisper API

    Args:
        audio: Audio file (wav, mp3, webm, etc.)
        session_id: Optional session ID (generated if not provided)

    Returns:
        {
            "success": true,
            "data": {
                "transcript": "Send five thousand naira to John",
                "confidence": 0.95,
                "session_id": "sess_abc123",
                "timestamp": "2025-10-24T18:30:00Z"
            }
        }
    """
    try:
        # Generate session ID if not provided
        if not session_id:
            session_id = f"sess_{uuid.uuid4().hex[:8]}"

        # Validate audio file
        whisper_service.validate_audio_file(audio)

        # Transcribe audio
        result = await whisper_service.transcribe_audio(audio)

        # Store transcript in session
        session_data = session_store.get(session_id) or {}
        session_data["last_transcript"] = result["transcript"]
        session_data["last_updated"] = datetime.utcnow().isoformat()
        session_store.set(session_id, session_data, expire_minutes=30)

        return {
            "success": True,
            "data": {
                "transcript": result["transcript"],
                "confidence": result["confidence"],
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    except Exception as e:
        error_message = str(e)
        if "Invalid audio format" in error_message:
            raise HTTPException(status_code=400, detail={
                "success": False,
                "error": {
                    "code": "INVALID_AUDIO_FORMAT",
                    "message": error_message
                }
            })
        else:
            raise HTTPException(status_code=400, detail={
                "success": False,
                "error": {
                    "code": "VOICE_UNCLEAR",
                    "message": error_message,
                    "suggestion": "Please speak clearly and try again."
                }
            })


@router.post("/intent", response_model=IntentResponse)
async def parse_intent(request: IntentRequest):
    """
    Parse intent from transcript using LLM

    Args:
        request: {
            "transcript": "Send five thousand naira to John",
            "session_id": "sess_abc123"  # optional
        }

    Returns:
        {
            "success": true,
            "data": {
                "intent": "transfer",
                "confidence": 0.92,
                "entities": {
                    "action": "send",
                    "recipient": "John",
                    "amount": 5000,
                    "currency": "NGN"
                },
                "next_step": "verify_recipient"
            }
        }
    """
    try:
        # Get session context if provided
        context = None
        if request.session_id:
            context = session_store.get(request.session_id)

        # Parse intent using LLM
        result = await llm_service.parse_intent(request.transcript, context)

        # Update session with intent
        if request.session_id:
            session_data = session_store.get(request.session_id) or {}
            session_data["last_intent"] = result
            session_data["current_step"] = result.get("next_step", "unknown")
            session_data["last_updated"] = datetime.utcnow().isoformat()
            session_store.set(request.session_id, session_data, expire_minutes=30)

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "success": False,
            "error": {
                "code": "INTENT_PARSING_FAILED",
                "message": str(e)
            }
        })


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """
    Get current session state

    Args:
        session_id: Session ID

    Returns:
        {
            "success": true,
            "data": {
                "session_id": "sess_abc123",
                "last_transcript": "Send 5000 to John",
                "last_intent": {...},
                "current_step": "verify_recipient",
                "last_updated": "2025-10-24T18:30:00Z"
            }
        }
    """
    session_data = session_store.get(session_id)

    if not session_data:
        raise HTTPException(status_code=404, detail={
            "success": False,
            "error": {
                "code": "SESSION_NOT_FOUND",
                "message": f"Session {session_id} not found or expired."
            }
        })

    return {
        "success": True,
        "data": {
            "session_id": session_id,
            **session_data
        }
    }


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear/delete a session

    Args:
        session_id: Session ID to delete

    Returns:
        {
            "success": true,
            "data": {
                "message": "Session cleared successfully"
            }
        }
    """
    session_store.delete(session_id)

    return {
        "success": True,
        "data": {
            "message": "Session cleared successfully"
        }
    }
