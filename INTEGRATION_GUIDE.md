# EchoBank Integration Guide for Banks

## Overview

EchoBank is a **Voice API Service** that adds voice intelligence to your banking app. Your customers can check balances, send money, and manage accounts using natural voice commands.

---

## How It Works

### The Flow:

1. **User logs into YOUR BANK APP** (with your existing authentication)
2. **User taps voice button** in your app
3. **Your app sends audio** to EchoBank API with user's token
4. **EchoBank transcribes** audio using OpenAI Whisper
5. **EchoBank parses intent** using LLM (e.g., "send 5000 to John" → transfer intent)
6. **EchoBank calls YOUR BANK'S API** with the user's token to execute the action
7. **EchoBank returns voice response** (text + audio)
8. **Your app plays** the voice response to user

**Key Point**: EchoBank NEVER stores user data. We just orchestrate the voice layer. All banking operations happen on YOUR servers.

---

## Step 1: Register Your Bank

**Endpoint**: `POST /api/v1/companies/register`

```json
{
  "company_name": "Zenith Bank",
  "email": "api@zenithbank.com",
  "contact_person": "John Doe",
  "phone": "+234123456789",
  "password": "YourSecurePassword"
}
```

**Response**:
```json
{
  "success": true,
  "company_id": 1,
  "company_name": "Zenith Bank",
  "api_key": "echobank_Xb9k2...",
  "message": "Save your API key - you won't see it again!"
}
```

**IMPORTANT**: Save the `api_key` - you'll use it in every request.

---

## Step 2: Configure Your API Endpoints

**Endpoint**: `POST /api/v1/companies/{company_id}/endpoints`

Tell EchoBank where YOUR banking API endpoints are:

```json
{
  "base_url": "https://api.zenithbank.com",
  "auth_type": "bearer",
  "auth_header_name": "Authorization",

  "get_balance_endpoint": "/api/v1/accounts/{account_number}/balance",
  "get_recipients_endpoint": "/api/v1/accounts/{account_number}/beneficiaries",
  "initiate_transfer_endpoint": "/api/v1/transfers/initiate",
  "confirm_transfer_endpoint": "/api/v1/transfers/{transfer_id}/confirm",
  "verify_pin_endpoint": "/api/v1/auth/verify-pin",

  "request_headers": {
    "X-Bank-Id": "zenith",
    "Content-Type": "application/json"
  },

  "response_mapping": {
    "balance_path": "data.account.balance",
    "recipients_path": "data.beneficiaries"
  }
}
```

**What each endpoint does**:

| Endpoint | Purpose | When Called |
|----------|---------|-------------|
| `get_balance` | Get user's account balance | User says "check my balance" |
| `get_recipients` | Get saved beneficiaries | User says "send money to John" |
| `initiate_transfer` | Start a transfer | After finding recipient |
| `confirm_transfer` | Confirm with PIN | User provides PIN |
| `verify_pin` | Verify user's PIN | Before executing transfer |

---

## Step 3: Integrate Voice Button in Your App

### Android Example:

```kotlin
// In your Banking Activity
class BankingActivity : AppCompatActivity() {

    val ECHOBANK_API = "https://api.echobank.com"
    val YOUR_API_KEY = "echobank_Xb9k2..."  // From Step 1

    fun onVoiceButtonClick() {
        // Start recording audio
        startAudioRecording()
    }

    fun sendAudioToEchoBank(audioFile: File) {
        val userToken = getCurrentUserToken()  // From your auth system
        val accountNumber = getCurrentUserAccount()

        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("audio_file", "recording.webm",
                audioFile.asRequestBody("audio/webm".toMediaType()))
            .addFormDataPart("account_number", accountNumber)
            .addFormDataPart("user_token", userToken)  // YOUR user's token
            .addFormDataPart("company_id", "1")  // Your company ID
            .build()

        val request = Request.Builder()
            .url("$ECHOBANK_API/api/v1/voice/process-audio")
            .addHeader("X-API-Key", YOUR_API_KEY)  // EchoBank API key
            .post(requestBody)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onResponse(call: Call, response: Response) {
                val result = response.body?.string()
                val json = JSONObject(result)

                val transcript = json.getString("transcript")
                val responseText = json.getString("response_text")
                val audioBase64 = json.optString("response_audio")

                // Play voice response
                playAudioResponse(audioBase64)

                // Show text in UI
                showTranscript(transcript, responseText)
            }
        })
    }
}
```

### React/JavaScript Example:

```javascript
const ECHOBANK_API = "https://api.echobank.com";
const YOUR_API_KEY = "echobank_Xb9k2...";  // From Step 1

async function sendVoiceToEchoBank(audioBlob) {
  const userToken = getUserToken();  // From your auth system
  const accountNumber = getUserAccount();

  const formData = new FormData();
  formData.append('audio_file', audioBlob, 'recording.webm');
  formData.append('account_number', accountNumber);
  formData.append('user_token', userToken);  // YOUR user's token
  formData.append('company_id', '1');  // Your company ID
  formData.append('include_audio', 'true');

  const response = await fetch(`${ECHOBANK_API}/api/v1/voice/process-audio`, {
    method: 'POST',
    headers: {
      'X-API-Key': YOUR_API_KEY  // EchoBank API key
    },
    body: formData
  });

  const result = await response.json();

  // Play audio response
  const audio = new Audio(`data:audio/mp3;base64,${result.response_audio}`);
  audio.play();

  // Show transcript
  console.log('User said:', result.transcript);
  console.log('Response:', result.response_text);
}
```

---

## Step 4: What YOUR API Must Provide

EchoBank will call YOUR endpoints with the user's token. Your API must:

### 1. Get Balance
**EchoBank calls**: `GET {base_url}/api/v1/accounts/{account_number}/balance`
**Headers**: `Authorization: Bearer {user_token}`

**Your API returns**:
```json
{
  "success": true,
  "data": {
    "balance": 95000.00,
    "currency": "NGN"
  }
}
```

### 2. Get Recipients
**EchoBank calls**: `GET {base_url}/api/v1/accounts/{account_number}/beneficiaries`
**Headers**: `Authorization: Bearer {user_token}`

**Your API returns**:
```json
{
  "success": true,
  "data": {
    "beneficiaries": [
      {
        "name": "John Doe",
        "account_number": "1234567890",
        "bank_name": "Access Bank",
        "bank_code": "044"
      }
    ]
  }
}
```

### 3. Initiate Transfer
**EchoBank calls**: `POST {base_url}/api/v1/transfers/initiate`
**Headers**: `Authorization: Bearer {user_token}`

**Body**:
```json
{
  "sender_account": "0123456789",
  "recipient_account": "1234567890",
  "bank_code": "044",
  "amount": 5000.00,
  "narration": "Voice transfer to John Doe"
}
```

**Your API returns**:
```json
{
  "success": true,
  "data": {
    "transfer_id": "TXN123456",
    "fee": 10.50,
    "total": 5010.50,
    "message": "PIN required to complete transfer"
  }
}
```

### 4. Confirm Transfer
**EchoBank calls**: `POST {base_url}/api/v1/transfers/{transfer_id}/confirm`
**Headers**: `Authorization: Bearer {user_token}`

**Body**:
```json
{
  "pin": "1234"
}
```

**Your API returns**:
```json
{
  "success": true,
  "data": {
    "transaction_ref": "TXN123456",
    "status": "completed",
    "new_balance": 89989.50
  }
}
```

---

## Complete User Flow Example

### User says: "Send 5000 naira to John"

1. **Your app** sends audio to EchoBank
2. **EchoBank** transcribes: "Send 5000 naira to John"
3. **EchoBank** parses intent: `transfer` (amount=5000, recipient="John")
4. **EchoBank** calls YOUR API: `GET /beneficiaries` with user's token
5. **Your API** returns John's details
6. **EchoBank** calls YOUR API: `POST /transfers/initiate`
7. **Your API** creates pending transfer
8. **EchoBank** responds: "Sending 5,000 naira to John. Say your PIN."
9. **User** says: "1-2-3-4"
10. **EchoBank** transcribes PIN
11. **EchoBank** calls YOUR API: `POST /transfers/{id}/confirm` with PIN
12. **Your API** validates PIN and executes transfer
13. **EchoBank** responds: "Transfer successful! 5,000 naira sent to John."

---

## Security

- **User Auth**: User's token from YOUR bank validates all requests to YOUR API
- **API Key**: Your EchoBank API key authenticates YOUR company to our service
- **PIN**: PINs are sent directly to YOUR API, never stored by EchoBank
- **HTTPS**: All requests use TLS encryption
- **No Data Storage**: We don't store user data, transactions, or PINs

---

## Testing

Test your integration with our sandbox environment:

```bash
# Test company registration
curl -X POST https://sandbox.echobank.com/api/v1/companies/register \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Bank",
    "email": "test@testbank.com",
    "contact_person": "Test User",
    "phone": "+234123456789",
    "password": "test123"
  }'
```

---

## Pricing

Contact sales@echobank.com for pricing based on:
- Monthly API calls
- Number of users
- Custom SLA requirements

---

## Support

- **Documentation**: https://docs.echobank.com
- **API Status**: https://status.echobank.com
- **Support**: support@echobank.com
- **Slack**: Join our #integrations channel

---

## Next Steps

1. **Register** your bank: `POST /api/v1/companies/register`
2. **Configure** endpoints: `POST /api/v1/companies/{id}/endpoints`
3. **Test** with sandbox account
4. **Integrate** voice button in your app
5. **Go live** with voice banking!
