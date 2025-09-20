"""
Enhanced Dashboard View - Complete layout matching user diagram
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QCheckBox, QPushButton, QGridLayout, QDialog)
from PyQt6.QtCore import Qt
from themes import theme_manager
from widgets import (PieChartWidget, LineChartWidget, BarChartWidget, 
                    ProgressChartWidget, HeatmapWidget, AnimatedGifWidget, HistogramWidget, WeeklySpendingTrendWidget, BoxPlotWidget)
from views.dialogs.account_selector_dialog import AccountSelectorDialog
from views.dialogs.hour_calculator_dialog import HourCalculatorDialog
from views.dialogs.settings_dialog import get_setting
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class RingChartWidget(QWidget):
    """Ring chart widget for account progress display"""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        
        # Create matplotlib figure and canvas with transparent background
        self.figure = Figure(figsize=(1, 1), tight_layout=True)  # Half the size
        self.figure.patch.set_facecolor('none')  # Transparent figure background
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Zero padding around everything
        layout.setSpacing(0)  # No spacing between elements
        
        # NO title inside the widget anymore - will be overlaid externally
        
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        # Make widget background transparent to match program background
        self.setStyleSheet("background: transparent; border: none;")
        
        # Make rings half the size but square for just the ring: 50x50
        self.setFixedSize(50, 50)
        
    def update_data(self, percentage: float, label: str = ""):
        """Update ring chart with percentage data"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Set transparent background for axes
        ax.set_facecolor('none')
        
        # Create ring chart (donut)
        colors = theme_manager.get_colors()
        wedges, texts = ax.pie([percentage, 100-percentage], 
                              colors=[colors['primary'], colors['surface_variant']], 
                              startangle=90, counterclock=False)
        
        # Add center hole to make it a ring - use program background color
        centre_circle = plt.Circle((0,0), 0.60, fc=colors['surface'])
        ax.add_artist(centre_circle)
        
        # NO percentage text - clean ring display only
        # ax.text(0, 0, f'{percentage:.0f}%', ha='center', va='center', 
        #        fontsize=12, fontweight='bold', color=colors['text_primary'])
        
        ax.axis('equal')
        self.canvas.draw()


class SavingsProgressWidget(QWidget):
    """Horizontal progress bars for savings accounts with goal visualization"""
    
    def __init__(self, title: str = "Savings Accounts Progress", parent=None):
        super().__init__(parent)
        self.title = title
        
        self.figure = Figure(figsize=(6, 4), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        
        # Make canvas background transparent
        self.canvas.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        if self.title:
            title_label = QLabel(self.title)
            title_label.setFont(theme_manager.get_font("subtitle"))
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_label)
        
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def update_data(self, accounts_data: list):
        """Update progress bars with savings account data
        
        Args:
            accounts_data: list of Account objects with running_total and goal attributes
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not accounts_data:
            ax.text(0.5, 0.5, 'No savings accounts found', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color=theme_manager.get_color('text_secondary'))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            colors = theme_manager.get_colors()
            
            # Prepare account data
            account_names = [acc.name for acc in accounts_data]
            current_amounts = [acc.running_total for acc in accounts_data]
            goals = [acc.goal_amount for acc in accounts_data]
            
            y_positions = range(len(accounts_data))
            
            # Find max value for x-axis scaling
            max_value = max(max(current_amounts), max(goals) if goals else 0, 1)
            
            # Draw goal backgrounds (shaded regions) for accounts with goals
            for i, (current, goal) in enumerate(zip(current_amounts, goals)):
                if goal > 0:
                    # Draw goal background as a light shaded rectangle
                    ax.barh(i, goal, color=colors['surface_variant'], alpha=0.3, height=0.6, 
                           label='Goal' if i == 0 else "")
            
            # Draw current savings bars (on top of goal backgrounds)
            bars = ax.barh(y_positions, current_amounts, color=colors['primary'], 
                          height=0.6)
            
            
            # Formatting
            ax.set_yticks(y_positions)
            ax.set_yticklabels(account_names)
            ax.set_xlim(0, max_value * 1.1)  # Add some padding
            ax.grid(True, alpha=0.3, axis='x')  # Vertical grid lines only
            
            # Hide x-axis values but keep grid
            ax.set_xticks([])
            ax.set_xlabel('')  # Remove x-axis label
            
            # Apply theme colors - make plot background match theme
            ax.set_facecolor(colors['surface'])
            self.figure.patch.set_facecolor(colors['surface'])
            ax.tick_params(colors=colors['text_primary'])
            ax.xaxis.label.set_color(colors['text_primary'])
            ax.yaxis.label.set_color(colors['text_primary'])
        
        self.canvas.draw()


class StackedAreaWidget(QWidget):
    """Stacked area chart showing category percentages over time"""
    
    def __init__(self, title: str = "Category % per Week", parent=None):
        super().__init__(parent)
        self.title = title
        
        self.figure = Figure(figsize=(6, 4), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = None
        if self.title:
            self.title_label = QLabel(self.title)
            self.title_label.setFont(theme_manager.get_font("subtitle"))
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.title_label)
        
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        # Apply initial theme and connect to theme changes
        self.update_title_styling()
        theme_manager.theme_changed.connect(self.on_theme_changed)
        
    def update_data(self, weekly_data: dict):
        """Update stacked area chart with weekly category percentages"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not weekly_data:
            ax.text(0.5, 0.5, 'No weekly data available', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color=theme_manager.get_color('text_secondary'))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            # Prepare data for stacked area
            weeks = list(weekly_data.keys())
            categories = set()
            for week_data in weekly_data.values():
                categories.update(week_data.keys())
            categories = sorted(list(categories))
            
            # Create percentage matrix
            data_matrix = []
            for category in categories:
                category_percentages = []
                for week in weeks:
                    week_total = sum(weekly_data[week].values()) if weekly_data[week] else 1
                    percentage = (weekly_data[week].get(category, 0) / week_total) * 100
                    category_percentages.append(percentage)
                data_matrix.append(category_percentages)
            
            # Create stacked area chart
            colors = theme_manager.get_chart_colors()[:len(categories)]
            ax.stackplot(range(len(weeks)), *data_matrix, colors=colors, alpha=0.8)
            
            # Remove axis labels (category key serves as legend)
            ax.set_ylim(0, 100)
            ax.set_xlim(0, len(weeks)-1)
            
            # Add week start dates on x-axis
            if weeks:
                week_labels = []
                for week_key in weeks:
                    try:
                        # Extract date from week key and format as M/D/YY
                        if "Week" in week_key:
                            week_labels.append(week_key)
                        else:
                            # Parse date and format as M/D
                            from datetime import datetime
                            week_date = datetime.strptime(week_key, "%Y-%m-%d")
                            week_labels.append(week_date.strftime("%-m/%-d"))
                    except:
                        week_labels.append(week_key)
                
                ax.set_xticks(range(len(weeks)))
                ax.set_xticklabels(week_labels, rotation=45, ha='right', fontsize=9)
            
            # No legend (category key serves as legend)
            ax.grid(True, alpha=0.3, axis='y')
        
        self.apply_theme()
        self.canvas.draw()
    
    def apply_theme(self):
        """Apply current theme to the chart"""
        colors = theme_manager.get_colors()
        self.figure.patch.set_facecolor(colors['surface'])
        
        for ax in self.figure.get_axes():
            ax.set_facecolor(colors['surface'])
            ax.tick_params(colors=colors['text_primary'])
            ax.spines['bottom'].set_color(colors['border'])
            ax.spines['top'].set_color(colors['border'])
            ax.spines['right'].set_color(colors['border'])
            ax.spines['left'].set_color(colors['border'])
            ax.xaxis.label.set_color(colors['text_primary'])
            ax.yaxis.label.set_color(colors['text_primary'])
    
    def update_title_styling(self):
        """Update title label styling with current theme colors"""
        if not self.title_label:
            return
            
        colors = theme_manager.get_colors()
        self.title_label.setStyleSheet(f"""
            QLabel {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 2px 4px;
                margin: 1px;
                color: {colors['text_primary']};
            }}
        """)
    
    def on_theme_changed(self, theme_id):
        """Handle theme change"""
        self.apply_theme()
        self.update_title_styling()
        self.canvas.draw()


class DashboardView(QWidget):
    def __init__(self, transaction_manager=None, analytics_engine=None):
        super().__init__()
        self.transaction_manager = transaction_manager
        self.analytics_engine = analytics_engine
        
        # Analytics toggle - load from settings
        from views.dialogs.settings_dialog import get_setting
        self.include_analytics_only = get_setting("default_analytics_only", True)
        self.time_frame_filter = get_setting("time_frame_filter", "All Time")
        
        # Track selected accounts for savings rate plots
        self.selected_accounts = [None, None]  # For the two savings rate charts
        
        # Chart widgets
        self.total_pie_chart = None
        self.weekly_pie_chart = None
        self.stacked_area_chart = None
        self.savings_line_charts = []
        self.ring_charts = []
        self.heatmap_chart = None
        self.gif_widget = None
        self.savings_progress_chart = None
        self.purchase_histogram = None
        self.weekly_trend_chart = None
        self.category_boxplot = None
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(1)  # Ultra minimal spacing for cluttered dashboard feel
        main_layout.setContentsMargins(2, 2, 2, 2)  # Minimal margins
        
        # Header section
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        # Title
        title = QLabel("💰 Financial Control Panel")
        title.setFont(theme_manager.get_font("title"))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Analytics toggle
        self.analytics_toggle = QCheckBox("Normal Spending Only")
        self.analytics_toggle.setChecked(self.include_analytics_only)  # Use setting from file
        self.analytics_toggle.toggled.connect(self.toggle_analytics_mode)
        self.analytics_toggle.setToolTip("Filter abnormal transactions from analytics")
        header_layout.addWidget(self.analytics_toggle)
        
        main_layout.addLayout(header_layout)
        
        # TOP ROW - Pie charts | Category Key | Week | Accounts | Bills | [Calc] + Chart areas
        top_row = QHBoxLayout()
        top_row.setSpacing(5)
        top_row.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Pie charts section with overlapped positioning
        pie_charts_container = QWidget()
        pie_charts_container.setFixedSize(160, 160)
        
        # Total spending pie chart (larger, positioned upper-right)
        self.total_pie_chart = PieChartWidget("")
        self.total_pie_chart.setParent(pie_charts_container)
        self.total_pie_chart.setGeometry(50, 0, 110, 110)  # x, y, w, h
        
        # Weekly spending pie chart (smaller, positioned lower-left) 
        self.weekly_pie_chart = PieChartWidget("", transparent_background=True)
        self.weekly_pie_chart.setParent(pie_charts_container)
        self.weekly_pie_chart.setGeometry(0, 70, 80, 80)  # x, y, w, h
        
        top_row.addWidget(pie_charts_container)
        
        # Category key
        self.category_key_frame = self.create_category_key()
        top_row.addWidget(self.category_key_frame)
        
        # Middle section with cards and chart area - takes more space
        middle_section = QVBoxLayout()
        
        # Cards row (Week, Accounts, Bills) - dynamic height, top aligned
        cards_row = QHBoxLayout()
        cards_row.setSpacing(3)
        cards_row.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Week status card - dynamic height
        weekly_status_card = self.create_dynamic_card("Week:", "weekly_status")
        cards_row.addWidget(weekly_status_card)
        
        # Accounts card - dynamic height  
        account_summary_card = self.create_dynamic_card("Accounts:", "account_summary")
        cards_row.addWidget(account_summary_card)
        
        # Bills card - dynamic height
        bills_status_card = self.create_dynamic_card("Bills:", "bills_status")
        cards_row.addWidget(bills_status_card)
        
        middle_section.addLayout(cards_row)
        
        # Category box plot chart area - expand to fill available space
        self.category_boxplot = BoxPlotWidget("")
        self.category_boxplot.setMinimumHeight(80)  # Larger minimum to fill space
        self.category_boxplot.setMaximumHeight(120)  # Allow more expansion
        middle_section.addWidget(self.category_boxplot, 1)  # Give it stretch to fill space
        
        # Give middle section more space (stretch factor 3)
        top_row.addLayout(middle_section, 3)
        
        # Right section with calculator and stacked chart areas - smaller
        right_section = QVBoxLayout()
        right_section.setSpacing(2)  # Tighter spacing to give more room to charts
        
        # Hour calculator button at top - full width, accent color
        self.hour_calc_button = QPushButton("💼 Hour Calculator\nFor $50/h I need 0.0 hours")
        self.hour_calc_button.setMinimumHeight(50)  # Taller for two-line text
        self.hour_calc_button.clicked.connect(self.open_hour_calculator_popup)
        self.hour_calc_button.setCursor(Qt.CursorShape.PointingHandCursor)
        # Apply accent color styling - will be updated in apply_button_theme()
        right_section.addWidget(self.hour_calc_button)
        
        # Weekly spending trend chart - match histogram height
        self.weekly_trend_chart = WeeklySpendingTrendWidget("")
        self.weekly_trend_chart.setMinimumHeight(80)  # Same as histogram
        self.weekly_trend_chart.setMaximumHeight(120)  # Same as histogram
        right_section.addWidget(self.weekly_trend_chart)
        
        # Purchase size histogram - give it more space
        self.purchase_histogram = HistogramWidget("")
        self.purchase_histogram.setMinimumHeight(80)  # Ensure minimum height
        self.purchase_histogram.setMaximumHeight(120)  # Allow more height
        right_section.addWidget(self.purchase_histogram, 1)  # Give it stretch priority
        
        # Give right section less space (stretch factor 1)
        top_row.addLayout(right_section, 1)
        
        main_layout.addLayout(top_row)
        
        # THIRD ROW - Stacked area chart | Two line plots for savings
        middle_row = QHBoxLayout()
        middle_row.setSpacing(0)  # Remove spacing between stacked and savings charts
        
        # Stacked percentage plot
        self.stacked_area_chart = StackedAreaWidget("Category % per Week")
        self.stacked_area_chart.setMinimumHeight(300)  # Increased by 50%
        middle_row.addWidget(self.stacked_area_chart)
        
        # Savings tracking line plots
        savings_container = QVBoxLayout()
        savings_container.setSpacing(0)  # Remove spacing between savings charts
        savings_container.setContentsMargins(0, 0, 0, 0)  # Remove margins
        for i in range(2):
            line_chart = LineChartWidget(f"Savings Rate {i+1}")
            line_chart.setMinimumHeight(142)  # Increased by 50%
            line_chart.setMaximumHeight(142)  # Increased by 50%
            
            # Connect title click signal
            line_chart.title_clicked.connect(lambda idx=i: self.on_savings_chart_clicked(idx))
            
            self.savings_line_charts.append(line_chart)
            savings_container.addWidget(line_chart)
        
        middle_row.addLayout(savings_container)
        
        main_layout.addLayout(middle_row)
        
        # BOTTOM ROW - Ring charts above heatmap | GIF | Histogram
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(2)  # Tighter spacing for cluttered dashboard feel
        
        # Left section: Rings above heatmap
        rings_heatmap_container = QVBoxLayout()
        rings_heatmap_container.setSpacing(0)  # Ultra tight spacing between rings and heatmap
        rings_heatmap_container.setContentsMargins(0, 0, 0, 0)  # Remove all margins
        
        # Dynamic ring charts based on bills (max 4, show available bills)
        self.rings_section = QWidget()
        self.rings_section.setFixedHeight(65)  # Fixed height for title + ring
        self.rings_section.setStyleSheet("background: transparent;")
        rings_heatmap_container.addWidget(self.rings_section)
        
        # Store references for updating
        self.ring_titles = []
        
        # Initialize with bill data
        self.setup_bill_rings()
        
        # Day/Category heatmap (bottom, wider to span under all 3 rings)
        self.heatmap_chart = HeatmapWidget("")  # No title
        self.heatmap_chart.setMinimumWidth(300)  # Wider to span under rings
        self.heatmap_chart.setMinimumHeight(200)  # Taller to show all categories
        self.heatmap_chart.setMaximumHeight(300)  # Allow it to be even taller
        rings_heatmap_container.addWidget(self.heatmap_chart)
        
        bottom_row.addLayout(rings_heatmap_container)
        
        # Central GIF holder
        self.gif_widget = AnimatedGifWidget("dashboard", (150, 100))
        bottom_row.addWidget(self.gif_widget)
        
        # Savings progress bars
        self.savings_progress_chart = SavingsProgressWidget("Savings Goals")
        self.savings_progress_chart.setMinimumWidth(150)
        self.savings_progress_chart.setMaximumHeight(200)  # Increased for more space
        bottom_row.addWidget(self.savings_progress_chart)
        
        main_layout.addLayout(bottom_row)
        
        self.setLayout(main_layout)
        
        # Initial refresh to populate data and auto-select for line charts
        if self.transaction_manager and self.analytics_engine:
            self.refresh()
        
        # Apply theme to hour calculator button
        self.apply_hour_calc_button_theme()
        
    def create_category_key(self):
        """Create category color key frame"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setMinimumWidth(140)  # Even wider to fit text
        frame.setMinimumHeight(250)  # Much taller to show all categories
        frame.setMaximumHeight(300)  # Allow it to be tall
        
        colors = theme_manager.get_colors()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                margin: 2px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(5, 5, 5, 5)
        
        key_title = QLabel("Categories")
        key_title.setFont(theme_manager.get_font("subtitle"))  # Bigger header
        key_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        key_title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 3px;")
        layout.addWidget(key_title)
        
        # Category key will be populated in refresh
        self.category_key_layout = QVBoxLayout()
        self.category_key_layout.setSpacing(2)
        layout.addLayout(self.category_key_layout)
        # No stretch - let it fill the space
        
        frame.setLayout(layout)
        return frame
        
    def create_dynamic_card(self, title: str, content_type: str, fixed_lines: int = None, fixed_height: bool = False):
        """Create a dynamic sizing card for metrics display"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        
        # Truly dynamic height like hanging tickets - each card independent
        frame.setMinimumHeight(40)  # Minimal height, let content drive it
        frame.setMinimumWidth(120)
        # No maximum height or width constraints - completely independent sizing
        
        if fixed_lines:
            frame.setMaximumWidth(150)  # Slightly wider for more content
        
        colors = theme_manager.get_colors()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                margin: 1px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(3)  # Reduced spacing
        layout.setContentsMargins(5, 3, 5, 3)  # Reduced margins
        
        # Title - bigger header 
        title_label = QLabel(title)
        title_label.setFont(theme_manager.get_font("subtitle"))  # Bigger font
        title_label.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        layout.addWidget(title_label)
        
        # Content label - dynamic height
        content_label = QLabel("Loading...")
        content_label.setFont(theme_manager.get_font("monospace"))
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_label.setStyleSheet(f"color: {colors['text_primary']}; padding: 2px;")
        layout.addWidget(content_label)
        
        frame.setLayout(layout)
        
        # Store reference for updating
        setattr(self, f"{content_type}_label", content_label)
        
        return frame
        
    def create_placeholder_chart(self, title: str):
        """Create placeholder chart area"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setMinimumHeight(100)
        frame.setMaximumHeight(100)
        
        colors = theme_manager.get_colors()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface_variant']};
                border: 2px dashed {colors['primary']};
                border-radius: 4px;
                margin: 2px;
            }}
        """)
        
        layout = QVBoxLayout()
        placeholder_label = QLabel(f"💡 {title}")
        placeholder_label.setFont(theme_manager.get_font("small"))
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet(f"""
            QLabel {{
                color: {colors['primary']};
                font-style: italic;
            }}
        """)
        layout.addWidget(placeholder_label)
        frame.setLayout(layout)
        
        return frame
        
    def toggle_analytics_mode(self, checked):
        """Toggle between normal and all spending analytics"""
        self.include_analytics_only = checked
        self.refresh()

    def apply_time_frame_filter(self, transactions):
        """Apply time frame filtering to a list of transactions"""
        if self.time_frame_filter == "All Time":
            return transactions

        from datetime import datetime, timedelta
        today = datetime.now().date()

        if self.time_frame_filter == "Last Year":
            cutoff_date = today - timedelta(days=365)
            return [t for t in transactions if t.date >= cutoff_date]

        elif self.time_frame_filter == "Last Month":
            cutoff_date = today - timedelta(days=30)
            return [t for t in transactions if t.date >= cutoff_date]

        elif self.time_frame_filter == "Last 20 Entries":
            # Sort by date descending and take first 20
            sorted_transactions = sorted(transactions, key=lambda t: t.date, reverse=True)
            return sorted_transactions[:20]

        return transactions

    def get_filtered_spending_transactions(self):
        """Get spending transactions with analytics, time, and rollover filtering applied"""
        transactions = self.transaction_manager.get_spending_transactions(self.include_analytics_only)

        # Filter out rollover transactions (category = "Rollover" or description contains "rollover")
        filtered_transactions = []
        for t in transactions:
            is_rollover = (
                (hasattr(t, 'category') and t.category and t.category.lower() == 'rollover') or
                (hasattr(t, 'description') and t.description and 'rollover' in t.description.lower())
            )
            if not is_rollover:
                filtered_transactions.append(t)

        return self.apply_time_frame_filter(filtered_transactions)

    def calculate_category_spending_from_filtered(self):
        """Calculate category spending totals from filtered transactions"""
        transactions = self.get_filtered_spending_transactions()
        transactions = [t for t in transactions if t.amount > 0]  # Exclude placeholder transactions

        category_totals = {}
        for transaction in transactions:
            category = getattr(transaction, 'category', 'Miscellaneous') or 'Miscellaneous'
            category_totals[category] = category_totals.get(category, 0.0) + float(transaction.amount)

        return category_totals
    
    def apply_hour_calc_button_theme(self):
        """Apply accent color theme to hour calculator button"""
        colors = theme_manager.get_colors()
        accent_color = colors.get('primary', colors['primary'])  # Use primary as accent
        text_color = colors.get('background', colors['background'])  # Contrasting background color
        
        self.hour_calc_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: {text_color};
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                padding: 8px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(accent_color, 1.1)};
            }}
            QPushButton:pressed {{
                background-color: {self.lighten_color(accent_color, 0.9)};
            }}
        """)
    
    def lighten_color(self, color: str, factor: float) -> str:
        """Lighten or darken a hex color by a factor"""
        try:
            # Remove '#' if present
            color = color.lstrip('#')
            
            # Convert to RGB
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            
            # Apply factor
            new_rgb = tuple(min(255, max(0, int(c * factor))) for c in rgb)
            
            # Convert back to hex
            return f"#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}"
        except:
            return color  # Return original if conversion fails
    
    def update_hour_calc_display(self, target_amount: float = None, hourly_rate: float = 50.0):
        """Update hour calculator button display with calculation"""
        if target_amount is None:
            # Calculate target amount based on remaining weekly budget
            try:
                from datetime import datetime, timedelta
                today = datetime.now()
                week_start = today - timedelta(days=today.weekday())
                days_left_in_week = 7 - (today.weekday() + 1)
                
                # Get current week spending using analytics and rollover filtering (ignore time frame)
                spending_transactions = self.transaction_manager.get_spending_transactions(self.include_analytics_only)

                # Filter out rollover transactions and get current week data
                current_week_spending = []
                for t in spending_transactions:
                    if (t.amount > 0 and  # Exclude placeholder transactions
                        t.date >= week_start.date()):
                        # Check if it's a rollover transaction
                        is_rollover = (
                            (hasattr(t, 'category') and t.category and t.category.lower() == 'rollover') or
                            (hasattr(t, 'description') and t.description and 'rollover' in t.description.lower())
                        )
                        if not is_rollover:
                            current_week_spending.append(t)
                
                week_spent = sum(t.amount for t in current_week_spending)
                
                # Estimate weekly budget
                income_summary = self.transaction_manager.get_income_vs_spending_summary()
                estimated_weekly_budget = income_summary.get('total_income', 400) / 4
                week_remaining = max(0, estimated_weekly_budget - week_spent)
                
                target_amount = week_remaining
            except:
                target_amount = 100.0  # Default target
        
        # Calculate hours needed
        hours_needed = target_amount / hourly_rate if hourly_rate > 0 else 0
        
        # Update button text
        self.hour_calc_button.setText(f"💼 Hour Calculator\nFor ${hourly_rate:.0f}/h I need {hours_needed:.1f} hours")
    
    def open_hour_calculator_popup(self):
        """Open hour calculator dialog"""
        try:
            dialog = HourCalculatorDialog(self.transaction_manager, self)
            dialog.exec()
        except Exception as e:
            print(f"Error opening hour calculator dialog: {e}")
    
    def refresh(self):
        """Refresh all dashboard data and charts"""
        if not self.transaction_manager or not self.analytics_engine:
            self.set_error_state("Services not available")
            return

        try:
            # Reload settings from file (in case they changed)
            from views.dialogs.settings_dialog import get_setting
            self.time_frame_filter = get_setting("time_frame_filter", "All Time")
            # Update all sections
            self.update_accounts_display()
            self.update_weekly_status()
            self.update_bills_status()
            self.update_category_key()
            self.update_pie_charts()
            self.update_stacked_area_chart()
            self.update_savings_line_charts()
            self.update_ring_charts()
            self.update_heatmap()
            self.update_savings_progress()
            self.update_purchase_histogram()
            self.update_weekly_spending_trends()
            self.update_category_boxplot()
            self.update_hour_calc_display()
            
        except Exception as e:
            error_msg = f"Error refreshing dashboard: {str(e)}"
            print(error_msg)
            self.set_error_state(error_msg)
    
    def set_error_state(self, error_msg: str):
        """Set all display areas to show error message"""
        if hasattr(self, 'account_summary_label'):
            self.account_summary_label.setText(error_msg)
        if hasattr(self, 'weekly_status_label'):
            self.weekly_status_label.setText(error_msg)
        if hasattr(self, 'bills_status_label'):
            self.bills_status_label.setText(error_msg)
    
    def update_accounts_display(self):
        """Update account summary display"""
        try:
            accounts = self.transaction_manager.get_all_accounts()
            
            if not accounts:
                self.account_summary_label.setText("No accounts found")
                return
            
            account_text = ""
            
            for account in accounts:  # Show all accounts
                name = account.name[:14] + "..." if len(account.name) > 14 else account.name
                # Right-align numbers for table-like appearance
                amount_str = f"${account.running_total:,.0f}"
                account_text += f"{name:<16} {amount_str:>10}\n"
            
            # No total line as requested
            self.account_summary_label.setText(account_text.rstrip())
            
        except Exception as e:
            self.account_summary_label.setText(f"Error: {e}")
    
    def update_weekly_status(self):
        """Update weekly status display with current week tracking"""
        try:
            from datetime import datetime, timedelta
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())  # Monday of current week
            days_into_week = today.weekday() + 1  # 1-7 (Monday = 1)
            days_left_in_week = 7 - days_into_week
            
            # Get current week transactions using analytics and rollover filtering (ignore time frame)
            spending_transactions = self.transaction_manager.get_spending_transactions(self.include_analytics_only)

            # Filter out rollover transactions and get current week data
            current_week_spending = []
            for t in spending_transactions:
                if (t.amount > 0 and  # Exclude placeholder transactions
                    t.date >= week_start.date()):
                    # Check if it's a rollover transaction
                    is_rollover = (
                        (hasattr(t, 'category') and t.category and t.category.lower() == 'rollover') or
                        (hasattr(t, 'description') and t.description and 'rollover' in t.description.lower())
                    )
                    if not is_rollover:
                        current_week_spending.append(t)
            
            # Calculate week spending total
            week_spent = sum(t.amount for t in current_week_spending)
            
            # Get weekly budget/allowance (try to get from paycheck processing or use default)
            try:
                # Try to get weekly spending allowance from recent paycheck
                income_summary = self.transaction_manager.get_income_vs_spending_summary()
                # Estimate weekly budget as 1/4 of total spending capability
                estimated_weekly_budget = income_summary.get('total_income', 400) / 4
            except:
                estimated_weekly_budget = 200  # Default weekly budget
            
            week_started = estimated_weekly_budget
            week_remaining = max(0, week_started - week_spent)
            
            # Calculate daily remaining
            if days_left_in_week > 0:
                daily_remaining = week_remaining / days_left_in_week
            else:
                daily_remaining = 0
            
            # Format the display
            status_text = f"Started: ${week_started:.0f}\n"
            status_text += f"Spent: ${week_spent:.0f}\n"
            status_text += f"Remaining: ${week_remaining:.0f}\n"
            if days_left_in_week > 0:
                status_text += f"Daily: ${daily_remaining:.0f}"
            else:
                status_text += "Week done"
            
            self.weekly_status_label.setText(status_text)
            
        except Exception as e:
            self.weekly_status_label.setText(f"Error: {e}")
    
    def update_bills_status(self):
        """Update bills status display"""
        try:
            bills = self.transaction_manager.get_all_bills()
            
            if not bills:
                self.bills_status_label.setText("No bills configured")
                return
            
            bills_text = ""
            
            for bill in bills:  # Show all bills
                name = bill.name[:14] + "..." if len(bill.name) > 14 else bill.name
                # Right-align numbers for table-like appearance
                amount_str = f"${bill.running_total:.0f}"
                bills_text += f"{name:<16} {amount_str:>10}\n"
            
            # Remove total line to keep it clean
            self.bills_status_label.setText(bills_text.rstrip())
            
        except Exception as e:
            self.bills_status_label.setText(f"Error: {e}")
    
    def update_category_key(self):
        """Update category color key"""
        try:
            # Clear existing items
            for i in reversed(range(self.category_key_layout.count())):
                self.category_key_layout.itemAt(i).widget().setParent(None)
            
            # Get categories from actual transaction data
            categories = self.analytics_engine.get_all_categories()
            colors = theme_manager.get_chart_colors()

            # Get theme colors for proper text display
            theme_colors = theme_manager.get_colors()

            # Only show categories if there are actual transactions
            if not categories:
                # Show empty state message
                empty_label = QLabel(f"<span style='color: {theme_colors['text_secondary']}; font-style: italic; font-size: 11px;'>No categories yet</span>")
                empty_label.setStyleSheet(f"padding: 10px; text-align: center;")
                self.category_key_layout.addWidget(empty_label)
                return

            for i, category in enumerate(categories):  # Show actual categories
                color = colors[i % len(colors)]  # Chart color for the bullet
                
                text_color = theme_colors['text_primary']
                key_item = QLabel(f"<span style='color: {color}; font-weight: bold;'>●</span> <span style='color: {text_color}; font-size: 11px;'>{category}</span>")
                key_item.setStyleSheet(f"padding: 2px; background: transparent;")
                self.category_key_layout.addWidget(key_item)
                
        except Exception as e:
            print(f"Error updating category key: {e}")
    
    def update_pie_charts(self):
        """Update both pie charts with different data sources"""
        try:
            # Get spending data by category for the big pie chart (respects time filtering)
            all_time_category_spending = self.calculate_category_spending_from_filtered()
            
            # Update total spending pie chart with filtered data
            if self.total_pie_chart and all_time_category_spending:
                chart_title = f"Spending by Category ({self.time_frame_filter})"
                self.total_pie_chart.update_data(all_time_category_spending, chart_title)
            
            # Get CURRENT WEEK spending data for the small pie chart
            from datetime import datetime, timedelta
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())  # Monday of current week

            # Get spending transactions using ONLY analytics filtering (ignore time frame for current week)
            spending_transactions = self.transaction_manager.get_spending_transactions(self.include_analytics_only)

            # Filter out rollover transactions and get current week data
            current_week_transactions = []
            for t in spending_transactions:
                if (t.amount > 0 and  # Exclude placeholder transactions
                    t.date >= week_start.date()):
                    # Check if it's a rollover transaction
                    is_rollover = (
                        (hasattr(t, 'category') and t.category and t.category.lower() == 'rollover') or
                        (hasattr(t, 'description') and t.description and 'rollover' in t.description.lower())
                    )
                    if not is_rollover:
                        current_week_transactions.append(t)
            
            # Calculate current week category spending
            weekly_category_spending = {}
            for transaction in current_week_transactions:
                category = getattr(transaction, 'category', 'Miscellaneous') or 'Miscellaneous'
                weekly_category_spending[category] = weekly_category_spending.get(category, 0) + transaction.amount
            
            # Update weekly pie chart (current week only)
            if self.weekly_pie_chart:
                if weekly_category_spending:
                    print(f"Current week spending data: {weekly_category_spending}")
                    self.weekly_pie_chart.update_data(weekly_category_spending, "This Week Spending")
                else:
                    # No spending this week - show greyed out empty chart
                    print(f"No current week spending found. Week start: {week_start.date()}, Today: {today.date()}")
                    self.weekly_pie_chart.update_data({}, "This Week Spending")
                
        except Exception as e:
            print(f"Error updating pie charts: {e}")
    
    def update_stacked_area_chart(self):
        """Update stacked area chart with real weekly category percentages"""
        try:
            from datetime import datetime, timedelta
            
            # Get spending transactions using proper filtering
            spending_transactions = self.get_filtered_spending_transactions()
            spending_transactions = [
                t for t in spending_transactions
                if t.amount > 0  # Exclude $0 placeholder transactions
            ]
            
            if not spending_transactions:
                # No data available - show empty chart
                if self.stacked_area_chart:
                    self.stacked_area_chart.update_data({})
                return
            
            # Group transactions by week (Monday-Sunday)
            weekly_data = {}
            for transaction in spending_transactions:
                # Get Monday of transaction's week
                transaction_date = transaction.date if hasattr(transaction.date, 'weekday') else datetime.strptime(str(transaction.date), "%Y-%m-%d")
                monday = transaction_date - timedelta(days=transaction_date.weekday())
                week_key = monday.strftime("%Y-%m-%d")  # Use Monday date as key
                
                if week_key not in weekly_data:
                    weekly_data[week_key] = {}
                
                category = getattr(transaction, 'category', 'Miscellaneous') or 'Miscellaneous'
                weekly_data[week_key][category] = weekly_data[week_key].get(category, 0) + transaction.amount
            
            # Sort weeks chronologically and take last 8 weeks
            sorted_weeks = sorted(weekly_data.keys())[-8:]
            filtered_weekly_data = {week: weekly_data[week] for week in sorted_weeks}
            
            if self.stacked_area_chart:
                self.stacked_area_chart.update_data(filtered_weekly_data)
                
        except Exception as e:
            print(f"Error updating stacked area chart: {e}")
            import traceback
            traceback.print_exc()
    
    def update_savings_line_charts(self):
        """Update savings tracking line charts"""
        try:
            # These charts are clickable and show account/bill running totals when selected
            # Default to showing random accounts/bills if nothing selected
            import random
            
            for i, chart in enumerate(self.savings_line_charts):
                if chart:
                    # Check if an account/bill has been selected for this chart
                    if i < len(self.selected_accounts) and self.selected_accounts[i] is not None:
                        # Chart will be updated by update_single_savings_chart when account is selected
                        self.update_single_savings_chart(i)
                    else:
                        # No account selected - auto-select a random account or bill
                        self.auto_select_random_for_chart(i)
                    
        except Exception as e:
            print(f"Error updating savings line charts: {e}")
    
    def update_ring_charts(self):
        """Update ring charts showing account progress"""
        try:
            # Get all bills from database (rings now represent bills)
            bills = self.transaction_manager.get_all_bills()
            
            # Update each ring with bill progress (running_total / typical_amount)
            for i, ring_chart in enumerate(self.ring_charts):
                if i < len(bills):
                    bill = bills[i]
                    
                    if bill.typical_amount > 0:
                        # Calculate bill progress: current running total / typical payment amount
                        percentage = min(100, (bill.running_total / bill.typical_amount) * 100)
                    else:
                        percentage = 0  # No typical amount set
                    
                    ring_chart.update_data(percentage, bill.name)
                else:
                    # This shouldn't happen with our dynamic setup, but just in case
                    ring_chart.update_data(0, f"Bill {i+1}")
                    
        except Exception as e:
            print(f"Error updating bill ring charts: {e}")
    
    def update_heatmap(self):
        """Update day/category heatmap with real data - average spending by day of week and category"""
        try:
            # Get spending transactions using proper filtering
            spending_transactions = self.get_filtered_spending_transactions()
            
            # Initialize data structure for day/category averages
            from collections import defaultdict
            import calendar
            
            # Dict structure: {category: {day_of_week: [amounts]}}
            category_day_amounts = defaultdict(lambda: defaultdict(list))
            
            # Process all spending transactions
            for transaction in spending_transactions:
                if transaction.category and transaction.date:
                    category = transaction.category.strip()
                    day_of_week = transaction.date.weekday()  # 0=Monday, 6=Sunday
                    amount = float(transaction.amount)
                    
                    category_day_amounts[category][day_of_week].append(amount)
            
            # Calculate averages for each category and day
            heatmap_data = {}
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            for category, day_data in category_day_amounts.items():
                daily_averages = []
                for day_idx in range(7):  # Monday=0 to Sunday=6
                    amounts = day_data.get(day_idx, [])
                    if amounts:
                        avg_amount = sum(amounts) / len(amounts)
                        daily_averages.append(avg_amount)
                    else:
                        daily_averages.append(0.0)  # No data for this day
                
                heatmap_data[category] = daily_averages
            
            # Only show data if we have any transactions
            if heatmap_data and self.heatmap_chart:
                self.heatmap_chart.update_data(heatmap_data, "Day", "Category")
            elif self.heatmap_chart:
                # Show empty state message if no data
                self.heatmap_chart.update_data({}, "Day", "Category")
                
        except Exception as e:
            print(f"Error updating heatmap: {e}")
    
    def update_savings_progress(self):
        """Update savings progress chart with real account data"""
        try:
            # Get all savings accounts from database
            accounts = self.transaction_manager.get_all_accounts()
            
            if self.savings_progress_chart:
                self.savings_progress_chart.update_data(accounts)
                
        except Exception as e:
            print(f"Error updating savings progress: {e}")
    
    def update_purchase_histogram(self):
        """Update purchase size histogram with spending transaction amounts"""
        try:
            # Get spending transactions using proper filtering
            spending_transactions = self.get_filtered_spending_transactions()
            spending_transactions = [
                t for t in spending_transactions
                if t.amount > 0  # Exclude placeholder transactions
            ]
            
            if not spending_transactions:
                # No spending data - show empty histogram
                if self.purchase_histogram:
                    self.purchase_histogram.update_data([])
                return
            
            # Extract purchase amounts
            purchase_amounts = [float(t.amount) for t in spending_transactions if t.amount > 0]
            
            if purchase_amounts and self.purchase_histogram:
                # Update histogram with 10 buckets by default
                self.purchase_histogram.update_data(purchase_amounts, num_buckets=10)
            elif self.purchase_histogram:
                # No valid amounts - show empty
                self.purchase_histogram.update_data([])
                
        except Exception as e:
            print(f"Error updating purchase histogram: {e}")
    
    def update_weekly_spending_trends(self):
        """Update weekly spending trend chart with daily spending by week"""
        try:
            # Get spending transactions using proper filtering
            spending_transactions = self.get_filtered_spending_transactions()
            spending_transactions = [
                t for t in spending_transactions
                if t.amount > 0  # Exclude placeholder transactions
            ]
            
            if not spending_transactions:
                if self.weekly_trend_chart:
                    self.weekly_trend_chart.update_data({})
                return
            
            # Group transactions by week
            from datetime import datetime, timedelta
            from collections import defaultdict
            
            weekly_daily_totals = defaultdict(lambda: [0.0] * 7)  # 7 days per week
            
            for transaction in spending_transactions:
                # Get the transaction date
                if hasattr(transaction.date, 'weekday'):
                    trans_date = transaction.date
                else:
                    trans_date = datetime.strptime(str(transaction.date), "%Y-%m-%d").date()
                
                # Get Monday of this transaction's week
                monday = trans_date - timedelta(days=trans_date.weekday())
                week_key = monday.strftime("%Y-%m-%d")
                
                # Get day of week (0=Monday, 6=Sunday)
                day_of_week = trans_date.weekday()
                
                # Add amount to the appropriate day
                weekly_daily_totals[week_key][day_of_week] += float(transaction.amount)
            
            # Keep only recent weeks (last 8-12 weeks for good cloud effect)
            sorted_weeks = sorted(weekly_daily_totals.keys())[-10:]  # Last 10 weeks
            recent_weekly_data = {week: weekly_daily_totals[week] for week in sorted_weeks}
            
            if self.weekly_trend_chart:
                self.weekly_trend_chart.update_data(recent_weekly_data)
                
        except Exception as e:
            print(f"Error updating weekly spending trends: {e}")
    
    def update_category_boxplot(self):
        """Update category box plot with spending distributions by category"""
        try:
            # Get spending transactions using proper filtering
            spending_transactions = self.get_filtered_spending_transactions()
            spending_transactions = [
                t for t in spending_transactions
                if t.amount > 0  # Exclude placeholder transactions
            ]
            
            if not spending_transactions:
                if self.category_boxplot:
                    self.category_boxplot.update_data({})
                return
            
            # Group spending amounts by category
            from collections import defaultdict
            category_amounts = defaultdict(list)
            
            for transaction in spending_transactions:
                category = getattr(transaction, 'category', 'Miscellaneous') or 'Miscellaneous'
                amount = float(transaction.amount)
                if amount > 0:  # Only positive amounts
                    category_amounts[category].append(amount)
            
            # Convert to dict for the widget
            category_data = dict(category_amounts)
            
            if self.category_boxplot:
                self.category_boxplot.update_data(category_data)
                
        except Exception as e:
            print(f"Error updating category box plot: {e}")
    
    def on_theme_changed(self, theme_id):
        """Handle theme change for dashboard - optimized for performance"""
        try:
            # Update UI element styling (fast)
            self.update_frame_styling()
            self.apply_hour_calc_button_theme()
            
            # Update visual theme elements without recalculating data
            self.update_category_key()  # Only updates colors, not data
            
            # Force chart theme updates - they need to redraw with new colors
            self.update_chart_themes_only()
            
        except Exception as e:
            print(f"Error applying theme to dashboard: {e}")
    
    def update_chart_themes_only(self):
        """Update only chart colors/themes without recalculating data - performance optimized"""
        try:
            # Force pie charts to update themes (they need explicit refresh)
            if hasattr(self, 'total_pie_chart') and self.total_pie_chart:
                self.update_pie_charts()  # This will update both pie charts
            
            # Force ring charts to update themes
            if hasattr(self, 'ring_charts') or hasattr(self, 'rings_section'):
                self.update_ring_charts()  # Update the bill ring charts
                
            # Force matplotlib-based charts to update with current data but new theme colors
            if hasattr(self, 'stacked_area_chart') and self.stacked_area_chart:
                self.update_stacked_area_chart()
                
            if hasattr(self, 'heatmap_chart') and self.heatmap_chart:
                self.update_heatmap()
                
            if hasattr(self, 'savings_line_charts'):
                self.update_savings_line_charts()
                
            if hasattr(self, 'purchase_histogram') and self.purchase_histogram:
                self.update_purchase_histogram()
                
            if hasattr(self, 'weekly_trend_chart') and self.weekly_trend_chart:
                self.update_weekly_spending_trends()
                
            if hasattr(self, 'savings_progress_chart') and self.savings_progress_chart:
                self.update_savings_progress()
                
            if hasattr(self, 'category_boxplot') and self.category_boxplot:
                self.update_category_boxplot()
                
        except Exception as e:
            print(f"Error updating chart themes: {e}")
    
    def update_frame_styling(self):
        """Update styling of all UI frames to match current theme"""
        colors = theme_manager.get_colors()
        
        # Update category key frame styling
        if hasattr(self, 'category_key_frame'):
            self.category_key_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    margin: 2px;
                }}
            """)
            
            # Update category key header title
            for child in self.category_key_frame.findChildren(QLabel):
                if child.text() == "Categories":  # This is the header
                    child.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 3px;")
        
        # Update card frames styling - find all dynamic cards
        for attr_name in ['weekly_status_label', 'account_summary_label', 'bills_status_label']:
            if hasattr(self, attr_name):
                label = getattr(self, attr_name)
                # Get the parent frame (card)
                card_frame = label.parent()
                if card_frame:
                    card_frame.setStyleSheet(f"""
                        QFrame {{
                            background-color: {colors['surface']};
                            border: 1px solid {colors['border']};
                            border-radius: 4px;
                            margin: 1px;
                        }}
                    """)
                    
                    # Update the title label in the card
                    for child in card_frame.findChildren(type(label)):
                        if child != label:  # This is likely the title label
                            child.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
                    
                    # Update the content label styling
                    label.setStyleSheet(f"color: {colors['text_primary']}; padding: 2px;")
    
    def setup_bill_rings(self):
        """Setup dynamic bill rings based on available bills"""
        try:
            # Get all bills from database
            bills = self.transaction_manager.get_all_bills()
            
            # Limit to max 7 rings to better utilize space
            max_rings = 7
            bills_to_show = bills[:max_rings]
            
            # Clear existing rings
            self.ring_charts = []
            self.ring_titles = []
            
            # Clear the rings section
            if hasattr(self.rings_section, 'layout') and self.rings_section.layout():
                QWidget().setLayout(self.rings_section.layout())
            
            # Create new layout for rings section
            rings_layout = QHBoxLayout(self.rings_section)
            rings_layout.setContentsMargins(0, 0, 0, 0)
            rings_layout.setSpacing(5)  # Small spacing between ring groups
            
            # Create rings for each bill
            for bill in bills_to_show:
                # Create container for title + ring
                ring_container = QWidget()
                ring_container.setFixedSize(70, 65)  # Width for title, height for title + ring
                ring_container.setStyleSheet("background: transparent;")
                
                # Create absolute positioning layout
                ring_container_layout = QVBoxLayout(ring_container)
                ring_container_layout.setContentsMargins(0, 0, 0, 0)
                ring_container_layout.setSpacing(0)
                
                # Add title label (above ring, can be as wide as needed)
                title_label = QLabel(bill.name)
                title_label.setFont(theme_manager.get_font("small"))
                title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                colors = theme_manager.get_colors()
                title_label.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
                title_label.setWordWrap(True)  # Allow text wrapping
                title_label.setFixedHeight(15)  # Fixed height for title
                ring_container_layout.addWidget(title_label)
                
                # Add ring chart (no internal title)
                ring_chart = RingChartWidget("")  # Empty title since we handle it externally
                ring_container_layout.addWidget(ring_chart)
                
                # Store references
                self.ring_charts.append(ring_chart)
                self.ring_titles.append(title_label)
                
                # Add to main layout
                rings_layout.addWidget(ring_container)
            
            # Add stretch to center the rings
            rings_layout.addStretch()
            
        except Exception as e:
            print(f"Error setting up bill rings: {e}")
    
    def on_savings_chart_clicked(self, chart_index):
        """Handle savings chart title click"""
        try:
            # Store chart index for the signal handler
            self.current_chart_index = chart_index
            
            # Create and show dialog
            dialog = AccountSelectorDialog(self.transaction_manager, self)
            dialog.account_selected.connect(self.on_account_selected)
            dialog.show()
                    
        except Exception as e:
            print(f"Error handling savings chart click: {e}")
    
    def on_account_selected(self, account_type, account_obj, account_name):
        """Handle account selection from dialog (keeps dialog open)"""
        try:
            chart_index = self.current_chart_index
            self.selected_accounts[chart_index] = (account_type, account_obj)
            
            # Update chart title
            if chart_index < len(self.savings_line_charts):
                self.savings_line_charts[chart_index].update_title(account_name)
            
            # Update chart data
            self.update_single_savings_chart(chart_index)
            
        except Exception as e:
            print(f"Error handling account selection: {e}")
    
    def update_single_savings_chart(self, chart_index):
        """Update a single savings chart with selected account data"""
        try:
            if chart_index >= len(self.savings_line_charts):
                return
                
            chart = self.savings_line_charts[chart_index]
            selected_account = self.selected_accounts[chart_index]
            
            if not selected_account or not chart:
                return
            
            account_type, account_obj = selected_account
            running_total_data = self.get_account_running_totals(account_type, account_obj)
            
            if running_total_data:
                # Don't pass xlabel/ylabel to keep savings rate styling
                chart.update_data({"Running Total": running_total_data})
            
        except Exception as e:
            print(f"Error updating single savings chart: {e}")
    
    def get_account_running_totals(self, account_type, account_obj):
        """Get running totals for an account over time"""
        try:
            from datetime import datetime, timedelta
            
            # Get transactions for this account
            all_transactions = self.transaction_manager.get_all_transactions()

            # Apply time filtering to all transactions
            all_transactions = self.apply_time_frame_filter(all_transactions)
            
            if account_type == 'account':
                # Filter saving transactions for this account
                account_transactions = [
                    t for t in all_transactions 
                    if t.transaction_type == "saving" and 
                       (t.account_id == account_obj.id or t.account_saved_to == account_obj.name)
                ]
            else:  # bill
                # For bills, we need to look at both bill_pay transactions AND savings transactions
                # that might be allocated to this bill
                account_transactions = []
                
                # Get bill_pay transactions for this bill
                bill_pay_transactions = [
                    t for t in all_transactions 
                    if t.transaction_type == "bill_pay" and 
                       (t.bill_id == account_obj.id or t.bill_type == account_obj.name)
                ]
                
                # Also get savings transactions that mention this bill in description
                savings_for_bill = [
                    t for t in all_transactions
                    if t.transaction_type == "saving" and
                       hasattr(t, 'description') and t.description and
                       account_obj.name.lower() in t.description.lower()
                ]
                
                # Combine both types
                account_transactions = bill_pay_transactions + savings_for_bill
            
            # Sort by date for both account types
            if account_transactions:
                account_transactions.sort(key=lambda t: t.date)
            
            # Calculate running totals over time
            data_points = []
            running_total = 0
            
            if account_type == 'account':
                # For savings accounts: start at 0, add deposits, subtract withdrawals
                for i, transaction in enumerate(account_transactions):
                    running_total += transaction.amount  # Positive for deposits, negative for withdrawals
                    data_points.append((i, running_total))
            else:
                # For bills: show accumulation then spending pattern
                # This tracks how much has been saved/allocated for this bill over time
                if not account_transactions:
                    # If no transactions, show the current bill running total as a flat line
                    current_total = getattr(account_obj, 'running_total', 0)
                    data_points = [(0, current_total), (1, current_total)]
                else:
                    for i, transaction in enumerate(account_transactions):
                        if transaction.transaction_type == "bill_pay":
                            running_total -= transaction.amount  # Money spent on bill
                        elif transaction.transaction_type == "saving":
                            running_total += transaction.amount  # Money saved for bill
                        data_points.append((i, running_total))
            
            return data_points
            
        except Exception as e:
            print(f"Error getting account running totals: {e}")
            return []
    
    def auto_select_random_for_chart(self, chart_index):
        """Automatically select account or bill for a savings chart based on settings"""
        try:
            import random
            
            # Get available accounts and bills
            accounts = self.transaction_manager.get_all_accounts()
            bills = self.transaction_manager.get_all_bills()
            
            # Get setting for this chart
            setting_key = f"dashboard_chart{chart_index + 1}_account"
            preferred_account = get_setting(setting_key, "random")
            
            # Combine accounts and bills into options
            options = []
            for account in accounts:
                options.append(('account', account, account.name))
            for bill in bills:
                options.append(('bill', bill, bill.name))
            
            if not options:
                # No accounts or bills available
                if chart_index < len(self.savings_line_charts):
                    self.savings_line_charts[chart_index].clear_chart()
                return
            
            # Select option based on settings
            selected_option = None
            if preferred_account == "random":
                # Random selection (original behavior)
                selected_option = random.choice(options)
            else:
                # Look for specific account/bill by name
                for option in options:
                    account_type, account_obj, account_name = option
                    if account_name == preferred_account:
                        selected_option = option
                        break
                
                # If preferred account not found, fall back to random
                if selected_option is None:
                    selected_option = random.choice(options)
            
            account_type, account_obj, account_name = selected_option
            
            # Ensure selected_accounts list is large enough
            while len(self.selected_accounts) <= chart_index:
                self.selected_accounts.append(None)
            
            # Set the selection
            self.selected_accounts[chart_index] = (account_type, account_obj)
            
            # Update chart title and data - remove "(auto)" text
            if chart_index < len(self.savings_line_charts):
                self.savings_line_charts[chart_index].update_title(account_name)
                self.update_single_savings_chart(chart_index)
            
        except Exception as e:
            print(f"Error auto-selecting random account for chart {chart_index}: {e}")