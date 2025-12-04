# justInvest – Authentication & RBAC System

SYSC 4810 — Assignment

This project implements a simple authentication system using secure password hashing (Argon2id), proactive password checking, user enrolment, and a role-based access control (RBAC) model. Users can sign up, log in, and interact with a command-line interface that shows which operations their assigned roles allow.

## Setup Instructions

These steps assume you are running Linux (or macOS).
Windows users should use the PowerShell equivalents.

### 1. Verify or Install Python 3.12

This project requires Python 3.12.3 or later.

Check your current version:

```bash
python3 --version
```

If Python 3.12 is not installed, install it:

```bash
sudo apt update
sudo apt install python3.12
```

Ensure that venv and pip are available:

```bash
sudo apt install python3.12-venv
sudo apt install python3-pip
```

### 2. Create a virtual environment

```bash
python3.12 -m venv .venv
```

(or use python3 if it points to Python 3.12)

### 3. Activate the virtual environment

```bash
source .venv/bin/activate
```

You should now see (.venv) at the start of your terminal prompt.

### 4. Install required packages

```bash
pip install -r requirements.txt
```

## Running the Program

From the project root (SYSC4810-Assignment), run:

```bash
python -m src.main
```

This launches the justInvest CLI, where you can:

- Sign up (username, password, selected roles)
- Log in
- View operations allowed for your roles
- Perform operations
- Log out or exit

## Running the Tests

All tests must be executed from the project root so imports resolve correctly.

### Run any specific test file

Example:

```bash
python -m tests.Problem1c_Test
```

### Run the entire test suite

If you want to run everything inside the tests/ directory:

```bash
python -m unittest discover -s tests
```
