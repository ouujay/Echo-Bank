"""
Check John Doe's recipients in Demo Bank
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import SessionLocal
from app.models.recipient import Recipient
from sqlalchemy import text

db = SessionLocal()

# John Doe's account number
account_number = "6523711418"

print("=" * 60)
print(f"CHECKING RECIPIENTS FOR JOHN DOE ({account_number})")
print("=" * 60)

# Get recipients
recipients = db.query(Recipient).filter(
    Recipient.account_number == account_number
).all()

if recipients:
    print(f"\nFound {len(recipients)} recipients:")
    for r in recipients:
        print(f"  - {r.recipient_name} ({r.recipient_account_number})")
        print(f"    Bank: {r.bank_name}, Nickname: {r.nickname}")
        print(f"    Active: {r.is_active}")
        print()
else:
    print("\nNO RECIPIENTS FOUND!")
    print("This means Demo Bank API needs to return recipients,")
    print("or they need to be seeded in the database.")

print("=" * 60)

# Check if Demo Bank company exists
result = db.execute(text("SELECT id, company_name FROM companies WHERE company_name = 'Demo Bank'"))
company = result.fetchone()

if company:
    print(f"\nDemo Bank registered: ID = {company[0]}, Name = {company[1]}")
else:
    print("\nWARNING: Demo Bank NOT registered in companies table!")

db.close()
