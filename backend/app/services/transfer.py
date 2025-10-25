"""
Transfer Service
"""
from sqlalchemy.orm import Session
from app.models.account import BankAccount
from app.models.transaction import BankTransaction
from app.models.recipient import BankRecipient
from app.schemas.transfer import TransferInitiate, TransferResponse
from app.services.account import update_account_balance
from app.services.auth import verify_pin_for_account
from datetime import datetime
from decimal import Decimal
import random


def generate_transaction_ref() -> str:
    """Generate unique transaction reference"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join([str(random.randint(0, 9)) for _ in range(3)])
    return f"TXN{timestamp}{random_suffix}"


def calculate_transfer_fee(amount: Decimal) -> Decimal:
    """
    Calculate transfer fee based on amount
    For demo: ₦10 for amounts < ₦5,000, ₦25 for amounts >= ₦5,000
    """
    if amount < 5000:
        return Decimal("10.00")
    else:
        return Decimal("25.00")


def initiate_transfer(db: Session, transfer_data: TransferInitiate) -> TransferResponse:
    """
    Initiate a transfer
    Creates a pending transaction that requires PIN verification
    """
    # Get sender account
    sender_account = db.query(BankAccount).filter(
        BankAccount.account_number == transfer_data.account_number
    ).first()

    if not sender_account:
        raise ValueError("Sender account not found")

    if not sender_account.is_active:
        raise ValueError("Sender account is inactive")

    # Get recipient info
    recipient_name = transfer_data.recipient_name
    recipient_account = transfer_data.recipient_account
    recipient_bank_code = transfer_data.recipient_bank_code
    recipient_bank_name = transfer_data.recipient_bank_name
    recipient_id = transfer_data.recipient_id

    # If recipient_id provided, get recipient details
    if recipient_id:
        recipient = db.query(BankRecipient).filter(
            BankRecipient.id == recipient_id,
            BankRecipient.user_id == sender_account.user_id
        ).first()

        if not recipient:
            raise ValueError("Recipient not found")

        recipient_name = recipient.recipient_name
        recipient_account = recipient.account_number
        recipient_bank_code = recipient.bank_code
        recipient_bank_name = recipient.bank_name

    # Validate recipient details
    if not all([recipient_name, recipient_account, recipient_bank_code, recipient_bank_name]):
        raise ValueError("Incomplete recipient information")

    # Calculate fee
    fee = calculate_transfer_fee(transfer_data.amount)
    total_amount = transfer_data.amount + fee

    # Check balance
    if sender_account.balance < total_amount:
        raise ValueError(f"Insufficient balance. You need ₦{total_amount:,.2f} (including ₦{fee} fee)")

    # Check daily transfer limit
    # TODO: Implement daily limit check

    # Generate transaction reference
    transaction_ref = generate_transaction_ref()

    # Create pending transaction
    new_transaction = BankTransaction(
        account_id=sender_account.id,
        transaction_ref=transaction_ref,
        transaction_type="transfer",
        amount=transfer_data.amount,
        fee=fee,
        currency="NGN",
        recipient_id=recipient_id,
        recipient_account=recipient_account,
        recipient_name=recipient_name,
        recipient_bank_name=recipient_bank_name,
        recipient_bank_code=recipient_bank_code,
        status="pending_pin",  # Requires PIN verification
        narration=transfer_data.narration,
        session_id=transfer_data.session_id,
        initiated_via=transfer_data.initiated_via,
        initiated_at=datetime.now()
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return TransferResponse(
        transaction_id=new_transaction.id,
        transaction_ref=new_transaction.transaction_ref,
        amount=transfer_data.amount,
        fee=fee,
        total_amount=total_amount,
        recipient_name=recipient_name,
        recipient_account=recipient_account,
        recipient_bank_name=recipient_bank_name,
        status="pending_pin",
        message="Transfer initiated. Please verify your PIN to continue.",
        requires_pin=True,
        requires_confirmation=False
    )


def verify_transfer_pin(db: Session, transaction_id: int, pin: str, account_number: str) -> TransferResponse:
    """
    Verify PIN for a pending transfer
    """
    # Get transaction
    transaction = db.query(BankTransaction).filter(BankTransaction.id == transaction_id).first()

    if not transaction:
        raise ValueError("Transaction not found")

    if transaction.status != "pending_pin":
        raise ValueError(f"Transaction is not pending PIN verification (current status: {transaction.status})")

    # Verify PIN
    pin_verification = verify_pin_for_account(db, account_number, pin)

    if not pin_verification.verified:
        raise ValueError(pin_verification.error or "Invalid PIN")

    # Update transaction status
    transaction.status = "pending_confirmation"
    transaction.confirmed_at = datetime.now()
    db.commit()
    db.refresh(transaction)

    total_amount = transaction.amount + transaction.fee

    return TransferResponse(
        transaction_id=transaction.id,
        transaction_ref=transaction.transaction_ref,
        amount=transaction.amount,
        fee=transaction.fee,
        total_amount=total_amount,
        recipient_name=transaction.recipient_name,
        recipient_account=transaction.recipient_account,
        recipient_bank_name=transaction.recipient_bank_name,
        status="pending_confirmation",
        message=f"PIN verified. Ready to transfer ₦{total_amount:,.2f} to {transaction.recipient_name}. Please confirm.",
        requires_pin=False,
        requires_confirmation=True
    )


def confirm_transfer(db: Session, transaction_id: int) -> TransferResponse:
    """
    Confirm and execute a transfer via Paystack
    This makes transfers appear in Paystack dashboard and use real APIs
    """
    from app.services.paystack import paystack_service
    from app.services.notification import notification_service
    import logging

    logger = logging.getLogger(__name__)

    # Get transaction
    transaction = db.query(BankTransaction).filter(BankTransaction.id == transaction_id).first()

    if not transaction:
        raise ValueError("Transaction not found")

    if transaction.status != "pending_confirmation":
        raise ValueError(f"Transaction is not pending confirmation (current status: {transaction.status})")

    try:
        # Get sender account
        sender_account = db.query(BankAccount).filter(BankAccount.id == transaction.account_id).first()

        if not sender_account:
            raise ValueError("Sender account not found")

        # Get recipient details
        recipient = None
        paystack_recipient_code = None

        if transaction.recipient_id:
            recipient = db.query(BankRecipient).filter(BankRecipient.id == transaction.recipient_id).first()
            if recipient and recipient.paystack_recipient_code:
                paystack_recipient_code = recipient.paystack_recipient_code
                logger.info(f"Using Paystack recipient code: {paystack_recipient_code}")

        # If recipient doesn't have Paystack code, create one
        if not paystack_recipient_code:
            logger.info("Creating Paystack recipient on-the-fly")
            paystack_result = paystack_service.create_transfer_recipient(
                recipient_name=transaction.recipient_name,
                account_number=transaction.recipient_account,
                bank_code=transaction.recipient_bank_code,
                currency="NGN"
            )

            if paystack_result["success"]:
                paystack_recipient_code = paystack_result["recipient_code"]
                # Update recipient if it exists
                if recipient:
                    recipient.paystack_recipient_code = paystack_recipient_code
                logger.info(f"Created Paystack recipient: {paystack_recipient_code}")
            else:
                logger.warning(f"Failed to create Paystack recipient: {paystack_result.get('error')}")

        # Initiate Paystack transfer
        transfer_success = False
        paystack_transfer_code = None
        paystack_status = "no_paystack_code"

        if paystack_recipient_code:
            logger.info(f"Initiating Paystack transfer of ₦{transaction.amount}")
            transfer_result = paystack_service.initiate_transfer(
                recipient_code=paystack_recipient_code,
                amount=transaction.amount,
                reason=transaction.narration or f"Transfer to {transaction.recipient_name}",
                reference=transaction.transaction_ref
            )

            if transfer_result["success"]:
                paystack_transfer_code = transfer_result["transfer_code"]
                paystack_status = transfer_result["status"]
                transfer_success = True
                logger.info(f"Paystack transfer initiated: {paystack_transfer_code}, status: {paystack_status}")

                # Store Paystack details
                transaction.paystack_transfer_code = paystack_transfer_code
                transaction.paystack_transfer_id = str(transfer_result["transfer_id"])
                transaction.paystack_status = paystack_status
            else:
                logger.error(f"Paystack transfer failed: {transfer_result.get('error')}")
                paystack_status = f"failed: {transfer_result.get('error')}"
                transaction.paystack_status = paystack_status
        else:
            logger.warning("No Paystack recipient code available, completing as database-only transfer")

        # Deduct from sender (amount + fee) - this happens regardless of Paystack
        total_amount = transaction.amount + transaction.fee
        update_account_balance(db, sender_account.id, total_amount, operation="debit")

        # Check if recipient is a Demo Bank user (internal transfer)
        recipient_demo_account = db.query(BankAccount).filter(
            BankAccount.account_number == transaction.recipient_account
        ).first()

        if recipient_demo_account:
            # INTERNAL TRANSFER - Credit the recipient's Demo Bank account
            logger.info(f"Internal transfer detected! Crediting {transaction.recipient_account}")
            update_account_balance(db, recipient_demo_account.id, transaction.amount, operation="credit")

            # Create credit transaction record for recipient
            # Use original ref + "-CR" suffix to make it unique while keeping link
            credit_ref = f"{transaction.transaction_ref}-CR"

            recipient_transaction = BankTransaction(
                account_id=recipient_demo_account.id,
                transaction_ref=credit_ref,
                transaction_type="credit",
                amount=transaction.amount,
                fee=Decimal("0.00"),  # No fee for receiving
                currency="NGN",
                recipient_account=sender_account.account_number,
                recipient_name=sender_account.account_name,
                recipient_bank_name="Demo Bank",
                status="completed",
                narration=f"Transfer from {sender_account.account_name} - Ref: {transaction.transaction_ref}",
                initiated_via=transaction.initiated_via,
                initiated_at=datetime.now(),
                completed_at=datetime.now()
            )
            db.add(recipient_transaction)

            # Send credit notification to recipient
            try:
                notification_service.send_transfer_credit_notification(
                    db=db,
                    user_id=recipient_demo_account.user_id,
                    account_id=recipient_demo_account.id,
                    amount=transaction.amount,
                    sender_name=sender_account.account_name,
                    sender_account=sender_account.account_number,
                    transaction_ref=transaction.transaction_ref,
                    new_balance=recipient_demo_account.balance
                )
                logger.info(f"Credit notification sent to user {recipient_demo_account.user_id}")
            except Exception as e:
                logger.error(f"Failed to send credit notification: {e}")

        # Update transaction status
        transaction.status = "completed"
        transaction.completed_at = datetime.now()

        # Update recipient's last transfer date
        if transaction.recipient_id and recipient:
            recipient.last_transfer_at = datetime.now()

        db.commit()
        db.refresh(transaction)

        # Send debit notification to sender
        try:
            notification_service.send_transfer_debit_notification(
                db=db,
                user_id=sender_account.user_id,
                account_id=sender_account.id,
                amount=transaction.amount,
                fee=transaction.fee,
                recipient_name=transaction.recipient_name,
                recipient_account=transaction.recipient_account,
                recipient_bank=transaction.recipient_bank_name,
                transaction_ref=transaction.transaction_ref,
                new_balance=sender_account.balance
            )

            # Check for low balance and send alert if needed
            if sender_account.balance < Decimal("1000"):
                notification_service.send_low_balance_alert(
                    db=db,
                    user_id=sender_account.user_id,
                    account_id=sender_account.id,
                    current_balance=sender_account.balance
                )
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

        success_message = f"Transfer of ₦{transaction.amount:,.2f} to {transaction.recipient_name} successful!"
        if paystack_transfer_code:
            success_message += f" (Paystack: {paystack_transfer_code})"

        return TransferResponse(
            transaction_id=transaction.id,
            transaction_ref=transaction.transaction_ref,
            amount=transaction.amount,
            fee=transaction.fee,
            total_amount=total_amount,
            recipient_name=transaction.recipient_name,
            recipient_account=transaction.recipient_account,
            recipient_bank_name=transaction.recipient_bank_name,
            status="completed",
            message=success_message,
            requires_pin=False,
            requires_confirmation=False
        )

    except ValueError as e:
        # Mark transaction as failed
        transaction.status = "failed"
        transaction.failed_at = datetime.now()
        transaction.failure_reason = str(e)
        db.commit()
        raise


def get_transfer_status(db: Session, transaction_id: int) -> TransferResponse:
    """Get the status of a transfer"""
    transaction = db.query(BankTransaction).filter(BankTransaction.id == transaction_id).first()

    if not transaction:
        raise ValueError("Transaction not found")

    total_amount = transaction.amount + transaction.fee

    return TransferResponse(
        transaction_id=transaction.id,
        transaction_ref=transaction.transaction_ref,
        amount=transaction.amount,
        fee=transaction.fee,
        total_amount=total_amount,
        recipient_name=transaction.recipient_name,
        recipient_account=transaction.recipient_account,
        recipient_bank_name=transaction.recipient_bank_name,
        status=transaction.status,
        message=f"Transfer status: {transaction.status}",
        requires_pin=(transaction.status == "pending_pin"),
        requires_confirmation=(transaction.status == "pending_confirmation")
    )


def cancel_transfer(db: Session, transaction_id: int) -> dict:
    """Cancel a pending transfer"""
    transaction = db.query(BankTransaction).filter(BankTransaction.id == transaction_id).first()

    if not transaction:
        raise ValueError("Transaction not found")

    if transaction.status not in ["pending_pin", "pending_confirmation"]:
        raise ValueError("Can only cancel pending transfers")

    transaction.status = "cancelled"
    db.commit()

    return {"message": "Transfer cancelled successfully"}
