#!/usr/bin/env python3
"""
Create account for Funbi
"""
import requests

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api"

print("Creating account for Funbi...")

# Funbi's account
funbi_user = {
    "full_name": "Funbi",
    "email": "funbi@demobank.ng",
    "phone": "+2348100000999",
    "password": "Funbi123",
    "pin": "0000"
}

try:
    response = requests.post(f"{BASE_URL}{API_PREFIX}/auth/register", json=funbi_user)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Account created successfully!")
        print(f"\n📱 LOGIN CREDENTIALS FOR FUNBI:")
        print(f"   Email:    {funbi_user['email']}")
        print(f"   Password: {funbi_user['password']}")
        print(f"   PIN:      {funbi_user['pin']}")

        # Get account details
        token = data['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        acc_response = requests.get(f"{BASE_URL}{API_PREFIX}/accounts", headers=headers)
        if acc_response.status_code == 200:
            account = acc_response.json()[0]
            print(f"\n💳 ACCOUNT DETAILS:")
            print(f"   Account Number: {account['account_number']}")
            print(f"   Balance: NGN {float(account['balance']):,.2f}")

        print(f"\n🚀 You can now login at: http://localhost:3001")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\nMake sure the backend is running on http://localhost:8000")
