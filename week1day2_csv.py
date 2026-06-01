import csv
from datetime import datetime

transactions = [
    {"date": "2026-05-07", "description": "Salary",      "category": "Income",        "amount":  3830.00},
    {"date": "2026-05-10", "description": "PTPTN",       "category": "Commitment",    "amount":  -181.70},
    {"date": "2026-05-07", "description": "Rumah Sewa",  "category": "Commitment",    "amount": -56.00},
    {"date": "2026-05-07", "description": "Rumah Family","category": "Commitment",    "amount": -100.00},
    {"date": "2026-05-05", "description": "ASB",         "category": "Commitment",    "amount":  -424.00},
    {"date": "2026-05-10", "description": "Medical",     "category": "Commitment",    "amount":  -200.00},
    {"date": "2026-05-07", "description": "Netflix",     "category": "Entertainment", "amount":  -63.00},
    {"date": "2026-05-07", "description": "Setel",       "category": "Transport",     "amount": -100.00},
    {"date": "2026-05-07", "description": "Shoes",       "category": "Shopping",      "amount":  -200.00},
    {"date": "2026-05-07", "description": "Zakat",       "category": "Commitment",    "amount":  -69.00},
    {"date": "2026-05-07", "description": "Parents",     "category": "Commitment",    "amount":  -250.00},
    {"date": "2026-05-07", "description": "Prepaid",     "category": "Commitment",    "amount":  -75.00},
    {"date": "2026-05-07", "description": "Scooter",     "category": "Transport",     "amount":  -100.00},
    {"date": "2026-05-07", "description": "Travel",      "category": "Tabung",        "amount":  -200.00},
    {"date": "2026-05-07", "description": "Toiletries",  "category": "Shopping",      "amount":  -100.00},
    {"date": "2026-05-07", "description": "Facial",      "category": "Tabung",        "amount":  -100.00},
]

# --- WRITE to CSV ---
filename = "transactions.csv"

with open(filename, mode="w", newline="") as file:
    fieldnames = ["date", "description", "category", "amount"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()           # writes the column names
    writer.writerows(transactions) # writes all rows

print(f"✅ Saved {len(transactions)} transactions to {filename}")

# --- READ back from CSV ---
print("\n=== READING FROM CSV ===")

with open(filename, mode="r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(f"{row['date']} | {row['description']:20} | RM {float(row['amount']):.2f}")