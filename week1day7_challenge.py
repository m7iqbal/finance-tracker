import redis
from pymongo import MongoClient

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# ── Challenge 1: Visit counter ──────────────────
print("=== CHALLENGE 1: VISIT COUNTER ===")
r.incr("visit_count")
count = r.get("visit_count")
print(f"Dashboard visited: {count} times")

# ── Challenge 2: MongoDB logs ───────────────────
print("\n=== CHALLENGE 2: LAST 3 PIPELINE RUNS ===")
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db     = mongo_client["finance_tracker"]
mongo_col    = mongo_db["pipeline_runs"]

logs = mongo_col.find().sort("run_date", -1).limit(3)
for i, log in enumerate(logs, 1):
    print(f"\nRun #{i}")
    print(f"  Date:    {log['run_date'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Records: {log['records_loaded']}")

    # Check if summary exists before printing it
    if "summary" in log:
        print(f"  Income:  RM {log['summary']['total_income']:.2f}")
        print(f"  Balance: RM {log['summary']['net_balance']:.2f}")
    else:
        print(f"  Summary: not available (old run)")

    print(f"  Status:  {log['status']}")

# ── Challenge 3: Clear Redis ────────────────────
print("\n=== CHALLENGE 3: CLEAR REDIS CACHE ===")
print(f"Keys before flush: {r.keys('*')}")
r.flushall()
print("🗑️ Redis cleared!")
print(f"Keys after flush:  {r.keys('*')}")