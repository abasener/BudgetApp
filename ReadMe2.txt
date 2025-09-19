================================================================================
BudgetApp V2 - Dynamic Rollover System Documentation
================================================================================

PART 1: LOGIC OVERVIEW (Human-Readable)
================================================================================

GOAL:
Create a bi-weekly budget system where money flows dynamically between weeks and
automatically rolls over to savings. The system must handle real-time updates
when transactions are added/changed at any point in time.

CORE PROCESS:
1. Paycheck arrives ($4625 example)
2. Bills deducted first ($300)
3. Account auto-saves deducted (currently $0)
4. Remaining split 50/50 between Week 1 & Week 2 ($2162.50 each)
5. Week 1 rollover: Unspent money flows to Week 2 immediately
6. Week 2 rollover: Unspent money flows to Emergency Fund at period end
7. All rollovers recalculate dynamically when ANY transaction changes

MONEY FLOW EXAMPLE:
- Paycheck: $4625
- After bills: $4325 remaining
- Week 1 gets: $2162.50
- Week 1 spends: $225
- Week 1 rollover: $1937.50 → flows to Week 2
- Week 2 total: $2162.50 + $1937.50 = $4100
- Week 2 spends: $200
- Week 2 rollover: $3900 → flows to Emergency Fund

DYNAMIC BEHAVIOR:
- Add $50 more spending to Week 1 → Week 1 rollover becomes $1887.50
- Week 2 total automatically updates to $4050
- Week 2 rollover automatically updates to $3850
- Emergency Fund projection updates in real-time

EDGE CASES HANDLED:
1. Out-of-order transactions: Can add transactions with past/future dates
2. Multiple updates: Each transaction change triggers full period recalculation
3. Negative rollovers: Deficit weeks can pull money from next week/savings
4. Period completion: Week 2 only rolls to savings when bi-weekly period ends
5. AccountHistory integrity: Running totals maintained correctly regardless of insertion order

BI-WEEKLY PERIOD LOGIC:
- Week 1 (odd numbers): 1, 3, 5, 7... → rollover to Week 2
- Week 2 (even numbers): 2, 4, 6, 8... → rollover to savings
- Periods: (Week 1, Week 2), (Week 3, Week 4), (Week 5, Week 6)...
- Week 2 rollover to savings only happens when Week 3 is created OR period definitely ended

ACCOUNT TRACKING:
- Emergency Fund: Default savings account (receives Week 2 rollovers)
- Bills: Have their own accounts with auto-save amounts per paycheck, starting balance support
- Savings Accounts: Support starting balance entries and direct transaction editing
- AccountHistory: Date-ordered transaction history with running totals for all account types
- All money movements tracked via transactions + automatic history updates
- Real-time balance calculation from AccountHistory (not stale model attributes)

================================================================================
PART 2: TECHNICAL IMPLEMENTATION (Developer Reference)
================================================================================

KEY FILES:
- services/paycheck_processor.py: Main paycheck logic & rollover system
- services/transaction_manager.py: CRUD operations & rollover triggers
- models/account_history.py: Date-ordered balance tracking system for all account types
- views/weekly_view.py: Frontend display logic (updated for AccountHistory)
- views/bills_view.py: Bills management with AccountHistory integration
- views/savings_view.py: Savings accounts with AccountHistory integration
- views/dialogs/bill_transaction_history_dialog.py: Direct transaction editing for bills
- views/dialogs/account_transaction_history_dialog.py: Direct transaction editing for savings
- widgets/bill_row_widget.py: Bills display widgets with live AccountHistory data
- widgets/account_row_widget.py: Savings display widgets with live AccountHistory data

CRITICAL METHODS:

PaycheckProcessor:
- split_paycheck(): Calculate (paycheck - bills - auto_saves) / 2
- recalculate_period_rollovers(week_number): MAIN dynamic recalc method
- calculate_week_rollover(): Calculate surplus/deficit for one week
- _create_rollover_transaction(): Create Week1→Week2 rollover transactions
- _create_rollover_to_savings_transaction(): Create Week2→savings transactions
- _remove_period_rollover_transactions(): Clean up old rollovers before recalc

TransactionManager:
- add_transaction(): Auto-triggers rollover recalc for spending/saving transactions
- trigger_rollover_recalculation(): Calls PaycheckProcessor.recalculate_period_rollovers()
- set_auto_rollover_disabled(): Prevent infinite loops during rollover creation

AccountHistoryManager:
- add_transaction_change(): Add new history entry, handle out-of-order dates
- _get_balance_at_date(): Get balance as of specific date (not latest)
- _update_running_totals_from_entry(): Recalculate all subsequent running totals
- get_current_balance(): Latest entry's running_total
- get_account_history(): Retrieve full history for any account type (savings/bill)
- recalculate_account_history(): Rebuild running totals after starting balance changes

Account/Bill Models:
- get_current_balance(): Live balance calculation from AccountHistory
- update_starting_balance(): Create/update starting balance entries
- get_account_history(): Wrapper for AccountHistory retrieval

TRANSACTION FLOW:
1. User adds transaction → TransactionManager.add_transaction()
2. If spending/saving → trigger_rollover_recalculation(week_number)
3. PaycheckProcessor.recalculate_period_rollovers() called
4. Remove existing rollover transactions for entire bi-weekly period
5. Recalculate Week 1 → Week 2 rollover, create new transaction
6. Recalculate Week 2 → savings rollover, create new transaction
7. set_auto_rollover_disabled() prevents infinite loops

ROLLOVER IDENTIFICATION:
- Week 1→Week 2: description contains "rollover from Week X", category="Rollover"
- Week 2→savings: description contains "End-of-period surplus/deficit from Week X"
- Rollover transactions excluded from triggering further recalculations

WEEK NUMBERING & PERIODS:
- Week numbers: 1, 2, 3, 4, 5, 6...
- Bi-weekly periods: (1,2), (3,4), (5,6)...
- is_odd_week = (week_number % 2) == 1 → Week 1 of period
- week1_number = odd_week, week2_number = odd_week + 1

TIMING CONTROLS:
- Week 2 created with rollover_applied = True (prevent premature rollover)
- Week 2 rollover only when week3_exists OR week_ended
- Cascading rollover logic: Week1→Week2 doesn't immediately trigger Week2→savings

DEBUGGING LOCATIONS:
- PaycheckProcessor.recalculate_period_rollovers(): Main recalc entry point
- TransactionManager.trigger_rollover_recalculation(): Rollover trigger
- AccountHistoryManager.add_transaction_change(): Date insertion logic
- models/transactions.py: Transaction type detection (is_spending, affects_account)

TEST FILES:
- test_dynamic_rollover.py: Demonstrates real-time rollover updates
- test_final_user_scenario.py: End-to-end user scenario validation
- debug_account_history.py: AccountHistory integrity verification
- debug_paycheck_logic.py: Step-by-step paycheck processing analysis

FRONTEND INTEGRATION:
- views/weekly_view.py updated to use AccountHistory instead of balance_history arrays
- update_savings_values(): Uses _find_balance_at_date() for period calculations
- Weekly view displays real-time rollover amounts via effective_allocation calculations
- Bills/Savings tabs: Refresh buttons update all visuals with live AccountHistory data
- Widget balance displays: Use get_current_balance() for real-time data, not stale model attributes
- Transaction history dialogs: Direct table editing with automatic recalculation
- Line charts: Plot AccountHistory data (date vs running_total) for accurate historical views
- Starting balance support: Bills and Savings accounts support configurable starting balances

INFINITE LOOP PREVENTION:
- set_auto_rollover_disabled(True) before creating rollover transactions
- is_rollover_transaction detection in add_transaction()
- Rollover transactions excluded from triggering further recalculations

CONFIGURATION:
- Emergency Fund: auto_save_amount = 0, is_default_save = True
- Bills: amount_to_save per paycheck (e.g. $300 for rent), starting_balance configurable
- Savings Accounts: goal_amount, auto_save_amount, starting_balance configurable
- Weeks: running_total = base allocation, effective = base + rollover_income
- AccountHistory: Handles starting balance entries (transaction_id = None)
- Widget refresh: Real-time balance updates via get_current_balance() calls

================================================================================
RECENT V2 ENHANCEMENTS (Bills & Savings Integration):
================================================================================

BILLS TAB IMPROVEMENTS:
- Complete AccountHistory integration matching Savings tab functionality
- Starting balance support for bills (replaces dangerous running_total editing)
- Bills transaction history dialog with direct table editing capabilities
- Line charts show date vs running_total from AccountHistory (with dots on datapoints)
- Refresh button updates all visuals with live data from AccountHistory
- Bills editor dialog with starting balance configuration
- Progress bars for money saved % and time passed % since last payment
- Real-time balance calculation from AccountHistory, not stale model attributes

SAVINGS TAB CONSISTENCY:
- Both Bills and Savings tabs now use identical AccountHistory patterns
- Unified transaction history editing dialogs
- Consistent refresh button behavior for live data updates
- Starting balance entries properly handled (transaction_id = None)
- Line charts plot AccountHistory data for accurate historical visualization
- Widget displays use get_current_balance() for real-time accuracy

TRANSACTION HISTORY DIALOGS:
- Direct table editing: Date, Amount, Description columns editable
- Read-only columns: ID, Running Total (calculated from AccountHistory)
- Delete row functionality with starting balance protection
- Save all changes with confirmation dialogs
- Automatic recalculation and reordering after saves
- Real-time balance updates throughout the interface

DATA INTEGRITY FIXES:
- Eliminated stale running_total usage in widgets
- All balance displays now use live AccountHistory calculations
- Refresh buttons properly update all frontend visuals
- Starting balance entries correctly handled in all operations
- Consistent AccountHistory usage across Bills and Savings

================================================================================
KEY ARCHITECTURAL CHANGES FROM V1:
================================================================================

OLD SYSTEM:
- Manual balance tracking with arrays
- Static rollover calculation
- Rollover happened at fixed timing
- Balance inconsistencies with out-of-order transactions

NEW SYSTEM:
- AccountHistory with date-ordered running totals
- Dynamic rollover recalculation on any transaction change
- Real-time rollover updates
- Robust date-based transaction insertion

PERFORMANCE NOTES:
- Rollover recalculation is O(n) where n = transactions in bi-weekly period
- AccountHistory updates are O(m) where m = history entries after insertion point
- get_current_balance() calls are O(1) - fetches latest AccountHistory entry
- Widget refresh operations are O(k) where k = number of accounts/bills displayed
- Direct transaction editing triggers targeted AccountHistory recalculation
- All operations acceptable for typical usage patterns (few hundred transactions)
- Real-time balance updates provide immediate feedback without performance impact

================================================================================