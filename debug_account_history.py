"""
Debug script to check AccountHistory data for a specific bill
"""
from models.database import get_db
from models.account_history import AccountHistory
from models.bills import Bill

# Get database session
db = get_db()

# Find the Internet bill
internet_bill = db.query(Bill).filter(Bill.name == "Internet").first()

if not internet_bill:
    print("Internet bill not found!")
    exit()

print(f"Internet Bill ID: {internet_bill.id}")
print(f"Current Balance: ${internet_bill.get_current_balance(db):.2f}")
print("\n" + "="*120)
print(f"{'ID':<6} {'Date':<12} {'Transaction ID':<15} {'Change Amount':<15} {'Running Total':<15} {'Description'}")
print("="*120)

# Get all AccountHistory entries for this bill
history_entries = db.query(AccountHistory).filter(
    AccountHistory.account_id == internet_bill.id,
    AccountHistory.account_type == "bill"
).order_by(AccountHistory.transaction_date, AccountHistory.id).all()

for entry in history_entries:
    date_str = entry.transaction_date.strftime("%Y-%m-%d")
    trans_id = str(entry.transaction_id) if entry.transaction_id else "None"
    change = f"${entry.change_amount:.2f}"
    running = f"${entry.running_total:.2f}"
    desc = (entry.description or "")[:50]

    print(f"{entry.id:<6} {date_str:<12} {trans_id:<15} {change:<15} {running:<15} {desc}")

print("="*120)

# Also check the corresponding transactions
print("\nCorresponding Transactions:")
print("="*120)
print(f"{'Transaction ID':<15} {'Date':<12} {'Type':<15} {'Amount':<15} {'Description'}")
print("="*120)

from models.transactions import Transaction
for entry in history_entries:
    if entry.transaction_id:
        trans = db.query(Transaction).filter(Transaction.id == entry.transaction_id).first()
        if trans:
            date_str = trans.date.strftime("%Y-%m-%d")
            trans_type = trans.transaction_type
            amount = f"${trans.amount:.2f}"
            desc = (trans.description or "")[:50]
            print(f"{trans.id:<15} {date_str:<12} {trans_type:<15} {amount:<15} {desc}")

print("="*120)

db.close()
