import questionary

import src.Problem1c as problem1c
import src.Problem2c as problem2c
import src.Problem3ab as problem3ab


def getUserRole(username: str):
    """
    Retrieve the roles associated with the given username from ROLES_FILE.
    Returns a list of roles or an empty list if user not found.
    """
    roles = []
    if problem3ab.ROLES_FILE.exists():
        with problem3ab.ROLES_FILE.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                stored_username, stored_roles = line.split(":", 1)

                if stored_username == username:
                    roles = [
                        role.strip() for role in stored_roles.split(",") if role.strip()
                    ]
                    break
    return roles


def login() -> problem3ab.User | None:
    """
    Prompt for credentials, verify them, and return a User object if valid.
    Loads the user's roles from roles.txt and maps them to Role enums.
    Returns None if authentication fails.
    """
    username = questionary.text("Enter username:").ask()
    password = questionary.password("Enter password:").ask()

    user = problem2c.verify_login(username, password)
    if user is None:
        print("Invalid username or password.")
        return None

    role_strings = getUserRole(username)

    roles: set[problem1c.Role] = set()
    for rs in role_strings:
        for role in problem1c.Role:
            if role.value == rs:
                roles.add(role)
                break

    return problem3ab.User(username=username, roles=roles)


def logged_in_menu(current_user: problem3ab.User):
    """
    Display the system’s operation menu and the operations allowed for
    the current user. Returns a list of permitted operation labels.
    """
    print("\n-------------------------------------")
    print("justInvest System")
    print("-------------------------------------")
    print("Operations available on the system:")

    for i, op in enumerate(problem1c.Operations, start=1):
        print(f"{i}. {op.value}")

    print("-------------------------------------\n")

    allowed_ops = problem1c.getAuthorizedOperations(current_user.roles)
    allowed_labels = [op.value for op in sorted(allowed_ops, key=lambda o: o.value)]

    print("Your roles:", ", ".join(r.value for r in current_user.roles))
    print("You can perform the following operations:")
    for label in allowed_labels:
        print("  -", label)
    print()

    return allowed_labels


def justInvest_CLI():
    """
    Main application loop for the justInvest system.
    Handles signup/login, session management, and operation selection
    until the user logs out or exits.
    """
    current_user: problem3ab.User | None = None

    while True:
        # ---------------- NOT LOGGED IN ----------------
        if current_user is None:
            action = questionary.select(
                "Select an option:",
                choices=["Signup", "Login", "Exit"],
            ).ask()

            if action == "Signup":
                user = problem3ab.signup()
                if user is not None:
                    current_user = user
                    print(f"You are now logged in as {user.username}.")
                else:
                    print("Signup failed.\n")

            elif action == "Login":
                user = login()
                if user is not None:
                    current_user = user
                    print(f"Login successful! Welcome, {user.username}.")

                else:
                    print("Login failed.\n")

            else:  # Exit
                print("Exiting application.")
                return

            allowed_labels = logged_in_menu(current_user)

        # ---------------- LOGGED IN: OPERATIONS MENU ----------------
        else:
            selection = questionary.select(
                "Select an option:",
                choices=allowed_labels + ["Logout", "Exit"],
            ).ask()

            if selection == "Logout":
                print("Logged out.\n")
                current_user = None
                continue

            if selection == "Exit":
                print("Exiting application.\n")
                return

            chosen_op = next(
                (op for op in problem1c.Operations if op.value == selection),
                None,
            )

            if chosen_op is None:
                print("Unknown operation selected.")
                continue

            if problem1c.canPerformOperation(current_user.roles, chosen_op):
                print(f"\n-> Performing operation: {chosen_op.value} ...\n")
            else:
                print("You are not allowed to perform this operation.\n")
