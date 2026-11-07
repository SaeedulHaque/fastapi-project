"""Create an admin user:  python -m app.create_admin admin@school.test"""
import asyncio
import sys
from getpass import getpass

from app import service
from app.database import SessionLocal, engine


async def create(email: str, password: str) -> None:
    try:
        async with SessionLocal() as db:
            await service.create_user(db, email, password, role="admin")
    finally:
        await engine.dispose()  # close the pooled connections before the loop ends


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m app.create_admin EMAIL")
        sys.exit(1)

    email = sys.argv[1]
    password = getpass("Password (at least 8 characters): ")
    if len(password) < 8:
        print("The password is too short.")
        sys.exit(1)

    try:
        asyncio.run(create(email, password))
    except Exception:
        print("Could not create the user. Does that email already exist?")
        sys.exit(1)
    print(f"Admin created: {email}")


if __name__ == "__main__":
    main()
