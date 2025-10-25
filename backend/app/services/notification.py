"""
Notification Service - Send realistic banking notifications
"""
from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationType, NotificationChannel
from app.models.user import BankUser
from app.models.account import BankAccount
from datetime import datetime
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service to create and send notifications"""

    @staticmethod
    def _format_amount(amount: Decimal) -> str:
        """Format amount as NGN currency"""
        return f"NGN {amount:,.2f}"

    @staticmethod
    def _mask_account_number(account_number: str) -> str:
        """Mask account number (e.g., 1234567890 -> 123*****890)"""
        if len(account_number) < 6:
            return account_number
        return f"{account_number[:3]}{'*' * (len(account_number) - 6)}{account_number[-3:]}"

    @staticmethod
    def _create_notification(
        db: Session,
        user_id: int,
        account_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        transaction_ref: str = None,
        amount: str = None,
        recipient_name: str = None,
        channel: NotificationChannel = NotificationChannel.IN_APP
    ) -> Notification:
        """Create a notification in the database"""
        notification = Notification(
            user_id=user_id,
            account_id=account_id,
            notification_type=notification_type,
            channel=channel,
            title=title,
            message=message,
            transaction_ref=transaction_ref,
            amount=amount,
            recipient_name=recipient_name,
            sent_at=datetime.now()
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        logger.info(f"Notification sent to user {user_id}: {title}")
        return notification

    @staticmethod
    def send_welcome_notification(db: Session, user_id: int, account_number: str):
        """Send welcome notification to new user"""
        user = db.query(BankUser).filter(BankUser.id == user_id).first()
        if not user:
            return

        account = db.query(BankAccount).filter(
            BankAccount.user_id == user_id,
            BankAccount.account_number == account_number
        ).first()

        title = "Welcome to Demo Bank"
        message = f"""Dear {user.full_name.upper()},

Welcome to Demo Bank! Your account has been successfully created.

Transaction Summary

A/C Number    {account_number}
Account Name    {user.full_name.upper()}
Account Type    SAVINGS ACCOUNT
Opening Balance    {NotificationService._format_amount(account.balance if account else 0)}
Transaction Branch    DEMO BANK HEAD OFFICE
Transaction Date    {datetime.now().strftime('%d-%b-%Y')}

You can now:
• Send and receive money
• Pay bills and buy airtime
• Check your balance anytime
• Add beneficiaries

Thank you for banking with us!

Demo Bank
Banking made simple"""

        return NotificationService._create_notification(
            db=db,
            user_id=user_id,
            account_id=account.id if account else None,
            notification_type=NotificationType.WELCOME,
            title=title,
            message=message
        )

    @staticmethod
    def send_transfer_debit_notification(
        db: Session,
        user_id: int,
        account_id: int,
        amount: Decimal,
        fee: Decimal,
        recipient_name: str,
        recipient_account: str,
        recipient_bank: str,
        transaction_ref: str,
        new_balance: Decimal
    ):
        """Send debit notification when user sends money (Nigerian bank format)"""
        user = db.query(BankUser).filter(BankUser.id == user_id).first()
        account = db.query(BankAccount).filter(BankAccount.id == account_id).first()

        total_amount = amount + fee
        formatted_total = NotificationService._format_amount(total_amount)
        formatted_balance = NotificationService._format_amount(new_balance)
        masked_account = NotificationService._mask_account_number(account.account_number)

        title = f"Debit Alert: {formatted_total}"
        message = f"""Dear {user.full_name.upper()},

Your account has been Debited
{formatted_total}
Transaction Summary

A/C Number    {masked_account}
Account Name    {user.full_name.upper()}
Description    MOBILE TRF TO {recipient_name.upper()}/{recipient_bank.upper()}
Reference Number    {transaction_ref}
Transaction Branch    DEMO BANK MOBILE
Transaction Date    {datetime.now().strftime('%d-%b-%Y')}
Value Date    {datetime.now().strftime('%d-%b-%Y')}

Account Balance
{formatted_balance}

If you did not authorize this transaction, please contact us immediately at support@demobank.ng

Demo Bank"""

        return NotificationService._create_notification(
            db=db,
            user_id=user_id,
            account_id=account_id,
            notification_type=NotificationType.TRANSFER_SENT,
            title=title,
            message=message,
            transaction_ref=transaction_ref,
            amount=formatted_total,
            recipient_name=recipient_name
        )

    @staticmethod
    def send_transfer_credit_notification(
        db: Session,
        user_id: int,
        account_id: int,
        amount: Decimal,
        sender_name: str,
        sender_account: str,
        transaction_ref: str,
        new_balance: Decimal
    ):
        """Send credit notification when user receives money (Nigerian bank format)"""
        user = db.query(BankUser).filter(BankUser.id == user_id).first()
        account = db.query(BankAccount).filter(BankAccount.id == account_id).first()

        formatted_amount = NotificationService._format_amount(amount)
        formatted_balance = NotificationService._format_amount(new_balance)
        masked_account = NotificationService._mask_account_number(account.account_number)

        title = f"Credit Alert: {formatted_amount}"
        message = f"""Dear {user.full_name.upper()},

Your account has been Credited
{formatted_amount}
Transaction Summary

A/C Number    {masked_account}
Account Name    {user.full_name.upper()}
Description    MOBILE TRF FROM {sender_name.upper()}
Reference Number    {transaction_ref}
Transaction Branch    DEMO BANK MOBILE
Transaction Date    {datetime.now().strftime('%d-%b-%Y')}
Value Date    {datetime.now().strftime('%d-%b-%Y')}

Account Balance
{formatted_balance}

Thank you for banking with us!

Demo Bank"""

        return NotificationService._create_notification(
            db=db,
            user_id=user_id,
            account_id=account_id,
            notification_type=NotificationType.TRANSFER_RECEIVED,
            title=title,
            message=message,
            transaction_ref=transaction_ref,
            amount=formatted_amount,
            recipient_name=sender_name
        )

    @staticmethod
    def send_low_balance_alert(
        db: Session,
        user_id: int,
        account_id: int,
        current_balance: Decimal,
        threshold: Decimal = Decimal("1000")
    ):
        """Send low balance alert (Nigerian bank format)"""
        if current_balance >= threshold:
            return None

        user = db.query(BankUser).filter(BankUser.id == user_id).first()
        account = db.query(BankAccount).filter(BankAccount.id == account_id).first()
        formatted_balance = NotificationService._format_amount(current_balance)
        masked_account = NotificationService._mask_account_number(account.account_number)

        title = "Low Balance Alert"
        message = f"""Dear {user.full_name.upper()},

Your account balance is running low.

Account Details

A/C Number    {masked_account}
Account Name    {user.full_name.upper()}
Current Balance    {formatted_balance}
Alert Date    {datetime.now().strftime('%d-%b-%Y')}

Please fund your account to avoid transaction failures.

You can top up via:
• Bank transfer to your account
• Card payment
• Direct deposit at any Demo Bank branch

For assistance, contact us at:
Phone: +234 800 DEMO BANK
Email: support@demobank.ng

Demo Bank"""

        return NotificationService._create_notification(
            db=db,
            user_id=user_id,
            account_id=account_id,
            notification_type=NotificationType.LOW_BALANCE,
            title=title,
            message=message,
            amount=formatted_balance
        )

    @staticmethod
    def send_login_notification(
        db: Session,
        user_id: int,
        device_info: str = "Mobile App",
        location: str = "Lagos, Nigeria"
    ):
        """Send login notification for security (Nigerian bank format)"""
        user = db.query(BankUser).filter(BankUser.id == user_id).first()
        accounts = db.query(BankAccount).filter(BankAccount.user_id == user_id).first()

        title = "Security Alert - New Login"
        message = f"""Dear {user.full_name.upper()},

We detected a new login to your Demo Bank account.

Login Details

Device    {device_info}
Location    {location}
Date/Time    {datetime.now().strftime('%d-%b-%Y %I:%M %p')}
IP Address    [Hidden for security]

If this wasn't you, please:
1. Change your password immediately
2. Contact us at +234 800 DEMO BANK
3. Visit the nearest Demo Bank branch

For your security, please do not share your:
• Password
• PIN
• OTP codes

Demo Bank
Keeping your account secure"""

        return NotificationService._create_notification(
            db=db,
            user_id=user_id,
            account_id=accounts.id if accounts else None,
            notification_type=NotificationType.LOGIN,
            title=title,
            message=message
        )

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: int,
        limit: int = 50,
        unread_only: bool = False
    ):
        """Get notifications for a user"""
        query = db.query(Notification).filter(Notification.user_id == user_id)

        if unread_only:
            query = query.filter(Notification.is_read == False)

        notifications = query.order_by(Notification.sent_at.desc()).limit(limit).all()
        return notifications

    @staticmethod
    def mark_as_read(db: Session, notification_id: int, user_id: int):
        """Mark a notification as read"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if notification and not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now()
            db.commit()

        return notification

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int):
        """Mark all notifications as read for a user"""
        db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.now()
        })
        db.commit()

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """Get count of unread notifications"""
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()


# Create global instance
notification_service = NotificationService()
