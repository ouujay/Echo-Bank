#!/usr/bin/env python3
"""
Create 2 permanent demo users for testing
"""
import requests

BASE_URL = "http://localhost:8002"
API_PREFIX = "/api"

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     CREATING PERMANENT DEMO USERS                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

# User 1: Adeleke (Sender)
print("\n1️⃣  Creating User 1 (Sender)...")
user1 = {
    "full_name": "Adeleke Paul Aladenusi",
    "email": "adeleke@demobank.ng",
    "phone": "+2348100000111",
    "password": "Password123",
    "pin": "1111"
}

response = requests.post(f"{BASE_URL}{API_PREFIX}/auth/register", json=user1)
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ Created: {user1['full_name']}")

    # Get account
    token = data['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    acc_response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts", headers=headers)
    account1 = acc_response.json()[0]
    print(f"   📱 Account: {account1['account_number']}")
    print(f"   💰 Balance: NGN {float(account1['balance']):,.2f}")
else:
    print(f"   ℹ️  User already exists (this is fine)")

# User 2: Therese (Recipient)
print("\n2️⃣  Creating User 2 (Recipient)...")
user2 = {
    "full_name": "Mbama Therese Chimbusonma",
    "email": "therese@demobank.ng",
    "phone": "+2348200000222",
    "password": "Password123",
    "pin": "2222"
}

response = requests.post(f"{BASE_URL}{API_PREFIX}/auth/register", json=user2)
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ Created: {user2['full_name']}")

    # Get account
    token = data['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    acc_response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts", headers=headers)
    account2 = acc_response.json()[0]
    print(f"   📱 Account: {account2['account_number']}")
    print(f"   💰 Balance: NGN {float(account2['balance']):,.2f}")
else:
    print(f"   ℹ️  User already exists (this is fine)")

print("""
\n╔══════════════════════════════════════════════════════════════════════════════╗
║                         ✅ DEMO USERS READY!                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

📱 USER 1 (SENDER):
   Email:    adeleke@demobank.ng
   Password: Password123
   PIN:      1111

📱 USER 2 (RECIPIENT):
   Email:    therese@demobank.ng
   Password: Password123
   PIN:      2222

🎬 YOU CAN NOW:
   1. Run the internal transfer test between these users
   2. Login as each user to see notifications
   3. Use these for all your demos

Try logging in now with these credentials! 🚀
""")
