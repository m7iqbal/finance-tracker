from pymongo import MongoClient
from datetime import datetime

# --- STEP 2 ---
# --- CONNECT ---
client = MongoClient("mongodb://localhost:27017/")

# Create database (MongoDB creates it automatically when you first use it)
db = client["finance_tracker"]

# Create collection (like a table in SQL)
collection = db["transactions"]

# --- CHECK CONNECTION ---
print("✅ Connected to MongoDB")
print(f"Databases: {client.list_database_names()}")

# --- STEP 3 ---
# --- CLEAR old data first (so we don't duplicate) ---
collection.delete_many({})
print("🗑️ Cleared old data")

# --- INSERT transactions as documents ---
# Notice: MongoDB is flexible — each document can have DIFFERENT fields
# This is the key difference from SQL

transactions = [
    {
        "date": datetime(2026, 5, 7),
        "description": "Salary",
        "category": "Income",
        "amount": 3830.00,
        "note": "Monthly salary from company",    # extra field — SQL can't do this easily
        "tags": ["income", "fixed"]               # array field — SQL can't do this at all
    },
    {
        "date": datetime(2026, 5, 10),
        "description": "PTPTN",
        "category": "Commitment",
        "amount": -181.70,
        "note": "Student loan repayment",
        "tags": ["loan", "fixed", "commitment"],
        "due_day": 10                             # PTPTN specific field
    },
    {
        "date": datetime(2026, 5, 5),
        "description": "ASB",
        "category": "Commitment",
        "amount": -424.00,
        "note": "ASB monthly savings contribution",
        "tags": ["savings", "investment", "fixed"],
        "account_number": "ASB-XXXX"             # ASB specific field
    },
    {
        "date": datetime(2026, 5, 7),
        "description": "Netflix",
        "category": "Entertainment",
        "amount": -63.00,
        "note": "Monthly subscription",
        "tags": ["subscription", "entertainment"],
        "shared_with": ["family"]                # who shares this subscription
    },
    {
        "date": datetime(2026, 5, 7),
        "description": "Setel",
        "category": "Transport",
        "amount": -100.00,
        "note": "Petrol top up",
        "tags": ["petrol", "transport"],
        "liters": 20.5                           # petrol specific field
    },
    {
        "date": datetime(2026, 5, 7),
        "description": "Shoes",
        "category": "Shopping",
        "amount": -200.00,
        "note": "New running shoes",
        "tags": ["clothing", "one-time"],
        "brand": "Nike",                         # shopping specific field
        "receipt_url": "receipts/shoes_may2026.jpg"
    },
    {
        "date": datetime(2026, 5, 7),
        "description": "Parents",
        "category": "Commitment",
        "amount": -250.00,
        "note": "Monthly allowance for parents",
        "tags": ["family", "fixed", "commitment"]
    },
    {
        "date": datetime(2026, 5, 7),
        "description": "Travel",
        "category": "Tabung",
        "amount": -200.00,
        "note": "Saving for year end trip",
        "tags": ["savings", "goal"],
        "goal_target": 3000.00,                  # savings goal specific
        "goal_deadline": "2026-12-31"
    },
]

# Insert all at once
result = collection.insert_many(transactions)
print(f"✅ Inserted {len(result.inserted_ids)} documents")

# --- STEP 4 ---
# --- QUERY 1: Find all documents ---
print("\n=== ALL TRANSACTIONS ===")
for doc in collection.find():
    print(f"{doc['date'].strftime('%Y-%m-%d')} | {doc['description']:20} | RM {doc['amount']:.2f}")

# --- QUERY 2: Find only expenses ---
print("\n=== EXPENSES ONLY ===")
expenses = collection.find({"amount": {"$lt": 0}})
for doc in expenses:
    print(f"{doc['description']:20} | RM {doc['amount']:.2f}")

# --- QUERY 3: Find by category ---
print("\n=== COMMITMENT ONLY ===")
commitment = collection.find({"category": "Commitment"})
for doc in commitment:
    print(f"{doc['description']:20} | RM {doc['amount']:.2f}")

# --- QUERY 4: Find by tag ---
print("\n=== FIXED EXPENSES (tagged 'fixed') ===")
fixed = collection.find({"tags": "fixed"})
for doc in fixed:
    print(f"{doc['description']:20} | RM {doc['amount']:.2f}")

# --- QUERY 5: Total spent (aggregation) ---
print("\n=== TOTAL EXPENSES ===")
pipeline = [
    {"$match": {"amount": {"$lt": 0}}},
    {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
    {"$sort": {"total": 1}}
]
results = collection.aggregate(pipeline)
for r in results:
    print(f"{r['_id']:20} : RM {abs(r['total']):.2f}")

# --- STEP 5 ---
# --- COMPARISON ---
print("\n=== SQL vs MongoDB Syntax ===")

# SQL:    SELECT * FROM transactions WHERE amount < 0
# Mongo:
expenses = collection.find({"amount": {"$lt": 0}})

# SQL:    SELECT * FROM transactions WHERE category = 'Commitment'
# Mongo:
commitment = collection.find({"category": "Commitment"})

# SQL:    SELECT * FROM transactions WHERE amount < -100 AND category = 'Commitment'
# Mongo:
big_commitment = collection.find({
    "amount": {"$lt": -100},
    "category": "Commitment"
})
for doc in big_commitment:
    print(f"{doc['description']:20} | RM {doc['amount']:.2f}")

# --- VERIFY ---
total_docs = collection.count_documents({})
print(f"\n✅ Total documents in MongoDB: {total_docs}")

# Show one document in full to see all fields
print("\n=== SAMPLE DOCUMENT (full) ===")
sample = collection.find_one({"description": "Shoes"})
for key, value in sample.items():
    print(f"  {key}: {value}")