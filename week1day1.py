# --- PERSONAL FINANCE TRACKER ---
# Day 1: Understanding our data

# A list of transactions (this is your "mini database" for now)
transactions = [
    {"date": "2026-05-07", "description": "Salary",      "category": "Income",        "amount":  3830.00},
    {"date": "2026-05-10", "description": "PTPTN",       "category": "Commitment",    "amount":  -181.70},
    {"date": "2026-05-07", "description": "Rumah Sewa",  "category": "Commitment",    "amount": -56.00},
    {"date": "2026-05-07", "description": "Rumah Family","category": "Commitment",    "amount": -100.00},
    {"date": "2026-05-05", "description": "ASB",         "category": "Commitment",    "amount":  -424.00},
    {"date": "2026-05-10", "description": "Medical",     "category": "Commitment",    "amount":  -200.00},
    {"date": "2026-05-07", "description": "Netflix",     "category": "Entertainment", "amount":  -63.00},
    {"date": "2026-05-07", "description": "Setel",       "category": "Transport",     "amount": -100.00},
    {"date": "2026-05-07", "description": "Shoes",       "category": "Shopping",      "amount":  -200.00},
    {"date": "2026-05-07", "description": "Zakat",       "category": "Commitment",    "amount":  -69.00},
    {"date": "2026-05-07", "description": "Parents",     "category": "Commitment",    "amount":  -250.00},
    {"date": "2026-05-07", "description": "Prepaid",     "category": "Commitment",    "amount":  -75.00},
    {"date": "2026-05-07", "description": "Scooter",     "category": "Transport",     "amount":  -100.00},
    {"date": "2026-05-07", "description": "Travel",      "category": "Tabung",        "amount":  -200.00},
    {"date": "2026-05-07", "description": "Toiletries",  "category": "Shopping",      "amount":  -100.00},
    {"date": "2026-05-07", "description": "Facial",      "category": "Tabung",        "amount":  -100.00},
]

# --- TASK 1: Print all transactions ---
print("=== COMMITMENT TRANSACTIONS ===")
for t in transactions:
    if t["category"] == "Commitment":
        print(f"{t['date']} | {t['description']:20} | {t['category']:15} | RM {t['amount']:.2f}")

# --- TASK 2: Calculate total income and total expenses ---
total_income = 0
total_expenses = 0

for t in transactions:
    if t["amount"] > 0:
        total_income += t["amount"]
    else:
        total_expenses += t["amount"]

print("\n=== SUMMARY ===")
print(f"Total Income:   RM {total_income:.2f}")
print(f"Total Expenses: RM {total_expenses:.2f}")
print(f"Net Balance:    RM {total_income + total_expenses:.2f}")

# --- TASK 3: Spending by category ---
print("\n=== SPENDING BY CATEGORY ===")
category_totals = {}

for t in transactions:
    if t["amount"] < 0:  # Only expenses
        category = t["category"]
        if category not in category_totals:
            category_totals[category] = 0
        category_totals[category] += abs(t["amount"])  # abs() removes the minus sign

for category, total in category_totals.items():
    print(f"{category:15} : RM {total:.2f}")

# --- TASK 4: Biggest single expense ---
biggest_expense = None

for t in transactions:
    if t["amount"] < 0:
        if biggest_expense is None or t["amount"] < biggest_expense["amount"]:
            biggest_expense = t

print("\n=== BIGGEST EXPENSE ===")
print(f"{biggest_expense['date']} | {biggest_expense['description']} | RM {biggest_expense['amount']:.2f}")

# Print a single value fr0m the dictionary
#print(transaction["description"])  # Output: Grocery Store
#print(transaction["amount"])       # Output: 85.5