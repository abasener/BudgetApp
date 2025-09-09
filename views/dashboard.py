"""
Enhanced Dashboard View - Complete layout matching user diagram
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QCheckBox, QPushButton, QGridLayout)
from PyQt6.QtCore import Qt
from themes import theme_manager
from widgets import (PieChartWidget, LineChartWidget, BarChartWidget, 
                    ProgressChartWidget, HeatmapWidget, AnimatedGifWidget)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class RingChartWidget(QWidget):
    """Ring chart widget for account progress display"""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(2, 2), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        if self.title:
            title_label = QLabel(self.title)
            title_label.setFont(theme_manager.get_font("small"))
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_label)
        
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        self.setFixedSize(100, 120)
        
    def update_data(self, percentage: float, label: str = ""):
        """Update ring chart with percentage data"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Create ring chart (donut)
        colors = theme_manager.get_colors()
        wedges, texts = ax.pie([percentage, 100-percentage], 
                              colors=[colors['primary'], colors['surface_variant']], 
                              startangle=90, counterclock=False)
        
        # Add center hole to make it a ring
        centre_circle = plt.Circle((0,0), 0.60, fc=colors['surface'])
        ax.add_artist(centre_circle)
        
        # Add percentage text in center
        ax.text(0, 0, f'{percentage:.0f}%', ha='center', va='center', 
               fontsize=12, fontweight='bold', color=colors['text_primary'])
        
        ax.axis('equal')
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
        
        if self.title:
            title_label = QLabel(self.title)
            title_label.setFont(theme_manager.get_font("subtitle"))
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_label)
        
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
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


class DashboardView(QWidget):
    def __init__(self, transaction_manager=None, analytics_engine=None):
        super().__init__()
        self.transaction_manager = transaction_manager
        self.analytics_engine = analytics_engine
        
        # Analytics toggle
        self.include_analytics_only = True
        
        # Chart widgets
        self.total_pie_chart = None
        self.weekly_pie_chart = None
        self.stacked_area_chart = None
        self.savings_line_charts = []
        self.ring_charts = []
        self.heatmap_chart = None
        self.gif_widget = None
        self.histogram_chart = None
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
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
        self.analytics_toggle.setChecked(True)
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
        self.weekly_pie_chart = PieChartWidget("")
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
        
        # Chart area under the cards - smaller to give room for taller cards
        chart_area_1 = self.create_placeholder_chart("Chart Area 1")
        chart_area_1.setMaximumHeight(60)  # Shrink chart area
        middle_section.addWidget(chart_area_1)
        
        # Give middle section more space (stretch factor 3)
        top_row.addLayout(middle_section, 3)
        
        # Right section with calculator and stacked chart areas - smaller
        right_section = QVBoxLayout()
        right_section.setSpacing(3)
        
        # Hour calculator button at top - smaller
        self.hour_calc_button = QPushButton("💳 Calc")
        self.hour_calc_button.setMaximumWidth(80)
        self.hour_calc_button.setMaximumHeight(25)
        self.hour_calc_button.clicked.connect(self.open_hour_calculator_popup)
        right_section.addWidget(self.hour_calc_button)
        
        # Two stacked chart areas under calculator - smaller
        chart_area_2 = self.create_placeholder_chart("Chart Area 2")
        chart_area_2.setMaximumHeight(60)
        right_section.addWidget(chart_area_2)
        
        chart_area_3 = self.create_placeholder_chart("Chart Area 3")
        chart_area_3.setMaximumHeight(60)
        right_section.addWidget(chart_area_3)
        
        # Give right section less space (stretch factor 1)
        top_row.addLayout(right_section, 1)
        
        main_layout.addLayout(top_row)
        
        # THIRD ROW - Stacked area chart | Two line plots for savings
        middle_row = QHBoxLayout()
        middle_row.setSpacing(5)
        
        # Stacked percentage plot
        self.stacked_area_chart = StackedAreaWidget("Category % per Week")
        self.stacked_area_chart.setMinimumHeight(300)  # Increased by 50%
        middle_row.addWidget(self.stacked_area_chart)
        
        # Savings tracking line plots
        savings_container = QVBoxLayout()
        for i in range(2):
            line_chart = LineChartWidget(f"Savings Rate {i+1}")
            line_chart.setMinimumHeight(142)  # Increased by 50%
            line_chart.setMaximumHeight(142)  # Increased by 50%
            self.savings_line_charts.append(line_chart)
            savings_container.addWidget(line_chart)
        
        middle_row.addLayout(savings_container)
        
        main_layout.addLayout(middle_row)
        
        # BOTTOM ROW - Ring charts | GIF | Heatmap | Histogram
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(5)
        
        # Three ring charts for account progress
        rings_container = QHBoxLayout()
        rings_container.setSpacing(3)
        for i in range(3):
            ring_chart = RingChartWidget(f"Account {i+1}")
            self.ring_charts.append(ring_chart)
            rings_container.addWidget(ring_chart)
        
        bottom_row.addLayout(rings_container)
        
        # Central GIF holder
        self.gif_widget = AnimatedGifWidget("dashboard", (150, 100))
        bottom_row.addWidget(self.gif_widget)
        
        # Day/Category heatmap
        self.heatmap_chart = HeatmapWidget("Spending by Day/Category")
        self.heatmap_chart.setMinimumWidth(200)
        self.heatmap_chart.setMaximumHeight(150)
        bottom_row.addWidget(self.heatmap_chart)
        
        # Histogram for savings values
        self.histogram_chart = BarChartWidget("Savings Distribution")
        self.histogram_chart.setMinimumWidth(150)
        self.histogram_chart.setMaximumHeight(150)
        bottom_row.addWidget(self.histogram_chart)
        
        main_layout.addLayout(bottom_row)
        
        self.setLayout(main_layout)
        
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
        content_label.setFont(theme_manager.get_font("mono"))
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
    
    def open_hour_calculator_popup(self):
        """Open hour calculator dialog (placeholder)"""
        # TODO: Implement hour calculator dialog
        print("Hour calculator clicked - dialog not implemented yet")
    
    def refresh(self):
        """Refresh all dashboard data and charts"""
        if not self.transaction_manager or not self.analytics_engine:
            self.set_error_state("Services not available")
            return
        
        try:
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
            self.update_histogram()
            
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
            
            # Get current week transactions
            all_transactions = self.transaction_manager.get_all_transactions()
            current_week_spending = [
                t for t in all_transactions 
                if t.transaction_type == "spending" and 
                   t.date >= week_start.date() and
                   (not self.include_analytics_only or not getattr(t, 'is_abnormal', False))
            ]
            
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
            
            # Get all categories and colors
            categories = ["Education", "Miscellaneous", "Shopping", "Entertainment", "Utilities", 
                         "Personal", "Transport", "Healthcare", "Food"]
            colors = theme_manager.get_chart_colors()
            
            for i, category in enumerate(categories):  # Show all categories
                color = colors[i % len(colors)]
                
                key_item = QLabel(f"● {category}")
                key_item.setStyleSheet(f"color: {color}; font-size: 11px; padding: 2px;")
                self.category_key_layout.addWidget(key_item)
                
        except Exception as e:
            print(f"Error updating category key: {e}")
    
    def update_pie_charts(self):
        """Update both pie charts with different data sources"""
        try:
            # Get ALL-TIME spending data by category for the big pie chart
            all_time_category_spending = self.analytics_engine.analyze_spending_by_category(self.include_analytics_only)
            
            # Update total spending pie chart (all-time percentages)
            if self.total_pie_chart and all_time_category_spending:
                self.total_pie_chart.update_data(all_time_category_spending, "All-Time Spending")
            
            # Get CURRENT WEEK spending data for the small pie chart
            from datetime import datetime, timedelta
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())  # Monday of current week
            
            # Get transactions for current week only
            all_transactions = self.transaction_manager.get_all_transactions()
            current_week_transactions = [
                t for t in all_transactions 
                if t.transaction_type == "spending" and 
                   t.date >= week_start.date() and
                   (not self.include_analytics_only or not getattr(t, 'is_abnormal', False))
            ]
            
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
                    # No spending this week - show sample data so user can see the chart works
                    print(f"No current week spending found. Week start: {week_start.date()}, Today: {today.date()}")
                    # Add some sample data for demonstration
                    sample_data = {
                        "Food": 45.0,
                        "Transport": 25.0, 
                        "Entertainment": 30.0,
                        "Shopping": 60.0
                    }
                    print(f"Using sample data for current week: {sample_data}")
                    self.weekly_pie_chart.update_data(sample_data, "This Week Spending")
                
        except Exception as e:
            print(f"Error updating pie charts: {e}")
    
    def update_stacked_area_chart(self):
        """Update stacked area chart with real weekly category percentages"""
        try:
            from datetime import datetime, timedelta
            
            # Get all spending transactions
            all_transactions = self.transaction_manager.get_all_transactions()
            spending_transactions = [
                t for t in all_transactions 
                if t.transaction_type == "spending" and
                   (not self.include_analytics_only or not getattr(t, 'is_abnormal', False))
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
            # Generate sample savings data
            for i, chart in enumerate(self.savings_line_charts):
                if chart:
                    # Sample data showing savings rate over weeks
                    savings_data = {f"Savings Rate": [(j, 0.05 + 0.01*j + i*0.01) for j in range(25)]}
                    chart.update_data(savings_data, "Month", "Savings Rate %")
                    
        except Exception as e:
            print(f"Error updating savings line charts: {e}")
    
    def update_ring_charts(self):
        """Update ring charts showing account progress"""
        try:
            accounts = self.transaction_manager.get_all_accounts()
            
            for i, ring_chart in enumerate(self.ring_charts):
                if i < len(accounts):
                    account = accounts[i]
                    if account.goal_amount > 0:
                        percentage = min(100, (account.running_total / account.goal_amount) * 100)
                    else:
                        percentage = 22  # Default display value
                    ring_chart.update_data(percentage, account.name)
                else:
                    ring_chart.update_data(22, f"Account {i+1}")
                    
        except Exception as e:
            print(f"Error updating ring charts: {e}")
    
    def update_heatmap(self):
        """Update day/category heatmap"""
        try:
            # Generate sample heatmap data
            heatmap_data = {
                "Food": [50, 30, 40, 60, 80, 90, 70],
                "Transport": [20, 25, 15, 30, 35, 40, 25],
                "Shopping": [10, 45, 20, 25, 15, 60, 35],
                "Entertainment": [5, 10, 80, 15, 20, 100, 90]
            }
            
            if self.heatmap_chart:
                self.heatmap_chart.update_data(heatmap_data, "Day", "Category")
                
        except Exception as e:
            print(f"Error updating heatmap: {e}")
    
    def update_histogram(self):
        """Update histogram of savings account values"""
        try:
            # Generate sample histogram data
            histogram_data = {
                "$0-500": 2,
                "$500-1K": 3,
                "$1K-2K": 5,
                "$2K-5K": 2,
                "$5K+": 1
            }
            
            if self.histogram_chart:
                self.histogram_chart.update_data(histogram_data, "Range", "Count")
                
        except Exception as e:
            print(f"Error updating histogram: {e}")
    
    def on_theme_changed(self, theme_id):
        """Handle theme change for dashboard"""
        try:
            self.refresh()
        except Exception as e:
            print(f"Error applying theme to dashboard: {e}")