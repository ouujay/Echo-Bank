#!/usr/bin/env python3
"""
Simple Paystack Integration Test
Tests the integration and shows results in Paystack dashboard
"""
import sys
import os

# Add backend to path
sys.path.insert(0, '/Users/useruser/Documents/demo-bank/backend')

from app.services.paystack import paystack_service
from decimal import Decimal
from datetime import datetime
import json

print("=" * 60)
print("🧪 PAYSTACK INTEGRATION TEST")
print("=" * 60)
print()

# Test 1: Get Banks
print("TEST 1: Fetch Nigerian Banks")
print("-" * 60)
banks_result = paystack_service.get_banks()
if banks_result['success']:
    print(f"✅ SUCCESS: Retrieved {len(banks_result['banks'])} banks")
    print(f"   Sample: {banks_result['banks'][0]['name']} ({banks_result['banks'][0]['code']})")
else:
    print(f"❌ FAILED: {banks_result.get('error')}")
print()

# Test 2: Create Transfer Recipient
print("TEST 2: Create Transfer Recipient")
print("-" * 60)
print("   Creating recipient for 'John Doe'...")
recipient_result = paystack_service.create_transfer_recipient(
    recipient_name="John Doe Test Recipient",
    account_number="0123456789",
    bank_code="058",  # GTBank
    currency="NGN"
)

if recipient_result['success']:
    recipient_code = recipient_result['recipient_code']
    print(f"✅ SUCCESS: Recipient created!")
    print(f"   Recipient Code: {recipient_code}")
    print(f"   Recipient ID: {recipient_result['recipient_id']}")
    print()
    print(f"📊 CHECK YOUR DASHBOARD:")
    print(f"   Go to: Payouts → Transfer Recipients")
    print(f"   Look for: 'John Doe Test Recipient'")
    print()

    # Test 3: Initiate Transfer
    print("TEST 3: Initiate Transfer to Recipient")
    print("-" * 60)
    print("   Initiating ₦100 transfer...")

    transfer_result = paystack_service.initiate_transfer(
        recipient_code=recipient_code,
        amount=Decimal("100"),
        reason="Test transfer from Demo Bank API"
    )

    if transfer_result['success']:
        print(f"✅ SUCCESS: Transfer initiated!")
        print(f"   Transfer Code: {transfer_result['transfer_code']}")
        print(f"   Transfer ID: {transfer_result['transfer_id']}")
        print(f"   Status: {transfer_result['status']}")
        print(f"   Amount: ₦{transfer_result['amount']}")
        print()
        print(f"📊 CHECK YOUR DASHBOARD:")
        print(f"   Go to: Payouts → Transfers")
        print(f"   Look for: Transfer to 'John Doe Test Recipient' (₦100)")
        print(f"   Reference: {transfer_result['transfer_code']}")
    else:
        print(f"⚠️  Transfer failed: {transfer_result.get('error')}")
        print(f"   (This is expected in test mode without balance)")
        print(f"   But recipient was created successfully!")
else:
    print(f"⚠️  {recipient_result.get('error')}")

print()

# Test 4: Initialize Payment Transaction
print("TEST 4: Initialize Payment Transaction")
print("-" * 60)
print("   Creating payment session for ₦5,000...")

payment_result = paystack_service.initialize_transaction(
    email="test@demobank.com",
    amount=Decimal("5000"),
    reference="TEST_PAYMENT_" + str(int(datetime.now().timestamp())),
    metadata={
        "customer_name": "Test Customer",
        "purpose": "Demo Bank Integration Test"
    }
)

if payment_result['success']:
    print(f"✅ SUCCESS: Payment session created!")
    print(f"   Reference: {payment_result['reference']}")
    print(f"   Authorization URL: {payment_result['authorization_url'][:60]}...")
    print()
    print(f"📊 CHECK YOUR DASHBOARD:")
    print(f"   Go to: Payments → Transactions")
    print(f"   Look for: Payment from 'test@demobank.com' (₦5,000)")
    print(f"   Status will be 'Abandoned' (not paid)")
else:
    print(f"❌ FAILED: {payment_result.get('error')}")

print()
print("=" * 60)
print("✅ TESTS COMPLETE!")
print("=" * 60)
print()
print("🔍 NEXT STEPS:")
print("   1. Go to https://dashboard.paystack.com/")
print("   2. Make sure you're in TEST MODE (top right)")
print("   3. Check these sections:")
print("      • Payouts → Transfer Recipients")
print("      • Payouts → Transfers")
print("      • Payments → Transactions")
print()
print("   You should see the test data created above!")
print()
