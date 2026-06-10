"""
finance_functions.py
=====================
Core business logic functions for the Personal Finance Tracker.
These are separated from the main scripts so they can be unit tested.

Author : Iqbal Horan
GitHub : https://github.com/m7iqbal/finance-tracker
"""

# ── TRANSACTION ANALYSIS FUNCTIONS ─────────────────────────────

def calculate_total_income(transactions):
    """
    Calculate total income from a list of transactions.
    
    Args:
        transactions (list): List of transaction dictionaries
        
    Returns:
        float: Total income amount (positive number)
        
    Example:
        >>> txns = [{"amount": 3830.00}, {"amount": -100.00}]
        >>> calculate_total_income(txns)
        3830.0
    """
    return sum(t["amount"] for t in transactions if t["amount"] > 0)


def calculate_total_expenses(transactions):
    """
    Calculate total expenses from a list of transactions.
    
    Args:
        transactions (list): List of transaction dictionaries
        
    Returns:
        float: Total expenses as a positive number
        
    Example:
        >>> txns = [{"amount": 3830.00}, {"amount": -100.00}]
        >>> calculate_total_expenses(txns)
        100.0
    """
    return sum(abs(t["amount"]) for t in transactions if t["amount"] < 0)


def calculate_net_balance(transactions):
    """
    Calculate net balance (income minus expenses).
    
    Args:
        transactions (list): List of transaction dictionaries
        
    Returns:
        float: Net balance amount
    """
    income   = calculate_total_income(transactions)
    expenses = calculate_total_expenses(transactions)
    return income - expenses


def get_biggest_expense(transactions):
    """
    Find the single biggest expense transaction.
    
    Args:
        transactions (list): List of transaction dictionaries
        
    Returns:
        dict: The transaction with the largest expense amount
        None: If no expenses found
    """
    expenses = [t for t in transactions if t["amount"] < 0]
    if not expenses:
        return None
    return min(expenses, key=lambda t: t["amount"])


def filter_by_category(transactions, category):
    """
    Filter transactions by category.
    
    Args:
        transactions (list): List of transaction dictionaries
        category (str): Category name to filter by
        
    Returns:
        list: Filtered list of transactions
    """
    return [t for t in transactions if t["category"] == category]


def get_spending_by_category(transactions):
    """
    Calculate total spending grouped by category.
    
    Args:
        transactions (list): List of transaction dictionaries
        
    Returns:
        dict: Category names as keys, total spent as values
    """
    result = {}
    for t in transactions:
        if t["amount"] < 0:
            cat = t["category"]
            if cat not in result:
                result[cat] = 0
            result[cat] += abs(t["amount"])
    return result


# ── STREAMING ALERT FUNCTIONS ───────────────────────────────────

def check_large_expense(transaction, threshold=100):
    """
    Check if a transaction is a large expense.
    
    Args:
        transaction (dict): Single transaction dictionary
        threshold (float): Amount threshold (default RM100)
        
    Returns:
        dict: Alert dictionary if triggered, None otherwise
    """
    if transaction["amount"] < -threshold:
        return {
            "type":    "LARGE_EXPENSE",
            "level":   "HIGH",
            "message": f"Large expense: {transaction['description']} — RM {abs(transaction['amount']):.2f}"
        }
    return None


def check_shopping(transaction):
    """
    Check if a transaction is a shopping expense.
    
    Args:
        transaction (dict): Single transaction dictionary
        
    Returns:
        dict: Alert dictionary if triggered, None otherwise
    """
    if transaction["category"] == "Shopping" and transaction["amount"] < 0:
        return {
            "type":    "SHOPPING",
            "level":   "MEDIUM",
            "message": f"Shopping detected: {transaction['description']} — RM {abs(transaction['amount']):.2f}"
        }
    return None


def check_income(transaction):
    """
    Check if a transaction is income.
    
    Args:
        transaction (dict): Single transaction dictionary
        
    Returns:
        dict: Alert dictionary if triggered, None otherwise
    """
    if transaction["amount"] > 0:
        return {
            "type":    "INCOME",
            "level":   "INFO",
            "message": f"Income received: {transaction['description']} — RM {transaction['amount']:.2f}"
        }
    return None


def check_food_overspend(transaction, threshold=50):
    """
    Check if a food transaction exceeds the threshold.
    
    Args:
        transaction (dict): Single transaction dictionary
        threshold (float): Food spending limit (default RM50)
        
    Returns:
        dict: Alert dictionary if triggered, None otherwise
    """
    if transaction["category"] == "Food" and transaction["amount"] < -threshold:
        return {
            "type":    "FOOD_OVERSPEND",
            "level":   "LOW",
            "message": f"Food overspend: {transaction['description']} — RM {abs(transaction['amount']):.2f}"
        }
    return None