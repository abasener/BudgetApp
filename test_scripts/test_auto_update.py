"""
Test that adding a transaction in the past automatically updates all subsequent running totals
"""
from models import get_db
from models.account_history import AccountHistory, AccountHistoryManager
from datetime import date

db = get_db()
manager = AccountHistoryManager(db)

print("=== TESTING AUTO-UPDATE OF RUNNING TOTALS ===\n")

# Get current first few entries
print("BEFORE adding new transaction:")
entries_before = db.query(AccountHistory).filter(
    AccountHistory.account_id == 1,
    AccountHistory.account_type == 'savings'
).order_by(AccountHistory.transaction_date, AccountHistory.id).limit(5).all()

for e in entries_before:
    tx_id = e.transaction_id if e.transaction_id else "START"
    print(f"ID {e.id:3} tx={str(tx_id):6} change=${e.change_amount:8.2f} running=${e.running_total:10.2f} date={e.transaction_date}")

# Add a test transaction dated 2024-10-01 (between first and second transaction)
test_date = date(2024, 10, 1)
test_amount = 100.00

print(f"\nAdding test transaction: ${test_amount:.2f} on {test_date}")
print("This should update all running totals from this date forward...")

try:
    # Create a dummy transaction (we'll clean it up)
    from models.transactions import Transaction
    test_tx = Transaction(
        transaction_type='saving',
        week_number=1,
        amount=test_amount,
        date=test_date,
        description='TEST TRANSACTION - WILL BE DELETED',
        account_id=1
    )
    db.add(test_tx)
    db.flush()

    # Add history entry (this should trigger auto-update)
    manager.add_transaction_change(
        account_id=1,
        account_type='savings',
        transaction_id=test_tx.id,
        change_amount=test_amount,
        transaction_date=test_date
    )

    db.commit()

    print("\nAFTER adding new transaction:")
    entries_after = db.query(AccountHistory).filter(
        AccountHistory.account_id == 1,
        AccountHistory.account_type == 'savings'
    ).order_by(AccountHistory.transaction_date, AccountHistory.id).limit(6).all()

    for e in entries_after:
        tx_id = e.transaction_id if e.transaction_id else "START"
        is_test = " ← TEST TX" if e.transaction_id == test_tx.id else ""
        print(f"ID {e.id:3} tx={str(tx_id):6} change=${e.change_amount:8.2f} running=${e.running_total:10.2f} date={e.transaction_date}{is_test}")

    print("\n=== VERIFICATION ===")
    # Check that entries after the test transaction increased by $100
    entry_152_before = [e for e in entries_before if e.id == 152][0]
    entry_152_after = [e for e in entries_after if e.id == 152][0]

    diff = entry_152_after.running_total - entry_152_before.running_total
    print(f"Entry ID 152 running total change: ${diff:.2f}")

    if abs(diff - test_amount) < 0.01:
        print("✓ AUTO-UPDATE WORKING! Subsequent entries updated correctly.")
    else:
        print(f"✗ AUTO-UPDATE FAILED! Expected ${test_amount:.2f}, got ${diff:.2f}")

    # Clean up test transaction
    print("\nCleaning up test transaction...")
    manager.delete_transaction_change(test_tx.id)
    db.delete(test_tx)
    db.commit()
    print("Test transaction removed.")

except Exception as e:
    print(f"ERROR: {e}")
    db.rollback()

db.close()
