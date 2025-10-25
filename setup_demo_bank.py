"""
Setup Demo Bank in Database

This script creates/updates the Demo Bank company with proper API endpoints
so that the voice pipeline works correctly.
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import SessionLocal
from app.models.company import Company, CompanyEndpoints

def setup_demo_bank():
    """Setup Demo Bank with proper endpoints"""
    db = SessionLocal()

    try:
        # Check if Demo Bank already exists
        demo_bank = db.query(Company).filter(Company.company_name == "Demo Bank").first()

        if not demo_bank:
            # Create Demo Bank company
            demo_bank = Company(
                company_name="Demo Bank",
                email="demo@demobank.com",
                contact_person="Demo Admin",
                phone="+2341234567890",
                api_key="demo_api_key_12345",  # For authentication
                is_active=True,
                is_verified=True
            )
            db.add(demo_bank)
            db.commit()
            db.refresh(demo_bank)
            print(f"[OK] Created Demo Bank company (ID: {demo_bank.id})")
        else:
            print(f"[OK] Demo Bank already exists (ID: {demo_bank.id})")

        # Check if endpoints are configured
        endpoints = db.query(CompanyEndpoints).filter(
            CompanyEndpoints.company_id == demo_bank.id
        ).first()

        if not endpoints:
            # Create endpoints configuration
            endpoints = CompanyEndpoints(
                company_id=demo_bank.id,
                base_url="http://127.0.0.1:8100",  # Mock bank server
                get_balance_endpoint="/api/v1/accounts/{account_number}/balance",
                get_recipients_endpoint="/api/v1/accounts/{account_number}/beneficiaries",
                initiate_transfer_endpoint="/api/v1/transfers/initiate",
                confirm_transfer_endpoint="/api/v1/transfers/{transfer_id}/confirm",
                cancel_transfer_endpoint="/api/v1/transfers/{transfer_id}/cancel",
                auth_type="bearer",
                auth_header_name="Authorization",
                is_active=True
            )
            db.add(endpoints)
            db.commit()
            print(f"[OK] Created endpoints configuration for Demo Bank")
        else:
            # Update endpoints to make sure they're correct
            endpoints.base_url = "http://127.0.0.1:8100"
            endpoints.get_balance_endpoint = "/api/v1/accounts/{account_number}/balance"
            endpoints.get_recipients_endpoint = "/api/v1/accounts/{account_number}/beneficiaries"
            endpoints.initiate_transfer_endpoint = "/api/v1/transfers/initiate"
            endpoints.confirm_transfer_endpoint = "/api/v1/transfers/{transfer_id}/confirm"
            endpoints.cancel_transfer_endpoint = "/api/v1/transfers/{transfer_id}/cancel"
            endpoints.auth_type = "bearer"
            endpoints.auth_header_name = "Authorization"
            endpoints.is_active = True
            db.commit()
            print(f"[OK] Updated endpoints configuration for Demo Bank")

        print("\n" + "="*60)
        print("Demo Bank Configuration:")
        print("="*60)
        print(f"Company ID: {demo_bank.id}")
        print(f"Company Name: {demo_bank.company_name}")
        print(f"Base URL: {endpoints.base_url}")
        print(f"Balance Endpoint: {endpoints.get_balance_endpoint}")
        print(f"Recipients Endpoint: {endpoints.get_recipients_endpoint}")
        print(f"Transfer Endpoint: {endpoints.initiate_transfer_endpoint}")
        print(f"Confirm Endpoint: {endpoints.confirm_transfer_endpoint}")
        print(f"Auth Type: {endpoints.auth_type}")
        print("="*60)
        print("\nDemo Bank is now ready to use!")
        print(f"\nUse company_id={demo_bank.id} when calling the voice API")
        print("\nMake sure the mock bank server is running:")
        print("  python mock_bank_server.py")

        return demo_bank.id

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Setting up Demo Bank...\n")
    company_id = setup_demo_bank()
    print(f"\n[OK] Setup complete! Demo Bank company_id = {company_id}")
