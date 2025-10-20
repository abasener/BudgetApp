"""
Year Overview View - Year-over-year analysis of spending, income, savings, and bills
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGroupBox, QScrollArea, QFrame, QToolButton, QCheckBox)
from PyQt6.QtCore import Qt
from datetime import datetime, date
from themes import theme_manager
from models import get_db, Transaction
from views.dialogs.settings_dialog import get_setting

# Matplotlib imports for plotting
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


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
        main_layout.addWidget(left_panel, stretch=1)

        # Right panel - Data visualizations
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, stretch=2)

        self.setLayout(main_layout)

    def create_left_panel(self):
        """Create left panel with year-by-year detail boxes"""
        # Scroll area for year boxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

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
        layout = QVBoxLayout()
        layout.setSpacing(10)

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

        layout.addLayout(header)

        # Placeholder for charts
        placeholder = QLabel("Year-over-year visualizations will appear here")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setFont(theme_manager.get_font("subtitle"))
        layout.addWidget(placeholder)

        panel.setLayout(layout)
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

        except Exception as e:
            print(f"Error refreshing Year Overview: {e}")

    def toggle_analytics_mode(self, checked):
        """Toggle between normal and all spending analytics (only affects right panel visualizations)"""
        self.include_analytics_only = checked
        # TODO: Refresh right panel charts when implemented
        # For now, just store the setting for future use

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
        # TODO: Refresh charts with new theme colors
