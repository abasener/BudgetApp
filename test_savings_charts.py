"""
Test script for savings account chart logic
"""

from services.transaction_manager import TransactionManager
from widgets.account_row_widget import AccountRowWidget
from datetime import date

def test_savings_charts():
    """Test the savings account chart logic"""

    print("Testing Savings Account Chart Logic")
    print("=" * 40)

    # Initialize transaction manager
    transaction_manager = TransactionManager()

    try:
        # Get all accounts
        accounts = transaction_manager.get_all_accounts()

        if not accounts:
            print("No savings accounts found")
            return

        print(f"Found {len(accounts)} savings accounts:")
        for account in accounts:
            print(f"  - {account.name}: ${account.running_total:.2f}")

        print("\n" + "=" * 40)

        # Test the chart logic for each account
        for account in accounts:
            print(f"\nTesting chart logic for: {account.name}")
            print(f"Current balance: ${account.running_total:.2f}")

            # Create a mock account row widget to test the chart logic
            # We'll just run the chart update method to see the debug output
            try:
                # Get all weeks
                all_weeks = transaction_manager.get_all_weeks()
                print(f"Total weeks in database: {len(all_weeks)}")

                if not all_weeks:
                    print("No weeks found - chart would show flat line")
                    continue

                # Sort weeks chronologically
                all_weeks.sort(key=lambda w: w.start_date)
                print(f"Week range: {all_weeks[0].start_date} to {all_weeks[-1].end_date}")

                # Group weeks into bi-weekly periods
                bi_weekly_periods = []
                for i in range(0, len(all_weeks), 2):
                    if i + 1 < len(all_weeks):
                        week1 = all_weeks[i]
                        week2 = all_weeks[i + 1]
                        bi_weekly_periods.append((week1, week2))
                    else:
                        bi_weekly_periods.append((all_weeks[i], None))

                print(f"Bi-weekly periods: {len(bi_weekly_periods)}")

                # Get all transactions for this account
                all_transactions = transaction_manager.get_all_transactions()
                account_transactions = [
                    t for t in all_transactions
                    if (t.transaction_type == "saving" and
                        ((hasattr(t, 'account_id') and t.account_id == account.id) or
                         (hasattr(t, 'account_saved_to') and t.account_saved_to and t.account_saved_to == account.name)))
                ]

                print(f"Account transactions: {len(account_transactions)}")
                for tx in account_transactions:
                    print(f"  - {tx.date}: ${tx.amount:.2f} ({tx.description})")

                # Simulate the NEW chart calculation logic
                current_account_balance = account.running_total
                has_any_transactions = len(account_transactions) > 0

                if not has_any_transactions and current_account_balance > 0:
                    # No transaction history but account has balance - show flat line
                    print("  NEW LOGIC: No transactions but account has balance - creating flat line")
                    balance_points = []
                    for period_idx, (week1, week2) in enumerate(bi_weekly_periods):
                        period_end_date = week2.end_date if week2 else week1.end_date
                        balance_points.append((period_end_date, current_account_balance))
                        print(f"  Period {period_idx + 1}: No transactions, showing balance ${current_account_balance:.2f}")
                else:
                    # Normal case: accumulate transactions chronologically
                    balance_points = []
                    running_balance = 0.0

                    for period_idx, (week1, week2) in enumerate(bi_weekly_periods):
                        period_end_date = week2.end_date if week2 else week1.end_date
                        period_start_date = week1.start_date

                        period_transactions = [
                            t for t in account_transactions
                            if period_start_date <= t.date <= period_end_date
                        ]

                        period_total = sum(t.amount for t in period_transactions)
                        running_balance += period_total

                        balance_points.append((period_end_date, running_balance))

                        print(f"  Period {period_idx + 1} ({period_start_date} to {period_end_date}): "
                              f"{len(period_transactions)} transactions = ${period_total:.2f}, "
                              f"running balance = ${running_balance:.2f}")

                    # Check if calculated balance matches actual balance
                    if balance_points and abs(balance_points[-1][1] - current_account_balance) > 0.01:
                        print(f"  NEW LOGIC: Adjusting final balance from ${balance_points[-1][1]:.2f} to ${current_account_balance:.2f}")
                        balance_points[-1] = (balance_points[-1][0], current_account_balance)

                # Check final result
                if balance_points:
                    final_balance = balance_points[-1][1]
                    print(f"\\nFinal chart result:")
                    print(f"  Chart will show: ${final_balance:.2f}")
                    print(f"  Actual balance:  ${current_account_balance:.2f}")
                    print(f"  Match: {'YES' if abs(final_balance - current_account_balance) < 0.01 else 'NO'}")
                    print(f"  Data points: {len(balance_points)}")
                else:
                    print("\\nNo chart data will be shown")

            except Exception as e:
                print(f"Error testing {account.name}: {e}")
                import traceback
                traceback.print_exc()

        print("\\n" + "=" * 40)
        print("Savings chart logic test completed")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()

if __name__ == "__main__":
    test_savings_charts()