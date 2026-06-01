import os
import json
import time
import redis
from datetime import datetime

# --- FLINK SETUP (attempts real Flink first) ---
os.environ["PYFLINK_PYTHON"] = r"C:\Users\iQbalhoran\AppData\Local\Programs\Python\Python311\python.exe"

try:
    from pyflink.datastream import StreamExecutionEnvironment
    from pyflink.common import Types
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    FLINK_AVAILABLE = True
    print("✅ Real PyFlink loaded")
except Exception:
    FLINK_AVAILABLE = False
    print("⚠️  PyFlink unavailable — running simulation mode")

# ── SIMULATION (works regardless) ──────────────────────────────
print("=" * 55)
print("   FLINK-STYLE REAL-TIME TRANSACTION STREAM")
print("=" * 55)

# --- CONNECT TO REDIS ---
r = redis.Redis(host="localhost", port=6379, decode_responses=True)
r.delete("alerts")
r.set("visit_count", 0)

# --- SOURCE ---
transactions = [
    {"id": 1,  "description": "Salary",      "category": "Income",        "amount":  3830.00},
    {"id": 2,  "description": "Mamak",        "category": "Food",          "amount":  -15.00},
    {"id": 3,  "description": "Grab",         "category": "Transport",     "amount":  -45.00},
    {"id": 4,  "description": "Shopee",       "category": "Shopping",      "amount":  -320.00},
    {"id": 5,  "description": "Teh Tarik",    "category": "Food",          "amount":  -3.50},
    {"id": 6,  "description": "Petronas",     "category": "Transport",     "amount":  -80.00},
    {"id": 7,  "description": "Uniqlo",       "category": "Shopping",      "amount":  -250.00},
    {"id": 8,  "description": "Netflix",      "category": "Entertainment", "amount":  -63.00},
    {"id": 9,  "description": "Pizza Hut",    "category": "Food",          "amount":  -55.00},
    {"id": 10, "description": "Lazada",       "category": "Shopping",      "amount":  -180.00},
    {"id": 11, "description": "Grab Food",    "category": "Food",          "amount":  -25.00},
    {"id": 12, "description": "Touch n Go",   "category": "Transport",     "amount":  -100.00},
    {"id": 13, "description": "Giant",        "category": "Food",          "amount":  -90.00},
    {"id": 14, "description": "Gym",          "category": "Health",        "amount":  -150.00},
    {"id": 15, "description": "Book",         "category": "Education",     "amount":  -45.00},
]

# --- TRANSFORM FUNCTIONS ---
def check_large_expense(t):
    if t["amount"] < -100:
        return {
            "type":    "LARGE_EXPENSE",
            "level":   "🚨 HIGH",
            "message": f"Large expense: {t['description']} — RM {abs(t['amount']):.2f}",
            "time":    datetime.now().strftime("%H:%M:%S")
        }
    return None

def check_shopping(t):
    if t["category"] == "Shopping" and t["amount"] < 0:
        return {
            "type":    "SHOPPING",
            "level":   "🛍️  MED",
            "message": f"Shopping detected: {t['description']} — RM {abs(t['amount']):.2f}",
            "time":    datetime.now().strftime("%H:%M:%S")
        }
    return None

def check_income(t):
    if t["amount"] > 0:
        return {
            "type":    "INCOME",
            "level":   "💰 INFO",
            "message": f"Income received: {t['description']} — RM {t['amount']:.2f}",
            "time":    datetime.now().strftime("%H:%M:%S")
        }
    return None

def save_to_redis(alert):
    if alert:
        r.rpush("alerts", json.dumps(alert))

# --- STREAM PROCESSING ---
print("\n⚡ Stream started — processing transactions in real time...\n")

alert_counts = {"LARGE_EXPENSE": 0, "SHOPPING": 0, "INCOME": 0}

for t in transactions:
    time.sleep(0.3)
    print(f"📥 [{datetime.now().strftime('%H:%M:%S')}] Received: "
          f"{t['description']:15} RM {t['amount']:>10.2f}")

    for rule in [check_large_expense, check_shopping, check_income]:
        alert = rule(t)
        if alert:
            print(f"   └─ {alert['level']} {alert['message']}")
            save_to_redis(alert)
            alert_counts[alert["type"]] += 1

# --- SINK SUMMARY ---
print("\n" + "=" * 55)
print("   STREAM COMPLETE — ALERT SUMMARY")
print("=" * 55)
print(f"  🚨 Large expense alerts : {alert_counts['LARGE_EXPENSE']}")
print(f"  🛍️  Shopping alerts      : {alert_counts['SHOPPING']}")
print(f"  💰 Income alerts        : {alert_counts['INCOME']}")
print(f"  📦 Total alerts stored  : {r.llen('alerts')}")

print("\n=== ALERTS STORED IN REDIS ===")
alerts = r.lrange("alerts", 0, -1)
for a in alerts:
    parsed = json.loads(a)
    print(f"  {parsed['level']} | {parsed['time']} | {parsed['message']}")

print("\n✅ Pipeline complete — Flink-style stream processing done!")