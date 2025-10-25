#!/usr/bin/env python3
"""
Login as both demo users and show everything
"""
import requests

BASE_URL = "http://localhost:8002"
API_PREFIX = "/api"

def show_user(email, password, name):
    print("\n" + "╔" + "═" * 78 + "╗")
    print(f"║ {name:^76} ║")
    print("╚" + "═" * 78 + "╝\n")

    # Login
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/auth/login",
        json={"email": email, "password": password}
    )

    if response.status_code != 200:
        print(f"❌ Login failed!")
        print(f"   Try these credentials:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        return

    print(f"✅ LOGIN SUCCESSFUL!")
    print(f"   Email: {email}\n")

    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}

    # Account
    response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts", headers=headers)
    account = response.json()[0]
    print(f"💳 ACCOUNT DETAILS:")
    print(f"   Account Number: {account['account_number']}")
    print(f"   Account Name: {account['account_name']}")
    print(f"   Balance: NGN {float(account['balance']):,.2f}")

    # Notifications
    print(f"\n📧 NOTIFICATIONS:")
    response = requests.get(f"{BASE_URL}{API_PREFIX}/notifications?limit=5", headers=headers)
    notifs_data = response.json()
    print(f"   Total: {notifs_data['total']} | Unread: {notifs_data['unread_count']}")

    if notifs_data['notifications']:
        print(f"\n   Latest Notification:")
        latest = notifs_data['notifications'][0]
        print(f"   " + "-" * 76)
        print(f"   📬 {latest['title']}")
        print(f"   " + "-" * 76)
        for line in latest['message'].split('\n'):
            if line.strip():
                print(f"   {line}")
        print(f"   " + "-" * 76)

    # Transactions
    print(f"\n💸 RECENT TRANSACTIONS:")
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/accounts/{account['id']}/transactions?limit=3",
        headers=headers
    )
    txns = response.json().get('transactions', [])

    if txns:
        for i, txn in enumerate(txns[:2], 1):
            print(f"\n   [{i}] {txn['transaction_type'].upper()}")
            print(f"       Amount: NGN {float(txn['amount']):,.2f}")
            print(f"       Status: {txn['status']}")
            print(f"       Ref: {txn['transaction_ref']}")
            if txn.get('recipient_name'):
                direction = "To" if txn['transaction_type'] == 'transfer' else "From"
                print(f"       {direction}: {txn['recipient_name']}")
    else:
        print("   No transactions yet")

    print("\n" + "=" * 80)

# Main
print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              DEMO BANK - CHECK BOTH USERS' ACCOUNTS                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

# Show both users
show_user("adeleke@demobank.ng", "Password123", "USER 1: ADELEKE (SENDER)")
show_user("therese@demobank.ng", "Password123", "USER 2: THERESE (RECIPIENT)")

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              ✅ CHECK COMPLETE!                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 CREDENTIALS FOR YOUR DEMO:

   User 1 (Sender):
   Email: adeleke@demobank.ng
   Password: Password123
   PIN: 1111

   User 2 (Recipient):
   Email: therese@demobank.ng
   Password: Password123
   PIN: 2222

You can use these to login and show the judges real Nigerian bank notifications! 🇳🇬
""")
