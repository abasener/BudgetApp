"""
Complete integration test of the new AccountHistory system
Tests the entire flow from account creation to paycheck processing to bill payments
"""

from datetime import date, timedelta
from models import get_db, create_tables, drop_tables
from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor


def test_complete_integration():
    """Test the complete integrated system"""

    # Fresh database for testing
    drop_tables()
    create_tables()

    tm = TransactionManager()
    processor = PaycheckProcessor()

    print("=== Complete System Integration Test ===")

    # Phase 1: Initial Setup
    print("\n=== Phase 1: Initial Setup ===")

    # Create savings accounts
    emergency_fund = tm.add_account(
        name="Emergency Fund",
        goal_amount=10000.0,
        auto_save_amount=300.0,
        is_default_save=True,
        initial_balance=2500.0
    )

    vacation_fund = tm.add_account(
        name="Vacation Fund",
        goal_amount=3000.0,
        auto_save_amount=100.0,
        is_default_save=False,
        initial_balance=750.0
    )

    car_fund = tm.add_account(
        name="Car Maintenance",
        goal_amount=2000.0,
        auto_save_amount=50.0,
        is_default_save=False,
        initial_balance=400.0
    )

    print(f"Emergency Fund: ${emergency_fund.get_current_balance(tm.db):.2f} / ${emergency_fund.goal_amount:.2f}")
    print(f"Vacation Fund: ${vacation_fund.get_current_balance(tm.db):.2f} / ${vacation_fund.goal_amount:.2f}")
    print(f"Car Fund: ${car_fund.get_current_balance(tm.db):.2f} / ${car_fund.goal_amount:.2f}")

    # Create bills
    rent_bill = tm.add_bill(
        name="Rent",
        bill_type="Housing",
        payment_frequency="monthly",
        typical_amount=1400.0,
        amount_to_save=350.0,
        initial_balance=700.0
    )

    utilities_bill = tm.add_bill(
        name="Utilities",
        bill_type="Housing",
        payment_frequency="monthly",
        typical_amount=200.0,
        amount_to_save=50.0,
        initial_balance=100.0
    )

    insurance_bill = tm.add_bill(
        name="Insurance",
        bill_type="Insurance",
        payment_frequency="monthly",
        typical_amount=300.0,
        amount_to_save=75.0,
        initial_balance=150.0
    )

    print(f"Rent: ${rent_bill.get_current_balance(tm.db):.2f} / ${rent_bill.typical_amount:.2f}")
    print(f"Utilities: ${utilities_bill.get_current_balance(tm.db):.2f} / ${utilities_bill.typical_amount:.2f}")
    print(f"Insurance: ${insurance_bill.get_current_balance(tm.db):.2f} / ${insurance_bill.typical_amount:.2f}")

    # Phase 2: First Paycheck Cycle
    print("\n=== Phase 2: First Paycheck (January 15) ===")

    paycheck1_split = processor.process_new_paycheck(
        paycheck_amount=3000.0,
        paycheck_date=date(2024, 1, 15),
        week_start_date=date(2024, 1, 15)
    )

    print(f"Paycheck Split: {paycheck1_split}")

    # Check balances after first paycheck
    print("\nBalances after first paycheck:")
    print(f"Emergency Fund: ${emergency_fund.get_current_balance(tm.db):.2f}")
    print(f"Vacation Fund: ${vacation_fund.get_current_balance(tm.db):.2f}")
    print(f"Car Fund: ${car_fund.get_current_balance(tm.db):.2f}")
    print(f"Rent: ${rent_bill.get_current_balance(tm.db):.2f}")
    print(f"Utilities: ${utilities_bill.get_current_balance(tm.db):.2f}")
    print(f"Insurance: ${insurance_bill.get_current_balance(tm.db):.2f}")

    # Expected balances after first paycheck:
    # Emergency: 2500 + 300 = 2800
    # Vacation: 750 + 100 = 850
    # Car: 400 + 50 = 450
    # Rent: 700 + 350 = 1050
    # Utilities: 100 + 50 = 150
    # Insurance: 150 + 75 = 225

    # Phase 3: Some Spending and Bill Payments
    print("\n=== Phase 3: Spending and Bill Payments ===")

    # Add some spending transactions
    spending_txs = [
        {
            "transaction_type": "spending",
            "week_number": 1,
            "amount": 120.0,
            "date": date(2024, 1, 18),
            "description": "Groceries",
            "category": "Food",
            "include_in_analytics": True
        },
        {
            "transaction_type": "spending",
            "week_number": 1,
            "amount": 50.0,
            "date": date(2024, 1, 20),
            "description": "Gas",
            "category": "Transportation",
            "include_in_analytics": True
        },
        {
            "transaction_type": "spending",
            "week_number": 2,
            "amount": 85.0,
            "date": date(2024, 1, 25),
            "description": "Dining out",
            "category": "Entertainment",
            "include_in_analytics": True
        }
    ]

    for spending_data in spending_txs:
        spending_tx = tm.add_transaction(spending_data)
        print(f"Added spending: {spending_tx}")

    # Pay some bills
    rent_payment = tm.add_transaction({
        "transaction_type": "bill_pay",
        "week_number": 2,
        "amount": 1400.0,
        "date": date(2024, 1, 30),
        "description": "January rent payment",
        "bill_id": rent_bill.id,
        "bill_type": "Housing"
    })
    print(f"Paid rent: {rent_payment}")

    utilities_payment = tm.add_transaction({
        "transaction_type": "bill_pay",
        "week_number": 2,
        "amount": 200.0,
        "date": date(2024, 1, 31),
        "description": "January utilities payment",
        "bill_id": utilities_bill.id,
        "bill_type": "Housing"
    })
    print(f"Paid utilities: {utilities_payment}")

    # Check balances after spending and payments
    print("\nBalances after spending and bill payments:")
    print(f"Rent: ${rent_bill.get_current_balance(tm.db):.2f}")  # Should be 1050 - 1400 = -350
    print(f"Utilities: ${utilities_bill.get_current_balance(tm.db):.2f}")  # Should be 150 - 200 = -50

    # Phase 4: Second Paycheck Cycle
    print("\n=== Phase 4: Second Paycheck (January 29) ===")

    paycheck2_split = processor.process_new_paycheck(
        paycheck_amount=3000.0,
        paycheck_date=date(2024, 1, 29),
        week_start_date=date(2024, 1, 29)
    )

    print(f"Second Paycheck Split: {paycheck2_split}")

    # Check final balances
    print("\nFinal balances after second paycheck:")
    accounts = tm.get_all_accounts()
    bills = tm.get_all_bills()

    total_savings = 0
    for account in accounts:
        balance = account.get_current_balance(tm.db)
        progress = account.goal_progress_percent
        print(f"{account.name}: ${balance:.2f} / ${account.goal_amount:.2f} ({progress:.1f}%)")
        total_savings += balance

    total_bill_savings = 0
    for bill in bills:
        balance = bill.get_current_balance(tm.db)
        progress = bill.savings_progress_percent
        print(f"{bill.name}: ${balance:.2f} / ${bill.typical_amount:.2f} ({progress:.1f}%)")
        total_bill_savings += balance

    print(f"\nTotal in savings accounts: ${total_savings:.2f}")
    print(f"Total in bill accounts: ${total_bill_savings:.2f}")
    print(f"Total managed funds: ${total_savings + total_bill_savings:.2f}")

    # Phase 5: Test Account History Viewing
    print("\n=== Phase 5: Account History Analysis ===")

    print("\nEmergency Fund transaction history:")
    emergency_history = emergency_fund.get_account_history(tm.db)
    for i, entry in enumerate(emergency_history):
        tx_desc = ""
        if entry.transaction:
            tx_desc = f" ({entry.transaction.description})"
        print(f"  {i+1}. {entry.transaction_date}: ${entry.change_amount:+.2f} = ${entry.running_total:.2f}{tx_desc}")

    print("\nRent Bill transaction history:")
    rent_history = rent_bill.get_account_history(tm.db)
    for i, entry in enumerate(rent_history):
        tx_desc = ""
        if entry.transaction:
            tx_desc = f" ({entry.transaction.description})"
        print(f"  {i+1}. {entry.transaction_date}: ${entry.change_amount:+.2f} = ${entry.running_total:.2f}{tx_desc}")

    # Phase 6: Test Transaction Updates and Deletions
    print("\n=== Phase 6: Transaction Management ===")

    # Update a transaction amount
    print(f"\nBefore update - Emergency Fund: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Find a savings transaction to update
    emergency_transactions = tm.get_transactions_by_account(emergency_fund.id)
    if emergency_transactions:
        tx_to_update = emergency_transactions[0]
        print(f"Updating transaction {tx_to_update.id} from ${tx_to_update.amount:.2f} to $500.00")

        updated_tx = tm.update_transaction(tx_to_update.id, {"amount": 500.0})
        print(f"Updated transaction: {updated_tx}")
        print(f"After update - Emergency Fund: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Test transaction deletion
    if len(emergency_transactions) > 1:
        tx_to_delete = emergency_transactions[1]
        print(f"\nDeleting transaction {tx_to_delete.id} (${tx_to_delete.amount:.2f})")
        print(f"Before deletion - Emergency Fund: ${emergency_fund.get_current_balance(tm.db):.2f}")

        success = tm.delete_transaction(tx_to_delete.id)
        print(f"Deletion successful: {success}")
        print(f"After deletion - Emergency Fund: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Final verification
    print("\n=== Phase 7: Final Verification ===")

    # Verify that all account balances can be recalculated from history
    all_accounts = accounts + bills
    for account in all_accounts:
        if hasattr(account, 'get_account_history'):
            history = account.get_account_history(tm.db)
            if hasattr(account, 'get_current_balance'):
                calculated_balance = 0.0
                for entry in history:
                    calculated_balance += entry.change_amount

                current_balance = account.get_current_balance(tm.db)

                if abs(calculated_balance - current_balance) > 0.01:
                    print(f"ERROR: Balance mismatch for {account.name}")
                    print(f"  Calculated: ${calculated_balance:.2f}")
                    print(f"  Reported: ${current_balance:.2f}")
                else:
                    print(f"[OK] {account.name}: Balance verified (${current_balance:.2f})")

    print("\n=== Integration Test Completed Successfully! ===")

    processor.close()
    tm.close()


if __name__ == "__main__":
    test_complete_integration()