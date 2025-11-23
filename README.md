# BudgetApp 💰

A comprehensive desktop budget tracking application built with PyQt6 and matplotlib, designed for detailed financial management and analytics.

## 🚀 Features

### 📊 Interactive Dashboard
- **Dual Pie Charts**: Visual breakdown of total spending vs. current paycheck spending
- **Dynamic Metrics Cards**: Weekly status, account balances, and bill tracking
- **Category Color Key**: Consistent color coding across all charts
- **Hour Calculator**: Built-in tool for freelance/hourly work planning
- **Time Frame Filtering**: View data for All Time, Last Year, Last Month, or Last 20 Entries

### 📅 Year Overview
- **Year Boxes**: Annual breakdown showing Income, Spent, Bills, Saving with YoY comparisons
- **Monthly Trends**: Line plot showing average activity per month across all years
- **Distribution Analysis**: Pie chart + violin plots showing spending patterns
- **Correlation Analysis**: Scatter plots showing Income vs Spending/Bills/Savings with regression
- **Year-by-Year Plots**: Smooth spline curves tracking Income, Spending, Bills, Savings over time
- **Analytics Toggle**: Filter abnormal spending across all visualizations

### 📈 Advanced Analytics
- **Spending Trends**: Line charts showing spending patterns over time
- **Bill Payment Tracking**: Monitor bill payment history and savings progress
- **Account Progress**: Visual progress bars for savings goals
- **Day-of-Week Analysis**: Identify spending patterns by weekday

### 🧾 Bills Management
- **Interactive Bills Tab**: Comprehensive bill tracking with payment history
- **Savings Status**: Track how much you've saved for each bill
- **Payment Frequency Analysis**: Bar charts of bill payment patterns
- **Management Table**: Full details of all bills with status indicators

### 📅 Weekly Planning
- **Paycheck Processing**: Bi-weekly paycheck distribution automation
- **Weekly Budget Tracking**: Monitor spending against weekly allocations
- **Transaction History**: Detailed transaction management and categorization

### 🔍 Advanced Transactions Tab *(Optional - Power User Tool)*
- **4 Sub-Tabs**: Bills, Savings, Paycheck, and Spending transaction views
- **Comprehensive Data View**: See ALL transactions including auto-generated rollovers and allocations
- **Smart Filtering**: Real-time search across all fields with sortable columns
- **Contextual Auto-Notes**: Generated descriptions showing payweek, category, day of week, and transfer destinations
- **Locked Transaction Protection**: Auto-generated transactions (rollovers, allocations) are non-editable
- **Batch Operations**: Mark multiple transactions for deletion, edit cells inline, save changes with validation
- **Change Tracking**: Edited and deleted rows tracked separately, cleared when switching sub-tabs
- **Data Validation**: Automatic validation of dates and amounts before saving to database
- **Bidirectional Transfer Visibility**: Manual transfers show on both sides (e.g., Week ↔ Savings)
- **Disabled by Default**: Toggle in Settings → Enable Transactions Tab for debugging and data inspection

### 📝 Scratch Pad Tab *(Excel-Like Workspace)*
- **Spreadsheet Interface**: Excel-like grid with 50 rows × 26 columns (A-Z)
- **Formula Support**: Excel-style formulas with `=` prefix for calculations
- **GET Function**: Pull live data from accounts and bills with `=GET(account_name, property)`
  - Account properties: `balance`, `goal`, `auto_save`
  - Bill properties: `balance`, `amount`, `frequency`, `type`, `auto_save`, `variable`
- **Built-in Functions**:
  - `SUM(range)` - Sum cell ranges like `=SUM(A1:A10)`
  - `AVERAGE(range)` - Average of cell ranges
  - `CURRENT_DATE()` - Today's date
- **Math Operations**: Standard operators (`+`, `-`, `*`, `/`) and parentheses for complex formulas
- **Cell References**: Use cell addresses (A1, B2) in formulas with support for ranges (A1:B10)
- **Text Formatting**: 4 styles - Header 1 (H1), Header 2 (H2), Normal Text (P), Notes (n)
- **Autocomplete**: Smart suggestions for functions, account names, and properties while typing
- **Formula Bar**: Edit formulas in dedicated input bar with error display
- **Cell Dependency Highlighting**: Click a cell to see which cells it depends on (light blue highlights)
- **Multi-Cell Selection**: Select and copy/paste ranges, insert cell references into formulas
- **JSON Persistence**: All formulas, values, and formatting saved automatically to workspace file
- **Error Handling**: Clear error messages for invalid formulas, missing accounts, or property mismatches

### 💼 Reimbursements Tracking
- **Separate Tracking System**: Work travel expenses and temporary out-of-pocket costs tracked independently from main budget
- **5-State Lifecycle**: Pending → Submitted → Reimbursed/Partial/Denied with auto-date tracking
- **Tag-Based Filtering**: Organize by trip/event (e.g., "Whispers25", "NYC24") for easy expense report generation
- **Bank Reconciliation**: View in Weekly tab (grayed out, italic) to match bank statements without affecting budget calculations
- **Full CRUD Operations**: Add, edit (with yellow highlighting), delete (red text marking), and export to Excel
- **Smart Export**: Auto-generates filenames like `Reimbursements_Whispers25_111925.xlsx` with export date
- **Dual Categorization**: Location/trip tags + expense categories (Hotel, Food, Transport, etc.)
- **Excel Export**: One-click export of selected reimbursements with headers (Amount, Tag, Category, Notes, Status)
- **Interactive Visualizations**:
  - **Stats Panel**: Total amount spent and status breakdown pie chart (semantic colors)
  - **Progress Bars**: Visual tracking of submitted % and reimbursed % (weighted by dollar amount)
  - **Dot Plot** *(adaptive)*: Amount vs Age scatter plot, color-coded by category (appears when window is wide enough)
  - **Tag × Category Heatmap**: Overview of spending patterns across all tags (always shows complete dataset)

### 🎨 Theme System
- **5 Built-in Themes**: Dark, Light, Coffee, Excel Blue, and Cyberpunk
- **Theme Selector**: Easy switching between visual styles
- **Font Management**: Custom fonts per theme
- **GIF Support**: Animated elements with theme-specific assets

## 🛠️ Technical Architecture

### Core Technologies
- **PyQt6**: Modern GUI framework for desktop applications
- **matplotlib**: Professional charting and data visualization
- **SQLite**: Local database for transaction and configuration storage
- **Python 3.8+**: Modern Python with type hints and dataclasses

### Key Components
- **Transaction Manager**: Handles all financial data operations
- **Analytics Engine**: Processes spending data for insights
- **Paycheck Processor**: Automates bi-weekly income distribution
- **Theme Manager**: Centralized styling and asset management

### Architecture Highlights
- **Service-oriented design**: Separated concerns for data, UI, and business logic
- **Dynamic UI sizing**: Cards and charts adapt to data volume
- **Theme-aware widgets**: All components respond to theme changes
- **Modular chart system**: Reusable chart widgets with consistent styling

## 📁 Project Structure

```
BudgetApp/
├── main.py                 # Application entry point
├── views/                  # UI components
│   ├── dashboard.py       # Main dashboard with analytics
│   ├── bills_view.py      # Bills management interface
│   ├── weekly_view.py     # Weekly budget planning
│   └── scratch_pad_view.py # Excel-like workspace with formulas
├── widgets/               # Custom UI widgets
│   ├── chart_widget.py    # matplotlib integration widgets
│   └── theme_selector.py  # Theme switching component
├── services/              # Business logic
│   ├── transaction_manager.py  # Data operations
│   ├── analytics.py           # Spending analysis
│   ├── paycheck_processor.py  # Income distribution
│   └── workspace_calculator.py # Scratch Pad formula engine
├── themes/                # Visual styling
│   ├── theme_manager.py   # Theme system core
│   └── assets/           # Theme-specific GIFs and images
├── dialogs/              # Modal dialogs for data entry
│   ├── add_transaction_dialog.py
│   ├── add_paycheck_dialog.py
│   └── pay_bill_dialog.py
└── scratch_pad_workspace.json # Saved workspace data
```

## 🎯 Current Development Focus

The application is actively being developed with focus on:
- **Phase 3: Rules & Automation (Next Up)**: Goal/Warning/Automation system
  - 📅 Planning phase - awaiting flowchart design
  - See RULES_PLANNING.md for full specification
- **Transactions Tab (COMPLETE ✅)**: Advanced data inspection interface
  - ✅ All 4 sub-tabs with real data, save/delete functionality
  - ✅ Fixed AccountHistory running_total corruption bug
  - ✅ Automatic tab refresh on switch
- **Performance optimization**: Query limiting and conditional refresh (Phase 4)

## 🔧 Installation & Usage

### Prerequisites
- Python 3.8+
- PyQt6
- matplotlib
- numpy

### Quick Start
```bash
git clone https://github.com/yourusername/BudgetApp.git
cd BudgetApp
pip install PyQt6 matplotlib numpy
python main.py
```

### Key Usage Tips
- **Add accounts first**: Use Admin → Add Account to set up your financial accounts
- **Configure bills**: Use Admin → Add Bill for recurring expenses
- **Process paychecks**: Use Tools → Add Paycheck for automated distribution
- **Track transactions**: Use Add Transaction for all spending entries

## 🎨 Themes

Choose from 5 carefully crafted themes:
- **Dark**: Classic dark mode with green accents
- **Light**: Clean light interface 
- **Coffee**: Warm browns and orange tones
- **Excel Blue**: Professional blue and yellow palette
- **Cyberpunk**: Neon sci-fi aesthetics with cyan and magenta

## 📊 Analytics Features

- **Category Breakdown**: Pie charts showing spending distribution
- **Trend Analysis**: Line charts revealing spending patterns
- **Goal Tracking**: Progress visualization for savings targets
- **Bill Forecasting**: Predictive analysis for upcoming payments
- **Weekly Summaries**: Quick insights into recent spending behavior

## 🚧 Development Status

**Current Version**: V2.0 Active Development
**Status**: Feature-complete core with ongoing enhancements
**Latest Updates** (2025-11-23):
- ✅ **Scratch Pad Tab - COMPLETE**: Excel-like workspace for budget planning and calculations
  * 50×26 spreadsheet grid with formula support (SUM, AVERAGE, GET, CURRENT_DATE)
  * Live data integration via GET function - pull account/bill balances and properties
  * Cell formatting system (H1, H2, Normal, Notes) with theme-aware styling
  * Smart autocomplete for functions, account names, and properties
  * Formula bar with error display and cell dependency highlighting
  * Multi-cell selection with copy/paste and cell reference insertion
  * JSON persistence for all formulas, values, and formatting
  * Nested function support and complex formula evaluation
  * Error handling with precise error messages for debugging
- ✅ **UI Polish & Bug Fixes** (2025-11-21):
  * Tax tab scroll area now properly displays scrollbar on initial load
  * Categories tab correlation plots increased from 5 to 4 per row (180x180px each)
  * Categories tab correlation plots now have proper padding around data points (20% range padding)
  * Theme color updates now properly refresh Categories and Reimbursements tabs
  * Fixed background colors for category selection, overview boxes, and reimbursement table/sidebar
- ✅ **Year Overview Tab - COMPLETE**: 10 comprehensive visualizations for year-over-year analysis
  * Monthly line plot showing average financial activity
  * Pie chart with analytics-aware percentage calculation
  * Violin plots showing transaction distribution patterns
  * Correlation scatter plots (Income vs Spending/Bills/Savings with β values)
  * 4 year-by-year line plots with smooth spline curves
  * 3-day bucketing for savings to reduce noise
  * Per-month averaging (not per-year) for accurate seasonal trends
- ✅ **Analytics Toggle Integration**: Normal spending filter across all visualizations
- ✅ **Smart Pie Chart Math**: Percentages calculate as % of (income - abnormal spending) when filtered
- See ReadMe2.txt for complete technical documentation

**Next Priorities**: Additional analytics features, seasonal pattern analysis

---

*Built with ❤️ for personal financial management and data-driven budgeting*

**For detailed technical documentation**, see [ReadMe2.txt](ReadMe2.txt) which contains:
- Complete rollover system specification
- AccountHistory auto-update mechanism
- Week calculation formulas with examples
- Critical bug fixes and prevention guidelines
