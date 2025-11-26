import sqlite3

conn = sqlite3.connect('budget_app.db')
cursor = conn.cursor()

# Get accounts
cursor.execute('SELECT id, name, is_default_save, goal_amount FROM accounts')
print('=== ACCOUNTS ===')
accounts = cursor.fetchall()
for a in accounts:
    print(f'ID {a[0]}: {a[1]} (Default: {bool(a[2])}) Goal: ${float(a[3]):.2f}')

# Check Emergency Fund account history
print('\n=== EMERGENCY FUND ACCOUNT HISTORY (oldest first) ===')
cursor.execute('''
    SELECT id, transaction_id, change_amount, running_total, transaction_date, description
    FROM account_history
    WHERE account_id = 1 AND account_type = 'savings'
    ORDER BY transaction_date ASC, id ASC
    LIMIT 10
''')

for h in cursor.fetchall():
    tx_id = h[1] if h[1] else "NO_TX"
    desc = h[5] if h[5] else "(from transaction)"
    print(f'ID {h[0]}: tx={tx_id:6} Change: ${float(h[2]):8.2f} Running: ${float(h[3]):10.2f} Date: {h[4]} - {desc}')

# Get the starting balance entry
cursor.execute('''
    SELECT id, change_amount, running_total, transaction_date, description
    FROM account_history
    WHERE account_id = 1 AND account_type = 'savings' AND transaction_id IS NULL
    ORDER BY transaction_date ASC, id ASC
    LIMIT 1
''')
starting = cursor.fetchone()
if starting:
    print(f'\n=== STARTING BALANCE ENTRY ===')
    print(f'ID {starting[0]}: ${float(starting[1]):.2f} on {starting[3]} - {starting[4]}')
else:
    print('\n=== NO STARTING BALANCE ENTRY FOUND ===')

conn.close()
