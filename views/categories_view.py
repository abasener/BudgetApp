"""
Categories View - Category analysis and details
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                             QScrollArea, QListWidget, QListWidgetItem, QPushButton, QDialog, QToolButton)
from PyQt6.QtCore import Qt
from themes import theme_manager
from widgets import PieChartWidget, BoxPlotWidget, HistogramWidget, WeeklySpendingTrendWidget
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from scipy.stats import pearsonr
from views.dialogs.settings_dialog import get_setting
from datetime import datetime, date


class CategoriesView(QWidget):
    def __init__(self, transaction_manager=None, analytics_engine=None):
        super().__init__()
        self.transaction_manager = transaction_manager
        self.analytics_engine = analytics_engine
        self.selected_category = None
        
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
        
        # Header with title and category management buttons
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("📊 Categories")
        title.setFont(theme_manager.get_font("title"))
        title.setStyleSheet(f"color: {colors['text_primary']};")
        header_layout.addWidget(title)
        
        # Add stretch to push buttons to the right
        header_layout.addStretch()

        # Refresh button - compact tool button with just emoji
        self.refresh_button = QToolButton()
        self.refresh_button.setText("🔄")
        self.refresh_button.setToolTip("Refresh Categories")
        self.refresh_button.setFixedSize(40, 30)
        self.refresh_button.clicked.connect(self.refresh)
        # Styling applied in apply_header_theme method
        header_layout.addWidget(self.refresh_button)

        # Add Category button
        self.add_category_btn = QPushButton("➕ Add Category")
        self.add_category_btn.setFixedHeight(35)
        self.add_category_btn.setFixedWidth(140)
        self.add_category_btn.setFont(theme_manager.get_font("button_small"))
        self.add_category_btn.clicked.connect(self.open_add_category_dialog)
        self.add_category_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['primary']};
                color: {colors['background']};
                border: 1px solid {colors['primary_dark'] if colors.get('primary_dark') else colors['border']};
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
                margin: 2px;
            }}
            QPushButton:hover {{
                background-color: {colors.get('primary_dark', colors['primary'])};
            }}
        """)
        header_layout.addWidget(self.add_category_btn)

        # Remove Category button
        self.remove_category_btn = QPushButton("🗑️ Remove Category")
        self.remove_category_btn.setFixedHeight(35)
        self.remove_category_btn.setFixedWidth(155)
        self.remove_category_btn.setFont(theme_manager.get_font("button_small"))
        self.remove_category_btn.clicked.connect(self.open_remove_category_dialog)
        self.remove_category_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('secondary', colors['surface'])};
                color: {colors['text_primary']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 5px 10px;
                margin: 2px;
            }}
            QPushButton:hover {{
                background-color: {colors.get('hover', colors['surface_variant'])};
            }}
        """)
        header_layout.addWidget(self.remove_category_btn)
        
        content_layout.addLayout(header_layout)

        # Apply initial theme to refresh button
        self.apply_header_theme()

        # TOP ROW - Category selector, stats, box plot, pie chart, color key
        top_row = self.create_top_row()
        content_layout.addWidget(top_row)
        
        # BOTTOM SECTION - Category details (placeholder for now)
        bottom_section = self.create_bottom_section()
        content_layout.addWidget(bottom_section)
        
        # Set content layout and add to scroll area
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
        
    def create_top_row(self):
        """Create the top row with category selector and overview widgets"""
        top_frame = QFrame()
        top_frame.setFrameStyle(QFrame.Shape.Box)
        colors = theme_manager.get_colors()
        top_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface_variant']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        # Set fixed height for top row
        top_frame.setFixedHeight(300)
        
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)
        
        # COLUMN 1: Category selector
        category_selector_column = self.create_category_selector_column()
        top_layout.addWidget(category_selector_column, 1)  # Takes 1 part of space
        
        # COLUMN 2: Combined category statistics and box plot
        stats_column = self.create_combined_stats_column()
        top_layout.addWidget(stats_column, 2)  # Takes 2 parts of space (wider)
        
        # COLUMN 4: Main pie chart
        pie_chart_column = self.create_pie_chart_column()
        top_layout.addWidget(pie_chart_column, 1)  # Takes 1 part of space
        
        # COLUMN 5: Color key
        color_key_column = self.create_color_key_column()
        top_layout.addWidget(color_key_column, 1)  # Takes 1 part of space
        
        top_frame.setLayout(top_layout)
        return top_frame
        
    def create_category_selector_column(self):
        """Create scrollable category list (similar to week selector)"""
        column_frame = QFrame()
        colors = theme_manager.get_colors()

        # Style column frame with surface background to stand out from surface_variant parent
        column_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 8px;
            }}
        """)

        column_layout = QVBoxLayout()

        # Column title
        self.category_title = QLabel("Categories")
        self.category_title.setFont(theme_manager.get_font("subtitle"))
        self.category_title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        column_layout.addWidget(self.category_title)

        # Scrollable list of categories
        self.category_list = QListWidget()
        self.category_list.setMaximumHeight(200)
        self.category_list.itemClicked.connect(self.on_category_selected)

        # Style the list
        self.category_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {colors['background']};
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
        
        column_layout.addWidget(self.category_list)
        column_frame.setLayout(column_layout)
        return column_frame
        
    def create_combined_stats_column(self):
        """Create combined category statistics and box plot column"""
        column_frame = QFrame()
        colors = theme_manager.get_colors()

        # Style column frame
        column_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 8px;
            }}
        """)

        column_layout = QVBoxLayout()

        # Column title
        stats_title = QLabel("Category Overview")
        stats_title.setFont(theme_manager.get_font("subtitle"))
        stats_title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        column_layout.addWidget(stats_title)

        # Statistics display - compact horizontal layout
        self.stats_label = QLabel("Loading...")
        self.stats_label.setFont(theme_manager.get_font("small"))
        self.stats_label.setStyleSheet(f"""
            color: {colors['text_primary']};
            background-color: {colors['background']};
            padding: 8px;
            border-radius: 4px;
            border: 1px solid {colors['border']};
        """)
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.stats_label.setWordWrap(True)
        column_layout.addWidget(self.stats_label)
        
        # Box plot widget (from dashboard) - same as dashboard, no title
        self.box_plot_widget = BoxPlotWidget("")  # No title to save space
        self.box_plot_widget.setMaximumHeight(140)  # Constrain height to fit
        column_layout.addWidget(self.box_plot_widget)
        
        # Add stretch to push content to top
        column_layout.addStretch()
        
        column_frame.setLayout(column_layout)
        return column_frame
        
    def create_pie_chart_column(self):
        """Create main pie chart for all-time spending"""
        column_frame = QFrame()
        column_layout = QVBoxLayout()
        
        # Column title
        pie_title = QLabel("All-Time Spending")
        pie_title.setFont(theme_manager.get_font("subtitle"))
        colors = theme_manager.get_colors()
        pie_title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        column_layout.addWidget(pie_title)
        
        # Pie chart widget (from dashboard)
        self.main_pie_chart = PieChartWidget("Category Spending")
        column_layout.addWidget(self.main_pie_chart)
        
        column_frame.setLayout(column_layout)
        return column_frame
        
    def create_color_key_column(self):
        """Create color key for pie chart categories"""
        column_frame = QFrame()
        column_layout = QVBoxLayout()
        
        # Column title
        key_title = QLabel("Category Colors")
        key_title.setFont(theme_manager.get_font("subtitle"))
        colors = theme_manager.get_colors()
        key_title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
        column_layout.addWidget(key_title)
        
        # Color key display
        self.color_key_label = QLabel("Loading...")
        self.color_key_label.setFont(theme_manager.get_font("small"))
        self.color_key_label.setStyleSheet(f"""
            color: {colors['text_primary']}; 
            background-color: {colors['surface']}; 
            padding: 10px; 
            border-radius: 4px;
            border: 1px solid {colors['border']};
        """)
        self.color_key_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.color_key_label.setWordWrap(True)
        self.color_key_label.setTextFormat(Qt.TextFormat.RichText)  # Enable HTML support
        column_layout.addWidget(self.color_key_label)
        
        # Add stretch to push content to top
        column_layout.addStretch()
        
        column_frame.setLayout(column_layout)
        return column_frame
        
    def create_bottom_section(self):
        """Create bottom section for selected category details"""
        bottom_frame = QFrame()
        bottom_frame.setFrameStyle(QFrame.Shape.Box)
        colors = theme_manager.get_colors()
        bottom_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface_variant']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(15)
        
        # Category details header
        self.category_details_title = QLabel("Select a Category")
        self.category_details_title.setFont(theme_manager.get_font("title"))
        self.category_details_title.setStyleSheet(f"color: {colors['text_primary']}; padding: 5px;")
        self.category_details_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_layout.addWidget(self.category_details_title)
        
        # Statistics text blocks in a horizontal layout
        stats_frame = QFrame()
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Average cost block
        avg_cost_frame = QFrame()
        avg_cost_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 12px;
            }}
        """)
        avg_cost_layout = QVBoxLayout()
        
        avg_cost_label = QLabel("Average Cost")
        avg_cost_label.setFont(theme_manager.get_font("small"))
        avg_cost_label.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: bold;")
        avg_cost_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.avg_cost_value = QLabel("$0.00")
        self.avg_cost_value.setFont(theme_manager.get_font("subtitle"))
        self.avg_cost_value.setStyleSheet(f"color: {colors['primary']}; font-weight: bold;")
        self.avg_cost_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        avg_cost_layout.addWidget(avg_cost_label)
        avg_cost_layout.addWidget(self.avg_cost_value)
        avg_cost_frame.setLayout(avg_cost_layout)
        stats_layout.addWidget(avg_cost_frame)
        
        # Variance block
        variance_frame = QFrame()
        variance_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 12px;
            }}
        """)
        variance_layout = QVBoxLayout()
        
        variance_label = QLabel("Cost Variance")
        variance_label.setFont(theme_manager.get_font("small"))
        variance_label.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: bold;")
        variance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.variance_value = QLabel("$0.00")
        self.variance_value.setFont(theme_manager.get_font("subtitle"))
        self.variance_value.setStyleSheet(f"color: {colors['primary']}; font-weight: bold;")
        self.variance_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        variance_layout.addWidget(variance_label)
        variance_layout.addWidget(self.variance_value)
        variance_frame.setLayout(variance_layout)
        stats_layout.addWidget(variance_frame)
        
        # Number of purchases block
        purchases_frame = QFrame()
        purchases_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 10px;
            }}
        """)
        purchases_layout = QVBoxLayout()
        
        purchases_label = QLabel("Total Purchases")
        purchases_label.setFont(theme_manager.get_font("small"))
        purchases_label.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: bold;")
        purchases_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.purchases_value = QLabel("0")
        self.purchases_value.setFont(theme_manager.get_font("subtitle"))
        self.purchases_value.setStyleSheet(f"color: {colors['primary']}; font-weight: bold;")
        self.purchases_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        purchases_layout.addWidget(purchases_label)
        purchases_layout.addWidget(self.purchases_value)
        purchases_frame.setLayout(purchases_layout)
        stats_layout.addWidget(purchases_frame)
        
        # Average transactions per week block
        weekly_freq_frame = QFrame()
        weekly_freq_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 10px;
            }}
        """)
        weekly_freq_layout = QVBoxLayout()
        
        weekly_freq_label = QLabel("Avg per Week")
        weekly_freq_label.setFont(theme_manager.get_font("small"))
        weekly_freq_label.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: bold;")
        weekly_freq_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.weekly_freq_value = QLabel("0.0")
        self.weekly_freq_value.setFont(theme_manager.get_font("subtitle"))
        self.weekly_freq_value.setStyleSheet(f"color: {colors['primary']}; font-weight: bold;")
        self.weekly_freq_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        weekly_freq_layout.addWidget(weekly_freq_label)
        weekly_freq_layout.addWidget(self.weekly_freq_value)
        weekly_freq_frame.setLayout(weekly_freq_layout)
        stats_layout.addWidget(weekly_freq_frame)
        
        stats_frame.setLayout(stats_layout)
        bottom_layout.addWidget(stats_frame)
        
        # Charts section - two charts side by side (half width each)
        charts_frame = QFrame()
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)
        
        # Left chart: Purchase size histogram
        histogram_frame = QFrame()
        histogram_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 5px;
            }}
        """)
        histogram_layout = QVBoxLayout()
        
        histogram_title = QLabel("Purchase Distribution")
        histogram_title.setFont(theme_manager.get_font("small"))
        histogram_title.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: bold;")
        histogram_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        histogram_layout.addWidget(histogram_title)
        
        self.category_histogram = HistogramWidget("")
        self.category_histogram.setMinimumHeight(120)
        self.category_histogram.setMaximumHeight(180)
        histogram_layout.addWidget(self.category_histogram)
        
        histogram_frame.setLayout(histogram_layout)
        charts_layout.addWidget(histogram_frame)
        
        # Right chart: Weekly spending trends
        trend_frame = QFrame()
        trend_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 5px;
            }}
        """)
        trend_layout = QVBoxLayout()
        
        trend_title = QLabel("Weekly Spending Pattern")
        trend_title.setFont(theme_manager.get_font("small"))
        trend_title.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: bold;")
        trend_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        trend_layout.addWidget(trend_title)
        
        self.category_trend_chart = WeeklySpendingTrendWidget("")
        self.category_trend_chart.setMinimumHeight(120)
        self.category_trend_chart.setMaximumHeight(180)
        trend_layout.addWidget(self.category_trend_chart)
        
        trend_frame.setLayout(trend_layout)
        charts_layout.addWidget(trend_frame)
        
        charts_frame.setLayout(charts_layout)
        bottom_layout.addWidget(charts_frame)
        
        # Correlation plots section - no scroll area, just expand as needed
        self.correlation_frame = QFrame()
        self.correlation_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 10px;
            }}
        """)
        
        correlation_layout = QVBoxLayout()
        
        # Correlation title
        correlation_title = QLabel("Category Correlations")
        correlation_title.setFont(theme_manager.get_font("small"))
        correlation_title.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: bold;")
        correlation_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        correlation_layout.addWidget(correlation_title)
        
        # Correlation explanation
        self.correlation_explanation = QLabel("📊 Correlation Guide: -1.0 = Strong Inverse Relationship  •  0.0 = No Relationship  •  +1.0 = Strong Positive Relationship")
        self.correlation_explanation.setFont(theme_manager.get_font("small"))
        self.correlation_explanation.setStyleSheet(f"color: {colors['text_secondary']}; font-style: italic; padding: 5px;")
        self.correlation_explanation.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.correlation_explanation.setWordWrap(True)
        correlation_layout.addWidget(self.correlation_explanation)
        
        # Direct correlation plots layout - no scroll area
        self.correlation_plots_layout = QVBoxLayout()
        self.correlation_plots_layout.setSpacing(10)
        correlation_layout.addLayout(self.correlation_plots_layout)
        
        self.correlation_frame.setLayout(correlation_layout)
        bottom_layout.addWidget(self.correlation_frame)
        
        # Add stretch to push content to top
        bottom_layout.addStretch()
        
        bottom_frame.setLayout(bottom_layout)
        return bottom_frame
        
    def on_category_selected(self, item):
        """Handle category selection from list"""
        self.selected_category = item.data(Qt.ItemDataRole.UserRole)
        if self.selected_category:
            # Update the category title to show selected category
            self.category_title.setText(f"Selected: {self.selected_category}")

        # Update top row charts to highlight selected category
        self.update_box_plot()  # Refresh box plot with highlighting
        self.update_main_pie_chart()  # Refresh pie chart with highlighting
        self.update_color_key()  # Refresh color key with bold text for selected category

        self.update_category_details()
        
    def update_category_details(self):
        """Update the bottom section with selected category details"""
        if not self.selected_category or not self.transaction_manager:
            # No category selected - show default state
            self.category_details_title.setText("Select a Category")
            self.avg_cost_value.setText("$0.00")
            self.variance_value.setText("$0.00")
            self.purchases_value.setText("0")
            self.weekly_freq_value.setText("0.0")
            return
            
        try:
            # Get all transactions for this category
            all_transactions = self.transaction_manager.get_all_transactions()
            category_transactions = [
                t for t in all_transactions 
                if t.is_spending and t.include_in_analytics and 
                (t.category == self.selected_category)
            ]
            
            
            if not category_transactions:
                # No transactions for this category
                self.category_details_title.setText(f"{self.selected_category} - No Data")
                self.avg_cost_value.setText("$0.00")
                self.variance_value.setText("$0.00")
                self.purchases_value.setText("0")
                self.weekly_freq_value.setText("0.0")
                return
            
            # Update title
            self.category_details_title.setText(f"{self.selected_category} Details")

            # Update title color to match category color
            color_map = self.get_category_color_map()
            category_color = color_map.get(self.selected_category, theme_manager.get_color('text_primary'))

            # Remove alpha channel if present (Qt CSS might not handle 8-digit hex colors properly)
            if len(category_color) == 9 and category_color.startswith('#'):
                category_color = category_color[:7]  # Keep only #RRGGBB, remove alpha
            self.category_details_title.setStyleSheet(f"color: {category_color}; padding: 5px; font-weight: bold;")
            
            # Calculate statistics
            amounts = [t.amount for t in category_transactions]
            
            # Average cost
            avg_cost = sum(amounts) / len(amounts)
            self.avg_cost_value.setText(f"${avg_cost:.2f}")
            
            # Variance (standard deviation)
            if len(amounts) > 1:
                import statistics
                variance = statistics.stdev(amounts)
                self.variance_value.setText(f"${variance:.2f}")
            else:
                self.variance_value.setText("$0.00")
            
            # Number of purchases
            self.purchases_value.setText(str(len(category_transactions)))
            
            # Average transactions per week
            # Calculate based on date range of transactions
            if category_transactions:
                dates = [t.date for t in category_transactions if t.date]
                if dates:
                    min_date = min(dates)
                    max_date = max(dates)
                    date_range_days = (max_date - min_date).days + 1
                    weeks = max(1, date_range_days / 7)  # At least 1 week
                    avg_per_week = len(category_transactions) / weeks
                    self.weekly_freq_value.setText(f"{avg_per_week:.1f}")
                else:
                    self.weekly_freq_value.setText("0.0")
            else:
                self.weekly_freq_value.setText("0.0")
                
        except Exception as e:
            print(f"Error updating category details: {e}")
            self.category_details_title.setText(f"{self.selected_category} - Error")
            self.avg_cost_value.setText("Error")
            self.variance_value.setText("Error")
            self.purchases_value.setText("Error")
            self.weekly_freq_value.setText("Error")
        
        # Update the category charts
        self.update_category_charts()
        
    def update_category_charts(self):
        """Update histogram, trend charts, and correlation plots for the selected category"""
        self.update_category_histogram()
        self.update_category_weekly_trends()
        self.update_correlation_plots()
        
    def update_category_histogram(self):
        """Update histogram with purchase size distribution for selected category"""
        if not self.selected_category or not self.transaction_manager or not self.category_histogram:
            if self.category_histogram:
                self.category_histogram.update_data([])
            return
            
        try:
            # Get all transactions for this category
            all_transactions = self.transaction_manager.get_all_transactions()
            category_transactions = [
                t for t in all_transactions 
                if t.is_spending and t.include_in_analytics and 
                (t.category == self.selected_category)
            ]
            
            if not category_transactions:
                self.category_histogram.update_data([])
                return
            
            # Extract purchase amounts
            purchase_amounts = [float(t.amount) for t in category_transactions if t.amount > 0]
            
            if purchase_amounts:
                # Update histogram with 20 buckets
                self.category_histogram.update_data(purchase_amounts, num_buckets=20)
            else:
                self.category_histogram.update_data([])
                
        except Exception as e:
            print(f"Error updating category histogram: {e}")
            if self.category_histogram:
                self.category_histogram.update_data([])
    
    def update_category_weekly_trends(self):
        """Update weekly spending trend chart for selected category"""
        if not self.selected_category or not self.transaction_manager or not self.category_trend_chart:
            if self.category_trend_chart:
                self.category_trend_chart.update_data({})
            return
            
        try:
            # Get all transactions for this category
            all_transactions = self.transaction_manager.get_all_transactions()
            category_transactions = [
                t for t in all_transactions 
                if t.is_spending and t.include_in_analytics and 
                (t.category == self.selected_category)
            ]
            
            if not category_transactions:
                self.category_trend_chart.update_data({})
                return
            
            # Group transactions by week (same logic as dashboard)
            from datetime import datetime, timedelta
            from collections import defaultdict
            
            weekly_daily_totals = defaultdict(lambda: [0.0] * 7)  # 7 days per week
            
            for transaction in category_transactions:
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
            
            # Keep only recent weeks (last 8-10 weeks for good cloud effect)
            sorted_weeks = sorted(weekly_daily_totals.keys())[-8:]  # Last 8 weeks
            recent_weekly_data = {week: weekly_daily_totals[week] for week in sorted_weeks}
            
            # Get category color for the average line
            color_map = self.get_category_color_map()
            category_color = color_map.get(self.selected_category)

            self.category_trend_chart.update_data(recent_weekly_data, average_line_color=category_color)
                
        except Exception as e:
            print(f"Error updating category weekly trends: {e}")
            if self.category_trend_chart:
                self.category_trend_chart.update_data({})
    
    def update_correlation_plots(self):
        """Create correlation scatter plots between selected category and all other categories"""
        if not self.selected_category or not self.transaction_manager:
            self.clear_correlation_plots()
            return
            
        try:
            # Get all spending transactions
            all_transactions = self.transaction_manager.get_all_transactions()
            spending_transactions = [
                t for t in all_transactions 
                if t.is_spending and t.include_in_analytics and t.category
            ]
            
            if not spending_transactions:
                self.clear_correlation_plots()
                return
            
            # Group transactions by week and category
            from datetime import datetime, timedelta
            from collections import defaultdict
            
            weekly_category_totals = defaultdict(lambda: defaultdict(float))
            
            for transaction in spending_transactions:
                # Get the transaction date
                if hasattr(transaction.date, 'weekday'):
                    trans_date = transaction.date
                else:
                    trans_date = datetime.strptime(str(transaction.date), "%Y-%m-%d").date()
                
                # Get Monday of this transaction's week
                monday = trans_date - timedelta(days=trans_date.weekday())
                week_key = monday.strftime("%Y-%m-%d")
                
                category = transaction.category
                weekly_category_totals[week_key][category] += float(transaction.amount)
            
            # Get all unique categories except the selected one
            all_categories = set()
            for week_data in weekly_category_totals.values():
                all_categories.update(week_data.keys())
            
            other_categories = [cat for cat in sorted(all_categories) if cat != self.selected_category]
            
            if not other_categories:
                self.clear_correlation_plots()
                return
                
            # Clear existing plots
            self.clear_correlation_plots()
            
            # Calculate grid layout: 5 plots per row
            plots_per_row = 5
            num_plots = len(other_categories)
            num_rows = (num_plots + plots_per_row - 1) // plots_per_row  # Ceiling division
            
            # Get chart colors for different categories
            chart_colors = theme_manager.get_chart_colors()
            
            # Create a grid layout for correlation plots (5 per row, evenly spaced like a table)
            from PyQt6.QtWidgets import QGridLayout
            
            # Create a single grid widget to hold all plots
            grid_widget = QWidget()
            grid_layout = QGridLayout()
            grid_layout.setSpacing(15)  # Space between plots
            
            # Add all plots to grid positions
            for plot_idx in range(num_plots):
                other_category = other_categories[plot_idx]
                
                # Calculate grid position
                row = plot_idx // plots_per_row
                col = plot_idx % plots_per_row
                
                # Prepare data for correlation plot
                selected_values = []
                other_values = []
                
                for week_key in sorted(weekly_category_totals.keys()):
                    week_data = weekly_category_totals[week_key]
                    selected_amount = week_data.get(self.selected_category, 0.0)
                    other_amount = week_data.get(other_category, 0.0)
                    
                    # Only include weeks where at least one category has spending
                    if selected_amount > 0 or other_amount > 0:
                        selected_values.append(selected_amount)
                        other_values.append(other_amount)
                
                # Calculate correlation coefficient
                correlation = 0.0
                if len(selected_values) > 2:
                    try:
                        correlation, _ = pearsonr(selected_values, other_values)
                        if np.isnan(correlation):
                            correlation = 0.0
                    except:
                        correlation = 0.0
                
                # Create matplotlib figure for this correlation plot
                fig = Figure(figsize=(2.5, 2.5))
                fig.patch.set_facecolor('none')
                
                ax = fig.add_subplot(111)
                
                if selected_values and other_values:
                    # Get color for this category
                    color = chart_colors[plot_idx % len(chart_colors)]
                    
                    # Create scatter plot
                    ax.scatter(other_values, selected_values, 
                             alpha=0.7, s=30, c=color, edgecolors='white', linewidth=0.5)
                    
                    # Set axis limits with some padding
                    if max(other_values) > 0:
                        ax.set_xlim(0, max(other_values) * 1.05)
                    if max(selected_values) > 0:
                        ax.set_ylim(0, max(selected_values) * 1.05)
                
                # Style the plot with ticks and grid
                if selected_values and other_values and max(other_values) > 0 and max(selected_values) > 0:
                    # Add meaningful tick marks
                    max_x = max(other_values)
                    max_y = max(selected_values)
                    
                    # Create 3-4 tick marks on each axis
                    x_ticks = [0, max_x/3, 2*max_x/3, max_x]
                    y_ticks = [0, max_y/3, 2*max_y/3, max_y]
                    
                    ax.set_xticks(x_ticks)
                    ax.set_yticks(y_ticks)
                    
                    # Format tick labels to be concise
                    ax.set_xticklabels([f"${int(x)}" if x > 0 else "0" for x in x_ticks], fontsize=6)
                    ax.set_yticklabels([f"${int(y)}" if y > 0 else "0" for y in y_ticks], fontsize=6)
                    
                    # Add grid
                    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
                else:
                    # Empty plot - minimal ticks
                    ax.set_xticks([])
                    ax.set_yticks([])
                    ax.grid(True, alpha=0.2)
                
                # Set title with category name and correlation
                title = f"{other_category[:8]}{'...' if len(other_category) > 8 else ''}: {correlation:.2f}"
                ax.set_title(title, fontsize=8, pad=5)
                
                # Apply theme colors (get fresh colors in case theme changed)
                theme_colors = theme_manager.get_colors()
                ax.set_facecolor(theme_colors['background'])
                ax.spines['bottom'].set_color(theme_colors['border'])
                ax.spines['top'].set_color(theme_colors['border'])
                ax.spines['left'].set_color(theme_colors['border'])
                ax.spines['right'].set_color(theme_colors['border'])
                ax.title.set_color(theme_colors['text_primary'])
                ax.tick_params(colors=theme_colors['text_secondary'])  # Tick color
                
                fig.tight_layout()
                
                # Create canvas and add to grid
                canvas = FigureCanvas(fig)
                canvas.setFixedSize(150, 150)  # Small square plots
                grid_layout.addWidget(canvas, row, col)
            
            # Set uniform column stretching so all columns take equal space
            for col in range(plots_per_row):
                grid_layout.setColumnStretch(col, 1)
            
            grid_widget.setLayout(grid_layout)
            self.correlation_plots_layout.addWidget(grid_widget)
                
        except Exception as e:
            print(f"Error updating correlation plots: {e}")
            self.clear_correlation_plots()
    
    def clear_correlation_plots(self):
        """Clear all correlation plots from the layout"""
        if hasattr(self, 'correlation_plots_layout'):
            # Remove all existing widgets
            while self.correlation_plots_layout.count():
                child = self.correlation_plots_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        
    def populate_category_list(self):
        """Populate the category list with all available categories"""
        if not self.transaction_manager:
            return
            
        try:
            # Get all transactions and extract unique categories
            all_transactions = self.transaction_manager.get_all_transactions()
            categories = set()
            
            for transaction in all_transactions:
                if transaction.category and transaction.is_spending:
                    categories.add(transaction.category)
            
            # Sort categories alphabetically
            sorted_categories = sorted(categories)
            
            self.category_list.clear()
            
            for category in sorted_categories:
                item = QListWidgetItem(category)
                item.setData(Qt.ItemDataRole.UserRole, category)
                self.category_list.addItem(item)
                
            # Select first item by default and trigger update
            if self.category_list.count() > 0:
                self.category_list.setCurrentRow(0)
                self.selected_category = self.category_list.item(0).data(Qt.ItemDataRole.UserRole)
                if self.selected_category:
                    self.category_title.setText(f"Selected: {self.selected_category}")
                    # Trigger category details update for default selection
                    self.update_category_details()
                    
        except Exception as e:
            print(f"Error populating category list: {e}")
            
    def get_consistent_category_order(self):
        """Get categories in consistent order for color assignment across all charts

        Returns:
            list: [(category_name, total_amount), ...] sorted by spending amount (highest first)
        """
        if not self.transaction_manager:
            return []

        try:
            # Get all spending transactions
            all_transactions = self.transaction_manager.get_all_transactions()
            spending_transactions = [t for t in all_transactions if t.is_spending and t.include_in_analytics]

            # Calculate spending by category
            category_spending = {}
            for transaction in spending_transactions:
                category = transaction.category or "Uncategorized"
                category_spending[category] = category_spending.get(category, 0) + transaction.amount

            # Sort by spending amount (highest first) - this is our master ordering
            sorted_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)

            return sorted_categories

        except Exception as e:
            print(f"Error getting consistent category order: {e}")
            return []

    def get_category_color_map(self):
        """Get a dictionary mapping category names to consistent colors

        Returns:
            dict: {category_name: hex_color, ...}
        """
        sorted_categories = self.get_consistent_category_order()
        chart_colors = theme_manager.get_chart_colors()

        color_map = {}
        for i, (category, amount) in enumerate(sorted_categories):
            color_index = i % len(chart_colors)
            color_map[category] = chart_colors[color_index]

        return color_map

    def get_category_color(self, category_name, color_map=None):
        """Get the consistent color for a specific category

        Args:
            category_name: name of the category
            color_map: optional pre-computed color mapping

        Returns:
            str: hex color code for this category
        """
        if color_map is None:
            color_map = self.get_category_color_map()

        if category_name in color_map:
            return color_map[category_name]

        # Category not found - return first color as fallback
        chart_colors = theme_manager.get_chart_colors()
        fallback_color = chart_colors[0] if chart_colors else "#000000"
        return fallback_color

    def update_category_stats(self):
        """Update category overview statistics"""
        if not self.transaction_manager:
            return
            
        try:
            # Get all spending transactions
            all_transactions = self.transaction_manager.get_all_transactions()
            spending_transactions = [t for t in all_transactions if t.is_spending and t.include_in_analytics]
            
            # Calculate statistics
            total_categories = len(set(t.category for t in spending_transactions if t.category))
            total_transactions = len(spending_transactions)
            
            # Most common category
            category_counts = {}
            for transaction in spending_transactions:
                if transaction.category:
                    category_counts[transaction.category] = category_counts.get(transaction.category, 0) + 1
            
            most_common_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else "None"
            most_common_count = category_counts.get(most_common_category, 0) if most_common_category != "None" else 0
            
            # Compact horizontal layout text
            stats_text = f"Number of Categories: {total_categories}     Number of Transactions: {total_transactions:,}     Most Common Category: {most_common_category} ({most_common_count})"
            
            self.stats_label.setText(stats_text)
            
        except Exception as e:
            print(f"Error updating category stats: {e}")
            self.stats_label.setText("Error loading statistics")
            
    def update_box_plot(self):
        """Update box plot with purchase value distribution by category"""
        if not self.transaction_manager or not self.box_plot_widget:
            return

        try:
            # Get consistent category ordering
            sorted_categories = self.get_consistent_category_order()

            if sorted_categories:
                # Group transactions by category
                all_transactions = self.transaction_manager.get_all_transactions()
                spending_transactions = [t for t in all_transactions if t.is_spending and t.include_in_analytics]

                category_amounts = {}
                for transaction in spending_transactions:
                    category = transaction.category or "Uncategorized"
                    if category not in category_amounts:
                        category_amounts[category] = []
                    category_amounts[category].append(transaction.amount)

                # Prepare data for box plot using consistent ordering
                plot_data = {}
                for category, total_amount in sorted_categories:
                    if category in category_amounts:  # Only include categories with data
                        amounts = category_amounts[category]
                        # Keep category names shorter for better fit when squished
                        display_name = category[:10] + "..." if len(category) > 10 else category
                        plot_data[display_name] = amounts

                # Pass selected category for highlighting (need to handle shortened names)
                highlight_key = None
                if self.selected_category:
                    # Find the matching shortened name in plot_data
                    for key in plot_data.keys():
                        if key.startswith(self.selected_category[:10]):
                            highlight_key = key
                            break
                        if self.selected_category == key:  # Exact match for short names
                            highlight_key = key
                            break

                # Get color map for consistent colors
                color_map = self.get_category_color_map()
                self.box_plot_widget.update_data(plot_data, highlight_category=highlight_key, color_map=color_map)
            else:
                self.box_plot_widget.clear_chart()

        except Exception as e:
            print(f"Error updating box plot: {e}")
            
    def update_main_pie_chart(self):
        """Update main pie chart with all-time category spending"""
        if not self.transaction_manager or not self.main_pie_chart:
            return

        try:
            # Get consistent category ordering
            sorted_categories = self.get_consistent_category_order()

            if sorted_categories:
                # Filter to only categories with spending data (same as box plot does)
                filtered_categories = [(cat, amount) for cat, amount in sorted_categories if amount > 0]

                # Convert to dict in the correct order for consistent colors
                category_spending = {category: amount for category, amount in filtered_categories}

                # Get consistent color mapping
                color_map = self.get_category_color_map()
                pie_colors = []
                for category, amount in filtered_categories:
                    color = color_map.get(category, "#000000")
                    pie_colors.append(color)

                # Pass selected category for highlighting and consistent colors
                self.main_pie_chart.update_data(category_spending, "All-Time Category Spending",
                                               highlight_category=self.selected_category,
                                               custom_colors=pie_colors)
            else:
                self.main_pie_chart.update_data({}, "No spending data")

        except Exception as e:
            print(f"Error updating main pie chart: {e}")
            
    def update_color_key(self):
        """Update color key display with actual colors"""
        if not self.main_pie_chart:
            return

        try:
            # Get consistent category ordering
            sorted_categories = self.get_consistent_category_order()

            if not sorted_categories:
                self.color_key_label.setText("No categories available")
                return

            # Filter to only categories with spending data (same as pie chart and box plot)
            filtered_categories = [(cat, amount) for cat, amount in sorted_categories if amount > 0]

            if not filtered_categories:
                self.color_key_label.setText("No categories available")
                return

            # Get consistent color mapping
            color_map = self.get_category_color_map()

            # Build color key with HTML for colors using color map
            key_html = ""
            for category, amount in filtered_categories:
                color = color_map.get(category, "#000000")

                # Truncate long category names
                display_name = category[:12] + "..." if len(category) > 12 else category

                # Bold the selected category for emphasis
                if category == self.selected_category:
                    key_html += f'<span style="color: {color}; font-weight: bold; font-size: 110%;">● {display_name}</span><br>'
                else:
                    key_html += f'<span style="color: {color};">● {display_name}</span><br>'

            if not key_html:
                key_html = "No categories available"

            self.color_key_label.setText(key_html.rstrip('<br>'))

        except Exception as e:
            print(f"Error updating color key: {e}")
            self.color_key_label.setText("Error loading colors")
            
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
        """Refresh categories view with current data"""
        self.populate_category_list()
        self.update_category_stats()
        self.update_box_plot()
        self.update_main_pie_chart()
        self.update_color_key()

    def on_theme_changed(self, theme_id):
        """Handle theme change for categories view"""
        try:
            self.update_view_styling()
            self.apply_header_theme()  # Update refresh button styling

            # Force regeneration of all charts to apply new theme colors
            if self.selected_category:
                # Regenerate charts that use category colors
                self.update_box_plot()  # Fix box plot colors
                self.update_main_pie_chart()  # Fix pie chart colors
                self.update_color_key()  # Fix color key
                self.update_category_histogram()  # Fix histogram colors
                self.update_category_weekly_trends()  # Fix trend line colors
                self.update_correlation_plots()  # Fix scatter plot colors
            
            # Also force chart widgets to apply themes immediately
            if hasattr(self, 'category_histogram') and self.category_histogram:
                self.category_histogram.apply_theme()
            if hasattr(self, 'category_trend_chart') and self.category_trend_chart:
                self.category_trend_chart.apply_theme()
            if hasattr(self, 'box_plot_widget') and self.box_plot_widget:
                self.box_plot_widget.apply_theme()
            if hasattr(self, 'main_pie_chart') and self.main_pie_chart:
                self.main_pie_chart.apply_theme()
            
        except Exception as e:
            print(f"Error applying theme to categories view: {e}")
    
    def update_view_styling(self):
        """Update only the visual styling of the categories view"""
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
            if "Categories" in child.text() and child.font().pointSize() > 12:  # Title label
                child.setStyleSheet(f"color: {colors['text_primary']};")
        
        # Update column title colors
        if hasattr(self, 'category_title'):
            self.category_title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
            
        # Update other column titles and bottom section titles
        for child in self.findChildren(QLabel):
            if child.text() in ["Category Overview", "All-Time Spending", "Category Colors"]:
                child.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; padding: 2px;")
            elif child.text().endswith("Details") or "Select a Category" in child.text():
                child.setStyleSheet(f"color: {colors['text_primary']}; padding: 5px;")
        
        # Update stats and color key labels
        if hasattr(self, 'stats_label'):
            self.stats_label.setStyleSheet(f"""
                color: {colors['text_primary']}; 
                background-color: {colors['surface']}; 
                padding: 10px; 
                border-radius: 4px;
                border: 1px solid {colors['border']};
            """)
            
        if hasattr(self, 'color_key_label'):
            self.color_key_label.setStyleSheet(f"""
                color: {colors['text_primary']}; 
                background-color: {colors['surface']}; 
                padding: 10px; 
                border-radius: 4px;
                border: 1px solid {colors['border']};
            """)
        
        # Update category list styling
        if hasattr(self, 'category_list'):
            self.category_list.setStyleSheet(f"""
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
        
        # Update all frame styling more aggressively
        for child in self.findChildren(QFrame):
            current_style = str(child.styleSheet())
            
            # Statistics blocks - look for the specific statistics frame patterns
            if ("surface" in current_style and "padding: 10px" in current_style) or \
               any(stat_child.text() in ["Average Cost", "Cost Variance", "Total Purchases", "Avg per Week"] 
                   for stat_child in child.findChildren(QLabel)):
                child.setStyleSheet(f"""
                    QFrame {{
                        background-color: {colors['surface']};
                        border: 1px solid {colors['border']};
                        border-radius: 4px;
                        padding: 10px;
                    }}
                """)
            
            # Chart frames (histogram and trend)
            elif ("surface" in current_style and "padding: 5px" in current_style) or \
                 any(chart_child.text() in ["Purchase Distribution", "Weekly Spending Pattern"] 
                     for chart_child in child.findChildren(QLabel)):
                child.setStyleSheet(f"""
                    QFrame {{
                        background-color: {colors['surface']};
                        border: 1px solid {colors['border']};
                        border-radius: 4px;
                        padding: 5px;
                    }}
                """)
        
        # Update stat value labels
        if hasattr(self, 'avg_cost_value'):
            self.avg_cost_value.setStyleSheet(f"color: {colors['primary']}; font-weight: bold;")
        if hasattr(self, 'variance_value'):
            self.variance_value.setStyleSheet(f"color: {colors['primary']}; font-weight: bold;")
        if hasattr(self, 'purchases_value'):
            self.purchases_value.setStyleSheet(f"color: {colors['primary']}; font-weight: bold;")
        if hasattr(self, 'weekly_freq_value'):
            self.weekly_freq_value.setStyleSheet(f"color: {colors['primary']}; font-weight: bold;")
        
        # Update chart frame styling and chart title labels
        for child in self.findChildren(QLabel):
            if child.text() in ["Purchase Distribution", "Weekly Spending Pattern", "Category Correlations"]:
                child.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: bold;")
            # Also update any label that contains category stats info
            elif child.text().startswith("Average Cost") or child.text().startswith("Cost Variance") or \
                 child.text().startswith("Total Purchases") or child.text().startswith("Avg per Week"):
                child.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: bold;")
        
        # Update correlation explanation label
        if hasattr(self, 'correlation_explanation'):
            self.correlation_explanation.setStyleSheet(f"color: {colors['text_secondary']}; font-style: italic; padding: 5px;")
        
        # Update correlation frame styling
        if hasattr(self, 'correlation_frame'):
            self.correlation_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 10px;
                }}
            """)
        
        # Update category management buttons
        if hasattr(self, 'add_category_btn'):
            self.add_category_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['primary']};
                    color: {colors['background']};
                    border: 1px solid {colors['primary_dark'] if colors.get('primary_dark') else colors['border']};
                    border-radius: 4px;
                    padding: 5px 10px;
                    font-weight: bold;
                    margin: 2px;
                }}
                QPushButton:hover {{
                    background-color: {colors.get('primary_dark', colors['primary'])};
                }}
            """)
        
        if hasattr(self, 'remove_category_btn'):
            self.remove_category_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors.get('secondary', colors['surface'])};
                    color: {colors['text_primary']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 5px 10px;
                    margin: 2px;
                }}
                QPushButton:hover {{
                    background-color: {colors.get('hover', colors['surface_variant'])};
                }}
            """)
    
    def open_add_category_dialog(self):
        """Open dialog to add a new category"""
        try:
            from views.dialogs.add_category_dialog import AddCategoryDialog
            
            dialog = AddCategoryDialog(self.transaction_manager, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Refresh the view to show the new category
                self.refresh()
                
        except Exception as e:
            print(f"Error opening add category dialog: {e}")
            import traceback
            traceback.print_exc()
    
    def open_remove_category_dialog(self):
        """Open dialog to remove a category"""
        try:
            from views.dialogs.remove_category_dialog import RemoveCategoryDialog
            
            dialog = RemoveCategoryDialog(self.transaction_manager, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Refresh the view to reflect changes
                self.refresh()
                
        except Exception as e:
            print(f"Error opening remove category dialog: {e}")
            import traceback
            traceback.print_exc()
