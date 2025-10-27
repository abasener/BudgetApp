"""
Fix the starting balance issue in savings account:
1. Update starting balance entry date to be before all transactions
2. Recalculate all running totals
"""

from models import get_db
from models.account_history import AccountHistory, AccountHistoryManager
from datetime import date

db = get_db()

print("=== FIXING SAVINGS ACCOUNT STARTING BALANCE ===\n")

# Get the starting balance entry
starting_entry = db.query(AccountHistory).filter(
    AccountHistory.account_id == 1,
    AccountHistory.account_type == 'savings',
    AccountHistory.transaction_id == None
).first()

if not starting_entry:
    print("ERROR: No starting balance entry found!")
    exit(1)

print(f"Found starting balance entry:")
print(f"  ID: {starting_entry.id}")
print(f"  Amount: ${starting_entry.change_amount:.2f}")
print(f"  Current date: {starting_entry.transaction_date}")

# Get the earliest transaction date
earliest_tx = db.query(AccountHistory).filter(
    AccountHistory.account_id == 1,
    AccountHistory.account_type == 'savings',
    AccountHistory.transaction_id != None
).order_by(AccountHistory.transaction_date.asc(), AccountHistory.id.asc()).first()

if earliest_tx:
    print(f"\nEarliest transaction date: {earliest_tx.transaction_date}")

    # Set starting balance date to one day before earliest transaction
    new_date = date(2024, 9, 21)  # Day before Sept 22, 2024
    print(f"Setting starting balance date to: {new_date}")

    starting_entry.transaction_date = new_date
    db.flush()

    print("\n=== RECALCULATING ALL RUNNING TOTALS ===")
    manager = AccountHistoryManager(db)
    manager.recalculate_account_history(1, 'savings')

    db.commit()

    print("\n=== VERIFICATION ===")
    # Show first few entries
    entries = db.query(AccountHistory).filter(
        AccountHistory.account_id == 1,
        AccountHistory.account_type == 'savings'
    ).order_by(AccountHistory.transaction_date.asc(), AccountHistory.id.asc()).limit(5).all()

    for entry in entries:
        tx_id = entry.transaction_id if entry.transaction_id else "START"
        desc = entry.description[:30] if entry.description else "(transaction)"
        print(f"ID {entry.id}: tx={tx_id:6} Change: ${entry.change_amount:8.2f} Running: ${entry.running_total:10.2f} - {desc}")

    print("\n✓ Starting balance fixed and all running totals recalculated!")
else:
    print("No transactions found - nothing to fix")

db.close()
