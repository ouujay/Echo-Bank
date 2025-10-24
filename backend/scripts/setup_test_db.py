"""
Setup script to create database tables and insert test data.
Run this before testing the API.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine, SessionLocal, Base
from app.models import User, Recipient, Transaction
from app.services.auth import auth_service
from decimal import Decimal


def create_tables():
    """Create all database tables."""
    print("🔧 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")


def create_test_data():
    """Create test users and recipients."""
    db = SessionLocal()

    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.account_number == "0123456789").first()
        if existing_user:
            print("⚠️  Test user already exists. Skipping...")
            return

        print("\n👤 Creating test user...")

        # Create test user with hashed PIN
        test_user = User(
            account_number="0123456789",
            full_name="Test User",
            email="test@echobank.com",
            phone="+2348012345678",
            pin_hash=auth_service.hash_pin("1234"),  # PIN is 1234
            balance=Decimal("100000.00"),  # ₦100,000 balance
            daily_limit=Decimal("50000.00"),
            is_active=True
        )

        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        print(f"✅ Test user created!")
        print(f"   Account: {test_user.account_number}")
        print(f"   Name: {test_user.full_name}")
        print(f"   Balance: ₦{test_user.balance:,.2f}")
        print(f"   PIN: 1234")

        # Create test recipients
        print("\n📋 Creating test recipients...")

        recipients_data = [
            {
                "name": "John Okafor",
                "account_number": "0111111111",
                "bank_name": "Zenith Bank",
                "bank_code": "057"
            },
            {
                "name": "John Adeyemi",
                "account_number": "0222222222",
                "bank_name": "GTBank",
                "bank_code": "058"
            },
            {
                "name": "Mary Johnson",
                "account_number": "0333333333",
                "bank_name": "Access Bank",
                "bank_code": "044"
            },
            {
                "name": "David Brown",
                "account_number": "0444444444",
                "bank_name": "First Bank",
                "bank_code": "011"
            }
        ]

        for recipient_data in recipients_data:
            recipient = Recipient(
                user_id=test_user.id,
                **recipient_data
            )
            db.add(recipient)

        db.commit()

        print(f"✅ Created {len(recipients_data)} test recipients:")
        for r in recipients_data:
            print(f"   - {r['name']} ({r['bank_name']})")

        print("\n" + "="*60)
        print("🎉 Database setup complete!")
        print("="*60)
        print("\n📝 Test Credentials:")
        print(f"   User ID: {test_user.id}")
        print(f"   Account Number: {test_user.account_number}")
        print(f"   PIN: 1234")
        print(f"   Balance: ₦{test_user.balance:,.2f}")
        print(f"   Daily Limit: ₦{test_user.daily_limit:,.2f}")
        print("\n🚀 You can now start testing the API!")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("🏦 EchoBank - Database Setup Script")
    print("="*60)

    # Create tables
    create_tables()

    # Create test data
    create_test_data()
