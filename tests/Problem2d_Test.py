import unittest
from pathlib import Path
import tempfile

import src.Problem2c as problem2c


class TestBasicPasswordFile(unittest.TestCase):
    def setUp(self):
        """
        Redirect PASSWD_FILE to a temporary location for each test.
        """
        self.tmpdir = tempfile.TemporaryDirectory()
        data_dir = Path(self.tmpdir.name) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        problem2c.PASSWD_FILE = data_dir / "passwd.txt"
        problem2c.PASSWD_FILE.touch(exist_ok=True)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_add_user_creates_hashed_record(self):
        username = "alice"
        password = "mypassword"

        added = problem2c.add_user(username, password)
        self.assertTrue(added)

        lines = problem2c.PASSWD_FILE.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 1)

        stored_username, stored_hash = lines[0].split(":", 1)
        self.assertEqual(stored_username, username)

        # Ensure it's a hash, not plaintext
        self.assertNotEqual(stored_hash, password)
        self.assertNotIn(password, stored_hash)

    def test_verify_login_correct_and_incorrect(self):
        username = "bob"
        password = "secret123"

        problem2c.add_user(username, password)

        # Correct password should pass
        self.assertTrue(
            problem2c.verify_login(username, password),
            "Correct password should verify",
        )

        # Incorrect password should fail
        self.assertFalse(
            problem2c.verify_login(username, "wrongpass"),
            "Incorrect password should not verify",
        )


if __name__ == "__main__":
    unittest.main()
