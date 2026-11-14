import asyncio
from sqlalchemy import select
from app.database import engine, Base, AsyncSessionLocal
from app.models.user import User
from app.models.resume import Resume
from app.services.auth import hash_password
from app.services.presets import (
    get_classic_single_column_preset,
    get_modern_two_column_preset,
    get_realistic_seed_content,
)


async def seed():
    print("Connecting to database and creating tables if not present...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check or create demo user
        demo_email = "alex@example.com"
        stmt = select(User).where(User.email == demo_email)
        result = await session.execute(stmt)
        user = result.scalars().first()

        if not user:
            print(f"Creating demo user: {demo_email}")
            user = User(
                email=demo_email,
                hashed_password=hash_password("password123"),
                full_name="Alex Mercer",
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        else:
            print(f"Demo user exists: {demo_email} (ID: {user.id})")

        # Check existing resumes for user
        stmt_resumes = select(Resume).where(Resume.user_id == user.id)
        result_resumes = await session.execute(stmt_resumes)
        existing_resumes = result_resumes.scalars().all()

        if not existing_resumes:
            print("Creating sample resumes...")
            content = get_realistic_seed_content()

            # Resume 1: Classic Single Column
            resume_classic = Resume(
                user_id=user.id,
                title="Staff Engineer - Classic Format",
                content=content.model_dump(),
                style=get_classic_single_column_preset().model_dump(),
            )
            session.add(resume_classic)

            # Resume 2: Modern Two-Column Sidebar
            resume_modern = Resume(
                user_id=user.id,
                title="Staff Engineer - Modern Sidebar",
                content=content.model_dump(),
                style=get_modern_two_column_preset().model_dump(),
            )
            session.add(resume_modern)

            await session.commit()
            await session.refresh(resume_classic)
            await session.refresh(resume_modern)

            print(f"Created Classic Resume: ID = {resume_classic.id}")
            print(f"Created Modern Resume:  ID = {resume_modern.id}")
        else:
            print(f"User already has {len(existing_resumes)} resume(s):")
            for r in existing_resumes:
                print(f" - [{r.id}] {r.title}")

    print("Seed completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
