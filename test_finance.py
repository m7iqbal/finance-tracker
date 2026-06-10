"""
test_finance.py
================
Unit tests for Personal Finance Tracker functions.
Run with: pytest test_finance.py -v

Author : Iqbal Horan
GitHub : https://github.com/m7iqbal/finance-tracker
"""

import pytest
from finance_functions import (
    calculate_total_income,
    calculate_total_expenses,
    calculate_net_balance,
    get_biggest_expense,
    filter_by_category,
    get_spending_by_category,
    check_large_expense,
    check_shopping,
    check_income,
    check_food_overspend
)

# ── TEST DATA ───────────────────────────────────────────────────
# This is our "fake" dataset used across all tests
# Think of it like a mini version of your real transactions

SAMPLE_TRANSACTIONS = [
    {"id": 1,  "description": "Salary",    "category": "Income",       "amount":  3830.00},
    {"id": 2,  "description": "ASB",       "category": "Commitment",   "amount":  -424.00},
    {"id": 3,  "description": "Mamak",     "category": "Food",         "amount":  -15.00},
    {"id": 4,  "description": "Shopee",    "category": "Shopping",     "amount":  -320.00},
    {"id": 5,  "description": "Giant",     "category": "Food",         "amount":  -90.00},
    {"id": 6,  "description": "Netflix",   "category": "Entertainment","amount":  -63.00},
    {"id": 7,  "description": "Grab",      "category": "Transport",    "amount":  -45.00},
]


# ── ANALYSIS TESTS ──────────────────────────────────────────────

class TestCalculations:
    """Tests for financial calculation functions"""

    def test_total_income_correct(self):
        """Income should only sum positive amounts"""
        result = calculate_total_income(SAMPLE_TRANSACTIONS)
        assert result == 3830.00

    def test_total_income_no_income(self):
        """Should return 0 if no income transactions"""
        expenses_only = [{"amount": -100}, {"amount": -50}]
        result = calculate_total_income(expenses_only)
        assert result == 0

    def test_total_expenses_correct(self):
        """Expenses should sum absolute values of negative amounts"""
        result = calculate_total_expenses(SAMPLE_TRANSACTIONS)
        assert result == 957.00  # 424+15+320+90+63+45

    def test_total_expenses_no_expenses(self):
        """Should return 0 if no expense transactions"""
        income_only = [{"amount": 3830.00}]
        result = calculate_total_expenses(income_only)
        assert result == 0

    def test_net_balance_correct(self):
        """Net balance should be income minus expenses"""
        result = calculate_net_balance(SAMPLE_TRANSACTIONS)
        assert result == 3830.00 - 957.00

    def test_net_balance_negative(self):
        """Net balance can be negative if expenses exceed income"""
        transactions = [
            {"amount":  500.00},
            {"amount": -800.00}
        ]
        result = calculate_net_balance(transactions)
        assert result == -300.00


# ── BIGGEST EXPENSE TESTS ───────────────────────────────────────

class TestBiggestExpense:
    """Tests for biggest expense function"""

    def test_biggest_expense_correct(self):
        """Should return ASB as biggest expense (RM424)"""
        result = get_biggest_expense(SAMPLE_TRANSACTIONS)
        assert result["description"] == "ASB"
        assert result["amount"] == -424.00

    def test_biggest_expense_empty(self):
        """Should return None if no expenses"""
        income_only = [{"amount": 3830.00, "description": "Salary",
                        "category": "Income"}]
        result = get_biggest_expense(income_only)
        assert result is None

    def test_biggest_expense_single(self):
        """Should work with only one expense"""
        single = [{"amount": -100.00, "description": "Test",
                   "category": "Food"}]
        result = get_biggest_expense(single)
        assert result["amount"] == -100.00


# ── FILTER TESTS ────────────────────────────────────────────────

class TestFiltering:
    """Tests for transaction filtering functions"""

    def test_filter_by_category_food(self):
        """Should return only Food transactions"""
        result = filter_by_category(SAMPLE_TRANSACTIONS, "Food")
        assert len(result) == 2
        assert all(t["category"] == "Food" for t in result)

    def test_filter_by_category_income(self):
        """Should return only Income transactions"""
        result = filter_by_category(SAMPLE_TRANSACTIONS, "Income")
        assert len(result) == 1
        assert result[0]["description"] == "Salary"

    def test_filter_by_category_nonexistent(self):
        """Should return empty list for category that doesn't exist"""
        result = filter_by_category(SAMPLE_TRANSACTIONS, "Health")
        assert result == []

    def test_spending_by_category(self):
        """Should correctly group spending by category"""
        result = get_spending_by_category(SAMPLE_TRANSACTIONS)
        assert result["Food"] == 105.00        # 15 + 90
        assert result["Shopping"] == 320.00
        assert result["Entertainment"] == 63.00
        assert "Income" not in result           # income not included


# ── ALERT FUNCTION TESTS ────────────────────────────────────────

class TestAlertFunctions:
    """Tests for streaming alert functions"""

    def test_large_expense_triggers(self):
        """Should trigger alert for expense over RM100"""
        txn = {"description": "Shopee", "category": "Shopping",
               "amount": -320.00}
        result = check_large_expense(txn)
        assert result is not None
        assert result["type"] == "LARGE_EXPENSE"
        assert result["level"] == "HIGH"

    def test_large_expense_no_trigger(self):
        """Should NOT trigger for expense under RM100"""
        txn = {"description": "Mamak", "category": "Food",
               "amount": -15.00}
        result = check_large_expense(txn)
        assert result is None

    def test_large_expense_custom_threshold(self):
        """Should respect custom threshold"""
        txn = {"description": "Netflix", "category": "Entertainment",
               "amount": -63.00}
        # With default threshold of 100 — no alert
        assert check_large_expense(txn) is None
        # With lower threshold of 50 — should alert
        assert check_large_expense(txn, threshold=50) is not None

    def test_large_expense_income_ignored(self):
        """Should NOT trigger for income"""
        txn = {"description": "Salary", "category": "Income",
               "amount": 3830.00}
        result = check_large_expense(txn)
        assert result is None

    def test_shopping_triggers(self):
        """Should trigger for Shopping category expenses"""
        txn = {"description": "Shopee", "category": "Shopping",
               "amount": -320.00}
        result = check_shopping(txn)
        assert result is not None
        assert result["type"] == "SHOPPING"

    def test_shopping_wrong_category(self):
        """Should NOT trigger for non-Shopping categories"""
        txn = {"description": "Mamak", "category": "Food",
               "amount": -15.00}
        result = check_shopping(txn)
        assert result is None

    def test_income_triggers(self):
        """Should trigger for positive amounts"""
        txn = {"description": "Salary", "category": "Income",
               "amount": 3830.00}
        result = check_income(txn)
        assert result is not None
        assert result["type"] == "INCOME"

    def test_income_no_trigger_expense(self):
        """Should NOT trigger for expenses"""
        txn = {"description": "Mamak", "category": "Food",
               "amount": -15.00}
        result = check_income(txn)
        assert result is None

    def test_food_overspend_triggers(self):
        """Should trigger when Food exceeds RM50"""
        txn = {"description": "Giant", "category": "Food",
               "amount": -90.00}
        result = check_food_overspend(txn)
        assert result is not None
        assert result["type"] == "FOOD_OVERSPEND"

    def test_food_overspend_no_trigger(self):
        """Should NOT trigger when Food is under RM50"""
        txn = {"description": "Mamak", "category": "Food",
               "amount": -15.00}
        result = check_food_overspend(txn)
        assert result is None

    def test_food_overspend_wrong_category(self):
        """Should NOT trigger for non-Food categories"""
        txn = {"description": "Shopee", "category": "Shopping",
               "amount": -320.00}
        result = check_food_overspend(txn)
        assert result is None


# ── EDGE CASE TESTS ─────────────────────────────────────────────

class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_empty_transactions(self):
        """All functions should handle empty list gracefully"""
        assert calculate_total_income([]) == 0
        assert calculate_total_expenses([]) == 0
        assert calculate_net_balance([]) == 0
        assert get_biggest_expense([]) is None
        assert filter_by_category([], "Food") == []
        assert get_spending_by_category([]) == {}

    def test_exactly_at_threshold(self):
        """Expense exactly at RM100 should NOT trigger large expense alert"""
        txn = {"description": "Test", "category": "Transport",
               "amount": -100.00}
        result = check_large_expense(txn)
        assert result is None  # exactly 100 doesn't trigger (needs > 100)

    def test_just_above_threshold(self):
        """Expense just above RM100 SHOULD trigger alert"""
        txn = {"description": "Test", "category": "Transport",
               "amount": -100.01}
        result = check_large_expense(txn)
        assert result is not None