"""
Setup Funbi user in Demo Bank with 3 recipients
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import SessionLocal
from app.models.recipient import Recipient
from sqlalchemy import text

db = SessionLocal()

print("=" * 70)
print("SETTING UP FUNBI USER IN DEMO BANK")
print("=" * 70)

# Funbi's account details
funbi_account = "8523711419"  # New account number for Funbi
funbi_name = "Funbi Adeyemi"

print(f"\nUser: {funbi_name}")
print(f"Account Number: {funbi_account}")

# Define 3 recipients for Funbi
recipients_data = [
    {
        "name": "Tunde Bakare",
        "account_number": "2234567891",
        "bank_name": "First Bank",
        "bank_code": "011",
        "nickname": "Tunde"
    },
    {
        "name": "Chioma Okafor",
        "account_number": "3345678912",
        "bank_name": "Zenith Bank",
        "bank_code": "057",
        "nickname": "Chi"
    },
    {
        "name": "Bola Tinubu Jr",
        "account_number": "4456789123",
        "bank_name": "UBA",
        "bank_code": "033",
        "nickname": "Bola"
    }
]

print(f"\n{len(recipients_data)} recipients to add:")
for r in recipients_data:
    print(f"  - {r['name']} ({r['nickname']}) - {r['bank_name']} - {r['account_number']}")

# Check if recipients already exist
print("\n" + "-" * 70)
print("Checking existing recipients for Funbi...")

existing = db.query(Recipient).filter(
    Recipient.account_number == funbi_account
).all()

if existing:
    print(f"Found {len(existing)} existing recipients. Deleting them first...")
    for r in existing:
        db.delete(r)
    db.commit()
    print("Deleted existing recipients.")

# Add new recipients
print("\nAdding new recipients...")
try:
    for r_data in recipients_data:
        recipient = Recipient(
            account_number=funbi_account,  # Owner's account
            recipient_name=r_data["name"],
            recipient_account_number=r_data["account_number"],
            bank_name=r_data["bank_name"],
            bank_code=r_data["bank_code"],
            nickname=r_data["nickname"],
            is_active=True,
            is_favorite=False
        )
        db.add(recipient)

    db.commit()
    print(f"✓ Successfully added {len(recipients_data)} recipients for Funbi!")

except Exception as e:
    db.rollback()
    print(f"✗ Error adding recipients: {e}")

# Verify
print("\n" + "-" * 70)
print("Verifying recipients...")
recipients = db.query(Recipient).filter(
    Recipient.account_number == funbi_account
).all()

if recipients:
    print(f"✓ Found {len(recipients)} recipients for Funbi:")
    for r in recipients:
        print(f"  - {r.recipient_name} ({r.nickname}) - {r.bank_name}")
else:
    print("✗ No recipients found!")

print("\n" + "=" * 70)
print("SETUP COMPLETE!")
print("=" * 70)
print(f"\nFunbi's Account: {funbi_account}")
print(f"Recipients: {len(recipients)}")
print("\nYou can now use voice commands like:")
print("  - 'Check my balance'")
print("  - 'Show my recipients'")
print("  - 'Send 5000 to Tunde'")
print("  - 'Transfer to Chi'")
print("=" * 70)

db.close()
