"""Seed the database with initial data."""
import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import text
from backend.app.core.database import async_session_factory, engine, Base
from backend.app.core.security import get_password_hash
from backend.app.models import User, Camera, Zone, Rule


async def seed():
    """Create initial admin user and sample data."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        # Check if admin already exists
        result = await session.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": "admin@surveillance.local"},
        )
        if result.scalar_one_or_none():
            print("Admin user already exists, skipping seed.")
            return

        # Create admin user
        admin = User(
            id=uuid.uuid4(),
            email="admin@surveillance.local",
            password_hash=get_password_hash("changeme"),
            full_name="System Admin",
            role="ADMIN",
            is_active=True,
        )
        session.add(admin)
        print(f"Created admin user: admin@surveillance.local")

        # Create operator user
        operator = User(
            id=uuid.uuid4(),
            email="operator@surveillance.local",
            password_hash=get_password_hash("operator123"),
            full_name="Security Operator",
            role="OPERATOR",
            is_active=True,
        )
        session.add(operator)
        print(f"Created operator user: operator@surveillance.local")

        # Create sample camera
        camera = Camera(
            id=uuid.uuid4(),
            name="Main Entrance Camera",
            source_type="file",
            source_reference="sample_video.mp4",
            location_label="Building A - Main Entrance",
            enabled=True,
            status="OFFLINE",
            owner_id=admin.id,
        )
        session.add(camera)
        print(f"Created sample camera: {camera.name}")

        # Create sample zone
        zone = Zone(
            id=uuid.uuid4(),
            camera_id=camera.id,
            name="Restricted Entry Zone",
            type="restricted",
            polygon=[
                {"x": 100, "y": 100},
                {"x": 400, "y": 100},
                {"x": 400, "y": 300},
                {"x": 100, "y": 300},
            ],
            enabled=True,
        )
        session.add(zone)

        # Create sample rule
        rule = Rule(
            id=uuid.uuid4(),
            camera_id=camera.id,
            rule_type="dwell",
            configuration={
                "zone_id": str(zone.id),
                "dwell_threshold_seconds": 30,
                "confidence_threshold": 0.5,
            },
            enabled=True,
        )
        session.add(rule)

        await session.commit()
        print("Seed data created successfully!")
        print("\nLogin credentials:")
        print("  Admin:    admin@surveillance.local / changeme")
        print("  Operator: operator@surveillance.local / operator123")


if __name__ == "__main__":
    asyncio.run(seed())
