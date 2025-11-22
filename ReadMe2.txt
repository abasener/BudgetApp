================================================================================
BudgetApp V2 - Dynamic Rollover System Documentation
================================================================================
Last Updated: 2025-11-21

RECENT FIXES & ADDITIONS (2025-11-21):
- Fixed: Tax tab scroll area now properly displays scrollbar on initial load (added showEvent handler)
- Fixed: Categories tab correlation plots layout - 4 per row (from 5) at 180x180px (from 150x150px)
- Fixed: Categories tab correlation plots padding - 20% data range padding on all axes
- Fixed: Theme color updates now properly refresh Categories and Reimbursements tabs
- Fixed: Categories tab - stats_label background color consistency (surface vs background)
- Fixed: Categories tab - frame and list widget theme updates (Selected/Overview boxes)
- Fixed: Reimbursements tab - added apply_table_theme() and apply_sidebar_theme() methods
- Fixed: Reimbursements tab - tag filter sidebar and table now update colors on theme change

RECENT FIXES & ADDITIONS (2025-11-19):
- Added: Reimbursements System - track work travel expenses & temporary out-of-pocket costs
- Added: Reimbursements tab with tag-based filtering (trip/event organization)
- Added: 5-state lifecycle tracking (Pending → Submitted → Reimbursed/Partial/Denied)
- Added: Excel export with smart filenames (e.g., Reimbursements_Whispers25_111925.xlsx)
- Added: Weekly view integration - reimbursements shown grayed/italic for bank reconciliation
- Added: Dual categorization - location/trip tags + expense categories
- Added: Batch edit/delete with visual highlighting (yellow=edited, red=deleted)
- Note: Reimbursements are NOT included in budget calculations (separate tracking system)

RECENT FIXES & ADDITIONS (2024-10-28):
- Added: Transfer Money dialog - transfer funds between accounts, bills, and weeks
- Added: + Bill and + Savings buttons to Bills and Savings tab toolbars
- Added: Reorganized menubar with File/Edit/View/Tools/Help structure
- Added: Import/Export Data directly accessible from File menu
- Added: Hour Calculator accessible from Tools menu
- Added: Help menu with About, User Guide, FAQ, and Report Bug options
- Fixed: Category color consistency - alphabetical ordering ensures same colors across all charts
- Fixed: secondary_dark theme color reference (changed to use 'accent' color for hover states)

RECENT FIXES & ADDITIONS (2024-10-20):
- Fixed: TransactionManager missing get_transaction_by_id method
- Fixed: AccountHistory starting balance auto-adjusts date when importing old data
- Added: Dashboard "Total Accounted" display (sum of bills + savings balances)
- Added: Dashboard stale data detection (Week card shows "-X weeks ago" when outdated)
- Added: Dashboard weekly pie chart auto-hides when data is stale or no spending
- Added: Year Overview tab with year-by-year financial breakdown boxes
- Note: Year boxes always show ALL data; analytics toggle only affects future charts

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
- services/transaction_manager.py: CRUD operations & rollover triggers (includes date-range queries)
- models/account_history.py: Date-ordered balance tracking system for all account types
- views/weekly_view.py: Frontend display logic (date-range transaction loading, improved charts)
- views/bills_view.py: Bills management with AccountHistory integration
- views/savings_view.py: Savings accounts with AccountHistory integration
- views/dialogs/bill_transaction_history_dialog.py: Direct transaction editing for bills
- views/dialogs/account_transaction_history_dialog.py: Direct transaction editing for savings
- widgets/bill_row_widget.py: Bills display widgets with live AccountHistory data
- widgets/account_row_widget.py: Savings display widgets with live AccountHistory data
- widgets/chart_widget.py: Chart widgets with negative value handling for overspending scenarios

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
- get_transactions_by_date_range(): Date-based transaction queries (preferred over week_number)
- get_transactions_by_week(): Legacy week_number-based queries (deprecated in weekly view)

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
- Visual feedback: Hover effects, edited cell highlighting (warning color), deleted row highlighting (red)
- Testing mode integration: Pre-save change preview and post-save verification reports
- Automatic recalculation and reordering after saves
- Real-time balance updates throughout the interface
- Theme color integration for consistent UI appearance

DATA INTEGRITY FIXES:
- Eliminated stale running_total usage in widgets
- All balance displays now use live AccountHistory calculations
- Refresh buttons properly update all frontend visuals
- Starting balance entries correctly handled in all operations
- Consistent AccountHistory usage across Bills and Savings

================================================================================
LATEST V2 ENHANCEMENTS (Dashboard Analytics & Settings):
================================================================================

DASHBOARD SPENDING ANALYTICS MODERNIZATION:
- All spending plots now use proper transaction filtering instead of manual queries
- Fixed old is_abnormal flag logic, replaced with include_in_analytics field filtering
- Consistent filtering across all charts: pie charts, histograms, box plots, trend charts, heatmaps
- "Normal Spending Only" checkbox properly controls analytics filtering throughout dashboard
- Time frame filtering applied to all spending visualizations and account balance charts

SETTINGS DIALOG COMPLETE REDESIGN:
- Reorganized into clean 2-column layout (no longer tall and skinny)
- Left Column: Sorting Settings + Graph Filtering Settings (consolidated)
- Right Column: Theme Settings + Calculator Settings
- New "Graph Filtering Settings" section combines filtering and chart options
- Dashboard chart account selection moved from separate section into Graph Filtering
- Full-width Data Management section with updated button functionality

GRAPH FILTERING SYSTEM:
- "Default to Normal Spending Only" checkbox setting (controls dashboard startup state)
- Time Frame Filter dropdown: All Time, Last Year, Last Month, Last 20 Entries
- All dashboard spending charts respect time frame filter (except current week pie chart)
- Current week pie chart always shows current week data (special behavior)
- Account/bill line charts also filtered by time frame setting
- Settings persist between app sessions in app_settings.json

DATA MANAGEMENT BUTTONS UPDATED:
- Delete All Data: Now includes AccountHistory deletion for complete fresh start
- Reset Test Data: Updated for AccountHistory system, creates proper starting balance entries
- Export Data: Enhanced with AccountHistory export, uses live balance calculations
- Import Test Data: Verified working with rebuilt backend, proper validation pipeline

DASHBOARD TIME FILTERING INTEGRATION:
- Dashboard loads time frame setting from app_settings.json on startup
- Settings changes immediately refresh dashboard with new time frame
- Chart titles reflect current time frame (e.g., "Spending by Category (Last Month)")
- Filtered transactions apply to all visualizations except current week spending
- Account balance history charts respect time filtering for focused analysis

BACKEND INTEGRATION IMPROVEMENTS:
- All settings automatically saved to persistent app_settings.json
- Main window properly handles settings_saved signals for immediate refresh
- Dashboard refresh() method reloads settings to apply changes without restart
- Time frame and analytics filtering work seamlessly with existing AccountHistory system
- All data management functions updated for new backend architecture

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
- Date-range transaction queries are O(log n) with proper database indexing

================================================================================
LATEST V2 ENHANCEMENTS (Weekly View Reliability & Chart Improvements):
================================================================================

WEEKLY VIEW TRANSACTION LOADING REDESIGN:
- Switched from week_number-based queries to date-range-based queries for transaction loading
- OLD: get_transactions_by_week(week_number) - Could miss transactions with wrong week_number
- NEW: get_transactions_by_date_range(start_date, end_date) - Always gets correct transactions
- More reliable transaction loading regardless of week_number field accuracy
- Eliminates transaction display bugs caused by week_number mismatches

TRANSACTION TABLE FILTERING IMPROVEMENTS:
- Fixed transaction filtering to show ONLY SPENDING transactions (not bill pays)
- BILL_PAY transactions are excluded from weekly spending displays
- Consistent filtering logic across all weekly view calculations (table, charts, progress bars)
- Only shows transactions within the actual week date range (10/21/2024 - 10/27/2024 format)
- Excludes rollover and allocation transactions from spending calculations
- Shows all non-rollover spending transactions regardless of include_in_analytics flag

PIE CHART ENHANCEMENTS:
- Improved category pie chart to handle positive-only spending transactions
- Added filtering for t.amount > 0 to prevent negative value errors
- Simplified logic to only show actual spending categories (not bill_pay)
- Consistent with user expectation: sum_category_n / sum_all for percentage calculation

RING CHART REDESIGN:
- Completely redesigned to show actual week money flow instead of theoretical allocations
- NEW LOGIC: Shows Bills/2 + Spending + Savings_Transactions + Rollover_In as total
- Segments: Bills allocation, Actual spending, Actual savings, Rollover income
- Only displays positive values to prevent chart rendering errors
- Dynamic segment filtering - only shows segments with positive amounts
- Handles overspending scenarios gracefully without crashes

CHART ERROR HANDLING:
- Added negative value protection for all chart widgets
- Fixed "Wedge sizes 'x' must be non negative values" errors in overspending scenarios
- Ring and pie charts now handle deficit weeks without crashing
- Fallback displays for extreme cases (no positive values)

CODE CLEANUP & RELIABILITY:
- Removed 95+ debug and test files that were cluttering the codebase
- Cleaned up all debug print statements and testing code
- Fixed syntax errors from cleanup operations
- Eliminated "sticky table" issues where transaction tables showed wrong data
- Improved error handling for chart widgets in edge cases

WEEKLY VIEW DATA ACCURACY:
- Date-range queries ensure correct transaction loading for each week
- Consistent spending calculations across table, charts, and progress bars
- Proper handling of overspending scenarios with negative savings transactions
- Real-time transaction loading without dependency on potentially incorrect week_number fields
- Eliminated transaction loading discrepancies between backend calculations and UI display

================================================================================
LATEST V2 ENHANCEMENTS (Category Color Consistency & Dynamic UI):
================================================================================

CATEGORY COLOR CONSISTENCY SYSTEM:
- Implemented centralized category-to-color mapping across entire application
- All charts (pie charts, box plots, line plots, stacked area charts) now use identical colors for same categories
- Consistent colors across all tabs: Dashboard, Categories, Bills, Savings, Weekly views
- Color consistency includes category highlighting system in Categories tab
- Alpha channel removal for Qt CSS compatibility (fixed hex color display issues)

KEY COMPONENTS:
- get_consistent_category_order(): Creates master category ordering by total spending
- get_consistent_category_colors(): Maps categories to consistent colors using global ordering
- Color mapping applied to: Dashboard (4 chart locations), Categories (3 chart locations), Weekly view pie charts
- All color keys and legends use same color mapping for perfect visual consistency

CATEGORIES TAB ENHANCEMENTS:
- Category highlighting system: Selected category emphasized in all charts (pie, box plot, color key)
- Pie chart highlighting: Exploded slice + thick border for selected category
- Box plot highlighting: Color + border emphasis for selected category
- Color key highlighting: Bold text + larger font for selected category
- Smooth integration with existing category filtering and analysis

CATEGORIES CORRELATION PLOTS (2025-11-21):
- Grid layout: 4 plots per row (changed from 5 for better visibility)
- Plot size: 180x180px each (increased from 150x150px)
- Smart padding system: (1/padding_factor) * (max - min) added to all sides
  * Default padding_factor = 5, giving 20% range padding on each axis
  * Prevents data points from sitting on plot edges
  * Formula: xlim = [min - padding, max + padding] for both x and y axes
  * Example: Data range 0-100 gets axis limits of -20 to 120
- Each plot shows correlation coefficient in title (e.g., "Gas: 0.73")
- Color-coded by category using theme chart_colors

DASHBOARD COLOR KEY REDESIGN:
- Removed borders and frames for clean text-only appearance (matches Categories tab style)
- Single HTML label with bullet points (●) instead of multiple widget approach
- Dynamic font sizing system: Automatically adjusts font size based on number of categories
- Font size calculation: available_height / (num_categories * line_height_multiplier)
- Size limits: Max 24px, Min 4px (prioritizes showing all categories over perfect readability)
- Line height multiplier: 2.0 for optimal spacing and category visibility

DYNAMIC FONT SIZING LOGIC:
- Formula: font_size = max(4, min(24, 250 / (num_categories * 2.0)))
- Example with 10 categories: 250 / (10 * 2.0) = 12.5px → 12px font
- Ensures all categories visible within 250px available height
- Automatic adjustment: Few categories = larger font, many categories = smaller font
- Complete visibility prioritized over perfect readability

THEME COMPATIBILITY FIXES:
- Fixed alpha channel issues in theme colors (8-digit hex → 6-digit hex conversion)
- Removed problematic alpha channels from Dark, Light, and Excel Blue themes
- Alpha removal automatic in category color lookup for Qt CSS compatibility
- Theme colors now properly display in category headers and UI elements

THEME UPDATE MECHANISM (2025-11-21):
All views must implement proper theme change handlers to ensure UI colors update correctly.
Required pattern:
1. Connect to theme_changed signal: theme_manager.theme_changed.connect(self.on_theme_changed)
2. Implement on_theme_changed() or apply_theme() method
3. Update ALL styled widgets (frames, labels, lists, tables, etc.)
4. Common mistake: Setting colors in init_ui() but not updating them in theme handler

Categories Tab Theme Updates:
- update_view_styling(): Updates main background, scroll areas, frames, list widgets
- Includes QFrame styling for column backgrounds (surface color + border)
- Includes QListWidget styling for category selection (background, hover, selected states)
- stats_label uses colors['surface'] (not colors['background']) for consistency

Reimbursements Tab Theme Updates:
- apply_button_theme(): Updates all action buttons
- apply_table_theme(): Updates table background, gridlines, headers, selected items
- apply_sidebar_theme(): Updates tag filter frame, list widget, title label
- on_theme_changed() calls all three methods + refreshes charts

Tax Tab Scroll Area Fix:
- Added showEvent() handler to force scroll area geometry update
- Calls updateGeometry() on scroll area and content widget
- Ensures scrollbar appears immediately when tab is first shown
- Prevents issue where scrollbar only appeared after window resize

TECHNICAL IMPLEMENTATION:
- widgets/chart_widget.py: Added custom_colors/color_map support to all chart widgets
- views/categories_view.py: Centralized color consistency methods and highlighting system
- views/dashboard.py: Updated all 4 chart locations + redesigned color key with dynamic sizing
- views/weekly_view.py: Added consistent category colors to pie charts
- themes/theme_manager.py: Fixed alpha channel issues across all themes

COLOR SYSTEM ARCHITECTURE:
- Centralized color ordering prevents inconsistencies between components
- Global category ordering based on total spending amounts (highest to lowest)
- Color assignment cycles through theme colors using modulo arithmetic
- Consistent color map creation in each view using shared methods
- Color key displays match chart colors perfectly across all tabs

DEBUGGING FEATURES:
- Debug output for color assignments (can be enabled for troubleshooting)
- Color map validation to ensure category-color matching
- Highlighting system debug output for category selection tracking
- Font size calculation debug output for dynamic sizing verification

================================================================================
LATEST V2 ENHANCEMENTS (Bill Payment Logic & Chart Improvements):
================================================================================

BILL PAYMENT TRANSACTION LOGIC FIX:
- CRITICAL FIX: Bill payments (BILL_PAY transaction type) no longer reduce weekly spending money
- OLD BEHAVIOR: Bill payments were incorrectly counted as both bill account deduction AND weekly spending
- NEW BEHAVIOR: Bill payments ONLY deduct from bill accounts, NOT from weekly allocations
- Money flow clarification: Bill Account → Outside World (e.g., paying Xfinity), NOT from weekly budget
- Rollover calculation fix: spent_amount now excludes BILL_PAY transactions
- Weekly view displays fix: Bill payments removed from transaction tables and spending totals
- Progress bar fix: Weekly spending progress no longer includes bill payments
- Requires rollover recalculation after update to fix historical data

BILL PAYMENT VS BILL SAVING:
- SAVING transaction (positive amount, bill_id): Money going INTO bill account from paycheck
- BILL_PAY transaction (amount, bill_id): Money leaving bill account to pay external bill
- Weekly SPENDING: Regular purchases from weekly allocation (groceries, gas, etc.)
- Clear separation: Bill payments are NOT weekly spending, they're bill account operations

LINE CHART X-AXIS IMPROVEMENTS:
- Dynamic tick spacing based on chart width to prevent date label overlap
- Algorithm: max_ticks = max(10, min(30, chart_width_pixels // 50))
- Adapts to different screen sizes and window widths automatically
- Creates evenly spaced time intervals across data range
- Finds closest actual data point to each target time for accurate labeling
- Always includes first and last dates for complete time context
- All data points remain plotted (only tick labels are reduced)

STARTING BALANCE HANDLING:
- Starting balance entries now automatically adjust when historical transactions added
- If transaction added before starting balance date, starting balance moves to day before earliest transaction
- Starting balance excluded from line chart plots (only "real" transactions shown as dots)
- Maintains correct running total calculations while keeping charts clean
- Dynamic adjustment prevents starting balance appearing mid-timeline

CHART WIDGET ENHANCEMENTS:
- LineChartWidget: Separate logic for Bill Balance, Running Total, and Account Balance series
- Bill Balance and Running Total charts use dynamic tick spacing
- Account Balance charts maintain 20-tick maximum for savings displays
- Date formatting: MM/DD/YYYY format with 45° rotation for readability
- Proper handling of single-point data (edge case for new accounts)

TRANSACTION TYPE CLARIFICATION:
- SPENDING: Reduces weekly allocation, no account association
- BILL_PAY: Reduces bill account balance, does NOT reduce weekly allocation
- SAVING: Increases bill/savings account balance from weekly allocation
- INCOME: Paycheck transaction, increases week allocation
- ROLLOVER: Week-to-week or week-to-savings money transfer

CODE LOCATIONS FOR BILL PAYMENT FIX:
- services/paycheck_processor.py:292-297: Rollover spent_amount calculation
- views/weekly_view.py:504-512: Week text info spending calculation
- views/weekly_view.py:666-674: Week progress bar spending calculation
- views/weekly_view.py:716-724: Transaction table filtering
- All locations now exclude TransactionType.BILL_PAY from weekly spending totals

================================================================================
TAX TRACKING FEATURES (Tax Tab):
================================================================================

OVERVIEW:
The Tax tab provides comprehensive tracking and visualization of tax savings and payments.
Designed for US tax system (Jan 1 - Dec 31 tax year, payments in following year around tax day).

YEAR-COLOR MAPPING:
- Each year assigned consistent color from theme's chart_colors array
- First year (earliest data) = chart_colors[0], second year = chart_colors[1], etc.
- Colors persist across all visualizations: year titles, line plots, bar charts
- Visual consistency helps identify year patterns across different views

TAX PAYMENT TYPES:
Categorized by keywords in transaction descriptions (case-insensitive):
- Federal: Contains "federal" in description
- State: Contains "state" in description
- Service: Contains "service" in description (e.g., TurboTax, tax preparation)
- Other: Bill_pay transactions from Taxes bill without above keywords (e.g., rebalancing)

Only Federal/State/Service counted in "Expected Tax" calculations.
Other transactions (like rebalancing) affect account balance but not tax projections.

SUMMARY METRICS (Top Bar):
- Expected Tax: Average annual tax payments (Federal + State + Service) across historical years
- Expected Percent: Average effective tax rate (tax spending / income) across years
- Current Saved: Total balance in Taxes bill account (includes all rollover)
- [Year] Saved: Amount saved in current year only (no rollover)

PROGRESS BARS:
- Year Progress: Percentage of calendar year completed (Jan 1 to Dec 31)
- Tax Savings: Current year savings vs expected spending (with rollover shown as background)

YEAR OVERVIEW BOXES (Left Column):
- One box per year with colored title (2024, 2025, etc.)
- Shows: Avg Income, Avg Saved, Saved %, Spent (if available), Remaining
- Sorted newest on top, oldest on bottom
- Title font size: 1.5x header font, bold, year-specific color

INCOME BY YEAR PLOT:
- Line chart showing paycheck amounts throughout the year
- Each year plotted as separate line with year-specific color
- X-axis: Months (Jan-Dec), all years aligned for comparison
- Y-axis: Dollar amounts
- Legend shows which color = which year

TAX PAYMENTS BY YEAR BAR CHART:
- Grouped by payment type: Federal, State, Service, Other
- Within each group: Bars ordered left to right (oldest to newest year)
- Each bar colored by year for consistency
- Dynamic spacing between groups (adjusts as years added)
- X-axis labels: Payment type names
- Y-axis: Dollar amounts

YEAR-OVER-YEAR COMPARISON TABLE:
- Columns: Year | Income | Saved | Federal | State | Service | Other | Remaining
- Shows "---" for incomplete years (no payment data yet)
- Remaining = Saved - All Deductions (for that year only, no rollover)
- Right-aligned dollar amounts for easy scanning

BREAKDOWN PIE CHART:
- Shows average distribution: Federal, State, Service, Other, Remaining
- Remaining = (Saved - Deductions) per year, averaged across years
- Only shows Remaining if positive (negative values excluded)
- Uses accent colors from theme (not chart_colors to avoid year confusion)
- Legend positioned below pie chart in 2 columns
- Legend text uses text_primary color for visibility

DATA FLOW:
- Tax savings: Positive "saving" transactions to Taxes bill during tax year
- Tax payments: "bill_pay" transactions from Taxes bill in following year
- Example: 2024 tax year → save Jan-Dec 2024 → pay taxes in 2025
- Rollovers from previous years included in current balance, excluded from pie chart

STARTING BALANCE HANDLING:
- Starting balance entries automatically adjusted if historical transactions added
- Moved to day before earliest transaction to maintain chronological integrity
- Excluded from line chart plots (only real transaction data shown)

CODE LOCATIONS:
- views/taxes_view.py: Main tax tab implementation
- Year color mapping: get_year_color() method (lines 103-115)
- Tax payment filtering: get_tax_spending_data() (lines 947-1005)
- Summary table: update_summary_table() (lines 1165-1244)
- Pie chart: generate_pie_chart() (lines 1246-1332)

SETUP REQUIREMENTS:
- Create "Taxes" bill in Bills tab
- Set starting balance if needed
- Add tax savings transactions (saving type, bill_id = Taxes bill)
- Add tax payment transactions with proper descriptions:
  * "Federal Taxes" or similar with "federal" keyword
  * "State Taxes" or similar with "state" keyword
  * "TurboTax Service" or similar with "service" keyword
- Future feature: Info popup in Settings to guide user setup

================================================================================
PART 5: LIVE ROLLOVER SYSTEM (October 2025 Update)
================================================================================

OVERVIEW:
The rollover system now works in REAL-TIME. Rollovers are created immediately
when a paycheck is added and update automatically as spending changes, without
waiting for weeks to end.

LIVE ROLLOVER BEHAVIOR:

When Paycheck Added ($5000 example):
- Bills deducted: $3582.50
- Remaining: $1417.50
- Week 1 allocation: $708.75
- Week 2 allocation: $708.75
- IMMEDIATELY CREATED:
  * Week 1 → Week 2 rollover: $708.75 (dated to Week 1 end)
  * Week 2 → Emergency Fund: $1417.50 (dated to Week 2 end - FUTURE DATE)

When Spending Added to Week 1 ($75.50):
- Week 1 remaining: $633.25
- Week 1 → Week 2 rollover UPDATES: $633.25
- Week 2 → Emergency Fund UPDATES: $1342.00
- All happens AUTOMATICALLY

When Spending Added to Week 2 ($120):
- Week 2 remaining: $588.75
- Week 2 → Emergency Fund UPDATES: $1222.00
- Automatic recalculation

When Transactions Edited/Deleted:
- Any change to Week 1 spending → recalculates both rollovers
- Any change to Week 2 spending → recalculates Emergency Fund rollover
- Works even for historical transactions (after period ends)

FUTURE-DATED TRANSACTIONS:
- Emergency Fund rollover dated to Week 2 end date
- Shows as "pending" or "in flux" in transaction history
- Reminds user that amount will change as they spend during the period
- Final amount locked when Week 3 is created (next pay period starts)

KEY FEATURES:
- No waiting for week/period to end
- Always see current projections
- Edit historical data anytime, everything recalculates
- Single transaction per rollover (updates in place, no duplicates)
- Works with add, edit, and delete operations

TECHNICAL IMPLEMENTATION:
- Paycheck processor creates rollover transactions immediately
- Transaction manager triggers recalculation on add/edit/delete
- Rollover calculation uses current spending to determine amounts
- Emergency Fund transaction uses Week 2's end date (may be in future)

CODE LOCATIONS:
- services/paycheck_processor.py:
  * _create_live_week1_to_week2_rollover() (lines 481-506)
  * _create_live_week2_to_savings_rollover() (lines 508-535)
  * recalculate_period_rollovers() (main recalc entry point)
- services/transaction_manager.py:
  * trigger_rollover_recalculation() (lines 244-253)
  * delete_transaction() - triggers recalc on delete (lines 311-332)
  * update_transaction() - triggers recalc on edit (lines 334-405)

================================================================================
PART 6: DASHBOARD & VISUALIZATION UPDATES (October 2025)
================================================================================

TIME FRAME FILTER:
- Global setting: All Time | Last Year | Last Month | Last 20 Entries
- Applies ONLY to timeline charts (charts with time on x-axis):
  * Stacked area chart (weekly category %)
  * Dashboard line charts (account balances)
  * Bills tab line charts (bill balances)
  * Savings tab line charts (account balances)
- Does NOT apply to summary charts:
  * Pie charts (need all data for accurate breakdown)
  * Heatmap (needs all data for averages)
  * Histogram (needs all data for distribution)
  * Weekly trends (shows average pattern, needs all data)
  * Box plots (needs all data for distribution)

X-AXIS TICK LIMITING:
- Dynamic tick spacing based on chart width
- Dashboard charts: Half density (100 pixels/tick) - less noise
- Bills/Savings tabs: Full density (50 pixels/tick) - more detail
- Stacked area chart: Evenly spaced weeks, always includes last week
- Line charts: Evenly spaced dates, always includes first and last
- Dashboard savings charts: No x-axis ticks (visual trends only)

CHART COLOR CONSISTENCY:
- Categories sorted by total spending amount (highest to lowest)
- Same category always gets same color across all charts
- Year colors consistent across Tax tab (chart_colors array)
- Tax payment bars use tax year color (payment year - 1)
- Stacked area chart categories match color order

DASHBOARD LINE CHARTS:
- Show account/bill balances over time
- X-axis: Dates (actual transaction dates)
- No x-axis labels (visual trends only, details on Bills/Savings tabs)
- Light grid lines for reference
- Respects time frame filter

THEME INTEGRATION:
- All charts refresh on theme change
- Tax tab: Year boxes, summary table, and pie chart update
- Color mappings use theme's chart_colors and accent colors
- Text colors use text_primary and text_secondary

BUG FIXES:
- Fixed: Bill payments were using "spending" instead of "bill_pay" type
- Fixed: Tax bar chart colors now use tax year (payment year - 1)
- Fixed: Stacked area chart color mapping (alphabetical vs amount order)
- Fixed: Time frame filter scope (only timeline charts, not summary)

CODE LOCATIONS:
- views/dashboard.py:
  * get_timeline_filtered_spending_transactions() (lines 775-785)
  * get_filtered_spending_transactions() (lines 755-773)
  * update_stacked_area_chart() (lines 1148-1197)
  * Dynamic tick spacing (lines 239-275)
- views/taxes_view.py:
  * refresh_plots() with table and pie chart (lines 1500-1534)
  * Tax year color mapping (lines 1127-1132)
- widgets/chart_widget.py:
  * LineChartWidget date formatting (lines 344-435)
- widgets/bill_row_widget.py & account_row_widget.py:
  * Time frame filter integration (lines 487-507)

================================================================================
PART 7: WEEK ROLLOVER & ACCOUNT HISTORY FIXES (October 2025)
================================================================================

CRITICAL BUG FIXES - WEEK DISPLAY & SAVINGS STARTING BALANCE:

ISSUE 1: Week Display Using Date Range Instead of Week Number
PROBLEM:
- weekly_view.py was using get_transactions_by_date_range() to load transactions
- Rollover transactions are dated to Week 1's END date but assigned to Week 2
- Result: Week 1 displayed the rollover LEAVING it, making it look like rollover coming IN
- Week 1 showed higher starting amount than Week 2 (backwards!)

SOLUTION:
- Changed weekly_view.py line 482 to use get_transactions_by_week(week_number)
- Now transactions are filtered by week_number field, not date range
- Rollover transactions properly attributed to receiving week
- Week 1 Starting: $454.46 (base only)
- Week 2 Starting: $454.46 + $312.76 rollover = $767.22 ✓

CODE LOCATION:
- views/weekly_view.py:482-484
- OLD: get_transactions_by_date_range(start_date, end_date)
- NEW: get_transactions_by_week(week_number)

ISSUE 2: Savings Account Starting Balance Not Included in Running Totals
PROBLEM:
- Starting balance entry existed but was dated AFTER all transactions (2025-10-12)
- First transaction showed running_total = $92.72 instead of $4296.73
- Starting balance was ignored in all calculations

ROOT CAUSE:
- Starting balance was added AFTER historical data was imported
- AccountHistory entries are sorted by date - starting balance came LAST chronologically
- _get_balance_at_date() returned 0 for transactions before starting balance date

SOLUTION:
- Updated starting balance entry date to 2024-09-21 (before first transaction)
- Recalculated ALL running totals in chronological order
- Starting balance now FIRST entry in AccountHistory
- All subsequent running totals now include starting balance

VERIFICATION:
- Before: First transaction running_total = $92.72
- After: First transaction running_total = $4296.73 ($4204.01 + $92.72) ✓

CODE LOCATIONS:
- models/account_history.py:115-137: add_transaction_change()
- models/account_history.py:177-201: _update_running_totals_from_entry()
- Fix script: fix_starting_balance_date.py

WEEK ROLLOVER SYSTEM - COMPLETE SPECIFICATION:

MONEY FLOW (Simple Version):
1. Week 1 → Week 2 (one rollover transaction)
2. Week 2 → Savings (one rollover transaction)
3. NO OTHER ROLLOVERS

WEEK CALCULATIONS:
- Week.running_total = BASE ALLOCATION ONLY (half of spendable income)
- Week Display Starting = running_total + rollover_in - rollover_out
- Week Display Current = Starting - Spending
- Week Display Daily = Current / max(days_left, 1)
- Spending does NOT affect Starting, only Current

EXAMPLE WITH NUMBERS:
Pay Period 4 (Weeks 57-58):
- Paycheck: $4237.50
- Bills/Taxes: $3328.59
- Spendable: $908.91
- Week 57 base: $454.46 (half of spendable)
- Week 58 base: $454.46 (half of spendable)

Week 57 (Week 1):
- Base allocation (running_total): $454.46
- Rollover IN: $0.00 (Week 1 doesn't receive rollovers)
- Starting: $454.46
- Spending: $141.70
- Current: $312.76
- Rollover OUT to Week 58: $312.76

Week 58 (Week 2):
- Base allocation (running_total): $454.46
- Rollover IN: $312.76 (from Week 57)
- Starting: $767.22 ($454.46 + $312.76)
- Spending: $0.00
- Current: $767.22
- Rollover OUT to Savings: $767.22

CRITICAL: Week.running_total NEVER includes rollovers!
- It's ONLY the base allocation from paycheck split
- Rollovers are separate transactions with their own entries
- Display logic ADDS rollover transactions to base for "Starting" amount

ROLLOVER TRANSACTIONS:
- Week 1 → Week 2: transaction_type="rollover", week_number=58, description="Rollover from Week 57"
- Week 2 → Savings: transaction_type="saving", week_number=58, account_id=1, description="End-of-period surplus from Week 58"
- Dated to source week's END date
- Updated in place when spending changes (no duplicates)

ACCOUNT HISTORY - COMPLETE SPECIFICATION:

PURPOSE:
AccountHistory tracks ALL balance changes for ALL account types (savings and bills).
Every transaction that affects an account creates an AccountHistory entry.
Running totals are maintained in chronological order by transaction_date.

SCHEMA:
- id: Primary key
- transaction_id: FK to transactions table (NULL for starting balance)
- account_id: ID of affected account (bill or savings)
- account_type: "bill" or "savings"
- change_amount: Dollar change (positive or negative)
- running_total: Cumulative balance AFTER this change
- transaction_date: Date of the change (from transaction or manual)
- description: For non-transaction entries (e.g., "Starting balance")

STARTING BALANCE ENTRIES:
- transaction_id = NULL (no associated transaction)
- change_amount = starting balance amount
- running_total = starting balance amount (first entry)
- transaction_date = MUST BE BEFORE ALL TRANSACTIONS
- description = "Starting balance for [type] account"

CRITICAL: Starting balance date MUST be chronologically first!
- If transactions exist before starting balance date, calculations will be wrong
- Starting balance should be dated one day before earliest transaction
- When adding historical transactions, check if they predate starting balance

AUTO-UPDATE BEHAVIOR:
When transaction added/edited/deleted at ANY point in history:
1. Find the insertion point in chronological order (by transaction_date)
2. Calculate running_total = previous_entry.running_total + change_amount
3. Update ALL subsequent entries' running_totals
4. This ensures historical edits propagate forward automatically

EXAMPLE:
Entries before adding $100 transaction on 2024-10-01:
- ID 1: Start balance $4204.01 on 2024-09-21, running=$4204.01
- ID 151: +$92.72 on 2024-09-22, running=$4296.73
- ID 152: -$64.66 on 2024-10-06, running=$4232.07

After adding $100 transaction on 2024-10-01:
- ID 1: Start balance $4204.01 on 2024-09-21, running=$4204.01
- ID 151: +$92.72 on 2024-09-22, running=$4296.73
- ID 213: +$100.00 on 2024-10-01, running=$4396.73 (NEW)
- ID 152: -$64.66 on 2024-10-06, running=$4332.07 (UPDATED +$100)
- All following entries also increased by $100 automatically

CODE METHODS:
- add_transaction_change(): Adds new entry, triggers auto-update
- update_transaction_change(): Updates existing entry, triggers auto-update
- delete_transaction_change(): Removes entry, triggers auto-update
- _update_running_totals_from_entry(): Recalculates all subsequent running_totals
- recalculate_account_history(): Full recalculation (for fixing data issues)

TESTING ACCOUNT HISTORY:
To verify auto-update works:
1. Add transaction in the PAST (before existing transactions)
2. Check that ALL subsequent running_totals increased by the amount
3. Edit that transaction to different amount
4. Check that ALL subsequent running_totals updated again
5. Delete that transaction
6. Check that ALL subsequent running_totals decreased by the amount

PREVENTING FUTURE BREAKS:

1. NEVER use get_transactions_by_date_range() for weekly view
   - USE: get_transactions_by_week(week_number)
   - Date ranges can pick up wrong rollover transactions

2. NEVER modify Week.running_total to include rollovers
   - Week.running_total = BASE ALLOCATION ONLY
   - Display calculations ADD rollover transactions separately

3. ALWAYS date starting balance BEFORE first transaction
   - Check earliest transaction date first
   - Set starting balance to day before earliest
   - Use recalculate_account_history() if order wrong

4. UNDERSTAND that running_totals update automatically
   - Don't manually set running_total values
   - Trust _update_running_totals_from_entry() to propagate changes
   - Historical edits work automatically

5. REMEMBER the rollover flow is simple
   - Week 1 → Week 2 (one transaction)
   - Week 2 → Savings (one transaction)
   - No other rollovers exist

CODE LOCATIONS FOR FUTURE REFERENCE:
- views/weekly_view.py:482: Transaction loading (use week_number!)
- views/weekly_view.py:514-531: Week starting amount calculation
- models/account_history.py:115-137: Transaction addition with auto-update
- models/account_history.py:177-201: Running total propagation logic
- services/paycheck_processor.py:481-556: Live rollover creation
- services/transaction_manager.py:213-219: AccountHistory integration
- services/transaction_manager.py:259: get_transaction_by_id (for test verification)
- views/dashboard.py:1076-1097: Total Accounted calculation
- views/dashboard.py:1113-1221: Stale data detection logic
- views/year_overview_view.py:120-240: Year financial data calculation

================================================================================
YEAR OVERVIEW TAB SPECIFICATION
================================================================================

PURPOSE:
Year-over-year financial analysis showing income, spending, bills, and savings
patterns across multiple years. Helps identify trends like holiday spending spikes,
bill increases over time, and savings rate improvements.

LEFT PANEL - YEAR BOXES:
Each year gets a colored box (newest first) with 4 rows:
1. Income:  Total paychecks        (no %, YoY change)
2. Spent:   Weekly spending        (% of income, YoY change)
3. Bills:   Bills actually paid    (% of income, YoY change)
4. Saving:  Net savings increase   (% of income, YoY change)

CRITICAL: Understanding the Financial Categories
=================================================
The rollover system means Income = Spent + Bills + Saving (always balanced)

INCOME: All paycheck transactions (type: "income")
- Simple sum of all paychecks in the year

SPENT: All weekly budget spending (type: "spending")
- Includes normal AND abnormal spending (include_in_analytics flag ignored)
- Does NOT include withdrawals from savings (those become spending transactions)

BILLS: Money actually PAID from bill accounts (type: "bill_pay")
- NOT deposits to bill accounts (those are savings)
- Only actual bills paid (negative transactions from bill accounts)

SAVING: Net increase in all savings/bill account balances
- Formula: (Deposits to savings/bills) - (Bills paid) - (Withdrawals from savings)
- Includes:
  * Weekly budget rollover to savings
  * Explicit deposits to savings/bill accounts
  * Money saved in bills (deposited but not yet spent)
- Excludes:
  * Bills actually paid (already counted in BILLS)
  * Emergency withdrawals from savings

WHY IT WORKS:
Because of automatic rollover, all income is either:
  a) Spent from weekly budget (Spent)
  b) Paid as bills (Bills)
  c) Everything else stays in savings/bills (Saving)

DISPLAY FORMAT:
Example year box (2024 in colored header):
Income:  $  45,000          ↑3.2%
Spent:   $  22,500   50.0%  ─
Bills:   $  11,250   25.0%  ↓4.1%
Saving:  $  11,250   25.0%  ↑6.5%

- Monospace font for perfect alignment
- % of income can exceed 100% if overspending (negative saving)
- First year shows ─ for YoY change (no previous year)
- ↑ = increase, ↓ = decrease from previous year

RIGHT PANEL - VISUALIZATIONS:
- Refresh button (🔄) - refreshes entire tab
- Analytics toggle - filters abnormal spending from CHARTS ONLY (not year boxes)
- Future: Income trends, spending patterns, bill cost increases, seasonal analysis

YEAR BOXES ALWAYS SHOW ALL DATA:
The analytics toggle only affects right panel charts. Left panel year boxes
always show complete financial picture including abnormal spending.

DATA COLLECTION:
Transaction types used:
- "income": Paychecks → INCOME
- "spending": Weekly budget → SPENT
- "bill_pay": Bills paid from bill accounts → BILLS
- "saving": Deposits to savings/bill accounts → SAVING (deposits part)
- "spending_from_savings": Withdrawals from savings → SAVING (withdrawal part)

Year boundaries: Jan 1 - Dec 31 (calendar year, not pay period aligned)

CODE STRUCTURE:
- get_year_data(): Queries transactions, calculates 4 categories per year
- create_year_box(): Builds UI with monospace alignment, YoY comparisons
- get_year_color(): Assigns consistent colors across years (from chart_colors)
- refresh(): Finds all years with data, creates boxes newest-first

================================================================================
YEAR OVERVIEW TAB - RIGHT PANEL VISUALIZATIONS (October 2025)
================================================================================

LAYOUT OVERVIEW (Top to Bottom):
1. Average Monthly Financial Activity - Full-width line plot
2. Pie Chart | Violin Plot - Side-by-side row (1/3 | 2/3 width)
3. Correlation Plots - Three scatter plots in row
4. Income by Year - Full-width line plot
5. Spending by Year - Full-width line plot with smooth curves
6. Bills by Year - Full-width line plot with smooth curves
7. Savings by Year - Full-width line plot with 3-day buckets

PLOT 1: AVERAGE MONTHLY FINANCIAL ACTIVITY
Purpose: Shows average spending/income patterns across all months
- 4 lines (12 datapoints each from Jan-Dec)
- Income: Fully opaque (stands out)
- Spending/Bills/Savings: 40% opacity (subtle background)
- Monthly averages calculated PER MONTH (not per year)
  * If December exists in 1 year only → average over 1 month
  * If August exists in 2 years → average over 2 months
- Uses analytics toggle for spending filter

PLOT 2: PIE CHART (Left 1/3)
Purpose: Shows distribution of income allocation
- Segments: Spending, Bills, Savings
- CRITICAL: Percentages calculated correctly based on analytics toggle
  * Normal Only ON: % of (income - abnormal_spending)
  * Normal Only OFF: % of total_income
- Title updates: "Average Distribution of Income (Normal Only)"
- Ensures Spending + Bills + Savings = 100%

PLOT 3: VIOLIN PLOT (Right 2/3)
Purpose: Shows distribution of transaction amounts
- 4 violins: Income, Spending, Bills, Savings
- Width = frequency of transactions at that dollar amount
- Shows median (white line) and mean (thick bar)
- Helps identify: consistent income vs variable spending
- Uses analytics toggle for spending filter

PLOT 4-6: CORRELATION PLOTS (Income vs Spending/Bills/Savings)
Purpose: Shows how categories correlate with income changes
- 3 square scatter plots (20% axis padding)
- Y-axis: Income per paycheck (shared across all 3)
- X-axis: Spending/Bills/Savings per paycheck
- Each year = 1 colored datapoint (year-specific color)
- Linear regression line with beta value in title
- Beta interpretation: "For every $1 increase in income, spending increases by β"
- Only leftmost plot shows y-axis labels (cleaner layout)
- Square aspect ratio maintained (set_aspect('equal'))

PLOT 7: INCOME BY YEAR
Purpose: Compare paycheck amounts across years
- One line per year (year-specific color)
- Datapoint on each paycheck date
- X-axis: Months (Jan-Dec), all years aligned
- No filtering needed (income is income)

PLOT 8: SPENDING BY YEAR
Purpose: Track spending trends with noise reduction
- Daily datapoints (tiny dots, 30% alpha)
- 14-day moving average trendline (smooth spline curve)
- Handles Feb 29 in leap years gracefully
- Uses analytics toggle for filtering
- X-axis aligned by month for year-over-year comparison

PLOT 9: BILLS BY YEAR
Purpose: Track bill payment patterns
- Datapoints when bills are actually paid
- Smooth spline curve (no straight lines)
- Larger markers (s=30) with black edge
- No daily interpolation (bills aren't daily)

PLOT 10: SAVINGS BY YEAR
Purpose: Track savings contributions over time
- 3-DAY BUCKETS: Aggregates transactions into 3-day periods
  * Reduces noise from frequent small transactions
  * Formula: bucket_num = days_into_year // 3
- Smooth spline curve through bucket centers
- Shows only money going INTO savings accounts

MONTHLY AVERAGE CALCULATION LOGIC:
Old (WRONG): Divided all months by total number of years
New (CORRECT): Tracks which months have data per year

Example with 2 years of data:
- December 2024: has data
- December 2025: NO data yet
- Result: December average = sum(Dec2024) / 1 (not /2)

Algorithm:
```python
monthly_counts = [0] * 12  # Track years with data per month
for year in years:
    months_with_data = set()
    for transaction in year_transactions:
        months_with_data.add(transaction.month - 1)
    for month_idx in months_with_data:
        monthly_counts[month_idx] += 1

# Later: divide by actual count
monthly_avg[i] = monthly_sum[i] / monthly_counts[i]
```

PIE CHART PERCENTAGE CALCULATION:
Normal spending mode affects how percentages are calculated to ensure they add up to 100%

When "Normal Spending Only" is CHECKED:
- effective_income = (total_income - abnormal_spending) / num_years
- spending = normal_spending_only / num_years
- percentages = [spending, bills, savings] / effective_income * 100
- Result: Pie adds up to 100% of "normal" income

When "Normal Spending Only" is UNCHECKED:
- effective_income = total_income / num_years
- spending = (normal + abnormal_spending) / num_years
- percentages = [spending, bills, savings] / total_income * 100
- Result: Pie adds up to 100% of total income

ANALYTICS TOGGLE INTEGRATION:
Plots that filter by toggle:
✓ Monthly Line Plot - Spending line only
✓ Pie Chart - Percentages adjust for abnormal spending
✓ Violin Plot - Spending violin only
✓ Spending by Year - All datapoints and trendline

Plots that don't filter (correct behavior):
✓ Correlation Plots - Uses year averages (already filtered)
✓ Income by Year - Income is income
✓ Bills by Year - Bills don't filter
✓ Savings by Year - Savings don't filter

SMOOTH CURVE IMPLEMENTATION:
Uses scipy.interpolate.make_interp_spline with cubic splines (k=3)
- Creates 3x-5x more interpolation points than original data
- Follows natural flow of data without sharp corners
- Applied to: Spending, Bills, Savings plots

3-DAY BUCKET ALGORITHM:
```python
days_into_year = (transaction.date - jan_1).days
bucket_num = days_into_year // 3
bucket_start = jan_1 + timedelta(days=bucket_num * 3)
bucketed_data[bucket_start] += transaction.amount
```
Result: ~122 buckets per year instead of 365 daily points

THEME INTEGRATION:
- All plots use theme colors (background, text, accent)
- Year-specific colors from chart_colors array
- Pie chart uses accent_colors (not chart_colors to avoid year confusion)
- Correlation plots use square aspect ratio with proper padding
- All plots refresh on theme change

CODE LOCATIONS:
- views/year_overview_view.py: Main implementation (1500+ lines)
- update_yoy_growth_bars(): Monthly line plot with per-month averaging
- update_master_pie_chart(): Pie chart with analytics-aware percentages
- update_violin_plots(): Violin plot with analytics filter
- update_correlation_plots(): Scatter plots with regression and padding
- update_income_plot(): Income by year plot
- update_spending_plot(): Spending with smooth curves and analytics filter
- update_bills_plot(): Bills with smooth curves
- update_savings_plot(): Savings with 3-day buckets and smooth curves
- toggle_analytics_mode(): Refreshes affected plots when toggle changes

FUTURE ENHANCEMENTS (Potential):
- Seasonal analysis (which months cost more/less)
- Category breakdown by year (not just totals)
- Spending velocity trends (acceleration/deceleration)
- Bill increase predictions based on historical rates
- Interactive tooltips showing exact values on hover

================================================================================
MENUBAR & UI ORGANIZATION (October 2024)
================================================================================

MENUBAR RESTRUCTURE:
The application menubar has been reorganized to follow standard desktop application conventions
with clear separation of concerns across five main menus.

FILE MENU - Document/Data Operations:
- Import Data (Excel): Import transactions from Excel file (Replace/Merge/Append modes)
- Export Data (Excel): Export all data to Excel file for backup or analysis
- ────────
- Reset All Data...: Permanently delete all data with math-based confirmation
- ────────
- Exit: Close application

Note: Future planned addition of SQL bulk import/export for database operations

EDIT MENU - Data Modification:
- Add Transaction: Add spending transaction to weekly budget
- Add Paycheck: Process bi-weekly paycheck with automatic distribution
- Pay Bill: Pay a bill from bill account balance
- Transfer Money: Transfer funds between accounts, bills, and weeks
- ────────
- Add Savings Account: Create new savings account with goal tracking
- Add Bill Account: Create new bill with payment frequency and auto-save amount

Philosophy: All operations that modify budget data are grouped in Edit menu for intuitive access

VIEW MENU - Navigation & Display:
- Refresh All: Refresh all views and recalculate balances
- ────────
- Dashboard: Navigate to Dashboard tab
- Bills: Navigate to Bills tab
- Savings: Navigate to Savings tab
- Weekly: Navigate to Weekly tab
- Categories: Navigate to Categories tab
- Yearly: Navigate to Yearly tab

Future: Keyboard shortcuts (Ctrl+1-6) for quick tab navigation

TOOLS MENU - Utilities:
- Hour Calculator...: Calculate hours needed for expenses and savings goals

Future additions: Additional financial calculators, goal planning tools

HELP MENU - Documentation & Support:
- About Budget App: Version info and feature overview
- User Guide: Opens readme2.txt with complete documentation
- ────────
- Questions / FAQ: Placeholder for future FAQ resource document
- Report Bug: Opens GitHub for issue reporting

TRANSFER MONEY DIALOG:
Comprehensive transfer system for moving funds between any account types.

FEATURES:
- FROM/TO dropdowns with current balances displayed
- Week number spinbox appears when "Current Week" selected
- Auto-updating transaction notes (lock when manually edited)
- Real-time balance validation (prevents overdrafts)
- Single transaction for week transfers, double for account-to-account

TRANSACTION PATTERNS:
- Week → Account/Bill: Creates positive SAVING transaction (money into account)
- Account/Bill → Week: Creates negative SAVING transaction (money out of account)
- Account → Account: Creates two SAVING transactions (one negative, one positive)
- Notes always reference the OTHER side for clarity in transaction history

VALIDATION:
- Prevents transfers from same account to itself
- Checks for sufficient balance before allowing transfer
- Amount must be greater than zero
- Refresh happens before success message for immediate feedback

CODE LOCATIONS:
- views/dialogs/transfer_dialog.py: Main dialog implementation
- _create_week_transfer(): Single-transaction week transfer logic (lines 406-439)
- _create_account_to_account_transfer(): Double-transaction account logic (lines 441-484)

TAB-LOCAL TOOLBARS:
Bills and Savings tabs now have mini-toolbars for quick access to common actions.

BILLS TAB TOOLBAR:
- + Bill (secondary styling - light blue): Opens Add Bill dialog
- 🔄 Refresh (primary styling - green): Refreshes bill data
- Sort by: [Dropdown] - Alphabetical, Richest, Closest, Payment Size

SAVINGS TAB TOOLBAR:
- + Savings (secondary styling - light blue): Opens Add Account dialog
- 🔄 Refresh (primary styling - green): Refreshes savings data
- Sort by: [Dropdown] - Alphabetical, Highest Balance, Goal Progress, Goal Amount

BUTTON STYLING HIERARCHY:
- Primary (green): Main action buttons for critical operations
- Secondary (light blue): Supporting action buttons for data entry
- Normal (gray): Regular buttons for standard operations
- Small (compact): Icon-only buttons like Settings (⚙️) and Refresh (🔄)

MAIN TOOLBAR (Below menubar):
- Add Transaction (primary - green)
- Add Paycheck (secondary - light blue)
- Pay Bill (normal)
- Transfer Money (normal)
- | Theme Selector Dropdown |
- Settings ⚙️ (small)
- Refresh 🔄 (small)

CATEGORY COLOR CONSISTENCY:
Categories are now sorted alphabetically (A-Z) for consistent color assignment across all charts.

SYSTEM:
- get_consistent_category_order(): Returns alphabetical category list
- Same category always receives same color from theme's chart_colors array
- Applies to: Dashboard, Categories tab, Weekly tab, all pie charts
- Future: custom_order parameter for user-defined category ordering in settings

BENEFITS:
- Users learn category colors quickly (not changing based on spending amounts)
- Visual consistency across all tabs and time periods
- Color key matches chart colors perfectly
- Easier to identify categories at a glance

CODE LOCATIONS:
- views/dashboard.py:351-405: get_consistent_category_order()
- views/categories_view.py:1001-1055: Same alphabetical implementation
- views/weekly_view.py:35-89: Same alphabetical implementation
- All three use custom_order parameter for future user customization

THEME COLOR FIX:
Fixed secondary_dark color reference that didn't exist in theme definitions.
- Changed hover states from colors['secondary_dark'] to colors['accent']
- Applies to: Bills tab + Bill button, Savings tab + Savings button
- All theme colors properly support button styling hierarchy

================================================================================
================================================================================
PART 12: REIMBURSEMENTS SYSTEM (November 2025)
================================================================================

PURPOSE:
Track work travel expenses, friend loans, and temporary out-of-pocket costs 
separately from main budget calculations. Money is expected to be reimbursed,
so it should NOT affect weekly spending totals or budget projections.

USE CASES:
1. Work Travel: Conference registrations, hotels, meals, transport awaiting 
   company reimbursement
2. Friend Loans: Money lent to friends expecting repayment
3. Temporary Expenses: Any out-of-pocket cost that will be reimbursed

KEY PRINCIPLE:
Reimbursements are SEPARATE from the budget system. They:
- Do NOT reduce weekly spending money
- Do NOT appear in spending calculations
- Do NOT affect account balances
- ONLY appear in weekly view for bank statement reconciliation (grayed out)

REIMBURSEMENT LIFECYCLE:
1. Pending Submission: Purchased but not yet submitted for reimbursement
2. Awaiting Payment: Submitted to company/friend, waiting for payment
3. Reimbursed: Money received back (complete)
4. Partially Reimbursed: Some money received, more expected
5. Denied: Not getting reimbursed (rare - add as backdated spending transaction)

AUTO-DATE TRACKING:
- submitted_date: Auto-set when state changes to "Awaiting Payment"
- reimbursed_date: Auto-set when state changes to "Reimbursed" or "Partially Reimbursed"
- Dates can be NULL if user skips states (e.g., goes straight from Pending to Reimbursed)

DUAL CATEGORIZATION SYSTEM:
1. Tag/Location: Trip or event identifier (e.g., "Whispers25", "NYC24", "Conference2025")
   - Used for filtering and grouping expenses by trip
   - Optional - can be NULL for misc expenses
   - Appears in "Other" filter category when empty

2. Category: Type of expense (e.g., "Transport", "Food", "Hotel", "Materials")
   - Required field
   - Similar to spending categories but specific to reimbursements
   - Common categories: Transport, Food, Hotel, Conference Fees, Energy Drinks, Materials

REIMBURSEMENTS TAB LAYOUT:
┌──────────────────────────────────────────────────────────────────────────────┐
│ Filter  │ Add    │ [$457.85]│ [Progress]│ [Dot Plot*]│ [Tag×Cat]            │
│ by Tag: │ Save   │ [Total  ]│ [Bars    ]│ [Amount vs]│ [Heatmap]            │
│ ┌─────┐ │ Delete │ [Pie:   ]│ [Submit% ]│ [Age by   ]│ [All tags]           │
│ │All  │ │ Export │ [Status%]│ [Reimb % ]│ [Category ]│ [rows×cols]          │
│ │Other│ └────────┘ └──────────┴───────────┴───────────┴──────────            │
│ │Whsp │                      *Appears when window wide enough                │
│ │NYC  │                                                                       │
│ └─────┘                                                                       │
├──────────────────────────────────────────────────────────────────────────────┤
│ Date       │ Status            │ Amount   │ Tag        │ Category  │ Notes  │
│ 11/18/2025 │ Reimbursed        │ $85.00   │ Whispers25 │ Transport │ ...    │
│ 11/16/2025 │ Awaiting Payment  │ $125.50  │ Whispers25 │ Conf. Fees│ ...    │
│ 11/15/2025 │ Pending           │ $45.00   │ NYC24      │ Food      │ ...    │
└──────────────────────────────────────────────────────────────────────────────┘

VISUALIZATION WIDGETS (Top Row, 170px height):
1. Stats Panel (200px wide, filtered data):
   - Large text: Total $ spent for current tag filter
   - Pie chart: Status breakdown by % (Pending/Submitted/Reimbursed/Partial/Denied)
   - Semantic colors: warning(pending), info(submitted), success(reimbursed),
     accent2(partial), error(denied)

2. Progress Bars (180px wide, filtered data):
   - Two vertical bars (weighted by $ amount, NOT transaction count)
   - Left bar (secondary color): Submitted % = (submitted+reimbursed+partial+denied) / total
   - Right bar (accent color): Reimbursed % = (reimbursed+partial) / total
   - Background bars (surface_variant) show unfilled portion
   - Example: $400 total, $320 submitted → 80% left bar filled

3. Dot Plot (170×170px square, *adaptive visibility*, filtered data):
   - ONLY shown when container width >= 840px (dynamically appears/disappears)
   - X-axis: Age of expense (date) - older left (0), newer right (1), normalized
   - Y-axis: Amount - lowest bottom (0), highest top (1), normalized
   - Dots colored by category using theme chart_colors (cycles if more categories)
   - Square cells (aspect='equal'), axis labels "Date" and "Amount", no tick labels
   - Placement: Between stats and progress bars when shown

4. Tag × Category Heatmap (250px wide, ALL data - ignores filter):
   - Rows: All tags with data (e.g., "Whispers25", "NYC24", "Amber")
   - Columns: All categories with data (e.g., "Food", "Hotel", "Transport")
   - Cell color: Surface (lowest $) → Primary (highest $) gradient
   - Square cells (aspect='equal')
   - Shows complete spending overview across all tags

Dynamic Layout Behavior:
- Widgets pull actual width dynamically (adapts to different screen sizes/DPI)
- Dot plot appears/disappears based on available space with 30px tolerance
- State tracking prevents layout flashing (only rebuilds when dot plot state changes)
- All visualizations update when tag filter changes (except heatmap shows all)

BUTTON FUNCTIONALITY:
- Add: Opens Add Transaction dialog with "Reimbursements" pre-selected
- Save: Commits all edited cells and deletions to database (batch operation)
- Delete: Marks selected rows red (actual deletion happens on Save)
- Export: Exports selected (or all) reimbursements to Excel

EDIT TRACKING:
- Double-click cell to edit
- Edited cells highlighted with subtle yellow background
- Deleted rows marked with red text
- Changes NOT saved until "Save" button clicked
- Confirmation dialog shows all changes before applying

WEEKLY VIEW INTEGRATION:
Reimbursements appear at BOTTOM of weekly transaction tables:
- Grayed out text (theme secondary color)
- Italic font style
- Non-editable (read-only)
- Shows status instead of category
- Disabled "Abnormal" checkbox
- NOT included in week spending totals

PURPOSE: Bank statement reconciliation
- User sees all charges from bank statement (including reimbursables)
- Prevents confusion: "Where did this $300 charge go?"
- Clearly distinguished from real spending (gray + italic)

EXPORT FUNCTIONALITY:
Filename Format: Reimbursements_[Tag]_[MMDDYY].xlsx
- With tag: Reimbursements_Whispers25_111925.xlsx
- Without tag (All/Other): Reimbursements_111925.xlsx
- Date format: MMDDYY (e.g., 111925 for Nov 19, 2025)

Excel Structure:
Row 1 (Headers): Amount | Tag | Category | Notes | Status
Row 2+: Data values

Features:
- Auto-sized columns (capped at 50 chars wide)
- Bold headers
- Status column last (easy to delete if needed for expense reports)
- Exports selected rows OR all rows if none selected
- Default save location: Same directory as database

COMMON WORKFLOW EXAMPLE:
1. User at conference, buys $125 registration with personal card
2. Opens Add Transaction → Reimbursements
3. Enters: $125, "Conference registration fee", Category="Conference Fees", Tag="Whispers25"
4. State defaults to "Pending Submission"
5. Later: Edit status to "Awaiting Payment" → submitted_date auto-set to today
6. Week view shows $125 charge (grayed out) matching bank statement
7. Money received: Edit status to "Reimbursed" → reimbursed_date auto-set
8. After conference: Filter by "Whispers25" tag
9. Select all, click Export
10. Send Reimbursements_Whispers25_111925.xlsx to boss

DATABASE SCHEMA:
models/reimbursements.py - Reimbursement model
- id, amount, date, state, notes, category, location
- submitted_date, reimbursed_date (auto-populated)
- created_at, updated_at timestamps

services/reimbursement_manager.py - ReimbursementManager class
- add_reimbursement(), get_all_reimbursements()
- update_reimbursement() - handles state changes and auto-dates
- delete_reimbursement(), get_unique_locations(), get_unique_categories()
- Filter methods: get_by_state(), get_by_location(), get_by_date_range()

views/reimbursements_view.py - ReimbursementsView class
- Tag filtering sidebar
- Sortable/editable table with change tracking
- Add/Save/Delete/Export button handlers
- Excel export with openpyxl

EDGE CASE HANDLING:
- Partial reimbursement: User adjusts amount manually and adds uncovered portion 
  as backdated spending transaction
- Denied reimbursement: User adds as backdated spending transaction with original date
- Mixed trips: User can split personal vs reimbursable expenses into separate entries
- No tag: Reimbursements without tags appear in "Other" filter category
- Skipped states: submitted_date/reimbursed_date can be NULL if user jumps states

VALIDATION RULES:
- Amount: Required, must be numeric, always stored as positive
- Date: Required, MM/DD/YYYY format
- Category: Required, cannot be empty
- Tag/Location: Optional, NULL if empty
- Notes: Optional, unlimited text
- Status: Must be one of 5 valid states

CODE LOCATIONS:
- models/reimbursements.py: Database model with ReimbursementState enum
- services/reimbursement_manager.py: CRUD operations and filtering
- views/reimbursements_view.py: Main tab UI with all functionality
- views/dialogs/add_transaction_dialog.py: "Reimbursements" mode added (lines 42-45, 272-290, 399-425)
- views/weekly_view.py: Reimbursement display integration (lines 811-912)
- main.py: Tab registration (lines 111-114, 476-477)

TESTING NOTES:
- Test reimbursement appears in correct week's transaction table
- Test editing cells highlights yellow
- Test delete marking shows red text
- Test save button confirmation dialog
- Test export generates correct filename
- Test tag filtering updates table correctly
- Test status changes auto-update dates

================================================================================
