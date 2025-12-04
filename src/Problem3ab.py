from pathlib import Path
import questionary
from dataclasses import dataclass

import src.Problem1c as problem1c
import src.Problem2c as problem2c

WEAK_PASSWD_FILE = Path("data/weak_passwords.txt")
WEAK_PASSWD_FILE.touch(exist_ok=True)

ROLES_FILE = Path("data/roles.txt")
ROLES_FILE.touch(exist_ok=True)

SPECIAL_CHARS = set("!@#$%*&")


@dataclass
class User:
    username: str
    roles: set[problem1c.Role]


def load_weak_passwords() -> set[str]:
    """
    Load weak passwords from WEAK_PASSWD_FILE (one per line).
    Comparison is case-insensitive.
    """
    weak = set()
    if WEAK_PASSWD_FILE.exists():
        with WEAK_PASSWD_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                pw = line.strip()
                if pw:
                    weak.add(pw.lower())
    return weak


def valid_username(username: str) -> bool:
    """
    Check if the username is valid (no colons, not empty or whitespace).
    """
    if ":" in username or not username.strip():
        return False

    # Check if user already exists
    if problem2c.PASSWD_FILE.exists():
        with problem2c.PASSWD_FILE.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                stored_username, _ = line.split(":", 1)
                if stored_username == username:
                    return False

    return True


def validate_password(username: str, password: str) -> None:
    """
    Validate password against the policy. Raises ValueError if invalid.
    Policy:
      - length 8-12 characters
      - at least one upper, one lower, one digit, one special (! @ # $ % * &)
      - must not equal the username
      - must not be found in the weak password list
    """
    if not (8 <= len(password) <= 12):
        raise ValueError("Password must be between 8 and 12 characters long.")

    # Not equal to username
    if password == username:
        raise ValueError("Password must not match the username.")

    # Character class checks
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in SPECIAL_CHARS for c in password)

    if not has_upper:
        raise ValueError("Password must contain at least one upper-case letter.")
    if not has_lower:
        raise ValueError("Password must contain at least one lower-case letter.")
    if not has_digit:
        raise ValueError("Password must contain at least one numerical digit.")
    if not has_special:
        raise ValueError(
            "Password must contain at least one special character: !, @, #, $, %, *, &."
        )

    weak_passwords = load_weak_passwords()
    if password.lower() in weak_passwords:
        raise ValueError("This password is too common and is not allowed.")


def store_roles(username: str, roles: list[str]) -> None:
    """
    Store roles for a given user in roles.txt.
    Format: username:ROLE1,ROLE2
    """
    entry = f"{username}:{','.join(roles)}\n"
    with ROLES_FILE.open("a", encoding="utf-8") as file:
        file.write(entry)


def signup() -> User | None:
    """
    Complete signup flow:
    1. Ask for username
    2. Validate username (format + uniqueness)
    3. Ask for roles
    4. Validate roles
    5. Ask for password
    6. Validate password
    7. Add user to passwd.txt
    8. Add roles to roles.txt

    Returns a User dataclass on success, or None on failure.
    """

    # 1. Ask for username
    username = questionary.text("Enter username:").ask()

    # 2. Validate username
    if not valid_username(username):
        print("Invalid or already existing username.")
        return None

    # 3. Ask user to choose roles (strings like "Client", "Employee", etc.)
    role_values = questionary.checkbox(
        "Select your roles (space to select, enter to confirm):",
        choices=[role.value for role in problem1c.Role],
    ).ask()

    # 4. Validate roles
    if not role_values:
        print("No roles selected. Signup cancelled.")
        return None

    # 5. Ask for password
    password = questionary.password("Enter password:").ask()

    # 6. Validate password using proactive checker
    try:
        validate_password(username, password)
        print("Password is valid.")
    except ValueError as e:
        print(f"Password is invalid: {e}")
        return None

    # 7. Add user to passwd.txt
    added = problem2c.add_user(username, password)
    if not added:
        print("Error: Failed to write user to password file.")
        return None

    # 8. Store roles in roles.txt (as their string values)
    try:
        store_roles(username, role_values)
    except Exception:
        print("Error: Failed to store user roles.")
        return None

    # 9. Map string values back to Role enums for the User dataclass
    role_set: set[problem1c.Role] = set()
    for rv in role_values:
        for role in problem1c.Role:
            if role.value == rv:
                role_set.add(role)
                break

    user = User(username=username, roles=role_set)
    print("Signup successful.")
    return user
