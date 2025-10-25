#!/usr/bin/env python3
"""
Make ONE transfer from Adeleke to Therese and show notifications
"""
import requests
import time

BASE_URL = "http://localhost:8002"
API_PREFIX = "/api"

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              MAKING TRANSFER: Adeleke → Therese (₦5,000)                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

# Login as Adeleke
print("1️⃣  Logging in as Adeleke...")
response = requests.post(
    f"{BASE_URL}{API_PREFIX}/auth/login",
    json={"email": "adeleke@demobank.ng", "password": "Password123"}
)
token_a = response.json()['access_token']
headers_a = {"Authorization": f"Bearer {token_a}"}

response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts", headers=headers_a)
account_a = response.json()[0]
print(f"   ✅ Adeleke logged in")
print(f"   Account: {account_a['account_number']}")
print(f"   Balance: NGN {float(account_a['balance']):,.2f}")

# Login as Therese
print("\n2️⃣  Logging in as Therese...")
response = requests.post(
    f"{BASE_URL}{API_PREFIX}/auth/login",
    json={"email": "therese@demobank.ng", "password": "Password123"}
)
token_b = response.json()['access_token']
headers_b = {"Authorization": f"Bearer {token_b}"}

response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts", headers=headers_b)
account_b = response.json()[0]
print(f"   ✅ Therese logged in")
print(f"   Account: {account_b['account_number']}")
print(f"   Balance: NGN {float(account_b['balance']):,.2f}")

# Add Therese as recipient for Adeleke
print("\n3️⃣  Adding Therese as recipient...")
recipient_data = {
    "recipient_name": "Mbama Therese Chimbusonma",
    "account_number": account_b['account_number'],
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
    print(f"   ✅ Recipient added")
else:
    # Get existing
    response = requests.get(f"{BASE_URL}{API_PREFIX}/recipients", headers=headers_a)
    recipients = response.json()
    for r in recipients:
        if r['account_number'] == account_b['account_number']:
            recipient_id = r['id']
            break
    print(f"   ✅ Using existing recipient")

# Initiate transfer
print("\n4️⃣  Initiating transfer of NGN 5,000...")
transfer_data = {
    "account_number": account_a['account_number'],
    "recipient_id": recipient_id,
    "amount": 5000,
    "narration": "Demo transfer",
    "initiated_via": "mobile_app"
}

response = requests.post(
    f"{BASE_URL}{API_PREFIX}/transfers/initiate",
    headers=headers_a,
    json=transfer_data
)

if response.status_code in [200, 201]:
    transfer = response.json()
    txn_id = transfer['transaction_id']
    print(f"   ✅ Transfer initiated")
    print(f"   Reference: {transfer['transaction_ref']}")
    print(f"   Fee: NGN {float(transfer['fee']):,.2f}")

    # Verify PIN
    print("\n5️⃣  Verifying PIN...")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/transfers/{txn_id}/verify-pin",
        headers=headers_a,
        json={"transaction_id": txn_id, "pin": "1111"}
    )
    print(f"   ✅ PIN verified")

    # Confirm transfer
    print("\n6️⃣  Confirming transfer...")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/transfers/{txn_id}/confirm",
        headers=headers_a,
        json={
            "transaction_id": txn_id,
            "account_number": account_a['account_number'],
            "pin": "1111"
        }
    )

    if response.status_code in [200, 201]:
        print(f"   ✅ Transfer completed!")
        print(f"   ⚡ Instant internal transfer")

        time.sleep(1)

        # Show Adeleke's debit notification
        print("\n" + "=" * 80)
        print("📧 ADELEKE'S DEBIT NOTIFICATION")
        print("=" * 80)
        response = requests.get(f"{BASE_URL}{API_PREFIX}/notifications?limit=3", headers=headers_a)
        notifs = response.json()['notifications']
        debit_notif = [n for n in notifs if 'Debit' in n['title']]
        if debit_notif:
            print(debit_notif[0]['message'])

        # Show Therese's credit notification
        print("\n" + "=" * 80)
        print("📧 THERESE'S CREDIT NOTIFICATION")
        print("=" * 80)
        response = requests.get(f"{BASE_URL}{API_PREFIX}/notifications?limit=3", headers=headers_b)
        notifs = response.json()['notifications']
        credit_notif = [n for n in notifs if 'Credit' in n['title']]
        if credit_notif:
            print(credit_notif[0]['message'])

        # Show updated balances
        print("\n" + "=" * 80)
        print("💰 UPDATED BALANCES")
        print("=" * 80)

        response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts", headers=headers_a)
        new_balance_a = float(response.json()[0]['balance'])

        response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts", headers=headers_b)
        new_balance_b = float(response.json()[0]['balance'])

        print(f"\nADELEKE (Sender):")
        print(f"   Before: NGN {float(account_a['balance']):,.2f}")
        print(f"   After:  NGN {new_balance_a:,.2f}")
        print(f"   Debited: NGN {float(account_a['balance']) - new_balance_a:,.2f}")

        print(f"\nTHERESE (Recipient):")
        print(f"   Before: NGN {float(account_b['balance']):,.2f}")
        print(f"   After:  NGN {new_balance_b:,.2f}")
        print(f"   Credited: NGN {new_balance_b - float(account_b['balance']):,.2f}")

print("""
\n╔══════════════════════════════════════════════════════════════════════════════╗
║                        ✅ TRANSFER COMPLETE!                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 NOW YOU CAN LOGIN AS EACH USER:

   Login as Adeleke:
   Email: adeleke@demobank.ng
   Password: Password123
   → You'll see DEBIT notification

   Login as Therese:
   Email: therese@demobank.ng
   Password: Password123
   → You'll see CREDIT notification

Run: python check_both_users.py to see both accounts! 🚀
""")
