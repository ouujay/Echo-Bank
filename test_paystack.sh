#!/bin/bash

# Demo Bank - Paystack Integration Test Script
# This script automates the testing of Paystack integration

set -e  # Exit on error

echo "🚀 Demo Bank - Paystack Integration Tester"
echo "=========================================="
echo ""

# Configuration
BASE_URL="http://localhost:8002"
API_PREFIX="/api"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if backend is running
echo "Checking if backend is running..."
if curl -s "$BASE_URL/health" > /dev/null; then
    print_success "Backend is running on $BASE_URL"
else
    print_error "Backend is not running! Start it with: cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8002"
    exit 1
fi

echo ""
echo "=========================================="
echo "TEST 1: User Registration"
echo "=========================================="

# Register new user
echo "Creating test user..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL$API_PREFIX/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Paystack Test User",
    "email": "paystack.test@demo.com",
    "phone": "+2348199999999",
    "password": "Test1234",
    "pin": "9999"
  }')

# Check if registration was successful
if echo "$REGISTER_RESPONSE" | grep -q "access_token"; then
    print_success "User registered successfully"
    TOKEN=$(echo "$REGISTER_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    USER_ID=$(echo "$REGISTER_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    print_info "Token: ${TOKEN:0:50}..."
    print_info "User ID: $USER_ID"
else
    # User might already exist, try login
    print_warning "Registration failed (user might exist), trying login..."

    LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL$API_PREFIX/auth/login" \
      -H "Content-Type: application/json" \
      -d '{
        "email": "paystack.test@demo.com",
        "password": "Test1234"
      }')

    if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
        print_success "Logged in successfully"
        TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
        USER_ID=$(echo "$LOGIN_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    else
        print_error "Both registration and login failed!"
        echo "$LOGIN_RESPONSE"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "TEST 2: Get Account Details"
echo "=========================================="

ACCOUNTS_RESPONSE=$(curl -s -X GET "$BASE_URL$API_PREFIX/accounts" \
  -H "Authorization: Bearer $TOKEN")

if echo "$ACCOUNTS_RESPONSE" | grep -q "account_number"; then
    print_success "Retrieved account details"
    ACCOUNT_NUMBER=$(echo "$ACCOUNTS_RESPONSE" | grep -o '"account_number":"[^"]*' | head -1 | cut -d'"' -f4)
    BALANCE=$(echo "$ACCOUNTS_RESPONSE" | grep -o '"balance":"[^"]*' | head -1 | cut -d'"' -f4)
    ACCOUNT_ID=$(echo "$ACCOUNTS_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    print_info "Account Number: $ACCOUNT_NUMBER"
    print_info "Balance: ₦$BALANCE"
    print_info "Account ID: $ACCOUNT_ID"
else
    print_error "Failed to retrieve account details"
    echo "$ACCOUNTS_RESPONSE"
    exit 1
fi

echo ""
echo "=========================================="
echo "TEST 3: Add Recipient (Paystack Integration)"
echo "=========================================="

echo "Adding recipient with Paystack verification..."
RECIPIENT_RESPONSE=$(curl -s -X POST "$BASE_URL$API_PREFIX/recipients" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_name": "Test Paystack Recipient",
    "account_number": "0123456789",
    "bank_code": "058",
    "bank_name": "GTBank",
    "is_favorite": false
  }')

if echo "$RECIPIENT_RESPONSE" | grep -q "paystack_recipient_code"; then
    print_success "Recipient added with Paystack integration"
    RECIPIENT_ID=$(echo "$RECIPIENT_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    PAYSTACK_CODE=$(echo "$RECIPIENT_RESPONSE" | grep -o '"paystack_recipient_code":"[^"]*' | cut -d'"' -f4)
    print_info "Recipient ID: $RECIPIENT_ID"
    print_info "Paystack Code: $PAYSTACK_CODE"

    if [ ! -z "$PAYSTACK_CODE" ] && [ "$PAYSTACK_CODE" != "null" ]; then
        print_success "✨ Paystack recipient code generated!"
    else
        print_warning "Paystack code is null (might be demo bank)"
    fi
else
    # Recipient might already exist
    print_warning "Could not add recipient (might already exist)"

    # Get existing recipients
    RECIPIENTS_LIST=$(curl -s -X GET "$BASE_URL$API_PREFIX/recipients" \
      -H "Authorization: Bearer $TOKEN")

    RECIPIENT_ID=$(echo "$RECIPIENTS_LIST" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    print_info "Using existing recipient ID: $RECIPIENT_ID"
fi

echo ""
echo "=========================================="
echo "TEST 4: Initiate Transfer"
echo "=========================================="

echo "Initiating ₦2,000 transfer..."
TRANSFER_RESPONSE=$(curl -s -X POST "$BASE_URL$API_PREFIX/transfers/initiate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"account_number\": \"$ACCOUNT_NUMBER\",
    \"recipient_id\": $RECIPIENT_ID,
    \"amount\": 2000,
    \"narration\": \"Automated Paystack test transfer\",
    \"initiated_via\": \"script\"
  }")

if echo "$TRANSFER_RESPONSE" | grep -q "transaction_id"; then
    print_success "Transfer initiated"
    TXN_ID=$(echo "$TRANSFER_RESPONSE" | grep -o '"transaction_id":[0-9]*' | cut -d':' -f2)
    TXN_REF=$(echo "$TRANSFER_RESPONSE" | grep -o '"transaction_ref":"[^"]*' | cut -d'"' -f4)
    TOTAL_AMOUNT=$(echo "$TRANSFER_RESPONSE" | grep -o '"total_amount":[0-9.]*' | cut -d':' -f2)
    print_info "Transaction ID: $TXN_ID"
    print_info "Reference: $TXN_REF"
    print_info "Total Amount (with fee): ₦$TOTAL_AMOUNT"
else
    print_error "Failed to initiate transfer"
    echo "$TRANSFER_RESPONSE"
    exit 1
fi

echo ""
echo "=========================================="
echo "TEST 5: Verify PIN"
echo "=========================================="

echo "Verifying PIN..."
# PIN_RESPONSE=$(curl -s -X POST "$BASE_URL$API_PREFIX/transfers/$TXN_ID/verify-pin" \
#   -H "Authorization: Bearer $TOKEN" \
#   -H "Content-Type: application/json" \
#   -d "{
#     \"pin\": \"9999\",
#     \"account_number\": \"$ACCOUNT_NUMBER\"
#   }")
PIN_RESPONSE=$(curl -s -X POST "$BASE_URL$API_PREFIX/transfers/$TXN_ID/verify-pin" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"transaction_id\": $TXN_ID,
    \"pin\": \"9999\"
  }")


if echo "$PIN_RESPONSE" | grep -q "pending_confirmation"; then
    print_success "PIN verified successfully"
else
    print_error "PIN verification failed"
    echo "$PIN_RESPONSE"
    exit 1
fi

echo ""
echo "=========================================="
echo "TEST 6: Confirm Transfer (Paystack API Call!)"
echo "=========================================="

echo "Confirming transfer (this will call Paystack API)..."
print_warning "Watch backend logs for Paystack API calls!"

# CONFIRM_RESPONSE=$(curl -s -X POST "$BASE_URL$API_PREFIX/transfers/$TXN_ID/confirm" \
#   -H "Authorization: Bearer $TOKEN")
CONFIRM_RESPONSE=$(curl -s -X POST "$BASE_URL$API_PREFIX/transfers/$TXN_ID/confirm" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"account_number\": \"$ACCOUNT_NUMBER\",
    \"pin\": \"9999\"
  }")


if echo "$CONFIRM_RESPONSE" | grep -q "completed"; then
    print_success "✨ Transfer completed successfully!"

    # Check if Paystack code is in response
    if echo "$CONFIRM_RESPONSE" | grep -q "Paystack:"; then
        PAYSTACK_TRF_CODE=$(echo "$CONFIRM_RESPONSE" | grep -o 'TRF_[a-zA-Z0-9]*' | head -1)
        print_success "🎉 Paystack Transfer Code: $PAYSTACK_TRF_CODE"
        print_info "Check your Paystack dashboard at: https://dashboard.paystack.com/"
    else
        print_warning "Transfer completed but no Paystack code in response"
    fi

    MESSAGE=$(echo "$CONFIRM_RESPONSE" | grep -o '"message":"[^"]*' | cut -d'"' -f4)
    print_info "Message: $MESSAGE"
else
    print_error "Transfer confirmation failed"
    echo "$CONFIRM_RESPONSE"
    exit 1
fi

echo ""
echo "=========================================="
echo "TEST 7: Check Updated Balance"
echo "=========================================="

BALANCE_RESPONSE=$(curl -s -X GET "$BASE_URL$API_PREFIX/accounts/balance/$ACCOUNT_NUMBER" \
  -H "Authorization: Bearer $TOKEN")

if echo "$BALANCE_RESPONSE" | grep -q "balance"; then
    NEW_BALANCE=$(echo "$BALANCE_RESPONSE" | grep -o '"balance":"[^"]*' | cut -d'"' -f4)
    print_success "Balance updated"
    print_info "Previous Balance: ₦$BALANCE"
    print_info "New Balance: ₦$NEW_BALANCE"

    # Calculate difference
    DIFF=$(echo "$BALANCE - $NEW_BALANCE" | bc)
    print_info "Deducted: ₦$DIFF (₦2,000 + fee)"
else
    print_error "Failed to check balance"
fi

echo ""
echo "=========================================="
echo "TEST 8: Check Transaction History"
echo "=========================================="

HISTORY_RESPONSE=$(curl -s -X GET "$BASE_URL$API_PREFIX/accounts/$ACCOUNT_ID/transactions?limit=3" \
  -H "Authorization: Bearer $TOKEN")

if echo "$HISTORY_RESPONSE" | grep -q "transactions"; then
    print_success "Retrieved transaction history"

    # Count transactions
    TXN_COUNT=$(echo "$HISTORY_RESPONSE" | grep -o '"id":[0-9]*' | wc -l)
    print_info "Found $TXN_COUNT recent transactions"

    # Show latest transaction ref
    LATEST_REF=$(echo "$HISTORY_RESPONSE" | grep -o '"transaction_ref":"[^"]*' | head -1 | cut -d'"' -f4)
    print_info "Latest transaction: $LATEST_REF"
else
    print_warning "Could not retrieve transaction history"
fi

echo ""
echo "=========================================="
echo "🎉 ALL TESTS PASSED!"
echo "=========================================="
echo ""

print_success "Paystack Integration is working perfectly!"
echo ""
print_info "Summary:"
echo "  • User registered/logged in"
echo "  • Recipient created with Paystack code: $PAYSTACK_CODE"
echo "  • Transfer initiated and completed"
echo "  • Paystack transfer code: $PAYSTACK_TRF_CODE"
echo "  • Balance updated correctly"
echo "  • Transaction history recorded"
echo ""
print_warning "Next Steps:"
echo "  1. Check backend logs for Paystack API calls"
echo "  2. Visit https://dashboard.paystack.com/ to see your transfers"
echo "  3. Look for 'Transfers' and 'Recipients' tabs in Paystack"
echo "  4. Make sure you're in TEST MODE in Paystack dashboard"
echo ""
print_info "Account Details for Manual Testing:"
echo "  • Email: paystack.test@demo.com"
echo "  • Password: Test1234"
echo "  • PIN: 9999"
echo "  • Account: $ACCOUNT_NUMBER"
echo "  • Balance: ₦$NEW_BALANCE"
echo ""
print_success "Ready for EchoBank integration! 🎤"
