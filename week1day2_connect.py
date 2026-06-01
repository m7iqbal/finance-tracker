import psycopg2

# Connect to your database
conn = psycopg2.connect(
    host="localhost",
    database="finance_tracker",
    user="postgres",
    password="123424722599189"  # ← replace this
)

cursor = conn.cursor()

# --- Query 1: Spending by category ---
cursor.execute("""
    SELECT category, SUM(ABS(amount)) AS total_spent
    FROM transactions
    WHERE amount < 0
    GROUP BY category
    ORDER BY total_spent DESC
""")

rows = cursor.fetchall()

print("=== SPENDING BY CATEGORY (from PostgreSQL) ===")
for row in rows:
    print(f"{row[0]:15} : RM {row[1]:.2f}")

# --- Query 2: Net balance ---
cursor.execute("""
    SELECT
        SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS income,
        SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) AS expenses
    FROM transactions
""")

result = cursor.fetchone()
income   = result[0]
expenses = result[1]

print("\n=== SUMMARY (from PostgreSQL) ===")
print(f"Total Income:   RM {income:.2f}")
print(f"Total Expenses: RM {expenses:.2f}")
print(f"Net Balance:    RM {income + expenses:.2f}")

cursor.close()
conn.close()
print("\n✅ Database connection closed.")