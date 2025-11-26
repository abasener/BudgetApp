================================================================================
📘 BudgetApp V2 - Technical Reference for Developers
================================================================================
Last Updated: 2025-11-26
Audience: Developers working on the codebase
Detail Level: Architecture, file structure, key methods (not implementation details)

For LLM-specific gotchas and detailed implementation notes, see ReadMeLLM.md
For public-facing feature overview and setup, see README.md
For project roadmap and todos, see PROJECT_PLAN.md

================================================================================
📑 TABLE OF CONTENTS
================================================================================

Part 1: 🗄️  DATABASE SCHEMA QUICK REFERENCE
Part 2: 💰 MONEY FLOW SYSTEM OVERVIEW
Part 3: 🏗️  ARCHITECTURE & FILE STRUCTURE
Part 4: 🔄 ROLLOVER SYSTEM TECHNICAL SPECS
Part 5: 📊 ACCOUNT HISTORY SYSTEM
Part 6: 🎨 THEME & UI COMPONENTS
Part 7: 📝 RECENT CHANGES LOG

================================================================================
PART 1: 🗄️  DATABASE SCHEMA QUICK REFERENCE
================================================================================

This section lists ALL database tables and their fields for quick reference.
Refer to this when you can't remember field names or need to verify spelling.

───────────────────────────────────────────────────────────────────────────────
📋 TABLE: transactions
───────────────────────────────────────────────────────────────────────────────
Location: models/transactions.py

FIELDS:
  • id (int, PK)
  • transaction_type (str) - Values: "spending", "bill_pay", "saving", "income", "rollover"
  • week_number (int, FK → weeks.week_number) - Calendar week 1-52
  • amount (float) - ⚠️ ALWAYS POSITIVE (even for bill payments!)
  • date (Date) - Transaction date
  • description (str, nullable) - User description
  • category (str, nullable) - Spending category (e.g., "Groceries", "Gas")
  • include_in_analytics (bool) - Default True, filter abnormal spending
  • bill_id (int, FK → bills.id, nullable) - For bill payments/savings
  • bill_type (str, nullable) - Alternative to bill_id
  • account_id (int, FK → accounts.id, nullable) - For savings account transactions
  • account_saved_to (str, nullable) - Alternative to account_id
  • created_at (DateTime)
  • updated_at (DateTime)

RELATIONSHIPS:
  • week → Week (many-to-one)
  • bill → Bill (many-to-one)
  • account → Account (many-to-one)
  • history_entries → AccountHistory (one-to-many)

HELPER PROPERTIES:
  • is_spending, is_bill_pay, is_saving, is_income, is_rollover
  • affects_account (bool) - True if bill_id or account_id set
  • account_type (str) - "bill" or "savings"
  • get_change_amount_for_account() - Returns signed amount for AccountHistory

CRITICAL NOTES:
  ⚠️ amount is ALWAYS positive - direction determined by transaction_type
  ⚠️ week_number is calendar week (1-52), NOT paycheck number
  ⚠️ Bill payments: type=BILL_PAY, amount=positive, AccountHistory gets negative

───────────────────────────────────────────────────────────────────────────────
💼 TABLE: accounts (Savings Accounts)
───────────────────────────────────────────────────────────────────────────────
Location: models/accounts.py

FIELDS:
  • id (int, PK)
  • name (str, unique) - Account name (e.g., "Emergency Fund", "Vacation")
  • is_default_save (bool) - True for Emergency Fund (rollover target)
  • goal_amount (float) - Savings goal, 0 = no goal
  • auto_save_amount (float) - Auto-deducted per paycheck (after bills)
  • created_at (DateTime)
  • updated_at (DateTime)

RELATIONSHIPS:
  • transactions → Transaction (one-to-many, back-reference)

KEY METHODS:
  • get_current_balance(db_session) → float - Queries AccountHistory
  • get_account_history(db_session) → List[AccountHistory]
  • initialize_history(db_session, starting_balance, start_date)

COMPUTED PROPERTIES:
  • goal_progress_percent (float) - % toward goal
  • goal_remaining (float) - $ needed to reach goal
  • is_goal_reached (bool)
  • goal_excess (float) - $ saved beyond goal
  • running_total (float) - Backward compat, calls get_current_balance()

CRITICAL NOTES:
  ⚠️ NO balance field! Always use get_current_balance()
  ⚠️ Balance tracked via AccountHistory, not on model

───────────────────────────────────────────────────────────────────────────────
📄 TABLE: bills
───────────────────────────────────────────────────────────────────────────────
Location: models/bills.py

FIELDS:
  • id (int, PK)
  • name (str) - Bill name (e.g., "Rent", "Internet", "Taxes")
  • bill_type (str) - Category for grouping
  • payment_frequency (str) - "weekly", "monthly", "semester", "yearly", "other"
  • typical_amount (float) - Expected payment amount
  • amount_to_save (float) - Auto-deducted per bi-weekly paycheck
  • last_payment_date (Date, nullable) - Last payment date
  • last_payment_amount (float) - Last payment amount
  • is_variable (bool) - True for bills that vary (e.g., school)
  • notes (str, nullable) - Additional notes
  • created_at (DateTime)
  • updated_at (DateTime)

RELATIONSHIPS:
  • transactions → Transaction (one-to-many, back-reference)

KEY METHODS:
  • get_current_balance(db_session) → float - Queries AccountHistory
  • get_account_history(db_session) → List[AccountHistory]
  • initialize_history(db_session, starting_balance, start_date)
  • update_last_payment(payment_date, payment_amount)

COMPUTED PROPERTIES:
  • savings_progress_percent (float) - % of typical_amount saved
  • savings_needed (float) - $ needed to cover typical payment
  • is_fully_funded (bool) - True if saved >= typical_amount
  • is_overfunded (bool) - True if saved > typical_amount
  • running_total (float) - Backward compat, calls get_current_balance()

CRITICAL NOTES:
  ⚠️ NO balance field! Always use get_current_balance()
  ⚠️ amount_to_save is per bi-weekly paycheck (not monthly)

───────────────────────────────────────────────────────────────────────────────
📅 TABLE: weeks
───────────────────────────────────────────────────────────────────────────────
Location: models/weeks.py

FIELDS:
  • id (int, PK)
  • week_number (int, unique, indexed) - Calendar week 1-52
  • start_date (Date) - Monday of the week
  • end_date (Date) - Sunday of the week
  • running_total (float) - ⚠️ BASE ALLOCATION ONLY (no rollovers!)
  • rollover_applied (bool) - Track if rollover processed
  • created_at (DateTime)
  • updated_at (DateTime)

CRITICAL NOTES:
  ⚠️ running_total = BASE ALLOCATION from paycheck split (half of spendable)
  ⚠️ running_total NEVER includes rollover amounts!
  ⚠️ Rollovers are separate transactions (type=rollover)
  ⚠️ Display logic must ADD rollover transactions to get true starting amount
  ⚠️ DO NOT modify running_total to include rollovers - breaks rollover system!

EXAMPLE:
  Paycheck $4237.50, Bills $3328.59, Spendable $908.91
  • Week 57 running_total: $454.46 (half of $908.91)
  • Week 58 running_total: $454.46 (half of $908.91)
  • Week 58 gets rollover transaction: +$312.76 (SEPARATE from running_total)
  • Week 58 display starting: $454.46 + $312.76 = $767.22

───────────────────────────────────────────────────────────────────────────────
📊 TABLE: account_history
───────────────────────────────────────────────────────────────────────────────
Location: models/account_history.py

PURPOSE: Universal balance tracking for Bills and Savings accounts

FIELDS:
  • id (int, PK)
  • transaction_id (int, FK → transactions.id, nullable) - NULL for starting balance
  • account_id (int, indexed) - References bills.id or accounts.id
  • account_type (str, indexed) - "bill" or "savings"
  • change_amount (float) - ⚠️ SIGNED: negative=out, positive=in
  • running_total (float) - Cumulative balance after this change
  • transaction_date (Date) - ⚠️ MUST be chronologically ordered!
  • description (str, nullable) - For non-transaction entries
  • created_at (DateTime)
  • updated_at (DateTime)

RELATIONSHIPS:
  • transaction → Transaction (many-to-one)

CRITICAL NOTES:
  ⚠️ change_amount is SIGNED (not like Transaction.amount which is always positive)
  ⚠️ running_total AUTO-PROPAGATES forward when inserting historical entries
  ⚠️ Starting balance (transaction_id=NULL) MUST be dated BEFORE all transactions
  ⚠️ Entries are date-ordered - inserting out-of-order triggers recalculation
  ⚠️ NEVER manually set running_total - use AccountHistoryManager methods!

───────────────────────────────────────────────────────────────────────────────
💸 TABLE: reimbursements
───────────────────────────────────────────────────────────────────────────────
Location: models/reimbursements.py

PURPOSE: Track work travel expenses & temporary out-of-pocket costs
NOTE: Completely SEPARATE from budget - NOT included in spending calculations

FIELDS:
  • id (int, PK)
  • amount (float) - Amount spent
  • date (Date, indexed) - Purchase date
  • state (str) - "pending", "submitted", "reimbursed", "partial", "denied"
  • notes (str, nullable) - User description
  • category (str, nullable) - Expense type (e.g., "Hotel", "Transport")
  • location (str, nullable) - Trip/event tag (e.g., "Whispers25", "NYC24")
  • submitted_date (Date, nullable) - Auto-set when state → submitted
  • reimbursed_date (Date, nullable) - Auto-set when state → reimbursed/partial
  • created_at (DateTime)
  • updated_at (DateTime)

HELPER PROPERTIES:
  • is_pending, is_submitted, is_reimbursed, is_partial, is_denied
  • is_complete (bool) - True if reimbursed or denied
  • status_display (str) - User-friendly status

CRITICAL NOTES:
  ⚠️ Reimbursements NOT included in weekly spending totals
  ⚠️ Shown in Weekly tab (grayed out, italic) for bank reconciliation only
  ⚠️ Separate tracking system - does NOT affect account balances

================================================================================
PART 2: 💰 MONEY FLOW SYSTEM OVERVIEW
================================================================================

───────────────────────────────────────────────────────────────────────────────
🎯 CORE PROCESS
───────────────────────────────────────────────────────────────────────────────

1. Paycheck arrives (e.g., $4625)
2. Bills deducted first (e.g., $300)
3. Account auto-saves deducted (e.g., $0)
4. Remaining split 50/50 between Week 1 & Week 2 (e.g., $2162.50 each)
5. Week 1 rollover: Unspent → Week 2 immediately
6. Week 2 rollover: Unspent → Emergency Fund at period end
7. All rollovers recalculate dynamically when ANY transaction changes

───────────────────────────────────────────────────────────────────────────────
🔄 THE ONLY ROLLOVERS THAT EXIST
───────────────────────────────────────────────────────────────────────────────

1. Week 1 → Week 2 (one transaction per pay period)
2. Week 2 → Emergency Fund (one transaction per pay period)

NO other rollovers! No Week 2→Week 3, no Week→Bill rollovers.

───────────────────────────────────────────────────────────────────────────────
📊 BI-WEEKLY PERIOD LOGIC
───────────────────────────────────────────────────────────────────────────────

• Week 1 (odd week_number): 1, 3, 5, 7... → rollover to Week 2
• Week 2 (even week_number): 2, 4, 6, 8... → rollover to savings
• Periods: (Week 1, Week 2), (Week 3, Week 4), (Week 5, Week 6)...
• Week 2 rollover to savings happens immediately (live rollover system)

───────────────────────────────────────────────────────────────────────────────
💡 DYNAMIC BEHAVIOR (LIVE ROLLOVER SYSTEM)
───────────────────────────────────────────────────────────────────────────────

Rollovers created IMMEDIATELY when paycheck added:
• Week 1→Week 2 rollover: Created at paycheck time (dated to Week 1 end)
• Week 2→Savings rollover: Created at paycheck time (dated to Week 2 end, may be future!)

When spending changes:
• Add/edit/delete spending → triggers recalculate_period_rollovers()
• Week 1 spending changes → updates Week 1→Week 2 rollover
• Week 2 spending changes → updates Week 2→Savings rollover
• Works for historical transactions too (past dates)

───────────────────────────────────────────────────────────────────────────────
🧮 WEEK DISPLAY CALCULATIONS
───────────────────────────────────────────────────────────────────────────────

Week.running_total = BASE ALLOCATION (half of spendable, set once at paycheck time)

Week Starting Amount = running_total + rollover_in - rollover_out
Week Current Amount = Starting - Spending
Week Daily Budget = Current / max(days_remaining, 1)

CRITICAL: Week.running_total NEVER changes after paycheck split!

================================================================================
PART 3: 🏗️  ARCHITECTURE & FILE STRUCTURE
================================================================================

───────────────────────────────────────────────────────────────────────────────
📂 SERVICES (Business Logic)
───────────────────────────────────────────────────────────────────────────────

services/transaction_manager.py
  Purpose: CRUD operations, rollover triggers
  Key Methods:
    • add_transaction() - Creates transaction + AccountHistory entry
    • update_transaction() - Updates transaction, triggers rollover recalc
    • delete_transaction() - Deletes transaction, triggers rollover recalc
    • trigger_rollover_recalculation(week_number) - Calls PaycheckProcessor
    • get_transactions_by_week(week_number) - ✅ Use for weekly view
    • get_transactions_by_date_range(start, end) - ⚠️ Don't use for weeks (rollover issue)

services/paycheck_processor.py
  Purpose: Paycheck splitting, rollover creation/recalculation
  Key Methods:
    • split_paycheck() - Deducts bills, splits remaining 50/50
    • recalculate_period_rollovers(week_number) - Main rollover recalc entry point
    • _create_live_week1_to_week2_rollover() - Week 1→2 rollover
    • _create_live_week2_to_savings_rollover() - Week 2→Savings rollover

services/analytics.py
  Purpose: Spending analysis, category breakdowns, time filtering

services/reimbursement_manager.py
  Purpose: Reimbursements CRUD (separate from budget)

services/workspace_calculator.py
  Purpose: Scratch Pad formula engine (SUM, AVERAGE, GET, CURRENT_DATE)

───────────────────────────────────────────────────────────────────────────────
📂 MODELS (Database Tables)
───────────────────────────────────────────────────────────────────────────────

See Part 1 (Database Schema) for complete field listings.

models/transactions.py - Transaction table + TransactionType enum
models/account_history.py - AccountHistory table + AccountHistoryManager
models/accounts.py - Savings accounts
models/bills.py - Bills
models/weeks.py - Weeks
models/reimbursements.py - Reimbursements (separate tracking)

───────────────────────────────────────────────────────────────────────────────
📂 VIEWS (UI Tabs)
───────────────────────────────────────────────────────────────────────────────

views/dashboard.py - Main dashboard (pie charts, metrics, analytics)
views/bills_view.py - Bills management with AccountHistory line plots
views/savings_view.py - Savings accounts with AccountHistory line plots
views/weekly_view.py - Weekly budget planning, transaction tables
views/categories_view.py - Category breakdown, correlation plots
views/year_overview_view.py - YoY analysis (10+ charts)
views/transactions_view.py - Advanced 4-tab inspection (optional, toggleable)
views/taxes_view.py - Tax tracking (optional, toggleable)
views/reimbursements_view.py - Work travel expense tracking
views/scratch_pad_view.py - Excel-like workspace with formulas

───────────────────────────────────────────────────────────────────────────────
📂 DIALOGS (views/dialogs/)
───────────────────────────────────────────────────────────────────────────────

add_transaction_dialog.py - Add spending/saving/reimbursement
add_paycheck_dialog.py - Process bi-weekly paycheck
pay_bill_dialog.py - Pay bill from bill account
transfer_dialog.py - Transfer between accounts/bills/weeks
add_account_dialog.py - Add savings account (admin)
add_bill_dialog.py - Add bill (admin)
settings_dialog.py - App settings, theme, toggles

───────────────────────────────────────────────────────────────────────────────
📂 WIDGETS (Reusable UI Components)
───────────────────────────────────────────────────────────────────────────────

widgets/chart_widget.py - Matplotlib chart widgets (pie, line, bar, etc.)
widgets/theme_selector.py - Theme dropdown selector
widgets/bill_row_widget.py - Bill display in Bills tab
widgets/account_row_widget.py - Account display in Savings tab

───────────────────────────────────────────────────────────────────────────────
📂 THEMES (Visual Styling)
───────────────────────────────────────────────────────────────────────────────

themes/theme_manager.py - Theme system core
themes/assets/ - Theme-specific GIFs and images

Available Themes: dark, light, coffee, excel_blue, cyberpunk

───────────────────────────────────────────────────────────────────────────────
📂 TEST SCRIPTS (Not Part of App - Safe to Delete)
───────────────────────────────────────────────────────────────────────────────

test_scripts/ - Debug, test, and migration scripts
  • debug_*.py - Database inspection scripts
  • test_*.py - Feature testing scripts
  • check_*.py - Data validation scripts
  • fix_*.py - One-time database fix scripts
  • migrate_*.py - Schema migration scripts
  • import_real_data.py - Data import utility
  • widget_showcase.py - UI component showcase

Note: This folder can be deleted without affecting app functionality

================================================================================
PART 4: 🔄 ROLLOVER SYSTEM TECHNICAL SPECS
================================================================================

───────────────────────────────────────────────────────────────────────────────
🎯 ROLLOVER CREATION LOGIC
───────────────────────────────────────────────────────────────────────────────

Week 1 → Week 2 Rollover:
  • Type: ROLLOVER
  • Amount: Week1.running_total - week1_spending
  • week_number: Week2.week_number (assigned to RECEIVING week!)
  • Date: Week1.end_date
  • Description: f"Rollover from Week {week1.week_number}"

Week 2 → Savings Rollover:
  • Type: SAVING
  • Amount: Week2.running_total + week1_rollover - week2_spending
  • account_id: Emergency Fund ID
  • week_number: Week2.week_number
  • Date: Week2.end_date (may be future date!)
  • Description: f"End-of-period surplus from Week {week2.week_number}"

───────────────────────────────────────────────────────────────────────────────
♻️  INFINITE LOOP PREVENTION
───────────────────────────────────────────────────────────────────────────────

In transaction_manager.py:
  self.set_auto_rollover_disabled(True)  # Before creating rollover
  # ... create rollover transaction ...
  self.set_auto_rollover_disabled(False)  # After creation

In add_transaction():
  if is_rollover_transaction(transaction):
      return  # Skip triggering recalculation

───────────────────────────────────────────────────────────────────────────────
🔧 KEY FILE LOCATIONS
───────────────────────────────────────────────────────────────────────────────

services/paycheck_processor.py:
  • recalculate_period_rollovers(week_number) - Main entry point
  • _create_live_week1_to_week2_rollover() - Lines 481-506
  • _create_live_week2_to_savings_rollover() - Lines 508-535

services/transaction_manager.py:
  • trigger_rollover_recalculation() - Lines 244-253
  • delete_transaction() - Triggers recalc on delete
  • update_transaction() - Triggers recalc on edit

views/weekly_view.py:
  • Uses get_transactions_by_week() - NOT date range (line 482)
  • Week starting amount calculation - Lines 514-531

================================================================================
PART 5: 📊 ACCOUNT HISTORY SYSTEM
================================================================================

───────────────────────────────────────────────────────────────────────────────
🎯 PURPOSE
───────────────────────────────────────────────────────────────────────────────

AccountHistory tracks ALL balance changes for Bills and Savings accounts.
Every transaction that affects an account creates an AccountHistory entry.
Running totals are maintained in chronological order by transaction_date.

───────────────────────────────────────────────────────────────────────────────
🔧 KEY METHODS (AccountHistoryManager)
───────────────────────────────────────────────────────────────────────────────

get_account_history(account_id, account_type)
  • Returns all entries ordered by date

get_current_balance(account_id, account_type)
  • Returns latest entry's running_total

add_transaction_change(account_id, account_type, transaction_id, change_amount, date)
  • Adds entry, handles out-of-order insertion
  • AUTO-UPDATES all subsequent running_totals
  • Adjusts starting balance date if needed

update_transaction_change(transaction_id, new_change_amount, new_date)
  • Updates entry, recalculates all subsequent entries
  • CRITICAL: Updates change_amount BEFORE recalculating (Bug fix Nov 3, 2024)

delete_transaction_change(transaction_id)
  • Removes entry, adjusts all subsequent running_totals

recalculate_account_history(account_id, account_type)
  • Full recalc from scratch (for fixing corruption)

───────────────────────────────────────────────────────────────────────────────
⚙️  AUTO-UPDATE MECHANISM
───────────────────────────────────────────────────────────────────────────────

When transaction added/edited at ANY point in history:
1. Find insertion point in chronological order (by transaction_date)
2. Calculate running_total = previous_entry.running_total + change_amount
3. Update ALL subsequent entries' running_totals

Formula: running_total = prev_entry.running_total + current_entry.change_amount

This ensures historical edits propagate forward automatically!

───────────────────────────────────────────────────────────────────────────────
⚠️  STARTING BALANCE CRITICAL RULE
───────────────────────────────────────────────────────────────────────────────

Starting balance MUST be dated BEFORE all transactions!

If transaction added before starting balance date:
  • Starting balance auto-adjusts to day before earliest transaction
  • Triggers full recalculation of all running_totals

Check earliest transaction date before setting starting balance:
  earliest_transaction = min(transactions, key=lambda t: t.date)
  starting_balance_date = earliest_transaction.date - timedelta(days=1)

================================================================================
PART 6: 🎨 THEME & UI COMPONENTS
================================================================================

───────────────────────────────────────────────────────────────────────────────
🎨 THEME SYSTEM
───────────────────────────────────────────────────────────────────────────────

Location: themes/theme_manager.py

5 Built-in Themes: dark, light, coffee, excel_blue, cyberpunk

Required Color Keys (all themes):
  • background, surface, surface_variant
  • text_primary, text_secondary
  • primary, primary_dark, secondary, accent, accent2
  • error, warning, success, info
  • border, hover, selected
  • chart_colors (array of 10+ colors for categories)

Required Font Keys:
  • main, title, header, button, button_small

───────────────────────────────────────────────────────────────────────────────
🔄 THEME CHANGE PATTERN
───────────────────────────────────────────────────────────────────────────────

In any view that needs theme updates:

def __init__(self):
    theme_manager.theme_changed.connect(self.on_theme_changed)

def on_theme_changed(self, theme_id):
    colors = theme_manager.get_colors()
    # Update ALL styled widgets
    self.setStyleSheet(f"background-color: {colors['background']};")
    # Refresh charts
    self.refresh()

COMMON MISTAKE: Setting colors in init_ui() but NOT in on_theme_changed()

───────────────────────────────────────────────────────────────────────────────
📊 CATEGORY COLOR CONSISTENCY
───────────────────────────────────────────────────────────────────────────────

Categories sorted ALPHABETICALLY for color assignment.
Same category = same color across all tabs/charts.
Color array cycles if more categories than colors.

Implementation: get_consistent_category_order(), get_consistent_category_colors()

================================================================================
PART 7: 📝 RECENT CHANGES LOG
================================================================================

───────────────────────────────────────────────────────────────────────────────
2025-11-23 - Scratch Pad Tab
───────────────────────────────────────────────────────────────────────────────
✅ Added Excel-like workspace with formula support
✅ Formula engine: SUM(), AVERAGE(), GET(), CURRENT_DATE()
✅ GET function pulls live account/bill data
✅ Cell formatting system (H1, H2, Normal, Notes)
✅ Smart autocomplete for functions and account names
✅ Formula bar with error display and dependency highlighting
✅ JSON workspace persistence

───────────────────────────────────────────────────────────────────────────────
2025-11-21 - UI Polish & Bug Fixes
───────────────────────────────────────────────────────────────────────────────
✅ Tax tab scroll area displays scrollbar on initial load
✅ Categories tab correlation plots: 4 per row at 180x180px (from 5 at 150x150px)
✅ Categories tab correlation plots: 20% data range padding on all axes
✅ Theme color updates refresh Categories and Reimbursements tabs properly
✅ Fixed background colors for category selection, overview boxes, reimbursement table

───────────────────────────────────────────────────────────────────────────────
2025-11-19 - Reimbursements System
───────────────────────────────────────────────────────────────────────────────
✅ Track work travel expenses & temporary out-of-pocket costs
✅ 5-state lifecycle: Pending → Submitted → Reimbursed/Partial/Denied
✅ Tag-based filtering (trip/event organization)
✅ Excel export with smart filenames
✅ Weekly view integration (grayed/italic for bank reconciliation)
✅ Dual categorization: location tags + expense categories
✅ Interactive visualizations: stats panel, progress bars, dot plot, heatmap
⚠️ NOT included in budget calculations (separate tracking system)

───────────────────────────────────────────────────────────────────────────────
2024-11-03 - Transactions Tab Complete (Phase 2)
───────────────────────────────────────────────────────────────────────────────
✅ 4 sub-tabs: Bills, Savings, Paycheck, Spending
✅ Search, sort, multi-select, delete marking
✅ Locked row detection (auto-generated transactions)
✅ Save logic with validation
✅ Fixed AccountHistory running_total corruption bug
✅ Fixed negative sign flipping on bill edits
✅ Added automatic tab refresh on switch

───────────────────────────────────────────────────────────────────────────────
2024-10-28 - Phase 1 Complete (UI & Transfers)
───────────────────────────────────────────────────────────────────────────────
✅ Transfer Money dialog (week ↔ account, account ↔ account)
✅ + Bill and + Savings buttons in tab toolbars
✅ Reorganized menubar (File/Edit/View/Tools/Help)
✅ Import/Export Data in File menu
✅ Hour Calculator in Tools menu
✅ Category color consistency (alphabetical ordering)

───────────────────────────────────────────────────────────────────────────────
2024-10-20 - Dashboard & Year Overview
───────────────────────────────────────────────────────────────────────────────
✅ Dashboard "Total Accounted" display
✅ Dashboard stale data detection (Week card shows "-X weeks ago")
✅ Year Overview tab with 10+ visualizations
✅ AccountHistory starting balance auto-adjusts date when importing old data

================================================================================
END OF TECHNICAL REFERENCE
================================================================================

For detailed implementation gotchas, bug histories, and LLM-specific notes:
  → See ReadMeLLM.md

For project roadmap, todos, and feature tracking:
  → See PROJECT_PLAN.md

For public-facing feature overview and setup instructions:
  → See README.md
