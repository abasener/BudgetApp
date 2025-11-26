import sqlite3

conn = sqlite3.connect('budget_app.db')
cursor = conn.cursor()

# Get accounts
cursor.execute('SELECT id, name, starting_balance FROM accounts')
print('=== ACCOUNTS ===')
accounts = cursor.fetchall()
for a in accounts:
    print(f'ID {a[0]}: {a[1]} - Starting Balance: ${float(a[2]):.2f}')

# Get Emergency Fund transactions
print('\n=== EMERGENCY FUND TRANSACTIONS (oldest first) ===')
cursor.execute('''
    SELECT id, amount, description, date, running_balance
    FROM transactions
    WHERE account_id = 1
    ORDER BY date ASC, id ASC
    LIMIT 10
''')
for t in cursor.fetchall():
    running = float(t[4]) if t[4] is not None else None
    if running is not None:
        print(f'ID {t[0]}: ${float(t[1]):8.2f} - {t[2][:50]:50} Date: {t[3]} Running: ${running:.2f}')
    else:
        print(f'ID {t[0]}: ${float(t[1]):8.2f} - {t[2][:50]:50} Date: {t[3]} Running: None')

conn.close()
