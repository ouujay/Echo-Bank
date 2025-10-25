"""
Company Model - Banks/Financial institutions that use EchoBank API
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from datetime import datetime
from app.models.base import Base


class Company(Base):
    """
    Company/Bank that registers to use EchoBank voice API
    """
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)

    # Company Info
    company_name = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    contact_person = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)

    # API Credentials
    api_key = Column(String(255), unique=True, index=True)  # Generated for them
    api_secret = Column(String(255))  # Hashed

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Company {self.company_name}>"


class CompanyEndpoints(Base):
    """
    API Endpoints that the company provides for EchoBank to call
    """
    __tablename__ = "company_endpoints"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, nullable=False, index=True)

    # Base URL
    base_url = Column(String(500), nullable=False)  # e.g., https://api.zenithbank.com

    # Authentication
    auth_type = Column(String(50), default="bearer")  # bearer, api_key, basic
    auth_header_name = Column(String(100), default="Authorization")

    # Endpoints - Required
    get_balance_endpoint = Column(String(500))  # e.g., /api/v1/accounts/{account_number}/balance
    get_recipients_endpoint = Column(String(500))  # e.g., /api/v1/accounts/{account_number}/beneficiaries
    initiate_transfer_endpoint = Column(String(500))  # e.g., /api/v1/transfers/initiate
    confirm_transfer_endpoint = Column(String(500))  # e.g., /api/v1/transfers/{transfer_id}/confirm
    verify_pin_endpoint = Column(String(500))  # e.g., /api/v1/auth/verify-pin

    # Optional Endpoints
    get_transactions_endpoint = Column(String(500), nullable=True)
    add_recipient_endpoint = Column(String(500), nullable=True)
    cancel_transfer_endpoint = Column(String(500), nullable=True)

    # Request/Response Configuration
    request_headers = Column(JSON, nullable=True)  # Custom headers they need
    response_mapping = Column(JSON, nullable=True)  # How to map their response to our format

    # Status
    is_active = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CompanyEndpoints company_id={self.company_id}>"
