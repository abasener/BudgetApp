import sqlite3

conn = sqlite3.connect('budget_app.db')
cursor = conn.cursor()

print("=== ALL ACCOUNT HISTORY ENTRIES (chronological) ===")
cursor.execute('''
    SELECT id, transaction_id, account_id, account_type, change_amount, running_total, transaction_date, description
    FROM account_history
    WHERE account_id = 1 AND account_type = 'savings'
    ORDER BY transaction_date ASC, id ASC
    LIMIT 15
''')

for h in cursor.fetchall():
    tx_id = str(h[1]) if h[1] else "NULL"
    desc = h[7] if h[7] else "(from tx)"
    print(f'ID {h[0]:3} tx={tx_id:6} acct={h[2]} type={h[3]:8} change=${float(h[4]):9.2f} running=${float(h[5]):10.2f} date={h[6]} - {desc[:40]}')

print("\n=== STARTING BALANCE ENTRIES (transaction_id IS NULL) ===")
cursor.execute('''
    SELECT id, account_id, change_amount, running_total, transaction_date, description
    FROM account_history
    WHERE account_id = 1 AND account_type = 'savings' AND transaction_id IS NULL
''')

result = cursor.fetchall()
if result:
    for h in result:
        print(f'ID {h[0]}: acct={h[1]} change=${float(h[2]):.2f} running=${float(h[3]):.2f} date={h[4]} - {h[5]}')
else:
    print("NO STARTING BALANCE ENTRY EXISTS")

conn.close()
