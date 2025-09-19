"""
Debug the balance issue in TransactionManager
"""

from datetime import date
from models import get_db, create_tables, drop_tables, TransactionType, AccountHistoryManager
from services.transaction_manager import TransactionManager


def debug_balance_issue():
    """Debug why balances aren't updating correctly"""

    # Fresh database for testing
    drop_tables()
    create_tables()

    tm = TransactionManager()

    print("=== Debugging Balance Issue ===")

    # Add account
    emergency_fund = tm.add_account(
        name="Emergency Fund",
        goal_amount=5000.0,
        auto_save_amount=200.0,
        is_default_save=True,
        initial_balance=1000.0
    )
    print(f"Created account: {emergency_fund}")

    # Check history directly
    history_manager = AccountHistoryManager(tm.db)
    initial_history = history_manager.get_account_history(emergency_fund.id, "savings")
    print(f"Initial history entries: {len(initial_history)}")
    for entry in initial_history:
        print(f"  {entry}")

    initial_balance = history_manager.get_current_balance(emergency_fund.id, "savings")
    print(f"Initial balance via history manager: ${initial_balance:.2f}")

    # Add a savings transaction
    savings_tx_data = {
        "transaction_type": TransactionType.SAVING.value,
        "week_number": 1,
        "amount": 300.0,
        "date": date(2024, 1, 15),
        "description": "Emergency fund deposit",
        "account_id": emergency_fund.id,
        "account_saved_to": "Emergency Fund"
    }
    savings_tx = tm.add_transaction(savings_tx_data)
    print(f"Added transaction: {savings_tx}")

    # Check if transaction affects account
    print(f"Transaction affects account: {savings_tx.affects_account}")
    print(f"Account type: {savings_tx.account_type}")
    print(f"Affected account ID: {savings_tx.affected_account_id}")
    print(f"Change amount: ${savings_tx.get_change_amount_for_account():.2f}")

    # Check history after transaction
    after_history = history_manager.get_account_history(emergency_fund.id, "savings")
    print(f"History entries after transaction: {len(after_history)}")
    for entry in after_history:
        print(f"  {entry} (Date: {entry.transaction_date}, ID: {entry.id})")

    # Check what get_current_balance is actually returning
    from models import AccountHistory
    latest_entry = tm.db.query(AccountHistory).filter(
        AccountHistory.account_id == emergency_fund.id,
        AccountHistory.account_type == "savings"
    ).order_by(AccountHistory.transaction_date.desc(), AccountHistory.id.desc()).first()

    print(f"Latest entry query result: {latest_entry}")

    after_balance = history_manager.get_current_balance(emergency_fund.id, "savings")
    print(f"Balance after transaction via history manager: ${after_balance:.2f}")

    # Check what the account model returns
    account_balance = emergency_fund.get_current_balance(tm.db)
    print(f"Balance via account model: ${account_balance:.2f}")

    tm.close()


if __name__ == "__main__":
    debug_balance_issue()