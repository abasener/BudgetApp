"""
Bill Row Widget - Individual bill display widget with progress bars, buttons, and charts
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, 
                             QPushButton, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from themes import theme_manager
from widgets.chart_widget import LineChartWidget
from datetime import datetime, timedelta
import math


class BillRowWidget(QWidget):
    """Widget representing a single bill with all its components"""
    
    # Signals for popup buttons
    see_more_clicked = pyqtSignal(object)  # Pass bill object
    see_history_clicked = pyqtSignal(object)  # Pass bill object
    
    def __init__(self, bill, transaction_manager, parent=None):
        super().__init__(parent)
        self.bill = bill
        self.transaction_manager = transaction_manager
        
        # Progress bars
        self.time_progress_bar = None
        self.savings_progress_bar = None
        
        # Line chart
        self.running_total_chart = None
        
        # Labels for bill writeup
        self.writeup_labels = {}
        
        self.init_ui()
        self.update_data()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.on_theme_changed)
    
    def init_ui(self):
        """Initialize the UI layout"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create main frame with border
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        colors = theme_manager.get_colors()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface']};
                border: 2px solid {colors['border']};
                border-radius: 8px;
                padding: 5px;
            }}
        """)
        
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(5)  # Reduced spacing between sections
        
        # TOP SECTION: 3-column layout (Name | Progress Bars | Buttons)
        top_section = QHBoxLayout()
        top_section.setSpacing(15)
        
        # COLUMN 1: Bill name (fixed width - only what's needed)
        self.name_label = QLabel(self.bill.name)
        self.name_label.setFont(theme_manager.get_font("subtitle"))  # Smaller font for tighter header
        self.name_label.setStyleSheet(f"color: {colors['text_primary']}; font-weight: bold;")
        self.name_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        top_section.addWidget(self.name_label)  # No stretch factor - takes only needed space
        
        # COLUMN 2: Stacked progress bars (flexible - fills remaining space)
        progress_column = QVBoxLayout()
        progress_column.setSpacing(1)  # Much tighter spacing to look like one unit
        
        # Money progress bar (top) with label on the left
        money_bar_layout = QHBoxLayout()
        money_bar_layout.setSpacing(8)
        
        money_label = QLabel("Money:")
        money_label.setFont(theme_manager.get_font("small"))
        money_label.setStyleSheet(f"color: {colors['text_secondary']};")
        money_label.setFixedWidth(60)
        
        self.savings_progress_bar = QProgressBar()
        self.savings_progress_bar.setMaximum(100)
        self.savings_progress_bar.setTextVisible(True)
        self.savings_progress_bar.setStyleSheet(f"""
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
        money_bar_layout.addWidget(self.savings_progress_bar, 1)  # Progress bar stretches
        progress_column.addLayout(money_bar_layout)
        
        # Time progress bar (bottom) with label on the left
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
                background-color: {colors['warning']};
                border-radius: 3px;
            }}
        """)
        
        time_bar_layout.addWidget(time_label)
        time_bar_layout.addWidget(self.time_progress_bar, 1)  # Progress bar stretches
        progress_column.addLayout(time_bar_layout)
        
        top_section.addLayout(progress_column, 1)  # Takes flexible space
        
        # COLUMN 3: Buttons (fixed width - only what's needed)
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(5)  # Tighter button spacing
        
        self.see_more_button = QPushButton("See More")
        self.see_more_button.clicked.connect(lambda: self.see_more_clicked.emit(self.bill))
        self.see_more_button.setFixedHeight(35)  # Smaller buttons
        self.see_more_button.setFixedWidth(120)  # Fixed width for buttons
        self.see_more_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.see_history_button = QPushButton("See History")
        self.see_history_button.clicked.connect(lambda: self.see_history_clicked.emit(self.bill))
        self.see_history_button.setFixedHeight(35)  # Smaller buttons  
        self.see_history_button.setFixedWidth(120)  # Fixed width for buttons
        self.see_history_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Style buttons
        button_style = f"""
            QPushButton {{
                background-color: {colors['primary']};
                color: {colors['surface']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(colors['primary'], 1.1)};
            }}
            QPushButton:pressed {{
                background-color: {self.lighten_color(colors['primary'], 0.9)};
            }}
        """
        self.see_more_button.setStyleSheet(button_style)
        self.see_history_button.setStyleSheet(button_style)
        
        buttons_layout.addWidget(self.see_more_button)
        buttons_layout.addWidget(self.see_history_button)
        buttons_layout.addStretch()
        
        top_section.addLayout(buttons_layout)  # No stretch factor - takes only needed space
        
        frame_layout.addLayout(top_section)
        
        # BOTTOM SECTION: Line Chart + Bill Writeup
        bottom_section = QHBoxLayout()
        bottom_section.setSpacing(10)  # Reduced spacing
        
        # Right: Bill writeup (define first to set height)
        writeup_section = QVBoxLayout()
        writeup_section.setSpacing(5)
        
        writeup_frame = QFrame()
        writeup_frame.setFrameStyle(QFrame.Shape.Box)
        writeup_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface_variant']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        
        writeup_layout = QVBoxLayout(writeup_frame)
        writeup_layout.setSpacing(3)
        
        # Bill writeup title
        writeup_title = QLabel("Bill Details")
        writeup_title.setFont(theme_manager.get_font("subtitle"))
        writeup_title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold;")
        writeup_layout.addWidget(writeup_title)
        
        # Bill details
        details = [
            ("Name:", "name"),
            ("Current Balance:", "current_balance"),
            ("Expected Payment:", "expected_payment"),
            ("Weekly Savings:", "weekly_savings"),
            ("Bill Type:", "bill_type")
        ]
        
        for label_text, key in details:
            detail_layout = QHBoxLayout()
            detail_layout.setSpacing(5)
            
            label = QLabel(label_text)
            label.setFont(theme_manager.get_font("small"))
            label.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: bold;")
            label.setMinimumWidth(120)
            
            value_label = QLabel("Loading...")
            value_label.setFont(theme_manager.get_font("small"))
            value_label.setStyleSheet(f"color: {colors['text_primary']};")
            
            self.writeup_labels[key] = value_label
            
            detail_layout.addWidget(label)
            detail_layout.addWidget(value_label, 1)
            writeup_layout.addLayout(detail_layout)
        
        writeup_layout.addStretch()
        writeup_section.addWidget(writeup_frame)
        
        # Left: Line chart showing running total over time (height matches writeup)
        self.running_total_chart = LineChartWidget("")  # No title
        # Set min and max height to match writeup frame - increased for better visibility
        writeup_frame.setMinimumHeight(250)
        writeup_frame.setMaximumHeight(250)
        self.running_total_chart.setMinimumHeight(250)  # Match writeup height
        self.running_total_chart.setMaximumHeight(250)  # Match writeup height
        
        bottom_section.addWidget(self.running_total_chart, 2)  # Take 2/3 of space
        bottom_section.addLayout(writeup_section, 1)  # Take 1/3 of space
        
        frame_layout.addLayout(bottom_section)
        
        main_layout.addWidget(frame)
        self.setLayout(main_layout)
        
        # Set fixed height for consistent rows - adjusted for tighter top, taller bottom
        self.setFixedHeight(360)
    
    def lighten_color(self, color: str, factor: float) -> str:
        """Lighten or darken a hex color by a factor"""
        try:
            color = color.lstrip('#')
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            new_rgb = tuple(min(255, max(0, int(c * factor))) for c in rgb)
            return f"#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}"
        except:
            return color
    
    def on_theme_changed(self, theme_id):
        """Handle theme change for bill row widget"""
        try:
            # Update all styling without recreating UI
            colors = theme_manager.get_colors()
            
            # Update main frame styling
            frame = self.findChild(QFrame)
            if frame:
                frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: {colors['surface']};
                        border: 2px solid {colors['border']};
                        border-radius: 8px;
                        padding: 5px;
                    }}
                """)
            
            # Update name label
            if hasattr(self, 'name_label'):
                self.name_label.setStyleSheet(f"color: {colors['text_primary']}; font-weight: bold;")
            
            # Update progress bar labels
            for child in self.findChildren(QLabel):
                if child.text() in ["Money:", "Time:"]:
                    child.setStyleSheet(f"color: {colors['text_secondary']};")
            
            # Update progress bars
            if hasattr(self, 'savings_progress_bar'):
                self.savings_progress_bar.setStyleSheet(f"""
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
            
            if hasattr(self, 'time_progress_bar'):
                self.time_progress_bar.setStyleSheet(f"""
                    QProgressBar {{
                        border: 1px solid {colors['border']};
                        border-radius: 3px;
                        background-color: {colors['surface_variant']};
                        height: 20px;
                    }}
                    QProgressBar::chunk {{
                        background-color: {colors['warning']};
                        border-radius: 3px;
                    }}
                """)
            
            # Update buttons
            button_style = f"""
                QPushButton {{
                    background-color: {colors['primary']};
                    color: {colors['surface']};
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {self.lighten_color(colors['primary'], 1.1)};
                }}
                QPushButton:pressed {{
                    background-color: {self.lighten_color(colors['primary'], 0.9)};
                }}
            """
            
            if hasattr(self, 'see_more_button'):
                self.see_more_button.setStyleSheet(button_style)
            if hasattr(self, 'see_history_button'):
                self.see_history_button.setStyleSheet(button_style)
            
            # Update writeup frame
            writeup_frames = self.findChildren(QFrame)
            for frame in writeup_frames:
                if frame.parent() != self:  # Not the main frame
                    frame.setStyleSheet(f"""
                        QFrame {{
                            background-color: {colors['surface_variant']};
                            border: 1px solid {colors['border']};
                            border-radius: 4px;
                            padding: 8px;
                        }}
                    """)
            
            # Update writeup text labels
            for label_name, label in self.writeup_labels.items():
                if ":" in label_name:  # Header labels
                    label.setStyleSheet(f"color: {colors['text_primary']}; font-weight: bold;")
                else:  # Value labels
                    label.setStyleSheet(f"color: {colors['text_secondary']};")
            
            # Force line chart to update its theme colors
            if hasattr(self, 'running_total_chart') and self.running_total_chart:
                # The LineChartWidget should auto-update via its theme_changed signal,
                # but if it's not working, we can force an update by refreshing the chart data
                self.update_line_chart()
                    
        except Exception as e:
            print(f"Error updating bill row theme: {e}")
    
    def update_data(self):
        """Update all data displays"""
        self.update_progress_bars()
        self.update_line_chart()
        self.update_writeup()
    
    def update_progress_bars(self):
        """Update the progress bars based on bill data"""
        try:
            # Time progress bar
            if hasattr(self.bill, 'last_payment_date') and self.bill.last_payment_date:
                # Calculate time progress based on payment frequency
                frequency = getattr(self.bill, 'payment_frequency', 'monthly')
                
                # Get days in payment cycle
                if frequency.lower() == 'monthly':
                    cycle_days = 30
                elif frequency.lower() == 'weekly':
                    cycle_days = 7
                elif frequency.lower() == 'bi-weekly':
                    cycle_days = 14
                elif frequency.lower() == 'yearly':
                    cycle_days = 365
                else:
                    cycle_days = 30  # Default to monthly
                
                # Calculate progress
                if isinstance(self.bill.last_payment_date, str):
                    last_payment = datetime.strptime(self.bill.last_payment_date, '%Y-%m-%d').date()
                else:
                    last_payment = self.bill.last_payment_date
                
                today = datetime.now().date()
                days_since_payment = (today - last_payment).days
                time_progress = min(100, (days_since_payment / cycle_days) * 100)
                
                self.time_progress_bar.setValue(int(time_progress))
                self.time_progress_bar.setFormat(f"{time_progress:.0f}%")
            else:
                self.time_progress_bar.setValue(0)
                self.time_progress_bar.setFormat("0%")
            
            # Savings progress bar
            typical_amount = getattr(self.bill, 'typical_amount', 1)
            current_saved = self.bill.get_current_balance(self.transaction_manager.db)
            
            if typical_amount > 0:
                savings_progress = min(100, (current_saved / typical_amount) * 100)
                self.savings_progress_bar.setValue(int(savings_progress))
                self.savings_progress_bar.setFormat(f"{savings_progress:.0f}%")
            else:
                self.savings_progress_bar.setValue(0)
                self.savings_progress_bar.setFormat("0%")
                
        except Exception as e:
            print(f"Error updating progress bars for {self.bill.name}: {e}")
            self.time_progress_bar.setValue(0)
            self.time_progress_bar.setFormat("0%")
            self.savings_progress_bar.setValue(0)
            self.savings_progress_bar.setFormat("0%")
    
    def update_line_chart(self):
        """Update the bill balance line chart using AccountHistory data"""
        try:
            # Get AccountHistory entries directly for this bill
            from models.account_history import AccountHistoryManager

            history_manager = AccountHistoryManager(self.transaction_manager.db)
            account_history = history_manager.get_account_history(self.bill.id, "bill")

            if not account_history:
                # No account history - show current balance as flat line
                current_balance = self.bill.get_current_balance(self.transaction_manager.db)
                from datetime import date
                today = date.today()
                chart_data = {"Bill Balance": [(today, current_balance)]}
                self.running_total_chart.update_data(chart_data, "", "")
                return

            # Build balance points from AccountHistory (date, running_total)
            balance_points = []
            for entry in account_history:
                balance_points.append((entry.transaction_date, entry.running_total))

            print(f"DEBUG: {self.bill.name} - Using AccountHistory with {len(account_history)} entries")
            print(f"DEBUG: {self.bill.name} - Created {len(balance_points)} chart points")

            # If more than 50 entries, show the most recent 50 for performance
            if len(balance_points) > 50:
                balance_points = balance_points[-50:]

            # Build chart data
            chart_data = {"Bill Balance": balance_points} if balance_points else {}

            # Check if this is a percentage-based bill (amount_to_save < 1.0)
            is_percentage_bill = (hasattr(self.bill, 'amount_to_save') and
                                self.bill.amount_to_save < 1.0 and
                                self.bill.amount_to_save > 0)

            if is_percentage_bill and balance_points:
                # For percentage bills, add paycheck amounts and percentage calculations
                from models.transactions import Transaction, TransactionType

                # Get income transactions (paychecks) in the same date range as balance points
                first_date = balance_points[0][0]
                last_date = balance_points[-1][0]

                income_transactions = self.transaction_manager.db.query(Transaction).filter(
                    Transaction.transaction_type == TransactionType.INCOME.value,
                    Transaction.date >= first_date,
                    Transaction.date <= last_date
                ).order_by(Transaction.date).all()

                if income_transactions:
                    # Plot paycheck amounts
                    paycheck_points = [(tx.date, tx.amount) for tx in income_transactions]
                    chart_data["Paycheck Amount"] = paycheck_points

                    # Plot expected percentage amounts (paycheck × percentage)
                    percentage_points = [
                        (tx.date, tx.amount * self.bill.amount_to_save)
                        for tx in income_transactions
                    ]
                    chart_data[f"Expected {self.bill.amount_to_save*100:.1f}%"] = percentage_points

            # Add goal line if typical amount is set and we have data points
            if (hasattr(self.bill, 'typical_amount') and self.bill.typical_amount and
                self.bill.typical_amount > 0 and balance_points):
                first_date = balance_points[0][0]
                last_date = balance_points[-1][0]
                goal_points = [
                    (first_date, self.bill.typical_amount),
                    (last_date, self.bill.typical_amount)
                ]
                chart_data["Payment Goal"] = goal_points

            # Update chart with date on X-axis, running total on Y-axis (with dots like bills should have)
            self.running_total_chart.update_data(chart_data, "", "")

        except Exception as e:
            print(f"Error updating line chart for {self.bill.name}: {e}")
            import traceback
            traceback.print_exc()
            # Show error state
            self.running_total_chart.update_data({})
    
    def update_writeup(self):
        """Update the bill writeup section"""
        try:
            # Check if this is a percentage-based bill
            is_percentage_bill = getattr(self.bill, 'amount_to_save', 0) < 1.0 and getattr(self.bill, 'amount_to_save', 0) > 0
            
            # Name
            self.writeup_labels["name"].setText(self.bill.name)
            
            # Current Balance
            current_balance = self.bill.get_current_balance(self.transaction_manager.db)
            self.writeup_labels["current_balance"].setText(f"${current_balance:.2f}")
            
            # Expected Payment - different for percentage bills
            if is_percentage_bill:
                # For percentage bills, show "Variable" since it depends on income
                self.writeup_labels["expected_payment"].setText("Variable")
            else:
                expected_payment = getattr(self.bill, 'typical_amount', 0)
                self.writeup_labels["expected_payment"].setText(f"${expected_payment:.2f}")
            
            # Weekly Savings - show as percentage for percentage bills
            amount_to_save = getattr(self.bill, 'amount_to_save', 0)
            if is_percentage_bill:
                # Show as percentage (0.3 = 30%)
                percentage = amount_to_save * 100
                self.writeup_labels["weekly_savings"].setText(f"{percentage:.1f}%")
            else:
                # Show as dollar amount (half of bi-weekly amount)
                weekly_savings = amount_to_save / 2
                self.writeup_labels["weekly_savings"].setText(f"${weekly_savings:.2f}")
            
            # Bill Type
            frequency = getattr(self.bill, 'payment_frequency', 'Unknown')
            bill_type = getattr(self.bill, 'bill_type', 'Unknown')
            if is_percentage_bill:
                type_text = f"{frequency.title()} - {bill_type} (% of income)"
            else:
                type_text = f"{frequency.title()} - {bill_type}"
            self.writeup_labels["bill_type"].setText(type_text)
            
        except Exception as e:
            print(f"Error updating writeup for {self.bill.name}: {e}")
            for key in self.writeup_labels:
                self.writeup_labels[key].setText("Error")