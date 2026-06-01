import psycopg2
import redis
import json
import pandas as pd
from pymongo import MongoClient
from sqlalchemy import create_engine
from datetime import datetime

print("=" * 50)
print("   PERSONAL FINANCE TRACKER — FULL PIPELINE")
print("=" * 50)

# ── 1. POSTGRESQL ──────────────────────────────────
print("\n📦 Step 1: Loading from PostgreSQL...")
engine = create_engine("postgresql://postgres:123424722599189@localhost/finance_tracker")
df = pd.read_sql("SELECT * FROM transactions", engine)
df["date"] = pd.to_datetime(df["date"])
print(f"✅ Loaded {len(df)} transactions")

# ── 2. PANDAS ANALYSIS ─────────────────────────────
print("\n📊 Step 2: Analysing with Pandas...")
total_income   = df[df["amount"] > 0]["amount"].sum()
total_expenses = df[df["amount"] < 0]["amount"].abs().sum()
net_balance    = total_income - total_expenses

category_summary = (
    df[df["amount"] < 0]
    .groupby("category")["amount"]
    .sum()
    .abs()
    .sort_values(ascending=False)
)

print(f"  Income:   RM {total_income:.2f}")
print(f"  Expenses: RM {total_expenses:.2f}")
print(f"  Balance:  RM {net_balance:.2f}")
print("✅ Analysis complete")

# ── 3. REDIS CACHE ─────────────────────────────────
print("\n⚡ Step 3: Caching summary in Redis...")
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

summary = {
    "total_income":   total_income,
    "total_expenses": total_expenses,
    "net_balance":    net_balance,
    "cached_at":      datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}
r.setex("finance_summary", 300, json.dumps(summary))

# Verify cache
cached = json.loads(r.get("finance_summary"))
print(f"✅ Cached at: {cached['cached_at']}")

# ── 4. MONGODB ─────────────────────────────────────
print("\n🍃 Step 4: Storing raw data in MongoDB...")
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db     = mongo_client["finance_tracker"]
mongo_col    = mongo_db["pipeline_runs"]

# Store a pipeline run log — flexible document
run_log = {
    "run_date":       datetime.now(),
    "records_loaded": len(df),
    "summary":        summary,
    "category_breakdown": category_summary.to_dict(),
    "status":         "success"
}
mongo_col.insert_one(run_log)
print(f"✅ Pipeline run logged to MongoDB")

# ── 5. FINAL REPORT ────────────────────────────────
print("\n" + "=" * 50)
print("   FINAL REPORT")
print("=" * 50)
print(f"\n{'Category':<15} {'Amount (RM)':>12}")
print("-" * 28)
for cat, amt in category_summary.items():
    print(f"{cat:<15} {amt:>12.2f}")
print("-" * 28)
print(f"{'TOTAL':<15} {total_expenses:>12.2f}")
print(f"\n💰 Net Balance: RM {net_balance:.2f}")
print("\n✅ Pipeline complete — all 4 tools used successfully!")