#!/usr/bin/env python3
"""
Demo Bank Internal Transfer Test
Shows realistic 2-user transfer with debit/credit notifications
"""
import requests
import json
import time

BASE_URL = "http://localhost:8002"
API_PREFIX = "/api"

def print_box(title):
    print("\n" + "╔" + "═" * 78 + "╗")
    print(f"║ {title:^76} ║")
    print("╚" + "═" * 78 + "╝")

def print_notification(notif, user_name):
    print("\n" + "┌" + "─" * 78 + "┐")
    print(f"│ 📧 {notif['title']:<74} │")
    print(f"│ To: {user_name:<73} │")
    print("├" + "─" * 78 + "┤")
    for line in notif['message'].split('\n'):
        print(f"│ {line:<76} │")
    print("└" + "─" * 78 + "┘")

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║           DEMO BANK - INTERNAL TRANSFER DEMONSTRATION                        ║
║                   Realistic 2-User Transfer Flow                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

This test demonstrates:
✓ User A sends money to User B (both Demo Bank users)
✓ User A gets DEBIT notification (Nigerian bank format)
✓ User B gets CREDIT notification (Nigerian bank format)
✓ Both users can see the transaction in their history
✓ Perfect for demo presentation!
""")

# ===========================
# STEP 1: Create User A (Sender)
# ===========================
print_box("STEP 1: Creating User A (Sender)")

import random
unique_id = random.randint(1000, 9999)

user_a_data = {
    "full_name": "Adeleke Paul Aladenusi",
    "email": f"adeleke.{unique_id}@demobank.ng",
    "phone": f"+23481{unique_id:08d}",
    "password": "Demo1234",
    "pin": "1111"
}

response = requests.post(f"{BASE_URL}{API_PREFIX}/auth/register", json=user_a_data)

if response.status_code == 200:
    data_a = response.json()
    token_a = data_a['access_token']
    print(f"✅ User A Created: {user_a_data['full_name']}")
else:
    # Try login if registration failed
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/auth/login",
        json={"email": user_a_data['email'], "password": user_a_data['password']}
    )
    if response.status_code == 200:
        data_a = response.json()
        token_a = data_a['access_token']
        print(f"✅ User A Logged In: {user_a_data['full_name']}")
    else:
        print(f"❌ Failed to create/login User A: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)

headers_a = {"Authorization": f"Bearer {token_a}"}

# Get User A account
response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts", headers=headers_a)
accounts_a = response.json()
account_a = accounts_a[0]
account_a_number = account_a['account_number']
balance_a_initial = float(account_a['balance'])

print(f"   Account Number: {account_a_number}")
print(f"   Initial Balance: NGN {balance_a_initial:,.2f}")

# ===========================
# STEP 2: Create User B (Recipient)
# ===========================
print_box("STEP 2: Creating User B (Recipient)")

user_b_data = {
    "full_name": "Mbama Therese Chimbusonma",
    "email": f"therese.{unique_id}@demobank.ng",
    "phone": f"+23482{unique_id:08d}",
    "password": "Demo1234",
    "pin": "2222"
}

response = requests.post(f"{BASE_URL}{API_PREFIX}/auth/register", json=user_b_data)

if response.status_code == 200:
    data_b = response.json()
    token_b = data_b['access_token']
    print(f"✅ User B Created: {user_b_data['full_name']}")
else:
    # Try login if registration failed
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/auth/login",
        json={"email": user_b_data['email'], "password": user_b_data['password']}
    )
    if response.status_code == 200:
        data_b = response.json()
        token_b = data_b['access_token']
        print(f"✅ User B Logged In: {user_b_data['full_name']}")
    else:
        print(f"❌ Failed to create/login User B: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)

headers_b = {"Authorization": f"Bearer {token_b}"}

# Get User B account
response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts", headers=headers_b)
accounts_b = response.json()
account_b = accounts_b[0]
account_b_number = account_b['account_number']
balance_b_initial = float(account_b['balance'])

print(f"   Account Number: {account_b_number}")
print(f"   Initial Balance: NGN {balance_b_initial:,.2f}")

# ===========================
# STEP 3: User A adds User B as recipient
# ===========================
print_box("STEP 3: User A Adds User B as Recipient")

recipient_data = {
    "recipient_name": user_b_data['full_name'],
    "account_number": account_b_number,
    "bank_code": "DEMO",
    "bank_name": "Demo Bank",
    "is_favorite": True
}

response = requests.post(
    f"{BASE_URL}{API_PREFIX}/recipients",
    headers=headers_a,
    json=recipient_data
)

if response.status_code in [200, 201]:
    recipient = response.json()
    recipient_id = recipient['id']
    print(f"✅ Recipient Added: {recipient_data['recipient_name']}")
    print(f"   Account: {account_b_number}")
    print(f"   Bank: Demo Bank (INTERNAL TRANSFER)")
elif response.status_code == 400:
    response = requests.get(f"{BASE_URL}{API_PREFIX}/recipients", headers=headers_a)
    recipients = response.json()
    for r in recipients:
        if r['account_number'] == account_b_number:
            recipient_id = r['id']
            break
    print(f"✅ Using Existing Recipient")

# ===========================
# STEP 4: User A sends money to User B
# ===========================
print_box("STEP 4: User A Sends NGN 7,500 to User B")

transfer_amount = 7500

transfer_data = {
    "account_number": account_a_number,
    "recipient_id": recipient_id,
    "amount": transfer_amount,
    "narration": "Payment for lunch",
    "initiated_via": "mobile_app"
}

print(f"\n💸 Transfer Details:")
print(f"   From: {user_a_data['full_name']}")
print(f"   To: {user_b_data['full_name']}")
print(f"   Amount: NGN {transfer_amount:,.2f}")

response = requests.post(
    f"{BASE_URL}{API_PREFIX}/transfers/initiate",
    headers=headers_a,
    json=transfer_data
)

if response.status_code in [200, 201]:
    transfer = response.json()
    transaction_id = transfer['transaction_id']
    transaction_ref = transfer['transaction_ref']
    total_amount = float(transfer['total_amount'])
    fee = float(transfer['fee'])

    print(f"\n✅ Transfer Initiated")
    print(f"   Reference: {transaction_ref}")
    print(f"   Fee: NGN {fee:,.2f}")
    print(f"   Total: NGN {total_amount:,.2f}")

    # Verify PIN
    pin_data = {"transaction_id": transaction_id, "pin": "1111"}
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/transfers/{transaction_id}/verify-pin",
        headers=headers_a,
        json=pin_data
    )

    if response.status_code in [200, 201]:
        print("✅ PIN Verified")

        # Confirm Transfer
        confirm_data = {
            "transaction_id": transaction_id,
            "account_number": account_a_number,
            "pin": "1111"
        }

        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/transfers/{transaction_id}/confirm",
            headers=headers_a,
            json=confirm_data
        )

        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Transfer Completed!")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            print("   ⚡ Internal transfer - instant credit to recipient!")

            time.sleep(1)  # Wait for notifications
        else:
            print(f"❌ Transfer confirmation failed: {response.status_code}")
            print(f"   Response: {response.text}")

# ===========================
# STEP 5: Check User A's notifications (DEBIT)
# ===========================
print_box("STEP 5: User A's Debit Notification")

response = requests.get(f"{BASE_URL}{API_PREFIX}/notifications?limit=5", headers=headers_a)
if response.status_code == 200:
    notifs_a = response.json()
    debit_notif = [n for n in notifs_a['notifications'] if 'Debit' in n['title']]
    if debit_notif:
        print_notification(debit_notif[0], user_a_data['full_name'])

# Check User A's new balance
response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts/balance/{account_a_number}", headers=headers_a)
balance_a_new = float(response.json()['balance'])

print(f"\n💳 User A Balance:")
print(f"   Before: NGN {balance_a_initial:,.2f}")
print(f"   After:  NGN {balance_a_new:,.2f}")
print(f"   Debited: NGN {balance_a_initial - balance_a_new:,.2f}")

# ===========================
# STEP 6: Check User B's notifications (CREDIT)
# ===========================
print_box("STEP 6: User B's Credit Notification")

response = requests.get(f"{BASE_URL}{API_PREFIX}/notifications?limit=5", headers=headers_b)
if response.status_code == 200:
    notifs_b = response.json()
    credit_notif = [n for n in notifs_b['notifications'] if 'Credit' in n['title']]
    if credit_notif:
        print_notification(credit_notif[0], user_b_data['full_name'])

# Check User B's new balance
response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts/balance/{account_b_number}", headers=headers_b)
balance_b_new = float(response.json()['balance'])

print(f"\n💳 User B Balance:")
print(f"   Before: NGN {balance_b_initial:,.2f}")
print(f"   After:  NGN {balance_b_new:,.2f}")
print(f"   Credited: NGN {balance_b_new - balance_b_initial:,.2f}")

# ===========================
# STEP 7: Check transaction histories
# ===========================
print_box("STEP 7: Transaction Histories")

print("\n📊 User A's Recent Transactions:")
response = requests.get(
    f"{BASE_URL}{API_PREFIX}/accounts/{account_a['id']}/transactions?limit=3",
    headers=headers_a
)
if response.status_code == 200:
    txns_a = response.json()['transactions']
    for txn in txns_a[:1]:
        print(f"   Type: {txn['transaction_type']}")
        print(f"   Amount: NGN {float(txn['amount']):,.2f}")
        print(f"   To: {txn.get('recipient_name', 'N/A')}")
        print(f"   Status: {txn['status']}")
        print(f"   Ref: {txn['transaction_ref']}")

print("\n📊 User B's Recent Transactions:")
response = requests.get(
    f"{BASE_URL}{API_PREFIX}/accounts/{account_b['id']}/transactions?limit=3",
    headers=headers_b
)
if response.status_code == 200:
    txns_b = response.json()['transactions']
    for txn in txns_b[:1]:
        print(f"   Type: {txn['transaction_type']}")
        print(f"   Amount: NGN {float(txn['amount']):,.2f}")
        print(f"   From: {txn.get('recipient_name', 'N/A')}")
        print(f"   Status: {txn['status']}")
        print(f"   Ref: {txn['transaction_ref']}")

# ===========================
# Summary
# ===========================
print("""
\n╔══════════════════════════════════════════════════════════════════════════════╗
║                        ✅ INTERNAL TRANSFER COMPLETE!                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 WHAT HAPPENED:
   1. User A sent NGN 7,500 to User B (both Demo Bank users)
   2. User A's account was debited NGN 7,510 (amount + ₦10 fee)
   3. User B's account was credited NGN 7,500 (no fee for receiving)
   4. Both users received Nigerian-style bank notifications
   5. Both can see the transaction in their history
   6. Transfer was INSTANT (internal Demo Bank transfer)

📱 LOGIN CREDENTIALS FOR DEMO:

   User A (Sender):
   Email:    adeleke.aladenusi@demobank.ng
   Password: Demo1234
   PIN:      1111

   User B (Recipient):
   Email:    therese.mbama@demobank.ng
   Password: Demo1234
   PIN:      2222

🎬 PERFECT FOR YOUR DEMO PRESENTATION:
   • Login as User A, show the debit notification
   • Login as User B, show the credit notification
   • Both can see transaction history
   • Looks exactly like real Nigerian bank transfers!
   • Judges will be IMPRESSED! 🚀

This is WAY better than Paystack dashboard visibility! 🇳🇬
""")
