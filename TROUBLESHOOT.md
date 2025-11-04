# Troubleshooting Log Template

## Purpose
This file serves as a structured log for documenting debugging sessions. When encountering a problem that requires extended troubleshooting, the user should instruct the AI: **"Read TROUBLESHOOT.md and fill it out with our current issue"**

## Target Audience
This document is formatted for AI consumption, not human readability. It should contain all technical details, code references, attempted solutions, and learned patterns that would help an AI assistant quickly understand the current problem state and past debugging attempts.

---

## CURRENT WORK: Transactions Tab - Advanced Data Inspection Interface (2024-11-01)

### PROGRESS: 98% Complete (Phases 1-8 of 9) ✅

**Completed:**
- ✅ Phase 1: Settings Toggle (enable/disable tab)
- ✅ Phase 2: Main Tab Structure (4 sub-tabs with search/delete/save UI)
- ✅ Phase 3: Table Widget Base (sortable, searchable, multi-select, delete marking)
- ✅ Phase 4: Bills Table (real data loaded from database)
- ✅ Phase 5: Savings Table (real data with deposits/withdrawals)
- ✅ Phase 6: Paycheck Table (all locked, with date ranges)
- ✅ Phase 7: Spending Table (includes rollovers and transfers)
- ✅ Phase 8: Save Logic (transaction ID tracking, validation, commit to database)

**Next Up:**
- 📋 Phase 9: Polish & Testing

### GOAL:
Create an optional "Transactions" tab (toggleable in Settings) that provides a comprehensive, table-based view of ALL transactions in the system. This is a fallback/debugging interface for power users to inspect and fix data issues.

### DESIGN PHILOSOPHY:
- **Fallback tool:** Users shouldn't need this normally, but it's there if something goes wrong
- **Comprehensive view:** Show ALL transactions including auto-generated ones (rollovers, allocations)
- **Non-destructive editing:** Only regular spending transactions are editable; auto-generated ones are locked
- **Batch operations:** Changes aren't saved until user clicks Save button
- **Organized by type:** Split into 4 tables (Bills, Savings, Paycheck, Spending) for clarity

---

### TAB ORGANIZATION:

**Selected Approach:** Sub-tabs within the main Transactions tab

```
Main Tabs: [Dashboard] [Bills] [Savings] [Weekly] ... [Transactions] ✨NEW

When Transactions tab selected:
┌────────────────────────────────────────────────────────────┐
│ [Bills] [Savings] [Paycheck] [Spending]  ← Sub-tabs       │
├────────────────────────────────────────────────────────────┤
│ 🔍 Search: [________]  [Delete Selected]  [Save Changes]  │
├────────────────────────────────────────────────────────────┤
│ Currently selected sub-tab content shown here              │
│ (Only ONE table visible at a time)                         │
│                                                            │
│ [Scrollbar if content exceeds window height]              │
└────────────────────────────────────────────────────────────┘
```

**Why sub-tabs?**
- 4 tables side-by-side won't fit comfortably
- Each transaction type has different columns
- Easier to focus on one type at a time
- Simpler search/filter logic (only affects current sub-tab)

---

### SEARCH & FILTER BEHAVIOR:

**One search bar per sub-tab** (shown above the table)
- Searches ALL fields in visible table
- Converts all fields to strings for comparison (including amounts)
- Partial match (case-insensitive)
- Real-time filtering (updates as user types)

**Example:**
```
User types "30" in search:
- Shows transactions with amount=$30.00
- Shows transactions with "30" in notes
- Shows transactions from Week 30
- Shows transactions from payweek 30
```

**Search Algorithm:**
```python
def matches_search(transaction, search_text):
    search_lower = search_text.lower()
    # Convert all fields to strings and check
    for field in [date, amount, category, notes, auto_notes, week]:
        if search_lower in str(field).lower():
            return True
    return False
```

---

### TABLE COLUMNS:

#### BILLS TABLE:
| Column | Type | Example | Editable? |
|--------|------|---------|-----------|
| Date | Date | 10/28/2024 | ✅ |
| Account | String | "Internet" | ❌ (read-only) |
| Amount | Dollar | $65.00 | ✅ |
| Manual Notes | Text | "October bill" | ✅ |
| Auto Notes | Text | "Manual: Bill payment" or "Generated: Auto saved from payweek 30" | ❌ (generated) |
| 🔒 | Icon | 🔒 or blank | ❌ (indicator) |

**Shows:**
- BILL_PAY transactions (payments from bill accounts)
- SAVING transactions with bill_id (deposits to bill accounts)

---

#### SAVINGS TABLE:
| Column | Type | Example | Editable? |
|--------|------|---------|-----------|
| Date | Date | 10/28/2024 | ✅ |
| Account | String | "Emergency Fund" | ❌ (read-only) |
| Amount | Dollar | $500.00 | ✅ |
| Manual Notes | Text | "Emergency deposit" | ✅ |
| Auto Notes | Text | "Manual: Transfer from checking" or "Generated: Rollover into Emergency Fund from payweek 30" | ❌ (generated) |
| 🔒 | Icon | 🔒 or blank | ❌ (indicator) |

**Shows:**
- SAVING transactions with account_id (deposits to savings accounts)
- SPENDING_FROM_SAVINGS transactions (withdrawals from savings)
- Week 2 → Savings rollovers

---

#### PAYCHECK TABLE:
| Column | Type | Example | Editable? |
|--------|------|---------|-----------|
| Earned Date | Date | 10/15/2024 | ❌ (read-only) |
| Start Date | Date | 10/21/2024 | ❌ (read-only) |
| Amount | Dollar | $4,237.50 | ❌ (read-only) |
| Manual Notes | Text | "Bi-weekly paycheck" | ✅ |
| Auto Notes | Text | "Manual: Paycheck 30 for 10/21/2024 to 11/03/2024" | ❌ (generated) |
| 🔒 | Icon | 🔒 | ❌ (indicator) |

**Shows:**
- INCOME transactions (paychecks)

**Note:** Paycheck transactions are user-entered but currently locked (editing would require auto-recalculation of allocations - see Feature 4.5 in PROJECT_PLAN.md)

**Date Fields:**
- **Earned Date:** Transaction.date (when paycheck was earned)
- **Start Date:** Week.start_date (when pay period starts)

---

#### SPENDING TABLE:
| Column | Type | Example | Editable? |
|--------|------|---------|-----------|
| Date | Date | 10/28/2024 | ✅ |
| Category | String | "Groceries" or "Transfer" | ✅ |
| Amount | Dollar | $45.67 | ✅ |
| Paycheck # | Integer | 30 | ❌ (calculated) |
| Week | String | "first" / "second" / "" | ❌ (calculated) |
| Manual Notes | Text | "Walmart" | ✅ |
| Auto Notes | Text | "Manual: Paycheck 30 bought Groceries on Monday" or "Generated: Rollover from week 59" or "Manual: Transfer to Emergency Fund" | ❌ (generated) |
| Abnormal | Checkbox | ☑ | ✅ |
| 🔒 | Icon | 🔒 or blank | ❌ (indicator) |

**Shows:**
- SPENDING transactions (regular spending) ✅ EDITABLE
- ROLLOVER transactions (Week 1 → Week 2) 🔒 LOCKED
- SAVING transactions with week_number (Week ↔ Account/Bill transfers) 🔒 LOCKED (editable in Savings/Bills tabs)

**Paycheck # vs Calendar Week:**
- Show paycheck number (1, 2, 3...) not calendar week (1-52)
- Paycheck # = (calendar_week_number + 1) // 2
- Example: Week 59 = Paycheck 30, Week 60 = Paycheck 30

**Week Column:**
- "first" = Odd week number (Week 1 of pay period)
- "second" = Even week number (Week 2 of pay period)
- "" = Not specific to one week (e.g., account-to-account transfer)

---

### AUTO-GENERATED NOTES FORMAT:

**All notes start with "Manual:" or "Generated:" prefix**

#### Manual Transactions:
```
"Manual: Coffee at Starbucks"
"Manual: October internet bill"
"Manual: Emergency withdrawal for car repair"
```

#### Generated Transactions:

**Paycheck:**
```
"Manual: Paycheck 30 for 10/21/2024 to 11/03/2024"
```

**Week 1 → Week 2 Rollover:**
```
"Generated: Rollover from week 59"
```

**Week 2 → Savings Rollover:**
```
"Generated: Rollover from payweek 30"
```

**Bill/Savings Auto-Save (from paycheck):**
```
"Generated: Savings allocation from payweek 30"
```

**Week → Account/Bill Transfer (manual):**
```
"Manual: Transfer to Vacation Fund"
```

**Account → Week Transfer (manual):**
```
"Manual: Transfer from Emergency Fund"
```

**Spending:**
```
"Manual: Paycheck 30 bought Groceries on Monday"
```

**Format Notes:**
- Always include payweek number for context
- Include source/destination for transfers
- Include week position (first/second) when relevant
- Be explicit about direction (from X to Y)

---

### LOCKED TRANSACTIONS:

**Transactions that are LOCKED (non-editable):**
- All ROLLOVER transactions
- All INCOME (paycheck) transactions
- Week allocation transactions (SAVING with week but no manual creation)
- Auto-generated SAVING transactions from paycheck processor

**How to indicate locked status:**
- 🔒 emoji in dedicated lock column
- Row is grayed out slightly (80% opacity)
- If user tries to edit: Do nothing (field is disabled)
- No warning popup needed (visual lock indicator is clear)

**Visual Example:**
```
┌──────────────────────────────────────────────────────────┐
│ Date       │ Category  │ Amount │ Notes              │ 🔒│
├──────────────────────────────────────────────────────────┤
│ 10/28/2024 │ Groceries │ $45.67 │ Manual: Walmart    │   │ ← Editable
│ 10/27/2024 │ Rollover  │ $312.76│ Generated: Roll... │ 🔒│ ← Locked (grayed)
│ 10/21/2024 │ Gas       │ $35.00 │ Manual: Shell      │   │ ← Editable
└──────────────────────────────────────────────────────────┘
```

---

### SAVE/DELETE BEHAVIOR:

#### Delete Flow:
1. User selects row(s) in table (single click to select, Ctrl+Click for multiple if easy)
2. User clicks "Delete Selected" button
3. Selected rows turn RED (text color changes)
4. Rows remain visible but marked for deletion
5. Nothing is deleted from database yet

#### Save Flow:
1. User clicks "Save Changes" button
2. App processes all changes:
   - RED rows → Delete from database
   - Edited rows → Update in database
3. Database committed in single transaction (all or nothing)
4. Table reloads from database (RED rows now gone)
5. Success message: "Saved X changes"

**Multi-select Implementation:**
- Try `QTableWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)`
- If it works easily: Great! ✅
- If it causes issues: Skip it, user can delete one at a time ❌

**Important:** Only delete on Save, not immediately

---

### SORTING:

**Clickable column headers** for sorting

**Default sort:** Oldest first (ascending by date)

**Sorting behavior:**
- Click header once: Sort ascending
- Click header again: Sort descending
- Click different header: Sort by that column (ascending)
- Each table has independent sort state

**Only affects current sub-tab** (Bills, Savings, Paycheck, or Spending)

**Sort indicators:** Show ▲ or ▼ arrow in header after column name

---

### SETTINGS INTEGRATION:

**Settings Dialog:**
```
┌─────────────────────────────────────┐
│ Advanced Settings                   │
├─────────────────────────────────────┤
│ ☐ Enable Transactions Tab           │
│   (Advanced data inspection tool)   │
└─────────────────────────────────────┘
```

**Behavior:**
- Checkbox in Settings dialog (under Advanced section)
- Default: DISABLED (unchecked)
- When enabled: "Transactions" tab appears in main tab bar
- When disabled: Tab is hidden from UI
- Setting saved to app_settings.json

**Why disabled by default?**
- Power user / debugging tool
- Most users won't need it
- Keeps UI simpler for normal use

---

### TRANSACTION TYPE DETECTION LOGIC:

#### BILLS Table Shows:
```python
if transaction.transaction_type == TransactionType.BILL_PAY:
    # Payments from bill accounts
    show_in_bills_table()
elif transaction.transaction_type == TransactionType.SAVING and transaction.bill_id:
    # Deposits to bill accounts
    show_in_bills_table()
```

#### SAVINGS Table Shows:
```python
if transaction.transaction_type == TransactionType.SAVING and transaction.account_id:
    # Deposits to savings accounts
    show_in_savings_table()
elif transaction.transaction_type == TransactionType.SPENDING_FROM_SAVINGS:
    # Withdrawals from savings
    show_in_savings_table()
```

#### PAYCHECK Table Shows:
```python
if transaction.transaction_type == TransactionType.INCOME:
    # Paycheck transactions
    show_in_paycheck_table()
```

#### SPENDING Table Shows:
```python
if transaction.transaction_type == TransactionType.SPENDING:
    # Regular spending
    show_in_spending_table()
elif transaction.transaction_type == TransactionType.ROLLOVER:
    # Week-to-week rollovers
    show_in_spending_table()
elif (transaction.transaction_type == TransactionType.SAVING and
      transaction.week_number and
      not transaction.account_id and
      not transaction.bill_id):
    # Week allocations from paycheck (if any exist)
    show_in_spending_table()
```

---

### FILE LOCATIONS:

**New Files to Create:**
- `views/transactions_view.py` - Main tab widget with sub-tabs
- `views/transactions_table_widget.py` - Reusable table widget for each sub-tab

**Files to Modify:**
- `main.py` - Add Transactions tab conditionally based on settings
- `views/dialogs/settings_dialog.py` - Add "Enable Transactions Tab" checkbox

**Reference Files:**
- `views/bills_view.py` - Reference for table-based views
- `views/dialogs/bill_transaction_history_dialog.py` - Reference for transaction tables
- `views/weekly_view.py` - Reference for transaction filtering

---

### IMPLEMENTATION PLAN:

#### Phase 1: Settings Toggle (30 min) ✅ COMPLETE
- [x] Add `enable_transactions_tab` to app_settings.json schema
- [x] Add checkbox to Settings dialog
- [x] Wire up to settings save/load

#### Phase 2: Main Tab Structure (1 hour) ✅ COMPLETE
- [x] Create `views/transactions_view.py`
- [x] Add QTabWidget for 4 sub-tabs (Bills, Savings, Paycheck, Spending)
- [x] Add search bar, delete button, save button to each sub-tab
- [x] Wire up to main window (conditionally add based on setting)

#### Phase 3: Table Widget Base (2 hours) ✅ COMPLETE
- [x] Create `views/transactions_table_widget.py`
- [x] QTableWidget with sortable columns (▲/▼ indicators)
- [x] Implement search filtering (real-time, all fields)
- [x] Implement row selection (ExtendedSelection = Ctrl+Click multi-select)
- [x] Implement delete marking (red text + strikethrough)
- [x] Implement locked row styling (gray + italic + 🔒)
- [x] **BONUS:** Abnormal column as checkbox widget
- [x] **BONUS:** Editable column non-editable, fixed 70px width
- [x] **BONUS:** Last 2 columns stretch (for long notes)

#### Phase 4: Bills Table (1.5 hours) ✅ COMPLETE
- [x] Define columns: Date, Account, Amount, Editable, Manual Notes, Auto Notes
- [x] Load BILL_PAY and SAVING(bill_id) transactions
- [x] Generate auto-notes for each row
- [x] Determine locked rows (auto-generated transactions)
- [x] Wire up to table widget
- [x] Test sorting, searching, deleting

#### Phase 5: Savings Table (1.5 hours) ✅ COMPLETE
- [x] Define columns: Date, Account, Amount, Editable, Manual Notes, Auto Notes
- [x] Load SAVING(account_id) transactions via AccountHistory (includes deposits/withdrawals)
- [x] Generate auto-notes (deposits, withdrawals, rollovers)
- [x] Wire up to table widget
- [x] Test sorting, searching, deleting

#### Phase 6: Paycheck Table (1 hour) ✅ COMPLETE
- [x] Define columns: Earned Date, Start Date, Amount, Editable, Manual Notes, Auto Notes
- [x] Load INCOME transactions
- [x] Generate auto-notes with date ranges ("Paycheck X for date1 to date2")
- [x] All rows locked (user-entered but locked until recalculation implemented)
- [x] Wire up to table widget
- [x] Test sorting, searching

#### Phase 7: Spending Table (2 hours) ✅ COMPLETE
- [x] Define columns: Date, Category, Amount, Paycheck#, Week, Editable, Abnormal, Manual Notes, Auto Notes
- [x] Load SPENDING, ROLLOVER, and SAVING(week_number) transactions
- [x] Calculate paycheck# and week position
- [x] Generate auto-notes (category + day of week, transfers with destination)
- [x] Determine locked vs editable rows
- [x] Wire up to table widget
- [x] Test all functionality

#### Phase 8: Save Logic (2 hours) ✅ COMPLETE
- [x] Track transaction IDs for each table row
- [x] Track edited and deleted rows separately
- [x] Clear tracking when switching sub-tabs
- [x] Validate data types (dates, amounts) before saving
- [x] Save deletes and edits to database transaction-by-transaction
- [x] Show detailed success/failure dialog with change summary
- [x] Refresh tables after save

#### Phase 9: Polish & Testing (2 hours)
- [x] Theme integration (colors update on theme change)
- [ ] Error handling for edge cases
- [ ] Test with real data (user testing in progress)
- [ ] Test enabling/disabling in settings
- [ ] Document any quirks found

**Total Estimated Time:** ~13-15 hours
**Time Spent So Far:** ~13 hours (Phases 1-8 complete)
**Remaining:** ~2 hours (Phase 9 testing & polish)

---

### TECHNICAL CHALLENGES:

#### Challenge 1: Auto-Notes Generation
**Problem:** Need to generate descriptive notes for every transaction type
**Solution:** Create helper methods per transaction type
```python
def get_auto_notes(transaction):
    if transaction.transaction_type == TransactionType.ROLLOVER:
        return generate_rollover_notes(transaction)
    elif transaction.transaction_type == TransactionType.INCOME:
        return generate_paycheck_notes(transaction)
    # ... etc
```

#### Challenge 2: Locked vs Editable Detection
**Problem:** Need to distinguish auto-generated from manual transactions
**Solution:** Check transaction type + creation pattern
```python
def is_locked(transaction):
    # Always locked
    if transaction.transaction_type in [TransactionType.ROLLOVER, TransactionType.INCOME]:
        return True
    # Locked if auto-generated from paycheck
    if transaction.transaction_type == TransactionType.SAVING:
        # Check if description contains "Auto saved from payweek"
        if "Auto saved" in transaction.description:
            return True
    return False
```

#### Challenge 3: Paycheck Number Calculation
**Problem:** Need to convert calendar week to paycheck number
**Solution:**
```python
def get_paycheck_number(calendar_week_number):
    return (calendar_week_number + 1) // 2

def get_week_position(calendar_week_number):
    if calendar_week_number % 2 == 1:
        return "first"
    elif calendar_week_number % 2 == 0:
        return "second"
    else:
        return ""
```

#### Challenge 4: Search String Conversion
**Problem:** Need to search numeric fields (amount) as strings
**Solution:**
```python
def to_search_string(value):
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return f"${value:.2f}"  # Format as dollar amount
    if isinstance(value, date):
        return value.strftime("%m/%d/%Y")
    return str(value)
```

---

### TESTING CHECKLIST:

#### Settings Integration:
- [ ] Checkbox appears in Settings dialog
- [ ] Default state is unchecked
- [ ] Checking enables tab, unchecking hides tab
- [ ] Setting persists after app restart

#### Table Loading:
- [ ] Bills table loads all BILL_PAY and SAVING(bill) transactions
- [ ] Savings table loads all SAVING(account) and SPENDING_FROM_SAVINGS transactions
- [ ] Paycheck table loads all INCOME transactions
- [ ] Spending table loads SPENDING, ROLLOVER, and week transfers

#### Auto-Notes:
- [ ] All auto-notes start with "Manual:" or "Generated:"
- [ ] Rollover notes include both weeks and payweek number
- [ ] Paycheck notes include payweek number
- [ ] Transfer notes include source and destination

#### Locked Rows:
- [ ] Rollovers show 🔒 and are grayed out
- [ ] Paychecks show 🔒 and are grayed out
- [ ] Regular spending shows no lock and is normal opacity
- [ ] Locked rows can't be edited (fields disabled)

#### Search:
- [ ] Typing in search filters visible rows
- [ ] Search works on all fields (amount, date, notes, etc.)
- [ ] Search is case-insensitive
- [ ] Clearing search shows all rows again

#### Sorting:
- [ ] Clicking column header sorts table
- [ ] Arrow indicator shows current sort direction
- [ ] Clicking same header toggles sort direction
- [ ] Default sort is oldest-first by date

#### Delete:
- [ ] Selecting row and clicking Delete turns text red
- [ ] Red rows remain visible
- [ ] Multiple deletes accumulate (multiple red rows)
- [ ] Clicking Delete on locked row does nothing (stays gray)

#### Save:
- [ ] Clicking Save commits all changes
- [ ] Red rows are deleted from database
- [ ] Edited rows are updated in database
- [ ] Tables reload and show updated data
- [ ] Red rows are now gone (deleted successfully)

#### Edge Cases:
- [ ] Empty tables show "No transactions" message
- [ ] Transactions with missing data display gracefully
- [ ] Very long notes wrap or truncate properly
- [ ] Large transaction counts don't freeze UI

---

## Template Sections (Save for future debugging - DO NOT DELETE)

### Problem Statement
- Clear description of the current issue
- Expected behavior vs actual behavior
- When the problem started occurring
- Any error messages or unexpected outputs

### Attempted Solutions
- What has been tried (with specific code changes or commands)
- Why each attempt failed
- What was learned from each attempt

### Code Patterns That Work
- Include working code snippets with explanations
- Proven query patterns
- Successful data transformations

### Code Patterns That Don't Work
- Anti-patterns discovered
- Failed approaches with reasons why
- Common pitfalls to avoid
