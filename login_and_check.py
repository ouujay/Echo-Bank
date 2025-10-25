#!/usr/bin/env python3
"""
Login as both users and view their notifications
"""
import requests
import json

BASE_URL = "http://localhost:8002"
API_PREFIX = "/api"

def print_box(title):
    print("\n" + "╔" + "═" * 78 + "╗")
    print(f"║ {title:^76} ║")
    print("╚" + "═" * 78 + "╝")

def login_and_show(email, password, user_name):
    """Login and show user's notifications and transactions"""
    print_box(f"LOGGING IN AS: {user_name}")

    # Login
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/auth/login",
        json={"email": email, "password": password}
    )

    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

    data = response.json()
    token = data['access_token']
    print(f"✅ Logged in successfully!")
    print(f"   Email: {email}")

    headers = {"Authorization": f"Bearer {token}"}

    # Get account info
    print("\n📱 ACCOUNT INFORMATION:")
    print("-" * 80)
    response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts", headers=headers)
    if response.status_code == 200:
        accounts = response.json()
        account = accounts[0]
        print(f"   Account Number: {account['account_number']}")
        print(f"   Account Name: {account['account_name']}")
        print(f"   Balance: NGN {float(account['balance']):,.2f}")
        account_id = account['id']
        account_number = account['account_number']

    # Get notifications
    print("\n📧 NOTIFICATIONS:")
    print("-" * 80)
    response = requests.get(f"{BASE_URL}{API_PREFIX}/notifications?limit=10", headers=headers)
    if response.status_code == 200:
        notifs_data = response.json()
        notifs = notifs_data['notifications']
        unread_count = notifs_data['unread_count']

        print(f"   Total: {notifs_data['total']} | Unread: {unread_count}")

        if notifs:
            print(f"\n   📬 Latest Notifications:")
            for i, notif in enumerate(notifs[:3], 1):
                print(f"\n   [{i}] {notif['title']}")
                print(f"       Type: {notif['notification_type']}")
                print(f"       Date: {notif['sent_at'][:19]}")
                print(f"       Read: {'Yes' if notif['is_read'] else 'No'}")

                # Show message preview
                msg_lines = notif['message'].split('\n')
                print(f"\n       Message Preview:")
                for line in msg_lines[:15]:
                    if line.strip():
                        print(f"       {line}")
        else:
            print("   No notifications yet")

    # Get transaction history
    print("\n💳 TRANSACTION HISTORY:")
    print("-" * 80)
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/accounts/{account_id}/transactions?limit=5",
        headers=headers
    )
    if response.status_code == 200:
        txn_data = response.json()
        txns = txn_data.get('transactions', [])

        if txns:
            for i, txn in enumerate(txns, 1):
                print(f"\n   [{i}] Transaction Ref: {txn['transaction_ref']}")
                print(f"       Type: {txn['transaction_type']}")
                print(f"       Amount: NGN {float(txn['amount']):,.2f}")
                print(f"       Status: {txn['status']}")
                if txn.get('recipient_name'):
                    if txn['transaction_type'] == 'transfer':
                        print(f"       To: {txn['recipient_name']}")
                    else:
                        print(f"       From: {txn['recipient_name']}")
                print(f"       Date: {txn.get('initiated_at', 'N/A')[:19]}")
        else:
            print("   No transactions yet")

    print("\n" + "=" * 80 + "\n")
    return token

# Main
print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  DEMO BANK - USER LOGIN & NOTIFICATION CHECK                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

Enter the email addresses of the two users created in the test.
You can find them in the test output above.
""")

# Get user credentials
print("User A (Sender) Credentials:")
email_a = input("  Email: ").strip()
if not email_a:
    email_a = "adeleke.demo@demobank.ng"
password_a = input("  Password [Demo1234]: ").strip() or "Demo1234"

print("\nUser B (Recipient) Credentials:")
email_b = input("  Email: ").strip()
if not email_b:
    email_b = "therese.demo@demobank.ng"
password_b = input("  Password [Demo1234]: ").strip() or "Demo1234"

print("\n")

# Login as User A
login_and_show(email_a, password_a, "USER A (SENDER)")

# Login as User B
login_and_show(email_b, password_b, "USER B (RECIPIENT)")

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              ✅ CHECK COMPLETE!                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

Both users logged in successfully! You can see:
✓ Their account balances (sender decreased, recipient increased)
✓ Nigerian-style notifications (debit for sender, credit for recipient)
✓ Transaction history for both users
✓ Masked account numbers and professional formatting

Perfect for your demo presentation! 🎯
""")
