# ==================================================
# PERSONAL FINANCE TRACKER — FULL PIPELINE
# Combines: PostgreSQL + Pandas + Redis + MongoDB
# ==================================================

# --- IMPORT LIBRARIES ---
# These are tools we installed earlier using pip
import psycopg2                          # connects Python to PostgreSQL directly
import redis                             # connects Python to Redis cache
import json                              # converts data to text format for storing in Redis
import pandas as pd                      # data analysis library
from pymongo import MongoClient          # connects Python to MongoDB
from sqlalchemy import create_engine     # another way to connect to PostgreSQL (used by pandas)
from datetime import datetime            # used to record current date and time

# ==================================================
# STEP 1 — LOAD DATA FROM POSTGRESQL
# PostgreSQL is our main structured database
# It stores clean transaction data in rows and columns
# ==================================================

print("=" * 50)
print("   PERSONAL FINANCE TRACKER — FULL PIPELINE")
print("=" * 50)

print("\n📦 Step 1: Loading from PostgreSQL...")

# Create connection to PostgreSQL
# Format: "postgresql://username:password@host/database_name"
# ⚠️ Replace YOUR_PASSWORD with your actual PostgreSQL password
engine = create_engine("postgresql://postgres:123424722599189@localhost/finance_tracker")

# Read the entire transactions table into a pandas DataFrame
# This is like doing SELECT * FROM transactions in pgAdmin
df = pd.read_sql("SELECT * FROM transactions", engine)

# Convert the date column from text to proper date format
# Without this, pandas treats dates as plain text strings
df["date"] = pd.to_datetime(df["date"])

print(f"✅ Loaded {len(df)} transactions from PostgreSQL")
print(f"   Columns: {list(df.columns)}")

# ==================================================
# STEP 2 — ANALYSE DATA WITH PANDAS
# Pandas lets us calculate summaries quickly
# Same logic as Day 3 but now inside the full pipeline
# ==================================================

print("\n📊 Step 2: Analysing with Pandas...")

# Calculate total income — only rows where amount is positive
total_income = df[df["amount"] > 0]["amount"].sum()

# Calculate total expenses — only rows where amount is negative
# .abs() removes the minus sign so we get a positive number
total_expenses = df[df["amount"] < 0]["amount"].abs().sum()

# Net balance = what is left after all expenses
net_balance = total_income - total_expenses

# Group expenses by category and sort biggest first
# Same as SQL: SELECT category, SUM(ABS(amount)) GROUP BY category ORDER BY total DESC
category_summary = (
    df[df["amount"] < 0]           # filter only expenses
    .groupby("category")["amount"] # group by category
    .sum()                         # sum each group
    .abs()                         # remove minus signs
    .sort_values(ascending=False)  # sort biggest to smallest
)

# Print the summary
print(f"   Total Income:   RM {total_income:.2f}")
print(f"   Total Expenses: RM {total_expenses:.2f}")
print(f"   Net Balance:    RM {net_balance:.2f}")
print("✅ Pandas analysis complete")

# ==================================================
# STEP 3 — CACHE SUMMARY IN REDIS
# Redis stores frequently used data in memory
# So next time we need the summary, we get it instantly
# without recalculating or hitting PostgreSQL again
# ==================================================

print("\n⚡ Step 3: Caching summary in Redis...")

# Connect to Redis running on localhost port 6379 (default port)
# decode_responses=True means Redis returns strings instead of bytes
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Test the connection — should return True
ping_result = r.ping()
print(f"   Redis connection: {ping_result}")

# Build the summary dictionary to store
summary = {
    "total_income":   total_income,     # total money in
    "total_expenses": total_expenses,   # total money out
    "net_balance":    net_balance,      # remaining balance
    "cached_at":      datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # when we cached it
}

# Redis can only store text, not dictionaries
# json.dumps() converts dictionary → text string
# setex() stores it with an expiry of 300 seconds (5 minutes)
# After 5 minutes Redis automatically deletes it
r.setex("finance_summary", 300, json.dumps(summary))

# Read it back to verify it was stored correctly
# json.loads() converts text string → dictionary
cached = json.loads(r.get("finance_summary"))
print(f"   Cached at: {cached['cached_at']}")
print(f"   Expires in: 300 seconds (5 minutes)")
print("✅ Summary cached in Redis")

# ==================================================
# STEP 4 — LOG PIPELINE RUN TO MONGODB
# MongoDB stores flexible unstructured documents
# We use it to keep a log of every time this pipeline runs
# This is useful for tracking history and debugging
# ==================================================

print("\n🍃 Step 4: Logging pipeline run to MongoDB...")

# Connect to MongoDB running on localhost port 27017 (default port)
mongo_client = MongoClient("mongodb://localhost:27017/")

# Select the database (MongoDB creates it automatically if it doesn't exist)
mongo_db = mongo_client["finance_tracker"]

# Select the collection (like a table in SQL)
# We use a separate collection just for pipeline run logs
mongo_col = mongo_db["pipeline_runs"]

# Build the log document
# Notice how flexible this is — we can store nested data,
# arrays, and any fields we want. SQL cannot do this easily.
run_log = {
    "run_date":           datetime.now(),        # when this pipeline ran
    "records_loaded":     len(df),               # how many rows we loaded
    "total_income":       total_income,           # income this run
    "total_expenses":     total_expenses,         # expenses this run
    "net_balance":        net_balance,            # balance this run
    "category_breakdown": category_summary.to_dict(),  # full category breakdown
    "status":             "success",             # did it run successfully?
    "tools_used":         ["PostgreSQL", "Pandas", "Redis", "MongoDB"]  # array field
}

# Insert the log document into MongoDB
result = mongo_col.insert_one(run_log)

# inserted_id is the unique ID MongoDB assigned to this document
print(f"   Document ID: {result.inserted_id}")
print(f"   Records logged: {len(df)}")
print("✅ Pipeline run logged to MongoDB")

# ==================================================
# STEP 5 — PRINT FINAL REPORT
# Display a clean summary of everything we processed
# ==================================================

print("\n" + "=" * 50)
print("   FINAL REPORT")
print("=" * 50)

# Print category breakdown table
print(f"\n{'Category':<15} {'Amount (RM)':>12}")
print("-" * 28)
for cat, amt in category_summary.items():
    print(f"{cat:<15} {amt:>12.2f}")
print("-" * 28)
print(f"{'TOTAL':<15} {total_expenses:>12.2f}")

# Print overall balance
print(f"\n💰 Net Balance: RM {net_balance:.2f}")

# ==================================================
# STEP 6 — VERIFY MONGODB LOG
# Read back the last pipeline run from MongoDB
# to confirm everything was saved correctly
# ==================================================

print("\n📋 Step 6: Verifying MongoDB log...")

# find_one() gets the most recently inserted document
last_run = mongo_col.find_one({"_id": result.inserted_id})

print(f"   Run date:       {last_run['run_date'].strftime('%Y-%m-%d %H:%M:%S')}")
print(f"   Records loaded: {last_run['records_loaded']}")
print(f"   Status:         {last_run['status']}")
print(f"   Tools used:     {last_run['tools_used']}")

# ==================================================
# DONE — ALL 4 TOOLS USED SUCCESSFULLY
# ==================================================

print("\n" + "=" * 50)
print("✅ Pipeline complete!")
print("   PostgreSQL → loaded transaction data")
print("   Pandas     → analysed and summarised")
print("   Redis      → cached summary for speed")
print("   MongoDB    → logged pipeline run history")
print("=" * 50)