# Demo Bank Widget Voice Pipeline Test

## Setup Complete ✅

### Services Running
- **EchoBank Backend**: http://localhost:8000 ✅
- **Demo Bank Frontend**: http://localhost:3000 ✅
- **Mock Bank API**: http://localhost:8100 ✅
- **CORS**: Port 3000 allowed ✅
- **TTS**: pyttsx3 with WAV format ✅

---

## Test Plan

### 1. **Open Demo Bank Widget**
Visit: http://localhost:3000

### 2. **Login Credentials**
The Demo Bank has users in its database. Check which users exist or use:
- Username: john_doe
- Password: (whatever Demo Bank uses)

OR

- Username: funbi
- Password: (whatever Demo Bank uses)

### 3. **Voice Modal Pipeline**

When you click the microphone button:

**Step 1: Audio Recording**
- Browser requests microphone access
- MediaRecorder captures audio as WebM format
- Audio chunks stored in memory

**Step 2: Send to EchoBank API**
```
POST http://localhost:8000/api/v1/voice/process-audio
Headers:
  - account-number: {from logged-in user}
  - company-id: 4
  - session-id: session_{account}_{timestamp}
  - token: {user token}
  - include-audio: true
Body:
  - audio: {WebM audio blob}
```

**Step 3: EchoBank Processing**
1. **Whisper API**: Transcribes audio to text
2. **LLM (Together AI)**: Parses intent and entities
3. **Company API Client**: Calls Mock Bank API
   - Balance: `GET /api/v1/accounts/{account}/balance`
   - Recipients: `GET /api/v1/accounts/{account}/beneficiaries`
4. **TTS Service**: Generates WAV audio response
5. **Response**: Returns JSON with `response_audio` field

**Step 4: Play TTS in Widget**
- Decode base64 audio
- Create WAV audio element
- Play response through speakers

---

## Test Cases

### Test 1: Balance Check (John Doe - 6523711418)
1. Login as John Doe
2. Click microphone
3. Say: **"Check my balance"**
4. Expected Response: "Your account balance is 95,000 naira"
5. ✅ Audio plays back

### Test 2: Balance Check (Funbi - 8523711419)
1. Login as Funbi
2. Click microphone
3. Say: **"What's my balance?"**
4. Expected Response: "Your account balance is 250,000 naira"
5. ✅ Audio plays back

### Test 3: Recipients (John Doe)
1. Say: **"Show my recipients"**
2. Expected Response: Lists John Doe, John Ade, John Epe, Mary Johnson
3. ✅ Audio plays back

### Test 4: Recipients (Funbi)
1. Say: **"Who can I send money to?"**
2. Expected Response: Lists Tunde Bakare, Chioma Okafor, Bola Tinubu Jr
3. ✅ Audio plays back

### Test 5: Transfer (Edge Case - Multiple Johns)
1. Say: **"Send 5000 to John"**
2. Expected Response: "I found multiple recipients: John Doe, John Ade, John Epe. Which one?"
3. ✅ Audio plays back

### Test 6: Transfer (Specific Recipient)
1. Say: **"Send 10000 to Tunde"**
2. Expected Response: "Sending 10,000 naira to Tunde Bakare. Please confirm"
3. ✅ Audio plays back

### Test 7: Multiple Rapid Requests
1. Say: "Check balance"
2. **Immediately** say: "Show recipients"
3. **Immediately** say: "Send to Tunde"
4. ✅ All responses come back without hanging

---

## Expected Backend Logs

When widget sends request, you should see:

```
[TTS DEBUG] include_audio header: true
[TTS DEBUG] should_include_audio: True
============================================================
[TRANSCRIPT] User said: 'Check my balance'
[INTENT] LLM parsed as: check_balance
[CONFIDENCE] Score: 0.99
[ENTITIES] Extracted: {'recipient': None, 'amount': None, 'currency': 'NGN', ...}
============================================================
[TTS DEBUG] request.include_audio = True
[TTS DEBUG] Generating TTS for: Your account balance is...
[TTS DEBUG] TTS generated, response_audio present: True
INFO: 127.0.0.1:XXXXX - "POST /api/v1/voice/process-audio HTTP/1.1" 200 OK
```

---

## Expected Mock Bank API Calls

When checking balance:
```
GET http://127.0.0.1:8100/api/v1/accounts/6523711418/balance
```

When fetching recipients:
```
GET http://127.0.0.1:8100/api/v1/accounts/6523711418/beneficiaries
```

---

## Common Issues & Fixes

### Issue 1: "No response_audio"
**Symptom**: Console shows `[WARNING] No response_audio in result`
**Cause**: `include-audio` header not set to "true"
**Check**: VoiceModal.tsx line 118 should have `'include-audio': 'true'`

### Issue 2: CORS Error
**Symptom**: Console shows "blocked by CORS policy"
**Cause**: Port 3000 not in allowed origins
**Fix**: Already done - backend config.py includes port 3000

### Issue 3: Recipients Not Loading
**Symptom**: "Cannot retrieve recipients"
**Cause**: Mock bank API not responding or wrong account number
**Check**:
```bash
curl http://127.0.0.1:8100/api/v1/accounts/6523711418/beneficiaries
```

### Issue 4: Second Request Hangs
**Symptom**: First request works, second hangs
**Cause**: pyttsx3 engine not cleaned up
**Fix**: Already done - fresh engine per request

### Issue 5: Audio Not Playing
**Symptom**: Response received but no sound
**Cause**: WAV format not supported or audio element error
**Check**: Browser console for audio playback errors

---

## Manual Test Checklist

Run through this checklist:

- [ ] Demo Bank opens at http://localhost:3000
- [ ] Can login to Demo Bank
- [ ] Voice button appears on dashboard
- [ ] Click voice button opens modal
- [ ] Microphone access granted
- [ ] Recording indicator shows when speaking
- [ ] First request: Check balance
  - [ ] Transcript appears
  - [ ] Response text shows
  - [ ] Audio plays
- [ ] Second request: Show recipients
  - [ ] No hanging/delay
  - [ ] Response returns quickly
  - [ ] Audio plays
- [ ] Third request: Send money
  - [ ] Transfer flow initiates
  - [ ] Audio plays

---

## Monitoring Commands

### Watch Backend Logs
```bash
# In EchoBank backend directory
tail -f nul  # Or use the BashOutput tool with ID 031a5a
```

### Watch Mock Bank Logs
```bash
# Check if mock bank receiving requests
tail -f nul  # Or use the BashOutput tool with ID 371e92
```

### Test CORS
```bash
curl -X OPTIONS http://localhost:8000/api/v1/voice/process-audio \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

### Test Mock Bank API
```bash
# John Doe
curl http://127.0.0.1:8100/api/v1/accounts/6523711418/balance
curl http://127.0.0.1:8100/api/v1/accounts/6523711418/beneficiaries

# Funbi
curl http://127.0.0.1:8100/api/v1/accounts/8523711419/balance
curl http://127.0.0.1:8100/api/v1/accounts/8523711419/beneficiaries
```

---

## Success Criteria

✅ **Pipeline Working** if:
1. Voice recording starts/stops correctly
2. Transcript appears in UI
3. Response text displays
4. **TTS audio plays back**
5. Multiple requests work without hanging
6. Both John Doe and Funbi accounts work
7. Recipients load correctly per user
8. Backend logs show all steps

---

## Next: Actually Test It!

1. Open http://localhost:3000
2. Login
3. Click microphone
4. Say "Check my balance"
5. **Listen for TTS audio response**
6. Check backend logs for confirmation

**Monitor with**:
- Backend bash ID: `031a5a`
- Mock bank bash ID: `371e92`
