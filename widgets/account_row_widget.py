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
    activation_changed = pyqtSignal(object, bool)  # Pass account object and new active state

    def __init__(self, account, transaction_manager, is_active=True, parent=None):
        super().__init__(parent)
        self.account = account
        self.transaction_manager = transaction_manager
        self.is_active = is_active  # Track if account is currently active

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
        # No "(Inactive)" suffix - visual separation via spacer is enough
        self.name_label = QLabel(self.account.name)
        self.name_label.setFont(theme_manager.get_font("subtitle"))

        # Use accent color for the default savings account (rollover destination)
        # Use text_secondary for inactive account headers (not as dim as text_disabled)
        is_default_save = getattr(self.account, 'is_default_save', False)
        if not self.is_active:
            header_color = colors['text_secondary']  # Header uses text_secondary for inactive
        elif is_default_save:
            header_color = colors['accent']  # Accent for default save
        else:
            header_color = colors['text_primary']  # Normal for active
        self.name_label.setStyleSheet(f"color: {header_color}; font-weight: bold;")

        self.name_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        top_section.addWidget(self.name_label)
        
        # COLUMN 2: Stacked progress bars (flexible - fills remaining space)
        progress_column = QVBoxLayout()
        progress_column.setSpacing(1)

        # For inactive accounts, shift colors: text_secondary -> text_disabled
        label_color = colors['text_secondary'] if self.is_active else colors['text_disabled']

        # For inactive accounts, blend progress bar colors with disabled (75% disabled, 25% original)
        if self.is_active:
            goal_bar_color = colors['primary']
            auto_bar_color = colors['accent']
        else:
            goal_bar_color = self.blend_colors(colors['primary'], colors['disabled'], 0.25)
            auto_bar_color = self.blend_colors(colors['accent'], colors['disabled'], 0.25)

        # Goal progress bar (top) with label on the left
        goal_bar_layout = QHBoxLayout()
        goal_bar_layout.setSpacing(8)

        goal_label = QLabel("Goal:")
        goal_label.setFont(theme_manager.get_font("small"))
        goal_label.setStyleSheet(f"color: {label_color};")
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
                background-color: {goal_bar_color};
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
        auto_save_label.setStyleSheet(f"color: {label_color};")
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
                background-color: {auto_bar_color};
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

        # Account writeup title - use text_secondary for inactive instead of primary
        writeup_title = QLabel("Account Details")
        writeup_title.setFont(theme_manager.get_font("subtitle"))
        title_color = colors['primary'] if self.is_active else colors['text_secondary']
        writeup_title.setStyleSheet(f"color: {title_color}; font-weight: bold;")
        writeup_layout.addWidget(writeup_title)

        # Account details - for inactive: all text uses text_disabled
        # Removed "Name:" since it's redundant with the title
        details = [
            ("Current Balance:", "current_balance"),
            ("Goal Amount:", "goal_amount"),
            ("Goal Remaining:", "goal_remaining"),
            ("Auto-Save Amount:", "auto_save_amount")
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

        # Check if this is the default savings account (cannot be deactivated)
        is_default_save = getattr(self.account, 'is_default_save', False)

        # Create a button that shows current status and toggles on click
        self.active_toggle = QPushButton("Active" if self.is_active else "Inactive")
        self.active_toggle.setCheckable(True)
        self.active_toggle.setChecked(self.is_active)
        self.active_toggle.setFixedHeight(24)
        self.active_toggle.setFixedWidth(80)

        # If default savings account, disable the toggle button
        if is_default_save:
            self.active_toggle.setEnabled(False)
            self.active_toggle.setCursor(Qt.CursorShape.ForbiddenCursor)
            self.active_toggle.setToolTip("Default savings account must always be active")
            # Locked style - no hover effect, slightly muted appearance
            self.active_toggle.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['secondary']};
                    color: {colors['surface']};
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 11px;
                    opacity: 0.8;
                }}
            """)
        else:
            self.active_toggle.clicked.connect(self.on_active_toggle_changed)
            self.active_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
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
            
            # Update account name label (respect inactive status and default save - headers use text_secondary)
            if hasattr(self, 'name_label'):
                is_default_save = getattr(self.account, 'is_default_save', False)
                if not self.is_active:
                    header_color = colors['text_secondary']  # Header uses text_secondary for inactive
                elif is_default_save:
                    header_color = colors['accent']  # Accent for default save
                else:
                    header_color = colors['text_primary']  # Normal for active
                self.name_label.setStyleSheet(f"color: {header_color}; font-weight: bold;")

            # Determine colors based on active status
            label_color = colors['text_secondary'] if self.is_active else colors['text_disabled']

            # Update progress bar labels
            for child in self.findChildren(QLabel):
                if child.text() in ["Goal:", "Auto:", "Auto Save:"]:
                    child.setStyleSheet(f"color: {label_color};")

            # Calculate progress bar colors (muted for inactive - 75% disabled, 25% original)
            if self.is_active:
                goal_bar_color = colors['primary']
                auto_bar_color = colors['accent']
            else:
                goal_bar_color = self.blend_colors(colors['primary'], colors['disabled'], 0.25)
                auto_bar_color = self.blend_colors(colors['accent'], colors['disabled'], 0.25)

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
                        background-color: {goal_bar_color};
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
                        background-color: {auto_bar_color};
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
            
            # Update writeup title (Account Details) - find it among children
            for child in self.findChildren(QLabel):
                if child.text() == "Account Details":
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
                if text.endswith(":") and text not in ["Goal:", "Auto:", "Auto Save:"]:
                    child.setStyleSheet(f"color: {detail_label_color}; font-weight: bold;")

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
            from datetime import timedelta

            history_manager = AccountHistoryManager(self.transaction_manager.db)
            account_history = history_manager.get_account_history(self.account.id, "savings")

            if not account_history:
                # No account history - show "No data" message
                chart_data = {}
                self.balance_chart.update_data(chart_data, "", "")
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
            if hasattr(self.account, '_get_periods_list'):
                activation_periods = self.account._get_periods_list()

            # For inactive accounts, limit the chart to show only up to the last deactivation date
            # This helps avoid showing long flat lines after the account became inactive
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

            # For inactive accounts, use muted chart colors (75% disabled, 25% original)
            custom_colors = None
            custom_axis_color = None
            if not self.is_active:
                colors = theme_manager.get_colors()
                chart_colors = theme_manager.get_chart_colors()
                custom_colors = [self.blend_colors(c, colors['disabled'], 0.25) for c in chart_colors]
                custom_axis_color = colors['text_disabled']  # Muted axis/tick colors

            # Update chart with date on X-axis, running total on Y-axis
            # Pass activation_periods for dashed line visualization during inactive periods
            self.balance_chart.update_data(chart_data, "", "", custom_colors=custom_colors,
                                           custom_axis_color=custom_axis_color,
                                           activation_periods=activation_periods)  # No x/y labels for cleaner look

        except Exception as e:
            print(f"Error updating line chart for {self.account.name}: {e}")
            import traceback
            traceback.print_exc()
            # Show error state
            self.balance_chart.update_data({})
    
    def update_writeup(self):
        """Update the account writeup section"""
        try:
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

    def on_active_toggle_changed(self):
        """Handle activation toggle button click - toggle the current state"""
        from datetime import date

        # Toggle: if currently active, deactivate; if inactive, activate
        new_is_active = not self.is_active
        print(f"[DEBUG] Toggle clicked for {self.account.name}: current={self.is_active}, new={new_is_active}")

        try:
            if new_is_active:
                # Activate the account
                print(f"[DEBUG] Calling activate() for {self.account.name}")
                self.account.activate(start_date=date.today(), db_session=self.transaction_manager.db)
            else:
                # Deactivate the account
                print(f"[DEBUG] Calling deactivate() for {self.account.name}")
                self.account.deactivate(end_date=date.today(), db_session=self.transaction_manager.db)

            # Verify the change took effect
            print(f"[DEBUG] After change: is_currently_active={self.account.is_currently_active}")
            print(f"[DEBUG] Periods: {self.account._get_periods_list()}")

            # Update local state
            self.is_active = new_is_active

            # Emit signal so parent view can refresh the entire view
            print(f"[DEBUG] Emitting activation_changed signal")
            self.activation_changed.emit(self.account, new_is_active)

        except Exception as e:
            print(f"Error changing activation for {self.account.name}: {e}")
            import traceback
            traceback.print_exc()