from pathlib import Path
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

PASSWD_FILE = Path("data/passwd.txt")
PASSWD_FILE.touch(exist_ok=True)

# Configure Argon2id hasher
ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
)


def add_user(username: str, password: str) -> bool:
    """
    Enroll a new user and append a record to passwd.txt.
    Returns True if the user was added.
    """

    if not PASSWD_FILE.exists():
        return False

    # Append new record: username:encoded_hash
    encoded_hash = ph.hash(password)
    with PASSWD_FILE.open("a", encoding="utf-8") as file:
        file.write(f"{username}:{encoded_hash}\n")

    return True


def verify_login(username: str, password: str) -> bool:
    """
    Look up the username in passwd.txt and verify the given password.
    Returns True if the password is correct, False otherwise.
    """
    if not PASSWD_FILE.exists():
        return False

    with PASSWD_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            stored_username, encoded_hash = line.split(":", 1)

            if stored_username == username:
                try:
                    ph.verify(encoded_hash, password)
                    return True
                except VerifyMismatchError:
                    return False

    return False
