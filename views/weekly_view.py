"""
Bi-weekly Tab - Complete bi-weekly budget tracking with historical view
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QScrollArea, QListWidget, QListWidgetItem, QProgressBar,
                             QSizePolicy, QTableWidget, QTableWidgetItem, QCheckBox,
                             QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from themes import theme_manager
from widgets import PieChartWidget
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class WeekDetailWidget(QWidget):
    """Widget for displaying detailed information about a single week"""
    
    def __init__(self, week_number, week_data, transaction_manager, parent=None):
        super().__init__(parent)
        self.week_number = week_number
        self.week_data = week_data  # Week model from database
        self.transaction_manager = transaction_manager
        self.transactions = []
        self.pay_period_data = None  # Will store paycheck/bills/savings data
        
        self.init_ui()
        self.load_week_data()

        # Connect to theme changes
        theme_manager.theme_changed.connect(self.on_theme_changed)

    def update_header(self):
        """Update the week header with current week data"""
        if self.week_data:
            start_date = self.week_data.start_date.strftime('%m/%d')
            end_date = self.week_data.end_date.strftime('%m/%d')
            week_title = f"Week {self.week_number}: {start_date} - {end_date}"
        else:
            week_title = f"Week {self.week_number}: No Data"

        self.header_label.setText(week_title)
        
    def init_ui(self):
        """Initialize the week detail UI"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        colors = theme_manager.get_colors()
        
        # Week header with date range
        if self.week_data:
            start_date = self.week_data.start_date.strftime('%m/%d')
            end_date = self.week_data.end_date.strftime('%m/%d')
            week_title = f"Week {self.week_number}: {start_date} - {end_date}"
        else:
            week_title = f"Week {self.week_number}: No Data"
            
        self.header_label = QLabel(week_title)
        self.header_label.setFont(theme_manager.get_font("subtitle"))
        self.header_label.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        main_layout.addWidget(self.header_label)
        
        # First row: Text info, Ring chart, Pie chart (with fixed height)
        first_row_frame = QFrame()
        first_row_frame.setFixedHeight(200)  # Set fixed height to prevent stretching
        first_row = QHBoxLayout()
        first_row.setSpacing(15)
        
        # Column 1: 4-line text display
        self.create_text_info_column(first_row)
        
        # Column 2: Ring chart for money breakdown
        self.create_ring_chart_column(first_row)
        
        # Column 3: Pie chart for category breakdown  
        self.create_pie_chart_column(first_row)
        
        first_row_frame.setLayout(first_row)
        main_layout.addWidget(first_row_frame)
        
        # Second row: Progress bars
        self.create_progress_bars_row(main_layout)
        
        # Third row: Transaction table
        self.create_transaction_table(main_layout)
        
        self.setLayout(main_layout)
        
    def create_text_info_column(self, parent_layout):
        """Create the 4-line text display column"""
        text_frame = QFrame()
        text_frame.setFrameStyle(QFrame.Shape.Box)
        text_layout = QVBoxLayout()
        
        colors = theme_manager.get_colors()
        text_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface_variant']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 5px;
            }}
        """)
        
        # Week financial info labels
        self.starting_amount_label = QLabel("Starting: $0.00")
        self.current_amount_label = QLabel("Current: $0.00")
        self.spent_amount_label = QLabel("Spent: $0.00")
        self.daily_amount_label = QLabel("Daily: $0.00")
        
        for label in [self.starting_amount_label, self.current_amount_label, 
                     self.spent_amount_label, self.daily_amount_label]:
            label.setFont(theme_manager.get_font("main"))
            label.setStyleSheet(f"color: {colors['text_primary']}; padding: 2px;")
            text_layout.addWidget(label)
            
        text_frame.setLayout(text_layout)
        parent_layout.addWidget(text_frame, 1)  # Take 1 part of space
        
    def create_ring_chart_column(self, parent_layout):
        """Create ring chart for week money breakdown"""
        ring_frame = QFrame()
        ring_frame.setFrameStyle(QFrame.Shape.Box)
        ring_layout = QVBoxLayout()
        
        colors = theme_manager.get_colors()
        ring_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface_variant']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 5px;
            }}
        """)
        
        # Ring chart title - styled like pie chart header
        ring_title = QLabel("Week Money Usage")
        ring_title.setFont(theme_manager.get_font("subtitle"))
        ring_title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px; background: transparent;")
        ring_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ring_layout.addWidget(ring_title)
        
        # Chart and legend container - horizontal layout
        chart_legend_layout = QHBoxLayout()
        chart_legend_layout.setSpacing(10)
        
        # Create ring chart
        self.ring_figure = Figure(figsize=(3, 3), tight_layout=True)
        self.ring_figure.patch.set_facecolor('none')
        self.ring_canvas = FigureCanvas(self.ring_figure)
        # Make canvas background transparent too
        self.ring_canvas.setStyleSheet("background: transparent;")
        chart_legend_layout.addWidget(self.ring_canvas, 1)  # Take most of the space
        
        # Legend for ring chart - 4 rows stacked vertically on the right
        legend_layout = QVBoxLayout()
        legend_layout.setSpacing(2)
        legend_layout.setContentsMargins(5, 10, 5, 10)  # Add some top/bottom padding
        
        # Stack all categories vertically with theme colors
        chart_colors = theme_manager.get_chart_colors()
        
        self.savings_legend = QLabel("● Savings")
        self.savings_legend.setStyleSheet(f"color: #4CAF50; font-size: 9px;")  # Keep green universal
        self.savings_legend.setFont(theme_manager.get_font("small"))
        legend_layout.addWidget(self.savings_legend)
        
        self.bills_legend = QLabel("● Bills")
        self.bills_legend.setStyleSheet(f"color: #FF9800; font-size: 9px;")  # Keep orange universal
        self.bills_legend.setFont(theme_manager.get_font("small"))
        legend_layout.addWidget(self.bills_legend)
        
        self.spent_legend = QLabel("● Spent")
        self.spent_legend.setStyleSheet(f"color: {colors.get('error', '#F44336')}; font-size: 9px;")
        self.spent_legend.setFont(theme_manager.get_font("small"))
        legend_layout.addWidget(self.spent_legend)
        
        self.rollover_legend = QLabel("● Rollover")
        self.rollover_legend.setStyleSheet(f"color: {colors['primary']}; font-size: 9px;")
        self.rollover_legend.setFont(theme_manager.get_font("small"))
        legend_layout.addWidget(self.rollover_legend)
        
        legend_layout.addStretch()  # Push legend to top
        chart_legend_layout.addLayout(legend_layout)
        
        ring_layout.addLayout(chart_legend_layout)
        
        ring_frame.setLayout(ring_layout)
        parent_layout.addWidget(ring_frame, 1)  # Take 1 part of space
        
    def create_pie_chart_column(self, parent_layout):
        """Create pie chart for category breakdown"""
        pie_frame = QFrame()
        pie_frame.setFrameStyle(QFrame.Shape.Box)
        pie_layout = QVBoxLayout()
        
        colors = theme_manager.get_colors()
        pie_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface_variant']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 5px;
            }}
        """)
        
        # Use existing PieChartWidget with transparent background and no header
        self.category_pie_chart = PieChartWidget("", transparent_background=True)
        
        # Add custom header that matches background
        pie_header = QLabel("Category Spending")
        pie_header.setFont(theme_manager.get_font("subtitle"))
        pie_header.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px; background: transparent;")
        pie_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pie_layout.addWidget(pie_header)
        
        pie_layout.addWidget(self.category_pie_chart)
        
        pie_frame.setLayout(pie_layout)
        parent_layout.addWidget(pie_frame, 1)  # Take 1 part of space
        
    def create_progress_bars_row(self, parent_layout):
        """Create progress bars for money and time"""
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.Shape.Box)
        progress_frame.setMaximumHeight(60)  # Reduce height by about 1/4
        progress_layout = QHBoxLayout()
        
        colors = theme_manager.get_colors()
        progress_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface_variant']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 3px;
            }}
        """)
        
        # Money progress bar
        money_bar_layout = QHBoxLayout()
        money_label = QLabel("Money:")
        money_label.setFont(theme_manager.get_font("small"))
        money_label.setStyleSheet(f"color: {colors['text_secondary']};")
        money_label.setFixedWidth(60)
        
        self.week_money_progress_bar = QProgressBar()
        self.week_money_progress_bar.setMaximum(100)
        self.week_money_progress_bar.setTextVisible(True)
        self.week_money_progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {colors['border']};
                border-radius: 3px;
                background-color: {colors['surface']};
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {colors['primary']};
                border-radius: 3px;
            }}
        """)
        
        money_bar_layout.addWidget(money_label)
        money_bar_layout.addWidget(self.week_money_progress_bar)
        progress_layout.addLayout(money_bar_layout)
        
        # Time progress bar
        time_bar_layout = QHBoxLayout()
        time_label = QLabel("Time:")
        time_label.setFont(theme_manager.get_font("small"))
        time_label.setStyleSheet(f"color: {colors['text_secondary']};")
        time_label.setFixedWidth(60)
        
        self.week_time_progress_bar = QProgressBar()
        self.week_time_progress_bar.setMaximum(100)
        self.week_time_progress_bar.setTextVisible(True)
        self.week_time_progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {colors['border']};
                border-radius: 3px;
                background-color: {colors['surface']};
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {colors['secondary']};
                border-radius: 3px;
            }}
        """)
        
        time_bar_layout.addWidget(time_label)
        time_bar_layout.addWidget(self.week_time_progress_bar)
        progress_layout.addLayout(time_bar_layout)
        
        progress_frame.setLayout(progress_layout)
        parent_layout.addWidget(progress_frame)
        
    def create_transaction_table(self, parent_layout):
        """Create editable transaction table"""
        table_frame = QFrame()
        table_frame.setFrameStyle(QFrame.Shape.Box)
        table_layout = QVBoxLayout()
        
        colors = theme_manager.get_colors()
        table_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface_variant']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 5px;
            }}
        """)
        
        # Header row with title and buttons
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Table title
        table_title = QLabel("Week Transactions")
        table_title.setFont(theme_manager.get_font("subtitle"))
        table_title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        header_layout.addWidget(table_title)
        
        # Buttons on the right side of header
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Save Changes button
        self.save_changes_btn = QPushButton("Save Changes")
        self.save_changes_btn.setStyleSheet("padding: 5px 10px;")
        buttons_layout.addWidget(self.save_changes_btn)
        
        # Delete Row button
        self.delete_row_btn = QPushButton("Delete Row")
        self.delete_row_btn.setStyleSheet("padding: 5px 10px;")
        buttons_layout.addWidget(self.delete_row_btn)
        
        # Ignore Changes button
        self.ignore_changes_btn = QPushButton("Ignore Changes")
        self.ignore_changes_btn.setStyleSheet("padding: 5px 10px;")
        buttons_layout.addWidget(self.ignore_changes_btn)
        
        # Add buttons to header with stretch to push them right
        header_layout.addStretch()
        header_layout.addLayout(buttons_layout)
        
        table_layout.addLayout(header_layout)
        
        # Transaction table
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(5)
        self.transaction_table.setHorizontalHeaderLabels(["Day", "Category", "Amount", "Notes", "Analytics"])
        
        # Remove internal scrollbars - let the whole tab scroll instead
        self.transaction_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.transaction_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Resize table to fit all content without scrolling
        self.transaction_table.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
        
        # Enable row selection
        self.transaction_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.transaction_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Style the table
        self.transaction_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                gridline-color: {colors['border']};
            }}
            QTableWidget::item {{
                padding: 5px;
                border-bottom: 1px solid {colors['border']};
            }}
            QHeaderView::section {{
                background-color: {colors['surface_variant']};
                border: 1px solid {colors['border']};
                padding: 5px;
                font-weight: bold;
            }}
        """)
        
        # Set column widths
        self.transaction_table.setColumnWidth(0, 80)   # Day
        self.transaction_table.setColumnWidth(1, 120)  # Category
        self.transaction_table.setColumnWidth(2, 100)  # Amount
        self.transaction_table.setColumnWidth(3, 200)  # Notes
        self.transaction_table.setColumnWidth(4, 80)   # Analytics
        
        # Remove minimum height to allow table to expand naturally
        # Let table show all rows without internal scrolling
        table_layout.addWidget(self.transaction_table)
        
        # Add spacer at bottom to absorb extra vertical space
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        table_layout.addWidget(spacer)
        
        # Connect button functionality
        self.save_changes_btn.clicked.connect(self.save_changes)
        self.delete_row_btn.clicked.connect(self.delete_selected_row)
        self.ignore_changes_btn.clicked.connect(self.ignore_changes)
        
        table_frame.setLayout(table_layout)
        parent_layout.addWidget(table_frame)
        
    def load_week_data(self):
        """Load and display data for this specific week"""
        if not self.transaction_manager or not self.week_data:
            return

        try:
            # Get transactions for this week
            self.transactions = self.transaction_manager.get_transactions_by_week(self.week_data.week_number)
            print(f"DEBUG: Week {self.week_data.week_number} loaded {len(self.transactions)} total transactions")

            # Count spending transactions for debugging
            spending_count = len([t for t in self.transactions if t.is_spending and t.include_in_analytics])
            print(f"DEBUG: Week {self.week_data.week_number} has {spending_count} spending transactions")
            
            # Update text display
            self.update_week_text_info()
            
            # Update charts
            self.update_ring_chart()
            self.update_category_pie_chart()
            
            # Update progress bars
            self.update_week_progress_bars()
            
            # Update transaction table
            self.update_transaction_table()
            
        except Exception as e:
            print(f"Error loading week {self.week_number} data: {e}")
            
    def update_week_text_info(self):
        """Update the 4-line text display with week financial info"""
        # Calculate spending for this week
        # Only count actual spending transactions, exclude rollovers and bill/savings allocations
        spending_transactions = [
            t for t in self.transactions
            if t.is_spending and t.include_in_analytics
            and not (t.category == "Rollover" or (t.description and "rollover" in t.description.lower()))
            and not (t.description and "allocation" in t.description.lower())
        ]
        total_spent = sum(t.amount for t in spending_transactions)
        
        # Calculate effective starting amount: base allocation + rollover income - rollover deficits
        # Note: Bill/savings allocation transactions are already deducted from base_allocation
        if self.week_data:
            base_allocation = self.week_data.running_total
            # Add rollover income transactions (positive rollover from previous week)
            rollover_income = [t for t in self.transactions if t.transaction_type == "income" and "rollover" in t.description.lower()]
            rollover_income_total = sum(t.amount for t in rollover_income)
            # Subtract rollover deficit transactions (negative rollover from previous week)
            rollover_deficits = [t for t in self.transactions if t.transaction_type == "spending" and "rollover" in t.description.lower()]
            rollover_deficit_total = sum(t.amount for t in rollover_deficits)
            starting_amount = base_allocation + rollover_income_total - rollover_deficit_total
        else:
            # Fallback to calculated amount if no week data
            if self.pay_period_data:
                paycheck = self.pay_period_data.get('paycheck', 0.0)
                bills = self.pay_period_data.get('bills', 0.0)
                savings = self.pay_period_data.get('savings', 0.0)
                starting_amount = (paycheck - bills - savings) / 2
            else:
                starting_amount = 0.0
            
        current_amount = starting_amount - total_spent  # Allow negative values
        
        # Calculate daily amount (current / days left in week)
        today = datetime.now().date()
        if self.week_data and today >= self.week_data.start_date and today <= self.week_data.end_date:
            days_left = (self.week_data.end_date - today).days + 1
            daily_amount = current_amount / max(1, days_left)
        else:
            daily_amount = 0.0
            
        # Update labels
        self.starting_amount_label.setText(f"Starting: ${starting_amount:.2f}")
        self.current_amount_label.setText(f"Current: ${current_amount:.2f}")
        self.spent_amount_label.setText(f"Spent: ${total_spent:.2f}")
        self.daily_amount_label.setText(f"Daily: ${daily_amount:.2f}")
        
    def update_ring_chart(self):
        """Update ring chart with money breakdown"""
        self.ring_figure.clear()
        ax = self.ring_figure.add_subplot(111)
        
        # Calculate actual data: paycheck/2 as total, then portions
        if self.pay_period_data:
            paycheck = self.pay_period_data.get('paycheck', 0.0)
            bills_total = self.pay_period_data.get('bills', 0.0)
            savings_total = self.pay_period_data.get('savings', 0.0)
            
            # Divide by 2 for per-week amounts
            total_week_money = paycheck / 2
            week_bills = bills_total / 2
            week_savings = savings_total / 2

            # Calculate spent for this week
            # Only count actual spending transactions, exclude rollovers and bill/savings allocations
            spending_transactions = [
                t for t in self.transactions
                if t.is_spending and t.include_in_analytics
                and not (t.category == "Rollover" or (t.description and "rollover" in t.description.lower()))
                and not (t.description and "allocation" in t.description.lower())
            ]
            week_spent = sum(t.amount for t in spending_transactions)

            # Rollover is any amount left
            week_rollover = max(0, total_week_money - week_bills - week_savings - week_spent)

            # Debug output
            print(f"Week {self.week_number} Ring Chart Data:")
            print(f"  Total week money: ${total_week_money:.2f}")
            print(f"  Week savings: ${week_savings:.2f}")
            print(f"  Week bills: ${week_bills:.2f}")
            print(f"  Week spent: ${week_spent:.2f}")
            print(f"  Week rollover: ${week_rollover:.2f}")

            sizes = [week_savings, week_bills, week_spent, week_rollover]
            labels = ['Savings', 'Bills', 'Spent', 'Rollover']
        else:
            # Fallback data
            sizes = [0, 0, 0, 100]
            labels = ['Savings', 'Bills', 'Spent', 'Rollover']
        
        # Use theme colors for consistency - get fresh colors on each update
        theme_colors = theme_manager.get_colors()
        colors_list = [
            '#4CAF50',  # Savings (keep green as universal)
            '#FF9800',  # Bills (keep orange as universal) 
            theme_colors.get('error', '#F44336'),  # Spent (use theme error color)
            theme_colors['primary']  # Rollover (use theme primary color)
        ]
        
        # Create ring chart (donut) with transparent background
        ax.set_facecolor('none')  # Transparent axis background
        
        # Only create chart if there's data
        if sum(sizes) > 0:
            wedges, texts = ax.pie(sizes, labels=None, colors=colors_list, startangle=90,
                                  wedgeprops=dict(width=0.5))
        
        # Remove title from chart itself (title is above in UI)
        ax.set_title("")
        
        # Make figure background transparent
        self.ring_figure.patch.set_facecolor('none')
        self.ring_canvas.draw()
        
    def update_category_pie_chart(self):
        """Update category pie chart with spending breakdown"""
        # Only count actual spending transactions, exclude rollovers and bill/savings allocations
        spending_transactions = [
            t for t in self.transactions
            if t.is_spending and t.include_in_analytics
            and not (t.category == "Rollover" or (t.description and "rollover" in t.description.lower()))
            and not (t.description and "allocation" in t.description.lower())
        ]
        
        if not spending_transactions:
            self.category_pie_chart.update_data({}, "No Spending")
            return
            
        # Calculate spending by category
        category_spending = {}
        for transaction in spending_transactions:
            category = transaction.category or "Uncategorized"
            category_spending[category] = category_spending.get(category, 0) + transaction.amount
            
        self.category_pie_chart.update_data(category_spending, "Category Spending")
        
    def update_week_progress_bars(self):
        """Update progress bars for this specific week"""
        # Money progress (similar to bi-weekly but for single week)
        # Only count actual spending transactions, exclude rollovers and bill/savings allocations
        spending_transactions = [
            t for t in self.transactions
            if t.is_spending and t.include_in_analytics
            and not (t.category == "Rollover" or (t.description and "rollover" in t.description.lower()))
            and not (t.description and "allocation" in t.description.lower())
        ]
        total_spent = sum(t.amount for t in spending_transactions)
        # Calculate effective starting amount: base allocation + rollover income - rollover deficits
        # Note: Bill/savings allocation transactions are already deducted from base_allocation
        if self.week_data:
            base_allocation = self.week_data.running_total
            # Add rollover income transactions (positive rollover from previous week)
            rollover_income = [t for t in self.transactions if t.transaction_type == "income" and "rollover" in t.description.lower()]
            rollover_income_total = sum(t.amount for t in rollover_income)
            # Subtract rollover deficit transactions (negative rollover from previous week)
            rollover_deficits = [t for t in self.transactions if t.transaction_type == "spending" and "rollover" in t.description.lower()]
            rollover_deficit_total = sum(t.amount for t in rollover_deficits)
            starting_amount = base_allocation + rollover_income_total - rollover_deficit_total
        else:
            starting_amount = 0.0
        
        if starting_amount > 0:
            money_percentage = min(100, (total_spent / starting_amount) * 100)
        else:
            money_percentage = 0
            
        self.week_money_progress_bar.setValue(int(money_percentage))
        self.week_money_progress_bar.setFormat(f"${total_spent:.0f} spent")
        
        # Time progress for this week
        if self.week_data:
            today = datetime.now().date()
            if today < self.week_data.start_date:
                time_percentage = 0
            elif today > self.week_data.end_date:
                time_percentage = 100
            else:
                week_length = (self.week_data.end_date - self.week_data.start_date).days + 1
                days_elapsed = (today - self.week_data.start_date).days + 1
                time_percentage = min(100, (days_elapsed / week_length) * 100)
        else:
            time_percentage = 0
            
        self.week_time_progress_bar.setValue(int(time_percentage))
        self.week_time_progress_bar.setFormat(f"{time_percentage:.0f}% complete")
        
    def update_transaction_table(self):
        """Update transaction table with week's spending transactions only"""
        # Filter to only spending transactions (exclude paychecks, bills, savings)
        # Show ALL spending transactions regardless of analytics flag, exclude rollovers and allocations
        spending_transactions = [
            t for t in self.transactions
            if t.is_spending
            and not (t.category == "Rollover" or (t.description and "rollover" in t.description.lower()))
            and not (t.description and "allocation" in t.description.lower())
        ]

        # Sort transactions by date (oldest to newest)
        sorted_transactions = sorted(spending_transactions, key=lambda t: t.date)
        
        # Store original transaction data for change comparison
        self.original_transactions = sorted_transactions.copy()
        
        self.transaction_table.setRowCount(len(sorted_transactions))
        
        for row, transaction in enumerate(sorted_transactions):
            # Day (from date)
            day_name = transaction.date.strftime('%a')  # Mon, Tue, etc.
            day_item = QTableWidgetItem(day_name)
            day_item.setFlags(day_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Read-only
            self.transaction_table.setItem(row, 0, day_item)
            
            # Category (editable)
            category_item = QTableWidgetItem(transaction.category or "")
            self.transaction_table.setItem(row, 1, category_item)
            
            # Amount (editable)
            amount_item = QTableWidgetItem(f"${transaction.amount:.2f}")
            self.transaction_table.setItem(row, 2, amount_item)
            
            # Notes (editable)
            notes_item = QTableWidgetItem(transaction.description or "")
            self.transaction_table.setItem(row, 3, notes_item)
            
            # Analytics checkbox (editable)
            analytics_checkbox = QCheckBox()
            analytics_checkbox.setChecked(transaction.include_in_analytics)
            self.transaction_table.setCellWidget(row, 4, analytics_checkbox)
        
        # Resize table to fit all rows without scrolling
        self.transaction_table.resizeRowsToContents()
        total_height = self.transaction_table.horizontalHeader().height()
        total_height += sum(self.transaction_table.rowHeight(i) for i in range(self.transaction_table.rowCount()))
        total_height += 2  # Border
        self.transaction_table.setFixedHeight(total_height)
    
    def delete_selected_row(self):
        """Delete the currently selected row from the table (visual only)"""
        current_row = self.transaction_table.currentRow()
        if current_row >= 0:
            self.transaction_table.removeRow(current_row)
            # Recalculate table height after removing row
            self.transaction_table.resizeRowsToContents()
            total_height = self.transaction_table.horizontalHeader().height()
            total_height += sum(self.transaction_table.rowHeight(i) for i in range(self.transaction_table.rowCount()))
            total_height += 2  # Border
            self.transaction_table.setFixedHeight(total_height)
            print(f"Deleted row {current_row} (visual only)")
        else:
            print("No row selected for deletion")
    
    def ignore_changes(self):
        """Reset the table to original database values"""
        print("Ignoring changes and resetting table...")
        self.update_transaction_table()  # Reload from database
    
    def save_changes(self):
        """Save changes to database after showing confirmation dialog"""
        changes = self.detect_changes()
        
        if not changes['modified'] and not changes['deleted']:
            QMessageBox.information(self, "No Changes", "No changes to save.")
            return
        
        # Build confirmation message
        message = "Are you sure you want to save these changes?\n\n"
        
        if changes['modified']:
            message += f"MODIFIED TRANSACTIONS ({len(changes['modified'])}):\n"
            for change in changes['modified']:
                message += f"• {change['description']}\n"
            message += "\n"
        
        if changes['deleted']:
            message += f"DELETED TRANSACTIONS ({len(changes['deleted'])}):\n"
            for transaction in changes['deleted']:
                message += f"• {transaction.date.strftime('%a')} - {transaction.description} (${transaction.amount:.2f})\n"
        
        # Show confirmation dialog
        reply = QMessageBox.question(
            self, 
            "Confirm Changes", 
            message,
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Ok:
            self.apply_changes(changes)
            QMessageBox.information(self, "Success", "Changes saved successfully!")
        # If Cancel, do nothing (don't save, don't ignore)
    
    def detect_changes(self):
        """Detect changes between current table and original database data"""
        changes = {
            'modified': [],
            'deleted': []
        }
        
        # Check for deleted transactions (rows removed from table)
        current_row_count = self.transaction_table.rowCount()
        if current_row_count < len(self.original_transactions):
            # Find which transactions are missing from the table
            table_transactions = []
            for row in range(current_row_count):
                # Try to map back to original transaction by day and amount
                day_item = self.transaction_table.item(row, 0)
                amount_item = self.transaction_table.item(row, 2)
                if day_item and amount_item:
                    day_text = day_item.text()
                    amount_text = amount_item.text().replace('$', '')
                    try:
                        amount = float(amount_text)
                        # Find matching original transaction
                        for orig_trans in self.original_transactions:
                            if (orig_trans.date.strftime('%a') == day_text and 
                                abs(orig_trans.amount - amount) < 0.01):
                                table_transactions.append(orig_trans)
                                break
                    except ValueError:
                        continue
            
            # Find deleted transactions
            for orig_trans in self.original_transactions:
                if orig_trans not in table_transactions:
                    changes['deleted'].append(orig_trans)
        
        # Check for modified transactions (field changes)
        for row in range(min(current_row_count, len(self.original_transactions))):
            if row < len(self.original_transactions):
                original = self.original_transactions[row]
                
                # Get current table values
                category_item = self.transaction_table.item(row, 1)
                amount_item = self.transaction_table.item(row, 2)
                notes_item = self.transaction_table.item(row, 3)
                analytics_widget = self.transaction_table.cellWidget(row, 4)
                
                if category_item and amount_item and notes_item and analytics_widget:
                    current_category = category_item.text()
                    current_amount_text = amount_item.text().replace('$', '')
                    current_notes = notes_item.text()
                    current_analytics = analytics_widget.isChecked()
                    
                    try:
                        current_amount = float(current_amount_text)
                    except ValueError:
                        current_amount = original.amount
                    
                    # Compare with original values
                    changes_found = []
                    if current_category != (original.category or ""):
                        changes_found.append(f"Category: '{original.category or ''}' → '{current_category}'")
                    if abs(current_amount - original.amount) > 0.01:
                        changes_found.append(f"Amount: ${original.amount:.2f} → ${current_amount:.2f}")
                    if current_notes != (original.description or ""):
                        changes_found.append(f"Notes: '{original.description or ''}' → '{current_notes}'")
                    if current_analytics != original.include_in_analytics:
                        changes_found.append(f"Analytics: {original.include_in_analytics} → {current_analytics}")
                    
                    if changes_found:
                        changes['modified'].append({
                            'transaction': original,
                            'row': row,
                            'changes': changes_found,
                            'description': f"{original.date.strftime('%a')} - {original.description} - " + ", ".join(changes_found),
                            'new_values': {
                                'category': current_category,
                                'amount': current_amount,
                                'description': current_notes,
                                'include_in_analytics': current_analytics
                            }
                        })
        
        return changes
    
    def apply_changes(self, changes):
        """Apply the changes to the database"""
        try:
            # Apply modifications
            for change in changes['modified']:
                transaction = change['transaction']
                new_values = change['new_values']
                
                # Update transaction in database
                self.transaction_manager.update_transaction(
                    transaction.id,
                    {
                        'category': new_values['category'],
                        'amount': new_values['amount'], 
                        'description': new_values['description'],
                        'include_in_analytics': new_values['include_in_analytics']
                    }
                )
                print(f"Updated transaction {transaction.id}: {change['description']}")
            
            # Apply deletions
            for transaction in changes['deleted']:
                self.transaction_manager.delete_transaction(transaction.id)
                print(f"Deleted transaction {transaction.id}: {transaction.description}")
            
            # Reload the table and refresh the parent view
            self.load_week_data()
            
            # Also trigger a refresh of the parent WeeklyView to update all data
            if hasattr(self.parent(), 'update_week_info'):
                self.parent().update_week_info()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save changes: {str(e)}")
            print(f"Error applying changes: {e}")
    
    def on_theme_changed(self, theme_id):
        """Handle theme change for week detail widget"""
        try:
            self.update_week_detail_styling(theme_id)
        except Exception as e:
            print(f"Error applying theme to week detail widget: {e}")
    
    def update_week_detail_styling(self, theme_id=None):
        """Update styling for week detail widget"""
        colors = theme_manager.get_colors()
        
        # Update header label color
        if hasattr(self, 'header_label'):
            self.header_label.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        
        # Update text info labels
        for label in [getattr(self, 'starting_amount_label', None), 
                     getattr(self, 'current_amount_label', None),
                     getattr(self, 'spent_amount_label', None), 
                     getattr(self, 'daily_amount_label', None)]:
            if label:
                label.setStyleSheet(f"color: {colors['text_primary']}; padding: 2px;")
        
        # Update ring chart legend colors
        if hasattr(self, 'spent_legend'):
            self.spent_legend.setStyleSheet(f"color: {colors.get('error', '#F44336')}; font-size: 9px;")
        if hasattr(self, 'rollover_legend'):
            self.rollover_legend.setStyleSheet(f"color: {colors['primary']}; font-size: 9px;")
        
        # Update pie chart headers to use theme colors
        for child in self.findChildren(QLabel):
            if child.text() in ["Week Money Usage", "Category Spending"]:
                child.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px; background: transparent;")
        
        # Force update ring chart and pie chart with new theme colors
        self.update_ring_chart()
        if hasattr(self, 'category_pie_chart'):
            if hasattr(self.category_pie_chart, 'on_theme_changed'):
                self.category_pie_chart.on_theme_changed(theme_id)
            # Also force update the pie chart data to refresh colors
            self.update_category_pie_chart()
        
        # Update progress bar styles
        if hasattr(self, 'week_money_progress_bar'):
            self.week_money_progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid {colors['border']};
                    border-radius: 3px;
                    background-color: {colors['surface']};
                    height: 20px;
                    color: {colors['text_primary']};
                }}
                QProgressBar::chunk {{
                    background-color: {colors['primary']};
                    border-radius: 3px;
                }}
            """)
        
        if hasattr(self, 'week_time_progress_bar'):
            self.week_time_progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid {colors['border']};
                    border-radius: 3px;
                    background-color: {colors['surface']};
                    height: 20px;
                    color: {colors['text_primary']};
                }}
                QProgressBar::chunk {{
                    background-color: {colors['secondary']};
                    border-radius: 3px;
                }}
            """)
        
        # Update frame backgrounds
        for frame in self.findChildren(QFrame):
            if frame.frameStyle() == QFrame.Shape.Box:
                frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: {colors['surface_variant']};
                        border: 1px solid {colors['border']};
                        border-radius: 4px;
                        padding: 5px;
                    }}
                """)
        
        # Update transaction table styling
        if hasattr(self, 'transaction_table'):
            self.transaction_table.setStyleSheet(f"""
                QTableWidget {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    gridline-color: {colors['border']};
                    color: {colors['text_primary']};
                }}
                QTableWidget::item {{
                    padding: 5px;
                    border-bottom: 1px solid {colors['border']};
                    color: {colors['text_primary']};
                }}
                QTableWidget::item:selected {{
                    background-color: {colors['primary']};
                    color: {colors['background']};
                }}
                QTableWidget::item:hover {{
                    background-color: {colors['hover']};
                }}
                QHeaderView::section {{
                    background-color: {colors['surface_variant']};
                    border: 1px solid {colors['border']};
                    padding: 5px;
                    font-weight: bold;
                    color: {colors['text_primary']};
                }}
            """)
        
        # Update button styling
        for button in [getattr(self, 'save_changes_btn', None),
                      getattr(self, 'delete_row_btn', None),
                      getattr(self, 'ignore_changes_btn', None)]:
            if button:
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {colors['surface']};
                        color: {colors['text_primary']};
                        border: 1px solid {colors['border']};
                        border-radius: 4px;
                        padding: 5px 10px;
                    }}
                    QPushButton:hover {{
                        background-color: {colors['hover']};
                    }}
                """)
        
        # Update table title color
        for child in self.findChildren(QLabel):
            if child.text() == "Week Transactions":
                child.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")


class WeeklyView(QWidget):
    def __init__(self, transaction_manager=None, paycheck_processor=None):
        super().__init__()
        self.transaction_manager = transaction_manager
        self.paycheck_processor = paycheck_processor
        self.selected_week = None
        self.init_ui()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.on_theme_changed)
        
    def init_ui(self):
        # Set main widget background
        colors = theme_manager.get_colors()
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['background']};
            }}
        """)
        
        # Create main layout for the scroll area
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Style scroll area
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {colors['background']};
                border: none;
            }}
        """)
        
        # Create scrollable content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("📅 Bi-weekly Tab")
        title.setFont(theme_manager.get_font("title"))
        colors = theme_manager.get_colors()
        title.setStyleSheet(f"color: {colors['text_primary']};")
        content_layout.addWidget(title)
        
        # TOP ROW (1/4 of screen) - Week selector and info columns
        top_row = self.create_top_row()
        content_layout.addWidget(top_row)
        
        # BOTTOM SECTION (3/4 of screen) - Two week detail blocks
        bottom_section = self.create_bottom_section()
        content_layout.addWidget(bottom_section)
        
        # Set content layout and add to scroll area
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
        
    def create_top_row(self):
        """Create the top row with week selector and info columns"""
        top_frame = QFrame()
        top_frame.setFrameStyle(QFrame.Shape.Box)
        colors = theme_manager.get_colors()
        top_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface']};
                border: 2px solid {colors['border']};
                border-radius: 8px;
                padding: 5px;
            }}
        """)
        
        # Set fixed height for top row (1/3 of typical screen)
        top_frame.setFixedHeight(300)
        
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)
        
        # COLUMN 1: Scrollable week list
        week_list_column = self.create_week_list_column()
        top_layout.addWidget(week_list_column, 1)  # Takes 1 part of space
        
        # COLUMN 2: Paycheck amount and savings payments
        paycheck_column = self.create_paycheck_column()
        top_layout.addWidget(paycheck_column, 1)  # Takes 1 part of space
        
        # COLUMN 3: Bills payment amount
        bills_column = self.create_bills_column()
        top_layout.addWidget(bills_column, 1)  # Takes 1 part of space
        
        # COLUMN 4: Final column (2/5ths width) - Savings values and progress bars
        final_column = self.create_final_column()
        top_layout.addWidget(final_column, 2)  # Takes 2 parts of space (2/5ths)
        
        top_frame.setLayout(top_layout)
        return top_frame
        
    def create_week_list_column(self):
        """Create scrollable week list (newest on top)"""
        column_frame = QFrame()
        column_layout = QVBoxLayout()
        
        # Column title - will be updated when week is selected
        self.week_title = QLabel("Week")
        self.week_title.setFont(theme_manager.get_font("subtitle"))
        colors = theme_manager.get_colors()
        self.week_title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        column_layout.addWidget(self.week_title)
        
        # Scrollable list of weeks
        self.week_list = QListWidget()
        self.week_list.setMaximumHeight(150)
        self.week_list.itemClicked.connect(self.on_week_selected)
        
        # Style the list
        self.week_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {colors['surface_variant']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
            }}
            QListWidget::item {{
                padding: 5px;
                border-bottom: 1px solid {colors['border']};
            }}
            QListWidget::item:selected {{
                background-color: {colors['primary']};
                color: {colors['background']};
            }}
        """)
        
        column_layout.addWidget(self.week_list)
        column_frame.setLayout(column_layout)
        return column_frame
        
    def create_paycheck_column(self):
        """Create paycheck amount column with savings payments below"""
        column_frame = QFrame()
        column_layout = QVBoxLayout()
        
        # Paycheck amount display - single line format like dashboard
        self.paycheck_amount_label = QLabel("Paycheck: $0.00")
        self.paycheck_amount_label.setFont(theme_manager.get_font("subtitle"))
        colors = theme_manager.get_colors()
        self.paycheck_amount_label.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        column_layout.addWidget(self.paycheck_amount_label)
        
        # Separator
        separator = QLabel("Amount paid to Savings")
        separator.setFont(theme_manager.get_font("small"))
        separator.setStyleSheet(f"color: {colors['text_secondary']}; margin-top: 10px;")
        column_layout.addWidget(separator)
        
        # Account listings with values like dashboard
        self.savings_payments_label = QLabel("Loading...")
        self.savings_payments_label.setFont(theme_manager.get_font("monospace"))
        self.savings_payments_label.setStyleSheet(f"color: {colors['text_primary']}; background-color: {colors['surface_variant']}; padding: 5px; border-radius: 3px;")
        self.savings_payments_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        column_layout.addWidget(self.savings_payments_label)
        
        # Add stretch to push content to top
        column_layout.addStretch()
        
        column_frame.setLayout(column_layout)
        return column_frame
        
    def create_bills_column(self):
        """Create bills payment amount column"""
        column_frame = QFrame()
        column_layout = QVBoxLayout()
        
        # Column title
        title = QLabel("Amount paid to Bills")
        title.setFont(theme_manager.get_font("subtitle"))
        colors = theme_manager.get_colors()
        title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        column_layout.addWidget(title)
        
        # Bills listings with values like dashboard
        self.bills_payments_label = QLabel("Loading...")
        self.bills_payments_label.setFont(theme_manager.get_font("monospace"))
        self.bills_payments_label.setStyleSheet(f"color: {colors['text_primary']}; background-color: {colors['surface_variant']}; padding: 5px; border-radius: 3px;")
        self.bills_payments_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        column_layout.addWidget(self.bills_payments_label)
        
        # Add stretch to push content to top
        column_layout.addStretch()
        
        column_frame.setLayout(column_layout)
        return column_frame
        
    def create_final_column(self):
        """Create final column with savings values and progress bars"""
        column_frame = QFrame()
        column_layout = QVBoxLayout()
        
        # Two blocks for savings values
        savings_blocks_layout = QHBoxLayout()
        
        # Starting savings values block
        start_savings_frame = QFrame()
        start_savings_frame.setFrameStyle(QFrame.Shape.Box)
        start_savings_layout = QVBoxLayout()
        
        start_title = QLabel("Starting Saving values")
        start_title.setFont(theme_manager.get_font("subtitle"))
        colors = theme_manager.get_colors()
        start_title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        start_savings_layout.addWidget(start_title)
        
        # Account listings with values like dashboard
        self.start_savings_label = QLabel("Loading...")
        self.start_savings_label.setFont(theme_manager.get_font("monospace"))
        self.start_savings_label.setStyleSheet(f"color: {colors['text_primary']}; background-color: {colors['surface_variant']}; padding: 5px; border-radius: 3px;")
        self.start_savings_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        start_savings_layout.addWidget(self.start_savings_label)
        
        start_savings_frame.setLayout(start_savings_layout)
        savings_blocks_layout.addWidget(start_savings_frame)
        
        # Final savings values block
        final_savings_frame = QFrame()
        final_savings_frame.setFrameStyle(QFrame.Shape.Box)
        final_savings_layout = QVBoxLayout()
        
        final_title = QLabel("Final Saving values")
        final_title.setFont(theme_manager.get_font("subtitle"))
        final_title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        final_savings_layout.addWidget(final_title)
        
        # Account listings with values like dashboard
        self.final_savings_label = QLabel("Loading...")
        self.final_savings_label.setFont(theme_manager.get_font("monospace"))
        self.final_savings_label.setStyleSheet(f"color: {colors['text_primary']}; background-color: {colors['surface_variant']}; padding: 5px; border-radius: 3px;")
        self.final_savings_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        final_savings_layout.addWidget(self.final_savings_label)
        
        final_savings_frame.setLayout(final_savings_layout)
        savings_blocks_layout.addWidget(final_savings_frame)
        
        column_layout.addLayout(savings_blocks_layout)
        
        # Progress bars at bottom with labels next to bars (like Bills tab)
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(0, 10, 0, 0)
        
        # Money spent progress bar (top) with label next to it
        money_bar_layout = QHBoxLayout()
        money_bar_layout.setSpacing(8)
        
        money_label = QLabel("Money:")
        money_label.setFont(theme_manager.get_font("small"))
        money_label.setStyleSheet(f"color: {colors['text_secondary']};")
        money_label.setFixedWidth(60)
        
        self.money_progress_bar = QProgressBar()
        self.money_progress_bar.setMaximum(100)
        self.money_progress_bar.setTextVisible(True)
        self.money_progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {colors['border']};
                border-radius: 3px;
                background-color: {colors['surface_variant']};
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {colors['primary']};
                border-radius: 3px;
            }}
        """)
        
        money_bar_layout.addWidget(money_label)
        money_bar_layout.addWidget(self.money_progress_bar)
        progress_layout.addLayout(money_bar_layout)
        
        # Time progress bar (bottom) with label next to it
        time_bar_layout = QHBoxLayout()
        time_bar_layout.setSpacing(8)
        
        time_label = QLabel("Time:")
        time_label.setFont(theme_manager.get_font("small"))
        time_label.setStyleSheet(f"color: {colors['text_secondary']};")
        time_label.setFixedWidth(60)
        
        self.time_progress_bar = QProgressBar()
        self.time_progress_bar.setMaximum(100)
        self.time_progress_bar.setTextVisible(True)
        self.time_progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {colors['border']};
                border-radius: 3px;
                background-color: {colors['surface_variant']};
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {colors['secondary']};
                border-radius: 3px;
            }}
        """)
        
        time_bar_layout.addWidget(time_label)
        time_bar_layout.addWidget(self.time_progress_bar)
        progress_layout.addLayout(time_bar_layout)
        
        column_layout.addLayout(progress_layout)
        column_frame.setLayout(column_layout)
        return column_frame
        
    def create_bottom_section(self):
        """Create bottom section with two WeekDetailWidget instances"""
        bottom_frame = QFrame()
        bottom_frame.setFrameStyle(QFrame.Shape.Box)
        colors = theme_manager.get_colors()
        bottom_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface']};
                border: 2px solid {colors['border']};
                border-radius: 8px;
                padding: 5px;
            }}
        """)
        
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)
        
        # Create placeholder week detail widgets (will be updated when week is selected)
        self.week1_detail = WeekDetailWidget(1, None, self.transaction_manager)
        self.week2_detail = WeekDetailWidget(2, None, self.transaction_manager)
        
        bottom_layout.addWidget(self.week1_detail)
        bottom_layout.addWidget(self.week2_detail)
        
        bottom_frame.setLayout(bottom_layout)
        return bottom_frame
        
    def on_week_selected(self, item):
        """Handle week selection from list"""
        self.selected_week = item.data(Qt.ItemDataRole.UserRole)
        if self.selected_week:
            # Update the week title to show selected pay period number
            self.week_title.setText(f"Pay Period {self.selected_week['period_id']}")
        self.update_week_info()
        
    def update_week_info(self):
        """Update the week info columns based on selected bi-weekly period"""
        if not self.selected_week or not self.transaction_manager:
            return
            
        try:
            # Get all transactions for this bi-weekly period
            week1 = self.selected_week['week1']
            week2 = self.selected_week['week2']
            
            all_transactions = []
            week_numbers = [week1.week_number]
            if week2:
                week_numbers.append(week2.week_number)
                
            # Get all transactions for both weeks
            for week_num in week_numbers:
                week_transactions = self.transaction_manager.get_transactions_by_week(week_num)
                all_transactions.extend(week_transactions)
            
            # Calculate paycheck amount (income transactions)
            income_transactions = [t for t in all_transactions if t.is_income]
            total_paycheck = sum(t.amount for t in income_transactions)
            self.paycheck_amount_label.setText(f"Paycheck: ${total_paycheck:.2f}")
            
            # Update savings payments
            self.update_savings_payments(all_transactions)

            # Update bills payments
            self.update_bills_payments(all_transactions)

            # Update progress bars
            self.update_progress_bars(all_transactions)

            # Update week detail widgets first so week data is available
            self.update_week_details()

            # Update savings account values (start vs end of period) - must be after week details
            self.update_savings_values()
            
        except Exception as e:
            print(f"Error updating week info: {e}")
            self.paycheck_amount_label.setText("Paycheck: Error")
            self.savings_payments_label.setText("Error loading data")
            self.bills_payments_label.setText("Error loading data")
            
    def update_week_details(self):
        """Update the week detail widgets with selected period data"""
        if not self.selected_week:
            return
            
        week1 = self.selected_week['week1']
        week2 = self.selected_week['week2']
        
        # Get paycheck/bills/savings data for calculations
        try:
            # Get all transactions for the bi-weekly period
            all_transactions = []
            week_numbers = [week1.week_number]
            if week2:
                week_numbers.append(week2.week_number)
                
            for week_num in week_numbers:
                week_transactions = self.transaction_manager.get_transactions_by_week(week_num)
                all_transactions.extend(week_transactions)
            
            # Calculate totals
            income_transactions = [t for t in all_transactions if t.is_income]
            savings_transactions = [t for t in all_transactions if t.is_saving]
            bills_transactions = [t for t in all_transactions if t.is_bill_pay]
            
            pay_period_data = {
                'paycheck': sum(t.amount for t in income_transactions),
                'savings': sum(t.amount for t in savings_transactions),
                'bills': sum(t.amount for t in bills_transactions)
            }
        except:
            pay_period_data = {'paycheck': 0.0, 'savings': 0.0, 'bills': 0.0}
        
        # Update week 1 detail widget
        if hasattr(self, 'week1_detail'):
            self.week1_detail.week_data = week1
            self.week1_detail.week_number = 1
            self.week1_detail.pay_period_data = pay_period_data
            self.week1_detail.update_header()  # Update header with new week data
            self.week1_detail.load_week_data()
            
        # Update week 2 detail widget
        if hasattr(self, 'week2_detail'):
            if week2:
                self.week2_detail.week_data = week2
                self.week2_detail.week_number = 2
                self.week2_detail.pay_period_data = pay_period_data
                self.week2_detail.update_header()  # Update header with new week data
                self.week2_detail.load_week_data()
            else:
                # No second week - show empty state
                self.week2_detail.week_data = None
                self.week2_detail.week_number = 2
                self.week2_detail.pay_period_data = pay_period_data
                self.week2_detail.update_header()  # Update header (will show "No Data")
                self.week2_detail.load_week_data()
            
    def update_savings_payments(self, transactions):
        """Update savings payments display with actual balance changes (final - starting)"""
        try:
            # Get all accounts
            accounts = self.transaction_manager.get_all_accounts()

            # Get current pay period index
            current_pay_period_index = self.get_current_pay_period_index()

            savings_text = ""
            for account in accounts:
                name = account.name[:14] + "..." if len(account.name) > 14 else account.name

                # Get balance history for this account
                history = account.get_balance_history_copy()

                if not history:
                    # No history available, assume 0 change
                    amount_change = 0.0
                else:
                    # Use balance history indexing to get starting and final balances
                    starting_index = current_pay_period_index - 1  # Convert to 0-based
                    final_index = current_pay_period_index

                    # Get starting balance (beginning of this pay period)
                    if starting_index < len(history):
                        starting_balance = history[starting_index]
                    else:
                        starting_balance = history[-1] if history else account.running_total

                    # Get final balance (end of this pay period)
                    if final_index < len(history):
                        final_balance = history[final_index]
                    else:
                        # This pay period hasn't finished yet, use current balance
                        final_balance = account.running_total

                    # Calculate actual amount added to account (includes transactions + rollovers)
                    amount_change = final_balance - starting_balance

                # Format amount with proper sign
                amount_str = f"${amount_change:.0f}"
                savings_text += f"{name:<16} {amount_str:>10}\n"

            self.savings_payments_label.setText(savings_text.rstrip() or "No accounts")

        except Exception as e:
            print(f"Error updating savings payments: {e}")
            import traceback
            traceback.print_exc()
            self.savings_payments_label.setText("Error loading savings data")
            
    def update_bills_payments(self, transactions):
        """Update bills payments display with bill-by-bill breakdown"""
        try:
            # Get all bills
            bills = self.transaction_manager.get_all_bills()
            
            # Calculate payments by bill
            payments_by_bill = {}
            for bill in bills:
                payments_by_bill[bill.name] = 0.0
                
            # Sum up bill savings transactions (TransactionType.SAVING with bill_id)
            for transaction in transactions:
                if transaction.is_saving and transaction.bill_id:
                    # Bill savings allocation transaction
                    if transaction.bill:
                        bill_name = transaction.bill.name
                        if bill_name in payments_by_bill:
                            payments_by_bill[bill_name] += transaction.amount
                elif transaction.is_saving and transaction.bill_type:
                    # Handle string-based bill references for savings
                    if transaction.bill_type in payments_by_bill:
                        payments_by_bill[transaction.bill_type] += transaction.amount
                elif transaction.is_bill_pay:
                    # Actual bill payment transactions
                    if transaction.bill:
                        bill_name = transaction.bill.name
                        if bill_name in payments_by_bill:
                            payments_by_bill[bill_name] += transaction.amount
                    elif transaction.bill_type:
                        # Handle string-based bill references
                        if transaction.bill_type in payments_by_bill:
                            payments_by_bill[transaction.bill_type] += transaction.amount
            
            # Format like dashboard display
            bills_text = ""
            for bill in bills:
                name = bill.name[:14] + "..." if len(bill.name) > 14 else bill.name
                amount = payments_by_bill.get(bill.name, 0.0)
                amount_str = f"${amount:.0f}"
                bills_text += f"{name:<16} {amount_str:>10}\n"
                
            self.bills_payments_label.setText(bills_text.rstrip() or "No bill payments")
            
        except Exception as e:
            print(f"Error updating bills payments: {e}")
            self.bills_payments_label.setText("Error loading bills data")
            
    def get_current_pay_period_index(self):
        """Get the current pay period index being displayed (1-based)"""
        # Determine which pay period we're displaying
        current_pay_period_index = None
        if hasattr(self, 'week1_detail') and hasattr(self, 'week2_detail'):
            if self.week1_detail.week_data and self.week2_detail.week_data:
                # Calculate pay period index based on week numbers
                # Week 1-2 = period 1, Week 3-4 = period 2, etc.
                week1_num = self.week1_detail.week_data.week_number
                current_pay_period_index = (week1_num - 1) // 2 + 1  # Convert to 1-based pay period

        # If we can't determine from displayed weeks, use the most recent pay period
        if current_pay_period_index is None:
            all_weeks = self.transaction_manager.get_all_weeks()
            if all_weeks:
                max_week = max(week.week_number for week in all_weeks)
                current_pay_period_index = (max_week - 1) // 2 + 1  # Most recent pay period
            else:
                current_pay_period_index = 1  # Default to first period

        return current_pay_period_index

    def update_savings_values(self):
        """Update starting and ending savings account values using balance history arrays"""
        try:
            # Get all accounts
            accounts = self.transaction_manager.get_all_accounts()

            # Get current pay period index
            current_pay_period_index = self.get_current_pay_period_index()

            # Display values for each account using balance history
            start_account_text = ""
            final_account_text = ""

            for account in accounts:
                name = account.name[:14] + "..." if len(account.name) > 14 else account.name

                # Get balance history for this account
                history = account.get_balance_history_copy()

                if not history:
                    # No history available, use current balance
                    starting_balance = account.running_total
                    final_balance = account.running_total
                else:
                    # Use balance history indexing:
                    # payweek1: starting = array[0], final = array[1]
                    # payweek2: starting = array[1], final = array[2]
                    # etc.

                    starting_index = current_pay_period_index - 1  # Convert to 0-based
                    final_index = current_pay_period_index

                    # Get starting balance (beginning of this pay period)
                    if starting_index < len(history):
                        starting_balance = history[starting_index]
                    else:
                        # Not enough history, use last available or current balance
                        starting_balance = history[-1] if history else account.running_total

                    # Get final balance (end of this pay period)
                    if final_index < len(history):
                        final_balance = history[final_index]
                    else:
                        # This pay period hasn't finished yet, use current balance
                        final_balance = account.running_total

                # Format display
                start_amount_str = f"${starting_balance:.0f}"
                final_amount_str = f"${final_balance:.0f}"

                start_account_text += f"{name:<16} {start_amount_str:>10}\n"
                final_account_text += f"{name:<16} {final_amount_str:>10}\n"

            # Set the display text
            self.start_savings_label.setText(start_account_text.rstrip() or "No accounts")
            self.final_savings_label.setText(final_account_text.rstrip() or "No accounts")

        except Exception as e:
            print(f"Error updating savings values: {e}")
            import traceback
            traceback.print_exc()
            self.start_savings_label.setText("Error loading data")
            self.final_savings_label.setText("Error loading data")
            
    def update_progress_bars(self, transactions):
        """Update progress bars for money spent and time progress"""
        try:
            # Calculate money spent (spending transactions)
            spending_transactions = [t for t in transactions if t.is_spending and t.include_in_analytics]
            total_spent = sum(t.amount for t in spending_transactions)
            
            # Calculate total available money for the period
            income_transactions = [t for t in transactions if t.is_income]
            total_income = sum(t.amount for t in income_transactions)
            
            # Money progress (spent vs available)
            if total_income > 0:
                money_percentage = min(100, (total_spent / total_income) * 100)
            else:
                money_percentage = 0
                
            self.money_progress_bar.setValue(int(money_percentage))
            self.money_progress_bar.setFormat(f"${total_spent:.0f} spent")
            
            # Time progress through bi-weekly period
            if self.selected_week:
                start_date = self.selected_week['start_date']
                end_date = self.selected_week['end_date']
                today = datetime.now().date()
                
                if today < start_date:
                    time_percentage = 0
                elif today > end_date:
                    time_percentage = 100
                else:
                    period_length = (end_date - start_date).days + 1
                    days_elapsed = (today - start_date).days + 1
                    time_percentage = min(100, (days_elapsed / period_length) * 100)
                    
                self.time_progress_bar.setValue(int(time_percentage))
                self.time_progress_bar.setFormat(f"{time_percentage:.0f}% complete")
            
        except Exception as e:
            print(f"Error updating progress bars: {e}")
            self.money_progress_bar.setValue(0)
            self.time_progress_bar.setValue(0)
        
    def populate_week_list(self):
        """Populate the week list with bi-weekly periods (newest first)"""
        print("=" * 50)
        print("DEBUG: Starting populate_week_list")

        if not self.transaction_manager:
            print("DEBUG: No transaction manager!")
            return

        weeks = self.transaction_manager.get_all_weeks()
        print(f"DEBUG: populate_week_list found {len(weeks)} weeks")
        for week in weeks:
            print(f"DEBUG: Week {week.week_number} - Start: {week.start_date} - End: {week.end_date}")
        self.week_list.clear()
        
        # Group weeks into bi-weekly periods based on consecutive week numbers
        bi_weekly_periods = []

        # Create a dictionary of weeks by week number for easy lookup
        weeks_dict = {week.week_number: week for week in weeks}

        # Find the highest week number to work backwards
        if not weeks:
            return

        max_week_num = max(week.week_number for week in weeks)

        # Calculate total number of pay periods first
        total_possible_periods = (max_week_num + 1) // 2

        # Group consecutive pairs starting from highest week number
        processed_weeks = set()
        period_counter = total_possible_periods  # Start with highest number for newest period

        # Start from the highest even-numbered week and work backwards
        current_week_num = max_week_num if max_week_num % 2 == 0 else max_week_num - 1

        while current_week_num >= 1:
            week1_num = current_week_num - 1  # Odd week (week 1 of pair)
            week2_num = current_week_num      # Even week (week 2 of pair)

            week1 = weeks_dict.get(week1_num)
            week2 = weeks_dict.get(week2_num)

            if week1 and week2 and week1_num not in processed_weeks and week2_num not in processed_weeks:
                # Both weeks exist - create bi-weekly period
                print(f"DEBUG: Creating Pay Period {period_counter} with Week {week1_num} and Week {week2_num}")
                bi_weekly_periods.append({
                    'period_id': period_counter,
                    'week1': week1,
                    'week2': week2,
                    'start_date': min(week1.start_date, week2.start_date),
                    'end_date': max(week1.end_date, week2.end_date)
                })
                processed_weeks.add(week1_num)
                processed_weeks.add(week2_num)
                period_counter -= 1
            elif week2 and week2_num not in processed_weeks:
                # Only week 2 exists - single week period
                print(f"DEBUG: Creating Pay Period {period_counter} with single Week {week2_num}")
                bi_weekly_periods.append({
                    'period_id': period_counter,
                    'week1': week2,
                    'week2': None,
                    'start_date': week2.start_date,
                    'end_date': week2.end_date
                })
                processed_weeks.add(week2_num)
                period_counter -= 1
            elif week1 and week1_num not in processed_weeks:
                # Only week 1 exists - single week period
                print(f"DEBUG: Creating Pay Period {period_counter} with single Week {week1_num}")
                bi_weekly_periods.append({
                    'period_id': period_counter,
                    'week1': week1,
                    'week2': None,
                    'start_date': week1.start_date,
                    'end_date': week1.end_date
                })
                processed_weeks.add(week1_num)
                period_counter -= 1

            current_week_num -= 2  # Move to next pair

        # Handle any remaining orphaned weeks (weeks that don't have a pair)
        # Process them in descending order to maintain proper numbering
        orphaned_weeks = [(week_num, week) for week_num, week in weeks_dict.items() if week_num not in processed_weeks]
        orphaned_weeks.sort(key=lambda x: x[0], reverse=True)  # Highest week numbers first

        for week_num, week in orphaned_weeks:
            print(f"DEBUG: Creating Pay Period {period_counter} with orphaned Week {week_num}")
            bi_weekly_periods.append({
                'period_id': period_counter,
                'week1': week,
                'week2': None,
                'start_date': week.start_date,
                'end_date': week.end_date
            })
            processed_weeks.add(week_num)
            period_counter -= 1

        # Sort periods by period_id (newest first)
        bi_weekly_periods.sort(key=lambda p: p['period_id'], reverse=True)

        print(f"DEBUG: Created {len(bi_weekly_periods)} pay periods")
        for period in bi_weekly_periods:
            print(f"DEBUG: Pay Period {period['period_id']} - Start: {period['start_date']} - Weeks: {period['week1'].week_number if period['week1'] else 'None'},{period['week2'].week_number if period['week2'] else 'None'}")

        print("DEBUG: Adding periods to QListWidget...")
        for period in bi_weekly_periods:
            start_date = period['start_date']
            item_text = f"Pay Period {period['period_id']}\n{start_date.strftime('%m/%d')}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, period)
            self.week_list.addItem(item)
            print(f"DEBUG: Added {item_text} to list widget")

        print(f"DEBUG: QListWidget now has {self.week_list.count()} items")
        print("=" * 50)
            
        # Select first item by default
        if self.week_list.count() > 0:
            self.week_list.setCurrentRow(0)
            self.selected_week = self.week_list.item(0).data(Qt.ItemDataRole.UserRole)
            if self.selected_week:
                self.week_title.setText(f"Pay Period {self.selected_week['period_id']}")
            
    def refresh(self):
        """Refresh weekly data"""
        print("Refreshing bi-weekly view...")
        self.populate_week_list()
        self.update_week_info()
        
    def on_theme_changed(self, theme_id):
        """Handle theme change for weekly view - optimized for performance"""
        try:
            # Update UI styling without recalculating data
            self.update_view_styling()
            # Week detail widgets will auto-update via their own theme_changed signals
        except Exception as e:
            print(f"Error applying theme to weekly view: {e}")
    
    def update_view_styling(self):
        """Update only the visual styling of the weekly view"""
        colors = theme_manager.get_colors()
        
        # Update main widget background
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['background']};
            }}
        """)
        
        # Update scroll area background
        for child in self.findChildren(QScrollArea):
            child.setStyleSheet(f"""
                QScrollArea {{
                    background-color: {colors['background']};
                    border: none;
                }}
            """)
        
        # Update title color
        for child in self.findChildren(QLabel):
            if "Bi-weekly Tab" in child.text():
                child.setStyleSheet(f"color: {colors['text_primary']};")
        
        # Update week title color
        if hasattr(self, 'week_title'):
            self.week_title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
            
        # Update paycheck amount label
        if hasattr(self, 'paycheck_amount_label'):
            self.paycheck_amount_label.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
            
        # Update column title colors
        for child in self.findChildren(QLabel):
            if child.text() in ["Amount paid to Bills", "Starting Saving values", "Final Saving values"]:
                child.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        
        # Update monospace data labels
        if hasattr(self, 'savings_payments_label'):
            self.savings_payments_label.setStyleSheet(f"color: {colors['text_primary']}; background-color: {colors['surface_variant']}; padding: 5px; border-radius: 3px;")
        if hasattr(self, 'bills_payments_label'):
            self.bills_payments_label.setStyleSheet(f"color: {colors['text_primary']}; background-color: {colors['surface_variant']}; padding: 5px; border-radius: 3px;")
        if hasattr(self, 'start_savings_label'):
            self.start_savings_label.setStyleSheet(f"color: {colors['text_primary']}; background-color: {colors['surface_variant']}; padding: 5px; border-radius: 3px;")
        if hasattr(self, 'final_savings_label'):
            self.final_savings_label.setStyleSheet(f"color: {colors['text_primary']}; background-color: {colors['surface_variant']}; padding: 5px; border-radius: 3px;")
        
        # Update week list styling
        if hasattr(self, 'week_list'):
            self.week_list.setStyleSheet(f"""
                QListWidget {{
                    background-color: {colors['surface_variant']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                }}
                QListWidget::item {{
                    padding: 5px;
                    border-bottom: 1px solid {colors['border']};
                    color: {colors['text_primary']};
                }}
                QListWidget::item:selected {{
                    background-color: {colors['primary']};
                    color: {colors['background']};
                }}
            """)
        
        # Update progress bar styling
        if hasattr(self, 'money_progress_bar'):
            self.money_progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid {colors['border']};
                    border-radius: 3px;
                    background-color: {colors['surface']};
                    height: 20px;
                    color: {colors['text_primary']};
                }}
                QProgressBar::chunk {{
                    background-color: {colors['primary']};
                    border-radius: 3px;
                }}
            """)
        
        if hasattr(self, 'time_progress_bar'):
            self.time_progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid {colors['border']};
                    border-radius: 3px;
                    background-color: {colors['surface']};
                    height: 20px;
                    color: {colors['text_primary']};
                }}
                QProgressBar::chunk {{
                    background-color: {colors['secondary']};
                    border-radius: 3px;
                }}
            """)
        
        # Update frame background colors
        for child in self.findChildren(QFrame):
            if child.frameStyle() == QFrame.Shape.Box:
                child.setStyleSheet(f"""
                    QFrame {{
                        background-color: {colors['surface']};
                        border: 2px solid {colors['border']};
                        border-radius: 8px;
                        padding: 5px;
                    }}
                """)
        
        # Week detail widgets will auto-update via their own theme_changed signals