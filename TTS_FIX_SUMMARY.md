# TTS (Text-to-Speech) Fix Summary

## Problem
Demo Bank voice widget was not playing back audio responses (TTS). The assistant would process voice commands but wouldn't "talk back" with audio.

## Root Causes Identified

### 1. Wrong Company ID
- **Issue**: Demo Bank widget was using `COMPANY_ID = '5'` but Demo Bank is registered as ID `4`
- **File**: `C:\Users\sbnuf\Desktop\projects\demo-bank\frontend\src\components\VoiceModal.tsx:29`
- **Fixed**: Changed to `COMPANY_ID = '4'`

### 2. Incorrect Audio Response Field Name
- **Issue**: Widget was looking for `result.audio_base64` but API returns `result.response_audio`
- **File**: `C:\Users\sbnuf\Desktop\projects\demo-bank\frontend\src\components\VoiceModal.tsx:140`
- **Fixed**: Changed to check `result.response_audio`

### 3. Missing TTS Request Header in Backend
- **Issue**: Backend `process-audio` endpoint wasn't accepting `include-audio` header
- **File**: `C:\Users\sbnuf\Desktop\projects\echobank\backend\app\api\voice_orchestrator.py:66`
- **Fixed**: Added `include_audio: Optional[str] = Header(None)` parameter and logic to pass it to `process_voice_text`

### 4. Transcript Field Inconsistency
- **Issue**: Transcript could be in `result.transcript` OR `result.data.transcript`
- **File**: `C:\Users\sbnuf\Desktop\projects\demo-bank\frontend\src\components\VoiceModal.tsx:128`
- **Fixed**: Added fallback logic: `const transcript = result.transcript || result.data?.transcript`

## Changes Made

### Backend (`echobank/backend/app/api/voice_orchestrator.py`)

```python
# Line 66 - Added include_audio header parameter
@router.post("/process-audio", response_model=VoiceResponse)
async def process_voice_audio(
    audio: UploadFile = File(...),
    account_number: str = Header(...),
    company_id: int = Header(...),
    session_id: Optional[str] = Header(None),
    token: Optional[str] = Header(None),
    include_audio: Optional[str] = Header(None),  # NEW - For TTS response
    db: Session = Depends(get_db)
):

# Lines 97-110 - Process include_audio header and pass to text processor
should_include_audio = include_audio and include_audio.lower() in ['true', '1', 'yes']

return await process_voice_text(
    request=VoiceRequest(
        text=transcript_text,
        account_number=account_number,
        company_id=company_id,
        session_id=session_id,
        token=token,
        include_audio=should_include_audio  # NEW - Pass to text processor
    ),
    db=db
)
```

### Frontend (`demo-bank/frontend/src/components/VoiceModal.tsx`)

```typescript
// Line 29 - Fixed Company ID
const COMPANY_ID = '4'; // Demo Bank's company ID (registered in EchoBank)

// Lines 110-119 - Fixed API call to include TTS header
const response = await fetch(`${ECHOBANK_API}/api/v1/voice/process-audio`, {
  method: 'POST',
  headers: {
    'account-number': accountNumber,
    'company-id': COMPANY_ID,
    'session-id': currentSessionId.current,
    'token': userToken,
    'include-audio': 'true',  // NEW - Request TTS audio response
  },
  body: formData
});

// Lines 124-149 - Fixed response handling with debug logs
console.log('[DEBUG] EchoBank Response:', result);

if (result.success) {
  // Fixed transcript extraction with fallback
  const transcript = result.transcript || result.data?.transcript;
  if (transcript) {
    setConversation(prev => [...prev, {
      type: 'user',
      text: transcript,
      intent: result.intent
    }]);
  }

  // Add assistant response
  setConversation(prev => [...prev, {
    type: 'assistant',
    text: result.response_text
  }]);

  // FIXED - Use correct field name for audio
  if (result.response_audio) {
    console.log('[DEBUG] Playing TTS audio response...');
    playAudioResponse(result.response_audio);
  } else {
    console.warn('[WARNING] No response_audio in result. TTS not enabled.');
  }
}
```

## Setup Steps Completed

### 1. Registered Demo Bank in Database
```
Company ID: 4
Company Name: Demo Bank
Base URL: http://127.0.0.1:8100
```

### 2. Started Mock Bank Server
```bash
# Running on port 8100
python mock_bank_server.py
```

### 3. Mock Bank Endpoints Configured
- Balance: `/api/v1/accounts/{account_number}/balance`
- Recipients: `/api/v1/accounts/{account_number}/beneficiaries`
- Initiate Transfer: `/api/v1/transfers/initiate`
- Confirm Transfer: `/api/v1/transfers/{transfer_id}/confirm`
- Cancel Transfer: `/api/v1/transfers/{transfer_id}/cancel`

## How to Test

### Prerequisites
1. **EchoBank Backend** must be running on `http://localhost:8000`
   ```bash
   cd echobank/backend
   ..\venv\Scripts\uvicorn app.main:app --reload --port 8000
   ```

2. **Mock Bank Server** must be running on `http://localhost:8100`
   ```bash
   cd echobank
   python mock_bank_server.py
   ```

3. **Demo Bank Frontend** must be running
   ```bash
   cd demo-bank/frontend
   npm run dev
   ```

### Test Flow
1. Open Demo Bank application in browser
2. Login with a demo account
3. Click the Voice Banking button (microphone icon)
4. Say: **"Check my balance"**
5. **Expected**:
   - You'll hear the transcript shown (e.g., "Check my balance")
   - Assistant responds with text: "Your account balance is 95,000.00 naira."
   - **TTS AUDIO PLAYS** - Assistant voice speaks the response
6. Try other commands:
   - "Send 5000 to John" - should handle disambiguation and TTS
   - "Show my recipients" - should list recipients with TTS
   - "View transactions" - should show transaction history with TTS

## Debug Console Logs

When testing, check browser console for:
```
[DEBUG] EchoBank Response: {
  success: true,
  session_id: "session_...",
  intent: "check_balance",
  response_text: "Your account balance is 95,000.00 naira.",
  response_audio: "base64_encoded_mp3_data_here...",  ← MUST BE PRESENT
  action: "complete",
  data: { balance: 95000 }
}

[DEBUG] Playing TTS audio response...
```

If you see:
```
[WARNING] No response_audio in result. TTS not enabled.
```
Then the backend is not generating TTS audio - check that include-audio header is being sent.

## Key Points

1. **"Echo" in EchoBank = Talk Back**: The whole point of EchoBank is voice responses (TTS)
2. **include-audio header**: Must be set to 'true' to get TTS audio in response
3. **response_audio field**: Contains base64-encoded MP3 audio data
4. **Company ID 4**: Demo Bank is registered with this ID in EchoBank database

## Files Modified

### Backend
- `backend/app/api/voice_orchestrator.py` - Added include_audio header support

### Frontend (Demo Bank)
- `C:\Users\sbnuf\Desktop\projects\demo-bank\frontend\src\components\VoiceModal.tsx`
  - Fixed company ID (line 29)
  - Fixed API call headers (line 117)
  - Fixed response audio field name (line 144)
  - Added debug logging (lines 124, 145, 148)
  - Fixed transcript extraction (line 128)

## Next Steps

**YOU NEED TO RESTART THE ECHOBANK BACKEND** for the TTS fixes to take effect!

```bash
# Kill existing backend processes
powershell -Command "Get-Process | Where-Object { $_.ProcessName -eq 'python' } | Stop-Process -Force"

# Restart EchoBank backend
cd C:\Users\sbnuf\Desktop\projects\echobank\backend
..\venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

Then test the voice pipeline again - TTS should now work!

---

**Created**: 2025-10-25
**Status**: ✅ All fixes applied, awaiting backend restart
