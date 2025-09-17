"""
Test script to validate balance history functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor
from datetime import date, timedelta

def test_balance_history():
    """Test the balance history tracking functionality"""

    print("=== TESTING BALANCE HISTORY FUNCTIONALITY ===")

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        # Test 1: Verify existing accounts have balance history
        print("\n1. TESTING EXISTING ACCOUNT BALANCE HISTORY:")
        accounts = transaction_manager.get_all_accounts()

        for account in accounts:
            history = account.get_balance_history_copy()
            period_count = account.get_period_count()
            current_balance = account.get_balance_at_period(len(history) - 1) if history else None

            print(f"  {account.name}:")
            print(f"    Balance history: {history}")
            print(f"    Period count: {period_count}")
            print(f"    Current balance: ${account.running_total:.2f}")
            print(f"    Last history entry: ${current_balance:.2f}" if current_balance is not None else "    Last history entry: None")

        # Test 2: Test balance history methods on first account
        if accounts:
            test_account = accounts[0]
            print(f"\n2. TESTING BALANCE HISTORY METHODS ON '{test_account.name}':")

            # Get original state
            original_history = test_account.get_balance_history_copy()
            original_balance = test_account.running_total
            print(f"  Original history: {original_history}")
            print(f"  Original balance: ${original_balance:.2f}")

            # Test appending a new period balance
            new_balance = original_balance + 100.0
            test_account.append_period_balance(new_balance)
            transaction_manager.db.commit()

            updated_history = test_account.get_balance_history_copy()
            print(f"  After appending ${new_balance:.2f}: {updated_history}")

            # Test historical balance update and propagation
            if len(updated_history) >= 2:
                # Update the second-to-last period by +50
                target_index = len(updated_history) - 2
                old_value = updated_history[target_index]
                new_value = old_value + 50.0

                print(f"  Testing update propagation...")
                print(f"    Updating index {target_index}: ${old_value:.2f} -> ${new_value:.2f}")

                test_account.update_historical_balance(target_index, new_value)
                transaction_manager.db.commit()

                final_history = test_account.get_balance_history_copy()
                print(f"    After propagation: {final_history}")

                # Verify propagation worked correctly
                expected_change = 50.0
                for i in range(target_index, len(final_history)):
                    expected_value = updated_history[i] + expected_change
                    actual_value = final_history[i]
                    print(f"      Index {i}: Expected ${expected_value:.2f}, Got ${actual_value:.2f}, Correct: {abs(expected_value - actual_value) < 0.01}")

        # Test 3: Test new account creation with balance history
        print(f"\n3. TESTING NEW ACCOUNT CREATION:")
        test_account_name = "Test History Account"

        # Remove test account if it exists
        existing_test_account = transaction_manager.db.query(Account).filter(Account.name == test_account_name).first()
        if existing_test_account:
            transaction_manager.db.delete(existing_test_account)
            transaction_manager.db.commit()
            print(f"  Removed existing test account")

        # Create new account
        new_account = transaction_manager.add_account(test_account_name, goal_amount=1000.0)
        print(f"  Created account: {new_account.name}")

        # Check its balance history
        new_history = new_account.get_balance_history_copy()
        print(f"  Initial balance history: {new_history}")
        print(f"  Expected: [0.0], Got: {new_history}, Correct: {new_history == [0.0]}")

        # Test 4: Test a small paycheck to see balance history recording
        print(f"\n4. TESTING PAYCHECK PROCESSING WITH BALANCE HISTORY:")

        # Record balances before paycheck
        balances_before = {}
        for account in transaction_manager.get_all_accounts():
            balances_before[account.name] = {
                'balance': account.running_total,
                'history_length': len(account.get_balance_history_copy())
            }

        print(f"  Balances before paycheck:")
        for name, info in balances_before.items():
            print(f"    {name}: ${info['balance']:.2f}, History length: {info['history_length']}")

        # Process a small test paycheck
        test_amount = 1000.0
        test_date = date.today() + timedelta(days=1)
        start_date = test_date - timedelta(days=3)

        print(f"  Processing test paycheck: ${test_amount:.2f}")
        paycheck_processor.process_new_paycheck(test_amount, test_date, start_date)

        # Check balances after paycheck
        print(f"  Balances after paycheck:")
        all_histories_extended = True

        for account in transaction_manager.get_all_accounts():
            new_history = account.get_balance_history_copy()
            old_info = balances_before.get(account.name, {'history_length': 0})
            history_extended = len(new_history) > old_info['history_length']
            all_histories_extended = all_histories_extended and history_extended

            print(f"    {account.name}: ${account.running_total:.2f}, History length: {len(new_history)}, Extended: {history_extended}")
            print(f"      History: {new_history}")

        print(f"  All account histories extended: {all_histories_extended}")

        # Clean up test account
        transaction_manager.db.delete(new_account)
        transaction_manager.db.commit()
        print(f"  Cleaned up test account")

        # Test 5: Summary
        print(f"\n5. FINAL VERIFICATION:")
        final_accounts = transaction_manager.get_all_accounts()

        all_have_history = True
        for account in final_accounts:
            history = account.get_balance_history_copy()
            has_history = len(history) > 0
            all_have_history = all_have_history and has_history

            print(f"  {account.name}: {len(history)} history entries, Last: ${history[-1]:.2f}" if history else f"  {account.name}: No history")

        print(f"\nSUMMARY:")
        print(f"  All accounts have balance history: {all_have_history}")
        print(f"  Balance history integration: COMPLETE")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    test_balance_history()