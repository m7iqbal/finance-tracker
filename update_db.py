import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="finance_tracker",
    user="postgres",
    password="123424722599189"
)
cursor = conn.cursor()

# Clear old data
cursor.execute("DELETE FROM transactions")

# Insert new data
transactions = [
    ('2026-05-07', 'Salary',       'Income',         3830.00),
    ('2026-05-10', 'PTPTN',        'Loan',           -181.70),
    ('2026-05-07', 'Rumah Sewa',   'Commitment',      -56.00),
    ('2026-05-07', 'Rumah Family', 'Commitment',     -100.00),
    ('2026-05-05', 'ASB',          'Loan',           -424.00),
    ('2026-05-10', 'Medical',      'Commitment',     -200.00),
    ('2026-05-07', 'Netflix',      'Entertainment',   -63.00),
    ('2026-05-07', 'Setel',        'Transport',      -100.00),
    ('2026-05-07', 'Shoes',        'Shopping',       -200.00),
    ('2026-05-07', 'Zakat',        'Commitment',      -69.00),
    ('2026-05-07', 'Parents',      'Commitment',     -250.00),
    ('2026-05-07', 'Prepaid',      'Commitment',      -75.00),
    ('2026-05-07', 'Scooter',      'Transport',      -100.00),
    ('2026-05-07', 'Travel',       'Tabung',         -200.00),
    ('2026-05-07', 'Toiletries',   'Shopping',       -100.00),
    ('2026-05-07', 'Facial',       'Tabung',         -100.00),
    ('2026-05-07', 'Car',          'Loan',          -1300.00),
]

cursor.executemany("""
    INSERT INTO transactions (date, description, category, amount)
    VALUES (%s, %s, %s, %s)
""", transactions)

conn.commit()
cursor.close()
conn.close()
print(f"✅ PostgreSQL updated with {len(transactions)} transactions")