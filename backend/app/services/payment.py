"""
Payment Service - For accepting money via Paystack
"""
from sqlalchemy.orm import Session
from app.models.account import BankAccount
from app.models.transaction import BankTransaction
from app.services.paystack import paystack_service
from app.services.account import update_account_balance
from app.schemas.payment import PaymentInitiate, PaymentInitiateResponse, PaymentVerifyResponse
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def initiate_wallet_funding(db: Session, payment_data: PaymentInitiate) -> PaymentInitiateResponse:
    """
    Initiate wallet funding via Paystack
    Creates a Paystack payment session and returns authorization URL
    """
    # Get account
    account = db.query(BankAccount).filter(
        BankAccount.account_number == payment_data.account_number
    ).first()

    if not account:
        raise ValueError("Account not found")

    if not account.is_active:
        raise ValueError("Account is inactive")

    # Get user email
    user_email = account.user.email

    # Generate unique reference
    reference = f"FUND_{account.account_number}_{int(datetime.now().timestamp())}"

    # Initialize Paystack transaction
    logger.info(f"Initializing Paystack payment for ₦{payment_data.amount}")
    paystack_result = paystack_service.initialize_transaction(
        email=user_email,
        amount=payment_data.amount,
        reference=reference,
        callback_url=payment_data.callback_url,
        metadata={
            "account_number": account.account_number,
            "account_name": account.account_name,
            "purpose": "wallet_funding"
        }
    )

    if not paystack_result["success"]:
        raise ValueError(f"Payment initialization failed: {paystack_result.get('error')}")

    # Create pending transaction record
    new_transaction = BankTransaction(
        account_id=account.id,
        transaction_ref=reference,
        transaction_type="credit",
        amount=payment_data.amount,
        fee=Decimal("0.00"),
        currency="NGN",
        status="pending",
        narration="Wallet funding via Paystack",
        paystack_transfer_code=paystack_result["reference"],
        initiated_via="web",
        initiated_at=datetime.now()
    )

    db.add(new_transaction)
    db.commit()

    logger.info(f"Payment session created: {paystack_result['reference']}")

    return PaymentInitiateResponse(
        success=True,
        authorization_url=paystack_result["authorization_url"],
        access_code=paystack_result["access_code"],
        reference=paystack_result["reference"],
        amount=payment_data.amount,
        message=f"Payment session created. Complete payment to fund your wallet with ₦{payment_data.amount:,.2f}"
    )


def verify_wallet_funding(db: Session, reference: str) -> PaymentVerifyResponse:
    """
    Verify payment and credit account if successful
    """
    # Get transaction from database
    transaction = db.query(BankTransaction).filter(
        BankTransaction.paystack_transfer_code == reference
    ).first()

    if not transaction:
        raise ValueError("Transaction not found")

    # Verify with Paystack
    logger.info(f"Verifying payment: {reference}")
    verify_result = paystack_service.verify_transaction(reference)

    if not verify_result["success"]:
        raise ValueError(f"Payment verification failed: {verify_result.get('error')}")

    payment_status = verify_result["status"]
    logger.info(f"Paystack status: {payment_status}")

    if payment_status == "success":
        # Payment successful - credit the account
        if transaction.status == "pending":
            # Credit account
            update_account_balance(
                db=db,
                account_id=transaction.account_id,
                amount=transaction.amount,
                operation="credit"
            )

            # Update transaction
            transaction.status = "completed"
            transaction.completed_at = datetime.now()
            transaction.paystack_status = "success"

            db.commit()
            db.refresh(transaction)

            # Get new balance
            account = db.query(BankAccount).filter(BankAccount.id == transaction.account_id).first()

            logger.info(f"Wallet funded successfully. New balance: ₦{account.balance}")

            return PaymentVerifyResponse(
                success=True,
                status="success",
                amount=transaction.amount,
                reference=reference,
                message=f"Payment successful! Your wallet has been credited with ₦{transaction.amount:,.2f}",
                new_balance=account.balance
            )
        else:
            # Already processed
            account = db.query(BankAccount).filter(BankAccount.id == transaction.account_id).first()
            return PaymentVerifyResponse(
                success=True,
                status="success",
                amount=transaction.amount,
                reference=reference,
                message="Payment already processed",
                new_balance=account.balance
            )

    elif payment_status == "failed":
        transaction.status = "failed"
        transaction.failed_at = datetime.now()
        transaction.paystack_status = "failed"
        transaction.failure_reason = "Payment failed at Paystack"
        db.commit()

        return PaymentVerifyResponse(
            success=False,
            status="failed",
            amount=transaction.amount,
            reference=reference,
            message="Payment failed. Please try again."
        )

    else:  # abandoned or pending
        return PaymentVerifyResponse(
            success=False,
            status=payment_status,
            amount=transaction.amount,
            reference=reference,
            message=f"Payment {payment_status}. Please complete the payment."
        )
