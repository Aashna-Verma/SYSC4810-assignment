import unittest
import datetime

from src.Problem1c import (
    Role,
    Operations,
    getAuthorizedOperations,
    isOperationAvailable,
    canPerformOperation,
)


class TestAccessControlPermissions(unittest.TestCase):
    def test_client_has_only_self_permissions(self):
        """Client can operate only on their own accounts, not on client accounts in general."""
        ops = getAuthorizedOperations({Role.CLIENT})

        # Positive checks
        self.assertIn(Operations.VIEW_SELF_ACCOUNT_BALANCE, ops)
        self.assertIn(Operations.VIEW_SELF_INVESTMENT_PORTFOLIO, ops)

        # Negative checks
        self.assertNotIn(Operations.VIEW_CLIENT_ACCOUNT_BALANCE, ops)
        self.assertNotIn(Operations.MODIFY_CLIENT_INVESTMENT_PORTFOLIO, ops)

    def test_premium_inherits_client_permissions(self):
        """Premium client must have at least all the permissions of a regular client."""
        client_ops = getAuthorizedOperations({Role.CLIENT})
        premium_ops = getAuthorizedOperations({Role.PREMIUM_CLIENT})

        # All client ops must be included in premium ops
        self.assertTrue(
            client_ops.issubset(premium_ops),
            "Premium client should have all Client permissions",
        )

        # Check one premium-specific permission we expect
        self.assertIn(
            Operations.VIEW_FINANCIAL_PLANNER_CONTACT,
            premium_ops,
        )

    def test_employee_can_view_client_accounts(self):
        """Employee should be able to view client balances and portfolios."""
        ops = getAuthorizedOperations({Role.EMPLOYEE})

        self.assertIn(Operations.VIEW_CLIENT_ACCOUNT_BALANCE, ops)
        self.assertIn(Operations.VIEW_CLIENT_INVESTMENT_PORTFOLIO, ops)

    def test_financial_advisor_inherits_employee_permissions(self):
        """Financial advisor should have all employee permissions plus extra ones."""
        employee_ops = getAuthorizedOperations({Role.EMPLOYEE})
        advisor_ops = getAuthorizedOperations({Role.FINANCIAL_ADVISOR})

        # Inherits all employee ops
        self.assertTrue(
            employee_ops.issubset(advisor_ops),
            "Financial advisor should include all employee permissions",
        )

        # Plus advisor-specific operations
        self.assertIn(
            Operations.MODIFY_CLIENT_INVESTMENT_PORTFOLIO,
            advisor_ops,
        )
        self.assertIn(
            Operations.VIEW_PRIVATE_CONSUMER_INSTRUMENTS,
            advisor_ops,
        )

    def test_financial_planner_inherits_employee_permissions(self):
        """Financial planner should have all employee permissions plus planner-specific ones."""
        employee_ops = getAuthorizedOperations({Role.EMPLOYEE})
        planner_ops = getAuthorizedOperations({Role.FINANCIAL_PLANNER})

        self.assertTrue(
            employee_ops.issubset(planner_ops),
            "Financial planner should include all employee permissions",
        )

        self.assertIn(
            Operations.MODIFY_CLIENT_INVESTMENT_PORTFOLIO,
            planner_ops,
        )
        self.assertIn(
            Operations.VIEW_MONEY_MARKET_INSTRUMENTS,
            planner_ops,
        )

    def test_teller_inherits_employee_permissions(self):
        """Teller should inherit employee permissions (view client accounts)."""
        employee_ops = getAuthorizedOperations({Role.EMPLOYEE})
        teller_ops = getAuthorizedOperations({Role.TELLER})

        self.assertTrue(
            employee_ops.issubset(teller_ops),
            "Teller should include all employee permissions",
        )


class TestAccessControlTimeRestrictions(unittest.TestCase):
    def test_teller_available_during_work_hours(self):
        """Teller is available during 09:00–17:00."""
        ten_am = datetime.time(10, 0)
        self.assertTrue(isOperationAvailable({Role.TELLER}, time=ten_am))

    def test_teller_unavailable_outside_work_hours(self):
        """Teller is not available at night."""
        eight_pm = datetime.time(20, 0)
        self.assertFalse(isOperationAvailable({Role.TELLER}, time=eight_pm))

    def test_other_roles_available_all_day(self):
        """Non-teller roles should be available at arbitrary times (assuming ROLE_AVAILABILITY is all day)."""
        two_am = datetime.time(2, 0)
        ten_pm = datetime.time(22, 0)

        for role in [
            Role.CLIENT,
            Role.PREMIUM_CLIENT,
            Role.EMPLOYEE,
            Role.FINANCIAL_ADVISOR,
            Role.FINANCIAL_PLANNER,
        ]:
            with self.subTest(role=role, when="2am"):
                self.assertTrue(isOperationAvailable({role}, time=two_am))
            with self.subTest(role=role, when="10pm"):
                self.assertTrue(isOperationAvailable({role}, time=ten_pm))


class TestPerformOperation(unittest.TestCase):
    def test_perform_operation_success_for_authorized_role(self):
        """Client should be allowed to perform their own balance view when available."""
        result = canPerformOperation(
            {Role.CLIENT},
            Operations.VIEW_SELF_ACCOUNT_BALANCE,
        )
        self.assertTrue(result)

    def test_perform_operation_denied_for_unauthorized_operation(self):
        """Client should not be allowed to view other clients' balances."""
        result = canPerformOperation(
            {Role.CLIENT},
            Operations.VIEW_CLIENT_ACCOUNT_BALANCE,
        )
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
