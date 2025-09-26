"""
Taxes View - Tax tracking and management interface with yearly history
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGroupBox, QScrollArea, QFrame, QProgressBar)
from PyQt6.QtCore import Qt
from datetime import datetime, date
from themes import theme_manager
from models import get_db, Bill, Week, Transaction


class TaxesView(QWidget):
    """View for tax tracking and management features"""

    def __init__(self, transaction_manager, analytics_engine=None):
        super().__init__()
        self.transaction_manager = transaction_manager
        self.analytics_engine = analytics_engine
        self.year_boxes = []  # Store references to year boxes for refresh

        self.init_ui()
        self.refresh()
        self.apply_theme()

        # Connect to theme changes
        theme_manager.theme_changed.connect(self.apply_theme)

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

        # Progress bars section
        self.create_progress_bars(right_layout)

        # Tax summary header row
        self.create_tax_summary_row(right_layout)

        # Main content area
        self.content_group = QGroupBox("Tax Features")
        content_layout = QVBoxLayout()

        self.info_label = QLabel()
        self.info_label.setFont(theme_manager.get_font("body"))
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setWordWrap(True)
        content_layout.addWidget(self.info_label)

        self.content_group.setLayout(content_layout)
        right_layout.addWidget(self.content_group)
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
        year_label = QLabel("Year:")
        year_label.setFont(theme_manager.get_font("small"))
        year_label.setFixedWidth(60)

        self.year_progress_bar = QProgressBar()
        self.year_progress_bar.setMaximum(100)
        self.year_progress_bar.setTextVisible(True)

        year_bar_layout.addWidget(year_label)
        year_bar_layout.addWidget(self.year_progress_bar)
        progress_layout.addLayout(year_bar_layout)

        # Tax savings health progress bar (bottom)
        savings_bar_layout = QHBoxLayout()
        savings_label = QLabel("Saved:")
        savings_label.setFont(theme_manager.get_font("small"))
        savings_label.setFixedWidth(60)

        self.tax_savings_progress_bar = QProgressBar()
        self.tax_savings_progress_bar.setMaximum(100)
        self.tax_savings_progress_bar.setTextVisible(True)

        savings_bar_layout.addWidget(savings_label)
        savings_bar_layout.addWidget(self.tax_savings_progress_bar)
        progress_layout.addLayout(savings_bar_layout)

        progress_frame.setLayout(progress_layout)
        parent_layout.addWidget(progress_frame)

    def create_tax_summary_row(self, parent_layout):
        """Create tax summary row with key numerical values"""
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(40)  # Space between items

        # Expected Tax
        self.expected_tax_label = QLabel()
        self.expected_tax_label.setFont(theme_manager.get_font("header"))
        self.expected_tax_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        summary_layout.addWidget(self.expected_tax_label)

        summary_layout.addStretch()  # Push everything to left
        parent_layout.addLayout(summary_layout)

    def update_tax_summary(self):
        """Update the tax summary row with current data"""
        if not hasattr(self, 'expected_tax_label'):
            return

        # Get expected tax (only historical data, no fallback)
        expected_tax = self.get_historical_average_spending()

        if expected_tax > 0:
            self.expected_tax_label.setText(f"Expected Tax: ${expected_tax:,.0f}")
        else:
            self.expected_tax_label.setText("Expected Tax: No Data")

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

                # Get spending in year+1 for taxes saved in 'year'
                spending_transactions = db.query(Transaction).filter(
                    Transaction.date >= next_year_start,
                    Transaction.date <= next_year_end,
                    Transaction.transaction_type == "spending",
                    Transaction.include_in_analytics == True,
                    Transaction.amount < 0  # Only negative withdrawals
                ).all()

                year_spending = sum(abs(t.amount) for t in spending_transactions)
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

                # Get spending in year+1 for taxes saved in 'year'
                spending_transactions = db.query(Transaction).filter(
                    Transaction.date >= next_year_start,
                    Transaction.date <= next_year_end,
                    Transaction.transaction_type == "spending",
                    Transaction.include_in_analytics == True,
                    Transaction.amount < 0  # Only negative withdrawals
                ).all()

                year_spending = sum(abs(t.amount) for t in spending_transactions)
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

    def update_progress_bars(self):
        """Update both progress bars with current data"""
        if not hasattr(self, 'year_progress_bar'):
            return

        # Update year progress
        year_percentage = self.calculate_year_progress()
        self.year_progress_bar.setValue(int(year_percentage))
        self.year_progress_bar.setFormat(f"{year_percentage:.1f}%")

        # Update tax savings health
        savings_health = self.calculate_tax_savings_health()
        avg_expected = self.calculate_average_past_spending()

        self.tax_savings_progress_bar.setValue(int(savings_health))
        if avg_expected > 0:
            self.tax_savings_progress_bar.setFormat(f"{savings_health:.0f}%")
        else:
            self.tax_savings_progress_bar.setFormat("0%")

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

            # Get spending transactions in year+1 (only negative amounts)
            next_year_start = date(year + 1, 1, 1)
            next_year_end = date(year + 1, 12, 31)

            spending_transactions = db.query(Transaction).filter(
                Transaction.date >= next_year_start,
                Transaction.date <= next_year_end,
                Transaction.transaction_type == "spending",
                Transaction.include_in_analytics == True,
                Transaction.amount < 0  # Only negative withdrawals
            ).all()

            total_spending = sum(abs(t.amount) for t in spending_transactions) if spending_transactions else None

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
        year_box = QGroupBox(str(year_data['year']))
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

    def refresh(self):
        """Refresh the tax view data"""
        # Update progress bars and summary
        self.update_progress_bars()
        self.update_tax_summary()

        # Clear existing year boxes
        for box in self.year_boxes:
            self.history_layout.removeWidget(box)
            box.deleteLater()
        self.year_boxes.clear()

        # Check if Taxes bill exists
        if not self.check_tax_bill_exists():
            self.info_label.setText(
                "No 'Taxes' bill found.\n\n"
                "Please create a bill named 'Taxes' to enable tax tracking features.\n\n"
                "Go to Admin → Add Bill and create a bill with the name 'Taxes'."
            )
            self.content_group.setTitle("Tax Features - Setup Required")
            return

        # Taxes bill exists, show data
        self.info_label.setText(
            "Tax tracking is enabled.\n\n"
            "The left panel shows your tax history by year.\n"
            "Each year displays:\n"
            "• Average income from paychecks\n"
            "• Average savings percentage\n"
            "• Total spending for the year\n\n"
            "More features coming soon:\n"
            "• Estimated tax calculations\n"
            "• Deduction tracking\n"
            "• Quarterly payment reminders"
        )
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

            if hasattr(self, 'tax_savings_progress_bar'):
                self.tax_savings_progress_bar.setStyleSheet(f"""
                    QProgressBar {{
                        border: 1px solid {colors['border']};
                        border-radius: 3px;
                        background-color: {colors['surface']};
                        height: 25px;
                        color: {colors['text_primary']};
                    }}
                    QProgressBar::chunk {{
                        background-color: {colors['secondary']};
                        border-radius: 3px;
                    }}
                """)

        except Exception as e:
            print(f"Error applying theme to taxes view: {e}")