import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('budget_app.db')
cursor = conn.cursor()

# Get current weeks
cursor.execute("""
    SELECT week_number, start_date, end_date, running_total, rollover_applied
    FROM weeks
    ORDER BY week_number DESC
    LIMIT 4
""")

print("=== WEEKS ===")
weeks = cursor.fetchall()
for w in weeks:
    print(f"Week {w[0]}: {w[1]} to {w[2]}")
    print(f"  running_total (base allocation): ${w[3]:.2f}")
    print(f"  rollover_applied: {w[4]}")
    print()

# Get transactions for the last 2 weeks
if len(weeks) >= 2:
    week1_num = weeks[1][0]
    week2_num = weeks[0][0]

    print(f"\n=== TRANSACTIONS FOR WEEK {week1_num} ===")
    cursor.execute("""
        SELECT id, transaction_type, amount, description, date
        FROM transactions
        WHERE week_number = ?
        ORDER BY date, id
    """, (week1_num,))

    for t in cursor.fetchall():
        print(f"ID {t[0]}: {t[1]:12} ${t[2]:8.2f} - {t[3]} ({t[4]})")

    print(f"\n=== TRANSACTIONS FOR WEEK {week2_num} ===")
    cursor.execute("""
        SELECT id, transaction_type, amount, description, date
        FROM transactions
        WHERE week_number = ?
        ORDER BY date, id
    """, (week2_num,))

    for t in cursor.fetchall():
        print(f"ID {t[0]}: {t[1]:12} ${t[2]:8.2f} - {t[3]} ({t[4]})")

# Get paycheck info
cursor.execute("""
    SELECT amount, date
    FROM paychecks
    ORDER BY date DESC
    LIMIT 1
""")
paycheck = cursor.fetchone()
if paycheck:
    print(f"\n=== LATEST PAYCHECK ===")
    print(f"Amount: ${paycheck[0]:.2f} on {paycheck[1]}")

conn.close()
