"""Create an admin user:  python -m app.create_admin admin@school.test"""
import sys
from getpass import getpass

from app import service
from app.database import SessionLocal


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m app.create_admin EMAIL")
        sys.exit(1)

    email = sys.argv[1]
    password = getpass("Password (at least 8 characters): ")
    if len(password) < 8:
        print("The password is too short.")
        sys.exit(1)

    with SessionLocal() as db:
        try:
            service.create_user(db, email, password, role="admin")
        except Exception:
            print("Could not create the user. Does that email already exist?")
            sys.exit(1)
    print(f"Admin created: {email}")


if __name__ == "__main__":
    main()
