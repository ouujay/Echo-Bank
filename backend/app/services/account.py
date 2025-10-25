"""
Account Service
"""
from sqlalchemy.orm import Session
from app.models.account import BankAccount
from app.models.transaction import BankTransaction
from app.schemas.account import AccountResponse, BalanceResponse, TransactionResponse, TransactionHistoryResponse
from typing import List
from decimal import Decimal


def get_user_accounts(db: Session, user_id: int) -> List[AccountResponse]:
    """Get all accounts for a user"""
    accounts = db.query(BankAccount).filter(BankAccount.user_id == user_id).all()
    return [AccountResponse.from_orm(account) for account in accounts]


def get_account_by_number(db: Session, account_number: str) -> BankAccount:
    """Get account by account number"""
    account = db.query(BankAccount).filter(BankAccount.account_number == account_number).first()
    if not account:
        raise ValueError("Account not found")
    return account


def get_account_balance(db: Session, account_id: int) -> BalanceResponse:
    """Get balance for an account"""
    account = db.query(BankAccount).filter(BankAccount.id == account_id).first()

    if not account:
        raise ValueError("Account not found")

    return BalanceResponse(
        account_number=account.account_number,
        account_name=account.account_name,
        balance=account.balance,
        available_balance=account.balance,  # In production, consider pending transactions
        currency=account.currency
    )


def get_account_balance_by_number(db: Session, account_number: str) -> BalanceResponse:
    """Get balance by account number"""
    account = db.query(BankAccount).filter(BankAccount.account_number == account_number).first()

    if not account:
        raise ValueError("Account not found")

    return BalanceResponse(
        account_number=account.account_number,
        account_name=account.account_name,
        balance=account.balance,
        available_balance=account.balance,
        currency=account.currency
    )


def get_account_transactions(
    db: Session,
    account_id: int,
    page: int = 1,
    page_size: int = 20
) -> TransactionHistoryResponse:
    """Get transaction history for an account"""
    # Get total count
    total = db.query(BankTransaction).filter(BankTransaction.account_id == account_id).count()

    # Get paginated transactions
    transactions = (
        db.query(BankTransaction)
        .filter(BankTransaction.account_id == account_id)
        .order_by(BankTransaction.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return TransactionHistoryResponse(
        transactions=[TransactionResponse.from_orm(txn) for txn in transactions],
        total=total,
        page=page,
        page_size=page_size
    )


def update_account_balance(db: Session, account_id: int, amount: Decimal, operation: str = "debit"):
    """
    Update account balance
    operation: 'debit' (subtract) or 'credit' (add)
    """
    account = db.query(BankAccount).filter(BankAccount.id == account_id).first()

    if not account:
        raise ValueError("Account not found")

    if operation == "debit":
        if account.balance < amount:
            raise ValueError("Insufficient balance")
        account.balance -= amount
    elif operation == "credit":
        account.balance += amount
    else:
        raise ValueError("Invalid operation. Use 'debit' or 'credit'")

    db.commit()
    db.refresh(account)
    return account
