from enum import Enum
import datetime


class Operations(Enum):
    VIEW_SELF_ACCOUNT_BALANCE = "View own account balance"
    VIEW_CLIENT_ACCOUNT_BALANCE = "View client's account balance"
    VIEW_SELF_INVESTMENT_PORTFOLIO = "View own investment portfolio"
    VIEW_CLIENT_INVESTMENT_PORTFOLIO = "View client's investment portfolio"
    MODIFY_SELF_INVESTMENT_PORTFOLIO = "Modify own investment portfolio"
    MODIFY_CLIENT_INVESTMENT_PORTFOLIO = "Modify client's investment portfolio"
    VIEW_FINANCIAL_ADVISOR_CONTACT = "View Financial Advisor contact info"
    VIEW_FINANCIAL_PLANNER_CONTACT = "View Financial Planner contact info"
    VIEW_MONEY_MARKET_INSTRUMENTS = "View money market instruments"
    VIEW_PRIVATE_CONSUMER_INSTRUMENTS = "View private consumer instruments"


class Role(Enum):
    CLIENT = "Client"
    PREMIUM_CLIENT = "Premium Client"
    EMPLOYEE = "Employee"
    FINANCIAL_ADVISOR = "Financial Advisor"
    FINANCIAL_PLANNER = "Financial Planner"
    TELLER = "Teller"


BASE_PERMS = {
    Role.CLIENT: {
        Operations.VIEW_SELF_ACCOUNT_BALANCE,
        Operations.VIEW_SELF_INVESTMENT_PORTFOLIO,
        Operations.VIEW_FINANCIAL_ADVISOR_CONTACT,
    },
    Role.PREMIUM_CLIENT: {
        Operations.MODIFY_SELF_INVESTMENT_PORTFOLIO,
        Operations.VIEW_FINANCIAL_PLANNER_CONTACT,
    },
    Role.EMPLOYEE: {
        Operations.VIEW_CLIENT_ACCOUNT_BALANCE,
        Operations.VIEW_CLIENT_INVESTMENT_PORTFOLIO,
    },
    Role.FINANCIAL_PLANNER: {
        Operations.MODIFY_CLIENT_INVESTMENT_PORTFOLIO,
        Operations.VIEW_MONEY_MARKET_INSTRUMENTS,
    },
    Role.FINANCIAL_ADVISOR: {
        Operations.MODIFY_CLIENT_INVESTMENT_PORTFOLIO,
        Operations.VIEW_PRIVATE_CONSUMER_INSTRUMENTS,
    },
    Role.TELLER: set(),
}

ROLE_PARENT = {
    Role.PREMIUM_CLIENT: [Role.CLIENT],
    Role.FINANCIAL_PLANNER: [Role.EMPLOYEE],
    Role.FINANCIAL_ADVISOR: [Role.EMPLOYEE],
    Role.TELLER: [Role.EMPLOYEE],
}

ALL_DAY_START = datetime.time(0, 0)
ALL_DAY_END = datetime.time(23, 59)
WORK_DAY_START = datetime.time(9, 0)
WORK_DAY_END = datetime.time(17, 0)

ROLE_AVAILABILITY = {
    Role.CLIENT: (ALL_DAY_START, ALL_DAY_END),
    Role.PREMIUM_CLIENT: (ALL_DAY_START, ALL_DAY_END),
    Role.EMPLOYEE: (ALL_DAY_START, ALL_DAY_END),
    Role.FINANCIAL_ADVISOR: (ALL_DAY_START, ALL_DAY_END),
    Role.FINANCIAL_PLANNER: (ALL_DAY_START, ALL_DAY_END),
    Role.TELLER: (WORK_DAY_START, WORK_DAY_END),
}


def isOperationAvailable(roles: set[Role], time: datetime.time | None = None) -> bool:
    """
    Return True if at least one of these roles is allowed to do operations
    at the given time.
    """
    if time is None:
        time = datetime.datetime.now().time()

    for role in roles:
        start, end = ROLE_AVAILABILITY[role]
        if start <= time <= end:
            return True

    return False


def getAuthorizedOperations(roles: set[Role]) -> set[Operations]:
    """
    Compute all operations allowed for any of the given roles,
    including inherited ones through ROLE_PARENT.
    """
    ops: set[Operations] = set()
    seen: set[Role] = set()

    def add_role(r: Role) -> None:
        if r in seen:
            return
        seen.add(r)

        ops.update(BASE_PERMS.get(r, ()))

        for parent in ROLE_PARENT.get(r, ()):
            add_role(parent)

    for role in roles:
        add_role(role)

    return ops


def canPerformOperation(roles: set[Role], operation: Operations) -> bool:
    """
    Check time plus permissions for a user with multiple roles.
    Prints a message and returns True or False.
    """
    if not roles:
        print("Operation not allowed for your access level.")
        return False

    # Time check: at least one role must be active at this time
    if not isOperationAvailable(roles):
        print("Operation not allowed at this time.")
        return False

    # Permission check: operation must be allowed by at least one role (with inheritance)
    if operation not in getAuthorizedOperations(roles):
        print("Operation not allowed for your access level.")
        return False

    return True
