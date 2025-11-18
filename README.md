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
│   └── weekly_view.py     # Weekly budget planning
├── widgets/               # Custom UI widgets
│   ├── chart_widget.py    # matplotlib integration widgets
│   └── theme_selector.py  # Theme switching component
├── services/              # Business logic
│   ├── transaction_manager.py  # Data operations
│   ├── analytics.py           # Spending analysis
│   └── paycheck_processor.py  # Income distribution
├── themes/                # Visual styling
│   ├── theme_manager.py   # Theme system core
│   └── assets/           # Theme-specific GIFs and images
└── dialogs/              # Modal dialogs for data entry
    ├── add_transaction_dialog.py
    ├── add_paycheck_dialog.py
    └── pay_bill_dialog.py
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
**Latest Updates** (2024-10-22):
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
