import pandas as pd
from sqlalchemy import create_engine

# Load from PostgreSQL
engine = create_engine("postgresql://postgres:123424722599189@localhost/finance_tracker")
df = pd.read_sql("SELECT * FROM transactions", engine)
df["date"] = pd.to_datetime(df["date"])

# --- Challenge 1: Average expense per category ---
category_avg = (
    df[df["amount"] < 0]
    .groupby("category")["amount"]
    .mean()
    .abs()
    .sort_values(ascending=False)
)
print("=== AVERAGE EXPENSE PER CATEGORY ===")
print(category_avg)

# --- Challenge 2: Transactions more than RM100 ---
big_expenses = df[df["amount"] < -100]
print("\n=== TRANSACTIONS OVER RM100 ===")
print(big_expenses[["date", "description", "category", "amount"]])

# --- Challenge 3: Sort by amount smallest first ---
sorted_df = df.sort_values("amount")
print("\n=== ALL TRANSACTIONS SORTED ===")
print(sorted_df[["date", "description", "category", "amount"]])