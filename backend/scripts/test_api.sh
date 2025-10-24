#!/bin/bash

# EchoBank API Test Script
# Run this after starting the server to test all endpoints

BASE_URL="http://localhost:8000"
echo "=================================================="
echo "🏦 EchoBank API - Automated Test Suite"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to print test header
test_header() {
    echo ""
    echo "=================================================="
    echo "📝 Test $1: $2"
    echo "=================================================="
}

# Function to check if server is running
check_server() {
    echo "🔍 Checking if server is running..."
    if curl -s "$BASE_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Server is running${NC}"
        return 0
    else
        echo -e "${RED}❌ Server is not running. Start it with: uvicorn app.main:app --reload${NC}"
        exit 1
    fi
}

# Function to run test
run_test() {
    local test_name="$1"
    local curl_cmd="$2"
    local expected_status="$3"

    echo ""
    echo "Running: $test_name"

    response=$(eval "$curl_cmd")
    status=$?

    if [ $status -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        echo "Response: $response" | jq '.' 2>/dev/null || echo "$response"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        FAILED=$((FAILED + 1))
    fi
}

# Check server
check_server

# ==========================================
# RECIPIENTS API TESTS
# ==========================================

test_header "1" "Search for Single Recipient (Mary)"
curl -s -X GET "$BASE_URL/api/v1/recipients/search?name=Mary" | jq '.'
echo ""
read -p "Press Enter to continue..."

test_header "2" "Search for Multiple Recipients (John)"
curl -s -X GET "$BASE_URL/api/v1/recipients/search?name=John" | jq '.'
echo ""
read -p "Press Enter to continue..."

test_header "3" "Search for Non-Existent Recipient"
curl -s -X GET "$BASE_URL/api/v1/recipients/search?name=NonExistent" | jq '.'
echo ""
read -p "Press Enter to continue..."

test_header "4" "List All Recipients"
curl -s -X GET "$BASE_URL/api/v1/recipients" | jq '.'
echo ""
read -p "Press Enter to continue..."

test_header "5" "Add New Recipient"
curl -s -X POST "$BASE_URL/api/v1/recipients" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sarah Williams",
    "account_number": "0555555555",
    "bank_name": "UBA",
    "bank_code": "033",
    "is_favorite": false
  }' | jq '.'
echo ""
read -p "Press Enter to continue..."

# ==========================================
# TRANSFERS API TESTS
# ==========================================

test_header "6" "Initiate Transfer (Success - ₦5,000)"
TRANSFER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/transfers/initiate" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": 1,
    "amount": 5000,
    "session_id": "test_session_123"
  }')
echo "$TRANSFER_RESPONSE" | jq '.'
TRANSFER_ID=$(echo "$TRANSFER_RESPONSE" | jq -r '.data.transfer_id')
echo ""
echo -e "${YELLOW}💡 Saved transfer_id: $TRANSFER_ID${NC}"
echo ""
read -p "Press Enter to continue..."

test_header "7" "Initiate Transfer (Insufficient Balance)"
curl -s -X POST "$BASE_URL/api/v1/transfers/initiate" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": 1,
    "amount": 200000,
    "session_id": "test_session_124"
  }' | jq '.'
echo ""
read -p "Press Enter to continue..."

test_header "8" "Initiate Transfer (Daily Limit Exceeded)"
curl -s -X POST "$BASE_URL/api/v1/transfers/initiate" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": 1,
    "amount": 60000,
    "session_id": "test_session_125"
  }' | jq '.'
echo ""
read -p "Press Enter to continue..."

test_header "9" "Verify PIN (Correct - 1234)"
if [ -n "$TRANSFER_ID" ]; then
    curl -s -X POST "$BASE_URL/api/v1/transfers/$TRANSFER_ID/verify-pin" \
      -H "Content-Type: application/json" \
      -d '{
        "pin": "1234"
      }' | jq '.'
else
    echo -e "${RED}❌ No transfer_id available. Skipping...${NC}"
fi
echo ""
read -p "Press Enter to continue..."

test_header "10" "Verify PIN (Wrong PIN)"
# Create new transfer for wrong PIN test
TRANSFER_RESPONSE_2=$(curl -s -X POST "$BASE_URL/api/v1/transfers/initiate" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": 1,
    "amount": 3000,
    "session_id": "test_session_126"
  }')
TRANSFER_ID_2=$(echo "$TRANSFER_RESPONSE_2" | jq -r '.data.transfer_id')

curl -s -X POST "$BASE_URL/api/v1/transfers/$TRANSFER_ID_2/verify-pin" \
  -H "Content-Type: application/json" \
  -d '{
    "pin": "9999"
  }' | jq '.'
echo ""
read -p "Press Enter to continue..."

test_header "11" "Confirm Transfer"
if [ -n "$TRANSFER_ID" ]; then
    curl -s -X POST "$BASE_URL/api/v1/transfers/$TRANSFER_ID/confirm" \
      -H "Content-Type: application/json" \
      -d '{
        "confirmation": "confirm"
      }' | jq '.'
else
    echo -e "${RED}❌ No transfer_id available. Skipping...${NC}"
fi
echo ""
read -p "Press Enter to continue..."

test_header "12" "Cancel Transfer"
# Create new transfer to cancel
TRANSFER_RESPONSE_3=$(curl -s -X POST "$BASE_URL/api/v1/transfers/initiate" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": 2,
    "amount": 2000,
    "session_id": "test_session_127"
  }')
TRANSFER_ID_3=$(echo "$TRANSFER_RESPONSE_3" | jq -r '.data.transfer_id')

curl -s -X POST "$BASE_URL/api/v1/transfers/$TRANSFER_ID_3/cancel" \
  -H "Content-Type: application/json" | jq '.'
echo ""

# ==========================================
# SUMMARY
# ==========================================

echo ""
echo "=================================================="
echo "📊 Test Summary"
echo "=================================================="
echo "✅ Tests completed!"
echo ""
echo "To verify the results:"
echo "1. Check API docs: http://localhost:8000/docs"
echo "2. Check database: psql -U postgres -d echobank"
echo ""
echo "=================================================="
