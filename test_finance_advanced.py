"""
test_finance_advanced.py
=========================
Advanced pytest features:
- Fixtures      : reusable test data
- Parametrize   : test multiple inputs at once
- Mocking       : fake external connections
"""

import pytest
from unittest.mock import patch, MagicMock
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


# ── FIXTURES ────────────────────────────────────────────────────

@pytest.fixture
def sample_transactions():
    """
    Fresh transaction data for each test.
    This runs before every test that requests it.
    Like a setUp() that resets automatically.
    """
    return [
        {"id": 1, "description": "Salary",  "category": "Income",       "amount":  3830.00},
        {"id": 2, "description": "ASB",     "category": "Commitment",   "amount":  -424.00},
        {"id": 3, "description": "Mamak",   "category": "Food",         "amount":  -15.00},
        {"id": 4, "description": "Shopee",  "category": "Shopping",     "amount":  -320.00},
        {"id": 5, "description": "Giant",   "category": "Food",         "amount":  -90.00},
        {"id": 6, "description": "Netflix", "category": "Entertainment","amount":  -63.00},
        {"id": 7, "description": "Grab",    "category": "Transport",    "amount":  -45.00},
    ]

@pytest.fixture
def single_income():
    """Single income transaction for focused tests"""
    return {"id": 1, "description": "Salary",
            "category": "Income", "amount": 3830.00}

@pytest.fixture
def single_expense():
    """Single expense transaction for focused tests"""
    return {"id": 2, "description": "Shopee",
            "category": "Shopping", "amount": -320.00}

@pytest.fixture
def empty_transactions():
    """Empty list for edge case tests"""
    return []


# ── FIXTURE USAGE TESTS ─────────────────────────────────────────

class TestWithFixtures:
    """Tests using fixtures — notice how clean each test is"""

    def test_income_with_fixture(self, sample_transactions):
        """Fixture passed as parameter — resets every test"""
        result = calculate_total_income(sample_transactions)
        assert result == 3830.00

    def test_expenses_with_fixture(self, sample_transactions):
        result = calculate_total_expenses(sample_transactions)
        assert result == 957.00

    def test_empty_income(self, empty_transactions):
        result = calculate_total_income(empty_transactions)
        assert result == 0

    def test_biggest_expense_with_fixture(self, sample_transactions):
        result = get_biggest_expense(sample_transactions)
        assert result["description"] == "ASB"


# ── PARAMETRIZE ─────────────────────────────────────────────────
# Test the same function with many different inputs at once
# Instead of writing 5 separate tests — write 1

class TestParametrize:
    """Tests using parametrize — one test, many inputs"""

    @pytest.mark.parametrize("amount, expected_type", [
        (-320.00, "LARGE_EXPENSE"),   # Shopee — should trigger
        (-250.00, "LARGE_EXPENSE"),   # Uniqlo — should trigger
        (-150.00, "LARGE_EXPENSE"),   # Gym    — should trigger
        (-100.01, "LARGE_EXPENSE"),   # just above threshold
    ])
    def test_large_expense_triggers(self, amount, expected_type):
        """Test multiple amounts that should all trigger large expense"""
        txn = {"description": "Test", "category": "Shopping",
               "amount": amount}
        result = check_large_expense(txn)
        assert result is not None
        assert result["type"] == expected_type

    @pytest.mark.parametrize("amount", [
        -100.00,   # exactly at threshold — no trigger
        -99.99,    # just below threshold — no trigger
        -50.00,    # well below — no trigger
        -0.01,     # tiny expense — no trigger
    ])
    def test_large_expense_no_trigger(self, amount):
        """Test multiple amounts that should NOT trigger"""
        txn = {"description": "Test", "category": "Food",
               "amount": amount}
        result = check_large_expense(txn)
        assert result is None

    @pytest.mark.parametrize("category, expected_count", [
        ("Food",          2),   # Mamak + Giant
        ("Shopping",      1),   # Shopee
        ("Entertainment", 1),   # Netflix
        ("Transport",     1),   # Grab
        ("Health",        0),   # none in sample data
    ])
    def test_filter_by_category(self, sample_transactions, category,
                                expected_count):
        """Test filtering returns correct count for each category"""
        result = filter_by_category(sample_transactions, category)
        assert len(result) == expected_count

    @pytest.mark.parametrize("transactions, expected_balance", [
        ([{"amount": 1000}, {"amount": -500}],   500),
        ([{"amount": 500},  {"amount": -500}],     0),
        ([{"amount": 200},  {"amount": -500}],  -300),
        ([{"amount": 3830}, {"amount": -957}],  2873),
    ])
    def test_net_balance_scenarios(self, transactions, expected_balance):
        """Test net balance with multiple income/expense scenarios"""
        result = calculate_net_balance(transactions)
        assert result == expected_balance


# ── MOCKING ─────────────────────────────────────────────────────
# Mock = replace a real external connection with a fake one
# Why: we don't want tests to actually connect to PostgreSQL or Redis
# Tests should run fast and independently — no database needed

class TestMocking:
    """Tests using mocks — fake external connections"""

    def test_mock_redis_connection(self):
        """
        Test that our alert saving logic works
        WITHOUT actually connecting to Redis
        """
        # Create a fake Redis object
        mock_redis = MagicMock()

        # Simulate saving an alert
        alert = {"type": "LARGE_EXPENSE", "message": "Test alert"}
        import json
        mock_redis.rpush("alerts", json.dumps(alert))

        # Verify rpush was called with correct arguments
        mock_redis.rpush.assert_called_once()
        print("\n✅ Redis mock working — no real Redis needed")

    def test_mock_database_query(self):
        """
        Test data processing WITHOUT connecting to PostgreSQL
        """
        # Fake what pd.read_sql would return
        import pandas as pd

        mock_data = pd.DataFrame([
            {"date": "2026-05-07", "description": "Salary",
             "category": "Income", "amount": 3830.00},
            {"date": "2026-05-07", "description": "ASB",
             "category": "Commitment", "amount": -424.00},
        ])

        # Test our calculations on the mock data
        income = mock_data[mock_data["amount"] > 0]["amount"].sum()
        expenses = mock_data[mock_data["amount"] < 0]["amount"].abs().sum()

        assert income == 3830.00
        assert expenses == 424.00
        print("\n✅ Database mock working — no real PostgreSQL needed")

    @patch("builtins.open")
    def test_mock_file_read(self, mock_open):
        """
        Test that file reading is called correctly
        WITHOUT actually reading a file
        """
        mock_open.return_value.__enter__ = MagicMock()
        mock_open.return_value.__exit__ = MagicMock()

        # Verify open was not yet called
        mock_open.assert_not_called()

        # Call open
        with open("transactions.csv", "r"):
            pass

        # Verify open was called with correct file
        mock_open.assert_called_once_with("transactions.csv", "r")
        print("\n✅ File mock working — no real file needed")


# ── INTEGRATION-STYLE TESTS ─────────────────────────────────────

class TestFullPipeline:
    """
    Tests that verify the full analysis pipeline works end to end
    Using only the fixture data — no external connections
    """

    def test_full_analysis_pipeline(self, sample_transactions):
        """Test the complete analysis flow from raw data to summary"""
        # Step 1 — Calculate totals
        income   = calculate_total_income(sample_transactions)
        expenses = calculate_total_expenses(sample_transactions)
        balance  = calculate_net_balance(sample_transactions)

        # Step 2 — Verify relationships
        assert income > 0
        assert expenses > 0
        assert balance == income - expenses

        # Step 3 — Category breakdown
        by_category = get_spending_by_category(sample_transactions)
        assert len(by_category) > 0
        assert sum(by_category.values()) == expenses

    def test_alert_pipeline(self, sample_transactions):
        """Test that alerts fire correctly for all transactions"""
        alerts = []

        for t in sample_transactions:
            for rule in [check_large_expense, check_shopping,
                         check_income, check_food_overspend]:
                result = rule(t)
                if result:
                    alerts.append(result)

        # Verify we got alerts
        assert len(alerts) > 0

        # Verify alert types
        alert_types = [a["type"] for a in alerts]
        assert "LARGE_EXPENSE" in alert_types
        assert "INCOME" in alert_types

    def test_category_totals_sum_to_expenses(self, sample_transactions):
        """Category totals should add up to total expenses"""
        total_expenses   = calculate_total_expenses(sample_transactions)
        by_category      = get_spending_by_category(sample_transactions)
        category_total   = sum(by_category.values())

        assert round(category_total, 2) == round(total_expenses, 2)