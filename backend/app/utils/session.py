"""
In-memory session management for EchoBank
For production on Azure, consider using Azure Cache for Redis or database-backed sessions
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json


class InMemorySessionStore:
    """Simple in-memory session store - suitable for single instance deployments"""

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._expiry: Dict[str, datetime] = {}

    def set(self, session_id: str, data: Dict[str, Any], expire_minutes: int = 30):
        """Store session data with expiration"""
        self._store[session_id] = data
        self._expiry[session_id] = datetime.utcnow() + timedelta(minutes=expire_minutes)

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data if not expired"""
        self._cleanup_expired()

        if session_id not in self._store:
            return None

        if session_id in self._expiry and datetime.utcnow() > self._expiry[session_id]:
            self.delete(session_id)
            return None

        return self._store.get(session_id)

    def delete(self, session_id: str):
        """Delete session data"""
        self._store.pop(session_id, None)
        self._expiry.pop(session_id, None)

    def update(self, session_id: str, data: Dict[str, Any]):
        """Update existing session data"""
        if session_id in self._store:
            self._store[session_id].update(data)

    def _cleanup_expired(self):
        """Remove expired sessions"""
        now = datetime.utcnow()
        expired_keys = [
            key for key, expiry in self._expiry.items()
            if now > expiry
        ]
        for key in expired_keys:
            self.delete(key)


# Global session store instance
session_store = InMemorySessionStore()
