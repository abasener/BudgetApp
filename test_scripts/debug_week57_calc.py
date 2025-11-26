import sqlite3

# Connect to database
conn = sqlite3.connect('budget_app.db')
cursor = conn.cursor()

# Get Week 57 data
cursor.execute("SELECT week_number, start_date, end_date, running_total FROM weeks WHERE week_number = 57")
week57 = cursor.fetchone()
week_num, start_date, end_date, running_total = week57
print(f"Week {week_num}: {start_date} to {end_date}")
print(f"running_total: ${float(running_total):.2f}")
print()

# Get ALL transactions in Week 57's date range
cursor.execute("""
    SELECT id, transaction_type, amount, description, date, week_number
    FROM transactions
    WHERE date >= ? AND date <= ?
    ORDER BY date, id
""", (start_date, end_date))

print("=== ALL TRANSACTIONS IN DATE RANGE ===")
transactions = cursor.fetchall()

spending_total = 0
rollover_income = 0
rollover_deficit = 0

for t in transactions:
    tx_id, tx_type, amount, desc, date, week_num_tx = t
    print(f"ID {tx_id}: {tx_type:12} ${float(amount):8.2f} week={week_num_tx} - {desc}")

    # Check if it's spending (excluding allocations)
    is_allocation = desc and "allocation" in desc.lower()
    if tx_type == "spending" and not is_allocation:
        spending_total += float(amount)
        print(f"  -> SPENDING: ${float(amount):.2f}")

    # Check if it's rollover income
    if tx_type == "rollover" and float(amount) > 0:
        rollover_income += float(amount)
        print(f"  -> ROLLOVER IN: ${float(amount):.2f}")

    # Check if it's rollover deficit
    if tx_type == "rollover" and float(amount) < 0:
        rollover_deficit += abs(float(amount))
        print(f"  -> ROLLOVER OUT: ${float(amount):.2f}")

print()
print("=== CALCULATION ===")
print(f"base_allocation (running_total): ${float(running_total):.2f}")
print(f"rollover_income: ${rollover_income:.2f}")
print(f"rollover_deficit: ${rollover_deficit:.2f}")
print(f"Starting = base + rollover_in - rollover_out")
print(f"Starting = ${float(running_total):.2f} + ${rollover_income:.2f} - ${rollover_deficit:.2f}")
starting = float(running_total) + rollover_income - rollover_deficit
print(f"Starting = ${starting:.2f}")
print()
print(f"total_spent: ${spending_total:.2f}")
print(f"Current = Starting - Spent")
print(f"Current = ${starting:.2f} - ${spending_total:.2f}")
print(f"Current = ${starting - spending_total:.2f}")

conn.close()
