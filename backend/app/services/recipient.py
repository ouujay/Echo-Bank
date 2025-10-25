"""
Recipient Service
"""
from sqlalchemy.orm import Session
from app.models.recipient import BankRecipient
from app.schemas.transfer import RecipientCreate, RecipientResponse
from app.services.paystack import paystack_service
from typing import List
import logging

logger = logging.getLogger(__name__)


def get_user_recipients(db: Session, user_id: int) -> List[RecipientResponse]:
    """Get all recipients for a user"""
    recipients = db.query(BankRecipient).filter(BankRecipient.user_id == user_id).all()
    return [RecipientResponse.from_orm(recipient) for recipient in recipients]


def create_recipient(db: Session, user_id: int, recipient_data: RecipientCreate) -> RecipientResponse:
    """
    Create a new recipient and register on Paystack
    This makes transfers appear in Paystack dashboard
    """
    # Check if recipient already exists
    existing = db.query(BankRecipient).filter(
        BankRecipient.user_id == user_id,
        BankRecipient.account_number == recipient_data.account_number,
        BankRecipient.bank_code == recipient_data.bank_code
    ).first()

    if existing:
        raise ValueError("Recipient already exists")

    # Step 1: Verify account with Paystack (Name Enquiry)
    logger.info(f"Verifying account {recipient_data.account_number} with Paystack")
    verification = paystack_service.verify_account(
        account_number=recipient_data.account_number,
        bank_code=recipient_data.bank_code
    )

    if not verification["success"]:
        # For demo banks or non-Paystack banks, skip verification
        logger.warning(f"Paystack verification failed: {verification.get('error')}. Proceeding anyway for demo.")
        verified_name = recipient_data.recipient_name
        is_verified = False
    else:
        verified_name = verification["account_name"]
        is_verified = True
        logger.info(f"Account verified: {verified_name}")

    # Step 2: Create Paystack transfer recipient
    logger.info(f"Creating Paystack recipient for {verified_name}")
    paystack_recipient = paystack_service.create_transfer_recipient(
        recipient_name=verified_name,
        account_number=recipient_data.account_number,
        bank_code=recipient_data.bank_code,
        currency="NGN"
    )

    paystack_recipient_code = None
    if paystack_recipient["success"]:
        paystack_recipient_code = paystack_recipient["recipient_code"]
        logger.info(f"Paystack recipient created: {paystack_recipient_code}")
    else:
        logger.warning(f"Failed to create Paystack recipient: {paystack_recipient.get('error')}")

    # Step 3: Save recipient to database
    new_recipient = BankRecipient(
        user_id=user_id,
        recipient_name=verified_name if is_verified else recipient_data.recipient_name,
        account_number=recipient_data.account_number,
        bank_name=recipient_data.bank_name,
        bank_code=recipient_data.bank_code,
        paystack_recipient_code=paystack_recipient_code,
        is_favorite=recipient_data.is_favorite,
        is_verified=is_verified
    )

    db.add(new_recipient)
    db.commit()
    db.refresh(new_recipient)

    logger.info(f"Recipient saved: {new_recipient.id} - {new_recipient.recipient_name}")

    return RecipientResponse.from_orm(new_recipient)


def get_recipient(db: Session, recipient_id: int, user_id: int) -> BankRecipient:
    """Get a specific recipient"""
    recipient = db.query(BankRecipient).filter(
        BankRecipient.id == recipient_id,
        BankRecipient.user_id == user_id
    ).first()

    if not recipient:
        raise ValueError("Recipient not found")

    return recipient


def toggle_favorite(db: Session, recipient_id: int, user_id: int) -> RecipientResponse:
    """Toggle favorite status for a recipient"""
    recipient = get_recipient(db, recipient_id, user_id)
    recipient.is_favorite = not recipient.is_favorite
    db.commit()
    db.refresh(recipient)

    return RecipientResponse.from_orm(recipient)


def delete_recipient(db: Session, recipient_id: int, user_id: int):
    """Delete a recipient"""
    recipient = get_recipient(db, recipient_id, user_id)
    db.delete(recipient)
    db.commit()
    return {"message": "Recipient deleted successfully"}
