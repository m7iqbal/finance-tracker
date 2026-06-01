import os
import json
import time
import redis
from datetime import datetime

os.environ["PYFLINK_PYTHON"] = r"C:\Users\iQbalhoran\AppData\Local\Programs\Python\Python311\python.exe"

try:
    from pyflink.datastream import StreamExecutionEnvironment
    from pyflink.common import Types
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    print("✅ Real PyFlink loaded")
except Exception:
    print("⚠️  Running simulation mode")

print("=" * 55)
print("   WEEK 2 DAY 1 — ALL CHALLENGES")
print("=" * 55)

# --- REDIS ---
r = redis.Redis(host="localhost", port=6379, decode_responses=True)
r.delete("alerts")

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

# ── CHALLENGE 2: Priority helper function ───────────────────────
def get_priority(amount):
    abs_amount = abs(amount)
    if abs_amount >= 200:
        return "HIGH"
    elif abs_amount >= 100:
        return "MEDIUM"
    else:
        return "LOW"

# ── TRANSFORM FUNCTIONS (with priority added) ───────────────────
def check_large_expense(t):
    if t["amount"] < -100:
        priority = get_priority(t["amount"])
        return {
            "type":     "LARGE_EXPENSE",
            "priority": priority,
            "level":    f"🚨 {priority}",
            "message":  f"Large expense: {t['description']} — RM {abs(t['amount']):.2f}",
            "time":     datetime.now().strftime("%H:%M:%S")
        }
    return None

def check_shopping(t):
    if t["category"] == "Shopping" and t["amount"] < 0:
        priority = get_priority(t["amount"])
        return {
            "type":     "SHOPPING",
            "priority": priority,
            "level":    f"🛍️  {priority}",
            "message":  f"Shopping: {t['description']} — RM {abs(t['amount']):.2f}",
            "time":     datetime.now().strftime("%H:%M:%S")
        }
    return None

def check_income(t):
    if t["amount"] > 0:
        return {
            "type":     "INCOME",
            "priority": "INFO",
            "level":    "💰 INFO",
            "message":  f"Income received: {t['description']} — RM {t['amount']:.2f}",
            "time":     datetime.now().strftime("%H:%M:%S")
        }
    return None

# ── CHALLENGE 1: Food overspend rule ────────────────────────────
def check_food_overspend(t):
    if t["category"] == "Food" and t["amount"] < -50:
        return {
            "type":     "FOOD_OVERSPEND",
            "priority": "LOW",
            "level":    "🍔 LOW",
            "message":  f"Food overspend: {t['description']} — RM {abs(t['amount']):.2f} exceeds RM50",
            "time":     datetime.now().strftime("%H:%M:%S")
        }
    return None

def save_to_redis(alert):
    if alert:
        r.rpush("alerts", json.dumps(alert))

# ── CHALLENGE 3: Summary printer ────────────────────────────────
def print_summary(alert_counts, total_stored):
    print("\n" + "=" * 55)
    print("   ALERT RULES SUMMARY")
    print("=" * 55)
    print(f"  {'Rule':<22} {'Count':>5}   {'Status'}")
    print(f"  {'-' * 45}")

    rules = {
        "🚨 Large Expense":   alert_counts["LARGE_EXPENSE"],
        "🛍️  Shopping":        alert_counts["SHOPPING"],
        "💰 Income":          alert_counts["INCOME"],
        "🍔 Food Overspend":  alert_counts["FOOD_OVERSPEND"],
    }

    for rule, count in rules.items():
        status = "🔴 FIRED" if count > 0 else "⚪ SILENT"
        print(f"  {rule:<22} {count:>5}   {status}")

    print(f"  {'-' * 45}")
    print(f"  {'TOTAL ALERTS':<22} {total_stored:>5}")

# ── STREAM PROCESSING ───────────────────────────────────────────
print("\n⚡ Stream started...\n")

alert_counts = {
    "LARGE_EXPENSE": 0,
    "SHOPPING":      0,
    "INCOME":        0,
    "FOOD_OVERSPEND": 0
}

# 4 rules now instead of 3
all_rules = [
    check_large_expense,
    check_shopping,
    check_income,
    check_food_overspend   # ← Challenge 1 added here
]

for t in transactions:
    time.sleep(0.3)
    print(f"📥 [{datetime.now().strftime('%H:%M:%S')}] "
          f"{t['description']:15} RM {t['amount']:>10.2f}")

    for rule in all_rules:
        alert = rule(t)
        if alert:
            print(f"   └─ {alert['level']:12} {alert['message']}")
            save_to_redis(alert)
            alert_counts[alert["type"]] += 1

# ── REDIS VERIFICATION ──────────────────────────────────────────
print("\n=== ALERTS STORED IN REDIS ===")
alerts = r.lrange("alerts", 0, -1)
for a in alerts:
    parsed = json.loads(a)
    print(f"  {parsed['level']:12} | {parsed['time']} | {parsed['message']}")

# ── CHALLENGE 3: Print summary ──────────────────────────────────
print_summary(alert_counts, r.llen("alerts"))

print("\n✅ All 3 challenges complete!")