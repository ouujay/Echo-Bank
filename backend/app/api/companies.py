"""
Company Registration and Management API

This is where banks/financial institutions sign up to use EchoBank
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, Dict
from sqlalchemy.orm import Session
import secrets
import hashlib
from app.core.database import get_db
from app.models.company import Company, CompanyEndpoints

router = APIRouter(prefix="/api/v1/companies", tags=["Company Management"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class CompanyRegistrationRequest(BaseModel):
    """Request to register a new company"""
    company_name: str
    email: EmailStr
    contact_person: str
    phone: str
    password: str  # They choose a password for API access


class EndpointConfigurationRequest(BaseModel):
    """Configuration of company's API endpoints"""
    base_url: str
    auth_type: str = "bearer"  # bearer, api_key, basic
    auth_header_name: str = "Authorization"

    # Required endpoints
    get_balance_endpoint: str
    get_recipients_endpoint: str
    initiate_transfer_endpoint: str
    confirm_transfer_endpoint: str
    verify_pin_endpoint: str

    # Optional endpoints
    get_transactions_endpoint: Optional[str] = None
    add_recipient_endpoint: Optional[str] = None
    cancel_transfer_endpoint: Optional[str] = None

    # Custom configuration
    request_headers: Optional[Dict] = None
    response_mapping: Optional[Dict] = None


class CompanyResponse(BaseModel):
    """Response after company registration"""
    success: bool
    company_id: int
    company_name: str
    api_key: str  # Give them this ONCE
    message: str


class CompanyLoginRequest(BaseModel):
    """Request to login as a company"""
    email: EmailStr
    password: str


class CompanyLoginResponse(BaseModel):
    """Response after successful login"""
    success: bool
    company_id: int
    company_name: str
    email: str
    is_active: bool
    is_verified: bool
    message: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/register", response_model=CompanyResponse)
async def register_company(
    request: CompanyRegistrationRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new company (bank) to use EchoBank API

    Flow:
    1. Company fills registration form
    2. We generate API key for them
    3. They configure their endpoints
    4. We verify endpoints work
    5. They integrate our voice API into their app
    """

    # Check if company already exists
    existing = db.query(Company).filter(
        (Company.email == request.email) | (Company.company_name == request.company_name)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "Company with this name or email already exists"
            }
        )

    # Generate API credentials
    api_key = f"echobank_{secrets.token_urlsafe(32)}"
    api_secret_hash = hashlib.sha256(request.password.encode()).hexdigest()

    # Create company
    new_company = Company(
        company_name=request.company_name,
        email=request.email,
        contact_person=request.contact_person,
        phone=request.phone,
        api_key=api_key,
        api_secret=api_secret_hash,
        is_active=False,  # Inactive until endpoints are configured
        is_verified=False
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return {
        "success": True,
        "company_id": new_company.id,
        "company_name": new_company.company_name,
        "api_key": api_key,
        "message": "Company registered successfully! Save your API key - you won't see it again. Next step: Configure your endpoints."
    }


@router.post("/login", response_model=CompanyLoginResponse)
async def login_company(
    request: CompanyLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login for registered companies

    Returns company information if credentials are valid.
    Use this to access the dashboard and configure endpoints.
    """

    # Find company by email
    company = db.query(Company).filter(Company.email == request.email).first()

    if not company:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": "Invalid email or password"
            }
        )

    # Verify password
    password_hash = hashlib.sha256(request.password.encode()).hexdigest()

    if company.api_secret != password_hash:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": "Invalid email or password"
            }
        )

    return {
        "success": True,
        "company_id": company.id,
        "company_name": company.company_name,
        "email": company.email,
        "is_active": company.is_active,
        "is_verified": company.is_verified,
        "message": "Login successful"
    }


@router.post("/{company_id}/endpoints")
async def configure_endpoints(
    company_id: int,
    request: EndpointConfigurationRequest,
    db: Session = Depends(get_db)
):
    """
    Configure API endpoints for a company

    The company tells us:
    - Their base URL
    - Endpoints for each operation (balance, transfers, etc.)
    - How to authenticate with their API
    - How to map their responses to our format
    """

    # Verify company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Check if endpoints already configured
    existing_endpoints = db.query(CompanyEndpoints).filter(
        CompanyEndpoints.company_id == company_id
    ).first()

    if existing_endpoints:
        # Update existing
        existing_endpoints.base_url = request.base_url
        existing_endpoints.auth_type = request.auth_type
        existing_endpoints.auth_header_name = request.auth_header_name
        existing_endpoints.get_balance_endpoint = request.get_balance_endpoint
        existing_endpoints.get_recipients_endpoint = request.get_recipients_endpoint
        existing_endpoints.initiate_transfer_endpoint = request.initiate_transfer_endpoint
        existing_endpoints.confirm_transfer_endpoint = request.confirm_transfer_endpoint
        existing_endpoints.verify_pin_endpoint = request.verify_pin_endpoint
        existing_endpoints.get_transactions_endpoint = request.get_transactions_endpoint
        existing_endpoints.add_recipient_endpoint = request.add_recipient_endpoint
        existing_endpoints.cancel_transfer_endpoint = request.cancel_transfer_endpoint
        existing_endpoints.request_headers = request.request_headers
        existing_endpoints.response_mapping = request.response_mapping

        db.commit()
        message = "Endpoints updated successfully"
    else:
        # Create new
        new_endpoints = CompanyEndpoints(
            company_id=company_id,
            base_url=request.base_url,
            auth_type=request.auth_type,
            auth_header_name=request.auth_header_name,
            get_balance_endpoint=request.get_balance_endpoint,
            get_recipients_endpoint=request.get_recipients_endpoint,
            initiate_transfer_endpoint=request.initiate_transfer_endpoint,
            confirm_transfer_endpoint=request.confirm_transfer_endpoint,
            verify_pin_endpoint=request.verify_pin_endpoint,
            get_transactions_endpoint=request.get_transactions_endpoint,
            add_recipient_endpoint=request.add_recipient_endpoint,
            cancel_transfer_endpoint=request.cancel_transfer_endpoint,
            request_headers=request.request_headers,
            response_mapping=request.response_mapping
        )

        db.add(new_endpoints)
        db.commit()
        message = "Endpoints configured successfully"

    # Activate company now that endpoints are configured
    company.is_active = True
    db.commit()

    return {
        "success": True,
        "company_id": company_id,
        "message": message,
        "next_step": "Test your integration by calling /api/v1/voice/process-audio with your API key"
    }


@router.get("/{company_id}/endpoints")
async def get_company_endpoints(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Get configured endpoints for a company"""

    endpoints = db.query(CompanyEndpoints).filter(
        CompanyEndpoints.company_id == company_id
    ).first()

    if not endpoints:
        raise HTTPException(
            status_code=404,
            detail="No endpoints configured for this company"
        )

    return {
        "success": True,
        "data": {
            "base_url": endpoints.base_url,
            "auth_type": endpoints.auth_type,
            "auth_header_name": endpoints.auth_header_name,
            "endpoints": {
                "get_balance": endpoints.get_balance_endpoint,
                "get_recipients": endpoints.get_recipients_endpoint,
                "initiate_transfer": endpoints.initiate_transfer_endpoint,
                "confirm_transfer": endpoints.confirm_transfer_endpoint,
                "verify_pin": endpoints.verify_pin_endpoint,
                "get_transactions": endpoints.get_transactions_endpoint,
                "add_recipient": endpoints.add_recipient_endpoint,
                "cancel_transfer": endpoints.cancel_transfer_endpoint
            }
        }
    }


@router.get("/{company_id}")
async def get_company_info(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Get company information"""

    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return {
        "success": True,
        "data": {
            "company_id": company.id,
            "company_name": company.company_name,
            "email": company.email,
            "contact_person": company.contact_person,
            "phone": company.phone,
            "is_active": company.is_active,
            "is_verified": company.is_verified,
            "created_at": company.created_at.isoformat()
        }
    }
# trigger reload
