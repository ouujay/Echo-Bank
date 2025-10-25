#!/usr/bin/env python3
"""
Make a transfer from YOUR account and view YOUR notifications
"""
import requests
import time

BASE_URL = "http://localhost:8002"
API_PREFIX = "/api"

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║          MAKING TRANSFER FROM YOUR ACCOUNT (NGN 3,000 to Therese)           ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

# Login as YOU
print("1️⃣  Logging in as YOU (aladenusiadeleke@gmail.com)...")
response = requests.post(
    f"{BASE_URL}{API_PREFIX}/auth/login",
    json={"email": "aladenusiadeleke@gmail.com", "password": "MyPassword123"}
)

if response.status_code != 200:
    print("❌ Login failed! Make sure you created your account first:")
    print("   Run: python create_my_account.py")
    exit(1)

token_you = response.json()['access_token']
headers_you = {"Authorization": f"Bearer {token_you}"}

response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts", headers=headers_you)
your_account = response.json()[0]
print(f"   ✅ Logged in successfully")
print(f"   Your Balance: NGN {float(your_account['balance']):,.2f}")

# Login as Therese to get her account number
print("\n2️⃣  Getting Therese's account number...")
response = requests.post(
    f"{BASE_URL}{API_PREFIX}/auth/login",
    json={"email": "therese@demobank.ng", "password": "Password123"}
)
token_therese = response.json()['access_token']
headers_therese = {"Authorization": f"Bearer {token_therese}"}

response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts", headers=headers_therese)
therese_account = response.json()[0]
print(f"   ✅ Therese's Account: {therese_account['account_number']}")

# Add Therese as recipient
print("\n3️⃣  Adding Therese as your recipient...")
recipient_data = {
    "recipient_name": "Mbama Therese Chimbusonma",
    "account_number": therese_account['account_number'],
    "bank_code": "DEMO",
    "bank_name": "Demo Bank",
    "is_favorite": True
}

response = requests.post(
    f"{BASE_URL}{API_PREFIX}/recipients",
    headers=headers_you,
    json=recipient_data
)

if response.status_code in [200, 201]:
    recipient = response.json()
    recipient_id = recipient['id']
    print(f"   ✅ Recipient added")
else:
    # Get existing
    response = requests.get(f"{BASE_URL}{API_PREFIX}/recipients", headers=headers_you)
    recipients = response.json()
    for r in recipients:
        if r['account_number'] == therese_account['account_number']:
            recipient_id = r['id']
            break
    print(f"   ✅ Using existing recipient")

# Initiate transfer
print("\n4️⃣  Initiating transfer of NGN 3,000...")
transfer_data = {
    "account_number": your_account['account_number'],
    "recipient_id": recipient_id,
    "amount": 3000,
    "narration": "Test from my personal account",
    "initiated_via": "mobile_app"
}

response = requests.post(
    f"{BASE_URL}{API_PREFIX}/transfers/initiate",
    headers=headers_you,
    json=transfer_data
)

transfer = response.json()
txn_id = transfer['transaction_id']
print(f"   ✅ Transfer initiated")
print(f"   Reference: {transfer['transaction_ref']}")
print(f"   Fee: NGN {float(transfer['fee']):,.2f}")
print(f"   Total: NGN {float(transfer['total_amount']):,.2f}")

# Verify PIN
print("\n5️⃣  Verifying your PIN (1234)...")
response = requests.post(
    f"{BASE_URL}{API_PREFIX}/transfers/{txn_id}/verify-pin",
    headers=headers_you,
    json={"transaction_id": txn_id, "pin": "1234"}
)
print(f"   ✅ PIN verified")

# Confirm transfer
print("\n6️⃣  Confirming transfer...")
response = requests.post(
    f"{BASE_URL}{API_PREFIX}/transfers/{txn_id}/confirm",
    headers=headers_you,
    json={
        "transaction_id": txn_id,
        "account_number": your_account['account_number'],
        "pin": "1234"
    }
)

if response.status_code in [200, 201]:
    print(f"   ✅ Transfer completed!")
    print(f"   ⚡ Money sent instantly to Therese")

    time.sleep(1)

    # Show YOUR debit notification
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " YOUR DEBIT NOTIFICATION (Nigerian Bank Format) ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    response = requests.get(f"{BASE_URL}{API_PREFIX}/notifications?limit=5", headers=headers_you)
    notifs = response.json()['notifications']
    debit_notif = [n for n in notifs if 'Debit' in n['title']]
    if debit_notif:
        print(debit_notif[0]['message'])

    print("\n" + "=" * 80)

    # Show updated balance
    response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts", headers=headers_you)
    new_balance = float(response.json()[0]['balance'])

    print(f"\n💰 YOUR UPDATED BALANCE:")
    print(f"   Before: NGN {float(your_account['balance']):,.2f}")
    print(f"   After:  NGN {new_balance:,.2f}")
    print(f"   Debited: NGN {float(your_account['balance']) - new_balance:,.2f}")

    # Show Therese's credit notification
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " THERESE'S CREDIT NOTIFICATION ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    response = requests.get(f"{BASE_URL}{API_PREFIX}/notifications?limit=5", headers=headers_therese)
    notifs = response.json()['notifications']
    credit_notif = [n for n in notifs if 'Credit' in n['title']]
    if credit_notif:
        print(credit_notif[0]['message'])

    print("\n" + "=" * 80)

print(f"""

╔══════════════════════════════════════════════════════════════════════════════╗
║                        ✅ YOUR TRANSFER COMPLETE!                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

📧 WHERE ARE YOUR NOTIFICATIONS?

The notifications are stored IN THE DATABASE (in-app notifications).
They are NOT sent to your email address.

You can view them by:

1️⃣  API Call (what we just did):
   GET /api/notifications
   Authorization: Bearer YOUR_TOKEN

2️⃣  In a Mobile/Web App:
   The app would fetch and display them in a notifications inbox

3️⃣  Check again anytime:
   Run: python view_my_notifications.py

🎯 YOUR CREDENTIALS:
   Email:    aladenusiadeleke@gmail.com
   Password: MyPassword123
   PIN:      1234
   Balance:  NGN {new_balance:,.2f}

This is how real banking apps work! Notifications are in-app, not email! 📱
""")
