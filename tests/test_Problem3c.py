import unittest
from pathlib import Path
import tempfile

import src.Problem1c as problem1c
import src.Problem2c as problem2c
import src.Problem3ab as problem3ab  # <-- change to your actual module name

import questionary


class TestSignupFlow(unittest.TestCase):
    def setUp(self):
        # Temporary data dir for all files used by this module
        self.tmpdir = tempfile.TemporaryDirectory()
        data_dir = Path(self.tmpdir.name) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        # Redirect files in Problem3 module
        problem3ab.PASSWD_FILE = data_dir / "passwd.txt"
        problem3ab.ROLES_FILE = data_dir / "roles.txt"
        problem3ab.WEAK_PASSWD_FILE = data_dir / "weak_passwords.txt"

        problem3ab.PASSWD_FILE.touch(exist_ok=True)
        problem3ab.ROLES_FILE.touch(exist_ok=True)
        problem3ab.WEAK_PASSWD_FILE.touch(exist_ok=True)

        # Also redirect Problem2c's PASSWD_FILE so add_user writes there
        problem2c.PASSWD_FILE = problem3ab.PASSWD_FILE

        # Save original questionary functions to restore later
        self._orig_text = questionary.text
        self._orig_password = questionary.password
        self._orig_checkbox = questionary.checkbox

        # If Role.list_values exists, we may want to stub it to a small, known list
        if hasattr(problem1c, "Role") and hasattr(problem1c.Role, "list_values"):
            self._orig_role_list_values = problem1c.Role.list_values
            problem1c.Role.list_values = staticmethod(lambda: ["CLIENT", "EMPLOYEE"])

    def tearDown(self):
        # Restore questionary
        questionary.text = self._orig_text
        questionary.password = self._orig_password
        questionary.checkbox = self._orig_checkbox

        # Restore Role.list_values if it was changed
        if hasattr(self, "_orig_role_list_values"):
            problem1c.Role.list_values = self._orig_role_list_values

        self.tmpdir.cleanup()

    # Helpers to fake questionary prompts
    class _DummyPrompt:
        def __init__(self, value):
            self._value = value

        def ask(self):
            return self._value

    def test_signup_success(self):
        """
        Successful signup with valid username, roles, and password
        should write to passwd.txt and roles.txt and return True.
        """
        # username, roles, password to "type"
        username = "alice"
        roles = ["CLIENT"]
        password = "GoodPass1!"  # length 10, upper, lower, digit, special

        # Monkeypatch questionary prompts
        questionary.text = lambda msg: self._DummyPrompt(username)
        questionary.checkbox = lambda msg, choices: self._DummyPrompt(roles)
        questionary.password = lambda msg: self._DummyPrompt(password)

        result = problem3ab.signup()
        self.assertTrue(result)

        # Check passwd.txt
        passwd_lines = (
            problem3ab.PASSWD_FILE.read_text(encoding="utf-8").strip().splitlines()
        )
        self.assertEqual(len(passwd_lines), 1)
        stored_username, stored_hash = passwd_lines[0].split(":", 1)
        self.assertEqual(stored_username, username)
        self.assertNotEqual(stored_hash, password)

        # Check roles.txt
        roles_lines = (
            problem3ab.ROLES_FILE.read_text(encoding="utf-8").strip().splitlines()
        )
        self.assertEqual(len(roles_lines), 1)
        r_user, r_roles = roles_lines[0].split(":", 1)
        self.assertEqual(r_user, username)
        self.assertEqual(r_roles, ",".join(roles))

    def test_signup_invalid_username_format(self):
        """
        Usernames with invalid format (e.g., containing ':') should fail immediately
        without prompting for roles or passwords, and without writing any files.
        """
        bad_username = "bad:username"

        questionary.text = lambda msg: self._DummyPrompt(bad_username)

        # These MUST NOT be called
        def fail_checkbox(*args, **kwargs):
            raise AssertionError(
                "Roles prompt should not be called for invalid username format"
            )

        def fail_password(*args, **kwargs):
            raise AssertionError(
                "Password prompt should not be called for invalid username format"
            )

        questionary.checkbox = fail_checkbox
        questionary.password = fail_password

        result = problem3ab.signup()
        self.assertFalse(result)

        # No writes should occur
        self.assertEqual(problem3ab.PASSWD_FILE.read_text(encoding="utf-8").strip(), "")
        self.assertEqual(problem3ab.ROLES_FILE.read_text(encoding="utf-8").strip(), "")

    def test_signup_duplicate_username(self):
        """
        If the username already exists in passwd.txt, signup should fail early
        without prompting for roles or passwords.
        """
        username = "existinguser"

        # Prepopulate passwd.txt with this user
        problem3ab.PASSWD_FILE.write_text(f"{username}:fakehash\n", encoding="utf-8")

        # Attempt signup again with same username
        questionary.text = lambda msg: self._DummyPrompt(username)

        # These MUST NOT be called
        def fail_checkbox(*args, **kwargs):
            raise AssertionError(
                "Roles prompt should not be called for duplicate username"
            )

        def fail_password(*args, **kwargs):
            raise AssertionError(
                "Password prompt should not be called for duplicate username"
            )

        questionary.checkbox = fail_checkbox
        questionary.password = fail_password

        result = problem3ab.signup()
        self.assertFalse(result)

        # passwd.txt should still contain the single, original entry
        passwd_lines = (
            problem3ab.PASSWD_FILE.read_text(encoding="utf-8").strip().splitlines()
        )
        self.assertEqual(len(passwd_lines), 1)
        stored_username, _ = passwd_lines[0].split(":", 1)
        self.assertEqual(stored_username, username)

        # roles.txt must still be empty
        self.assertEqual(problem3ab.ROLES_FILE.read_text(encoding="utf-8").strip(), "")

    def test_signup_no_roles_selected(self):
        """
        If no roles are selected, signup should fail and not proceed to password.
        """
        username = "bob"

        questionary.text = lambda msg: self._DummyPrompt(username)
        # Simulate user hitting enter without selecting roles
        questionary.checkbox = lambda msg, choices: self._DummyPrompt([])

        def fail_password(*args, **kwargs):
            raise AssertionError(
                "Password prompt should not be called if no roles selected"
            )

        questionary.password = fail_password

        result = problem3ab.signup()
        self.assertFalse(result)

        # No user or roles should be written
        self.assertEqual(problem3ab.PASSWD_FILE.read_text(encoding="utf-8").strip(), "")
        self.assertEqual(problem3ab.ROLES_FILE.read_text(encoding="utf-8").strip(), "")

    def test_signup_invalid_password(self):
        """
        If the password fails any proactive password rule
        (length, character classes, or weak-password list),
        signup should fail and not write any files.
        """
        username = "charlie"
        roles = ["EMPLOYEE"]

        # Username and roles are always valid for this test
        questionary.text = lambda msg: self._DummyPrompt(username)
        questionary.checkbox = lambda msg, choices: self._DummyPrompt(roles)

        # Add a weak password to the weak_passwords.txt file (lowercase)
        problem3ab.WEAK_PASSWD_FILE.write_text("goodpass1!\n", encoding="utf-8")

        def attempt_with(password: str):
            """Helper to run signup with a given password and assert failure + no file writes."""
            questionary.password = lambda msg: self._DummyPrompt(password)
            result = problem3ab.signup()
            self.assertFalse(result, f"Signup should fail for password: {password!r}")
            # Both files must remain empty after each failed attempt
            self.assertEqual(
                problem3ab.PASSWD_FILE.read_text(encoding="utf-8").strip(),
                "",
                "PASSWD_FILE should remain empty after invalid password",
            )
            self.assertEqual(
                problem3ab.ROLES_FILE.read_text(encoding="utf-8").strip(),
                "",
                "ROLES_FILE should remain empty after invalid password",
            )

        # Too short (fails length rule)
        attempt_with("Aa1!")

        # No upper-case letter
        attempt_with("lower1!ab")  # all lower, digit, special, length ok

        # No lower-case letter
        attempt_with("UPPER1!AB")  # all upper, digit, special, length ok

        # No digit
        attempt_with("NoDigit!!")  # upper+lower+special, length ok

        # No allowed special character
        attempt_with("NoSpec1ab")  # upper+lower+digit, but no ! @ # $ % * &

        # On weak-password list (case-insensitive match)
        attempt_with("GoodPass1!")  # lower() == "goodpass1!" in weak_passwords.txt


if __name__ == "__main__":
    unittest.main()
