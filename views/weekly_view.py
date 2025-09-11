"""
Bi-weekly Tab - Complete bi-weekly budget tracking with historical view
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QScrollArea, QListWidget, QListWidgetItem, QProgressBar,
                             QSizePolicy, QTableWidget, QTableWidgetItem, QCheckBox)
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
        
    def init_ui(self):
        """Initialize the week detail UI"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        colors = theme_manager.get_colors()
        
        # Week header with start date (first day of week)
        if self.week_data:
            week_title = f"Week {self.week_number}: {self.week_data.start_date.strftime('%A')}"
        else:
            week_title = f"Week {self.week_number}: No Data"
            
        self.header_label = QLabel(week_title)
        self.header_label.setFont(theme_manager.get_font("subtitle"))
        self.header_label.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        main_layout.addWidget(self.header_label)
        
        # First row: Text info, Ring chart, Pie chart
        first_row = QHBoxLayout()
        first_row.setSpacing(15)
        
        # Column 1: 4-line text display
        self.create_text_info_column(first_row)
        
        # Column 2: Ring chart for money breakdown
        self.create_ring_chart_column(first_row)
        
        # Column 3: Pie chart for category breakdown  
        self.create_pie_chart_column(first_row)
        
        main_layout.addLayout(first_row)
        
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
        
        # Stack all categories vertically
        savings_legend = QLabel("● Savings")
        savings_legend.setStyleSheet(f"color: #4CAF50; font-size: 9px;")
        savings_legend.setFont(theme_manager.get_font("small"))
        legend_layout.addWidget(savings_legend)
        
        bills_legend = QLabel("● Bills")
        bills_legend.setStyleSheet(f"color: #FF9800; font-size: 9px;")
        bills_legend.setFont(theme_manager.get_font("small"))
        legend_layout.addWidget(bills_legend)
        
        spent_legend = QLabel("● Spent")
        spent_legend.setStyleSheet(f"color: #F44336; font-size: 9px;")
        spent_legend.setFont(theme_manager.get_font("small"))
        legend_layout.addWidget(spent_legend)
        
        rollover_legend = QLabel("● Rollover")
        rollover_legend.setStyleSheet(f"color: #2196F3; font-size: 9px;")
        rollover_legend.setFont(theme_manager.get_font("small"))
        legend_layout.addWidget(rollover_legend)
        
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
        
        # Table title
        table_title = QLabel("Week Transactions")
        table_title.setFont(theme_manager.get_font("subtitle"))
        table_title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        table_layout.addWidget(table_title)
        
        # Transaction table
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(5)
        self.transaction_table.setHorizontalHeaderLabels(["Day", "Category", "Amount", "Notes", "Analytics"])
        
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
        
        # Give transaction table more space and minimum height
        self.transaction_table.setMinimumHeight(200)  # Increase table height
        table_layout.addWidget(self.transaction_table)
        table_frame.setLayout(table_layout)
        parent_layout.addWidget(table_frame)
        
    def load_week_data(self):
        """Load and display data for this specific week"""
        if not self.transaction_manager or not self.week_data:
            return
            
        try:
            # Get transactions for this week
            self.transactions = self.transaction_manager.get_transactions_by_week(self.week_data.week_number)
            
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
        spending_transactions = [t for t in self.transactions if t.is_spending and t.include_in_analytics]
        total_spent = sum(t.amount for t in spending_transactions)
        
        # Calculate starting amount: (paycheck - bills - savings) / 2
        if self.pay_period_data:
            paycheck = self.pay_period_data.get('paycheck', 0.0)
            bills = self.pay_period_data.get('bills', 0.0)
            savings = self.pay_period_data.get('savings', 0.0)
            starting_amount = (paycheck - bills - savings) / 2
        else:
            starting_amount = 0.0
            
        current_amount = max(0, starting_amount - total_spent)
        
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
            spending_transactions = [t for t in self.transactions if t.is_spending and t.include_in_analytics]
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
        
        colors_list = ['#4CAF50', '#FF9800', '#F44336', '#2196F3']
        
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
        spending_transactions = [t for t in self.transactions if t.is_spending and t.include_in_analytics]
        
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
        spending_transactions = [t for t in self.transactions if t.is_spending and t.include_in_analytics]
        total_spent = sum(t.amount for t in spending_transactions)
        starting_amount = self.week_data.running_total if self.week_data else 0.0
        
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
        """Update transaction table with week's transactions"""
        # Sort transactions by date (oldest to newest)
        sorted_transactions = sorted(self.transactions, key=lambda t: t.date)
        
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


class WeeklyView(QWidget):
    def __init__(self, transaction_manager=None, paycheck_processor=None):
        super().__init__()
        self.transaction_manager = transaction_manager
        self.paycheck_processor = paycheck_processor
        self.selected_week = None
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("📅 Bi-weekly Tab")
        title.setFont(theme_manager.get_font("title"))
        colors = theme_manager.get_colors()
        title.setStyleSheet(f"color: {colors['text_primary']};")
        main_layout.addWidget(title)
        
        # TOP ROW (1/4 of screen) - Week selector and info columns
        top_row = self.create_top_row()
        main_layout.addWidget(top_row)
        
        # BOTTOM SECTION (3/4 of screen) - Two week detail blocks
        bottom_section = self.create_bottom_section()
        main_layout.addWidget(bottom_section)
        
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
            
            # Update savings account values (start vs end of period)
            self.update_savings_values()
            
            # Update progress bars
            self.update_progress_bars(all_transactions)
            
            # Update week detail widgets
            self.update_week_details()
            
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
            self.week1_detail.load_week_data()
            
        # Update week 2 detail widget
        if hasattr(self, 'week2_detail'):
            if week2:
                self.week2_detail.week_data = week2
                self.week2_detail.week_number = 2
                self.week2_detail.pay_period_data = pay_period_data
                self.week2_detail.load_week_data()
            else:
                # No second week - show empty state
                self.week2_detail.week_data = None
                self.week2_detail.week_number = 2
                self.week2_detail.pay_period_data = pay_period_data
                self.week2_detail.load_week_data()
            
    def update_savings_payments(self, transactions):
        """Update savings payments display with account-by-account breakdown"""
        try:
            # Get all accounts
            accounts = self.transaction_manager.get_all_accounts()
            
            # Calculate savings by account
            savings_by_account = {}
            for account in accounts:
                savings_by_account[account.name] = 0.0
                
            # Sum up savings transactions by account
            for transaction in transactions:
                if transaction.is_saving and transaction.account:
                    account_name = transaction.account.name
                    if account_name in savings_by_account:
                        savings_by_account[account_name] += transaction.amount
                elif transaction.is_saving and transaction.account_saved_to:
                    # Handle string-based account references
                    if transaction.account_saved_to in savings_by_account:
                        savings_by_account[transaction.account_saved_to] += transaction.amount
            
            # Format like dashboard display
            savings_text = ""
            for account in accounts:
                name = account.name[:14] + "..." if len(account.name) > 14 else account.name
                amount = savings_by_account.get(account.name, 0.0)
                amount_str = f"${amount:.0f}"
                savings_text += f"{name:<16} {amount_str:>10}\n"
                
            self.savings_payments_label.setText(savings_text.rstrip() or "No savings payments")
            
        except Exception as e:
            print(f"Error updating savings payments: {e}")
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
                
            # Sum up bill payment transactions
            for transaction in transactions:
                if transaction.is_bill_pay:
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
            
    def update_savings_values(self):
        """Update starting and ending savings account values"""
        try:
            # Get all accounts
            accounts = self.transaction_manager.get_all_accounts()
            
            # For now, show current values (would need historical tracking for true start/end)
            # This could be enhanced to track account balances over time
            account_text = ""
            for account in accounts:
                name = account.name[:14] + "..." if len(account.name) > 14 else account.name
                amount_str = f"${account.running_total:.0f}"
                account_text += f"{name:<16} {amount_str:>10}\n"
            
            # Use current values for both start and end for now
            display_text = account_text.rstrip() or "No accounts"
            self.start_savings_label.setText(display_text)
            self.final_savings_label.setText(display_text)
            
        except Exception as e:
            print(f"Error updating savings values: {e}")
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
        if not self.transaction_manager:
            return
            
        weeks = self.transaction_manager.get_all_weeks()
        self.week_list.clear()
        
        # Sort weeks by number (newest first)
        weeks.sort(key=lambda w: w.week_number, reverse=True)
        
        # Group weeks into bi-weekly periods (assuming consecutive weeks form pairs)
        bi_weekly_periods = []
        
        # Calculate total number of pay periods first
        total_periods = (len(weeks) + 1) // 2  # Round up for odd number of weeks
        
        for i in range(0, len(weeks), 2):
            # Calculate pay period number (newest = highest number)
            pay_period_number = total_periods - (i // 2)
            
            if i + 1 < len(weeks):
                # Bi-weekly period with 2 weeks
                week1 = weeks[i]
                week2 = weeks[i + 1]
                bi_weekly_periods.append({
                    'period_id': pay_period_number,  # Newest period has highest number
                    'week1': week1,
                    'week2': week2,
                    'start_date': min(week1.start_date, week2.start_date),
                    'end_date': max(week1.end_date, week2.end_date)
                })
            elif len(weeks) > 0:
                # Single week period
                week = weeks[i]
                bi_weekly_periods.append({
                    'period_id': pay_period_number,  # Newest period has highest number
                    'week1': week,
                    'week2': None,
                    'start_date': week.start_date,
                    'end_date': week.end_date
                })
        
        for period in bi_weekly_periods:
            start_date = period['start_date']
            item_text = f"Pay Period {period['period_id']}\n{start_date.strftime('%m/%d')}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, period)
            self.week_list.addItem(item)
            
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
        """Handle theme changes"""
        # Reapply styles when theme changes
        colors = theme_manager.get_colors()
        
        # Update header colors to use primary (accent) color
        if hasattr(self, 'week_title'):
            self.week_title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        if hasattr(self, 'paycheck_amount_label'):
            self.paycheck_amount_label.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        
        # Re-initialize UI for complete theme update
        self.init_ui()