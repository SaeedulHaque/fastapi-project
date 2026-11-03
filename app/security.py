from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

# Checked when the email is unknown, so a wrong email and a wrong password
# take the same time and the answer does not reveal which one was wrong.
DUMMY_HASH = password_hash.hash("not-a-real-password")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)
