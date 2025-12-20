# Transactions Tab Refactor Roadmap

## !!! VERY IMPORTANT - READ FIRST !!!

**WE ARE NOT ADJUSTING ANY BACKEND OR DATABASE CODE**

We are ONLY adjusting the code for the Transactions tab to:
1. Read data from the existing database
2. Interpret that data correctly
3. Display it in a user-friendly way

The backend (models, services, paycheck_processor, etc.) is complex and interconnected.
What might seem like a helpful change could break the entire budget system.

**FILES WE CAN MODIFY:**
- `views/transactions_view.py` - Main transactions tab
- `views/transactions_table_widget.py` - Table widget component

**FILES WE CANNOT MODIFY:**
- `models/*.py` - Database models
- `services/*.py` - Business logic
- Any other backend files

---

## DELETE THIS FILE WHEN DONE

This is a temporary working document. Delete when the Transactions tab refactor is complete.

---

## Current Understanding

### How Transfers Work (from transfer_dialog.py)

**Week <-> Account/Bill Transfer (Single Transaction):**
- Creates ONE transaction with `type=saving`
- If Week -> Account: `amount = positive`, `account_id = destination`
- If Account -> Week: `amount = negative`, `account_id = source`
- The `week_number` field links to the week involved

**Account <-> Account Transfer (Two Transactions):**
- Creates TWO transactions, both `type=saving`
- Transaction 1: `amount = negative` (withdrawal from source)
- Transaction 2: `amount = positive` (deposit to destination)
- Both have same `week_number` (current week), same date
- Notes reference each other: "Transferring $X to Y" / "Transferring $X from Y"

### Key Insight: Amount Signs in Database
- `Transaction.amount` is NOT always positive!
- For `saving` type: positive = INTO account, negative = OUT OF account
- For `bill_pay` type: always positive (AccountHistory converts to negative)
- For `spending` type: always positive
- For `income` type: always positive
- For `rollover` type: always positive

### AccountHistory vs Transaction
- `AccountHistory.change_amount` is SIGNED (reflects actual balance change)
- Bills/Savings tabs currently show AccountHistory, which is why signs appear correct
- Spending tab shows Transaction.amount directly

---

## Decisions Made

### 1. Locking Logic
Only lock these transaction types:
- `type = rollover` (all)
- `type = saving` WHERE description contains "end-of-period" (auto-rollover to savings)

Everything else is editable.

### 2. New Tab Structure

| Sub-tab | Shows | Source |
|---------|-------|--------|
| **Accounts** | All bill + savings history merged | AccountHistory entries |
| **Paycheck** | Income transactions | Transactions where type=income |
| **Spending** | Spending + Rollovers | Transactions where type=spending OR type=rollover |
| **Transfers** | All transfers (Week<->Account, Account<->Account) | Transactions where type=saving |

Note: Rollovers stay in Spending tab (user wants to see them together).

### 3. Sign Display
**Phase 1 (Current Task):** Show all amounts as positive (database raw values)
- This keeps things simple and truthful
- User can see transaction_type to understand direction
- We can add smart signs later if needed

### 4. Columns to Add
- `ID` - Transaction ID (for debugging, may remove later)
- `Type` - Transaction type (spending, saving, income, etc.)
- `Week` - Week number (always has a value)

### 5. Transfers Tab Display
Use From/To columns with positive amount:
- `Amount`: Always positive (e.g., "$100.00")
- `From`: Source ("Week 5", "Safety Saving", "Rent")
- `To`: Destination ("Vacation", "Week 7", "Safety Saving")

For Account<->Account transfers (2 transactions), we need to:
- Detect pairs by matching: same date, same absolute amount, opposite signs, notes reference each other
- Display as single row with From/To filled in
- OR display both rows but make it clear they're linked

---

## Implementation Steps

### Step 1: Fix Locking Logic
File: `transactions_view.py`
Function: `is_transaction_locked()`

Change from:
```python
if transaction.transaction_type in [TransactionType.ROLLOVER.value, TransactionType.INCOME.value]:
    return True
```

To:
```python
if transaction.transaction_type == TransactionType.ROLLOVER.value:
    return True

# Only lock auto-generated savings (end-of-period rollovers)
if transaction.transaction_type == TransactionType.SAVING.value:
    if transaction.description:
        desc_lower = transaction.description.lower()
        if "end-of-period" in desc_lower:
            return True

return False
```

### Step 2: Add New Columns
Update column definitions in each `load_*_data()` function:
- Add "ID" column (transaction.id)
- Add "Type" column (transaction.transaction_type)
- Add "Week" column (transaction.week_number)

### Step 3: Restructure Tabs
1. Rename "Bills" tab to "Accounts"
2. Merge Bills + Savings data loading into one function
3. Rename "Savings" tab to "Transfers"
4. Create new `load_transfers_data()` function

### Step 4: Create Transfers Tab
New function `load_transfers_data()`:
- Query transactions where `type = saving`
- Determine From/To based on:
  - If `amount > 0`: To = account_id/bill_id, From = Week {week_number}
  - If `amount < 0`: From = account_id/bill_id, To = Week {week_number}
- For account-to-account pairs: detect and combine (or show both with clear linking)

### Step 5: Fix Save Logic
When editing transactions:
1. Save the updated values
2. Call `paycheck_processor.recalculate_period_rollovers(week_number)`
3. Refresh the view

### Step 6: Handle Paycheck Edits
Special case for income transactions:
1. Update the transaction amount
2. Recalculate percentage-based auto-saves (if any)
3. Recalculate week allocations
4. Call rollover recalculation

---

## Concerns / Unknowns

### 1. Account-to-Account Transfer Detection
How to reliably detect that two transactions are a pair?
- Same date
- Same absolute amount
- Opposite signs
- Both are type=saving
- Notes reference each other ("to X" / "from X")

May need to show both rows with a visual indicator they're linked.

### 2. Paycheck Edit Consequences
When editing income amount:
- Do we need to recalculate week.running_total? (This is set by paycheck processor)
- Do we need to recalculate auto-save amounts?
- Current plan: Call existing recalculation functions and hope they handle it

### 3. Rollover Duplication Check
Need to verify rollovers don't appear in Accounts tab.
- Accounts tab shows AccountHistory entries
- Week 2 -> Savings rollovers create AccountHistory entries for the savings account
- These SHOULD appear in Accounts tab (they're real deposits to the account)
- They should NOT appear in Transfers tab (they're not user-created transfers)

How to distinguish:
- Transfers: `type=saving`, no "end-of-period" in description
- Auto-rollovers: `type=saving`, "end-of-period" in description

---

## Testing Checklist

After implementation:
- [ ] Bills/Accounts tab shows all account history entries
- [ ] Paycheck tab shows all income, is editable
- [ ] Spending tab shows spending + rollovers, rollovers locked
- [ ] Transfers tab shows Week<->Account and Account<->Account transfers
- [ ] Editing spending triggers rollover recalculation
- [ ] Editing income triggers proper recalculation
- [ ] No duplicate entries across tabs
- [ ] All amounts display as positive (Phase 1)
- [ ] ID, Type, Week columns visible

---

## File Locations

Main file to edit:
`c:\Users\arrow\OneDrive\Documents\GitHub\BudgetApp\views\transactions_view.py`

Table widget (may need minor updates):
`c:\Users\arrow\OneDrive\Documents\GitHub\BudgetApp\views\transactions_table_widget.py`

Reference files (DO NOT EDIT):
- `models/transactions.py` - Transaction model
- `models/account_history.py` - AccountHistory model
- `services/paycheck_processor.py` - Rollover logic
- `views/dialogs/transfer_dialog.py` - How transfers are created
