"""
Database initialization and seed script
Run this to create the database and add test data
"""
from app.core.database import init_db, SessionLocal
from app.models import User, Recipient
from passlib.context import CryptContext
from decimal import Decimal

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_test_data():
    """Add test users and recipients for development"""
    db = SessionLocal()

    try:
        # Check if we already have test data
        existing_user = db.query(User).filter(User.account_number == "0123456789").first()
        if existing_user:
            print("Test data already exists!")
            return

        # Create test user
        test_user = User(
            account_number="0123456789",
            full_name="Test User",
            email="test@echobank.com",
            phone="+2348012345678",
            pin_hash=pwd_context.hash("1234"),  # Test PIN: 1234
            balance=Decimal("100000.00"),  # ₦100,000 balance
            daily_limit=Decimal("50000.00"),
            is_active=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        # Create test recipients
        recipients = [
            Recipient(
                user_id=test_user.id,
                name="John Okafor",
                account_number="0111111111",
                bank_name="Zenith Bank",
                bank_code="057",
                is_favorite=True
            ),
            Recipient(
                user_id=test_user.id,
                name="John Adeyemi",
                account_number="0222222222",
                bank_name="GTBank",
                bank_code="058",
                is_favorite=False
            ),
            Recipient(
                user_id=test_user.id,
                name="Mary Johnson",
                account_number="0333333333",
                bank_name="Access Bank",
                bank_code="044",
                is_favorite=True
            ),
            Recipient(
                user_id=test_user.id,
                name="David Nwosu",
                account_number="0444444444",
                bank_name="First Bank",
                bank_code="011",
                is_favorite=False
            )
        ]

        for recipient in recipients:
            db.add(recipient)

        db.commit()

        print("Test data created successfully!")
        print(f"   Test User: {test_user.account_number}")
        print(f"   Test PIN: 1234")
        print(f"   Balance: N{test_user.balance:,.2f}")
        print(f"   Recipients: {len(recipients)} added")

    except Exception as e:
        print(f"Error seeding test data: {e}")
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("\nSeeding test data...")
    seed_test_data()
    print("\nDatabase setup complete!")
