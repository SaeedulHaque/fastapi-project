import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set. Add it to .env (see .env.example).")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

password_hash = PasswordHash.recommended()

# Checked when the email is unknown, so a wrong email and a wrong password
# take the same time and the answer does not reveal which one was wrong.
DUMMY_HASH = password_hash.hash("not-a-real-password")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),  # who the token is about
        "iat": now,  # issued at
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),  # expires at
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def read_access_token(token: str) -> int | None:
    """Return the user id inside a valid token, or None for any bad token."""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],  # never read the algorithm from the token itself
            options={"require": ["exp", "sub"]},
        )
        return int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError):
        return None
