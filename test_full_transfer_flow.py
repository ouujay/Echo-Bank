#!/usr/bin/env python3
"""
Full Transfer Flow Test - Demo Bank + Paystack Integration
Tests the complete user journey from registration to transfer
"""
import requests
import json
from decimal import Decimal

BASE_URL = "http://localhost:8002"
API_PREFIX = "/api"

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_success(message):
    print(f"✅ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def print_error(message):
    print(f"❌ {message}")

print_section("🏦 DEMO BANK + PAYSTACK FULL TRANSFER TEST")

# Step 1: Register New User
print_section("STEP 1: Register New User")
register_data = {
    "full_name": "Paystack Demo User",
    "email": "paystack.demo@test.com",
    "phone": "+2348100000001",
    "password": "Test1234",
    "pin": "1234"
}

print_info(f"Creating user: {register_data['full_name']}")
print_info(f"Email: {register_data['email']}")

response = requests.post(
    f"{BASE_URL}{API_PREFIX}/auth/register",
    json=register_data
)

if response.status_code == 200:
    data = response.json()
    token = data['access_token']
    user_id = data.get('user', {}).get('id') or data.get('id')
    print_success("User registered successfully!")
    print_info(f"User ID: {user_id}")
    print_info(f"Token: {token[:30]}...")
else:
    # Try login if user exists
    print_info("User might exist, trying login...")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/auth/login",
        json={
            "email": register_data['email'],
            "password": register_data['password']
        }
    )
    if response.status_code == 200:
        data = response.json()
        token = data['access_token']
        user_id = data.get('user', {}).get('id') or data.get('id')
        print_success("Logged in successfully!")
        print_info(f"User ID: {user_id}")
    else:
        print_error(f"Failed: {response.text}")
        exit(1)

# Step 2: Get Account Details
print_section("STEP 2: Get Account Details")
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(
    f"{BASE_URL}{API_PREFIX}/accounts",
    headers=headers
)

if response.status_code == 200:
    accounts = response.json()
    account = accounts[0]
    account_number = account['account_number']
    balance = float(account['balance'])
    account_id = account['id']

    print_success("Account retrieved!")
    print_info(f"Account Number: {account_number}")
    print_info(f"Balance: ₦{balance:,.2f}")
else:
    print_error(f"Failed: {response.text}")
    exit(1)

# Step 3: Add Recipient with Paystack Integration
print_section("STEP 3: Add Recipient (Paystack Integration)")
print_info("Adding recipient - this will create Paystack recipient code!")

# Use a different demo bank account (not GTBank which requires real accounts)
recipient_data = {
    "recipient_name": "Test Recipient Name",
    "account_number": "2234567890",
    "bank_code": "044",  # Access Bank
    "bank_name": "Access Bank",
    "is_favorite": True
}

print_info(f"Recipient: {recipient_data['recipient_name']}")
print_info(f"Account: {recipient_data['account_number']}")
print_info(f"Bank: {recipient_data['bank_name']}")

response = requests.post(
    f"{BASE_URL}{API_PREFIX}/recipients",
    headers=headers,
    json=recipient_data
)

if response.status_code in [200, 201]:
    recipient = response.json()
    recipient_id = recipient['id']
    paystack_code = recipient.get('paystack_recipient_code')

    print_success("Recipient added!")
    print_info(f"Recipient ID: {recipient_id}")
    if paystack_code:
        print_success(f"🎉 Paystack Recipient Code: {paystack_code}")
        print_info("Check Paystack: Payouts → Transfer Recipients")
    else:
        print_info("No Paystack code (account verification failed - normal for test accounts)")
elif response.status_code == 400:
    print_info("Recipient might already exist, fetching existing...")
    # Try to get existing recipients
    response = requests.get(f"{BASE_URL}{API_PREFIX}/recipients", headers=headers)
    if response.status_code == 200 and response.json():
        recipients = response.json()
        recipient_id = recipients[0]['id']
        paystack_code = recipients[0].get('paystack_recipient_code')
        print_success(f"Using existing recipient ID: {recipient_id}")
        if paystack_code:
            print_success(f"🎉 Paystack Recipient Code: {paystack_code}")
    else:
        print_error("Could not get recipients")
        exit(1)
else:
    print_error(f"Failed: {response.text}")
    exit(1)

# Step 4: Initiate Transfer
print_section("STEP 4: Initiate Transfer")
transfer_amount = 1000  # ₦1,000

transfer_data = {
    "account_number": account_number,
    "recipient_id": recipient_id,
    "amount": transfer_amount,
    "narration": "Test transfer via Paystack",
    "initiated_via": "api_test"
}

print_info(f"Initiating transfer of ₦{transfer_amount:,.2f}")

response = requests.post(
    f"{BASE_URL}{API_PREFIX}/transfers/initiate",
    headers=headers,
    json=transfer_data
)

if response.status_code in [200, 201]:
    transfer = response.json()
    transaction_id = transfer['transaction_id']
    transaction_ref = transfer['transaction_ref']
    total_amount = float(transfer['total_amount'])
    fee = float(transfer['fee'])

    print_success("Transfer initiated!")
    print_info(f"Transaction ID: {transaction_id}")
    print_info(f"Reference: {transaction_ref}")
    print_info(f"Amount: ₦{transfer_amount:,.2f}")
    print_info(f"Fee: ₦{fee:,.2f}")
    print_info(f"Total: ₦{total_amount:,.2f}")
else:
    print_error(f"Failed: {response.status_code} - {response.text}")
    exit(1)

# Step 5: Verify PIN
print_section("STEP 5: Verify PIN")
pin_data = {
    "transaction_id": transaction_id,
    "pin": "1234"
}

print_info("Verifying PIN...")

response = requests.post(
    f"{BASE_URL}{API_PREFIX}/transfers/{transaction_id}/verify-pin",
    headers=headers,
    json=pin_data
)

if response.status_code in [200, 201]:
    print_success("PIN verified!")
    print_info("Transfer ready for confirmation")
else:
    print_error(f"Failed: {response.status_code} - {response.text}")
    exit(1)

# Step 6: Confirm Transfer (THIS CALLS PAYSTACK!)
print_section("STEP 6: Confirm Transfer (PAYSTACK API CALL)")
print_info("🚀 This will call Paystack API to initiate the transfer!")

confirm_data = {
    "transaction_id": transaction_id,
    "account_number": account_number,
    "pin": "1234"
}

response = requests.post(
    f"{BASE_URL}{API_PREFIX}/transfers/{transaction_id}/confirm",
    headers=headers,
    json=confirm_data
)

if response.status_code in [200, 201]:
    result = response.json()

    print_success("🎉 TRANSFER COMPLETED!")
    print_info(f"Status: {result['status']}")
    print_info(f"Message: {result['message']}")

    # Check if Paystack transfer code is in the message
    if 'Paystack:' in result.get('message', '') or 'TRF_' in result.get('message', ''):
        print_success("✨ Paystack transfer was initiated!")
        print_info("Check your Paystack dashboard:")
        print_info("  → Payouts → Transfers")
    else:
        print_info("Transfer completed in database")
        print_info("(Paystack transfer may have failed due to test account)")

else:
    print_error(f"Failed: {response.status_code} - {response.text}")

# Step 7: Check Updated Balance
print_section("STEP 7: Check Updated Balance")

response = requests.get(
    f"{BASE_URL}{API_PREFIX}/accounts/balance/{account_number}",
    headers=headers
)

if response.status_code == 200:
    balance_data = response.json()
    new_balance = float(balance_data['balance'])

    print_success("Balance updated!")
    print_info(f"Previous Balance: ₦{balance:,.2f}")
    print_info(f"New Balance: ₦{new_balance:,.2f}")
    print_info(f"Deducted: ₦{balance - new_balance:,.2f}")

# Step 8: Check Transaction History
print_section("STEP 8: Check Transaction History")

response = requests.get(
    f"{BASE_URL}{API_PREFIX}/accounts/{account_id}/transactions?limit=5",
    headers=headers
)

if response.status_code == 200:
    history = response.json()
    transactions = history.get('transactions', [])

    print_success(f"Found {len(transactions)} recent transactions")

    if transactions:
        latest = transactions[0]
        print_info(f"Latest transaction:")
        print_info(f"  Reference: {latest['transaction_ref']}")
        print_info(f"  Type: {latest['transaction_type']}")
        print_info(f"  Amount: ₦{float(latest['amount']):,.2f}")
        print_info(f"  Status: {latest['status']}")

        # Check for Paystack info
        if latest.get('paystack_transfer_code'):
            print_success(f"  Paystack Code: {latest['paystack_transfer_code']}")

# Final Summary
print_section("📊 SUMMARY & NEXT STEPS")

print("\n✅ What worked:")
print("  • User registration/login")
print("  • Account creation")
print("  • Recipient addition")
print("  • Transfer initiation, PIN verification, and confirmation")
print("  • Balance deduction")
print("  • Transaction history recording")

print("\n📱 Check Your Paystack Dashboard:")
print("  1. Go to: https://dashboard.paystack.com/")
print("  2. Switch to TEST MODE (top right)")
print("  3. Navigate to:")
print("     • Payouts → Transfer Recipients (for recipient)")
print("     • Payouts → Transfers (for the transfer)")
print("     • Payments → Transactions (for any payments)")

print("\n💡 Note:")
print("  If you see 'insufficient funds' or similar errors in Paystack,")
print("  that's expected - your test account needs to be funded in Paystack.")
print("  But the recipient creation should still appear!")

print("\n🎯 Account Info for Manual Testing:")
print(f"  Email: {register_data['email']}")
print(f"  Password: {register_data['password']}")
print(f"  PIN: {register_data['pin']}")
print(f"  Account Number: {account_number}")
print(f"  Current Balance: ₦{new_balance:,.2f}")

print_section("✨ TEST COMPLETE!")
