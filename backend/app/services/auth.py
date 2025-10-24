import bcrypt
from datetime import datetime, timedelta
from app.models.user import User
from sqlalchemy.orm import Session


class AuthService:
    """
    Authentication service for PIN verification and security.

    Handles:
    - PIN hashing and verification
    - Failed attempt tracking
    - Account lockout after 3 failed attempts
    - Auto-unlock after lockout period
    """

    @staticmethod
    def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
        """
        Verify that a plain PIN matches the hashed PIN.

        Args:
            plain_pin: The PIN entered by the user
            hashed_pin: The hashed PIN stored in database

        Returns:
            True if PIN matches, False otherwise
        """
        return bcrypt.checkpw(plain_pin.encode('utf-8'), hashed_pin.encode('utf-8'))

    @staticmethod
    def hash_pin(pin: str) -> str:
        """
        Hash a PIN for secure storage.

        Args:
            pin: Plain text PIN (typically 4 digits)

        Returns:
            Hashed PIN string
        """
        return bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    async def check_pin_locked(user: User, db: Session) -> dict:
        """
        Check if user's PIN is currently locked due to failed attempts.

        If the lockout period has expired, automatically unlock the account.

        Args:
            user: User object to check
            db: Database session

        Returns:
            {
                "is_locked": bool,
                "locked_until": datetime or None,
                "message": str
            }
        """
        if user.pin_locked_until:
            now = datetime.utcnow()

            if now < user.pin_locked_until:
                # Still locked
                remaining_minutes = int((user.pin_locked_until - now).total_seconds() / 60)
                return {
                    "is_locked": True,
                    "locked_until": user.pin_locked_until,
                    "message": f"Account locked. Try again in {remaining_minutes} minutes."
                }
            else:
                # Lockout period expired - unlock user
                user.pin_locked_until = None
                db.commit()
                return {
                    "is_locked": False,
                    "locked_until": None,
                    "message": "Account unlocked"
                }

        return {
            "is_locked": False,
            "locked_until": None,
            "message": "Account not locked"
        }

    @staticmethod
    async def lock_pin(user: User, db: Session, duration_minutes: int = 30):
        """
        Lock user's PIN for a specified duration.

        Args:
            user: User object to lock
            db: Database session
            duration_minutes: How long to lock (default: 30 minutes)
        """
        user.pin_locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        db.commit()

    @staticmethod
    async def handle_pin_verification(
        user: User,
        entered_pin: str,
        db: Session,
        attempt_count: int
    ) -> dict:
        """
        Handle PIN verification with attempt tracking and lockout.

        Args:
            user: User object
            entered_pin: PIN entered by user
            db: Database session
            attempt_count: Current attempt number (1-3)

        Returns:
            {
                "verified": bool,
                "attempts_remaining": int,
                "locked": bool,
                "locked_until": datetime or None,
                "message": str
            }
        """
        # Check if already locked
        lock_status = await AuthService.check_pin_locked(user, db)
        if lock_status["is_locked"]:
            return {
                "verified": False,
                "attempts_remaining": 0,
                "locked": True,
                "locked_until": lock_status["locked_until"],
                "message": lock_status["message"]
            }

        # Verify PIN
        if AuthService.verify_pin(entered_pin, user.pin_hash):
            return {
                "verified": True,
                "attempts_remaining": 3,
                "locked": False,
                "locked_until": None,
                "message": "PIN verified successfully"
            }

        # PIN incorrect
        attempts_remaining = 3 - attempt_count

        # Lock account after 3 failed attempts
        if attempt_count >= 3:
            await AuthService.lock_pin(user, db, duration_minutes=30)
            return {
                "verified": False,
                "attempts_remaining": 0,
                "locked": True,
                "locked_until": user.pin_locked_until,
                "message": "Too many incorrect attempts. Account locked for 30 minutes."
            }

        return {
            "verified": False,
            "attempts_remaining": attempts_remaining,
            "locked": False,
            "locked_until": None,
            "message": f"Incorrect PIN. {attempts_remaining} attempts remaining."
        }


# Create singleton instance
auth_service = AuthService()
