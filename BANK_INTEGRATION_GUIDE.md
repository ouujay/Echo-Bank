# EchoBank Integration Guide for Banks

## Overview

**EchoBank** is a Voice Intelligence API that integrates into your existing banking application. It provides voice-powered banking features without requiring you to rebuild your app.

### What EchoBank Does:
- 🎤 **Voice-to-Text**: Transcribes user voice commands
- 🧠 **Intent Recognition**: Understands banking commands using AI
- 🔄 **Smart Orchestration**: Connects to your existing banking APIs
- 🗣️ **Text-to-Speech**: Returns what to say back to users

### What EchoBank Does NOT Do:
- ❌ Does NOT store customer data
- ❌ Does NOT handle money directly
- ❌ Does NOT replace your banking infrastructure

**Think of EchoBank as a voice layer on top of your existing APIs.**

---

## Architecture

```
┌─────────────────────────────────────────────┐
│         Your Bank's Mobile App             │
│                                             │
│  ┌────────────────┐    ┌────────────────┐ │
│  │  Your Database │    │  Your Backend  │ │
│  │  - Users       │◄───┤  - REST API    │ │
│  │  - Accounts    │    │  - Auth        │ │
│  │  - Recipients  │    │  - Transfers   │ │
│  └────────────────┘    └────────┬───────┘ │
└─────────────────────────────────┼───────────┘
                                  │
                      ┌───────────▼───────────┐
                      │   EchoBank Voice API  │
                      │  (Voice Intelligence) │
                      │                       │
                      │  1. Transcribe Voice  │
                      │  2. Recognize Intent  │
                      │  3. Call Your API     │
                      │  4. Generate Response │
                      └───────────────────────┘
```

---

## Integration Steps

### Step 1: Implement the BankAPIClient Interface

EchoBank calls **your** APIs through the `BankAPIClient` interface. You need to implement this interface to connect to your banking system.

**File: `your_bank_adapter.py`**

```python
from app.integrations.bank_client import BankAPIClient
import requests

class YourBankAPIClient(BankAPIClient):
    """
    Your bank's implementation of EchoBank interface
    """

    def __init__(self, api_base_url: str, api_key: str):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def verify_account(self, account_number: str, pin: str) -> Dict:
        """
        Call YOUR auth endpoint to verify account
        """
        response = requests.post(
            f"{self.api_base_url}/auth/verify",
            json={"account_number": account_number, "pin": pin},
            headers=self.headers
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "verified": True,
                "user_id": data["user_id"],
                "account_name": data["full_name"],
                "error": None
            }
        else:
            return {
                "verified": False,
                "user_id": None,
                "account_name": None,
                "error": "Invalid credentials"
            }

    async def get_balance(self, account_number: str, token: str) -> Dict:
        """
        Call YOUR balance endpoint
        """
        response = requests.get(
            f"{self.api_base_url}/accounts/{account_number}/balance",
            headers={**self.headers, "Authorization": f"Bearer {token}"}
        )

        data = response.json()
        return {
            "success": True,
            "balance": Decimal(data["balance"]),
            "currency": "NGN",
            "available_balance": Decimal(data["available_balance"]),
            "error": None
        }

    async def initiate_transfer(
        self,
        sender_account: str,
        recipient_account: str,
        bank_code: str,
        amount: Decimal,
        narration: str,
        token: str
    ) -> Dict:
        """
        Call YOUR transfer initiation endpoint
        """
        response = requests.post(
            f"{self.api_base_url}/transfers/initiate",
            json={
                "sender_account": sender_account,
                "recipient_account": recipient_account,
                "bank_code": bank_code,
                "amount": float(amount),
                "narration": narration
            },
            headers={**self.headers, "Authorization": f"Bearer {token}"}
        )

        data = response.json()
        return {
            "success": True,
            "transfer_id": data["transfer_id"],
            "status": "pending_confirmation",
            "recipient_name": data["recipient_name"],
            "amount": amount,
            "fee": Decimal(data["fee"]),
            "total": Decimal(data["total"]),
            "error": None
        }

    # Implement other methods: confirm_transfer, get_recipients, etc.
    # See app/integrations/bank_client.py for full interface
```

### Step 2: Configure Your Bank Client

Update EchoBank configuration to use your bank adapter:

**File: `app/integrations/__init__.py`**

```python
from your_bank_adapter import YourBankAPIClient

# Initialize with your bank's API credentials
bank_client = YourBankAPIClient(
    api_base_url="https://api.yourbank.com/v1",
    api_key="your_api_key_here"
)
```

### Step 3: Integrate Voice into Your Mobile App

#### Frontend Integration (React Native / React)

**Install dependencies:**
```bash
npm install axios react-native-audio-recorder-player
```

**Voice Button Component:**

```javascript
import React, { useState } from 'react';
import AudioRecorderPlayer from 'react-native-audio-recorder-player';
import axios from 'axios';

const ECHOBANK_API = 'https://your-echobank-instance.azurewebsites.net';

function VoiceAssistant({ accountNumber, authToken }) {
  const [isRecording, setIsRecording] = useState(false);
  const [response, setResponse] = useState(null);
  const audioRecorderPlayer = new AudioRecorderPlayer();

  const startRecording = async () => {
    setIsRecording(true);
    const result = await audioRecorderPlayer.startRecorder();
    console.log('Recording started:', result);
  };

  const stopRecording = async () => {
    const result = await audioRecorderPlayer.stopRecorder();
    audioRecorderPlayer.removeRecordBackListener();
    setIsRecording(false);

    // Send audio to EchoBank
    const formData = new FormData();
    formData.append('audio', {
      uri: result,
      type: 'audio/wav',
      name: 'voice.wav',
    });

    try {
      const response = await axios.post(
        `${ECHOBANK_API}/api/v1/voice/process-audio`,
        formData,
        {
          headers: {
            'account_number': accountNumber,
            'token': authToken,
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setResponse(response.data);

      // Speak the response back to user
      speakResponse(response.data.response_text);

      // Handle next action
      handleNextAction(response.data);

    } catch (error) {
      console.error('Voice processing error:', error);
    }
  };

  const speakResponse = (text) => {
    // Use Web Speech API or react-native-tts
    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = 'en-NG';
    window.speechSynthesis.speak(speech);
  };

  const handleNextAction = (voiceResponse) => {
    switch (voiceResponse.action) {
      case 'confirm_transfer':
        // Show confirmation modal
        showTransferConfirmation(voiceResponse.data);
        break;

      case 'request_pin':
        // Show PIN input
        showPINInput(voiceResponse.data);
        break;

      case 'complete':
        // Show success message
        showSuccess(voiceResponse.response_text);
        break;

      default:
        // Continue listening
        break;
    }
  };

  return (
    <button
      onMouseDown={startRecording}
      onMouseUp={stopRecording}
      onTouchStart={startRecording}
      onTouchEnd={stopRecording}
    >
      {isRecording ? '🎤 Listening...' : '🎤 Hold to Speak'}
    </button>
  );
}

export default VoiceAssistant;
```

---

## API Reference

### Primary Endpoint: Process Voice Audio

**POST** `/api/v1/voice/process-audio`

Process voice audio and execute banking action.

**Headers:**
- `account_number`: Customer account number (required)
- `token`: Your bank's auth token (optional)
- `session_id`: Session identifier (optional)

**Body:**
- `audio`: Audio file (multipart/form-data)

**Response:**
```json
{
  "success": true,
  "session_id": "session_123",
  "intent": "transfer",
  "response_text": "You're about to send 5000 naira to John. Please confirm.",
  "action": "confirm_transfer",
  "data": {
    "transfer_id": "txn_abc123",
    "recipient_name": "John Okafor",
    "amount": 5000,
    "fee": 10,
    "total": 5010
  }
}
```

### Alternative: Process Text Command

**POST** `/api/v1/voice/process-text`

For testing or text-based input (when voice is not available).

**Body:**
```json
{
  "text": "Send five thousand naira to John",
  "account_number": "0123456789",
  "session_id": "session_123",
  "token": "your_auth_token"
}
```

---

## Supported Intents

EchoBank recognizes these banking intents:

| Intent | Example Command | Response Action |
|--------|----------------|----------------|
| `transfer` | "Send 5000 naira to John" | `confirm_transfer` |
| `check_balance` | "What's my balance?" | `complete` |
| `confirm` | "Yes, confirm the transfer" | `request_pin` |
| `provide_pin` | "1-2-3-4" | `complete` |
| `cancel` | "Cancel this transaction" | `complete` |
| `add_recipient` | "Add Sarah to my recipients" | `redirect_to_ui` |

---

## Testing Your Integration

### 1. Test with Mock Bank (Included)

EchoBank includes a mock bank implementation for testing:

```bash
# Start EchoBank server
cd backend
../venv/Scripts/uvicorn app.main:app --port 8001

# Test endpoints are available at:
# http://localhost:8001/docs
```

**Test Account:**
- Account: `0123456789`
- PIN: `1234`
- Balance: ₦100,000

**Test Recipients:**
- John Okafor - `0111111111`
- Mary Johnson - `0333333333`

### 2. Test Voice Flow

**Test Files:** See `backend/test_dev1.http` and `backend/test_dev2.http`

**Example Test:**
```http
### Test Voice Intent Recognition
POST http://localhost:8001/api/v1/voice/process-text
Content-Type: application/json

{
  "text": "Send five thousand naira to John",
  "account_number": "0123456789",
  "session_id": "test_123"
}
```

### 3. Test With Your Bank API

Replace mock client with your implementation:

```python
# app/integrations/__init__.py
from your_bank_adapter import YourBankAPIClient

bank_client = YourBankAPIClient(
    api_base_url=os.getenv("YOUR_BANK_API_URL"),
    api_key=os.getenv("YOUR_BANK_API_KEY")
)
```

---

## Deployment

### Deploy to Azure Web App

```bash
# Install Azure CLI
az login

# Create resource group
az group create --name echobank-rg --location eastus

# Deploy web app
cd backend
az webapp up \
  --name your-bank-echobank \
  --resource-group echobank-rg \
  --runtime "PYTHON:3.11" \
  --sku B1

# Set environment variables
az webapp config appsettings set \
  --name your-bank-echobank \
  --resource-group echobank-rg \
  --settings \
    YOUR_BANK_API_URL="https://api.yourbank.com" \
    YOUR_BANK_API_KEY="your_secret_key" \
    WHISPERAPI="your_openai_key" \
    TOGETHER_API_KEY="your_together_key"
```

---

## Security Considerations

### 1. Authentication

- **Your bank's auth tokens** are passed through EchoBank to your API
- EchoBank does NOT store tokens
- Tokens expire based on your bank's policy

### 2. Data Privacy

- Voice audio is transcribed and immediately deleted
- Only transcribed text is kept in session (30 min TTL)
- No customer data stored in EchoBank database

### 3. API Security

- Use HTTPS for all API calls
- Implement rate limiting on your endpoints
- Validate all inputs from EchoBank
- Audit all transfer requests

### 4. PCI Compliance

- PINs are NEVER sent to EchoBank
- PINs are directly verified through YOUR API
- EchoBank only indicates "verify PIN" action

---

## FAQ

**Q: Does EchoBank have access to our customer data?**
A: No. EchoBank only calls your APIs with your authentication. Your data stays in your systems.

**Q: How do we charge customers for using voice features?**
A: EchoBank is white-labeled. You can charge customers however you like.

**Q: Can we customize the voice responses?**
A: Yes. The LLM prompts are configurable. You can adjust tone, language, and phrasing.

**Q: What languages are supported?**
A: Currently English (Nigerian dialect). Additional languages can be added by training the LLM.

**Q: How much does EchoBank cost?**
A: Contact TIC Hackathon team for licensing terms. Demo version is free for hackathon participants.

**Q: Do we need Redis?**
A: No. The included in-memory session store works for single-instance deployments. Redis is optional for scaling.

---

## Support

**Hackathon Support:**
- GitHub: https://github.com/ouujay/Echo-Bank
- Issues: https://github.com/ouujay/Echo-Bank/issues
- Demo: https://echobank.azurewebsites.net

**For Production Integration:**
- Contact TIC Hackathon organizers
- Request integration consultation

---

## Next Steps

1. ✅ Review the `BankAPIClient` interface: `backend/app/integrations/bank_client.py`
2. ✅ Implement your bank's adapter: `your_bank_adapter.py`
3. ✅ Test with mock bank first
4. ✅ Integrate voice button into your mobile app
5. ✅ Deploy EchoBank to Azure
6. ✅ Go live! 🚀

---

**EchoBank** - Voice Banking for Nigeria, Built for TIC Hackathon 2025
