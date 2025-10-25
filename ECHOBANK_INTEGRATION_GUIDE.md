# EchoBank Voice Integration Guide for Demo Bank

**Date:** October 25, 2025
**Demo Bank Company ID:** 5
**Status:** ✅ Backend Configured & Ready

---

## 🎯 Overview

Your bank (Demo Bank Official) has been successfully registered with EchoBank's voice API. This guide provides **two options** for integrating voice banking into your application.

---

## 📋 Your EchoBank Account Details

```
Company Name: Demo Bank Official
Company ID: 5
Email: official@demobank.com
Login URL: http://localhost:5174/login

API Key: echobank_gNL7DXY6e5ssKzAqUpCO6fcmLuvOY3808nHbVv4eALU
⚠️ Keep this secret! Don't commit to git.
```

### ✅ Your API Endpoints (Already Configured)

EchoBank knows how to call your APIs:

```
Base URL: http://localhost:8002
Auth Type: Bearer Token

Endpoints:
- Get Balance: /api/accounts/balance/{account_number}
- Get Recipients: /api/recipients
- Initiate Transfer: /api/transfers/initiate
- Confirm Transfer: /api/transfers/{transfer_id}/confirm
- Verify PIN: /api/auth/verify-pin
```

---

## 🚀 Integration Options

### Option 1: Quick Integration (We Provide the UI)

**What You Get:**
- ✅ Pre-built voice modal component (React)
- ✅ Audio recording functionality
- ✅ Premium UI/UX (tested and polished)
- ✅ Full conversation management
- ✅ Text-to-speech (assistant talks back)
- ✅ Ready to drop into your app

**What You Need to Do:**
1. Copy the components we provide
2. Add one button to your dashboard
3. Configure with your user's data
4. Done! (30-60 minutes)

**👉 See: [Option 1 - Quick Integration](#option-1-quick-integration-detailed)**

---

### Option 2: Custom Integration (You Build the UI)

**What You Get:**
- ✅ Full control over UI/UX
- ✅ API documentation
- ✅ Code examples
- ✅ Integration guidelines

**What You Need to Do:**
1. Build your own voice recording UI
2. Call our API endpoint
3. Handle responses
4. Customize to match your brand

**👉 See: [Option 2 - Custom Integration](#option-2-custom-integration-detailed)**

---

# Option 1: Quick Integration (Detailed)

## Step 1: Copy the Voice Components

**Files to Copy:**

From EchoBank's frontend, copy these files into your project:

```
Source: C:\Users\sbnuf\Desktop\projects\echobank\frontend\src\

Copy to your project:
📁 src/
  📁 components/
    📄 VoiceModal.jsx          (NEW)
    📄 VoiceModalPremium.css   (NEW)
```

**VoiceModal.jsx** - The complete voice interface component
**VoiceModalPremium.css** - Premium styling

---

## Step 2: Install Dependencies

Your Demo Bank already has React, but make sure you have these:

```bash
# You should already have these, but verify:
npm install react react-dom
```

No additional packages needed! The component uses native browser APIs.

---

## Step 3: Add Voice Button to Dashboard

In your **Dashboard** component (e.g., `src/pages/Dashboard.tsx`):

```jsx
import { useState } from 'react';
import VoiceModal from '../components/VoiceModal';

function Dashboard() {
  const [showVoiceModal, setShowVoiceModal] = useState(false);

  // Get user data from your auth context
  const user = useAuth(); // or however you get logged-in user
  const userAccount = user.accounts[0]?.account_number; // e.g., '0634250390'
  const userToken = localStorage.getItem('token'); // Your JWT token

  return (
    <div className="dashboard">
      {/* Your existing dashboard content */}

      {/* Add Voice Banking Button */}
      <button
        onClick={() => setShowVoiceModal(true)}
        className="voice-banking-btn"
      >
        🎤 Voice Banking
      </button>

      {/* Voice Modal */}
      {showVoiceModal && (
        <VoiceModal
          accountNumber={userAccount}
          userToken={userToken}
          companyId={5}  // Your Demo Bank company ID
          onClose={() => setShowVoiceModal(false)}
        />
      )}
    </div>
  );
}
```

---

## Step 4: Configure API URL

Create or update your `.env` file:

```bash
# Demo Bank .env
VITE_ECHOBANK_API_URL=http://localhost:8000
```

Then in **VoiceModal.jsx**, update the API URL:

```javascript
const ECHOBANK_API = import.meta.env.VITE_ECHOBANK_API_URL || 'http://localhost:8000';
```

---

## Step 5: Style the Button (Optional)

Add this CSS to your dashboard styles:

```css
.voice-banking-btn {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0066FF 0%, #0052CC 100%);
  color: white;
  border: none;
  font-size: 28px;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(0, 102, 255, 0.3);
  transition: transform 0.2s;
  z-index: 1000;
}

.voice-banking-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 12px 30px rgba(0, 102, 255, 0.4);
}
```

---

## Step 6: Test It!

1. **Start Demo Bank:**
   ```bash
   cd /c/Users/sbnuf/Desktop/projects/demo-bank/frontend
   npm run dev
   ```

2. **Login to Demo Bank** (http://localhost:3000)
   - Email: testuser@demo.com
   - Password: password123

3. **Click the Voice Button** 🎤

4. **Try Commands:**
   - "What's my balance?"
   - "Send 5000 to Sarah"
   - "Show my recent transactions"

---

## ✅ That's It!

You now have:
- ✅ Voice recording
- ✅ Speech-to-text transcription
- ✅ Intent recognition
- ✅ Banking actions executed via your APIs
- ✅ Text-to-speech responses
- ✅ Premium UI

**Total Integration Time: 30-60 minutes**

---

# Option 2: Custom Integration (Detailed)

Build your own voice interface from scratch.

## API Endpoint

```
POST http://localhost:8000/api/v1/voice/process-audio
```

---

## Request Format

### Headers (Required)

```javascript
{
  'account-number': string,  // User's bank account number
  'company-id': '5',         // Demo Bank's company ID
  'session-id': string,      // Unique session ID for conversation
  'token': string            // User's JWT token from your auth
}
```

### Body

```javascript
FormData with:
- audio: File | Blob  // Audio file (WAV, MP3, OGG, WEBM)
```

### Query Parameters (Optional)

```
?include_audio=true  // Set to true if you want TTS audio response
```

---

## Example Code

### 1. Record Audio

```javascript
// Record audio from microphone
let mediaRecorder;
let audioChunks = [];

async function startRecording() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);

  mediaRecorder.ondataavailable = (event) => {
    audioChunks.push(event.data);
  };

  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    await sendToEchoBank(audioBlob);
    audioChunks = [];
  };

  mediaRecorder.start();
}

function stopRecording() {
  mediaRecorder.stop();
  mediaRecorder.stream.getTracks().forEach(track => track.stop());
}
```

---

### 2. Send to EchoBank API

```javascript
async function sendToEchoBank(audioBlob) {
  const formData = new FormData();
  formData.append('audio', audioBlob);

  // Get user info from your auth context
  const userAccount = getCurrentUserAccount(); // e.g., '0634250390'
  const userToken = getAuthToken(); // Your JWT
  const sessionId = getOrCreateSessionId(); // Unique per conversation

  const response = await fetch(
    'http://localhost:8000/api/v1/voice/process-audio?include_audio=true',
    {
      method: 'POST',
      headers: {
        'account-number': userAccount,
        'company-id': '5',
        'session-id': sessionId,
        'token': userToken,
      },
      body: formData
    }
  );

  const result = await response.json();
  handleEchoBankResponse(result);
}
```

---

### 3. Handle Response

```javascript
function handleEchoBankResponse(result) {
  if (!result.success) {
    console.error('Error:', result.error);
    displayError(result.response_text);
    return;
  }

  // Display what user said
  console.log('User said:', result.data?.transcript);

  // Display assistant's response
  displayMessage(result.response_text);

  // Play audio response if available
  if (result.response_audio) {
    playAudio(result.response_audio);
  }

  // Handle actions (e.g., show PIN modal)
  if (result.action === 'confirm_transfer') {
    showTransferConfirmation(result.data);
  }
}
```

---

### 4. Play Audio Response

```javascript
function playAudio(base64Audio) {
  const audioData = `data:audio/mp3;base64,${base64Audio}`;
  const audio = new Audio(audioData);
  audio.play();
}
```

---

## Response Format

### Success Response

```json
{
  "success": true,
  "session_id": "session_0634250390",
  "intent": "check_balance",
  "response_text": "Your balance is 94,975 naira",
  "response_audio": "base64_encoded_mp3_audio...",
  "action": null,
  "data": {
    "transcript": "what's my balance",
    "balance": 94975.00,
    "account_number": "0634250390"
  }
}
```

### Transfer Flow Response

```json
{
  "success": true,
  "session_id": "session_0634250390",
  "intent": "transfer",
  "response_text": "You're about to send 5000 naira to Sarah Bello. Please confirm by saying 'confirm' or enter your PIN.",
  "response_audio": "base64_encoded_audio...",
  "action": "confirm_transfer",
  "data": {
    "transfer_id": "trans_abc123",
    "recipient_name": "Sarah Bello",
    "amount": 5000.0,
    "fee": 10.0,
    "total": 5010.0
  }
}
```

### Error Response

```json
{
  "success": false,
  "session_id": "session_0634250390",
  "intent": "error",
  "response_text": "Sorry, I couldn't understand that. Please try again.",
  "error": "Transcription failed"
}
```

---

## Supported Intents

EchoBank recognizes these banking intents:

| Intent | Example Commands | Response Action |
|--------|-----------------|-----------------|
| `check_balance` | "What's my balance?", "How much do I have?" | Returns balance |
| `transfer` | "Send 5000 to John", "Transfer money to Sarah" | Initiates transfer → `action: confirm_transfer` |
| `get_recipients` | "Show my beneficiaries", "List recipients" | Returns recipient list |
| `get_transactions` | "Show my transactions", "Transaction history" | Returns transaction list |
| `cancel` | "Cancel", "Stop", "Nevermind" | Cancels current action |
| `start_over` | "Start over", "Restart", "Begin again" | Clears session |

---

## Session Management

**Session IDs** track conversations. Keep the same `session_id` for a full conversation:

```javascript
// Generate once per user login or conversation
const sessionId = `session_${accountNumber}_${Date.now()}`;

// Reuse for all requests in the same conversation
// Clear when user logs out or starts new conversation
```

---

## Error Handling

```javascript
try {
  const response = await fetch(ECHOBANK_API, options);
  const result = await response.json();

  if (!response.ok) {
    // HTTP error
    console.error('API Error:', response.status, result);
    showError('Voice service unavailable. Please try again.');
    return;
  }

  if (!result.success) {
    // Business logic error
    console.error('Processing Error:', result.error);
    showError(result.response_text || 'Something went wrong');
    return;
  }

  // Success!
  handleResponse(result);

} catch (error) {
  // Network error
  console.error('Network Error:', error);
  showError('Cannot connect to voice service. Check your connection.');
}
```

---

## Security Best Practices

### ⚠️ NEVER expose these in frontend code:

```javascript
❌ const API_KEY = "echobank_gNL7DXY6e5ssKzAqUpCO6fcmLuvOY3808nHbVv4eALU";
```

### ✅ DO use environment variables:

```javascript
// .env (NOT committed to git)
VITE_ECHOBANK_COMPANY_ID=5

// In code
const companyId = import.meta.env.VITE_ECHOBANK_COMPANY_ID;
```

### ✅ DO validate user authentication:

```javascript
// Only allow authenticated users to use voice
if (!isUserLoggedIn()) {
  showError('Please login to use voice banking');
  return;
}
```

---

## Testing

### Test User (From Demo Bank)

```
Account: 0634250390
Balance: ₦94,975.00
PIN: 1234
Token: (Get from login)
```

### Test Commands

1. **Balance Check:**
   - "What's my balance?"
   - "How much money do I have?"

2. **Transfer:**
   - "Send 1000 to Sarah"
   - "Transfer 5000 naira to John"

3. **Recipients:**
   - "Show my beneficiaries"
   - "List my recipients"

---

## Troubleshooting

### Issue: "Microphone permission denied"

**Solution:**
```javascript
// Request permission explicitly
try {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  // Permission granted
} catch (error) {
  alert('Please allow microphone access to use voice banking');
}
```

---

### Issue: "CORS error"

**Solution:** EchoBank's backend is already configured for CORS. Make sure you're calling:
- `http://localhost:8000` (not `http://127.0.0.1:8000`)

---

### Issue: "Invalid company-id"

**Solution:** Double-check you're using:
```javascript
headers: {
  'company-id': '5',  // String, not number!
}
```

---

### Issue: "Transcription empty"

**Solution:**
- Check audio format (WAV, MP3, OGG, WEBM supported)
- Ensure audio is at least 1 second long
- Test microphone is working

---

## Production Deployment

### Update API URLs

```javascript
// Development
const ECHOBANK_API = 'http://localhost:8000';

// Production
const ECHOBANK_API = 'https://api.echobank.com';
```

### SSL Required

In production, HTTPS is required for:
- ✅ Microphone access
- ✅ Secure API calls
- ✅ User data protection

---

## Support

**Questions?** Contact EchoBank:
- Email: support@echobank.com
- Dashboard: http://localhost:5174/login
- API Docs: http://localhost:8000/docs

---

## 🎉 That's It!

Choose your integration approach and get started:

- **Option 1:** Copy our components → Fast & easy
- **Option 2:** Build custom UI → Full control

Both options use the same powerful EchoBank API under the hood! 🚀

---

**Generated:** October 25, 2025
**EchoBank Version:** 1.0
**Demo Bank Company ID:** 5
