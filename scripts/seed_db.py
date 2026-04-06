#!/usr/bin/env python3
"""
Standalone seed script using asyncpg directly.
Usage: python scripts/seed.py
"""
import asyncio
import os
import hashlib
import uuid

try:
    import asyncpg
except ImportError:
    raise SystemExit("asyncpg required: pip install asyncpg")

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://localhost/app")

def _pg_url(url: str) -> str:
    return url.replace("postgresql+asyncpg://", "postgresql://").replace("postgresql+psycopg2://", "postgresql://")

def _fake_hash(pw: str) -> str:
    return "$2b$12$" + hashlib.sha256(pw.encode()).hexdigest()[:53]

async def seed() -> None:
    conn = await asyncpg.connect(_pg_url(DATABASE_URL))
    try:
        admin_id = await conn.fetchval(
            """
            INSERT INTO users (email, hashed_password, full_name, role, is_active)
            VALUES ($1,$2,$3,$4,$5)
            ON CONFLICT (email) DO UPDATE SET role=EXCLUDED.role
            RETURNING id
            """,
            "admin@example.com", _fake_hash("adminpass123"), "Admin User", "admin", True,
        )
        user_id = await conn.fetchval(
            """
            INSERT INTO users (email, hashed_password, full_name, role, is_active)
            VALUES ($1,$2,$3,$4,$5)
            ON CONFLICT (email) DO NOTHING
            RETURNING id
            """,
            "user@example.com", _fake_hash("userpass123"), "Regular User", "user", True,
        )
        for i in range(1, 6):
            await conn.execute(
                "INSERT INTO items (title, description, owner_id) VALUES ($1,$2,$3) ON CONFLICT DO NOTHING",
                f"Sample Item {i}", f"Description {i}", admin_id,
            )
        for name, slug, color in [("Python","python","#3776ab"),("FastAPI","fastapi","#009688")]:
            await conn.execute(
                "INSERT INTO tags (name, slug, color) VALUES ($1,$2,$3) ON CONFLICT DO NOTHING",
                name, slug, color,
            )
        await conn.execute(
            "INSERT INTO notifications (user_id, title, body, type) VALUES ($1,$2,$3,$4)",
            admin_id, "Welcome!", "Seeded successfully.", "success",
        )
        print("Seed complete.")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(seed())