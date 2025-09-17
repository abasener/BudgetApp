"""
Test the new savings chart logic directly using the AccountRowWidget
"""

from services.transaction_manager import TransactionManager
from widgets.account_row_widget import AccountRowWidget

def test_new_chart_logic():
    """Test the new chart logic by creating AccountRowWidget instances"""

    print("Testing New Savings Chart Logic (Start + Changes = End)")
    print("=" * 55)

    transaction_manager = TransactionManager()

    try:
        # Get all accounts
        accounts = transaction_manager.get_all_accounts()

        if not accounts:
            print("No savings accounts found")
            return

        print(f"Found {len(accounts)} savings accounts")

        for account in accounts:
            print(f"\\n{'=' * 40}")
            print(f"Testing: {account.name}")
            print(f"Current Balance: ${account.running_total:.2f}")

            # Create a mock AccountRowWidget to test the chart logic
            # We'll create a minimal widget just to call update_line_chart
            try:
                widget = AccountRowWidget(account, transaction_manager)
                # The widget constructor calls update_line_chart which will show our debug output
                print(f"Chart logic completed for {account.name}")

            except Exception as e:
                print(f"Error testing {account.name}: {e}")
                import traceback
                traceback.print_exc()

        print(f"\\n{'=' * 55}")
        print("Chart logic test completed")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()

if __name__ == "__main__":
    test_new_chart_logic()