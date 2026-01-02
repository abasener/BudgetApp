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
    activation_changed = pyqtSignal(object, bool)  # Pass bill object and new active state

    def __init__(self, bill, transaction_manager, is_active=True, parent=None):
        super().__init__(parent)
        self.bill = bill
        self.transaction_manager = transaction_manager
        self.is_active = is_active  # Track if bill is currently active

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
        # Grey out inactive bills (no label suffix - visual separation via spacer is enough)
        self.name_label = QLabel(self.bill.name)
        self.name_label.setFont(theme_manager.get_font("subtitle"))  # Smaller font for tighter header
        # Use text_secondary for inactive bill headers (more muted than primary but not as dim as text_disabled)
        name_color = colors['text_primary'] if self.is_active else colors['text_secondary']
        self.name_label.setStyleSheet(f"color: {name_color}; font-weight: bold;")
        self.name_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        top_section.addWidget(self.name_label)  # No stretch factor - takes only needed space
        
        # COLUMN 2: Stacked progress bars (flexible - fills remaining space)
        progress_column = QVBoxLayout()
        progress_column.setSpacing(1)  # Much tighter spacing to look like one unit
        
        # Money progress bar (top) with label on the left
        money_bar_layout = QHBoxLayout()
        money_bar_layout.setSpacing(8)

        # For inactive bills, all non-header text uses text_disabled
        label_color = colors['text_secondary'] if self.is_active else colors['text_disabled']

        money_label = QLabel("Money:")
        money_label.setFont(theme_manager.get_font("small"))
        money_label.setStyleSheet(f"color: {label_color};")
        money_label.setFixedWidth(60)

        # For inactive bills, blend progress bar colors with disabled (75% disabled, 25% original)
        if self.is_active:
            money_bar_color = colors['primary']
        else:
            money_bar_color = self.blend_colors(colors['primary'], colors['disabled'], 0.25)

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
                background-color: {money_bar_color};
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
        time_label.setStyleSheet(f"color: {label_color};")
        time_label.setFixedWidth(60)

        # For inactive bills, blend time bar color with disabled (75% disabled, 25% original)
        if self.is_active:
            time_bar_color = colors['warning']
        else:
            time_bar_color = self.blend_colors(colors['warning'], colors['disabled'], 0.25)

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
                background-color: {time_bar_color};
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
        
        # Style buttons - subtle outlined style instead of solid color
        button_style = f"""
            QPushButton {{
                background-color: {colors['background']};
                color: {colors['text_primary']};
                border: 2px solid {colors['border']};
                border-radius: 6px;
                font-weight: normal;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {colors['surface_variant']};
                border-color: {colors['primary']};
                color: {colors['primary']};
            }}
            QPushButton:pressed {{
                background-color: {colors['hover']};
                border-color: {colors['primary']};
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

        # Bill writeup title - use text_secondary for inactive instead of primary
        writeup_title = QLabel("Bill Details")
        writeup_title.setFont(theme_manager.get_font("subtitle"))
        title_color = colors['primary'] if self.is_active else colors['text_secondary']
        writeup_title.setStyleSheet(f"color: {title_color}; font-weight: bold;")
        writeup_layout.addWidget(writeup_title)

        # Bill details - for inactive: all text uses text_disabled
        # Removed "Name:" since it's redundant with the title
        details = [
            ("Current Balance:", "current_balance"),
            ("Expected Payment:", "expected_payment"),
            ("Weekly Savings:", "weekly_savings"),
            ("Bill Type:", "bill_type")
        ]

        # Colors for detail labels and values - all text_disabled for inactive
        detail_label_color = colors['text_secondary'] if self.is_active else colors['text_disabled']
        detail_value_color = colors['text_primary'] if self.is_active else colors['text_disabled']

        for label_text, key in details:
            detail_layout = QHBoxLayout()
            detail_layout.setSpacing(5)

            label = QLabel(label_text)
            label.setFont(theme_manager.get_font("small"))
            label.setStyleSheet(f"color: {detail_label_color}; font-weight: bold;")
            label.setMinimumWidth(120)

            value_label = QLabel("Loading...")
            value_label.setFont(theme_manager.get_font("small"))
            value_label.setStyleSheet(f"color: {detail_value_color};")

            self.writeup_labels[key] = value_label

            detail_layout.addWidget(label)
            detail_layout.addWidget(value_label, 1)
            writeup_layout.addLayout(detail_layout)

        # Add activation toggle button at the bottom
        toggle_layout = QHBoxLayout()
        toggle_layout.setSpacing(5)

        toggle_label = QLabel("Status:")
        toggle_label.setFont(theme_manager.get_font("small"))
        toggle_label.setStyleSheet(f"color: {detail_label_color}; font-weight: bold;")
        toggle_label.setMinimumWidth(120)

        # Create a button that shows current status and toggles on click
        self.active_toggle = QPushButton("Active" if self.is_active else "Inactive")
        self.active_toggle.setCheckable(True)
        self.active_toggle.setChecked(self.is_active)
        self.active_toggle.clicked.connect(self.on_active_toggle_changed)
        self.active_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.active_toggle.setFixedHeight(24)
        self.active_toggle.setFixedWidth(80)

        # Style based on active state
        if self.is_active:
            self.active_toggle.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['primary']};
                    color: {colors['surface']};
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {colors['primary_dark']};
                }}
            """)
        else:
            self.active_toggle.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['disabled']};
                    color: {colors['text_secondary']};
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {colors['border']};
                }}
            """)

        toggle_layout.addWidget(toggle_label)
        toggle_layout.addWidget(self.active_toggle)
        toggle_layout.addStretch()
        writeup_layout.addLayout(toggle_layout)

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

    def blend_colors(self, color1: str, color2: str, ratio: float = 0.5) -> str:
        """Blend two hex colors together. ratio=0.5 means 50% of each."""
        try:
            c1 = color1.lstrip('#')
            c2 = color2.lstrip('#')
            rgb1 = tuple(int(c1[i:i+2], 16) for i in (0, 2, 4))
            rgb2 = tuple(int(c2[i:i+2], 16) for i in (0, 2, 4))
            blended = tuple(int(rgb1[i] * ratio + rgb2[i] * (1 - ratio)) for i in range(3))
            return f"#{blended[0]:02x}{blended[1]:02x}{blended[2]:02x}"
        except:
            return color1
    
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
            
            # Update name label (respect inactive status - headers use text_secondary)
            if hasattr(self, 'name_label'):
                name_color = colors['text_primary'] if self.is_active else colors['text_secondary']
                self.name_label.setStyleSheet(f"color: {name_color}; font-weight: bold;")

            # Determine colors based on active status
            label_color = colors['text_secondary'] if self.is_active else colors['text_disabled']

            # Update progress bar labels
            for child in self.findChildren(QLabel):
                if child.text() in ["Money:", "Time:"]:
                    child.setStyleSheet(f"color: {label_color};")

            # Calculate progress bar colors (muted for inactive - 75% disabled, 25% original)
            if self.is_active:
                money_bar_color = colors['primary']
                time_bar_color = colors['warning']
            else:
                money_bar_color = self.blend_colors(colors['primary'], colors['disabled'], 0.25)
                time_bar_color = self.blend_colors(colors['warning'], colors['disabled'], 0.25)

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
                        background-color: {money_bar_color};
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
                        background-color: {time_bar_color};
                        border-radius: 3px;
                    }}
                """)
            
            # Update buttons - subtle outlined style
            button_style = f"""
                QPushButton {{
                    background-color: {colors['background']};
                    color: {colors['text_primary']};
                    border: 2px solid {colors['border']};
                    border-radius: 6px;
                    font-weight: normal;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {colors['surface_variant']};
                    border-color: {colors['primary']};
                    color: {colors['primary']};
                }}
                QPushButton:pressed {{
                    background-color: {colors['hover']};
                    border-color: {colors['primary']};
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
            
            # Update writeup title (Bill Details) - find it among children
            for child in self.findChildren(QLabel):
                if child.text() == "Bill Details":
                    title_color = colors['primary'] if self.is_active else colors['text_secondary']
                    child.setStyleSheet(f"color: {title_color}; font-weight: bold;")

            # Update writeup detail labels (the label: and value pairs)
            # For inactive: all text uses text_disabled
            detail_label_color = colors['text_secondary'] if self.is_active else colors['text_disabled']
            detail_value_color = colors['text_primary'] if self.is_active else colors['text_disabled']

            # Update the value labels we stored
            for label_name, label in self.writeup_labels.items():
                label.setStyleSheet(f"color: {detail_value_color};")

            # Update the static label texts (Name:, Current Balance:, etc.)
            for child in self.findChildren(QLabel):
                text = child.text()
                if text.endswith(":") and text not in ["Money:", "Time:"]:
                    child.setStyleSheet(f"color: {detail_label_color}; font-weight: bold;")
            
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
            from datetime import timedelta

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

            # Find starting balance entry and transaction entries
            starting_balance_entry = None
            transaction_entries = []

            for entry in account_history:
                if entry.transaction_id is None and "Starting balance" in (entry.description or ""):
                    starting_balance_entry = entry
                else:
                    transaction_entries.append(entry)

            # If we have transactions before the starting balance date, move starting balance back
            if starting_balance_entry and transaction_entries:
                earliest_transaction_date = min(entry.transaction_date for entry in transaction_entries)

                if starting_balance_entry.transaction_date >= earliest_transaction_date:
                    # Move starting balance to day before earliest transaction
                    new_start_date = earliest_transaction_date - timedelta(days=1)
                    starting_balance_entry.transaction_date = new_start_date
                    self.transaction_manager.db.flush()

            # Build balance points from AccountHistory, excluding starting balance from plot
            balance_points = []
            for entry in account_history:
                # Skip starting balance entry - don't plot it
                if entry.transaction_id is None and "Starting balance" in (entry.description or ""):
                    continue
                balance_points.append((entry.transaction_date, entry.running_total))

            # Get activation periods for boundary points and date limiting
            from datetime import date as date_type
            activation_periods = []
            if hasattr(self.bill, '_get_periods_list'):
                activation_periods = self.bill._get_periods_list()

            # For inactive bills, limit the chart to show only up to the last deactivation date
            # This helps avoid showing long flat lines after the bill became inactive
            if not self.is_active and activation_periods and balance_points:
                # Find the last end date (most recent deactivation)
                last_deactivation = None
                for period in activation_periods:
                    end_str = period.get('end')
                    if end_str:
                        end_date = date_type.fromisoformat(end_str) if isinstance(end_str, str) else end_str
                        if last_deactivation is None or end_date > last_deactivation:
                            last_deactivation = end_date

                # Filter balance points to only include those up to last deactivation
                if last_deactivation:
                    balance_points = [(d, v) for d, v in balance_points if d <= last_deactivation]

            # Add points at activation/deactivation boundaries for clearer transitions
            if activation_periods and balance_points:
                boundary_dates = set()
                for period in activation_periods:
                    start_str = period.get('start')
                    end_str = period.get('end')
                    if start_str:
                        start_date = date_type.fromisoformat(start_str) if isinstance(start_str, str) else start_str
                        boundary_dates.add(start_date)
                    if end_str:
                        end_date = date_type.fromisoformat(end_str) if isinstance(end_str, str) else end_str
                        boundary_dates.add(end_date)

                # For each boundary date not already in balance_points, interpolate the value
                existing_dates = {d for d, v in balance_points}
                sorted_points = sorted(balance_points, key=lambda x: x[0])

                for boundary in boundary_dates:
                    if boundary not in existing_dates and sorted_points:
                        # Find the balance at this boundary by interpolation
                        # Use the most recent balance before this date
                        prev_balance = None
                        for d, v in sorted_points:
                            if d <= boundary:
                                prev_balance = v
                            else:
                                break
                        if prev_balance is not None:
                            balance_points.append((boundary, prev_balance))

                # Re-sort after adding boundary points
                balance_points = sorted(balance_points, key=lambda x: x[0])

            # Apply time frame filter from settings
            from views.dialogs.settings_dialog import get_setting
            from datetime import datetime

            time_frame_filter = get_setting("time_frame_filter", "All Time")

            if time_frame_filter != "All Time" and balance_points:
                today = date_type.today()

                if time_frame_filter == "Last Year":
                    cutoff_date = today - timedelta(days=365)
                    balance_points = [(d, v) for d, v in balance_points if d >= cutoff_date]
                elif time_frame_filter == "Last Month":
                    cutoff_date = today - timedelta(days=30)
                    balance_points = [(d, v) for d, v in balance_points if d >= cutoff_date]
                elif time_frame_filter == "Last 20 Entries":
                    # Take last 20 entries
                    balance_points = balance_points[-20:]

            # Legacy fallback: If more than 50 entries and no time filter, show the most recent 50 for performance
            if time_frame_filter == "All Time" and len(balance_points) > 50:
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

            # For inactive bills, use muted chart colors (75% disabled, 25% original)
            custom_colors = None
            custom_axis_color = None
            if not self.is_active:
                colors = theme_manager.get_colors()
                chart_colors = theme_manager.get_chart_colors()
                custom_colors = [self.blend_colors(c, colors['disabled'], 0.25) for c in chart_colors]
                custom_axis_color = colors['text_disabled']  # Muted axis/tick colors

            # Get activation periods for dashed line visualization
            activation_periods = None
            if hasattr(self.bill, '_get_periods_list'):
                activation_periods = self.bill._get_periods_list()

            # Update chart with date on X-axis, running total on Y-axis (with dots like bills should have)
            self.running_total_chart.update_data(chart_data, "", "", custom_colors=custom_colors,
                                                  custom_axis_color=custom_axis_color,
                                                  activation_periods=activation_periods)

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

    def on_active_toggle_changed(self):
        """Handle activation toggle button click - toggle the current state"""
        from datetime import date

        # Toggle: if currently active, deactivate; if inactive, activate
        new_is_active = not self.is_active

        try:
            if new_is_active:
                # Activate: Add new period starting today
                self.bill.activate(start_date=date.today(), db_session=self.transaction_manager.db)
            else:
                # Deactivate: End current period today
                self.bill.deactivate(end_date=date.today(), db_session=self.transaction_manager.db)

            # Update internal state
            self.is_active = new_is_active

            # Emit signal so parent view can refresh the entire view
            self.activation_changed.emit(self.bill, new_is_active)

        except Exception as e:
            print(f"Error changing activation for {self.bill.name}: {e}")
            import traceback
            traceback.print_exc()