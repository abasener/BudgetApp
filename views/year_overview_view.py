"""
Year Overview View - Year-over-year financial analysis

This view provides comprehensive financial analysis across multiple years,
showing income, spending, bills, and savings patterns. It helps identify:
- Monthly spending trends (which months cost more/less)
- Year-over-year comparisons (spending up/down from last year)
- Correlation between income and spending/bills/savings
- Distribution patterns (consistent vs variable spending)

LEFT PANEL: Year-by-year breakdown boxes
- Income: Total paychecks
- Spent: Weekly budget spending (all transactions)
- Bills: Money actually paid from bill accounts
- Saving: Net increase in savings/bill accounts

RIGHT PANEL: Visual analytics
1. Monthly Line Plot: Average activity per month across all years
2. Pie Chart | Violin Plot: Distribution analysis
3. Correlation Plots: Income vs Spending/Bills/Savings relationships
4. Year-by-Year Line Plots: Income, Spending, Bills, Savings over time

ANALYTICS TOGGLE:
- Affects RIGHT PANEL charts only (not year boxes)
- Filters abnormal spending from visualizations
- Adjusts pie chart percentages to ensure they add up to 100%

MONTHLY AVERAGING:
- Calculates averages PER MONTH, not per year
- If December has data in 1 year only → average = sum / 1
- If August has data in 2 years → average = sum / 2
- This ensures accurate seasonal pattern analysis
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGroupBox, QScrollArea, QFrame, QToolButton, QCheckBox)
from PyQt6.QtCore import Qt
from datetime import datetime, date, timedelta
from themes import theme_manager
from models import get_db, Transaction
from views.dialogs.settings_dialog import get_setting

# Matplotlib imports for plotting
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats
import numpy as np


class YearOverviewView(QWidget):
    """View for year-over-year financial overview and analysis"""

    def __init__(self, transaction_manager, analytics_engine=None):
        super().__init__()
        self.transaction_manager = transaction_manager
        self.analytics_engine = analytics_engine
        self.year_boxes = []  # Store references to year boxes for refresh
        self.first_year = None  # Will be set to earliest year with data

        # Analytics toggle - load from settings (only affects right panel visualizations)
        self.include_analytics_only = get_setting("default_analytics_only", True)

        self.init_ui()
        self.refresh()
        self.apply_theme()

        # Connect to theme changes
        theme_manager.theme_changed.connect(self.apply_theme)

    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Left panel - Year-by-year details (scrollable)
        left_panel = self.create_left_panel()

        # Right panel - Data visualizations
        right_panel = self.create_right_panel()

        # Add to main layout with size ratios (1:3 like taxes tab)
        main_layout.addWidget(left_panel, 1)  # 25%
        main_layout.addWidget(right_panel, 3)  # 75%

        self.setLayout(main_layout)

    def create_left_panel(self):
        """Create left panel with year-by-year detail boxes"""
        # Scroll area for year boxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setMaximumWidth(400)  # Limit width like taxes tab
        scroll.setMinimumWidth(250)

        # Container widget for scroll area
        container = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_layout.setSpacing(10)
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Placeholder text
        placeholder = QLabel("Year overview details will appear here")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setFont(theme_manager.get_font("subtitle"))
        self.left_layout.addWidget(placeholder)

        container.setLayout(self.left_layout)
        scroll.setWidget(container)

        return scroll

    def create_right_panel(self):
        """Create right panel with data visualizations"""
        panel = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_layout.setSpacing(10)

        # Header with title, refresh button, and analytics toggle
        header = QHBoxLayout()
        header.setSpacing(10)

        # Title
        title = QLabel("Year-over-Year Analysis")
        title.setFont(theme_manager.get_font("title"))
        header.addWidget(title)

        # Refresh button - compact tool button with emoji (styled like dashboard)
        self.refresh_button = QToolButton()
        self.refresh_button.setText("🔄")
        self.refresh_button.setToolTip("Refresh Year Overview")
        self.refresh_button.setFixedSize(40, 30)
        self.refresh_button.clicked.connect(self.refresh)
        header.addWidget(self.refresh_button)

        # Analytics toggle - styled checkbox (only affects right panel charts)
        self.analytics_toggle = QCheckBox("Normal Spending Only")
        self.analytics_toggle.setChecked(self.include_analytics_only)
        self.analytics_toggle.toggled.connect(self.toggle_analytics_mode)
        self.analytics_toggle.setToolTip("Filter abnormal transactions from visualizations (does not affect year boxes)")
        self.analytics_toggle.setFont(theme_manager.get_font("main"))
        header.addWidget(self.analytics_toggle)

        header.addStretch()  # Push everything to the left

        self.right_layout.addLayout(header)

        # Create scroll area for all plots
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Container for all plots
        plots_container = QWidget()
        self.plots_layout = QVBoxLayout()
        self.plots_layout.setSpacing(15)

        # Create all visualization sections
        self.create_yoy_growth_bars()
        self.create_pie_and_violin_row()  # Combined row
        self.create_correlation_plots()
        self.create_line_plots()

        plots_container.setLayout(self.plots_layout)
        scroll.setWidget(plots_container)
        self.right_layout.addWidget(scroll)

        panel.setLayout(self.right_layout)
        return panel

    def get_year_color(self, year):
        """Get consistent color for a year based on chart_colors"""
        if self.first_year is None:
            return None

        colors = theme_manager.get_colors()
        chart_colors = colors.get('chart_colors', ['#44C01E', '#3F0979', '#D6CA18'])

        # Calculate index based on years since first_year
        year_index = year - self.first_year
        color_index = year_index % len(chart_colors)

        return chart_colors[color_index]

    def get_year_data(self, year):
        """
        Calculate financial data for a specific year

        IMPORTANT - Understanding the Budget System:
        ==========================================
        The app uses an automatic rollover system where:
        1. Each paycheck is allocated to weekly budget and bills
        2. Any REMAINDER automatically rolls into designated savings account
        3. This means: Income ALWAYS = Spent + Bills + Savings (fully accounted)

        Category Definitions:
        =====================
        INCOME: All paychecks received in the year

        SPENT: All weekly budget spending (spending transactions)
            - Includes normal spending AND abnormal spending (include_in_analytics=false)
            - Does NOT include withdrawals from savings (those become spending transactions)

        BILLS: Money actually PAID from bill accounts (bill_pay transactions)
            - NOT deposits to bill accounts (those are savings)
            - Only actual bills paid (negative transactions from bill accounts)

        SAVINGS: Net increase in savings/bill account balances
            - = (Deposits to savings accounts) + (Deposits to bill accounts)
            -   MINUS (Bills paid from bill accounts)
            -   MINUS (Withdrawals from savings accounts)
            - This captures:
                * Weekly rollover to savings ✓
                * Explicit deposits ✓
                * Money saved in bills (deposited but not yet spent) ✓
                * MINUS bills actually paid ✓
                * MINUS emergency withdrawals from savings ✓

        Why this works:
        ===============
        Income = Spent + Bills + Savings
        Because the rollover system ensures all income is either:
            a) Spent from weekly budget (Spent)
            b) Paid as bills (Bills)
            c) Everything else stays in savings/bills (Savings)
        """
        try:
            db = get_db()

            year_start = date(year, 1, 1)
            year_end = date(year, 12, 31)

            # ===== INCOME: All paychecks =====
            income_transactions = db.query(Transaction).filter(
                Transaction.date >= year_start,
                Transaction.date <= year_end,
                Transaction.transaction_type == "income"
            ).all()

            total_income = sum(t.amount for t in income_transactions)

            # ===== SPENT: All weekly budget spending =====
            # This includes EVERYTHING spent from weekly budget (normal + abnormal)
            spending_transactions = db.query(Transaction).filter(
                Transaction.date >= year_start,
                Transaction.date <= year_end,
                Transaction.transaction_type == "spending"
            ).all()

            total_spending = sum(t.amount for t in spending_transactions)

            # ===== BILLS: Money actually paid from bill accounts =====
            # These are bill_pay transactions (negative from bill accounts)
            bill_pay_transactions = db.query(Transaction).filter(
                Transaction.date >= year_start,
                Transaction.date <= year_end,
                Transaction.transaction_type == "bill_pay"
            ).all()

            total_bills = sum(t.amount for t in bill_pay_transactions)

            # ===== SAVINGS: Net increase in savings/bill balances =====
            # Step 1: Get all deposits TO savings and bill accounts (positive = saving)
            saving_deposits = db.query(Transaction).filter(
                Transaction.date >= year_start,
                Transaction.date <= year_end,
                Transaction.transaction_type == "saving"
            ).all()

            total_deposits = sum(t.amount for t in saving_deposits)

            # Step 2: Get all withdrawals FROM savings accounts (negative = unsaving)
            # These are spending_from_savings type or negative saving transactions
            withdrawal_transactions = db.query(Transaction).filter(
                Transaction.date >= year_start,
                Transaction.date <= year_end,
                Transaction.transaction_type == "spending_from_savings"
            ).all()

            total_withdrawals = sum(t.amount for t in withdrawal_transactions)

            # Step 3: Calculate net savings
            # Net Savings = (Deposits to savings/bills) - (Bills paid) - (Withdrawals from savings)
            # Note: total_bills already calculated above (money paid from bill accounts)
            total_savings = total_deposits - total_bills - total_withdrawals

            db.close()

            return {
                'year': year,
                'total_income': total_income,
                'total_spending': total_spending,
                'total_bills': total_bills,
                'total_savings': total_savings
            }

        except Exception as e:
            print(f"Error calculating year data for {year}: {e}")
            return {
                'year': year,
                'total_income': 0,
                'total_spending': 0,
                'total_bills': 0,
                'total_savings': 0
            }

    def create_year_box(self, year_data, prev_year_data=None):
        """Create a box widget for a year's financial data"""
        year = year_data['year']
        year_box = QGroupBox(str(year))

        # Apply year color and larger font to the title
        year_color = self.get_year_color(year)
        if year_color:
            title_font = theme_manager.get_font("header")
            base_size = title_font.pointSize()
            new_size = int(base_size * 1.5)
            title_font.setPointSize(new_size)
            year_box.setFont(title_font)

            colors = theme_manager.get_colors()
            year_box.setStyleSheet(f"""
                QGroupBox {{
                    font-weight: bold;
                    color: {year_color};
                    border: 2px solid {colors['border']};
                    border-radius: 6px;
                    margin-top: 12px;
                    padding-top: 10px;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }}
            """)

        # Create layout for year data
        layout = QVBoxLayout()
        layout.setSpacing(5)

        # Get data values
        income = year_data['total_income']
        spending = year_data['total_spending']
        bills = year_data['total_bills']
        savings = year_data['total_savings']

        # Calculate percentages of income
        spending_pct = (spending / income * 100) if income > 0 else 0
        bills_pct = (bills / income * 100) if income > 0 else 0
        savings_pct = (savings / income * 100) if income > 0 else 0

        # Calculate year-over-year changes
        if prev_year_data:
            income_change = ((income - prev_year_data['total_income']) / prev_year_data['total_income'] * 100) if prev_year_data['total_income'] > 0 else 0
            spending_change = ((spending - prev_year_data['total_spending']) / prev_year_data['total_spending'] * 100) if prev_year_data['total_spending'] > 0 else 0
            bills_change = ((bills - prev_year_data['total_bills']) / prev_year_data['total_bills'] * 100) if prev_year_data['total_bills'] > 0 else 0
            savings_change = ((savings - prev_year_data['total_savings']) / prev_year_data['total_savings'] * 100) if prev_year_data['total_savings'] > 0 else 0
        else:
            income_change = spending_change = bills_change = savings_change = None

        # Helper to get change arrow/emoji
        def get_change_indicator(change):
            if change is None:
                return "─"
            elif change > 0:
                return f"↑{change:.1f}%"
            elif change < 0:
                return f"↓{abs(change):.1f}%"
            else:
                return "─"

        # Create monospace font for alignment
        mono_font = theme_manager.get_font("monospace")

        # Income row
        income_text = f"Income:  ${income:>8,.0f}          {get_change_indicator(income_change)}"
        income_label = QLabel(income_text)
        income_label.setFont(mono_font)
        layout.addWidget(income_label)

        # Spending row
        spending_text = f"Spent:   ${spending:>8,.0f}  {spending_pct:>5.1f}%  {get_change_indicator(spending_change)}"
        spending_label = QLabel(spending_text)
        spending_label.setFont(mono_font)
        layout.addWidget(spending_label)

        # Bills row
        bills_text = f"Bills:   ${bills:>8,.0f}  {bills_pct:>5.1f}%  {get_change_indicator(bills_change)}"
        bills_label = QLabel(bills_text)
        bills_label.setFont(mono_font)
        layout.addWidget(bills_label)

        # Savings row
        savings_text = f"Saving:  ${savings:>8,.0f}  {savings_pct:>5.1f}%  {get_change_indicator(savings_change)}"
        savings_label = QLabel(savings_text)
        savings_label.setFont(mono_font)
        layout.addWidget(savings_label)

        year_box.setLayout(layout)
        return year_box

    def create_correlation_plots(self):
        """Create 3 correlation scatter plots: Income vs Spending/Bills/Savings"""
        # Create figure with 1x3 subplots - square subplots
        self.correlation_figure = Figure(figsize=(12, 4))
        self.correlation_canvas = FigureCanvas(self.correlation_figure)
        self.correlation_canvas.setMinimumHeight(280)
        self.correlation_canvas.setMaximumHeight(320)
        self.plots_layout.addWidget(self.correlation_canvas)

    def create_yoy_growth_bars(self):
        """Create monthly average line plot for all 4 categories"""
        self.yoy_figure = Figure(figsize=(12, 5))
        self.yoy_canvas = FigureCanvas(self.yoy_figure)
        self.yoy_canvas.setMinimumHeight(400)
        self.plots_layout.addWidget(self.yoy_canvas)

    def create_pie_and_violin_row(self):
        """Create pie chart and violin plot side by side"""
        # Create horizontal layout for this row
        row_widget = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setSpacing(10)
        row_layout.setContentsMargins(0, 0, 0, 0)

        # Pie chart on left (1/3 width)
        self.pie_figure = Figure(figsize=(4, 2.5))
        self.pie_canvas = FigureCanvas(self.pie_figure)
        self.pie_canvas.setMinimumHeight(200)
        self.pie_canvas.setMaximumHeight(250)
        row_layout.addWidget(self.pie_canvas, stretch=1)

        # Violin plot on right (2/3 width)
        self.violin_figure = Figure(figsize=(8, 2.5))
        self.violin_canvas = FigureCanvas(self.violin_figure)
        self.violin_canvas.setMinimumHeight(200)
        self.violin_canvas.setMaximumHeight(250)
        row_layout.addWidget(self.violin_canvas, stretch=2)

        row_widget.setLayout(row_layout)
        self.plots_layout.addWidget(row_widget)

    def create_line_plots(self):
        """Create 4 line plots (Income, Spending, Bills, Savings) like tax tab"""
        # Income plot
        self.income_figure = Figure(figsize=(12, 5))
        self.income_canvas = FigureCanvas(self.income_figure)
        self.income_canvas.setMinimumHeight(400)
        self.plots_layout.addWidget(self.income_canvas)

        # Spending plot
        self.spending_figure = Figure(figsize=(12, 5))
        self.spending_canvas = FigureCanvas(self.spending_figure)
        self.spending_canvas.setMinimumHeight(400)
        self.plots_layout.addWidget(self.spending_canvas)

        # Bills plot
        self.bills_figure = Figure(figsize=(12, 5))
        self.bills_canvas = FigureCanvas(self.bills_figure)
        self.bills_canvas.setMinimumHeight(400)
        self.plots_layout.addWidget(self.bills_canvas)

        # Savings plot
        self.savings_figure = Figure(figsize=(12, 5))
        self.savings_canvas = FigureCanvas(self.savings_figure)
        self.savings_canvas.setMinimumHeight(400)
        self.plots_layout.addWidget(self.savings_canvas)

    def update_correlation_plots(self):
        """Update correlation scatter plots"""
        try:
            self.correlation_figure.clear()

            # Get data for all years
            db = get_db()
            all_years = db.query(Transaction.date).all()
            if not all_years:
                db.close()
                return

            unique_years = sorted(set(d[0].year for d in all_years if d[0]))

            # Collect data points for each year
            year_incomes = []
            year_spendings = []
            year_bills = []
            year_savings = []
            years_list = []

            for year in unique_years:
                year_data = self.get_year_data(year)

                # Calculate averages (per paycheck or per month)
                year_start = date(year, 1, 1)
                year_end = date(year, 12, 31)

                # Count paychecks
                paycheck_count = db.query(Transaction).filter(
                    Transaction.date >= year_start,
                    Transaction.date <= year_end,
                    Transaction.transaction_type == "income"
                ).count()

                if paycheck_count > 0:
                    avg_income = year_data['total_income'] / paycheck_count
                    avg_spending = year_data['total_spending'] / paycheck_count
                    avg_bills = year_data['total_bills'] / paycheck_count
                    avg_savings = year_data['total_savings'] / paycheck_count

                    year_incomes.append(avg_income)
                    year_spendings.append(avg_spending)
                    year_bills.append(avg_bills)
                    year_savings.append(avg_savings)
                    years_list.append(year)

            db.close()

            if len(years_list) < 2:
                # Not enough data for correlation
                ax = self.correlation_figure.add_subplot(111)
                ax.text(0.5, 0.5, "Need at least 2 years of data for correlation analysis",
                       ha='center', va='center', transform=ax.transAxes)
                self.correlation_canvas.draw()
                return

            # Get theme colors
            colors = theme_manager.get_colors()
            text_color = colors.get('text_primary', '#000000')
            bg_color = colors.get('background', '#FFFFFF')

            # Create 3 scatter plots
            datasets = [
                (year_spendings, 'Spending'),
                (year_bills, 'Bills'),
                (year_savings, 'Savings')
            ]

            for idx, (x_data, x_label) in enumerate(datasets):
                ax = self.correlation_figure.add_subplot(1, 3, idx + 1)

                # Plot points with year colors
                for i, year in enumerate(years_list):
                    year_color = self.get_year_color(year)
                    ax.scatter(x_data[i], year_incomes[i], color=year_color, s=100, alpha=0.7, edgecolor='black', linewidth=1)

                # Calculate linear regression if enough points
                if len(x_data) >= 2:
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, year_incomes)

                    # Plot regression line
                    x_range_vals = np.linspace(min(x_data), max(x_data), 100)
                    y_range_vals = slope * x_range_vals + intercept
                    ax.plot(x_range_vals, y_range_vals, 'r--', linewidth=2, alpha=0.5)

                    # Add beta to title
                    ax.set_title(f'Income vs {x_label}\n(β = {slope:.2f})', color=text_color, fontsize=10)
                else:
                    ax.set_title(f'Income vs {x_label}', color=text_color, fontsize=10)

                ax.set_xlabel(f'{x_label} per Paycheck ($)', color=text_color, fontsize=8)

                # Only show y-axis label on first (leftmost) plot
                if idx == 0:
                    ax.set_ylabel('Income per Paycheck ($)', color=text_color, fontsize=8)
                else:
                    ax.set_yticklabels([])  # Remove y-axis labels on right plots

                ax.tick_params(colors=text_color, labelsize=8)
                ax.set_facecolor(bg_color)
                ax.grid(True, alpha=0.3)

                # Add padding to axes (20% of range on each side)
                if len(x_data) > 0 and len(year_incomes) > 0:
                    x_range = max(x_data) - min(x_data)
                    y_range = max(year_incomes) - min(year_incomes)
                    padding = 0.20  # 20% padding

                    x_min = min(x_data) - x_range * padding
                    x_max = max(x_data) + x_range * padding
                    y_min = min(year_incomes) - y_range * padding
                    y_max = max(year_incomes) + y_range * padding

                    ax.set_xlim(x_min, x_max)
                    ax.set_ylim(y_min, y_max)
                    # No aspect ratio constraint - let plots naturally match height

                # Format axes
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.1f}k' if x >= 1000 else f'${x:.0f}'))
                ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.1f}k' if x >= 1000 else f'${x:.0f}'))

            self.correlation_figure.patch.set_facecolor(bg_color)
            self.correlation_figure.tight_layout(pad=2.5)  # Extra padding for labels
            self.correlation_canvas.draw()

        except Exception as e:
            print(f"Error updating correlation plots: {e}")

    def update_yoy_growth_bars(self):
        """Update monthly average line plot for all 4 categories"""
        try:
            self.yoy_figure.clear()
            ax = self.yoy_figure.add_subplot(111)

            # Get data for all years
            db = get_db()
            all_years = db.query(Transaction.date).all()
            if not all_years:
                db.close()
                return

            unique_years = sorted(set(d[0].year for d in all_years if d[0]))

            # Calculate monthly averages - track count per month to average correctly
            monthly_income = [0] * 12
            monthly_spending = [0] * 12
            monthly_bills = [0] * 12
            monthly_savings = [0] * 12
            monthly_counts = [0] * 12  # Track how many years have data for each month

            # Aggregate data by month across all years
            for year in unique_years:
                year_start = date(year, 1, 1)
                year_end = date(year, 12, 31)

                # Track which months have data in this year
                months_with_data = set()

                # Income by month
                income_txns = db.query(Transaction).filter(
                    Transaction.date >= year_start,
                    Transaction.date <= year_end,
                    Transaction.transaction_type == "income"
                ).all()
                for t in income_txns:
                    monthly_income[t.date.month - 1] += t.amount
                    months_with_data.add(t.date.month - 1)

                # Spending by month
                spending_query = db.query(Transaction).filter(
                    Transaction.date >= year_start,
                    Transaction.date <= year_end,
                    Transaction.transaction_type == "spending"
                )
                if self.include_analytics_only:
                    spending_query = spending_query.filter(Transaction.include_in_analytics == True)
                spending_txns = spending_query.all()
                for t in spending_txns:
                    monthly_spending[t.date.month - 1] += t.amount
                    months_with_data.add(t.date.month - 1)

                # Bills by month
                bill_txns = db.query(Transaction).filter(
                    Transaction.date >= year_start,
                    Transaction.date <= year_end,
                    Transaction.transaction_type == "bill_pay"
                ).all()
                for t in bill_txns:
                    monthly_bills[t.date.month - 1] += t.amount
                    months_with_data.add(t.date.month - 1)

                # Savings by month
                saving_txns = db.query(Transaction).filter(
                    Transaction.date >= year_start,
                    Transaction.date <= year_end,
                    Transaction.transaction_type == "saving"
                ).all()
                for t in saving_txns:
                    monthly_savings[t.date.month - 1] += t.amount
                    months_with_data.add(t.date.month - 1)

                # Increment count for months that had data this year
                for month_idx in months_with_data:
                    monthly_counts[month_idx] += 1

            db.close()

            # Calculate averages - only divide by count of years with data for that month
            for i in range(12):
                if monthly_counts[i] > 0:
                    monthly_income[i] = monthly_income[i] / monthly_counts[i]
                    monthly_spending[i] = monthly_spending[i] / monthly_counts[i]
                    monthly_bills[i] = monthly_bills[i] / monthly_counts[i]
                    monthly_savings[i] = monthly_savings[i] / monthly_counts[i]

            # Get theme colors (use pie chart colors for consistency)
            colors = theme_manager.get_colors()
            text_color = colors.get('text_primary', '#000000')
            bg_color = colors.get('background', '#FFFFFF')
            accent_colors = colors.get('accent_colors', ['#44C01E', '#3F0979', '#D6CA18', '#FF6B6B'])

            # Month labels
            months = range(1, 13)
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            # Plot 4 lines
            ax.plot(months, monthly_income, marker='o', markersize=6, linewidth=2.5,
                   label='Income', color=accent_colors[0])
            ax.plot(months, monthly_spending, marker='s', markersize=6, linewidth=2.5,
                   label='Spending', color=accent_colors[1], alpha=0.40)
            ax.plot(months, monthly_bills, marker='^', markersize=6, linewidth=2.5,
                   label='Bills', color=accent_colors[2], alpha=0.40)
            ax.plot(months, monthly_savings, marker='d', markersize=6, linewidth=2.5,
                   label='Savings', color=accent_colors[3] if len(accent_colors) > 3 else accent_colors[0], alpha=0.40)

            # Format
            ax.set_xlabel('Month', color=text_color, fontsize=10)
            ax.set_ylabel('Average Amount ($)', color=text_color, fontsize=10)
            ax.set_title('Average Monthly Financial Activity', color=text_color, fontsize=12)
            ax.set_xticks(months)
            ax.set_xticklabels(month_names, fontsize=9)
            ax.legend(fontsize=10)
            ax.tick_params(colors=text_color, labelsize=9)
            ax.set_facecolor(bg_color)
            ax.grid(True, alpha=0.3)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.1f}k' if x >= 1000 else f'${x:.0f}'))

            self.yoy_figure.patch.set_facecolor(bg_color)
            self.yoy_figure.tight_layout(pad=2.0)
            self.yoy_canvas.draw()

        except Exception as e:
            print(f"Error updating monthly line plot: {e}")

    def update_master_pie_chart(self):
        """Update master percentage breakdown pie chart"""
        try:
            self.pie_figure.clear()
            ax = self.pie_figure.add_subplot(111)

            # Get data for all years
            db = get_db()
            all_years = db.query(Transaction.date).all()
            if not all_years:
                db.close()
                return

            unique_years = sorted(set(d[0].year for d in all_years if d[0]))

            # Calculate totals across all years (respecting analytics toggle)
            total_income = 0
            total_normal_spending = 0
            total_abnormal_spending = 0
            total_bills = 0
            total_savings = 0

            for year in unique_years:
                year_start = date(year, 1, 1)
                year_end = date(year, 12, 31)

                # Total income
                income_txns = db.query(Transaction).filter(
                    Transaction.date >= year_start,
                    Transaction.date <= year_end,
                    Transaction.transaction_type == "income"
                ).all()
                total_income += sum(t.amount for t in income_txns)

                # Normal spending (analytics only)
                normal_spending_txns = db.query(Transaction).filter(
                    Transaction.date >= year_start,
                    Transaction.date <= year_end,
                    Transaction.transaction_type == "spending",
                    Transaction.include_in_analytics == True
                ).all()
                total_normal_spending += sum(t.amount for t in normal_spending_txns)

                # Abnormal spending (excluded from analytics)
                abnormal_spending_txns = db.query(Transaction).filter(
                    Transaction.date >= year_start,
                    Transaction.date <= year_end,
                    Transaction.transaction_type == "spending",
                    Transaction.include_in_analytics == False
                ).all()
                total_abnormal_spending += sum(t.amount for t in abnormal_spending_txns)

                # Bills
                bill_txns = db.query(Transaction).filter(
                    Transaction.date >= year_start,
                    Transaction.date <= year_end,
                    Transaction.transaction_type == "bill_pay"
                ).all()
                total_bills += sum(t.amount for t in bill_txns)

                # Savings
                saving_txns = db.query(Transaction).filter(
                    Transaction.date >= year_start,
                    Transaction.date <= year_end,
                    Transaction.transaction_type == "saving"
                ).all()
                total_savings += sum(t.amount for t in saving_txns)

            db.close()

            num_years = len(unique_years) if unique_years else 1

            # When analytics toggle is ON: use only normal spending, base percentages on (income - abnormal)
            # When analytics toggle is OFF: use all spending, base percentages on total income
            if self.include_analytics_only:
                # Pie chart as % of (income - abnormal spending)
                effective_income = (total_income - total_abnormal_spending) / num_years
                avg_spending = total_normal_spending / num_years
            else:
                # Pie chart as % of total income
                effective_income = total_income / num_years
                avg_spending = (total_normal_spending + total_abnormal_spending) / num_years

            avg_bills = total_bills / num_years
            avg_savings = total_savings / num_years

            # Create pie chart with proper percentages
            sizes = [avg_spending, avg_bills, avg_savings]
            labels = ['Spending', 'Bills', 'Savings']

            colors = theme_manager.get_colors()
            accent_colors = colors.get('accent_colors', ['#44C01E', '#3F0979', '#D6CA18'])
            text_color = colors.get('text_primary', '#000000')
            bg_color = colors.get('background', '#FFFFFF')

            # Calculate percentages manually based on effective income
            total = sum(sizes)
            percentages = [s / effective_income * 100 if effective_income > 0 else 0 for s in sizes]

            wedges, texts, autotexts = ax.pie(sizes, labels=labels,
                                               autopct=lambda pct: f'{pct:.1f}%',
                                               colors=accent_colors[:3], startangle=90)

            # Override autopct with correct percentages
            for i, autotext in enumerate(autotexts):
                autotext.set_text(f'{percentages[i]:.1f}%')
                autotext.set_color('white')
                autotext.set_fontsize(9)
                autotext.set_weight('bold')

            for text in texts:
                text.set_color(text_color)
                text.set_fontsize(10)

            title_suffix = " (Normal Only)" if self.include_analytics_only else ""
            ax.set_title(f'Average Distribution of Income{title_suffix}', color=text_color, fontsize=12)

            self.pie_figure.patch.set_facecolor(bg_color)
            self.pie_figure.tight_layout()
            self.pie_canvas.draw()

        except Exception as e:
            print(f"Error updating master pie chart: {e}")

    def update_violin_plots(self):
        """Update violin/box plot comparison"""
        try:
            self.violin_figure.clear()
            ax = self.violin_figure.add_subplot(111)

            # Get data for all years
            db = get_db()
            all_years = db.query(Transaction.date).all()
            if not all_years:
                db.close()
                return

            unique_years = sorted(set(d[0].year for d in all_years if d[0]))

            # Collect all transaction amounts by category
            income_amounts = []
            spending_amounts = []
            bill_amounts = []
            saving_amounts = []

            for year in unique_years:
                year_start = date(year, 1, 1)
                year_end = date(year, 12, 31)

                # Get all transactions
                income_txns = db.query(Transaction).filter(
                    Transaction.date >= year_start,
                    Transaction.date <= year_end,
                    Transaction.transaction_type == "income"
                ).all()
                income_amounts.extend([t.amount for t in income_txns])

                spending_query = db.query(Transaction).filter(
                    Transaction.date >= year_start,
                    Transaction.date <= year_end,
                    Transaction.transaction_type == "spending"
                )
                if self.include_analytics_only:
                    spending_query = spending_query.filter(Transaction.include_in_analytics == True)
                spending_txns = spending_query.all()
                spending_amounts.extend([t.amount for t in spending_txns])

                bill_txns = db.query(Transaction).filter(
                    Transaction.date >= year_start,
                    Transaction.date <= year_end,
                    Transaction.transaction_type == "bill_pay"
                ).all()
                bill_amounts.extend([t.amount for t in bill_txns])

                saving_txns = db.query(Transaction).filter(
                    Transaction.date >= year_start,
                    Transaction.date <= year_end,
                    Transaction.transaction_type == "saving"
                ).all()
                saving_amounts.extend([t.amount for t in saving_txns])

            db.close()

            # Create violin plot
            data_to_plot = [income_amounts, spending_amounts, bill_amounts, saving_amounts]
            labels = ['Income', 'Spending', 'Bills', 'Savings']

            colors = theme_manager.get_colors()
            text_color = colors.get('text_primary', '#000000')
            bg_color = colors.get('background', '#FFFFFF')
            accent_color = colors.get('accent', '#44C01E')

            parts = ax.violinplot(data_to_plot, positions=range(1, 5), showmeans=True, showmedians=True)

            # Color the violins
            for pc in parts['bodies']:
                pc.set_facecolor(accent_color)
                pc.set_alpha(0.5)

            ax.set_xticks(range(1, 5))
            ax.set_xticklabels(labels)
            ax.set_ylabel('Amount ($)', color=text_color)
            ax.set_title('Transaction Amount Distribution', color=text_color)
            ax.tick_params(colors=text_color)
            ax.set_facecolor(bg_color)
            ax.grid(True, alpha=0.3, axis='y')
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.1f}k' if x >= 1000 else f'${x:.0f}'))

            self.violin_figure.patch.set_facecolor(bg_color)
            self.violin_figure.tight_layout()
            self.violin_canvas.draw()

        except Exception as e:
            print(f"Error updating violin plots: {e}")

    def update_line_plots(self):
        """Update all 4 line plots"""
        self.update_income_plot()
        self.update_spending_plot()
        self.update_bills_plot()
        self.update_savings_plot()

    def update_income_plot(self):
        """Update income by year line plot"""
        try:
            self.income_figure.clear()
            ax = self.income_figure.add_subplot(111)

            db = get_db()
            income_transactions = db.query(Transaction).filter(
                Transaction.transaction_type == "income"
            ).order_by(Transaction.date).all()

            if not income_transactions:
                ax.text(0.5, 0.5, "No income data available",
                       ha='center', va='center', transform=ax.transAxes)
                self.income_canvas.draw()
                db.close()
                return

            # Group by year
            years_data = {}
            for t in income_transactions:
                year = t.date.year
                if year not in years_data:
                    years_data[year] = []
                years_data[year].append({'date': t.date, 'amount': t.amount})

            current_year = date.today().year

            # Plot each year
            for year, transactions in sorted(years_data.items()):
                transactions.sort(key=lambda x: x['date'])

                dates = []
                amounts = []
                for trans in transactions:
                    aligned_date = trans['date'].replace(year=current_year)
                    dates.append(aligned_date)
                    amounts.append(trans['amount'])

                year_color = self.get_year_color(year)
                ax.plot(dates, amounts, marker='o', markersize=4, color=year_color,
                       label=str(year), linewidth=2)

            # Format
            ax.set_xlim(date(current_year, 1, 1), date(current_year, 12, 31))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            ax.set_title('Income by Year')
            ax.grid(True, alpha=0.3)
            ax.legend()

            # Apply theme
            colors = theme_manager.get_colors()
            self.income_figure.patch.set_facecolor(colors['background'])
            ax.set_facecolor(colors['background'])
            ax.tick_params(colors=colors['text_secondary'])
            ax.title.set_color(colors['text_primary'])

            self.income_figure.tight_layout()
            self.income_canvas.draw()
            db.close()

        except Exception as e:
            print(f"Error updating income plot: {e}")

    def update_spending_plot(self):
        """Update spending by year line plot with daily datapoints and smooth trendline"""
        try:
            self.spending_figure.clear()
            ax = self.spending_figure.add_subplot(111)

            db = get_db()

            # Get all years with data
            all_years = db.query(Transaction.date).all()
            if not all_years:
                db.close()
                ax.text(0.5, 0.5, "No spending data available",
                       ha='center', va='center', transform=ax.transAxes)
                self.spending_canvas.draw()
                return

            unique_years = sorted(set(d[0].year for d in all_years if d[0]))
            current_year = date.today().year

            # Plot each year
            for year in unique_years:
                year_start = date(year, 1, 1)
                year_end = date(year, 12, 31)

                # Create daily spending data (including $0 days)
                daily_spending = {}
                current_date = year_start
                while current_date <= year_end:
                    daily_spending[current_date] = 0
                    current_date = current_date + timedelta(days=1)

                # Get spending transactions
                spending_query = db.query(Transaction).filter(
                    Transaction.date >= year_start,
                    Transaction.date <= year_end,
                    Transaction.transaction_type == "spending"
                )
                if self.include_analytics_only:
                    spending_query = spending_query.filter(Transaction.include_in_analytics == True)

                spending_txns = spending_query.all()
                for t in spending_txns:
                    if t.date in daily_spending:
                        daily_spending[t.date] += t.amount

                # Convert to lists
                dates = sorted(daily_spending.keys())
                amounts = [daily_spending[d] for d in dates]

                if not dates:
                    continue

                # Align dates to current year for overlay
                try:
                    aligned_dates = []
                    for d in dates:
                        try:
                            # Handle Feb 29 in leap years
                            if d.month == 2 and d.day == 29:
                                aligned_dates.append(date(current_year, 2, 28))
                            else:
                                aligned_dates.append(date(current_year, d.month, d.day))
                        except ValueError:
                            # Skip invalid dates
                            continue
                except Exception as e:
                    print(f"Error aligning dates: {e}")
                    continue

                if len(aligned_dates) != len(amounts):
                    amounts = amounts[:len(aligned_dates)]

                # Plot daily points (small, semi-transparent)
                year_color = self.get_year_color(year)
                ax.scatter(aligned_dates, amounts, s=2, alpha=0.3, color=year_color)

                # Calculate smooth trendline using LOWESS (locally weighted scatterplot smoothing)
                if len(amounts) >= 30:
                    # Convert dates to numeric for smoothing
                    x_numeric = np.arange(len(aligned_dates))

                    # Simple moving average for smoothing
                    window = 14  # 2-week window
                    weights = np.ones(window) / window
                    smoothed = np.convolve(amounts, weights, mode='valid')
                    smooth_dates = aligned_dates[window-1:]

                    # Interpolate for smoother curve
                    if len(smooth_dates) > 10:
                        from scipy.interpolate import make_interp_spline
                        x_smooth = np.linspace(0, len(smooth_dates)-1, len(smooth_dates)*3)
                        spl = make_interp_spline(range(len(smooth_dates)), smoothed, k=3)
                        y_smooth = spl(x_smooth)

                        # Create corresponding dates
                        date_indices = np.linspace(0, len(smooth_dates)-1, len(x_smooth))
                        smooth_dates_interp = [smooth_dates[int(i)] for i in date_indices]

                        ax.plot(smooth_dates_interp, y_smooth, color=year_color, linewidth=2.5, label=str(year), alpha=0.8)
                    else:
                        ax.plot(smooth_dates, smoothed, color=year_color, linewidth=2, label=str(year))
                else:
                    ax.plot(aligned_dates, amounts, color=year_color, linewidth=2, label=str(year))

            # Format
            ax.set_xlim(date(current_year, 1, 1), date(current_year, 12, 31))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            ax.set_title('Spending by Year (Smoothed Trend)')
            ax.grid(True, alpha=0.3)
            ax.legend()

            # Apply theme
            colors = theme_manager.get_colors()
            self.spending_figure.patch.set_facecolor(colors['background'])
            ax.set_facecolor(colors['background'])
            ax.tick_params(colors=colors['text_secondary'])
            ax.title.set_color(colors['text_primary'])

            self.spending_figure.tight_layout()
            self.spending_canvas.draw()
            db.close()

        except Exception as e:
            print(f"Error updating spending plot: {e}")
            import traceback
            traceback.print_exc()

    def update_bills_plot(self):
        """Update bills by year line plot with smooth trendline"""
        try:
            self.bills_figure.clear()
            ax = self.bills_figure.add_subplot(111)

            db = get_db()
            bill_transactions = db.query(Transaction).filter(
                Transaction.transaction_type == "bill_pay"
            ).order_by(Transaction.date).all()

            if not bill_transactions:
                ax.text(0.5, 0.5, "No bill payment data available",
                       ha='center', va='center', transform=ax.transAxes)
                self.bills_canvas.draw()
                db.close()
                return

            # Group by year
            years_data = {}
            for t in bill_transactions:
                year = t.date.year
                if year not in years_data:
                    years_data[year] = []
                years_data[year].append({'date': t.date, 'amount': t.amount})

            current_year = date.today().year

            # Plot each year
            for year, transactions in sorted(years_data.items()):
                transactions.sort(key=lambda x: x['date'])

                dates = []
                amounts = []
                for trans in transactions:
                    try:
                        # Handle Feb 29 in leap years
                        if trans['date'].month == 2 and trans['date'].day == 29:
                            aligned_date = date(current_year, 2, 28)
                        else:
                            aligned_date = date(current_year, trans['date'].month, trans['date'].day)
                        dates.append(aligned_date)
                        amounts.append(trans['amount'])
                    except ValueError:
                        continue

                year_color = self.get_year_color(year)

                # Plot points
                ax.scatter(dates, amounts, s=30, alpha=0.6, color=year_color, edgecolor='black', linewidth=0.5)

                # Add smooth trendline if enough points
                if len(dates) >= 5:
                    from scipy.interpolate import make_interp_spline
                    # Sort by date
                    sorted_indices = sorted(range(len(dates)), key=lambda i: dates[i])
                    sorted_dates = [dates[i] for i in sorted_indices]
                    sorted_amounts = [amounts[i] for i in sorted_indices]

                    # Convert to numeric for interpolation
                    x_numeric = np.arange(len(sorted_dates))
                    x_smooth = np.linspace(0, len(sorted_dates)-1, len(sorted_dates)*5)

                    spl = make_interp_spline(x_numeric, sorted_amounts, k=min(3, len(sorted_dates)-1))
                    y_smooth = spl(x_smooth)

                    # Create corresponding dates
                    date_indices = np.linspace(0, len(sorted_dates)-1, len(x_smooth))
                    smooth_dates_interp = [sorted_dates[int(i)] for i in date_indices]

                    ax.plot(smooth_dates_interp, y_smooth, color=year_color, linewidth=2.5, label=str(year), alpha=0.7)
                elif len(dates) >= 2:
                    ax.plot(dates, amounts, color=year_color, linewidth=2, label=str(year))
                else:
                    ax.plot(dates, amounts, marker='o', color=year_color, linewidth=2, label=str(year))

            # Format
            ax.set_xlim(date(current_year, 1, 1), date(current_year, 12, 31))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            ax.set_title('Bills by Year (Smooth Trend)')
            ax.grid(True, alpha=0.3)
            ax.legend()

            # Apply theme
            colors = theme_manager.get_colors()
            self.bills_figure.patch.set_facecolor(colors['background'])
            ax.set_facecolor(colors['background'])
            ax.tick_params(colors=colors['text_secondary'])
            ax.title.set_color(colors['text_primary'])

            self.bills_figure.tight_layout()
            self.bills_canvas.draw()
            db.close()

        except Exception as e:
            print(f"Error updating bills plot: {e}")

    def update_savings_plot(self):
        """Update savings by year line plot with 3-day bucketing"""
        try:
            self.savings_figure.clear()
            ax = self.savings_figure.add_subplot(111)

            db = get_db()
            saving_transactions = db.query(Transaction).filter(
                Transaction.transaction_type == "saving"
            ).order_by(Transaction.date).all()

            if not saving_transactions:
                ax.text(0.5, 0.5, "No savings data available",
                       ha='center', va='center', transform=ax.transAxes)
                self.savings_canvas.draw()
                db.close()
                return

            # Group by year
            years_data = {}
            for t in saving_transactions:
                year = t.date.year
                if year not in years_data:
                    years_data[year] = []
                years_data[year].append({'date': t.date, 'amount': t.amount})

            current_year = date.today().year

            # Plot each year
            for year, transactions in sorted(years_data.items()):
                transactions.sort(key=lambda x: x['date'])

                # Bucket transactions into 3-day periods
                bucketed_data = {}
                for trans in transactions:
                    # Calculate which 3-day bucket this transaction belongs to
                    days_into_year = (trans['date'] - date(trans['date'].year, 1, 1)).days
                    bucket_num = days_into_year // 3
                    bucket_start = date(trans['date'].year, 1, 1) + timedelta(days=bucket_num * 3)

                    if bucket_start not in bucketed_data:
                        bucketed_data[bucket_start] = 0
                    bucketed_data[bucket_start] += trans['amount']

                # Convert to lists
                dates = sorted(bucketed_data.keys())
                amounts = [bucketed_data[d] for d in dates]

                # Align dates to current year for overlay
                aligned_dates = []
                for d in dates:
                    try:
                        # Handle Feb 29 in leap years
                        if d.month == 2 and d.day == 29:
                            aligned_dates.append(date(current_year, 2, 28))
                        else:
                            aligned_dates.append(date(current_year, d.month, d.day))
                    except ValueError:
                        # Skip invalid dates
                        continue

                # Adjust amounts list if dates were skipped
                if len(aligned_dates) != len(amounts):
                    amounts = amounts[:len(aligned_dates)]

                year_color = self.get_year_color(year)

                # Plot points
                ax.scatter(aligned_dates, amounts, s=30, alpha=0.7, color=year_color, edgecolor='black', linewidth=0.5)

                # Add smooth line if enough points
                if len(aligned_dates) >= 5:
                    from scipy.interpolate import make_interp_spline
                    # Convert to numeric for interpolation
                    x_numeric = np.arange(len(aligned_dates))
                    x_smooth = np.linspace(0, len(aligned_dates)-1, len(aligned_dates)*3)

                    spl = make_interp_spline(x_numeric, amounts, k=min(3, len(aligned_dates)-1))
                    y_smooth = spl(x_smooth)

                    # Create corresponding dates
                    date_indices = np.linspace(0, len(aligned_dates)-1, len(x_smooth))
                    smooth_dates_interp = [aligned_dates[int(i)] for i in date_indices]

                    ax.plot(smooth_dates_interp, y_smooth, color=year_color, linewidth=2.5, label=str(year), alpha=0.7)
                elif len(aligned_dates) >= 2:
                    ax.plot(aligned_dates, amounts, marker='o', markersize=4, color=year_color,
                           label=str(year), linewidth=2)
                else:
                    ax.plot(aligned_dates, amounts, marker='o', markersize=6, color=year_color,
                           label=str(year))

            # Format
            ax.set_xlim(date(current_year, 1, 1), date(current_year, 12, 31))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            ax.set_title('Savings by Year (3-day Buckets)')
            ax.grid(True, alpha=0.3)
            ax.legend()

            # Apply theme
            colors = theme_manager.get_colors()
            self.savings_figure.patch.set_facecolor(colors['background'])
            ax.set_facecolor(colors['background'])
            ax.tick_params(colors=colors['text_secondary'])
            ax.title.set_color(colors['text_primary'])

            self.savings_figure.tight_layout()
            self.savings_canvas.draw()
            db.close()

        except Exception as e:
            print(f"Error updating savings plot: {e}")

    def refresh(self):
        """Refresh all data and visualizations"""
        try:
            # Clear existing year boxes
            while self.left_layout.count():
                child = self.left_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            self.year_boxes = []

            # Get all years with transaction data
            db = get_db()
            years_with_data = db.query(Transaction.date).all()

            if not years_with_data:
                # No data - show placeholder
                placeholder = QLabel("No financial data available yet")
                placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
                placeholder.setFont(theme_manager.get_font("subtitle"))
                self.left_layout.addWidget(placeholder)
                db.close()
                return

            # Extract unique years
            unique_years = sorted(set(d[0].year for d in years_with_data if d[0]), reverse=True)

            if unique_years:
                self.first_year = min(unique_years)

            db.close()

            # Create year boxes (newest first)
            prev_year_data = None
            for i, year in enumerate(unique_years):
                year_data = self.get_year_data(year)

                # For year-over-year comparison, use previous year in chronological order
                # Since we're iterating newest to oldest, we need to look forward in the list
                if i < len(unique_years) - 1:
                    # Get the previous year's data (chronologically)
                    prev_year = unique_years[i + 1]
                    prev_year_data = self.get_year_data(prev_year)
                else:
                    prev_year_data = None

                year_box = self.create_year_box(year_data, prev_year_data)
                self.left_layout.addWidget(year_box)
                self.year_boxes.append(year_box)

            # Update all right panel visualizations
            self.update_yoy_growth_bars()
            self.update_master_pie_chart()
            self.update_violin_plots()
            self.update_correlation_plots()
            self.update_line_plots()

        except Exception as e:
            print(f"Error refreshing Year Overview: {e}")

    def toggle_analytics_mode(self, checked):
        """Toggle between normal and all spending analytics (only affects right panel visualizations)"""
        self.include_analytics_only = checked
        # Refresh only the right panel charts (not year boxes)
        self.update_yoy_growth_bars()
        self.update_master_pie_chart()
        self.update_violin_plots()
        self.update_spending_plot()

    def apply_theme(self):
        """Apply current theme to all elements"""
        try:
            colors = theme_manager.get_colors()

            # Apply theme to main widget
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {colors['background']};
                    color: {colors['text_primary']};
                }}
                QLabel {{
                    color: {colors['text_primary']};
                }}
                QScrollArea {{
                    border: 1px solid {colors['border']};
                    background-color: {colors['surface']};
                }}
            """)

            # Style refresh button (QToolButton) - matching dashboard
            if hasattr(self, 'refresh_button'):
                self.refresh_button.setStyleSheet(f"""
                    QToolButton {{
                        background-color: {colors['primary']};
                        color: {colors['text_primary']};
                        border: 1px solid {colors['border']};
                        border-radius: 4px;
                        padding: 4px;
                        font-size: 16px;
                    }}
                    QToolButton:hover {{
                        background-color: {colors['primary_dark']};
                        border-color: {colors['primary']};
                    }}
                    QToolButton:pressed {{
                        background-color: {colors['selected']};
                    }}
                """)

            # Style analytics toggle checkbox - matching dashboard
            if hasattr(self, 'analytics_toggle'):
                self.analytics_toggle.setStyleSheet(f"""
                    QCheckBox {{
                        color: {colors['text_primary']};
                        spacing: 8px;
                        font-weight: normal;
                    }}
                    QCheckBox::indicator {{
                        width: 18px;
                        height: 18px;
                        border: 2px solid {colors['border']};
                        border-radius: 3px;
                        background-color: {colors['surface']};
                    }}
                    QCheckBox::indicator:hover {{
                        border: 2px solid {colors['primary']};
                    }}
                    QCheckBox::indicator:checked {{
                        background-color: {colors['primary']};
                        border-color: {colors['primary']};
                    }}
                """)

        except Exception as e:
            print(f"Error applying theme to Year Overview: {e}")

    def on_theme_changed(self, theme_id):
        """Handle theme changes"""
        self.apply_theme()
        # Refresh all charts with new theme colors
        self.refresh()
