import sqlite3

# Connect to database
conn = sqlite3.connect('budget_app.db')
cursor = conn.cursor()

print("=== TESTING WEEK DISPLAY LOGIC ===\n")

for week_num in [57, 58]:
    # Get week data
    cursor.execute("SELECT week_number, start_date, end_date, running_total FROM weeks WHERE week_number = ?", (week_num,))
    week = cursor.fetchone()
    week_number, start_date, end_date, running_total = week

    print(f"WEEK {week_number} ({start_date} to {end_date})")
    print(f"Base allocation (running_total): ${float(running_total):.2f}")

    # Get transactions BY WEEK_NUMBER (new way)
    cursor.execute("""
        SELECT id, transaction_type, amount, description
        FROM transactions
        WHERE week_number = ?
        ORDER BY date, id
    """, (week_num,))

    transactions = cursor.fetchall()

    spending_total = 0
    rollover_in = 0
    rollover_out = 0

    for t in transactions:
        tx_id, tx_type, amount, desc = t

        # Count spending (excluding allocations)
        is_allocation = desc and "allocation" in desc.lower()
        if tx_type == "spending" and not is_allocation:
            spending_total += float(amount)

        # Count rollover IN (positive)
        if tx_type == "rollover" and float(amount) > 0:
            rollover_in += float(amount)

        # Count rollover OUT (negative)
        if tx_type == "rollover" and float(amount) < 0:
            rollover_out += abs(float(amount))

    starting = float(running_total) + rollover_in - rollover_out
    current = starting - spending_total

    print(f"  Rollover IN: ${rollover_in:.2f}")
    print(f"  Rollover OUT: ${rollover_out:.2f}")
    print(f"  Starting: ${starting:.2f}")
    print(f"  Spending: ${spending_total:.2f}")
    print(f"  Current: ${current:.2f}")
    print()

print("=== EXPECTED VALUES ===")
print("Week 57:")
print("  Starting: $454.46 (just base, no rollover in)")
print("  Current: $454.46 - $141.70 = $312.76")
print()
print("Week 58:")
print("  Starting: $454.46 + $312.76 = $767.22")
print("  Current: $767.22 - $0.00 = $767.22")

conn.close()
