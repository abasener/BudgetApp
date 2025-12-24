# Transactions Tab Roadmap

## Current Status: Save Logic Implemented

**Last Updated:** December 23, 2025

---

## Completed Work

### Phase 1: Display Refactoring (COMPLETE)

- [x] Sub-tabs restructured: Bills+Savings merged into Accounts, new Transfers tab added
- [x] All 4 tabs query Transaction table directly (consistent pattern)
- [x] Transaction IDs tracked for each row
- [x] Transfers tab stores tuple `(source_id, dest_id)` for paired transactions
- [x] Info button added with field descriptions for each sub-tab
- [x] Accounts tab loads from Transaction directly (was using AccountHistory indirectly)
- [x] `transfer_group_id` field links Account-to-Account transfer pairs

### Phase 2: Save Logic (COMPLETE)

- [x] Accounts tab save handler with Movement -> amount sign conversion
- [x] Spending tab save handler with category creation support
- [x] Paycheck tab save handler with date/amount recalculation
- [x] Transfers tab save handler with From/To validation
- [x] Partial field saves (valid fields save even if one field fails)
- [x] Non-editable columns enforced in UI
- [x] Fixed dropdown for Movement (Deposit/Withdrawal/Payment)
- [x] Editable dropdowns for Account, Category, From, To fields

### Current Sub-Tab Structure

| Tab | Shows | Filter Logic |
|-----|-------|--------------|
| **Accounts** | Week <-> Account transfers, bill payments | `account_id OR bill_id` is set, `transfer_group_id` is NULL |
| **Paycheck** | Paychecks | `type = INCOME` |
| **Spending** | Regular spending, rollovers | `type = SPENDING or ROLLOVER` |
| **Transfers** | Account <-> Account transfers | `transfer_group_id` is set (one row per pair) |

### Column Structure

**Accounts:** `[ID][Locked][Date][Account][Movement][Amount][Type][Week][Manual Notes][Auto Notes]`

**Paycheck:** `[ID][Earned Date][Start Date][Amount][Type][Week][Locked][Manual Notes][Auto Notes]`

**Spending:** `[ID][Date][Amount][Category][Type][Abnormal][Paycheck][Week][Locked][Manual Notes][Auto Notes]`

**Transfers:** `[ID][Date][Amount][From][To][Week][Locked][Manual Notes][Auto Notes]`

---

## Implementation Details

### Key Editing Principles

1. **Row-level locking**: If a row is locked (shows 🔒), NO fields in that row can be edited. Lock overrides everything.
2. **Column consistency**: All non-locked rows treat each column the same way (Amount in row 1 behaves like Amount in row 6).
3. **Type is derived**: Type auto-updates based on account type (bill -> bill_pay, savings -> saving).
4. **Admin-level access**: Major changes allowed (swapping accounts, changing amounts) as long as they're safe.
5. **Partial saves**: If one field fails validation, other valid fields still save.

### Editable Fields by Tab (non-locked rows only)

| Tab | Editable | Auto-calculated (cannot edit directly) |
|-----|----------|----------------------------------------|
| **Accounts** | Date, Account, Movement, Amount, Manual Notes | ID, Locked, Type, Week, Auto Notes |
| **Paycheck** | Earned Date, Start Date, Amount, Manual Notes | ID, Locked, Type, Week, Auto Notes |
| **Spending** | Date, Amount, Category, Abnormal, Manual Notes | ID, Locked, Type, Paycheck, Week, Auto Notes |
| **Transfers** | Date, Amount, From, To, Manual Notes | ID, Locked, Week, Auto Notes |

### Amount Sign Convention

**UI Layer (Display + Input):**
- All amounts DISPLAYED as **positive** to the user
- Movement column (Deposit/Withdrawal/Payment) or From/To indicates direction
- User enters **positive** values only
- If user enters negative, code takes `abs()` of the value

**Database Layer (Storage):**
- Amount can be **positive or negative** depending on transaction type
- Sign is determined by Movement type, not user input

| Scenario | Type | User Enters | DB Stores | get_change_amount_for_account() |
|----------|------|-------------|-----------|----------------------------------|
| Deposit INTO savings | SAVING | $100 | +$100 | +$100 (money into account) |
| Withdrawal FROM savings | SAVING | $100 | -$100 | -$100 (money out of account) |
| Bill payment | BILL_PAY | $500 | +$500 | -$500 (inverted - money out) |
| Transfer source | SAVING | $200 | -$200 | -$200 (money out) |
| Transfer destination | SAVING | $200 | +$200 | +$200 (money in) |
| Rollover deficit | ROLLOVER | N/A | -$50 | N/A (week overspent) |

### Validation Rules

| Field | Validation | Error Handling |
|-------|------------|----------------|
| **Amount** | Always display positive, sign from Movement/From-To | Warning in testing mode if user enters negative |
| **Account/From/To** | Must match existing bill or savings account name | Error if not found |
| **Category** | Can be new value (creates new category) | Always valid |
| **Date** | Valid MM/DD/YYYY format | Error if invalid format |
| **Movement** | Must be: Deposit, Withdrawal, or Payment | Error if invalid |
| **From/To same** | From and To cannot be the same account | Error on both fields |

### Dropdown Types

| Field | Dropdown Type | Behavior |
|-------|---------------|----------|
| **Movement** | Fixed | Only 3 options: Deposit, Withdrawal, Payment |
| **Account** | Editable | Shows existing accounts, can type new (but must exist on save) |
| **Category** | Editable | Shows existing categories, can type new (auto-creates) |
| **From/To** | Editable | Shows existing accounts, can type new (but must exist on save) |

---

## Special Handling by Tab

### Accounts Tab (`_validate_accounts_row`)

**Movement determines database values:**
- **Deposit**: `amount = +value`, `type = SAVING`
- **Withdrawal**: `amount = -value`, `type = SAVING`
- **Payment**: `amount = +value`, `type = BILL_PAY`

**Account lookup:**
- Checks savings accounts first, then bills
- Sets `account_id` OR `bill_id` (not both)

### Spending Tab (`_validate_spending_row`)

- Category can be any string (creates new if doesn't exist)
- Abnormal checkbox: `include_in_analytics = NOT checked`
- Amount always stored positive (spending is always an outflow)

### Paycheck Tab (`_validate_paycheck_row` + `_apply_paycheck_recalculation`)

**Simple edits:**
- Earned Date: Just updates transaction date, no recalculation

**Complex edits (Start Date or Amount changed):**

1. **Validate Start Date is Monday**
2. **Check for week overlap** with other paychecks
3. **Check for orphaned spending** - reject if any spending transactions would fall outside new date range
4. **Delete auto-generated transactions:**
   - Rollovers (type = ROLLOVER)
   - Auto-saves with descriptions containing "allocation for", "auto-", "end-of-period"
5. **Update week dates** for both weeks of the paycheck period
6. **Trigger rollover recalculation** via `transaction_manager.trigger_rollover_recalculation()`
7. **Recalculate percentage-based auto-saves** (if Amount changed) - e.g., if tax is 30% of income, recalculate tax allocation
   - ✅ IMPLEMENTED: `_recalculate_percentage_auto_saves()` finds transactions with "% of paycheck" in description
   - Extracts percentage from description, recalculates: `new_amount = percentage * new_paycheck_amount`
   - Fixed-amount auto-saves are unchanged (only percentage-based ones are updated)

**TRICKY BITS:**
- Must check BOTH week 1 and week 2 for overlaps
- Orphan check compares spending transaction dates against NEW date range
- Auto-save detection uses description pattern matching (may miss edge cases)
- Percentage-based auto-saves identified by "% of paycheck" in description

### Transfers Tab (`_validate_transfers_row`)

- **From/To must be different accounts** - error if same
- Updates TWO transactions for each row:
  - Source: negative amount, From account
  - Destination: positive amount, To account
- Both transactions share the same `transfer_group_id`

---

## Files Modified

**views/transactions_view.py:**
- `on_save_clicked()` - Routes to tab-specific handlers
- `_validate_accounts_row()` - Movement -> sign conversion
- `_validate_spending_row()` - Category can be new
- `_validate_paycheck_row()` - Marks for recalculation
- `_apply_paycheck_recalculation()` - Complex paycheck update logic
- `_validate_transfers_row()` - From/To same-account check
- `_build_transfer_source_updates()` - Negative amount for source
- `_build_transfer_dest_updates()` - Positive amount for dest
- `load_accounts_data()` - Editable dropdown for Account
- `load_spending_data()` - Editable dropdown for Category
- `load_transfers_data()` - Editable dropdowns for From/To

**views/transactions_table_widget.py:**
- `editable_dropdown_columns` - New tracking dict
- `set_columns()` - Accepts editable_dropdown_columns parameter
- `refresh_display()` - Renders editable comboboxes
- `get_row_data()` - Reads from editable comboboxes

---

## Testing Checklist

### Accounts Tab
- [ ] Edit Date -> Week auto-updates
- [ ] Edit Account -> Type auto-updates, validates name exists
- [ ] Edit Movement -> Amount sign updates correctly (Deposit=+, Withdrawal=-, Payment=+/BILL_PAY)
- [ ] Edit Amount -> Positive display, correct sign in DB based on Movement
- [ ] Invalid account name shows error, other fields still save
- [ ] Editable dropdown shows existing accounts

### Spending Tab
- [ ] Edit Date -> Week auto-updates
- [ ] Edit Amount -> Stored as positive
- [ ] Edit Category -> New category creates automatically
- [ ] Abnormal checkbox toggles `include_in_analytics`
- [ ] Locked rows (rollovers) cannot be edited
- [ ] Editable dropdown shows existing categories

### Paycheck Tab
- [ ] Edit Earned Date -> Just updates date, no recalculation
- [ ] Edit Amount -> Triggers rollover recalculation
- [ ] Edit Start Date -> Must be Monday (error if not)
- [ ] Edit Start Date -> Validates no overlap with other paychecks
- [ ] Edit Start Date -> Rejects if would orphan spending transactions
- [ ] Edit Start Date -> Deletes auto-saves and rollovers, recreates them

### Transfers Tab
- [ ] Edit updates BOTH linked transactions
- [ ] Edit Amount -> Source gets negative, dest gets positive
- [ ] Edit From/To -> Must be different accounts (error if same)
- [ ] From/To validation errors shown in testing mode only
- [ ] Editable dropdowns show existing accounts

### General
- [ ] Locked rows cannot be edited (UI enforces)
- [ ] Delete works for non-locked rows
- [ ] Partial saves: invalid field errors don't block valid fields
- [ ] Results dialog only shows in testing mode
- [ ] Refresh after save shows updated data
