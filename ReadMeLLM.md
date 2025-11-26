# ReadMeLLM.md - LLM Memory & Context

**Last Updated:** 2025-11-26
**Purpose:** AI assistant reference for BudgetApp development
**Audience:** Large Language Models (Claude, GPT, etc.)
**Format:** Optimized for LLM parsing, not human reading

---

## 📚 How to Interact With Documentation Files

### Documentation Hierarchy (Read in Order)
1. **README.md** - Public GitHub overview (features, setup, philosophy)
   - Audience: External users discovering project
   - Detail Level: High-level features, no implementation details
   - Update When: Major feature releases, version changes

2. **ReadMe2.txt** - Developer technical reference (architecture, file structure)
   - Audience: Developers reading the codebase
   - Detail Level: Architecture patterns, key files, critical methods
   - Update When: Major architectural changes, new tabs/services

3. **ReadMeLLM.md** (THIS FILE) - LLM memory & gotchas
   - Audience: AI assistants working on code
   - Detail Level: Variable semantics, common bugs, anti-patterns
   - Update When: After fixing confusing bugs, miscommunications, or adding complex features

4. **PROJECT_PLAN.md** - Roadmap & todo tracking
   - Audience: User + LLM during active development
   - Detail Level: Feature status, GUI layouts, implementation todos
   - Update When: Starting/completing phases, tracking bugs, planning features

5. **RULES_PLANNING.md** - Future feature spec (Phase 3 - on hold)
   - Audience: User + LLM when resuming Rules system work
   - Detail Level: Detailed spec for automation/goals/warnings system
   - Update When: Only when resuming Phase 3 work

### When Adding New Information
- **Implementation details of new tabs/features** → ReadMe2.txt (condensed) + ReadMeLLM.md (detailed)
- **Bug fixes & lessons learned** → ReadMeLLM.md (always!)
- **Architecture decisions & rationale** → ReadMeLLM.md
- **Public-facing feature descriptions** → README.md
- **Work tracking & status** → PROJECT_PLAN.md
- **Future feature specs** → New file in `planning/` folder

### What NOT to Document
- ❌ Temporary debugging output (delete after fixing)
- ❌ Session-by-session logs (outdated quickly)
- ❌ Code that explains itself (use inline comments instead)
- ❌ Font size changes, color tweaks (too granular)

---

## 🗄️ Database Schema - Critical Details

### Transaction Table
```python
class Transaction(Base):
    id: int
    date: Date
    amount: float          # ⚠️ ALWAYS POSITIVE (even for bill payments!)
    description: str
    category: str
    transaction_type: TransactionType  # ENUM: INCOME, SPENDING, BILL_PAY, SAVING, ROLLOVER, SPENDING_FROM_SAVINGS
    week_number: int       # Calendar week (1-52), NOT paycheck number
    account_id: int        # FK to savings accounts (nullable)
    bill_id: int           # FK to bills (nullable)
    include_in_analytics: bool  # Filter for "normal spending only"
```

**Critical Gotchas:**
- `amount` is **ALWAYS positive** - direction determined by `transaction_type`
- `week_number` is **calendar week** (1-52), not bi-weekly paycheck number
- Bill payments have `transaction_type=BILL_PAY` and `bill_id` set
- Transfers between accounts create **2 transactions** (one negative, one positive in AccountHistory)

### AccountHistory Table
```python
class AccountHistory(Base):
    id: int
    transaction_id: int       # FK to Transaction (NULL for starting balance entries)
    account_id: int           # Account/Bill affected
    account_type: str         # "bill" or "savings"
    change_amount: float      # ⚠️ SIGNED: negative = money out, positive = money in
    running_total: float      # Cumulative balance after this change
    transaction_date: Date    # ⚠️ MUST be chronologically ordered!
    description: str          # For non-transaction entries
```

**Critical Gotchas:**
- `change_amount` is **SIGNED** (negative for payments/withdrawals)
- `running_total` **auto-propagates** forward when inserting historical entries
- Starting balance entries have `transaction_id=NULL` and **must be dated BEFORE all transactions**
- Entries are **date-ordered** - inserting out-of-order triggers recalculation
- **NEVER manually set running_total** - always use `_update_running_totals_from_entry()`

### Week Table
```python
class Week(Base):
    id: int
    week_number: int          # Calendar week (1-52)
    start_date: Date
    end_date: Date
    running_total: float      # ⚠️ BASE ALLOCATION ONLY (does NOT include rollovers!)
    rollover_applied: bool
```

**Critical Gotchas:**
- `running_total` = **base allocation from paycheck split** (half of spendable income)
- `running_total` **NEVER includes rollovers** - rollovers are separate transactions
- Week display "Starting" amount = `running_total` + rollover_in - rollover_out
- Week 1 (odd week_number) = first week of pay period
- Week 2 (even week_number) = second week of pay period

### Account & Bill Tables
```python
class Account(Base):
    id: int
    name: str
    goal_amount: float
    auto_save_amount: float
    is_default_save: bool     # True for Emergency Fund
    # ⚠️ NO balance field! Use get_current_balance() from AccountHistory

class Bill(Base):
    id: int
    name: str
    amount_to_save: float     # Auto-deducted per paycheck
    typical_amount: float
    frequency: str            # "monthly", "quarterly", etc.
    bill_type: str            # "fixed" or "variable"
    # ⚠️ NO balance field! Use get_current_balance() from AccountHistory
```

**Critical Gotchas:**
- **NO `balance` field on Account/Bill models** - always call `get_current_balance()`
- Balance is **calculated from AccountHistory** (latest entry's running_total)
- `auto_save_amount` for bills is deducted **per paycheck** (bi-weekly)

---

## 🔄 Rollover System - Money Flow

### The ONLY Rollovers That Exist
1. **Week 1 → Week 2** (one transaction per pay period)
2. **Week 2 → Emergency Fund** (one transaction per pay period)

**NO other rollovers exist!** Do not create Week 2→Week 3 or Week→Bill rollovers.

### Rollover Calculation Logic
```python
# Week 1 rollover (to Week 2)
week1_remaining = week1.running_total - week1_spending
rollover_transaction = create(
    type=ROLLOVER,
    amount=week1_remaining,  # Can be negative (deficit)
    week_number=week2.week_number,  # ⚠️ Assigned to RECEIVING week
    date=week1.end_date,
    description=f"Rollover from Week {week1.week_number}"
)

# Week 2 rollover (to savings)
week2_remaining = week2.running_total + week1_rollover - week2_spending
rollover_transaction = create(
    type=SAVING,
    amount=week2_remaining,
    account_id=emergency_fund.id,
    week_number=week2.week_number,
    date=week2.end_date,  # ⚠️ May be future date!
    description=f"End-of-period surplus from Week {week2.week_number}"
)
```

**Critical Details:**
- Rollovers are **created immediately** when paycheck added (live rollover system)
- Week 2→Savings rollover dated to Week 2 end date (may be **future date**)
- Rollovers **recalculate automatically** when spending changes
- Week 1→Week 2 transaction is assigned to **Week 2** (receiving week)
- Only **one rollover transaction per type per period** (updates in-place, no duplicates)

### Preventing Infinite Loops
```python
# In transaction_manager.py
self.set_auto_rollover_disabled(True)  # Before creating rollover
# ... create rollover transaction ...
self.set_auto_rollover_disabled(False)  # After creation

# In add_transaction()
if is_rollover_transaction(transaction):
    return  # Skip triggering recalculation for rollovers
```

---

## 🚨 Common Miscommunications & Gotchas

### Terminology Clarifications
| User Says | User Means | NOT |
|-----------|------------|-----|
| "Balance" | `AccountHistory.running_total` (latest entry) | `Account.balance` (doesn't exist) |
| "Week number" | Calendar week (1-52) | Paycheck number (1, 2, 3...) |
| "Rollover" | Week1→Week2 or Week2→Savings | Any transfer between accounts |
| "Starting balance" | AccountHistory entry with `transaction_id=NULL` | First transaction |
| "Week starting amount" | `running_total + rollover_in - rollover_out` | Just `running_total` |

### Variable Naming Patterns
```python
# Week calculations
week.running_total          # Base allocation (half of spendable)
week_starting_amount        # Base + rollovers (display value)
week_current_amount         # Starting - spending
week_daily_budget           # Current / days_remaining

# AccountHistory
history_entry.change_amount      # Signed (+ or -)
history_entry.running_total      # Cumulative balance
transaction.amount               # Always positive

# Paycheck vs Week
paycheck_number = (week_number + 1) // 2  # 1, 2, 3...
week_position = "first" if week_number % 2 == 1 else "second"
```

### Data Type Expectations
- **Dates:** Always `datetime.date` objects (NOT strings, NOT datetime)
- **Amounts:** Always `float` (NOT Decimal, NOT int)
- **Week numbers:** Always `int` calendar week (NOT paycheck number)
- **Boolean flags:** Use `True`/`False` (NOT 1/0)

---

## 🐛 Critical Bugs Fixed (Learn From These!)

### Bug 1: AccountHistory Running Total Corruption
**Symptom:** Line plots showing wrong balances ($52.50 - $35.00 = $49.50 instead of $17.50)

**Root Cause:**
```python
# WRONG (in update_transaction_change):
self._update_running_totals_from_entry(history_entry, change_difference)
history_entry.change_amount = new_change_amount  # Too late! Recalc used old value

# CORRECT:
history_entry.change_amount = new_change_amount  # Update FIRST
history_entry.transaction_date = new_date
self._update_running_totals_from_entry(history_entry, 0)  # Then recalculate
```

**Lesson:** Always update data BEFORE triggering recalculations that depend on it.

**Fix Script:** `fix_running_totals.py` - recalculates all AccountHistory running totals

---

### Bug 2: Negative Sign Flipping on Bill Edits
**Symptom:** User edits bill payment from -$35 to -$50 → flips to +$50

**Root Cause:** Bills display `AccountHistory.change_amount` (negative for payments) but save to `Transaction.amount` (always positive). Missing conversion.

**Fix:**
```python
# In save logic (bills tab):
if tab_name == "bills":
    updates["amount"] = abs(amount)  # Always store positive in Transaction

# In display logic:
display_amount = history_entry.change_amount  # Shows negative for payments
```

**Lesson:** `Transaction.amount` and `AccountHistory.change_amount` have different sign conventions - always convert!

---

### Bug 3: Week Display Using Date Range Instead of week_number
**Symptom:** Week 1 showing Week 2's rollover (backwards flow)

**Root Cause:** Loading transactions with `get_transactions_by_date_range()` instead of `get_transactions_by_week()`. Rollover dated to Week 1 end date but assigned to Week 2.

**Fix:**
```python
# WRONG:
transactions = get_transactions_by_date_range(week.start_date, week.end_date)

# CORRECT:
transactions = get_transactions_by_week(week.week_number)
```

**Lesson:** Use `week_number` field for week-specific queries, NOT date ranges (rollovers have week 1 dates but belong to week 2).

---

### Bug 4: Starting Balance Dated After Transactions
**Symptom:** First transaction shows `running_total = $92.72` instead of `$4296.73`

**Root Cause:** Starting balance entry dated 2025-10-12, but first transaction dated 2024-09-22. AccountHistory sorted by date, so starting balance came LAST.

**Fix:**
```python
# Always date starting balance BEFORE first transaction
earliest_transaction = min(transactions, key=lambda t: t.date)
starting_balance_date = earliest_transaction.date - timedelta(days=1)

# Or use this pattern:
if transaction_date < starting_balance_date:
    # Adjust starting balance date to day before transaction
    starting_balance.transaction_date = transaction_date - timedelta(days=1)
    recalculate_account_history(account_id)
```

**Lesson:** Starting balance must ALWAYS be the first chronological entry in AccountHistory.

---

## 🏗️ Architecture Patterns (Do This, Not That)

### Getting Account/Bill Balances
```python
# ✅ CORRECT:
balance = account.get_current_balance()  # Queries AccountHistory

# ❌ WRONG:
balance = account.balance  # Doesn't exist!
balance = account.running_total  # Also doesn't exist!
```

### Creating Transfers
```python
# Week → Account transfer (single transaction)
transaction = create_transaction(
    type=SAVING,
    amount=100.00,  # Positive
    week_number=current_week,
    account_id=target_account.id,
    description=f"Transfer to {target_account.name}"
)

# Account → Week transfer (single transaction, negative)
transaction = create_transaction(
    type=SAVING,
    amount=-100.00,  # Negative (withdrawal)
    week_number=current_week,
    account_id=source_account.id,
    description=f"Transfer from {source_account.name}"
)

# Account → Account transfer (TWO transactions required!)
create_transaction(type=SAVING, amount=-100, account_id=source.id, ...)
create_transaction(type=SAVING, amount=+100, account_id=target.id, ...)
```

### Triggering Rollover Recalculation
```python
# ✅ CORRECT (after adding/editing spending):
if transaction.transaction_type in [TransactionType.SPENDING, TransactionType.SAVING]:
    if transaction.week_number:
        self.trigger_rollover_recalculation(transaction.week_number)

# ❌ WRONG (causes infinite loop):
self.trigger_rollover_recalculation(transaction.week_number)  # For ALL transaction types
```

### Querying Transactions for Weeks
```python
# ✅ CORRECT:
transactions = transaction_manager.get_transactions_by_week(week_number)

# ❌ WRONG (misses rollovers):
transactions = transaction_manager.get_transactions_by_date_range(
    week.start_date, week.end_date
)
```

### Updating AccountHistory
```python
# ✅ CORRECT (auto-propagates running totals):
account_history_manager.add_transaction_change(
    transaction_id=trans.id,
    account_id=account.id,
    account_type="savings",
    change_amount=100.00,  # Signed!
    transaction_date=trans.date
)

# ❌ WRONG (manual running_total = corruption):
history_entry = AccountHistory(
    transaction_id=trans.id,
    running_total=old_total + 100.00,  # DON'T DO THIS!
    ...
)
```

---

## 📁 File Organization & Key Locations

### Services (Business Logic)
- `services/transaction_manager.py` - CRUD operations, rollover triggers
  - `add_transaction()` - Creates transaction + AccountHistory entry
  - `trigger_rollover_recalculation()` - Calls PaycheckProcessor
  - `get_transactions_by_week()` - ✅ Use this for week queries
  - `get_transactions_by_date_range()` - ⚠️ Don't use for weeks (rollover issue)

- `services/paycheck_processor.py` - Paycheck splitting, rollover creation
  - `split_paycheck()` - Deducts bills, splits remaining 50/50
  - `recalculate_period_rollovers()` - Main rollover recalc entry point
  - `_create_live_week1_to_week2_rollover()` - Week 1→2 transaction
  - `_create_live_week2_to_savings_rollover()` - Week 2→Savings transaction

- `services/analytics.py` - Spending analysis, category breakdowns
- `services/reimbursement_manager.py` - Reimbursements CRUD (separate from budget)
- `services/workspace_calculator.py` - Scratch Pad formula engine

### Models (Database Tables)
- `models/transactions.py` - Transaction table + TransactionType enum
- `models/account_history.py` - AccountHistory table + manager
  - `add_transaction_change()` - Add entry, auto-update running totals
  - `_update_running_totals_from_entry()` - Propagate changes forward
  - `get_current_balance()` - Latest entry's running_total
  - `recalculate_account_history()` - Full recalc (for fixing corruption)

- `models/accounts.py` - Savings accounts table
- `models/bills.py` - Bills table
- `models/weeks.py` - Weeks table
- `models/reimbursements.py` - Reimbursements table (separate tracking)

### Views (UI Tabs)
- `views/dashboard.py` - Main dashboard with pie charts, metrics
- `views/bills_view.py` - Bills management with AccountHistory integration
- `views/savings_view.py` - Savings accounts with AccountHistory integration
- `views/weekly_view.py` - Weekly budget planning, transaction tables
- `views/categories_view.py` - Category breakdown with correlation plots
- `views/year_overview_view.py` - YoY financial analysis (10+ charts)
- `views/transactions_view.py` - Advanced 4-tab inspection interface (optional)
- `views/taxes_view.py` - Tax tracking (optional, toggleable)
- `views/reimbursements_view.py` - Work travel expense tracking
- `views/scratch_pad_view.py` - Excel-like workspace with formulas

### Dialogs (views/dialogs/)
- `add_transaction_dialog.py` - Add spending/saving/reimbursement
- `add_paycheck_dialog.py` - Process bi-weekly paycheck
- `pay_bill_dialog.py` - Pay bill from bill account
- `transfer_dialog.py` - Transfer between accounts/bills/weeks
- `settings_dialog.py` - App settings, theme, toggles

### Widgets (views/widgets/ - Reusable Components)
- `chart_widget.py` - Matplotlib chart widgets (pie, line, bar, etc.)
- `theme_selector.py` - Theme dropdown selector
- `bill_row_widget.py` - Bill display in Bills tab
- `account_row_widget.py` - Account display in Savings tab

### Test Scripts (test_scripts/ - Not Part of App)
- Debug, testing, migration, and data import utilities
- Safe to delete entire folder without affecting app functionality
- See ReadMe2.txt for complete list

---

## 🎨 Theme System

### Theme Structure
```python
# themes/theme_manager.py
class ThemeManager:
    themes = {
        "dark": {...},
        "light": {...},
        "coffee": {...},
        "excel_blue": {...},
        "cyberpunk": {...}
    }
```

**Color Keys (all themes must have):**
- `background`, `surface`, `surface_variant`
- `text_primary`, `text_secondary`
- `primary`, `primary_dark`, `secondary`, `accent`, `accent2`
- `error`, `warning`, `success`, `info`
- `border`, `hover`, `selected`
- `chart_colors` (array of 10+ colors for categories)

**Font Keys:**
- `main`, `title`, `header`, `button`, `button_small`

### Theme Change Pattern
```python
# In any view that needs theme updates:
def __init__(self):
    theme_manager.theme_changed.connect(self.on_theme_changed)

def on_theme_changed(self, theme_id):
    colors = theme_manager.get_colors()
    # Update all styled widgets
    self.setStyleSheet(f"background-color: {colors['background']};")
    # Refresh charts
    self.refresh()
```

**Common Mistake:** Setting colors in `init_ui()` but not in `on_theme_changed()` - colors won't update on theme switch!

---

## 🧮 Scratch Pad Formula System

### Supported Functions
```python
# Built-in functions
SUM(A1:A10)                    # Sum range
AVERAGE(B2:D5)                 # Average range
CURRENT_DATE()                 # Today's date

# Live data integration
GET(account_name, property)    # Pull from accounts/bills

# Account properties: balance, goal, auto_save
# Bill properties: balance, amount, frequency, type, auto_save, variable
```

### Formula Evaluation Gotchas
- All formulas start with `=`
- Cell references are case-insensitive (A1 = a1)
- GET function returns **numbers, strings, or dates** depending on property
- String properties (frequency, type) can't be used in math operations
- Circular references detected and blocked
- Empty cells evaluate to 0 in formulas

### Persistence
- Saved to `scratch_pad_workspace.json`
- Format: `{"cells": {"A1": {"formula": "...", "type": "...", "format": "..."}}}`
- Auto-saves on cell edit, format change, app exit

---

## 🔢 Week Number Calculations

### Calendar Week vs Paycheck Number
```python
# Week numbering
calendar_week = 1-52  # ISO week number
paycheck_number = (calendar_week + 1) // 2  # 1, 2, 3...

# Week position in pay period
is_week1 = (calendar_week % 2) == 1  # Odd = first week
is_week2 = (calendar_week % 2) == 0  # Even = second week

# Example:
Week 59 → Paycheck 30, first week
Week 60 → Paycheck 30, second week
Week 61 → Paycheck 31, first week
```

### Week Display Calculations
```python
# Week starting amount
rollover_in = get_rollover_to_week(week.week_number)  # From previous week
rollover_out = get_rollover_from_week(week.week_number)  # To next week/savings
starting = week.running_total + rollover_in - rollover_out

# Week current amount
spending = sum(t.amount for t in week_transactions if t.is_spending)
current = starting - spending

# Daily budget
days_remaining = (week.end_date - today).days
daily = current / max(days_remaining, 1)  # Avoid division by zero
```

---

## 📊 Analytics & Filtering

### Normal Spending Filter
- `Transaction.include_in_analytics` (boolean) determines if "normal"
- User can toggle "Normal Spending Only" in Dashboard
- Affects: Pie charts, histograms, trend lines, category breakdowns
- Does NOT affect: Current week pie chart (always shows all), year overview boxes

### Time Frame Filter
- Settings: "All Time", "Last Year", "Last Month", "Last 20 Entries"
- Affects: Timeline charts (line charts, stacked area charts)
- Does NOT affect: Summary charts (pie charts, heatmaps, box plots)

### Category Color Consistency
- Categories sorted **alphabetically** for color assignment
- Same category = same color across all tabs/charts
- Color array cycles if more categories than colors
- Implemented in: `get_consistent_category_order()` and `get_consistent_category_colors()`

---

## 💰 Reimbursements System

### Key Principle
**Reimbursements are SEPARATE from budget** - they:
- Do NOT reduce weekly spending money
- Do NOT appear in spending calculations
- Do NOT affect account balances
- ONLY appear in weekly view for bank reconciliation (grayed out, italic)

### Lifecycle States
1. Pending Submission
2. Awaiting Payment (Submitted)
3. Reimbursed
4. Partially Reimbursed
5. Denied

**Auto-date tracking:**
- `submitted_date` set when state → "Awaiting Payment"
- `reimbursed_date` set when state → "Reimbursed" or "Partially Reimbursed"

### Dual Categorization
- **Tag/Location:** Trip identifier ("Whispers25", "NYC24") - for filtering
- **Category:** Expense type ("Hotel", "Transport", "Food") - for analysis

---

## 🚫 Anti-Patterns (Don't Do These!)

### Database Operations
```python
# ❌ NEVER:
account.balance = 500.00  # Field doesn't exist
week.running_total += rollover_amount  # Don't modify running_total
history_entry.running_total = calculated_value  # Let auto-update handle it

# ✅ ALWAYS:
balance = account.get_current_balance()
# running_total is set once during paycheck split, never modified
# AccountHistory auto-calculates running_total
```

### Transaction Creation
```python
# ❌ NEVER:
transaction = Transaction(
    transaction_type=TransactionType.BILL_PAY,
    amount=-35.00  # Wrong! Amount is always positive
)

# ✅ ALWAYS:
transaction = Transaction(
    transaction_type=TransactionType.BILL_PAY,
    amount=35.00  # Positive, direction from type + AccountHistory sign
)
```

### Week Queries
```python
# ❌ NEVER (for weekly view):
transactions = get_transactions_by_date_range(week.start_date, week.end_date)

# ✅ ALWAYS (for weekly view):
transactions = get_transactions_by_week(week.week_number)
```

### Rollover Creation
```python
# ❌ NEVER:
# Don't create Week 2 → Week 3 rollovers
# Don't create Week → Bill rollovers
# Don't create multiple rollover transactions per period

# ✅ ALWAYS:
# Only Week 1 → Week 2
# Only Week 2 → Emergency Fund
# One transaction per rollover type per period (update in-place)
```

---

## 🔧 Utility Scripts & Tools

**Note:** All utility scripts moved to `test_scripts/` folder (can be deleted without affecting app).

### Database Fix Scripts (in test_scripts/)
- `fix_running_totals.py` - Recalculate all AccountHistory running totals
- `fix_starting_balance_date.py` - Adjust starting balance dates to before first transaction
- `debug_account_history.py` - Inspect AccountHistory for debugging

### When to Run Fix Scripts
- After AccountHistory corruption (wrong balances in line plots)
- After importing historical data (starting balance might be dated wrong)
- After database schema migrations affecting AccountHistory

---

## 📝 Code Comment Conventions

### What to Comment
```python
# ✅ Good comments:
# CRITICAL: Week.running_total NEVER includes rollovers
# HACK: Using abs() here because Transaction.amount is always positive
# TODO: Implement paycheck editing with auto-recalc (Feature 4.5)
# NOTE: Rollover assigned to RECEIVING week, not source week

# ❌ Bad comments:
# Add 100 to balance
# Loop through transactions
# Calculate total
```

### Special Markers
- `# CRITICAL:` - Violating this causes bugs
- `# HACK:` - Workaround for technical limitation
- `# TODO:` - Future work, reference PROJECT_PLAN.md feature number
- `# NOTE:` - Important non-obvious behavior
- `# FIXME:` - Known issue, needs proper fix
- `# ⚠️` - Warning emoji for inline gotchas

---

## 🎯 Testing Patterns

### Manual Testing Checklist After Changes
1. Add transaction → Check rollover recalculated
2. Edit transaction → Check AccountHistory running totals correct
3. Delete transaction → Check balances update
4. Switch tabs → Check data refreshes
5. Change theme → Check all colors update
6. Add paycheck → Check Week 1/Week 2 allocations correct

### Edge Cases to Test
- Negative rollovers (overspending)
- Starting balance before/after first transaction
- Multiple edits to same transaction
- Switching weeks during pay period
- Abnormal transactions excluded from analytics

---

## 🔮 Known Limitations & Future Work

### Not Yet Implemented
- **Paycheck editing with auto-recalc** (Feature 4.5 in PROJECT_PLAN.md)
  - Currently paychecks are locked in Transactions tab
  - Editing would require recalculating all allocations and rollovers

- **Rules & Automation System** (Phase 3 - RULES_PLANNING.md)
  - Goals, Warnings, Automations
  - Currently 50% done (Reimbursements complete, Rules pending)
  - On hold while doing Phase 4 polish

### Performance Optimizations Not Done
- Query limiting (show last N entries)
- Conditional refresh (timestamp checking)
- Lazy loading tabs
- See Feature 4.4 in PROJECT_PLAN.md

---

## 📞 When to Ask User for Clarification

### Always Confirm Before:
- Deleting any documentation files
- Changing database schema
- Modifying rollover calculation logic
- Adding new transaction types
- Changing week numbering system

### Safe to Assume:
- Bug fixes (if logic is clearly wrong)
- UI polish (colors, spacing, fonts)
- Theme updates (adding missing colors)
- Code comments and documentation
- Test scripts and debugging tools

---

## 🔚 Session Wrap-Up: Updating Documentation

**When the user says "update documentation files as needed" at end of session:**

### ❌ **DON'T Add (Bloat):**
- Session-by-session changelogs (outdated quickly)
- Temporary organizational changes (moving test files)
- Minor code tweaks that don't affect architecture
- Detailed play-by-play of what we just did
- Duplicate information already in PROJECT_PLAN.md

### ✅ **DO Add (Value):**
- **New bugs discovered** → PROJECT_PLAN.md Phase 4 tracking table
- **New anti-patterns learned** → ReadMeLLM.md Anti-Patterns section
- **Architecture changes** → ReadMe2.txt relevant section
- **New critical gotchas** → ReadMeLLM.md Database/Architecture sections
- **Fixed bugs with lessons** → ReadMeLLM.md Critical Bugs Fixed section
- **Major file structure changes** → ReadMe2.txt Project Structure

### 🎯 **The Test:**
Before adding to documentation, ask:
1. **Will this help in 6 months?** (No = don't add)
2. **Is this already documented elsewhere?** (Yes = don't duplicate)
3. **Does this change behavior or just organization?** (Organization = minimal update)
4. **Would a new LLM need this to understand the codebase?** (No = skip ReadMeLLM.md)

### 📝 **Example Session (2025-11-26):**
**What we did:**
- ✅ Created ReadMeLLM.md (NEW file = document in ReadMe2.txt ✓)
- ✅ Restructured ReadMe2.txt (Major change = note in Recent Changes ✓)
- ✅ Deleted TROUBLESHOOT.md, SESSION_NOTES.md (Cleanup = no doc needed ✗)
- ✅ Updated PROJECT_PLAN.md with Phase 4 bugs (Already in PROJECT_PLAN = no further update ✗)
- ✅ Moved test scripts to test_scripts/ folder (Organization = 1-line mention ✓)

**Updates made:**
1. ReadMe2.txt - Added test_scripts/ folder to Project Structure (1 paragraph)
2. ReadMeLLM.md - Added test_scripts/ note to File Organization (1 line)
3. ReadMeLLM.md - Added this Session Wrap-Up section (guidance for future)

**Updates NOT made (correctly avoided bloat):**
- ❌ README.md - Test scripts not user-facing
- ❌ PROJECT_PLAN.md - Already up-to-date with Phase 4
- ❌ Detailed changelog of today's work - Not valuable in 6 months

---

**End of ReadMeLLM.md**
