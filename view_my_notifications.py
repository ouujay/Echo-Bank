#!/usr/bin/env python3
"""
View YOUR notifications anytime
"""
import requests

BASE_URL = "http://localhost:8002"
API_PREFIX = "/api"

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     YOUR DEMO BANK NOTIFICATIONS                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

# Login
print("Logging in as aladenusiadeleke@gmail.com...")
response = requests.post(
    f"{BASE_URL}{API_PREFIX}/auth/login",
    json={"email": "aladenusiadeleke@gmail.com", "password": "MyPassword123"}
)

if response.status_code != 200:
    print("❌ Login failed! Create your account first:")
    print("   Run: python create_my_account.py")
    exit(1)

token = response.json()['access_token']
headers = {"Authorization": f"Bearer {token}"}

# Get account
response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts", headers=headers)
account = response.json()[0]

print(f"✅ Logged in!\n")
print(f"💳 Account: {account['account_number']}")
print(f"💰 Balance: NGN {float(account['balance']):,.2f}\n")

# Get notifications
response = requests.get(f"{BASE_URL}{API_PREFIX}/notifications?limit=10", headers=headers)
notifs_data = response.json()

print(f"📧 NOTIFICATIONS ({notifs_data['total']} total, {notifs_data['unread_count']} unread)")
print("=" * 80)

for i, notif in enumerate(notifs_data['notifications'], 1):
    print(f"\n[{i}] {notif['title']}")
    print(f"    Type: {notif['notification_type']}")
    print(f"    Date: {notif['sent_at'][:19]}")
    print(f"    Read: {'Yes' if notif['is_read'] else 'No'}")
    print(f"\n    Message:")
    print("    " + "-" * 76)
    for line in notif['message'].split('\n'):
        if line.strip():
            print(f"    {line}")
    print("    " + "-" * 76)

# Get transactions
print(f"\n\n💸 TRANSACTION HISTORY")
print("=" * 80)

response = requests.get(
    f"{BASE_URL}{API_PREFIX}/accounts/{account['id']}/transactions?limit=5",
    headers=headers
)
txns = response.json().get('transactions', [])

if txns:
    for i, txn in enumerate(txns, 1):
        print(f"\n[{i}] {txn['transaction_type'].upper()}")
        print(f"    Amount: NGN {float(txn['amount']):,.2f}")
        print(f"    Status: {txn['status']}")
        print(f"    Reference: {txn['transaction_ref']}")
        if txn.get('recipient_name'):
            direction = "To" if txn['transaction_type'] == 'transfer' else "From"
            print(f"    {direction}: {txn['recipient_name']}")
        print(f"    Date: {txn.get('initiated_at', 'N/A')[:19]}")
else:
    print("No transactions yet")

print(f"""

╔══════════════════════════════════════════════════════════════════════════════╗
║                         📱 IN-APP NOTIFICATIONS                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

These notifications are stored in the database (like in real banking apps).
They would appear in your notifications inbox in a mobile app.

They are NOT sent to email - that would require SMTP configuration.

For your demo, this is PERFECT because:
✓ Judges can see instant notifications
✓ Both sender and recipient can view them
✓ Professional Nigerian bank format
✓ Complete transaction history

Your credentials:
Email: aladenusiadeleke@gmail.com
Password: MyPassword123
PIN: 1234
""")
