#!/usr/bin/env python3
"""
Create your personal account and make a transfer
"""
import requests
import time

BASE_URL = "http://localhost:8002"
API_PREFIX = "/api"

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              CREATING YOUR PERSONAL DEMO BANK ACCOUNT                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

# Create your account
print("1️⃣  Creating your account...")
your_data = {
    "full_name": "Aladenusi Adeleke Paul",
    "email": "aladenusiadeleke@gmail.com",
    "phone": "+2348123456789",
    "password": "MyPassword123",
    "pin": "1234"
}

response = requests.post(f"{BASE_URL}{API_PREFIX}/auth/register", json=your_data)

if response.status_code == 200:
    print(f"   ✅ Account created successfully!")
    data = response.json()
    token = data['access_token']
else:
    # Try login
    print(f"   ℹ️  Account exists, logging in...")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/auth/login",
        json={"email": your_data['email'], "password": your_data['password']}
    )
    if response.status_code != 200:
        print(f"   ❌ Login failed. Try resetting or use different credentials.")
        exit(1)
    data = response.json()
    token = data['access_token']
    print(f"   ✅ Logged in successfully!")

headers = {"Authorization": f"Bearer {token}"}

# Get your account details
response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts", headers=headers)
your_account = response.json()[0]

print(f"\n💳 YOUR ACCOUNT DETAILS:")
print(f"   Account Number: {your_account['account_number']}")
print(f"   Account Name: {your_account['account_name']}")
print(f"   Balance: NGN {float(your_account['balance']):,.2f}")

# Check your welcome notification
print(f"\n📧 YOUR WELCOME NOTIFICATION:")
print("=" * 80)
response = requests.get(f"{BASE_URL}{API_PREFIX}/notifications", headers=headers)
notifs = response.json()['notifications']
if notifs:
    welcome = notifs[0]
    print(welcome['message'])
print("=" * 80)

print(f"\n\n🎯 YOUR LOGIN CREDENTIALS:")
print(f"   Email:    {your_data['email']}")
print(f"   Password: {your_data['password']}")
print(f"   PIN:      {your_data['pin']}")
print(f"   Account:  {your_account['account_number']}")

print(f"\n\n🔹 NEXT STEP: Make a transfer to Therese")
print(f"   Run: python make_my_transfer.py")
print(f"\n   This will:")
print(f"   • Transfer NGN 3,000 from your account to Therese")
print(f"   • You'll get a DEBIT notification")
print(f"   • Therese will get a CREDIT notification")
print(f"   • You can view your notifications via API or app")
