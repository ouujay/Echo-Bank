"""
Bank API Integrations

This module provides the interface for banks to integrate with EchoBank's voice AI.
"""

from app.integrations.bank_client import BankAPIClient, BankAPIError

__all__ = ["BankAPIClient", "BankAPIError"]
