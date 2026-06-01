import pandas as pd
from sqlalchemy import create_engine

# Connect to PostgreSQL (Replace password below)
engine = create_engine("postgresql://postgres:123424722599189@localhost/finance_tracker")

# Load entire table into a DataFrame in ONE line
df = pd.read_sql("SELECT * FROM transactions", engine)

# Fix date column
df["date"] = pd.to_datetime(df["date"])

print("=== DATA LOADED FROM POSTGRESQL ===")
print(df.head())
print(f"\nTotal rows: {len(df)}")

# --- Full analysis from database ---
total_income   = df[df["amount"] > 0]["amount"].sum()
total_expenses = df[df["amount"] < 0]["amount"].sum()

print("\n=== SUMMARY FROM DATABASE ===")
print(f"Total Income:   RM {total_income:.2f}")
print(f"Total Expenses: RM {total_expenses:.2f}")
print(f"Net Balance:    RM {total_income + total_expenses:.2f}")

print("\n=== SPENDING BY CATEGORY FROM DATABASE ===")
category_summary = (
    df[df["amount"] < 0]
    .groupby("category")["amount"]
    .sum()
    .abs()
    .sort_values(ascending=False)
)
print(category_summary)

df = pd.read_sql("SELECT * FROM transactions", engine)

# This proves WHERE the data came from
print("=== SOURCE CHECK ===")
print(f"Columns: {list(df.columns)}")
print(f"Total rows loaded: {len(df)}")
print(df.head())