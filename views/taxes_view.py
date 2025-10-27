"""
Taxes View - Tax tracking and management interface with yearly history
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGroupBox, QScrollArea, QFrame, QProgressBar, QToolButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor
from datetime import datetime, date
from themes import theme_manager
from models import get_db, Bill, Transaction

# Matplotlib imports for plotting
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Optional import for hover tooltips
try:
    import mplcursors
    MPLCURSORS_AVAILABLE = True
except ImportError:
    MPLCURSORS_AVAILABLE = False


class DualProgressBar(QProgressBar):
    """Custom progress bar that shows two values - background and foreground"""
    def __init__(self):
        super().__init__()
        self.background_value = 0
        self.setTextVisible(False)  # Don't show text on the bar

    def set_background_value(self, value):
        """Set the background progress value (0-100)"""
        self.background_value = min(100, max(0, value))
        self.update()

    def paintEvent(self, event):
        """Custom paint to show both background and foreground values"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get colors from theme
        try:
            colors = theme_manager.get_colors()
            bg_color = QColor(colors['surface'])
            border_color = QColor(colors['border'])
            secondary_color = QColor(colors['secondary'])
        except:
            bg_color = QColor('#f0f0f0')
            border_color = QColor('#cccccc')
            secondary_color = QColor('#4CAF50')

        # Draw background
        painter.fillRect(self.rect(), bg_color)

        # Draw border
        painter.setPen(border_color)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

        # Calculate widths
        width = self.width() - 2
        height = self.height() - 2

        # Draw background progress (lighter/shaded)
        if self.background_value > 0:
            bg_width = int(width * (self.background_value / 100.0))
            bg_rect = self.rect().adjusted(1, 1, -width + bg_width - 1, -1)

            # Use semi-transparent secondary color
            bg_progress_color = QColor(secondary_color)
            bg_progress_color.setAlpha(64)  # 25% opacity
            painter.fillRect(bg_rect, bg_progress_color)

        # Draw foreground progress (full color)
        if self.value() > 0:
            fg_width = int(width * (self.value() / 100.0))
            fg_rect = self.rect().adjusted(1, 1, -width + fg_width - 1, -1)
            painter.fillRect(fg_rect, secondary_color)

        # Don't draw text - it will be in the label instead


class TaxesView(QWidget):
    """View for tax tracking and management features"""

    def __init__(self, transaction_manager, analytics_engine=None):
        super().__init__()
        self.transaction_manager = transaction_manager
        self.analytics_engine = analytics_engine
        self.year_boxes = []  # Store references to year boxes for refresh
        self.first_year = None  # Will be set to earliest year with data

        self.init_ui()
        self.refresh()
        self.apply_theme()

        # Connect to theme changes
        theme_manager.theme_changed.connect(self.apply_theme)
        theme_manager.theme_changed.connect(self.refresh_plots)

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

    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)

        # Left column - History (25% width)
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setMaximumWidth(400)  # Limit width
        self.history_scroll.setMinimumWidth(250)

        self.history_widget = QWidget()
        self.history_layout = QVBoxLayout()
        self.history_layout.setSpacing(10)

        # History header
        history_header = QLabel("Tax History")
        history_header.setFont(theme_manager.get_font("title"))
        history_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.history_layout.addWidget(history_header)

        # Year boxes will be added dynamically
        self.history_layout.addStretch()
        self.history_widget.setLayout(self.history_layout)
        self.history_scroll.setWidget(self.history_widget)

        # Right side - Main content (75% width)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)

        # Create content group box for tax features (invisible, just for compatibility)
        self.content_group = QGroupBox()
        self.content_group.setStyleSheet("QGroupBox { border: none; background: transparent; }")

        # Create info label for displaying setup instructions or status
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.info_label.setVisible(False)  # Hide since we're not using it
        right_layout.addWidget(self.info_label)

        # Tax summary header row (moved to top)
        self.create_tax_summary_row(right_layout)

        # Progress bars section (moved below summary)
        self.create_progress_bars(right_layout)

        # Income plot area
        self.create_income_plot(right_layout)

        # Tax payments bar chart area
        self.create_tax_payments_chart(right_layout)

        # Table and pie chart section
        self.create_summary_section(right_layout)

        right_layout.addStretch()

        # Add to main layout with size ratios
        main_layout.addWidget(self.history_scroll, 1)  # 25%
        main_layout.addLayout(right_layout, 3)  # 75%

        self.setLayout(main_layout)

    def create_progress_bars(self, parent_layout):
        """Create progress bars for year progress and tax savings health"""
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.Shape.Box)
        progress_frame.setMaximumHeight(120)  # Height for two bars

        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(10)

        # Year progress bar (top)
        year_bar_layout = QHBoxLayout()
        self.year_label = QLabel("Year:")
        self.year_label.setFont(theme_manager.get_font("small"))
        self.year_label.setFixedWidth(80)

        self.year_progress_bar = QProgressBar()
        self.year_progress_bar.setMaximum(100)
        self.year_progress_bar.setTextVisible(False)

        year_bar_layout.addWidget(self.year_label)
        year_bar_layout.addWidget(self.year_progress_bar)
        progress_layout.addLayout(year_bar_layout)

        # Tax savings health progress bar (bottom) - with dual layers
        savings_bar_layout = QHBoxLayout()
        self.savings_label = QLabel("Saved:")
        self.savings_label.setFont(theme_manager.get_font("small"))
        self.savings_label.setFixedWidth(80)

        # Use our custom dual progress bar
        self.tax_savings_progress_bar = DualProgressBar()
        self.tax_savings_progress_bar.setMaximum(100)

        savings_bar_layout.addWidget(self.savings_label)
        savings_bar_layout.addWidget(self.tax_savings_progress_bar)
        progress_layout.addLayout(savings_bar_layout)

        progress_frame.setLayout(progress_layout)
        parent_layout.addWidget(progress_frame)

    def create_tax_summary_row(self, parent_layout):
        """Create tax summary row with key numerical values"""
        # Create a frame for the summary to span full width
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.Shape.NoFrame)

        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(50)  # Space between items

        # Expected Tax (left)
        self.expected_tax_label = QLabel()
        # Make font slightly bigger than header
        font = theme_manager.get_font("header")
        font.setPointSize(font.pointSize() + 2)
        self.expected_tax_label.setFont(font)
        summary_layout.addWidget(self.expected_tax_label)

        # Expected Percent
        self.expected_percent_label = QLabel()
        self.expected_percent_label.setFont(font)
        summary_layout.addWidget(self.expected_percent_label)

        # Current Saved (total balance in tax account)
        self.current_saved_label = QLabel()
        self.current_saved_label.setFont(font)
        summary_layout.addWidget(self.current_saved_label)

        # Current Year Saved (saved in current year only)
        self.year_saved_label = QLabel()
        self.year_saved_label.setFont(font)
        summary_layout.addWidget(self.year_saved_label)

        summary_layout.addStretch()  # Push items left

        # Refresh button - compact tool button with just emoji (rightmost position)
        self.refresh_button = QToolButton()
        self.refresh_button.setText("🔄")
        self.refresh_button.setToolTip("Refresh Taxes")
        self.refresh_button.setFixedSize(40, 30)
        self.refresh_button.clicked.connect(self.refresh)
        # Styling applied in apply_header_theme method
        summary_layout.addWidget(self.refresh_button)

        summary_frame.setLayout(summary_layout)
        parent_layout.addWidget(summary_frame)

        # Apply initial theme to refresh button
        self.apply_header_theme()

    def create_income_plot(self, parent_layout):
        """Create the income line plot area"""
        # Create matplotlib figure and canvas with 1:5 height:width ratio
        self.income_figure = Figure(figsize=(12, 2.4))  # Width 12, height 2.4 for 1:5 ratio
        self.income_canvas = FigureCanvas(self.income_figure)
        self.income_canvas.setMinimumHeight(180)
        self.income_canvas.setMaximumHeight(220)
        parent_layout.addWidget(self.income_canvas)

    def create_tax_payments_chart(self, parent_layout):
        """Create the tax payments bar chart area"""
        # Create matplotlib figure and canvas with same ratio as income plot
        self.tax_payments_figure = Figure(figsize=(12, 2.4))  # Same 1:5 ratio
        self.tax_payments_canvas = FigureCanvas(self.tax_payments_figure)
        self.tax_payments_canvas.setMinimumHeight(180)
        self.tax_payments_canvas.setMaximumHeight(220)
        parent_layout.addWidget(self.tax_payments_canvas)

    def create_summary_section(self, parent_layout):
        """Create the table and pie chart section"""
        from PyQt6.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem

        # Horizontal layout for table (2/3) and pie chart (1/3)
        summary_layout = QHBoxLayout()

        # Table widget
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(8)
        self.summary_table.setHorizontalHeaderLabels([
            "Year", "Income", "Saved", "Federal", "State", "Service", "Other", "Remaining"
        ])
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.summary_table.setMaximumHeight(300)
        summary_layout.addWidget(self.summary_table, 2)  # 2/3 width

        # Pie chart
        self.pie_figure = Figure(figsize=(4, 4))
        self.pie_canvas = FigureCanvas(self.pie_figure)
        self.pie_canvas.setMaximumHeight(300)
        summary_layout.addWidget(self.pie_canvas, 1)  # 1/3 width

        parent_layout.addLayout(summary_layout)

    def calculate_expected_yearly_income(self):
        """Calculate expected yearly income based on past years average"""
        try:
            db = get_db()
            current_year = datetime.now().year

            # Get past years income data (not current year)
            past_years_data = []
            for year in range(current_year - 5, current_year):
                # Get income transactions for this year
                year_start = date(year, 1, 1)
                year_end = date(year, 12, 31)

                income_transactions = db.query(Transaction).filter(
                    Transaction.date >= year_start,
                    Transaction.date <= year_end,
                    Transaction.transaction_type == "income"
                ).all()

                if income_transactions:
                    # Calculate average income per paycheck
                    total_income = sum(t.amount for t in income_transactions)
                    num_paychecks = len(income_transactions)
                    avg_paycheck = total_income / num_paychecks if num_paychecks > 0 else 0

                    past_years_data.append({
                        'avg_paycheck': avg_paycheck,
                        'num_paychecks': num_paychecks
                    })

            db.close()

            if not past_years_data:
                return 0

            # Calculate average of averages as described
            avg_paycheck = sum(d['avg_paycheck'] for d in past_years_data) / len(past_years_data)
            avg_paychecks_per_year = sum(d['num_paychecks'] for d in past_years_data) / len(past_years_data)

            expected_yearly_income = avg_paycheck * avg_paychecks_per_year
            return expected_yearly_income

        except Exception as e:
            print(f"Error calculating expected yearly income: {e}")
            return 0

    def update_tax_summary(self):
        """Update the tax summary row with current data"""
        if not hasattr(self, 'expected_tax_label'):
            return

        # Get expected tax (only historical data, no fallback)
        expected_tax = self.get_historical_average_spending()

        if expected_tax > 0:
            self.expected_tax_label.setText(f"Expected Tax: ${expected_tax:,.0f}")

            # Calculate and show expected percent (average of yearly percentages)
            expected_percent = self.get_historical_average_percentage()
            if expected_percent > 0:
                self.expected_percent_label.setText(f"Expected Percent: {expected_percent:.1f}%")
            else:
                self.expected_percent_label.setText("Expected Percent: NA")
        else:
            self.expected_tax_label.setText("Expected Tax: No Data")
            self.expected_percent_label.setText("Expected Percent: NA")

        # Current Saved (total balance including rollover)
        current_saved = self.get_tax_account_total_balance()
        self.current_saved_label.setText(f"Current Saved: ${current_saved:,.0f}")

        # Current Year Saved (savings in current year only)
        current_year = datetime.now().year
        year_data = self.get_year_data(current_year)
        year_saved = year_data['total_savings']
        self.year_saved_label.setText(f"{current_year} Saved: ${year_saved:,.0f}")

    def get_historical_average_spending(self):
        """Get historical average spending without fallback calculation"""
        try:
            db = get_db()
            current_year = datetime.now().year

            # Find the Taxes bill
            tax_bill = db.query(Bill).filter(Bill.name == "Taxes").first()
            if not tax_bill:
                db.close()
                return 0

            # Get all years before current year that have spending data
            past_years_spending = []

            # Check years going back up to 5 years
            for year in range(current_year - 5, current_year):
                next_year_start = date(year + 1, 1, 1)
                next_year_end = date(year + 1, 12, 31)

                # Get bill_pay transactions in year+1 for taxes saved in 'year'
                spending_transactions = db.query(Transaction).filter(
                    Transaction.date >= next_year_start,
                    Transaction.date <= next_year_end,
                    Transaction.transaction_type == "bill_pay",
                    Transaction.bill_id == tax_bill.id
                ).all()

                # Filter to only tax payments (federal, state, service) - exclude rebalancing
                tax_keywords = ['federal', 'state', 'service']
                tax_payment_transactions = [
                    t for t in spending_transactions
                    if t.description and any(keyword in t.description.lower() for keyword in tax_keywords)
                ]

                year_spending = sum(t.amount for t in tax_payment_transactions)
                if year_spending > 0:
                    past_years_spending.append(year_spending)

            db.close()

            # Calculate average from historical data only (no fallback)
            if past_years_spending:
                return sum(past_years_spending) / len(past_years_spending)
            else:
                return 0

        except Exception as e:
            print(f"Error calculating historical average: {e}")
            return 0

    def get_historical_average_percentage(self):
        """Get historical average tax percentage (spending/income ratio averaged across years)"""
        try:
            db = get_db()
            current_year = datetime.now().year

            # Find the Taxes bill
            tax_bill = db.query(Bill).filter(Bill.name == "Taxes").first()
            if not tax_bill:
                db.close()
                return 0

            # Get percentages for each year with spending data
            yearly_percentages = []

            # Check years going back up to 5 years
            for year in range(current_year - 5, current_year):
                # Get year data which includes income and spending
                year_data = self.get_year_data(year)

                # Only include years where we have both income and spending
                if year_data['total_income'] > 0 and year_data['total_spending'] and year_data['total_spending'] > 0:
                    percentage = (year_data['total_spending'] / year_data['total_income']) * 100
                    yearly_percentages.append(percentage)

            db.close()

            # Calculate average percentage
            if yearly_percentages:
                return sum(yearly_percentages) / len(yearly_percentages)
            else:
                return 0

        except Exception as e:
            print(f"Error calculating historical average percentage: {e}")
            return 0

    def calculate_year_progress(self):
        """Calculate percentage of year completed (Jan 1 to Dec 31)"""
        now = datetime.now()
        year_start = datetime(now.year, 1, 1)
        year_end = datetime(now.year, 12, 31, 23, 59, 59)

        total_seconds = (year_end - year_start).total_seconds()
        elapsed_seconds = (now - year_start).total_seconds()

        return (elapsed_seconds / total_seconds) * 100

    def calculate_average_past_spending(self):
        """Calculate average spending from past years for current year tax estimation"""
        try:
            db = get_db()
            current_year = datetime.now().year

            # Find the Taxes bill
            tax_bill = db.query(Bill).filter(Bill.name == "Taxes").first()
            if not tax_bill:
                db.close()
                return 0

            # Get all years before current year that have spending data
            past_years_spending = []

            # Check years going back up to 5 years
            for year in range(current_year - 5, current_year):
                next_year_start = date(year + 1, 1, 1)
                next_year_end = date(year + 1, 12, 31)

                # Get bill_pay transactions in year+1 for taxes saved in 'year'
                spending_transactions = db.query(Transaction).filter(
                    Transaction.date >= next_year_start,
                    Transaction.date <= next_year_end,
                    Transaction.transaction_type == "bill_pay",
                    Transaction.bill_id == tax_bill.id
                ).all()

                # Filter to only tax payments (federal, state, service) - exclude rebalancing
                tax_keywords = ['federal', 'state', 'service']
                tax_payment_transactions = [
                    t for t in spending_transactions
                    if t.description and any(keyword in t.description.lower() for keyword in tax_keywords)
                ]

                year_spending = sum(t.amount for t in tax_payment_transactions)
                if year_spending > 0:
                    past_years_spending.append(year_spending)

            # Calculate average from historical data
            if past_years_spending:
                avg_spending = sum(past_years_spending) / len(past_years_spending)
                db.close()
                return avg_spending
            else:
                # FALLBACK: Use 33% of current year's average paycheck * number of pay periods
                current_year_data = self.get_year_data(current_year)
                avg_paycheck = current_year_data['avg_income']

                if avg_paycheck > 0:
                    # Calculate number of pay periods per year (total weeks / 2 for bi-weekly)
                    weeks_per_year = 52
                    pay_periods_per_year = weeks_per_year / 2  # 26 pay periods

                    # 33% of annual income (avg_paycheck * pay_periods * 0.33)
                    fallback_estimate = avg_paycheck * pay_periods_per_year * 0.33
                    db.close()
                    return fallback_estimate
                else:
                    db.close()
                    return 0

        except Exception as e:
            print(f"Error calculating past spending: {e}")
            return 0

    def calculate_tax_savings_health(self):
        """Calculate tax savings health as percentage of expected spending"""
        current_year = datetime.now().year

        # Get current year tax savings data
        year_data = self.get_year_data(current_year)
        current_savings = year_data['total_savings']

        # Get average expected spending
        avg_expected_spending = self.calculate_average_past_spending()

        if avg_expected_spending > 0:
            # Calculate percentage: how much we've saved vs expected spending
            health_percentage = (current_savings / avg_expected_spending) * 100
            return min(100, health_percentage)  # Cap at 100%
        else:
            return 0

    def get_tax_account_total_balance(self):
        """Get the total balance in the Taxes account including all rollover"""
        try:
            db = get_db()

            # Find the Taxes bill
            tax_bill = db.query(Bill).filter(Bill.name == "Taxes").first()
            if not tax_bill:
                db.close()
                return 0

            # Get ALL transactions for the tax bill (all time) - sum of all positive and negative
            all_tax_transactions = db.query(Transaction).filter(
                Transaction.transaction_type == "saving",
                Transaction.bill_id == tax_bill.id
            ).all()

            # Simple sum of all transactions (positive deposits, negative withdrawals)
            current_balance = sum(t.amount for t in all_tax_transactions)

            db.close()
            return max(0, current_balance)  # Don't return negative

        except Exception as e:
            print(f"Error getting tax account balance: {e}")
            return 0

    def calculate_total_balance_percentage(self):
        """Calculate total balance as percentage of expected spending"""
        total_balance = self.get_tax_account_total_balance()
        avg_expected_spending = self.calculate_average_past_spending()

        if avg_expected_spending > 0:
            balance_percentage = (total_balance / avg_expected_spending) * 100
            return min(100, balance_percentage)  # Cap at 100%
        else:
            return 0

    def update_progress_bars(self):
        """Update both progress bars with current data"""
        if not hasattr(self, 'year_progress_bar'):
            return

        # Update year progress
        year_percentage = self.calculate_year_progress()
        self.year_progress_bar.setValue(int(year_percentage))
        self.year_label.setText(f"{year_percentage:.1f}% Year")

        # Update tax savings health - current year only
        savings_health = self.calculate_tax_savings_health()
        avg_expected = self.calculate_average_past_spending()

        # Update total balance background value (with rollover)
        total_balance_percentage = self.calculate_total_balance_percentage()
        self.tax_savings_progress_bar.set_background_value(int(total_balance_percentage))

        # Update current year foreground value
        self.tax_savings_progress_bar.setValue(int(savings_health))

        # Update the label with percentage
        self.savings_label.setText(f"{savings_health:.0f}% Saved")

    def has_historical_spending_data(self):
        """Check if we have any historical spending data"""
        try:
            db = get_db()
            current_year = datetime.now().year

            # Check years going back up to 5 years for any spending data
            for year in range(current_year - 5, current_year):
                next_year_start = date(year + 1, 1, 1)
                next_year_end = date(year + 1, 12, 31)

                spending_count = db.query(Transaction).filter(
                    Transaction.date >= next_year_start,
                    Transaction.date <= next_year_end,
                    Transaction.transaction_type == "spending",
                    Transaction.include_in_analytics == True,
                    Transaction.amount < 0
                ).count()

                if spending_count > 0:
                    db.close()
                    return True

            db.close()
            return False

        except Exception as e:
            print(f"Error checking historical data: {e}")
            return False

    def check_tax_bill_exists(self):
        """Check if a bill named 'Taxes' exists"""
        try:
            db = get_db()
            tax_bill = db.query(Bill).filter(Bill.name == "Taxes").first()
            db.close()
            return tax_bill is not None
        except Exception as e:
            print(f"Error checking for Taxes bill: {e}")
            return False

    def get_year_data(self, year):
        """Calculate tax data for a specific year"""
        try:
            db = get_db()

            year_start = date(year, 1, 1)
            year_end = date(year, 12, 31)

            # Get income transactions directly by date (not by weeks)
            income_transactions = db.query(Transaction).filter(
                Transaction.date >= year_start,
                Transaction.date <= year_end,
                Transaction.transaction_type == "income"
            ).all()

            # Calculate total income from paychecks
            total_income = 0
            paycheck_count = len(income_transactions)

            for transaction in income_transactions:
                total_income += transaction.amount

            avg_income = total_income / paycheck_count if paycheck_count > 0 else 0

            # Get ONLY Taxes bill saving transactions in this year (only positive amounts)
            # Find the Taxes bill first
            tax_bill = db.query(Bill).filter(Bill.name == "Taxes").first()

            if tax_bill:
                tax_saving_transactions = db.query(Transaction).filter(
                    Transaction.date >= year_start,
                    Transaction.date <= year_end,
                    Transaction.transaction_type == "saving",
                    Transaction.bill_id == tax_bill.id,
                    Transaction.amount > 0  # Only positive deposits
                ).all()

                total_savings = sum(t.amount for t in tax_saving_transactions)
            else:
                total_savings = 0

            # Get bill_pay transactions in year+1 (tax payments from Taxes bill account)
            next_year_start = date(year + 1, 1, 1)
            next_year_end = date(year + 1, 12, 31)

            if tax_bill:
                spending_transactions = db.query(Transaction).filter(
                    Transaction.date >= next_year_start,
                    Transaction.date <= next_year_end,
                    Transaction.transaction_type == "bill_pay",
                    Transaction.bill_id == tax_bill.id
                ).all()

                # Filter to only tax payments (federal, state, service) - exclude rebalancing
                tax_keywords = ['federal', 'state', 'service']
                tax_payment_transactions = [
                    t for t in spending_transactions
                    if t.description and any(keyword in t.description.lower() for keyword in tax_keywords)
                ]

                total_spending = sum(t.amount for t in tax_payment_transactions) if tax_payment_transactions else None
            else:
                spending_transactions = []
                total_spending = None

            # Calculate average saved amount per paycheck
            avg_saved_amount = total_savings / paycheck_count if paycheck_count > 0 else 0

            # Calculate average savings percentage
            avg_savings_percent = (total_savings / total_income * 100) if total_income > 0 else 0

            # Calculate remaining amount
            remaining_amount = None
            if total_spending is not None and total_spending > 0:
                remaining_amount = total_savings - total_spending

            db.close()

            return {
                'year': year,
                'avg_income': avg_income,
                'total_income': total_income,
                'total_savings': total_savings,
                'total_spending': total_spending,
                'avg_savings_percent': avg_savings_percent,
                'avg_saved_amount': avg_saved_amount,
                'paycheck_count': paycheck_count,
                'remaining_amount': remaining_amount
            }

        except Exception as e:
            print(f"Error calculating year data for {year}: {e}")
            return {
                'year': year,
                'avg_income': 0,
                'total_income': 0,
                'total_savings': 0,
                'total_spending': None,
                'avg_savings_percent': 0,
                'avg_saved_amount': 0,
                'paycheck_count': 0,
                'remaining_amount': None
            }

    def create_year_box(self, year_data):
        """Create a box widget for a year's tax data"""
        year = year_data['year']
        year_box = QGroupBox(str(year))

        # Apply year color and larger font to the title
        year_color = self.get_year_color(year)
        if year_color:
            # Get base font and multiply size by 1.5
            title_font = theme_manager.get_font("header")
            base_size = title_font.pointSize()
            new_size = int(base_size * 1.5)

            # Set font on the year_box widget
            year_box.setFont(title_font)
            title_font.setPointSize(new_size)
            title_font.setBold(True)
            year_box.setFont(title_font)

            # Apply color via stylesheet
            year_box.setStyleSheet(f"QGroupBox {{ font-size: {new_size}pt; }} QGroupBox::title {{ color: {year_color}; font-weight: bold; }}")

        year_layout = QVBoxLayout()
        year_layout.setSpacing(5)

        # Show data if we have any transactions OR income
        has_data = (year_data['paycheck_count'] > 0 or
                   year_data['total_spending'] is not None or
                   year_data['total_savings'] > 0)

        if has_data:
            # Row 1: Average Income
            if year_data['paycheck_count'] > 0:
                avg_income_label = QLabel(f"Avg Income: ${year_data['avg_income']:,.2f}")
                avg_income_label.setFont(theme_manager.get_font("body_small"))
                year_layout.addWidget(avg_income_label)
            else:
                no_income_label = QLabel("Avg Income: $0.00")
                no_income_label.setFont(theme_manager.get_font("body_small"))
                year_layout.addWidget(no_income_label)

            # Row 2: Average Saved Amount (per paycheck)
            if year_data['paycheck_count'] > 0:
                avg_saved_label = QLabel(f"Avg Saved: ${year_data['avg_saved_amount']:,.2f}")
                avg_saved_label.setFont(theme_manager.get_font("body_small"))
                year_layout.addWidget(avg_saved_label)
            else:
                avg_saved_label = QLabel("Avg Saved: $0.00")
                avg_saved_label.setFont(theme_manager.get_font("body_small"))
                year_layout.addWidget(avg_saved_label)

            # Row 3: Saved (percentage, only positive deposits)
            if year_data['total_income'] > 0:
                savings_label = QLabel(f"Saved: {year_data['avg_savings_percent']:.1f}%")
                savings_label.setFont(theme_manager.get_font("body_small"))
                year_layout.addWidget(savings_label)
            else:
                savings_label = QLabel("Saved: 0.0%")
                savings_label.setFont(theme_manager.get_font("body_small"))
                year_layout.addWidget(savings_label)

            # Row 4: Spent (from year+1, only negative amounts)
            if year_data['total_spending'] is not None:
                spending_label = QLabel(f"Spent: ${year_data['total_spending']:,.2f}")
                spending_label.setFont(theme_manager.get_font("body_small"))
                year_layout.addWidget(spending_label)
            else:
                spending_label = QLabel("Spent: NA")
                spending_label.setFont(theme_manager.get_font("body_small"))
                year_layout.addWidget(spending_label)

            # Row 5: Remaining (saved - spent)
            if year_data['remaining_amount'] is not None:
                remaining_label = QLabel(f"Remaining: ${year_data['remaining_amount']:,.2f}")
                remaining_label.setFont(theme_manager.get_font("body_small"))
                year_layout.addWidget(remaining_label)
            else:
                remaining_label = QLabel("Remaining: NA")
                remaining_label.setFont(theme_manager.get_font("body_small"))
                year_layout.addWidget(remaining_label)
        else:
            no_data_label = QLabel("No data for this year")
            no_data_label.setFont(theme_manager.get_font("body_small"))
            no_data_label.setStyleSheet("color: gray;")
            year_layout.addWidget(no_data_label)

        year_box.setLayout(year_layout)
        return year_box

    def generate_income_plot(self):
        """Generate the income line plot for multiple years"""
        try:
            # Clear the figure
            self.income_figure.clear()
            ax = self.income_figure.add_subplot(111)

            db = get_db()

            # Get all years with income data
            income_transactions = db.query(Transaction).filter(
                Transaction.transaction_type == "income"
            ).order_by(Transaction.date).all()

            if not income_transactions:
                # Show empty plot with message
                ax.text(0.5, 0.5, "No income data available",
                       horizontalalignment='center',
                       verticalalignment='center',
                       transform=ax.transAxes,
                       fontsize=14)
                ax.set_xticks([])
                ax.set_yticks([])
                self.income_canvas.draw()
                db.close()
                return

            # Group transactions by year and accumulate income
            years_data = {}
            for transaction in income_transactions:
                year = transaction.date.year
                if year not in years_data:
                    years_data[year] = []
                years_data[year].append({
                    'date': transaction.date,
                    'amount': transaction.amount
                })

            max_income = 0
            min_income = float('inf')
            current_year = date.today().year

            for i, (year, transactions) in enumerate(sorted(years_data.items())):
                # Sort transactions by date
                transactions.sort(key=lambda x: x['date'])

                # Extract dates and income amounts
                dates = []
                income_amounts = []

                for trans in transactions:
                    # Convert date to use current year for x-axis alignment
                    aligned_date = trans['date'].replace(year=current_year)
                    dates.append(aligned_date)
                    income_amounts.append(trans['amount'])
                    max_income = max(max_income, trans['amount'])
                    min_income = min(min_income, trans['amount'])

                # Get year-specific color from chart_colors
                line_color = self.get_year_color(year)
                if not line_color:
                    # Fallback if color system not ready
                    line_color = '#1f77b4'

                # Plot the line for this year
                if dates and income_amounts:
                    ax.plot(dates, income_amounts,
                           marker='o', markersize=4,
                           color=line_color,
                           label=str(year),
                           linewidth=2)

            # Set x-axis to show months from Jan to Dec
            ax.set_xlim(date(current_year, 1, 1), date(current_year, 12, 31))

            # Format x-axis to show month names
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

            # Set y-axis range (minimum is 1000 less than smallest income)
            if min_income != float('inf') and max_income > 0:
                y_min = max(0, min_income - 1000)  # Don't go below 0
                y_max = max_income * 1.1
                ax.set_ylim(y_min, y_max)

            # Format y-axis to show dollar amounts
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

            # Remove labels, only keep title
            ax.set_xlabel('')
            ax.set_ylabel('')
            ax.set_title('Income by Year')

            # Add grid
            ax.grid(True, alpha=0.3)

            # No legend needed

            # Apply theme colors if available
            try:
                colors = theme_manager.get_colors()
                self.income_figure.patch.set_facecolor(colors['background'])
                ax.set_facecolor(colors['background'])
                ax.spines['bottom'].set_color(colors['text_secondary'])
                ax.spines['left'].set_color(colors['text_secondary'])
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.tick_params(colors=colors['text_secondary'])
                ax.xaxis.label.set_color(colors['text_primary'])
                ax.yaxis.label.set_color(colors['text_primary'])
                ax.title.set_color(colors['text_primary'])
            except:
                pass  # Use default colors if theme not available

            # Refresh the canvas with more padding to prevent cutoff
            self.income_figure.tight_layout(pad=1.75)  # Increase padding
            self.income_canvas.draw()

            db.close()

        except Exception as e:
            print(f"Error generating income plot: {e}")
            # Show error in the plot area
            self.income_figure.clear()
            ax = self.income_figure.add_subplot(111)
            ax.text(0.5, 0.5, f"Error: {str(e)}",
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
            self.income_canvas.draw()

    def get_tax_spending_data(self):
        """Get all tax-related bill_pay transactions grouped by payment type and year"""
        try:
            db = get_db()

            # Find the Taxes bill
            tax_bill = db.query(Bill).filter(Bill.name == "Taxes").first()
            if not tax_bill:
                db.close()
                return {}

            # Get all bill_pay transactions from Taxes bill
            bill_pay_transactions = db.query(Transaction).filter(
                Transaction.transaction_type == "bill_pay",
                Transaction.bill_id == tax_bill.id
            ).all()

            db.close()

            # Categorize by payment type (federal, state, service, other)
            tax_keywords = {
                'Federal': 'federal',
                'State': 'state',
                'Service': 'service'
            }

            # Structure: {payment_type: {year: amount}}
            tax_data = {
                'Federal': {},
                'State': {},
                'Service': {},
                'Other': {}
            }

            for transaction in bill_pay_transactions:
                year = transaction.date.year
                desc_lower = (transaction.description or '').lower()

                # Categorize transaction
                payment_type = 'Other'  # Default
                for type_name, keyword in tax_keywords.items():
                    if keyword in desc_lower:
                        payment_type = type_name
                        break

                # Add amount to the category and year
                if year not in tax_data[payment_type]:
                    tax_data[payment_type][year] = 0

                tax_data[payment_type][year] += transaction.amount

            # Remove empty categories
            tax_data = {k: v for k, v in tax_data.items() if v}

            return tax_data

        except Exception as e:
            print(f"Error fetching tax spending data: {e}")
            return {}

    def generate_tax_payments_chart(self):
        """Generate the tax payments bar chart with grouped bars by year"""
        try:
            # Clear the figure
            self.tax_payments_figure.clear()
            ax = self.tax_payments_figure.add_subplot(111)

            # Get real tax spending data from database
            tax_data = self.get_tax_spending_data()

            # Set up the empty plot regardless of data availability
            ax.set_xticks([])
            ax.set_xlabel('')
            ax.set_ylabel('')
            ax.set_title('Tax Payments by Year')

            # Format y-axis to show dollar amounts
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

            # Add grid
            ax.grid(True, alpha=0.3, axis='y')

            # Apply theme colors
            try:
                colors = theme_manager.get_colors()
                self.tax_payments_figure.patch.set_facecolor(colors['background'])
                ax.set_facecolor(colors['background'])
                ax.spines['bottom'].set_color(colors['text_secondary'])
                ax.spines['left'].set_color(colors['text_secondary'])
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.tick_params(colors=colors['text_secondary'])
                ax.xaxis.label.set_color(colors['text_primary'])
                ax.yaxis.label.set_color(colors['text_primary'])
                ax.title.set_color(colors['text_primary'])
            except:
                pass  # Use default colors if theme not available

            if not tax_data:
                # Just show empty plot with no bars
                self.tax_payments_figure.tight_layout(pad=1.75)
                self.tax_payments_canvas.draw()
                return

            # Get all unique years across all payment types
            all_years = set()
            for payment_type, year_data in tax_data.items():
                all_years.update(year_data.keys())
            all_years = sorted(all_years)  # Sort years (oldest to newest)

            # Payment type order
            payment_types = ['Federal', 'State', 'Service', 'Other']
            payment_types = [pt for pt in payment_types if pt in tax_data]  # Only include types with data

            # Calculate bar positions
            num_years = len(all_years)
            num_groups = len(payment_types)

            # Bar width and spacing
            bar_width = 0.8 / num_years if num_years > 0 else 0.8
            group_width = bar_width * num_years
            total_width = num_groups * group_width
            group_spacing = (10 - total_width) / (num_groups + 1) if num_groups > 0 else 1

            # Plot bars grouped by payment type
            for group_idx, payment_type in enumerate(payment_types):
                year_data = tax_data[payment_type]

                # Base position for this group
                group_center = group_spacing * (group_idx + 1) + group_width * group_idx + group_width / 2

                # Plot bars for each year in this group
                for year_idx, year in enumerate(all_years):
                    amount = year_data.get(year, 0)

                    if amount > 0:
                        # Calculate x position: left to right = oldest to newest year
                        x_offset = (year_idx - (num_years - 1) / 2) * bar_width
                        x_pos = group_center + x_offset

                        # Get year color - use tax year (payment year - 1)
                        # Payments made in 2025 are for tax year 2024
                        tax_year = year - 1
                        year_color = self.get_year_color(tax_year)
                        if not year_color:
                            year_color = '#1f77b4'

                        # Plot the bar
                        ax.bar(x_pos, amount, bar_width * 0.9, color=year_color, alpha=0.8)

                # Add payment type label on x-axis (use same color as y-axis ticks)
                try:
                    label_color = colors.get('text_secondary', '#B3B3B3')
                except:
                    label_color = '#B3B3B3'
                ax.text(group_center, -ax.get_ylim()[1] * 0.05,
                       payment_type, ha='center', va='top', fontweight='bold', color=label_color)

            # Set x-axis limits and remove ticks
            ax.set_xlim(0, 10)
            ax.set_xticks([])

            # Remove hover tooltips section for now
            pass

            # Refresh the canvas with padding
            self.tax_payments_figure.tight_layout(pad=1.75)
            self.tax_payments_canvas.draw()

        except Exception as e:
            print(f"Error generating tax payments chart: {e}")
            # Show error in the plot area
            self.tax_payments_figure.clear()
            ax = self.tax_payments_figure.add_subplot(111)
            ax.text(0.5, 0.5, f"Error: {str(e)}",
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
            self.tax_payments_canvas.draw()

    def update_summary_table(self):
        """Update the year-over-year comparison table"""
        try:
            from PyQt6.QtWidgets import QTableWidgetItem
            from PyQt6.QtCore import Qt

            # Get all years with data
            db = get_db()
            min_date = db.query(Transaction.date).order_by(Transaction.date).first()
            max_date = db.query(Transaction.date).order_by(Transaction.date.desc()).first()
            db.close()

            if not min_date or not max_date:
                return

            min_year = min_date[0].year
            current_year = datetime.now().year

            # Get data for each year
            years_data = []
            for year in range(min_year, current_year + 1):
                year_data = self.get_year_data(year)
                years_data.append(year_data)

            # Populate table
            self.summary_table.setRowCount(len(years_data))

            for row, year_data in enumerate(years_data):
                # Year
                year_item = QTableWidgetItem(str(year_data['year']))
                year_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.summary_table.setItem(row, 0, year_item)

                # Income
                income_item = QTableWidgetItem(f"${year_data['total_income']:,.0f}")
                income_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.summary_table.setItem(row, 1, income_item)

                # Saved
                saved_item = QTableWidgetItem(f"${year_data['total_savings']:,.0f}")
                saved_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.summary_table.setItem(row, 2, saved_item)

                # Get breakdown by payment type
                year = year_data['year']
                tax_data = self.get_tax_spending_data()

                # Federal
                federal = tax_data.get('Federal', {}).get(year + 1, 0)  # Payments in year+1
                federal_item = QTableWidgetItem(f"${federal:,.0f}" if federal > 0 else "---")
                federal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.summary_table.setItem(row, 3, federal_item)

                # State
                state = tax_data.get('State', {}).get(year + 1, 0)
                state_item = QTableWidgetItem(f"${state:,.0f}" if state > 0 else "---")
                state_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.summary_table.setItem(row, 4, state_item)

                # Service
                service = tax_data.get('Service', {}).get(year + 1, 0)
                service_item = QTableWidgetItem(f"${service:,.0f}" if service > 0 else "---")
                service_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.summary_table.setItem(row, 5, service_item)

                # Other
                other = tax_data.get('Other', {}).get(year + 1, 0)
                other_item = QTableWidgetItem(f"${other:,.0f}" if other > 0 else "---")
                other_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.summary_table.setItem(row, 6, other_item)

                # Remaining (saved - total deductions)
                total_deductions = federal + state + service + other
                remaining = year_data['total_savings'] - total_deductions
                remaining_item = QTableWidgetItem(f"${remaining:,.0f}")
                remaining_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.summary_table.setItem(row, 7, remaining_item)

        except Exception as e:
            print(f"Error updating summary table: {e}")

    def generate_pie_chart(self):
        """Generate pie chart showing average breakdown of tax payments"""
        try:
            self.pie_figure.clear()
            ax = self.pie_figure.add_subplot(111)

            # Get tax payment data and year savings data
            tax_data = self.get_tax_spending_data()

            # Get all years with data
            db = get_db()
            min_date = db.query(Transaction.date).order_by(Transaction.date).first()
            max_date = db.query(Transaction.date).order_by(Transaction.date.desc()).first()
            db.close()

            if not min_date or not max_date:
                ax.text(0.5, 0.5, "No data", ha='center', va='center')
                self.pie_canvas.draw()
                return

            min_year = min_date[0].year
            current_year = datetime.now().year

            # Calculate averages across all years (only for years with payments)
            categories = {'Federal': 0, 'State': 0, 'Service': 0, 'Other': 0, 'Remaining': 0}
            year_count = 0

            for year in range(min_year, current_year + 1):
                year_data = self.get_year_data(year)

                # Get payments for this year (paid in year+1)
                federal = tax_data.get('Federal', {}).get(year + 1, 0)
                state = tax_data.get('State', {}).get(year + 1, 0)
                service = tax_data.get('Service', {}).get(year + 1, 0)
                other = tax_data.get('Other', {}).get(year + 1, 0)

                # Only include years where we have payment data
                if federal + state + service + other > 0:
                    categories['Federal'] += federal
                    categories['State'] += state
                    categories['Service'] += service
                    categories['Other'] += other

                    # Remaining = saved - deductions (only for that year, not including rollover)
                    remaining = year_data['total_savings'] - (federal + state + service + other)
                    if remaining > 0:
                        categories['Remaining'] += remaining

                    year_count += 1

            # Calculate averages
            if year_count > 0:
                for key in categories:
                    categories[key] = categories[key] / year_count

            # Remove categories with 0 value
            categories = {k: v for k, v in categories.items() if v > 0}

            if not categories:
                ax.text(0.5, 0.5, "No data",
                       ha='center', va='center')
                self.pie_canvas.draw()
                return

            # Get accent colors from theme
            colors_theme = theme_manager.get_colors()
            accent_colors = [
                colors_theme.get('accent', '#9871F4'),
                colors_theme.get('accent2', '#6BF164'),
                colors_theme.get('primary', '#49A041'),
                colors_theme.get('secondary', '#8CBEFB')
            ]

            # Prepare data
            labels = list(categories.keys())
            sizes = list(categories.values())
            colors = [accent_colors[i % len(accent_colors)] for i in range(len(labels))]

            # Create pie chart
            wedges, texts, autotexts = ax.pie(sizes, labels=None, colors=colors,
                                               autopct='%1.1f%%', startangle=90)

            # Create legend below the pie chart
            legend_labels = [f"{label}" for label in labels]
            text_color = colors_theme.get('text_primary', '#FFFFFF')
            legend = ax.legend(wedges, legend_labels, loc="upper center", bbox_to_anchor=(0.5, -0.05),
                     frameon=False, fontsize=10, ncol=2)

            # Apply theme colors to legend text
            for text in legend.get_texts():
                text.set_color(text_color)

            # Apply theme colors to pie chart text
            for text in texts + autotexts:
                text.set_color(text_color)

            ax.set_facecolor(colors_theme.get('background', '#1A1A1A'))
            self.pie_figure.patch.set_facecolor(colors_theme.get('background', '#1A1A1A'))

            self.pie_figure.tight_layout()
            self.pie_canvas.draw()

        except Exception as e:
            print(f"Error generating pie chart: {e}")

    def apply_header_theme(self):
        """Apply theme styling to header elements (refresh button)"""
        colors = theme_manager.get_colors()

        # Style refresh button (QToolButton)
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

    def refresh(self):
        """Refresh the tax view data"""
        # Update progress bars and summary
        self.update_progress_bars()
        self.update_tax_summary()

        # Update income plot
        self.generate_income_plot()

        # Update tax payments chart
        self.generate_tax_payments_chart()

        # Update summary table and pie chart
        self.update_summary_table()
        self.generate_pie_chart()

        # Clear existing year boxes
        for box in self.year_boxes:
            self.history_layout.removeWidget(box)
            box.deleteLater()
        self.year_boxes.clear()

        # Check if Taxes bill exists
        if not self.check_tax_bill_exists():
            self.info_label.setText("")
            self.content_group.setTitle("Tax Features - Setup Required")
            return

        # Taxes bill exists, show data
        self.info_label.setText("")
        self.content_group.setTitle("Tax Features - Active")

        # Get all years with data
        try:
            db = get_db()

            # Get min and max years from transactions
            min_date = db.query(Transaction.date).order_by(Transaction.date).first()
            max_date = db.query(Transaction.date).order_by(Transaction.date.desc()).first()

            if min_date and max_date:
                min_year = min_date[0].year if min_date[0] else datetime.now().year
                max_year = max_date[0].year if max_date[0] else datetime.now().year

                # Set first_year for consistent color mapping
                self.first_year = min_year

                # Create year boxes from current year down to oldest
                current_year = datetime.now().year

                # Always show current year even if no data
                if current_year > max_year:
                    max_year = current_year

                # Insert at position 1 (after header) to keep newest on top
                insert_position = 1

                for year in range(max_year, min_year - 1, -1):  # Descending order
                    year_data = self.get_year_data(year)
                    year_box = self.create_year_box(year_data)
                    self.year_boxes.append(year_box)
                    self.history_layout.insertWidget(insert_position, year_box)
                    insert_position += 1
            else:
                # No data, show current year only
                current_year = datetime.now().year
                year_data = self.get_year_data(current_year)
                year_box = self.create_year_box(year_data)
                self.year_boxes.append(year_box)
                self.history_layout.insertWidget(1, year_box)

            db.close()

        except Exception as e:
            print(f"Error refreshing tax history: {e}")

    def apply_theme(self):
        """Apply the current theme to the view"""
        try:
            colors = theme_manager.get_colors()

            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {colors['background']};
                    color: {colors['text_primary']};
                }}

                QLabel {{
                    color: {colors['text_primary']};
                }}

                QScrollArea {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 5px;
                }}

                QScrollArea QWidget {{
                    background-color: {colors['surface']};
                }}

                QFrame {{
                    background-color: {colors['surface_variant']};
                    border: 1px solid {colors['border']};
                    border-radius: 5px;
                }}

                QGroupBox {{
                    font-weight: bold;
                    border: 2px solid {colors['border']};
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                    color: {colors['text_primary']};
                    background-color: {colors['surface_variant']};
                }}

                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    background-color: {colors['surface_variant']};
                }}
            """)

            # Style progress bars specifically
            if hasattr(self, 'year_progress_bar'):
                self.year_progress_bar.setStyleSheet(f"""
                    QProgressBar {{
                        border: 1px solid {colors['border']};
                        border-radius: 3px;
                        background-color: {colors['surface']};
                        height: 25px;
                        color: {colors['text_primary']};
                    }}
                    QProgressBar::chunk {{
                        background-color: {colors['primary']};
                        border-radius: 3px;
                    }}
                """)

            # No need for special styling since we use custom painting
            # Just ensure the size is correct
            if hasattr(self, 'tax_savings_progress_bar'):
                self.tax_savings_progress_bar.setFixedHeight(25)

            # Apply header theme for refresh button
            self.apply_header_theme()

        except Exception as e:
            print(f"Error applying theme to taxes view: {e}")

    def refresh_plots(self):
        """Refresh plots when theme changes"""
        try:
            if hasattr(self, 'income_canvas'):
                self.generate_income_plot()
            if hasattr(self, 'tax_payments_canvas'):
                self.generate_tax_payments_chart()
            if hasattr(self, 'summary_table'):
                self.update_summary_table()
            if hasattr(self, 'pie_canvas'):
                self.generate_pie_chart()
            # Refresh year box colors
            if hasattr(self, 'year_boxes_layout'):
                self.update_year_box_colors()
        except Exception as e:
            print(f"Error refreshing plots on theme change: {e}")

    def update_year_box_colors(self):
        """Update year box title colors to match current theme"""
        try:
            # Iterate through all year boxes and update their title colors
            for i in range(self.year_boxes_layout.count()):
                item = self.year_boxes_layout.itemAt(i)
                if item and item.widget():
                    year_box = item.widget()
                    # Extract year from title (format: "YYYY Tax Summary")
                    title = year_box.title()
                    if title and title.split()[0].isdigit():
                        year = int(title.split()[0])
                        year_color = self.get_year_color(year)

                        # Update stylesheet with new color
                        title_font = theme_manager.get_font("header")
                        base_size = title_font.pointSize()
                        new_size = int(base_size * 1.5)
                        year_box.setStyleSheet(
                            f"QGroupBox {{ font-size: {new_size}pt; }} "
                            f"QGroupBox::title {{ color: {year_color}; font-weight: bold; }}"
                        )
        except Exception as e:
            print(f"Error updating year box colors: {e}")