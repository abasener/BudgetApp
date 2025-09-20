"""
Account Row Widget - Individual savings account display widget with progress bars, buttons, and charts
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, 
                             QPushButton, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from themes import theme_manager
from widgets.chart_widget import LineChartWidget
from datetime import datetime, timedelta
import math


class AccountRowWidget(QWidget):
    """Widget representing a single savings account with all its components"""
    
    # Signals for popup buttons
    see_more_clicked = pyqtSignal(object)  # Pass account object
    see_history_clicked = pyqtSignal(object)  # Pass account object
    
    def __init__(self, account, transaction_manager, parent=None):
        super().__init__(parent)
        self.account = account
        self.transaction_manager = transaction_manager
        
        # Progress bars
        self.goal_progress_bar = None
        self.auto_save_progress_bar = None
        
        # Line chart
        self.balance_chart = None
        
        # Labels for account writeup
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
        
        # COLUMN 1: Account name (fixed width - only what's needed)
        self.name_label = QLabel(self.account.name)
        self.name_label.setFont(theme_manager.get_font("subtitle"))
        
        # Use accent color for the default savings account (rollover destination)
        is_default_save = getattr(self.account, 'is_default_save', False)
        header_color = colors['accent'] if is_default_save else colors['text_primary']
        self.name_label.setStyleSheet(f"color: {header_color}; font-weight: bold;")
        
        self.name_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        top_section.addWidget(self.name_label)
        
        # COLUMN 2: Stacked progress bars (flexible - fills remaining space)
        progress_column = QVBoxLayout()
        progress_column.setSpacing(1)
        
        # Goal progress bar (top) with label on the left
        goal_bar_layout = QHBoxLayout()
        goal_bar_layout.setSpacing(8)
        
        goal_label = QLabel("Goal:")
        goal_label.setFont(theme_manager.get_font("small"))
        goal_label.setStyleSheet(f"color: {colors['text_secondary']};")
        goal_label.setFixedWidth(60)
        
        self.goal_progress_bar = QProgressBar()
        self.goal_progress_bar.setMaximum(100)
        self.goal_progress_bar.setTextVisible(True)
        self.goal_progress_bar.setStyleSheet(f"""
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
        
        goal_bar_layout.addWidget(goal_label)
        goal_bar_layout.addWidget(self.goal_progress_bar, 1)
        progress_column.addLayout(goal_bar_layout)
        
        # Auto-save progress bar (bottom) with label on the left
        auto_save_bar_layout = QHBoxLayout()
        auto_save_bar_layout.setSpacing(8)
        
        auto_save_label = QLabel("Auto:")
        auto_save_label.setFont(theme_manager.get_font("small"))
        auto_save_label.setStyleSheet(f"color: {colors['text_secondary']};")
        auto_save_label.setFixedWidth(60)
        
        self.auto_save_progress_bar = QProgressBar()
        self.auto_save_progress_bar.setMaximum(100)
        self.auto_save_progress_bar.setTextVisible(True)
        self.auto_save_progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {colors['border']};
                border-radius: 3px;
                background-color: {colors['surface_variant']};
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {colors['accent']};
                border-radius: 3px;
            }}
        """)
        
        auto_save_bar_layout.addWidget(auto_save_label)
        auto_save_bar_layout.addWidget(self.auto_save_progress_bar, 1)
        progress_column.addLayout(auto_save_bar_layout)
        
        top_section.addLayout(progress_column, 1)
        
        # COLUMN 3: Buttons (fixed width - only what's needed)
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(5)
        
        self.see_more_button = QPushButton("See More")
        self.see_more_button.clicked.connect(lambda: self.see_more_clicked.emit(self.account))
        self.see_more_button.setFixedHeight(35)
        self.see_more_button.setFixedWidth(120)
        self.see_more_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.see_history_button = QPushButton("See History")
        self.see_history_button.clicked.connect(lambda: self.see_history_clicked.emit(self.account))
        self.see_history_button.setFixedHeight(35)
        self.see_history_button.setFixedWidth(120)
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
        
        top_section.addLayout(buttons_layout)
        
        frame_layout.addLayout(top_section)
        
        # BOTTOM SECTION: Line Chart + Account Writeup
        bottom_section = QHBoxLayout()
        bottom_section.setSpacing(10)
        
        # Right: Account writeup (define first to set height)
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
        
        # Account writeup title
        writeup_title = QLabel("Account Details")
        writeup_title.setFont(theme_manager.get_font("subtitle"))
        writeup_title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold;")
        writeup_layout.addWidget(writeup_title)
        
        # Account details
        details = [
            ("Name:", "name"),
            ("Current Balance:", "current_balance"),
            ("Goal Amount:", "goal_amount"),
            ("Goal Remaining:", "goal_remaining"),
            ("Auto-Save Amount:", "auto_save_amount")
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
        
        # Left: Line chart showing balance over time (height matches writeup)
        self.balance_chart = LineChartWidget("")  # No title
        # Set min and max height to match writeup frame
        writeup_frame.setMinimumHeight(250)
        writeup_frame.setMaximumHeight(250)
        self.balance_chart.setMinimumHeight(250)
        self.balance_chart.setMaximumHeight(250)
        
        bottom_section.addWidget(self.balance_chart, 2)  # Take 2/3 of space
        bottom_section.addLayout(writeup_section, 1)  # Take 1/3 of space
        
        frame_layout.addLayout(bottom_section)
        
        main_layout.addWidget(frame)
        self.setLayout(main_layout)
        
        # Set fixed height for consistent rows
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
        """Handle theme change for account row widget"""
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
            
            # Update account name label
            if hasattr(self, 'name_label'):
                self.name_label.setStyleSheet(f"color: {colors['text_primary']}; font-weight: bold;")
            
            # Update progress bar labels
            for child in self.findChildren(QLabel):
                if child.text() in ["Goal:", "Auto Save:"]:
                    child.setStyleSheet(f"color: {colors['text_secondary']};")
            
            # Update progress bars
            if hasattr(self, 'goal_progress_bar'):
                self.goal_progress_bar.setStyleSheet(f"""
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
            
            if hasattr(self, 'auto_save_progress_bar'):
                self.auto_save_progress_bar.setStyleSheet(f"""
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
            if hasattr(self, 'balance_chart') and self.balance_chart:
                # The LineChartWidget should auto-update via its theme_changed signal,
                # but if it's not working, we can force an update by refreshing the chart data
                self.update_line_chart()
                    
        except Exception as e:
            print(f"Error updating account row theme: {e}")
    
    def update_data(self):
        """Update all data displays"""
        self.update_progress_bars()
        self.update_line_chart()
        self.update_writeup()
    
    def update_progress_bars(self):
        """Update the progress bars based on account data"""
        try:
            # Goal progress bar
            if hasattr(self.account, 'goal_amount') and self.account.goal_amount > 0:
                current_balance = self.account.get_current_balance(self.transaction_manager.db)
                goal_progress = min(100, (current_balance / self.account.goal_amount) * 100)
                
                self.goal_progress_bar.setValue(int(goal_progress))
                self.goal_progress_bar.setFormat(f"{goal_progress:.0f}%")
            else:
                self.goal_progress_bar.setValue(0)
                self.goal_progress_bar.setFormat("No Goal")
            
            # Auto-save progress bar (show auto-save amount as % of goal or fixed amount)
            auto_save_amount = getattr(self.account, 'auto_save_amount', 0)
            if auto_save_amount > 0:
                # Check if this is a percentage-based auto-save
                is_percentage_auto_save = auto_save_amount < 1.0 and auto_save_amount > 0

                if hasattr(self.account, 'goal_amount') and self.account.goal_amount > 0:
                    # Show auto-save as percentage of goal
                    auto_save_progress = min(100, (auto_save_amount / self.account.goal_amount) * 100)
                    self.auto_save_progress_bar.setValue(int(auto_save_progress))
                    if is_percentage_auto_save:
                        self.auto_save_progress_bar.setFormat(f"{auto_save_amount*100:.1f}%")
                    else:
                        self.auto_save_progress_bar.setFormat(f"${auto_save_amount:.0f}")
                else:
                    # Show fixed amount (since no goal to compare against)
                    self.auto_save_progress_bar.setValue(50)  # Arbitrary visual
                    if is_percentage_auto_save:
                        self.auto_save_progress_bar.setFormat(f"{auto_save_amount*100:.1f}%")
                    else:
                        self.auto_save_progress_bar.setFormat(f"${auto_save_amount:.0f}")
            else:
                self.auto_save_progress_bar.setValue(0)
                self.auto_save_progress_bar.setFormat("None")
                
        except Exception as e:
            print(f"Error updating progress bars for {self.account.name}: {e}")
            self.goal_progress_bar.setValue(0)
            self.goal_progress_bar.setFormat("Error")
            self.auto_save_progress_bar.setValue(0)
            self.auto_save_progress_bar.setFormat("Error")
    
    def update_line_chart(self):
        """Update the account balance line chart using AccountHistory data"""
        try:
            # Get AccountHistory entries directly from the database
            from models.account_history import AccountHistoryManager

            history_manager = AccountHistoryManager(self.transaction_manager.db)
            account_history = history_manager.get_account_history(self.account.id, "savings")

            if not account_history:
                # No account history - show current balance as flat line
                current_balance = self.account.get_current_balance(self.transaction_manager.db)
                from datetime import date
                today = date.today()
                chart_data = {"Account Balance": [(today, current_balance)]}
                self.balance_chart.update_data(chart_data, "", "")
                return

            # Build balance points from AccountHistory (date, running_total)
            balance_points = []
            for entry in account_history:
                balance_points.append((entry.transaction_date, entry.running_total))

            print(f"DEBUG: {self.account.name} - Using AccountHistory with {len(account_history)} entries")
            print(f"DEBUG: {self.account.name} - Created {len(balance_points)} chart points")

            # If more than 50 entries, show the most recent 50 for performance
            if len(balance_points) > 50:
                balance_points = balance_points[-50:]

            # Build chart data
            chart_data = {"Account Balance": balance_points} if balance_points else {}

            # Check if this is a percentage-based auto-save account (auto_save_amount < 1.0)
            is_percentage_auto_save = (hasattr(self.account, 'auto_save_amount') and
                                     self.account.auto_save_amount < 1.0 and
                                     self.account.auto_save_amount > 0)

            if is_percentage_auto_save and balance_points:
                # For percentage auto-save accounts, add paycheck amounts and percentage calculations
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
                        (tx.date, tx.amount * self.account.auto_save_amount)
                        for tx in income_transactions
                    ]
                    chart_data[f"Expected {self.account.auto_save_amount*100:.1f}%"] = percentage_points

            # Add goal line if goal is set and we have data points
            if (hasattr(self.account, 'goal_amount') and self.account.goal_amount and
                self.account.goal_amount > 0 and balance_points):
                first_date = balance_points[0][0]
                last_date = balance_points[-1][0]
                goal_points = [
                    (first_date, self.account.goal_amount),
                    (last_date, self.account.goal_amount)
                ]
                chart_data["Goal"] = goal_points

            # Update chart with date on X-axis, running total on Y-axis
            self.balance_chart.update_data(chart_data, "", "")  # No x/y labels for cleaner look

        except Exception as e:
            print(f"Error updating line chart for {self.account.name}: {e}")
            import traceback
            traceback.print_exc()
            # Show error state
            self.balance_chart.update_data({})
    
    def update_writeup(self):
        """Update the account writeup section"""
        try:
            # Name
            self.writeup_labels["name"].setText(self.account.name)
            
            # Current Balance
            current_balance = self.account.get_current_balance(self.transaction_manager.db)
            self.writeup_labels["current_balance"].setText(f"${current_balance:.2f}")
            
            # Goal Amount
            goal_amount = getattr(self.account, 'goal_amount', 0)
            if goal_amount > 0:
                self.writeup_labels["goal_amount"].setText(f"${goal_amount:.2f}")
            else:
                self.writeup_labels["goal_amount"].setText("No goal set")
            
            # Goal Remaining
            if goal_amount > 0:
                goal_remaining = max(0, goal_amount - current_balance)
                if goal_remaining > 0:
                    self.writeup_labels["goal_remaining"].setText(f"${goal_remaining:.2f}")
                else:
                    self.writeup_labels["goal_remaining"].setText("Goal achieved!")
            else:
                self.writeup_labels["goal_remaining"].setText("N/A")
            
            # Auto-Save Amount - handle percentage vs dollar display
            auto_save_amount = getattr(self.account, 'auto_save_amount', 0)
            if auto_save_amount > 0:
                # Check if this is a percentage-based auto-save
                if auto_save_amount < 1.0 and auto_save_amount > 0:
                    # Show as percentage (0.1 = 10%)
                    percentage = auto_save_amount * 100
                    self.writeup_labels["auto_save_amount"].setText(f"{percentage:.1f}% per paycheck")
                else:
                    # Show as dollar amount
                    self.writeup_labels["auto_save_amount"].setText(f"${auto_save_amount:.2f} per paycheck")
            else:
                self.writeup_labels["auto_save_amount"].setText("Not configured")
            
        except Exception as e:
            print(f"Error updating writeup for {self.account.name}: {e}")
            for key in self.writeup_labels:
                self.writeup_labels[key].setText("Error")