import pandas as pd

# ============================================================
# STEP 2 — Load CSV
# ============================================================
df = pd.read_csv("transactions.csv")

# df means "DataFrame" — think of it as a smart Excel table in Python

# --- FIRST LOOK at your data ---
print("=== FIRST 5 ROWS ===")
print(df.head())

print("\n=== DATA TYPES ===")
print(df.dtypes)

print("\n=== SHAPE (rows, columns) ===")
print(df.shape)

print("\n=== BASIC STATS ===")
print(df.describe())

# ============================================================
# STEP 3 — Filter & Explore
# ============================================================
# --- FIX date column (tell pandas it's a date, not text) ---
df["date"] = pd.to_datetime(df["date"])

# --- FILTER: only expenses ---
expenses = df[df["amount"] < 0]
print("\n=== EXPENSES ONLY ===")
print(expenses)

# --- FILTER: only Commitment ---
commitment = df[df["category"] == "Commitment"]
print("\n=== COMMITMENT TRANSACTIONS ===")
print(commitment[["date", "description", "amount"]])

# --- FILTER: only Tabung ---
tabung = df[df["category"] == "Tabung"]
print("\n=== TABUNG TRANSACTIONS ===")
print(tabung[["date", "description", "amount"]])

# --- COMPARE: pandas vs your Day 1 Python ---
# Day 1 you wrote 10 lines to filter Food. Now its just 1 line:
food = df[df["category"] == "Food"]
print("\n=== FOOD (1 line vs 10 lines in Day 1) ===")
print(food)

# ============================================================
# STEP 4 — Analysis
# ============================================================
# --- SUMMARY: income vs expenses ---
total_income   = df[df["amount"] > 0]["amount"].sum()
total_expenses = df[df["amount"] < 0]["amount"].sum()
net_balance    = total_income + total_expenses

print("\n=== SUMMARY ===")
print(f"Total Income:   RM {total_income:.2f}")
print(f"Total Expenses: RM {total_expenses:.2f}")
print(f"Net Balance:    RM {net_balance:.2f}")

# --- SPENDING BY CATEGORY ---
# Remember the 15 lines you wrote in Day 1? This does the same:
category_summary = (
    df[df["amount"] < 0]
    .groupby("category")["amount"]
    .sum()
    .abs()
    .sort_values(ascending=False)
)

print("\n=== SPENDING BY CATEGORY ===")
print(category_summary)

# --- BIGGEST EXPENSE ---
biggest = df[df["amount"] < 0].loc[df["amount"].idxmin()]
print("\n=== BIGGEST EXPENSE ===")
print(f"{biggest['date']} | {biggest['description']} | RM {biggest['amount']:.2f}")

# --- % of income spent per category ---
print("\n=== % OF INCOME SPENT PER CATEGORY ===")
category_pct = (category_summary / total_income * 100).round(1)
for cat, pct in category_pct.items():
    print(f"{cat:15} : {pct}%")