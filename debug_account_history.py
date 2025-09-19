"""
Debug AccountHistory to find why running totals are wrong
"""

from datetime import date, timedelta
from models import get_db, create_tables, drop_tables
from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor


def debug_account_history():
    """Debug AccountHistory step by step"""

    # Fresh database for testing
    drop_tables()
    create_tables()

    tm = TransactionManager()
    processor = PaycheckProcessor()

    print("=== Debugging AccountHistory ===")

    # Create Emergency Fund account
    emergency_fund = tm.add_account(
        name="Emergency Fund",
        goal_amount=5000.0,
        auto_save_amount=300.0,
        is_default_save=True,
        initial_balance=1000.0
    )

    print(f"Initial Emergency Fund: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Check initial history
    print(f"\n--- Initial History ---")
    history = emergency_fund.get_account_history(tm.db)
    for i, entry in enumerate(history):
        tx_desc = f" ({entry.transaction.description})" if entry.transaction else ""
        print(f"  {i+1}. ID={entry.id}, TX_ID={entry.transaction_id}, {entry.transaction_date}: ${entry.change_amount:+.2f} = ${entry.running_total:.2f}{tx_desc}")

    # First paycheck
    print(f"\n--- First Paycheck ---")
    today = date.today()
    paycheck_date = today - timedelta(days=1)

    split = processor.process_new_paycheck(
        paycheck_amount=4625.0,
        paycheck_date=paycheck_date,
        week_start_date=paycheck_date
    )

    print(f"Emergency Fund after paycheck: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Check history after paycheck
    print(f"\n--- History After Paycheck ---")
    history = emergency_fund.get_account_history(tm.db)
    for i, entry in enumerate(history):
        tx_desc = f" ({entry.transaction.description})" if entry.transaction else ""
        print(f"  {i+1}. ID={entry.id}, TX_ID={entry.transaction_id}, {entry.transaction_date}: ${entry.change_amount:+.2f} = ${entry.running_total:.2f}{tx_desc}")

    # Add Week 1 spending (triggers rollover)
    print(f"\n--- Week 1 Spending (triggers rollover) ---")
    tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 1,
        "amount": 150.0,
        "date": paycheck_date + timedelta(days=1),
        "description": "Groceries",
        "category": "Food",
        "include_in_analytics": True
    })

    print(f"Emergency Fund after Week 1 spending: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Check history after Week 1 rollover
    print(f"\n--- History After Week 1 Rollover ---")
    history = emergency_fund.get_account_history(tm.db)
    for i, entry in enumerate(history):
        tx_desc = f" ({entry.transaction.description})" if entry.transaction else ""
        print(f"  {i+1}. ID={entry.id}, TX_ID={entry.transaction_id}, {entry.transaction_date}: ${entry.change_amount:+.2f} = ${entry.running_total:.2f}{tx_desc}")

    # Add Week 2 spending
    print(f"\n--- Week 2 Spending ---")
    tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 2,
        "amount": 200.0,
        "date": paycheck_date + timedelta(days=8),
        "description": "Dining",
        "category": "Entertainment",
        "include_in_analytics": True
    })

    print(f"Emergency Fund after Week 2 spending: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Check history after Week 2 (should be same as before)
    print(f"\n--- History After Week 2 Spending (should be unchanged) ---")
    history = emergency_fund.get_account_history(tm.db)
    for i, entry in enumerate(history):
        tx_desc = f" ({entry.transaction.description})" if entry.transaction else ""
        print(f"  {i+1}. ID={entry.id}, TX_ID={entry.transaction_id}, {entry.transaction_date}: ${entry.change_amount:+.2f} = ${entry.running_total:.2f}{tx_desc}")

    # Second paycheck (triggers Week 2 rollover to savings)
    print(f"\n--- Second Paycheck (triggers Week 2 rollover) ---")
    next_paycheck_date = today + timedelta(days=14)

    print(f"Emergency Fund BEFORE second paycheck: ${emergency_fund.get_current_balance(tm.db):.2f}")

    split2 = processor.process_new_paycheck(
        paycheck_amount=4625.0,
        paycheck_date=next_paycheck_date,
        week_start_date=next_paycheck_date
    )

    print(f"Emergency Fund AFTER second paycheck: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Check final history
    print(f"\n--- Final History (THE PROBLEM IS HERE) ---")
    history = emergency_fund.get_account_history(tm.db)
    for i, entry in enumerate(history):
        tx_desc = f" ({entry.transaction.description})" if entry.transaction else ""
        print(f"  {i+1}. ID={entry.id}, TX_ID={entry.transaction_id}, {entry.transaction_date}: ${entry.change_amount:+.2f} = ${entry.running_total:.2f}{tx_desc}")

    # Manual calculation to verify what the balance should be
    print(f"\n--- Manual Balance Verification ---")
    manual_balance = 0.0
    for i, entry in enumerate(history):
        manual_balance += entry.change_amount
        expected_running_total = manual_balance
        actual_running_total = entry.running_total
        match = "✓" if abs(expected_running_total - actual_running_total) < 0.01 else "✗"
        print(f"  {i+1}. ${entry.change_amount:+.2f} -> Expected: ${expected_running_total:.2f}, Actual: ${actual_running_total:.2f} {match}")

    print(f"\nManual total: ${manual_balance:.2f}")
    print(f"get_current_balance(): ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Check for duplicate transactions
    print(f"\n--- Check for Duplicate Transactions ---")
    all_transactions = tm.db.query(tm.Transaction).filter(
        tm.Transaction.account_id == emergency_fund.id
    ).all()

    print(f"Total transactions affecting Emergency Fund: {len(all_transactions)}")
    for tx in all_transactions:
        print(f"  TX_ID={tx.id}: {tx.transaction_type}, ${tx.amount:.2f}, {tx.date}, {tx.description}")

    print("\n=== AccountHistory Debug Complete ===")

    processor.close()
    tm.close()


if __name__ == "__main__":
    debug_account_history()