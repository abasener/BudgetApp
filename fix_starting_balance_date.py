"""
Fix starting balance date and recalculate all running totals
"""
import sqlite3
from datetime import date

conn = sqlite3.connect('budget_app.db')
cursor = conn.cursor()

print("=== FIXING STARTING BALANCE DATE ===\n")

# Get starting balance entry
cursor.execute('''
    SELECT id, change_amount, transaction_date
    FROM account_history
    WHERE account_id = 1 AND account_type = 'savings' AND transaction_id IS NULL
''')
starting = cursor.fetchone()

if not starting:
    print("ERROR: No starting balance found!")
    exit(1)

print(f"Starting balance: ID {starting[0]}, Amount: ${float(starting[1]):.2f}, Date: {starting[2]}")

# Get earliest transaction
cursor.execute('''
    SELECT MIN(transaction_date)
    FROM account_history
    WHERE account_id = 1 AND account_type = 'savings' AND transaction_id IS NOT NULL
''')
earliest_date = cursor.fetchone()[0]
print(f"Earliest transaction date: {earliest_date}")

# Set starting balance to day before earliest transaction
new_date = '2024-09-21'  # Day before 2024-09-22
print(f"Setting starting balance date to: {new_date}")

cursor.execute('''
    UPDATE account_history
    SET transaction_date = ?
    WHERE id = ?
''', (new_date, starting[0]))

print(f"\n=== RECALCULATING ALL RUNNING TOTALS ===")

# Get all entries in chronological order
cursor.execute('''
    SELECT id, change_amount
    FROM account_history
    WHERE account_id = 1 AND account_type = 'savings'
    ORDER BY transaction_date ASC, id ASC
''')

entries = cursor.fetchall()
running_total = 0.0

for entry_id, change_amount in entries:
    running_total += float(change_amount)
    cursor.execute('''
        UPDATE account_history
        SET running_total = ?
        WHERE id = ?
    ''', (running_total, entry_id))

conn.commit()

print(f"Updated {len(entries)} entries")

# Verify
print(f"\n=== VERIFICATION (first 5 entries) ===")
cursor.execute('''
    SELECT id, transaction_id, change_amount, running_total, transaction_date
    FROM account_history
    WHERE account_id = 1 AND account_type = 'savings'
    ORDER BY transaction_date ASC, id ASC
    LIMIT 5
''')

for h in cursor.fetchall():
    tx_id = h[1] if h[1] else "START"
    print(f"ID {h[0]:3} tx={str(tx_id):6} change=${float(h[2]):9.2f} running=${float(h[3]):10.2f} date={h[4]}")

print("\nDone! Starting balance is now first entry and all running totals updated.")

conn.close()
