"""
kafka_consumer.py
==================
Reads transactions from Kafka topic in real time.
Applies alert rules and stores results in Redis.

Run this in a separate terminal AFTER kafka_producer.py starts.
"""

import json
import redis
from datetime import datetime
from kafka import KafkaConsumer
from finance_functions import (
    check_large_expense,
    check_shopping,
    check_income,
    check_food_overspend
)

# --- CONNECT TO KAFKA ---
consumer = KafkaConsumer(
    "finance-transactions",
    bootstrap_servers=["localhost:9092"],
    auto_offset_reset="earliest",      # read from beginning
    enable_auto_commit=True,
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)

# --- CONNECT TO REDIS ---
r = redis.Redis(host="localhost", port=6379, decode_responses=True)
r.delete("kafka_alerts")   # clear old alerts
r.set("kafka_total_processed", 0)

print("✅ Kafka Consumer connected")
print("✅ Redis connected")
print("👂 Listening for transactions...\n")
print("=" * 55)

# --- ALERT RULES ---
all_rules = [
    check_large_expense,
    check_shopping,
    check_income,
    check_food_overspend
]

alert_counts = {
    "LARGE_EXPENSE":  0,
    "SHOPPING":       0,
    "INCOME":         0,
    "FOOD_OVERSPEND": 0
}

# --- CONSUME MESSAGES ---
for message in consumer:
    t = message.value  # the transaction dict

    # Update counter
    r.incr("kafka_total_processed")
    total = int(r.get("kafka_total_processed"))

    print(f"📥 [{datetime.now().strftime('%H:%M:%S')}] "
          f"#{total:02d} {t['description']:15} "
          f"RM {t['amount']:>10.2f}")

    # Apply all alert rules
    for rule in all_rules:
        alert = rule(t)
        if alert:
            # Add timestamp and transaction details
            alert["timestamp"] = datetime.now().strftime("%H:%M:%S")
            alert["description"] = t["description"]
            alert["amount"] = t["amount"]

            # Save to Redis
            r.rpush("kafka_alerts", json.dumps(alert))
            alert_counts[alert["type"]] += 1

            print(f"   └─ 🚨 {alert['level']:6} | {alert['message']}")

    # Print summary every 5 transactions
    if total % 5 == 0:
        print(f"\n   📊 Progress: {total} processed | "
              f"Alerts: {sum(alert_counts.values())}\n")