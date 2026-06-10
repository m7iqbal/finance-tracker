"""
kafka_producer.py
==================
Simulates real-time transaction events being sent to Kafka.
In production this would be connected to a payment gateway API.

Run this first, then run kafka_consumer.py in another terminal.
"""

import json
import time
from datetime import datetime
from kafka import KafkaProducer

# --- CONNECT TO KAFKA ---
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print("✅ Kafka Producer connected")
print("📤 Sending transactions to topic: finance-transactions\n")

# --- TRANSACTIONS TO SEND ---
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

# --- SEND EACH TRANSACTION ---
for t in transactions:
    # Add timestamp to each transaction
    t["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Send to Kafka topic
    producer.send("finance-transactions", value=t)

    print(f"📤 [{t['timestamp']}] Sent: "
          f"{t['description']:15} RM {t['amount']:>10.2f}")

    time.sleep(1)  # 1 second between each — simulates real-time

producer.flush()  # make sure all messages are sent
producer.close()
print("\n✅ All transactions sent to Kafka!")