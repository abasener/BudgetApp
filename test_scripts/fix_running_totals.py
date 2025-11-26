"""
Script to fix corrupted running_total values in AccountHistory
This recalculates all running totals from scratch using the change_amount values
"""
from models.database import get_db
from models.account_history import AccountHistoryManager
from models.bills import Bill
from models.accounts import Account

print("="*80)
print("FIXING CORRUPTED RUNNING TOTALS IN ACCOUNT HISTORY")
print("="*80)

# Get database session
db = get_db()
history_manager = AccountHistoryManager(db)

# Track what we fix
fixed_accounts = []
fixed_bills = []

print("\n1. Recalculating running totals for all BILLS...")
bills = db.query(Bill).all()
for bill in bills:
    print(f"   - Fixing {bill.name}...")
    try:
        history_manager.recalculate_account_history(bill.id, "bill")
        fixed_bills.append(bill.name)
    except Exception as e:
        print(f"     ERROR: {e}")

print(f"\n   [OK] Fixed {len(fixed_bills)} bills")

print("\n2. Recalculating running totals for all SAVINGS ACCOUNTS...")
accounts = db.query(Account).all()
for account in accounts:
    print(f"   - Fixing {account.name}...")
    try:
        history_manager.recalculate_account_history(account.id, "savings")
        fixed_accounts.append(account.name)
    except Exception as e:
        print(f"     ERROR: {e}")

print(f"\n   [OK] Fixed {len(fixed_accounts)} accounts")

# Commit changes
print("\n3. Committing changes to database...")
db.commit()
print("   [OK] Changes committed")

# Verify fix for Internet bill
print("\n4. Verifying fix for Internet bill...")
from models.account_history import AccountHistory
internet_bill = db.query(Bill).filter(Bill.name == "Internet").first()
if internet_bill:
    # Get the specific entries we were debugging
    entry_147 = db.query(AccountHistory).filter(AccountHistory.id == 147).first()
    entry_219 = db.query(AccountHistory).filter(AccountHistory.id == 219).first()

    if entry_147 and entry_219:
        print(f"   Entry 147: change={entry_147.change_amount:>8.2f}, running_total={entry_147.running_total:>8.2f}")
        print(f"   Entry 219: change={entry_219.change_amount:>8.2f}, running_total={entry_219.running_total:>8.2f}")

        expected = entry_147.running_total + entry_219.change_amount
        actual = entry_219.running_total

        if abs(expected - actual) < 0.01:  # Allow for floating point precision
            print(f"   [OK] VERIFIED: {entry_147.running_total:.2f} + {entry_219.change_amount:.2f} = {entry_219.running_total:.2f}")
        else:
            print(f"   [FAILED] Expected {expected:.2f}, got {actual:.2f}")

print("\n" + "="*80)
print("RECALCULATION COMPLETE!")
print("="*80)
print(f"\nFixed {len(fixed_bills)} bills and {len(fixed_accounts)} accounts")
print("\nPlease restart the application to see the corrected line plots.")
print("="*80)

db.close()
