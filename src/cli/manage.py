"""Management CLI built with Typer."""
import asyncio
from typing import Optional

import typer

app = typer.Typer(help="Project management CLI")

@app.command("db-migrate")
def db_migrate(
    revision: str = typer.Argument("head", help="Alembic revision target"),
):
    """Run Alembic database migrations."""
    import subprocess
    result = subprocess.run(["alembic", "upgrade", revision], check=False)
    if result.returncode == 0:
        typer.echo(typer.style("Migrations applied", fg=typer.colors.GREEN))
    else:
        typer.echo(typer.style("Migration failed", fg=typer.colors.RED))
        raise typer.Exit(result.returncode)

@app.command("db-seed")
def db_seed():
    """Seed the database with sample data."""
    from src.cli.seed import run_seed
    asyncio.run(run_seed())
    typer.echo(typer.style("Database seeded", fg=typer.colors.GREEN))

@app.command("create-admin")
def create_admin(
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True, confirmation_prompt=True),
):
    """Create an admin user account."""
    async def _create():
        from src.core.database import AsyncSessionLocal
        from src.models.user import User
        from src.core.security import hash_password
        async with AsyncSessionLocal() as db:
            user = User(email=email, hashed_password=hash_password(password), role="admin", is_active=True)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            typer.echo(f"Admin created: id={user.id} email={user.email}")
    asyncio.run(_create())

@app.command("show-stats")
def show_stats():
    """Print platform statistics."""
    async def _stats():
        from src.models.item import Item
        from sqlalchemy import func, select
        async with AsyncSessionLocal() as db:
            users = (await db.execute(select(func.count(User.id)))).scalar_one()
            items = (await db.execute(select(func.count(Item.id)))).scalar_one()
            typer.echo(f"Users: {users}  Items: {items}")
    asyncio.run(_stats())

if __name__ == "__main__":
    app()