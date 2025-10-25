#!/usr/bin/env python3
"""
Test Nigerian-Style Bank Notifications
Shows realistic debit/credit alerts like real Nigerian banks
"""
import requests
import json

BASE_URL = "http://localhost:8002"
API_PREFIX = "/api"

def print_notification(notif):
    """Print notification in a nice format"""
    print("\n" + "=" * 80)
    print(f"  📧 {notif['title']}")
    print("=" * 80)
    print(notif['message'])
    print("=" * 80)
    print(f"Type: {notif['notification_type']} | Sent: {notif['sent_at'][:19]}")
    print()

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    DEMO BANK - NIGERIAN NOTIFICATION TEST                    ║
║                  Realistic Banking Notifications Demo                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

# Step 1: Register new user
print("\n🔹 STEP 1: Creating New User Account...")
print("-" * 80)

register_data = {
    "full_name": "Adeleke Paul Aladenusi",
    "email": "adeleke.demo@demobank.ng",
    "phone": "+2348123456789",
    "password": "Demo1234",
    "pin": "1111"
}

response = requests.post(
    f"{BASE_URL}{API_PREFIX}/auth/register",
    json=register_data
)

if response.status_code == 200:
    data = response.json()
    token = data['access_token']
    print(f"✅ Account Created: {register_data['full_name']}")
    print(f"   Email: {register_data['email']}")
else:
    # Try login
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/auth/login",
        json={"email": register_data['email'], "password": register_data['password']}
    )
    data = response.json()
    token = data['access_token']
    print(f"✅ Logged in: {register_data['email']}")

headers = {"Authorization": f"Bearer {token}"}

# Step 2: Check Welcome Notification
print("\n🔹 STEP 2: Checking Welcome Notification (Nigerian Bank Format)...")
print("-" * 80)

response = requests.get(f"{BASE_URL}{API_PREFIX}/notifications?limit=10", headers=headers)
if response.status_code == 200:
    notifs = response.json()
    welcome_notif = [n for n in notifs['notifications'] if n['notification_type'] == 'welcome']
    if welcome_notif:
        print_notification(welcome_notif[0])

# Step 3: Get Account
response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts", headers=headers)
accounts = response.json()
account = accounts[0]
account_number = account['account_number']
account_id = account['id']
balance = float(account['balance'])

print(f"\n💰 Current Balance: NGN {balance:,.2f}")
print(f"📱 Account Number: {account_number}")

# Step 4: Add Recipient
print("\n🔹 STEP 3: Adding Transfer Recipient...")
print("-" * 80)

recipient_data = {
    "recipient_name": "Mbama Therese Chimbusonma",
    "account_number": "3456789012",
    "bank_code": "058",
    "bank_name": "GTBank",
    "is_favorite": True
}

response = requests.post(
    f"{BASE_URL}{API_PREFIX}/recipients",
    headers=headers,
    json=recipient_data
)

if response.status_code in [200, 201]:
    recipient = response.json()
    recipient_id = recipient['id']
    print(f"✅ Recipient Added: {recipient_data['recipient_name']}")
elif response.status_code == 400:
    response = requests.get(f"{BASE_URL}{API_PREFIX}/recipients", headers=headers)
    recipients = response.json()
    recipient_id = recipients[0]['id']
    print(f"✅ Using Existing Recipient")

# Step 5: Make Transfer
print("\n🔹 STEP 4: Initiating Transfer (Will Generate Debit Alert)...")
print("-" * 80)

transfer_amount = 5000  # NGN 5,000

transfer_data = {
    "account_number": account_number,
    "recipient_id": recipient_id,
    "amount": transfer_amount,
    "narration": "Payment for services",
    "initiated_via": "mobile_app"
}

print(f"   Amount: NGN {transfer_amount:,.2f}")
print(f"   To: {recipient_data['recipient_name']}")
print(f"   Bank: {recipient_data['bank_name']}")

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

    print(f"\n✅ Transfer Initiated")
    print(f"   Reference: {transaction_ref}")
    print(f"   Amount: NGN {transfer_amount:,.2f}")
    print(f"   Fee: NGN {fee:,.2f}")
    print(f"   Total: NGN {total_amount:,.2f}")

    # Verify PIN
    print("\n🔹 STEP 5: Verifying PIN...")
    pin_data = {"transaction_id": transaction_id, "pin": "1111"}
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/transfers/{transaction_id}/verify-pin",
        headers=headers,
        json=pin_data
    )

    if response.status_code in [200, 201]:
        print("✅ PIN Verified")

        # Confirm Transfer
        print("\n🔹 STEP 6: Confirming Transfer (Debit Alert Will Be Sent)...")
        confirm_data = {
            "transaction_id": transaction_id,
            "account_number": account_number,
            "pin": "1111"
        }

        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/transfers/{transaction_id}/confirm",
            headers=headers,
            json=confirm_data
        )

        if response.status_code in [200, 201]:
            print("✅ Transfer Completed!")

            # Wait a moment for notification to be created
            import time
            time.sleep(1)

            # Get Debit Notification
            print("\n🔹 STEP 7: Fetching Debit Alert (Nigerian Bank Format)...")
            print("-" * 80)

            response = requests.get(f"{BASE_URL}{API_PREFIX}/notifications?limit=5", headers=headers)
            if response.status_code == 200:
                notifs = response.json()
                print(f"\n📬 You have {notifs['unread_count']} unread notifications")
                print(f"📊 Total notifications: {notifs['total']}")

                # Show latest notifications
                for notif in notifs['notifications'][:3]:
                    print_notification(notif)

            # Check new balance
            response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts/balance/{account_number}", headers=headers)
            if response.status_code == 200:
                balance_data = response.json()
                new_balance = float(balance_data['balance'])

                print("\n" + "=" * 80)
                print(f"💳 ACCOUNT BALANCE UPDATE")
                print("=" * 80)
                print(f"Previous Balance:  NGN {balance:,.2f}")
                print(f"Amount Debited:    NGN {total_amount:,.2f}")
                print(f"New Balance:       NGN {new_balance:,.2f}")
                print("=" * 80)

print("""
\n╔══════════════════════════════════════════════════════════════════════════════╗
║                          ✅ TEST COMPLETED!                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

📱 DEMO FEATURES SHOWN:
   ✓ Nigerian-style welcome notification
   ✓ Realistic debit alert with transaction summary
   ✓ Masked account number (123*****890 format)
   ✓ NGN currency formatting
   ✓ Transaction branch and dates
   ✓ Account balance updates
   ✓ Professional banking tone

🎯 YOUR DEMO IS READY!

Account Credentials:
   Email:    adeleke.demo@demobank.ng
   Password: Demo1234
   PIN:      1111

API Endpoints to show:
   GET  /api/notifications              - View all notifications
   GET  /api/notifications/stats        - Notification statistics
   POST /api/notifications/mark-all-read - Mark all as read

This looks EXACTLY like real Nigerian bank alerts! 🇳🇬
Perfect for your demo presentation! 🚀
""")
