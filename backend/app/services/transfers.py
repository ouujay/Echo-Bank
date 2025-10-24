from app.models.transaction import Transaction
from app.models.user import User
from app.models.recipient import Recipient
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from datetime import datetime, timedelta
import uuid


class TransferService:
    """
    Transfer service handling all transfer-related business logic.

    Features:
    - Balance validation
    - Daily limit enforcement
    - Transaction creation and management
    - Transfer execution
    - Transaction status tracking
    """

    @staticmethod
    async def check_balance(user: User, amount: Decimal) -> dict:
        """
        Verify user has sufficient balance for the transfer.

        Args:
            user: User attempting the transfer
            amount: Transfer amount

        Returns:
            {
                "sufficient": bool,
                "current_balance": float,
                "requested_amount": float,
                "message": str
            }
        """
        if user.balance < amount:
            return {
                "sufficient": False,
                "current_balance": float(user.balance),
                "requested_amount": float(amount),
                "message": f"Insufficient balance. You have ₦{user.balance:,.2f}, need ₦{amount:,.2f}"
            }

        return {
            "sufficient": True,
            "current_balance": float(user.balance),
            "requested_amount": float(amount),
            "message": "Balance sufficient"
        }

    @staticmethod
    async def check_daily_limit(user: User, amount: Decimal, db: Session) -> dict:
        """
        Check if transfer exceeds daily limit.

        Calculates today's total transfers and checks if adding this amount
        would exceed the user's daily limit.

        Args:
            user: User attempting the transfer
            amount: Transfer amount
            db: Database session

        Returns:
            {
                "within_limit": bool,
                "daily_limit": float,
                "used_amount": float,
                "remaining": float,
                "requested": float,
                "message": str
            }
        """
        # Calculate today's start time (midnight UTC)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        # Get sum of all completed transactions today
        today_total = db.query(func.sum(Transaction.amount)).filter(
            Transaction.sender_id == user.id,
            Transaction.status == "completed",
            Transaction.created_at >= today_start
        ).scalar() or Decimal(0)

        # Calculate what total would be with this new transaction
        total_with_new = today_total + amount
        remaining = user.daily_limit - today_total

        if total_with_new > user.daily_limit:
            return {
                "within_limit": False,
                "daily_limit": float(user.daily_limit),
                "used_amount": float(today_total),
                "remaining": float(remaining),
                "requested": float(amount),
                "message": f"Daily limit exceeded. Limit: ₦{user.daily_limit:,.0f}, Used: ₦{today_total:,.0f}, Remaining: ₦{remaining:,.0f}"
            }

        return {
            "within_limit": True,
            "daily_limit": float(user.daily_limit),
            "used_amount": float(today_total),
            "remaining": float(remaining),
            "requested": float(amount),
            "message": "Within daily limit"
        }

    @staticmethod
    async def create_transaction(
        sender: User,
        recipient: Recipient,
        amount: Decimal,
        session_id: str,
        db: Session
    ) -> Transaction:
        """
        Create a new pending transaction.

        Args:
            sender: User sending money
            recipient: Recipient receiving money
            amount: Transfer amount
            session_id: Voice session ID
            db: Database session

        Returns:
            Transaction object
        """
        # Generate unique transaction reference
        transaction_ref = f"REF{uuid.uuid4().hex[:10].upper()}"

        transaction = Transaction(
            transaction_ref=transaction_ref,
            sender_id=sender.id,
            recipient_id=recipient.id,
            amount=amount,
            currency="NGN",
            status="pending_pin",
            session_id=session_id
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction

    @staticmethod
    async def update_transaction_status(
        transaction: Transaction,
        new_status: str,
        db: Session,
        failure_reason: str = None
    ) -> Transaction:
        """
        Update transaction status.

        Args:
            transaction: Transaction to update
            new_status: New status (pending_pin, pending_confirmation, completed, failed, cancelled)
            db: Database session
            failure_reason: Optional reason for failure

        Returns:
            Updated transaction
        """
        transaction.status = new_status

        if new_status == "completed":
            transaction.completed_at = datetime.utcnow()

        if failure_reason:
            transaction.failure_reason = failure_reason

        db.commit()
        db.refresh(transaction)

        return transaction

    @staticmethod
    async def execute_transfer(transaction: Transaction, db: Session) -> dict:
        """
        Execute the actual transfer - deduct from sender and update transaction.

        This is the critical operation that moves money.

        Args:
            transaction: Transaction to execute
            db: Database session

        Returns:
            {
                "success": bool,
                "new_balance": float or None,
                "error": str or None
            }
        """
        try:
            # Get sender
            sender = transaction.sender

            # Double-check balance (safety check)
            if sender.balance < transaction.amount:
                transaction.status = "failed"
                transaction.failure_reason = "Insufficient balance at execution time"
                db.commit()
                return {
                    "success": False,
                    "new_balance": None,
                    "error": "Insufficient balance"
                }

            # Deduct amount from sender's balance
            sender.balance -= transaction.amount

            # Update transaction status
            transaction.status = "completed"
            transaction.completed_at = datetime.utcnow()

            # Commit the changes
            db.commit()
            db.refresh(sender)
            db.refresh(transaction)

            return {
                "success": True,
                "new_balance": float(sender.balance),
                "error": None
            }

        except Exception as e:
            # Rollback on any error
            db.rollback()

            # Mark transaction as failed
            transaction.status = "failed"
            transaction.failure_reason = str(e)
            db.commit()

            return {
                "success": False,
                "new_balance": None,
                "error": str(e)
            }

    @staticmethod
    async def cancel_transaction(transaction: Transaction, db: Session) -> dict:
        """
        Cancel a pending transaction.

        Args:
            transaction: Transaction to cancel
            db: Database session

        Returns:
            {
                "success": bool,
                "message": str
            }
        """
        # Can only cancel if not completed
        if transaction.status == "completed":
            return {
                "success": False,
                "message": "Cannot cancel a completed transaction"
            }

        transaction.status = "cancelled"
        db.commit()

        return {
            "success": True,
            "message": "Transaction cancelled successfully"
        }

    @staticmethod
    async def get_transaction_by_ref(transaction_ref: str, db: Session) -> Transaction:
        """
        Get transaction by reference code.

        Args:
            transaction_ref: Transaction reference (e.g., REF123456789)
            db: Database session

        Returns:
            Transaction object or None
        """
        return db.query(Transaction).filter(
            Transaction.transaction_ref == transaction_ref
        ).first()

    @staticmethod
    async def validate_transfer(
        user: User,
        amount: Decimal,
        db: Session
    ) -> dict:
        """
        Comprehensive validation before creating a transaction.

        Checks both balance and daily limit.

        Args:
            user: User attempting transfer
            amount: Transfer amount
            db: Database session

        Returns:
            {
                "valid": bool,
                "balance_check": dict,
                "limit_check": dict,
                "message": str
            }
        """
        # Check balance
        balance_check = await TransferService.check_balance(user, amount)

        # Check daily limit
        limit_check = await TransferService.check_daily_limit(user, amount, db)

        # Both must pass
        valid = balance_check["sufficient"] and limit_check["within_limit"]

        message = "Transfer validated successfully"
        if not valid:
            if not balance_check["sufficient"]:
                message = balance_check["message"]
            elif not limit_check["within_limit"]:
                message = limit_check["message"]

        return {
            "valid": valid,
            "balance_check": balance_check,
            "limit_check": limit_check,
            "message": message
        }


# Create singleton instance
transfer_service = TransferService()
