// MOCK SERVICE FOR TESTING ONLY
// This file provides mock data for testing the UI without backend
// TODO: Remove this file before production deployment

export const mockVoiceService = {
  async transcribeAudio(audioBlob, sessionId = null) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    return {
      success: true,
      data: {
        transcript: "Send 5000 naira to John",
        confidence: 0.95,
        session_id: sessionId || `sess_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date().toISOString()
      }
    };
  },

  async parseIntent(transcript, sessionId) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 800));

    // Parse different intents based on transcript
    if (transcript.toLowerCase().includes('send') || transcript.toLowerCase().includes('transfer')) {
      return {
        success: true,
        data: {
          intent: 'transfer',
          confidence: 0.92,
          entities: {
            action: 'send',
            amount: 5000,
            currency: 'NGN',
            recipient: 'John'
          },
          next_step: 'verify_recipient'
        }
      };
    } else if (transcript.toLowerCase().includes('balance')) {
      return {
        success: true,
        data: {
          intent: 'check_balance',
          confidence: 0.95,
          entities: {},
          next_step: 'complete'
        }
      };
    } else {
      return {
        success: true,
        data: {
          intent: 'unknown',
          confidence: 0.5,
          entities: {},
          next_step: 'clarify'
        }
      };
    }
  },

  async getSession(sessionId) {
    return {
      success: true,
      data: {
        session_id: sessionId,
        user_id: 'demo_user',
        current_step: 'pending_pin',
        context: {},
        created_at: new Date().toISOString()
      }
    };
  }
};

export const mockTransferService = {
  async searchRecipients(name, limit = 5) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 600));

    return {
      success: true,
      data: {
        recipients: [
          {
            id: 'recp_123',
            name: 'John Okafor',
            account_number: '0123456789',
            bank_name: 'Zenith Bank',
            bank_code: '057'
          }
        ],
        match_type: 'single',
        message: `Found John Okafor at Zenith Bank.`
      }
    };
  },

  async initiateTransfer(recipientId, amount, sessionId) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 800));

    return {
      success: true,
      data: {
        transfer_id: `txn_${Math.random().toString(36).substr(2, 10).toUpperCase()}`,
        status: 'pending_pin',
        recipient: {
          name: 'John Okafor',
          account_number: '0123456789',
          bank_name: 'Zenith Bank'
        },
        amount: amount,
        currency: 'NGN',
        current_balance: 45320,
        new_balance: 45320 - amount,
        message: `Sending ₦${amount.toLocaleString()} to John Okafor. Please say your 4-digit PIN.`
      }
    };
  },

  async verifyPin(transferId, pin) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Mock PIN validation (accept "1234" as correct PIN)
    if (pin === '1234') {
      return {
        success: true,
        data: {
          transfer_id: transferId,
          status: 'pending_confirmation',
          pin_verified: true,
          message: "PIN verified. Say 'confirm' to complete the transfer."
        }
      };
    } else {
      throw {
        response: {
          data: {
            success: false,
            error: {
              code: 'INVALID_PIN',
              message: 'Incorrect PIN. You have 2 attempts remaining.',
              attempts_remaining: 2
            }
          }
        }
      };
    }
  },

  async confirmTransfer(transferId) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1200));

    return {
      success: true,
      data: {
        transfer_id: transferId,
        status: 'completed',
        recipient: {
          name: 'John Okafor',
          account_number: '0123456789'
        },
        amount: 5000,
        transaction_ref: `REF${Math.random().toString(36).substr(2, 10).toUpperCase()}`,
        timestamp: new Date().toISOString(),
        new_balance: 40320,
        message: '✅ Transfer successful! ₦5,000 sent to John Okafor. New balance: ₦40,320.'
      }
    };
  },

  async cancelTransfer(transferId) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    return {
      success: true,
      data: {
        transfer_id: transferId,
        status: 'cancelled',
        message: 'Transfer cancelled. No money was sent.'
      }
    };
  }
};
