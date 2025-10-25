"""
Load demo data into the database
"""
import sys
import os

# Change to backend directory
os.chdir('backend')
sys.path.insert(0, os.getcwd())

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import BankUser
from app.models.account import BankAccount
from app.core.security import hash_password, hash_pin
from datetime import datetime
import random

def generate_account_number():
    """Generate a random 10-digit account number"""
    return ''.join([str(random.randint(0, 9)) for _ in range(10)])

def load_demo_data():
    """Load demo users and accounts"""
    db = SessionLocal()

    try:
        # Demo users data
        demo_users = [
            {
                "email": "john.doe@demobank.com",
                "phone": "+2348012345678",
                "full_name": "John Doe",
                "password": "password123",
                "pin": "1234",
                "balance": 150000.00
            },
            {
                "email": "jane.smith@demobank.com",
                "phone": "+2348087654321",
                "full_name": "Jane Smith",
                "password": "password123",
                "pin": "5678",
                "balance": 250000.00
            },
            {
                "email": "demo@test.com",
                "phone": "+2348098765432",
                "full_name": "Demo User",
                "password": "demo123",
                "pin": "0000",
                "balance": 100000.00
            }
        ]

        print("\n" + "="*60)
        print("LOADING DEMO DATA INTO DATABASE")
        print("="*60 + "\n")

        for user_data in demo_users:
            # Check if user already exists
            existing_user = db.query(BankUser).filter(BankUser.email == user_data["email"]).first()
            if existing_user:
                print(f"[SKIP] User {user_data['email']} already exists. Skipping...")
                continue

            # Create user
            user = BankUser(
                email=user_data["email"],
                phone=user_data["phone"],
                full_name=user_data["full_name"],
                password_hash=hash_password(user_data["password"]),
                pin_hash=hash_pin(user_data["pin"]),
                is_active=True,
                is_verified=True,
                pin_attempts=0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(user)
            db.flush()  # Get the user ID

            # Create bank account for user
            account_number = generate_account_number()
            account = BankAccount(
                user_id=user.id,
                account_number=account_number,
                account_name=user_data["full_name"],
                account_type="savings",
                balance=user_data["balance"],
                currency="NGN",
                daily_transfer_limit=500000.00,
                monthly_transfer_limit=5000000.00,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(account)

            print(f"[OK] Created user: {user_data['full_name']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Password: {user_data['password']}")
            print(f"   PIN: {user_data['pin']}")
            print(f"   Account Number: {account_number}")
            print(f"   Balance: N{user_data['balance']:,.2f}")
            print()

        db.commit()

        print("="*60)
        print("DEMO DATA LOADED SUCCESSFULLY!")
        print("="*60)
        print("\n[LOGIN] LOGIN CREDENTIALS:\n")
        print("USER 1:")
        print("  Email: john.doe@demobank.com")
        print("  Password: password123")
        print("  PIN: 1234")
        print("  Balance: N150,000.00\n")

        print("USER 2:")
        print("  Email: jane.smith@demobank.com")
        print("  Password: password123")
        print("  PIN: 5678")
        print("  Balance: N250,000.00\n")

        print("USER 3:")
        print("  Email: demo@test.com")
        print("  Password: demo123")
        print("  PIN: 0000")
        print("  Balance: N100,000.00\n")

        print("="*60)
        print("[WEB] Access the application at:")
        print("   Frontend: http://localhost:5173")
        print("   Backend API: http://localhost:8002")
        print("   API Docs: http://localhost:8002/docs")
        print("="*60 + "\n")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Error loading demo data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    load_demo_data()
