from pymongo import MongoClient
from datetime import datetime

# --- CONNECT ---
client = MongoClient("mongodb://localhost:27017/")
db = client["finance_tracker"]
collection = db["transactions"]

# --- Challenge 1: Find by tag ---
print("=== CHALLENGE 1: SAVINGS TRANSACTIONS ===")
savings = collection.find({"tags": "savings"})
for doc in savings:
    print(f"{doc['description']:20} | RM {doc['amount']:.2f}")

# --- Challenge 2: Amount range ---
print("\n=== CHALLENGE 2: EXPENSES BETWEEN RM50 - RM200 ===")
range_expenses = collection.find({
    "amount": {
        "$gte": -200,
        "$lte": -50
    }
})
for doc in range_expenses:
    print(f"{doc['description']:20} | RM {doc['amount']:.2f}")

# --- Challenge 3: Insert creative document ---
print("\n=== CHALLENGE 3: INSERT NEW TRANSACTION ===")
new_transaction = {
    "date": datetime(2026, 5, 17),
    "description": "Mamak TBS",
    "category": "Food",
    "amount": -25.50,
    "note": "Dinner with friends",
    "tags": ["food", "social", "one-time"],
    "order_details": [
        {"item": "Teh Tarik",  "price": 2.50, "qty": 2},
        {"item": "Roti Canai", "price": 1.50, "qty": 3},
        {"item": "Nasi Goreng","price": 8.00, "qty": 1},
    ],
    "location": {
        "name": "Mamak TBS",
        "city": "Johor Bahru",
        "state": "Johor"
    },
    "paid_by": "Touch n Go",
    "split_with": ["Ali", "Abu"],
    "receipt_photo": "receipts/mamak_may17.jpg"
}

result = collection.insert_one(new_transaction)
print(f"✅ Inserted with id: {result.inserted_id}")

# Verify
doc = collection.find_one({"description": "Mamak TBS"})
print(f"\nDescription : {doc['description']}")
print(f"Amount      : RM {doc['amount']:.2f}")
print(f"Paid by     : {doc['paid_by']}")
print(f"Split with  : {doc['split_with']}")
print(f"Order details:")
for item in doc["order_details"]:
    print(f"  - {item['item']:15} x{item['qty']} @ RM {item['price']:.2f}")