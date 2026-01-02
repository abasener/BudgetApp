# TEMPORARY: Account Activation/Deactivation Feature Plan

> **STATUS:** In Progress
> **DELETE THIS FILE** when feature is complete and tested
> **Created:** 2026-01-01

---

## How to Use This Document

This document is a **working reference** for implementing the Account Activation/Deactivation feature. It is designed for LLM assistants (Claude, etc.) to pick up work mid-stream.

### Document Sections:
1. **Quick Context** - TL;DR of what we're building
2. **Decisions Made** - Finalized design choices (don't re-discuss)
3. **Key Files to Know** - What to read before coding
4. **Implementation Phases** - Step-by-step TODO with checkboxes
5. **Technical Details** - Code patterns, gotchas, edge cases
6. **Testing Checklist** - Manual verification steps
7. **Polish/Future Items** - Deferred improvements

### Workflow:
1. New chat? Read this file first, then check off completed items
2. Starting a phase? Mark items `[x]` as you complete them
3. Found a bug/gotcha? Add to "Discovered Issues" section
4. Finished? Delete this file and update PROJECT_PLAN.md

---

## 1. Quick Context

### What We're Building
Accounts (Bills and Savings) can have **active periods** instead of being always-on. This enables:
- Seasonal accounts (vacation savings April-August)
- Life transitions (rent account ends, mortgage account starts)
- Temporary goals (save for specific purchase, then deactivate)

### Core Behavior
- **Active account:** Receives automatic allocations from paychecks
- **Inactive account:** No auto-allocations, but manual transfers still allowed
- **Money handling:** When account ends, money stays in place (user transfers manually)
- **Default savings protection:** The default savings account (Emergency Fund) cannot be deactivated

---

## 2. Decisions Made

These are **finalized** - don't re-discuss unless there's a blocking issue.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Data structure | Period list (JSON) | Allows reactivation, preserves history under one name |
| Money on deactivation | Stays in account | Simple; user can transfer manually |
| Paycheck logic | Check `is_active_on(paycheck_date)` | Handles back-dated paychecks correctly |
| Inactive UI | Grey out, sink to bottom | Clear visual distinction |
| Hide toggle | Checkbox at top of tab | User can hide inactive accounts entirely |
| Reactivation | Allowed (adds new period) | Same account can be used year after year |
| Bills vs Savings | Same logic | Both use activation_periods |
| Default savings | Cannot deactivate | Must change default first (show error popup) |

---

## 3. Key Files to Know

### Must Read Before Coding
| File | Why |
|------|-----|
| `ReadMeLLM.md` | Critical gotchas, amount sign conventions, anti-patterns |
| `models/accounts.py` | Current Account model structure |
| `models/bills.py` | Current Bill model structure |
| `services/paycheck_processor.py` | Where auto-allocations happen (lines 142-285) |

### Reference Files
| File | Why |
|------|-----|
| `migrations/add_transfer_group_id.py` | Example of safe migration pattern |
| `migrations/backup_database.py` | Backup utility to use in migrations |
| `views/bills_view.py` | UI to modify for inactive display |
| `views/savings_view.py` | UI to modify for inactive display |
| `views/dialogs/settings_dialog.py` | Example of toggle checkbox pattern |

### Models Overview
```python
# Current Account model (models/accounts.py)
class Account(Base):
    id: int
    name: str (unique)
    is_default_save: bool  # True = Emergency Fund, cannot deactivate
    goal_amount: float
    auto_save_amount: float
    created_at: DateTime
    updated_at: DateTime
    # NEW FIELDS TO ADD:
    # activation_periods: JSON  # List of {start, end} dicts

# Current Bill model (models/bills.py)
class Bill(Base):
    id: int
    name: str
    bill_type: str
    payment_frequency: str
    typical_amount: float
    amount_to_save: float
    # ... other fields ...
    # NEW FIELDS TO ADD:
    # activation_periods: JSON  # List of {start, end} dicts
```

---

## 4. Implementation Phases

### Phase 1: Database Migration ✅ COMPLETE
Add `activation_periods` field to both Account and Bill tables.

- [x] **1.1** Create `migrations/add_activation_periods.py`
  - Backup database first (use existing backup_database.py)
  - Add `activation_periods` column to `accounts` table (JSON, nullable)
  - Add `activation_periods` column to `bills` table (JSON, nullable)
  - Initialize existing accounts/bills with `[{"start": created_at, "end": null}]`
  - Verify migration succeeded
  - Script must be idempotent (safe to run multiple times)

- [x] **1.2** Update `models/accounts.py`
  - Add `activation_periods = Column(JSON, default=list)` field
  - Add `is_active_on(date) -> bool` method
  - Add `is_currently_active -> bool` property
  - Add `current_period -> dict | None` property
  - Add `activate(start_date)` method
  - Add `deactivate(end_date)` method
  - Add `get_display_date_range() -> str` method for UI
  - Add `can_deactivate() -> tuple[bool, str]` method (checks is_default_save)

- [x] **1.3** Update `models/bills.py`
  - Same changes as accounts.py (copy-paste with adjustments)
  - `can_deactivate()` simpler (no default bill concept)

- [x] **1.4** Test migration on test database
  - Run migration script
  - Verify all existing accounts have activation_periods populated
  - Verify app still loads and functions normally

- [x] **1.5** Clean up old migration scripts
  - Removed: add_auto_save_amount.py, add_rollover_applied.py, fix_bills_schema.py, add_transfer_group_id.py
  - Kept: backup_database.py, add_activation_periods.py

### Phase 2: Paycheck Processing Logic ✅ COMPLETE
Update paycheck processor to respect activation periods.

- [x] **2.1** Update `services/paycheck_processor.py` - Bill allocations
  - Updated `update_bill_savings()` method (line 278-316)
  - Added check: `if not bill.is_active_on(transaction_date): continue`
  - Inactive bills are skipped, no auto-allocation created

- [x] **2.2** Update `services/paycheck_processor.py` - Account allocations
  - Updated `update_account_auto_savings()` method (line 318-357)
  - Added check: `if not account.is_active_on(transaction_date): continue`
  - Inactive accounts are skipped, no auto-allocation created

- [x] **2.3** Update `services/paycheck_processor.py` - Calculation methods
  - Updated `calculate_bills_deduction()` - now accepts `week_start_date` param
  - Updated `calculate_account_auto_savings()` - now accepts `week_start_date` param
  - Both skip inactive accounts/bills in their totals
  - Updated `process_new_paycheck()` to pass `week_start_date` to both methods

- [x] **2.4** Test paycheck processing
  - Verified `is_active_on()` logic with multiple date scenarios
  - Verified inactive accounts/bills are skipped in calculations
  - Main app imports successfully

**Key Design Notes:**
- Activation is checked against `week_start_date` (the start of the pay period)
- If account is deactivated mid-week, the entire paycheck still skips it
- Manual transfers/payments still work for inactive accounts (not blocked)

### Phase 2.5: Transactions Tab Paycheck Editing ✅ COMPLETE (Bug Fix)

Found and fixed a pre-existing bug where editing paycheck start date in Transactions tab
would delete auto-save transactions but not recreate them.

- [x] **2.5.1** Fixed `views/transactions_view.py` - `_apply_paycheck_recalculation()`
  - Added call to new `_recreate_auto_save_transactions()` after deletions
  - This runs after auto-saves are deleted and week dates updated

- [x] **2.5.2** Added `views/transactions_view.py` - `_recreate_auto_save_transactions()`
  - Uses PaycheckProcessor.update_bill_savings() and update_account_auto_savings()
  - These methods already have activation checks built in
  - Ensures both entry points (new paycheck dialog + transactions tab edit) respect activation

**Two Entry Points for Paycheck Processing:**
1. **Add Paycheck Dialog** → `PaycheckProcessor.process_new_paycheck()` → ✅ Has activation checks
2. **Transactions Tab Edit** → `_apply_paycheck_recalculation()` → ✅ Now uses PaycheckProcessor methods

**Amount-Only Change Behavior:**
- `_recalculate_percentage_auto_saves()` only updates EXISTING transactions
- It finds transactions with "% of paycheck" in description and recalculates amounts
- Does NOT create new transactions or check activation (transactions already exist)
- This is correct behavior - if user wants to rebuild for changed activation, use start date change

### Phase 3: UI - Bills Tab ✅ COMPLETE
Update Bills tab to show activation status.

- [x] **3.1** Update `views/bills_view.py` - Sorting
  - Modified `sort_bills()` to always put inactive bills at bottom
  - Separates active/inactive, sorts each group by current sort option, then combines

- [x] **3.2** Update `views/bills_view.py` - Visual styling
  - Grey out inactive bill rows (header shows "(Inactive)" suffix in grey)
  - `BillRowWidget` now accepts `is_active` parameter
  - Inactive bills show `text_secondary` color instead of `text_primary`

- [x] **3.3** Add toggle: "Hide inactive accounts"
  - Added "Hide inactive" checkbox to toolbar
  - Saves to `bills_hide_inactive` setting
  - Filters out inactive bills when checked

- [x] **3.4** Add activate/deactivate button
  - Added Status toggle button to BillRowWidget writeup section
  - Active state: `primary` background, `primary_dark` hover
  - Inactive state: `disabled` background, `border` hover
  - Button calls `bill.activate()` or `bill.deactivate()` with same-day flapping prevention

- [x] **3.5** Add Status field to Bill Editor Dialog ("See More")
  - Editable activation periods in format: `(M/D/YYYY, M/D/YYYY), (M/D/YYYY, current)`
  - Parsing and validation with clear error messages
  - Validation rules: start >= creation date, end >= start + 1 day, gaps >= 1 day, end <= today

- [x] **3.6** Add Status checkbox to Add Bill Dialog
  - "Start as Active" checkbox (defaults to checked)
  - Preview shows activation status
  - Creates appropriate activation_periods on save

- [x] **3.7** Default account protection
  - N/A for bills (no default bill concept)

### Phase 4: UI - Savings Tab ✅ COMPLETE
Same changes as Bills tab.

- [x] **4.1** Update `views/savings_view.py` - Sorting
  - Active accounts first, inactive at bottom
  - Same pattern as bills_view.py

- [x] **4.2** Update `views/savings_view.py` - Visual styling
  - Grey out inactive account rows
  - `AccountRowWidget` now accepts `is_active` parameter
  - Shows "(Inactive)" suffix in grey for inactive accounts
  - Default savings account still shows accent color when active

- [x] **4.3** Add toggle: "Hide inactive accounts"
  - Added "Hide inactive" checkbox to toolbar
  - Saves to `savings_hide_inactive` setting

- [x] **4.4** Add activate/deactivate button
  - Added Status toggle button to AccountRowWidget writeup section
  - Active state: `primary` background, `primary_dark` hover
  - Inactive state: `disabled` background, `border` hover
  - Button calls `account.activate()` or `account.deactivate()` with same-day flapping prevention

- [x] **4.5** Add Status field to Account Editor Dialog ("See More")
  - Editable activation periods in format: `(M/D/YYYY, M/D/YYYY), (M/D/YYYY, current)`
  - Parsing and validation with clear error messages
  - Validation rules: start >= creation date, end >= start + 1 day, gaps >= 1 day, end <= today
  - **Rule 5:** Default savings accounts cannot have last period end with a date (must be "current")

- [x] **4.6** Add Status checkbox to Add Account Dialog
  - "Start as Active" checkbox (defaults to checked)
  - Locks to Active when "Make this the default savings account" is checked
  - Preview shows activation status
  - Creates appropriate activation_periods on save

- [x] **4.7** Default account protection
  - **Add Account Dialog:** Activation checkbox locks to Active when is_default_save is checked
  - **Account Row Widget:** Toggle button disabled with ForbiddenCursor for default savings
    - Uses `secondary`/`accent` colors to distinguish from normal active buttons (`primary`/`primary_dark`)
  - **Account Editor Dialog:** Validation prevents deactivating default savings via Status field editing

### Phase 4.5: Additional Improvements ✅ COMPLETE

- [x] **4.5.1** Same-day flapping prevention
  - Updated `activate()` and `deactivate()` methods in both Account and Bill models
  - If activated then deactivated same day: remove the period entirely (no clutter)
  - If deactivated then reactivated same day: just remove the end date (undo deactivation)

- [x] **4.5.2** Update generate_test_data.py for activation periods
  - Added `created_at` field set properly for all test accounts/bills
  - Created diverse activation scenarios: active since start, inactive seasonal, reactivated with gap
  - Test data now includes Steam Sale Fund (inactive), Gym Membership (inactive), Streaming Bundle (new)

- [x] **4.5.3** Chart visualization for inactive periods
  - LineChartWidget now accepts `activation_periods` parameter
  - Draws dashed lines for segments during inactive periods, solid for active
  - Inactive accounts/bills use muted chart colors (75% disabled blend)

### Phase 5: Testing & Verification

- [ ] **5.1** Test paycheck allocations
  - [ ] Active account receives allocation
  - [ ] Inactive account does NOT receive allocation
  - [ ] Back-dated paycheck respects historical active status
  - [ ] Reactivated account receives allocation after reactivation date

- [ ] **5.2** Test manual transfers
  - [ ] Can transfer money OUT of inactive account
  - [ ] Can transfer money INTO inactive account (edge case but should work)
  - [ ] Can pay bill from inactive bill account

- [ ] **5.3** Test UI
  - [ ] Inactive accounts appear greyed at bottom
  - [ ] "Hide inactive" toggle works
  - [ ] Date ranges display correctly
  - [ ] Activate/deactivate buttons work

- [ ] **5.4** Test default account protection
  - [ ] Cannot deactivate Emergency Fund (or current default)
  - [ ] Error popup appears with clear message

- [ ] **5.5** Test edge cases
  - [ ] Account with zero balance can be deactivated
  - [ ] Account with money can be deactivated (money stays)
  - [ ] Multiple activation periods work correctly
  - [ ] App startup with inactive accounts works

### Phase 6: Polish (Deferred)

These are nice-to-haves, not required for initial release:

- [ ] **6.1** Money transfer prompt on deactivation
  - When user clicks "Deactivate" and balance > 0
  - Popup: "This account has $X. Would you like to transfer it?"
  - Options: [Transfer to: dropdown] [Leave in place] [Cancel]

- [x] **6.2** Grey out plots/charts for inactive accounts ✅ DONE
  - Charts use muted colors (75% disabled blend)
  - Dashed lines for inactive periods
  - Muted axis/tick colors for inactive items

- [ ] **6.3** Schedule future deactivation
  - "End Now" vs "Schedule End Date..."
  - Account remains active until end date passes

- [ ] **6.4** Visual indicator in other tabs
  - Dashboard cards for inactive accounts?
  - Probably not needed - they won't have recent activity anyway

- [ ] **6.5** Rebuild allocations for changed activation status (Low Priority)
  - Currently, editing paycheck amount only recalculates EXISTING transactions
  - If user deactivates an account after paycheck was created, old allocations remain
  - Workaround: Change start date to trigger full rebuild (even same date works)
  - Future: Add explicit "Rebuild Allocations" button on paycheck row
  - Or: Detect activation changes and prompt user to rebuild affected paychecks

---

## 5. Technical Details

### Data Structure: activation_periods

```python
# JSON field storing list of activation periods
# Each period has 'start' (required) and 'end' (nullable)
activation_periods = [
    {"start": "2024-01-15", "end": "2024-08-31"},  # First period (ended)
    {"start": "2025-04-01", "end": null}           # Second period (ongoing)
]

# Rules:
# - Periods should not overlap (validate on save)
# - 'end' = null means currently active
# - Empty list or null field = treat as inactive (edge case)
# - Dates stored as ISO strings "YYYY-MM-DD"
```

### Helper Methods to Add

```python
# In Account and Bill models:

def is_active_on(self, check_date: date) -> bool:
    """Check if account was active on a specific date"""
    if not self.activation_periods:
        return False

    for period in self.activation_periods:
        start = date.fromisoformat(period['start'])
        end = date.fromisoformat(period['end']) if period['end'] else None

        if start <= check_date:
            if end is None or check_date <= end:
                return True
    return False

@property
def is_currently_active(self) -> bool:
    """Check if account is currently active (today)"""
    return self.is_active_on(date.today())

@property
def current_period(self) -> dict | None:
    """Get the current active period, or None if inactive"""
    today = date.today()
    if not self.activation_periods:
        return None

    for period in self.activation_periods:
        start = date.fromisoformat(period['start'])
        end = date.fromisoformat(period['end']) if period['end'] else None

        if start <= today and (end is None or today <= end):
            return period
    return None

def activate(self, start_date: date = None):
    """Start a new activation period"""
    if start_date is None:
        start_date = date.today()

    if self.activation_periods is None:
        self.activation_periods = []

    # Add new period
    self.activation_periods.append({
        'start': start_date.isoformat(),
        'end': None
    })

def deactivate(self, end_date: date = None):
    """End the current activation period"""
    if end_date is None:
        end_date = date.today()

    # Find the current open period and close it
    if self.activation_periods:
        for period in self.activation_periods:
            if period['end'] is None:
                period['end'] = end_date.isoformat()
                break

def get_display_date_range(self) -> str:
    """Get human-readable date range for UI display"""
    if not self.activation_periods:
        return "Never active"

    # Get most recent period
    last_period = self.activation_periods[-1]
    start = date.fromisoformat(last_period['start'])
    end = date.fromisoformat(last_period['end']) if last_period['end'] else None

    start_str = start.strftime("%b %Y")  # e.g., "Apr 2024"

    if end is None:
        return f"Since {start_str}"
    else:
        end_str = end.strftime("%b %Y")
        return f"{start_str} - {end_str}"
```

### Migration Script Pattern

Follow the pattern in `migrations/add_transfer_group_id.py`:
1. Backup database first
2. Check if column exists (idempotent)
3. Add column if missing
4. Initialize data for existing rows
5. Verify migration succeeded
6. Print clear status messages

### Paycheck Date Context

When processing paychecks, use the **paycheck's start date** for activation checks, not `date.today()`. This handles:
- Back-dated paychecks (adding old paychecks that were missed)
- Paychecks added on Transactions tab for past dates
- Ensures historical accuracy

```python
# In paycheck_processor.py
def _update_bill_savings(self, paycheck_start_date, ...):
    for bill in all_bills:
        # Check if bill was active when this paycheck was earned
        if bill.is_active_on(paycheck_start_date):
            if bill.amount_to_save > 0:
                # ... existing allocation logic ...
```

---

## 6. Discovered Issues

> Add bugs, gotchas, and unexpected issues here as you find them

| Issue | Status | Notes |
|-------|--------|-------|
| (none yet) | | |

---

## 7. Migration Instructions for Production Machine

When ready to deploy to the machine with real data:

### Pre-Migration Checklist
- [ ] Commit all changes to GitHub on dev machine
- [ ] Pull latest code on production machine
- [ ] Close the BudgetApp if running

### Run Migration
```bash
# From BudgetApp directory:
python migrations/add_activation_periods.py
```

### Post-Migration Verification
- [ ] App launches without errors
- [ ] Bills tab loads correctly
- [ ] Savings tab loads correctly
- [ ] All accounts show as active (initial state)
- [ ] Adding a paycheck still works

### Rollback (if needed)
```bash
# Restore from backup created by migration
python migrations/backup_database.py restore backups/budget_app_backup_YYYYMMDD_HHMMSS.db
```

---

## 8. Completion Checklist

Before deleting this file:

- [ ] All Phase 1-5 items checked off
- [ ] Migration tested on both machines
- [ ] No items in "Discovered Issues" marked unresolved
- [ ] PROJECT_PLAN.md updated with feature completion
- [ ] ReadMeLLM.md updated if new gotchas discovered
- [ ] This file deleted

---

**End of Planning Document**
