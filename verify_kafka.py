# Create verify_kafka.py
import redis
import json

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

print("=== KAFKA PIPELINE RESULTS ===")
print(f"Total processed: {r.get('kafka_total_processed')}")
print(f"Total alerts:    {r.llen('kafka_alerts')}")

print("\n=== ALERTS FROM KAFKA ===")
alerts = r.lrange("kafka_alerts", 0, -1)
for a in alerts:
    parsed = json.loads(a)
    print(f"  {parsed['level']:6} | {parsed['timestamp']} | {parsed['message']}")