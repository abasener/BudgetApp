# BudgetApp 💰

A comprehensive desktop budget tracking application built with PyQt6 and matplotlib, designed for detailed financial management and analytics.

## 🚀 Features

### 📊 Interactive Dashboard
- **Dual Pie Charts**: Visual breakdown of total spending vs. current paycheck spending
- **Dynamic Metrics Cards**: Weekly status, account balances, and bill tracking
- **Category Color Key**: Consistent color coding across all charts
- **Hour Calculator**: Built-in tool for freelance/hourly work planning

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
- **Chart area enhancements**: Adding specialized financial visualizations
- **Data insights**: More sophisticated spending analysis
- **User experience**: Streamlined workflows for common tasks
- **Performance optimization**: Efficient data handling for large transaction sets

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

**Current Version**: Active Development  
**Status**: Feature-complete core with ongoing enhancements  
**Next Release**: Enhanced chart areas and additional financial insights

---

*Built with ❤️ for personal financial management and data-driven budgeting*
