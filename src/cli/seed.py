"""Database seeder — populates sample data."""
import asyncio
import logging

from src.core.database import AsyncSessionLocal
from src.core.security import hash_password
from src.models.user import User
from src.models.item import Item
from src.models.tag import Tag
from src.models.notification import Notification

logger = logging.getLogger(__name__)

async def run_seed() -> None:
    async with AsyncSessionLocal() as db:
        admin = User(
            email="admin@example.com",
            hashed_password=hash_password("adminpass123"),
            full_name="Admin User",
            role="admin",
            is_active=True,
        )
        db.add(admin)
        await db.flush()

        regular = User(
            email="user@example.com",
            hashed_password=hash_password("userpass123"),
            full_name="Regular User",
            role="user",
            is_active=True,
        )
        db.add(regular)
        await db.flush()

        tags = [Tag(name=n, slug=n.lower().replace(" ", "-"), color=c) for n, c in [
            ("Python", "#3776ab"), ("FastAPI", "#009688"), ("Database", "#ff5722"),
        ]]
        for tag in tags:
            db.add(tag)
        await db.flush()

        for i in range(1, 6):
            item = Item(
                title=f"Sample Item {i}",
                description=f"Description for sample item {i}",
                owner_id=admin.id,
            )
            db.add(item)

        notif = Notification(
            user_id=admin.id,
            title="Welcome!",
            body="Your admin account is ready.",
            type="success",
        )
        db.add(notif)

        await db.commit()
        logger.info("Seed complete: 2 users, 3 tags, 5 items, 1 notification")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_seed())