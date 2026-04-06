"""Test factories for generating fixture objects."""
from __future__ import annotations
import random
import string
from datetime import datetime, timezone
from typing import Any, Dict, Optional

def _rand_str(n: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=n))

class UserFactory:
    """Create User-compatible dicts for testing."""

    @classmethod
    def build(cls, **overrides: Any) -> Dict[str, Any]:
        defaults: Dict[str, Any] = {
            "email": f"{_rand_str()}@example.com",
            "full_name": f"Test {_rand_str()}",
            "hashed_password": "$2b$12$fakehash",
            "role": "user",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
        }
        return {**defaults, **overrides}

    @classmethod
    def build_admin(cls, **overrides: Any) -> Dict[str, Any]:
        return cls.build(role="admin", **overrides)

class ItemFactory:
    """Create Item-compatible dicts for testing."""

    @classmethod
    def build(cls, owner_id: int = 1, **overrides: Any) -> Dict[str, Any]:
        defaults: Dict[str, Any] = {
            "title": f"Item {_rand_str()}",
            "description": f"Description {_rand_str(16)}",
            "owner_id": owner_id,
            "is_active": True,
            "view_count": random.randint(0, 1000),
            "created_at": datetime.now(timezone.utc),
        }
        return {**defaults, **overrides}

class NotificationFactory:
    """Create Notification-compatible dicts for testing."""

    @classmethod
    def build(cls, user_id: int = 1, **overrides: Any) -> Dict[str, Any]:
        defaults: Dict[str, Any] = {
            "title": f"Notification {_rand_str()}",
            "body": f"Body text {_rand_str(20)}",
            "type": random.choice(["info", "warning", "success", "error"]),
            "read": False,
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
        }
        return {**defaults, **overrides}