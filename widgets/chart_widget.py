"""
Chart Widget - Matplotlib integration with PyQt6 and theme support
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from themes import theme_manager
import numpy as np


class BaseChartWidget(QWidget):
    """Base class for matplotlib chart widgets with theme support"""
    
    # Signal emitted when title is clicked (for savings rate charts)
    title_clicked = pyqtSignal()
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.title_label = None
        self.is_savings_rate_chart = "Savings Rate" in title  # Track savings rate charts permanently
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(8, 6), tight_layout=True)
        # Extra tight margins for heatmap, normal for others
        if "Spending Heatmap" in title or title == "":
            self.figure.subplots_adjust(left=0.15, right=0.99, top=0.99, bottom=0.01)
        else:
            self.figure.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
        self.canvas = FigureCanvas(self.figure)
        
        self.init_ui()
        self.apply_theme()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.on_theme_changed)
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove all margins to eliminate white borders
        layout.setSpacing(0)  # Remove spacing to eliminate white borders
        
        # Add title if provided
        if self.title:
            # For savings rate charts, use a clickable button
            if self.is_savings_rate_chart:
                self.title_label = QPushButton(self.title)
                self.title_label.setFont(theme_manager.get_font("subtitle"))
                self.title_label.setCursor(Qt.CursorShape.PointingHandCursor)
                self.title_label.clicked.connect(self.on_title_clicked)
            else:
                # For other charts, use a regular label
                self.title_label = QLabel(self.title)
                self.title_label.setFont(theme_manager.get_font("subtitle"))
                self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Apply simple styling to both labels and buttons
            colors = theme_manager.get_colors()
            if self.is_savings_rate_chart:
                # Simple button styling for clickable headers
                self.title_label.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        border: 1px solid {colors['border']};
                        border-radius: 4px;
                        padding: 2px 4px;
                        margin: 1px;
                        color: {colors['text_primary']};
                    }}
                    QPushButton:hover {{
                        background-color: {colors['primary']};
                        color: {colors['background']};
                        border: 1px solid {colors.get('primary_dark', colors['primary'])};
                    }}
                """)
            else:
                # Regular label styling
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
            layout.addWidget(self.title_label)
        
        # Add canvas
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
        
        # Remove widget border/frame styling but keep chart backgrounds
        self.setStyleSheet("border: none; background: transparent;")
    
    def apply_theme(self):
        """Apply current theme to the chart"""
        colors = theme_manager.get_colors()
        
        # Set matplotlib theme
        self.figure.patch.set_facecolor(colors['surface'])
        
        # Update all axes
        for ax in self.figure.get_axes():
            ax.set_facecolor(colors['surface'])
            ax.tick_params(colors=colors['text_primary'])
            
            # Remove borders for savings rate charts
            if hasattr(self, 'title') and "Savings Rate" in self.title:
                ax.spines['bottom'].set_color('none')
                ax.spines['top'].set_color('none')
                ax.spines['right'].set_color('none')
                ax.spines['left'].set_color('none')
            else:
                ax.spines['bottom'].set_color(colors['border'])
                ax.spines['top'].set_color(colors['border'])
                ax.spines['right'].set_color(colors['border'])
                ax.spines['left'].set_color(colors['border'])
            
            ax.xaxis.label.set_color(colors['text_primary'])
            ax.yaxis.label.set_color(colors['text_primary'])
            ax.title.set_color(colors['text_primary'])
        
        self.canvas.draw()
    
    def on_theme_changed(self, theme_id):
        """Handle theme change"""
        self.apply_theme()
        # Update title label styling with new theme colors
        self.update_title_styling()
    
    def update_title_styling(self):
        """Update title label styling with current theme colors"""
        if not self.title_label:
            return
            
        colors = theme_manager.get_colors()
        if self.is_savings_rate_chart:
            # Update button styling for clickable headers with fresh theme colors
            self.title_label.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 2px 4px;
                    margin: 1px;
                    color: {colors['text_primary']};
                }}
                QPushButton:hover {{
                    background-color: {colors['primary']};
                    color: {colors['background']};
                    border: 1px solid {colors.get('primary_dark', colors['primary'])};
                }}
            """)
        else:
            # Update regular label styling with fresh theme colors
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
    
    def on_title_clicked(self):
        """Handle title click for savings rate charts"""
        self.title_clicked.emit()
    
    def update_title(self, new_title: str):
        """Update the chart title"""
        self.title = new_title
        if self.title_label:
            self.title_label.setText(new_title)
            # For buttons, also update the text
            if hasattr(self.title_label, 'setText'):
                self.title_label.setText(new_title)
    
    def clear_chart(self):
        """Clear the chart"""
        self.figure.clear()
        self.canvas.draw()


class PieChartWidget(BaseChartWidget):
    """Pie chart widget for category breakdowns"""
    
    def __init__(self, title: str = "Spending by Category", transparent_background: bool = False, parent=None):
        self.transparent_background = transparent_background
        super().__init__(title, parent)
    
    def update_data(self, data: dict, total_label: str = "Total"):
        """Update pie chart with new data"""
        self.figure.clear()
        
        if not data or not any(data.values()):
            # Show completely blank chart - no text
            ax = self.figure.add_subplot(111)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            # Create pie chart
            ax = self.figure.add_subplot(111)
            
            # Prepare data
            labels = list(data.keys())
            sizes = list(data.values())
            colors = theme_manager.get_chart_colors()[:len(labels)]
            
            # Create pie chart without labels and percentages
            # When autopct=None, pie() only returns wedges and texts (2 values), not autotexts
            wedges, texts = ax.pie(sizes, labels=None, colors=colors, 
                                 autopct=None, startangle=90)
            
            
            # Store data for potential tooltips (basic implementation)
            self.pie_data = list(zip(labels, sizes))
            self.pie_wedges = wedges
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')
            
            # No center labels - clean pie charts only
        
        self.apply_theme()
        self.canvas.draw()
    
    def apply_theme(self):
        """Apply current theme to the chart, with optional transparency"""
        if self.transparent_background:
            # Set transparent backgrounds
            self.figure.patch.set_facecolor('none')  # Transparent figure background
            self.canvas.setStyleSheet("background: transparent;")  # Transparent canvas
            
            # Make axes transparent too
            for ax in self.figure.get_axes():
                ax.set_facecolor('none')  # Transparent axes background
                ax.tick_params(colors=theme_manager.get_color('text_primary'))
                # Hide spines for cleaner transparent look
                for spine in ax.spines.values():
                    spine.set_visible(False)
        else:
            # Use the default theme application from BaseChartWidget
            super().apply_theme()
    
    def on_theme_changed(self, theme_id):
        """Handle theme change and refresh pie chart colors"""
        # Call parent theme change
        super().on_theme_changed(theme_id)
        
        # If we have data, redraw with new theme colors
        if hasattr(self, 'pie_data') and self.pie_data:
            # Recreate the chart with new colors
            data = {label: value for label, value in self.pie_data}
            self.update_data(data)


class LineChartWidget(BaseChartWidget):
    """Line chart widget for trends over time"""
    
    def __init__(self, title: str = "Spending Trends", parent=None):
        super().__init__(title, parent)
    
    def update_data(self, data: dict, xlabel: str = "Time", ylabel: str = "Amount ($)"):
        """Update line chart with new data
        
        Args:
            data: dict where keys are series names and values are lists of (x, y) tuples
        """
        self.figure.clear()
        
        if not data or not any(data.values()):
            # Show "No data" message
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No trend data available', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=14, color=theme_manager.get_color('text_secondary'))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            ax = self.figure.add_subplot(111)
            colors = theme_manager.get_chart_colors()
            
            # Plot each series with different styles for secondary lines
            for i, (series_name, series_data) in enumerate(data.items()):
                if series_data:
                    x_vals, y_vals = zip(*series_data)
                    color = colors[i % len(colors)]
                    
                    # Check if x-axis contains dates (for bill charts)
                    import datetime
                    has_dates = len(x_vals) > 0 and isinstance(x_vals[0], (datetime.date, datetime.datetime))
                    
                    # Main "Running Total" line gets full styling with markers
                    if series_name == "Running Total":
                        ax.plot(x_vals, y_vals, marker='o', label=series_name, 
                               color=color, linewidth=2, markersize=4)
                    # Account Balance lines (savings accounts) get clean line style without markers
                    elif series_name == "Account Balance":
                        ax.plot(x_vals, y_vals, marker='', label=series_name, 
                               color=color, linewidth=2)
                    else:
                        # Secondary lines (Weekly Saved, Weekly Paycheck) get thinner, different colors
                        secondary_colors = [colors[3], colors[4]]  # Use different colors from chart palette
                        secondary_color = secondary_colors[(i-1) % len(secondary_colors)]
                        ax.plot(x_vals, y_vals, marker='', label=series_name, 
                               color=secondary_color, linewidth=1, alpha=0.7)
                    
                    # Format x-axis for dates (for Running Total and Account Balance)
                    if has_dates and (series_name == "Running Total" or series_name == "Account Balance"):
                        import matplotlib.dates as mdates
                        
                        # Handle date formatting differently for each series type
                        if len(x_vals) > 1:
                            if series_name == "Running Total":
                                # Only show ticks where running total actually changes
                                change_points = []
                                change_dates = []
                                
                                for j in range(len(y_vals)):
                                    if j == 0 or y_vals[j] != y_vals[j-1]:  # First point or value changed
                                        change_points.append(j)
                                        change_dates.append(x_vals[j])
                                
                                # Limit to max 100 ticks
                                if len(change_dates) > 100:
                                    step = len(change_dates) // 100
                                    change_dates = change_dates[::step]
                                
                                # Set custom tick locations
                                ax.set_xticks(change_dates)
                            
                            elif series_name == "Account Balance":
                                # For Account Balance, show evenly spaced dates
                                # Show at most 20 ticks, evenly spaced
                                if len(x_vals) > 20:
                                    step = len(x_vals) // 20
                                    tick_dates = x_vals[::step]
                                else:
                                    tick_dates = x_vals
                                
                                ax.set_xticks(tick_dates)
                            
                            # Apply date formatting to both
                            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
                        else:
                            # Single point - just show that date
                            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Clean formatting - no labels for savings charts
            if self.is_savings_rate_chart:
                # Remove axis labels and legends for savings charts
                
                # Remove x-axis ticks for top savings chart but add vertical grid lines
                if "1" in self.title:
                    ax.set_xticks([])
                    ax.grid(True, alpha=0.3, axis='y')  # Only horizontal grid lines
                    ax.grid(True, alpha=0.2, axis='x')  # Light vertical grid lines
                else:
                    # Bottom chart keeps x-axis labels
                    ax.grid(True, alpha=0.3)
                    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            else:
                # Keep formatting for other line charts
                ax.set_xlabel(xlabel)
                ax.set_ylabel(ylabel)
                ax.grid(True, alpha=0.3)
                
                # Only show legend if we have axis labels (bill charts have empty labels)
                if xlabel and ylabel:
                    ax.legend()
                
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.apply_theme()
        self.canvas.draw()


class BarChartWidget(BaseChartWidget):
    """Bar chart widget for categorical data"""
    
    def __init__(self, title: str = "Spending Analysis", parent=None):
        super().__init__(title, parent)
    
    def update_data(self, data: dict, xlabel: str = "Category", ylabel: str = "Amount ($)", 
                   horizontal: bool = False):
        """Update bar chart with new data"""
        self.figure.clear()
        
        if not data or not any(data.values()):
            # Show "No data" message
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=14, color=theme_manager.get_color('text_secondary'))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            ax = self.figure.add_subplot(111)
            
            # Prepare data
            labels = list(data.keys())
            values = list(data.values())
            colors = theme_manager.get_chart_colors()[:len(labels)]
            
            # Create bar chart
            if horizontal:
                bars = ax.barh(labels, values, color=colors)
                ax.set_xlabel(ylabel)
                ax.set_ylabel(xlabel)
            else:
                bars = ax.bar(labels, values, color=colors)
                ax.set_xlabel(xlabel)
                ax.set_ylabel(ylabel)
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                if horizontal:
                    ax.text(value + max(values) * 0.01, bar.get_y() + bar.get_height()/2, 
                           f'${value:.0f}', ha='left', va='center', fontsize=9)
                else:
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values) * 0.01,
                           f'${value:.0f}', ha='center', va='bottom', fontsize=9)
            
            ax.grid(True, alpha=0.3, axis='y' if not horizontal else 'x')
        
        self.apply_theme()
        self.canvas.draw()


class ProgressChartWidget(BaseChartWidget):
    """Progress chart for account goals"""
    
    def __init__(self, title: str = "Account Goals", parent=None):
        super().__init__(title, parent)
    
    def update_data(self, accounts_data: list):
        """Update progress chart with account goal data
        
        Args:
            accounts_data: list of dicts with 'name', 'current', 'goal' keys
        """
        self.figure.clear()
        
        if not accounts_data:
            # Show "No data" message
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No account goals set', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=14, color=theme_manager.get_color('text_secondary'))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            ax = self.figure.add_subplot(111)
            colors = theme_manager.get_colors()
            
            # Filter accounts with goals
            accounts_with_goals = [acc for acc in accounts_data if acc.get('goal', 0) > 0]
            
            if not accounts_with_goals:
                ax.text(0.5, 0.5, 'No account goals set', 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=14, color=colors['text_secondary'])
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
            else:
                # Create horizontal progress bars
                y_positions = range(len(accounts_with_goals))
                names = [acc['name'] for acc in accounts_with_goals]
                
                for i, account in enumerate(accounts_with_goals):
                    current = account.get('current', 0)
                    goal = account.get('goal', 1)
                    progress = min(100, (current / goal) * 100) if goal > 0 else 0
                    
                    # Background bar (goal)
                    ax.barh(i, 100, color=colors['surface_variant'], alpha=0.3, height=0.6)
                    
                    # Progress bar
                    bar_color = colors['success'] if progress >= 100 else colors['primary']
                    ax.barh(i, progress, color=bar_color, height=0.6)
                    
                    # Add text labels
                    ax.text(progress + 2, i, f'${current:.0f} / ${goal:.0f} ({progress:.1f}%)',
                           va='center', fontsize=9, color=colors['text_primary'])
                
                ax.set_yticks(y_positions)
                ax.set_yticklabels(names)
                ax.set_xlabel('Progress (%)')
                ax.set_xlim(0, 110)
                ax.grid(True, alpha=0.3, axis='x')
        
        self.apply_theme()
        self.canvas.draw()


class HeatmapWidget(BaseChartWidget):
    """Heatmap widget for spending patterns by day/category"""
    
    def __init__(self, title: str = "Spending Heatmap", parent=None):
        super().__init__(title, parent)
    
    def update_data(self, data: dict, xlabel: str = "Day", ylabel: str = "Category"):
        """Update heatmap with spending data
        
        Args:
            data: dict where keys are categories and values are lists of daily amounts
        """
        self.figure.clear()
        
        if not data or not any(data.values()):
            # Show "No data" message
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No heatmap data available', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=14, color=theme_manager.get_color('text_secondary'))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            ax = self.figure.add_subplot(111)
            
            # Prepare data matrix
            categories = list(data.keys())
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            # Create matrix (categories x days)
            import numpy as np
            from matplotlib.colors import LinearSegmentedColormap
            
            matrix = np.zeros((len(categories), len(days)))
            
            for i, category in enumerate(categories):
                amounts = data[category]
                for j, amount in enumerate(amounts[:len(days)]):
                    matrix[i, j] = amount
            
            # Create custom colormap using accent color (primary)
            colors = theme_manager.get_colors()
            primary_color = colors['primary']
            surface_color = colors['surface']
            
            # Create colormap from surface color to primary color
            custom_colors = [surface_color, primary_color]
            custom_cmap = LinearSegmentedColormap.from_list('custom', custom_colors)
            
            # Create heatmap with custom colormap
            im = ax.imshow(matrix, cmap=custom_cmap, aspect='auto')
            
            # Set ticks and labels - NO x-axis labels for cleaner look
            ax.set_xticks([])  # Remove x-axis ticks completely
            ax.set_yticks(range(len(categories)))
            ax.set_yticklabels(categories, fontsize=9)
            
            # NO colorbar/legend - removed for cleaner look
            
            # NO axis labels - removed for cleaner look
            
            # Style tick labels
            ax.tick_params(colors=colors['text_primary'])
        
        self.apply_theme()
        self.canvas.draw()


class HistogramWidget(BaseChartWidget):
    """Histogram widget for purchase size distribution"""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(title, parent)
        # Override figure settings for better histogram display with minimal padding
        self.figure.subplots_adjust(left=0.05, right=0.95, top=0.90, bottom=0.20)
    
    def update_data(self, purchase_amounts: list, num_buckets: int = 10):
        """Update histogram with purchase amounts
        
        Args:
            purchase_amounts: list of purchase amounts (floats)
            num_buckets: number of histogram buckets
        """
        self.figure.clear()
        
        if not purchase_amounts or len(purchase_amounts) == 0:
            # Show empty chart with just axes
            ax = self.figure.add_subplot(111)
            ax.set_xlim(0, 100)  # Default range
            ax.set_ylim(0, 1)
            ax.grid(True, alpha=0.3)
            ax.set_xticks([])  # No x-axis labels for empty chart
            ax.set_yticks([])  # No y-axis
        else:
            ax = self.figure.add_subplot(111)
            
            # Calculate histogram
            import numpy as np
            max_amount = max(purchase_amounts)
            min_amount = 0  # Start from 0
            
            # Create evenly spaced bins
            bins = np.linspace(min_amount, max_amount, num_buckets + 1)
            
            # Create histogram
            counts, bin_edges, patches = ax.hist(purchase_amounts, bins=bins, 
                                               color=theme_manager.get_color('primary'), 
                                               alpha=0.7, edgecolor='none')
            
            # Clean formatting - minimal labels
            ax.grid(True, alpha=0.3, axis='both')
            
            # X-axis with ticks at bucket edges (start/end of each bucket)
            if num_buckets == 20:  # Special handling for 20 buckets to show all edges
                # Show ticks at every bucket edge
                ax.set_xticks(bin_edges)
                # Only label every few ticks to avoid crowding
                tick_labels = []
                for i, edge in enumerate(bin_edges):
                    if i % 4 == 0 or i == len(bin_edges) - 1:  # Show every 4th tick and the last one
                        tick_labels.append(f"${int(edge)}")
                    else:
                        tick_labels.append("")
                ax.set_xticklabels(tick_labels, fontsize=8, rotation=0)
            else:
                # Original behavior for other bucket counts
                x_ticks = [min_amount, max_amount/2, max_amount]
                x_labels = [f"${int(x)}" for x in x_ticks]
                ax.set_xticks(x_ticks)
                ax.set_xticklabels(x_labels, fontsize=9)
            
            # No y-axis labels or ticks
            ax.set_yticks([])
            
            # Set limits with small padding
            ax.set_xlim(min_amount - max_amount*0.02, max_amount + max_amount*0.02)
            ax.set_ylim(0, max(counts) * 1.05 if len(counts) > 0 else 1)
        
        self.apply_theme()
        self.canvas.draw()


class WeeklySpendingTrendWidget(BaseChartWidget):
    """Weekly spending trend widget showing daily spending patterns across weeks"""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(title, parent)
        # Override figure settings for clean trend display
        self.figure.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.10)
    
    def update_data(self, weekly_spending_data: dict):
        """Update with weekly spending data
        
        Args:
            weekly_spending_data: dict where keys are week identifiers and 
                                values are lists of 7 daily amounts [Mon, Tue, Wed, Thu, Fri, Sat, Sun]
        """
        self.figure.clear()
        
        if not weekly_spending_data:
            # Show empty chart with grid
            ax = self.figure.add_subplot(111)
            ax.set_xlim(0, 6)  # 0-6 for 7 days
            ax.set_ylim(0, 100)  # Default range
            ax.grid(True, alpha=0.3)
            ax.set_xticks(range(7))
            ax.set_xticklabels(['M', 'T', 'W', 'T', 'F', 'S', 'S'], fontsize=8)
            ax.set_yticks([])  # No y-axis labels
        else:
            ax = self.figure.add_subplot(111)
            
            # Get color for all lines
            line_color = theme_manager.get_color('primary')
            
            # Plot each week as a semi-transparent line
            all_amounts = []  # To calculate y-axis range
            daily_totals = [0.0] * 7  # Sum for average calculation
            week_count = 0
            
            for week_id, daily_amounts in weekly_spending_data.items():
                if len(daily_amounts) == 7:  # Ensure we have all 7 days
                    x_values = list(range(7))  # 0-6 for Mon-Sun
                    y_values = [float(amount) for amount in daily_amounts]
                    
                    # Plot line with 30% alpha
                    ax.plot(x_values, y_values, color=line_color, alpha=0.3, 
                           linewidth=1.5, marker='o', markersize=2)
                    
                    all_amounts.extend(y_values)
                    
                    # Add to daily totals for average
                    for i, amount in enumerate(y_values):
                        daily_totals[i] += amount
                    week_count += 1
            
            # Calculate and plot average line if we have data
            if week_count > 0:
                daily_averages = [total / week_count for total in daily_totals]
                
                # Get secondary color (warning/accent color)
                secondary_color = theme_manager.get_color('warning')  # Usually orange/yellow
                if not secondary_color or secondary_color == line_color:
                    # Fallback to a different color if warning not available
                    secondary_color = theme_manager.get_color('accent')
                if not secondary_color or secondary_color == line_color:
                    # Final fallback - use a contrasting color
                    secondary_color = '#FFA500'  # Orange
                
                # Plot average line - thinner, 100% alpha, on top
                ax.plot(x_values, daily_averages, color=secondary_color, alpha=1.0, 
                       linewidth=1.0, linestyle='-', zorder=10)  # zorder puts it on top
            
            # Set up axes
            ax.set_xlim(-0.2, 6.2)  # Small padding on x-axis
            
            if all_amounts:
                max_amount = max(all_amounts)
                ax.set_ylim(0, max_amount * 1.05)  # 5% padding on top
            else:
                ax.set_ylim(0, 100)  # Default range
            
            # Clean formatting
            ax.grid(True, alpha=0.3)
            
            # X-axis labels (days of week)
            ax.set_xticks(range(7))
            ax.set_xticklabels(['M', 'T', 'W', 'T', 'F', 'S', 'S'], fontsize=8)
            
            # No y-axis labels
            ax.set_yticks([])
        
        self.apply_theme()
        self.canvas.draw()


class BoxPlotWidget(BaseChartWidget):
    """Box and whisker plot widget for category spending distributions"""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(title, parent)
        # Override figure settings for horizontal box plot
        self.figure.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.10)
    
    def update_data(self, category_spending_data: dict):
        """Update with category spending distributions
        
        Args:
            category_spending_data: dict where keys are category names and 
                                  values are lists of spending amounts for that category
        """
        self.figure.clear()
        
        if not category_spending_data:
            # Show empty chart
            ax = self.figure.add_subplot(111)
            ax.set_xlim(0, 100)  # Default range
            ax.set_ylim(-1, 1)
            ax.grid(True, alpha=0.3, axis='x')  # Only vertical grid lines
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            ax = self.figure.add_subplot(111)
            
            # Use ALL categories from the data (not hardcoded list)
            # Sort by total spending to show most important categories first
            category_totals = {cat: sum(amounts) for cat, amounts in category_spending_data.items()}
            categories_with_data = sorted(category_totals.keys(), key=lambda x: category_totals[x], reverse=True)
            chart_colors = theme_manager.get_chart_colors()
            
            if categories_with_data:
                # Prepare data for box plot
                data_lists = []
                colors = []
                positions = []
                
                for i, category in enumerate(categories_with_data):
                    spending_amounts = [float(amount) for amount in category_spending_data[category] if amount > 0]
                    if spending_amounts:  # Only add if there's actual data
                        data_lists.append(spending_amounts)
                        # Assign colors sequentially to all categories
                        colors.append(chart_colors[i % len(chart_colors)])
                        positions.append(i)
                
                if data_lists:
                    # Create horizontal box plot - no outliers
                    box_parts = ax.boxplot(data_lists, positions=positions, vert=False, 
                                         patch_artist=True, widths=0.6, showfliers=False)
                    
                    # Color the boxes with category colors
                    for patch, color in zip(box_parts['boxes'], colors):
                        patch.set_facecolor(color)
                        patch.set_alpha(0.7)  # Slight transparency
                        patch.set_edgecolor(color)
                    
                    # Style whiskers, caps, and medians with subtle color
                    # Use text_secondary or border color for whiskers instead of white
                    whisker_color = theme_manager.get_color('text_secondary')
                    if not whisker_color:
                        whisker_color = theme_manager.get_color('border')
                    if not whisker_color:
                        whisker_color = '#808080'  # Fallback gray
                    
                    for element in ['whiskers', 'medians', 'caps']:
                        if element in box_parts:
                            for item in box_parts[element]:
                                item.set_color(whisker_color)
                                item.set_alpha(0.8)
                    
                    # Set up axes based on box plot whiskers (excluding outliers)
                    if data_lists:
                        # Calculate max whisker end for each category (Q3 + 1.5*IQR)
                        import numpy as np
                        max_whisker_ends = []

                        for amounts in data_lists:
                            q1, q3 = np.percentile(amounts, [25, 75])
                            iqr = q3 - q1
                            upper_whisker = q3 + 1.5 * iqr
                            # Whisker end is the highest value within the whisker range
                            whisker_end = max([x for x in amounts if x <= upper_whisker], default=q3)
                            max_whisker_ends.append(whisker_end)

                        max_whisker = max(max_whisker_ends) if max_whisker_ends else 100
                        ax.set_xlim(0, max_whisker * 1.1)  # 10% padding beyond whiskers
                    
                    ax.set_ylim(-0.5, len(positions) - 0.5)
                    
                    # Clean formatting
                    ax.grid(True, alpha=0.3, axis='x')  # Only vertical grid lines
                    ax.set_yticks([])  # No y-axis labels
                    ax.set_xticks([])  # No x-axis labels
            else:
                # No valid data - show empty
                ax.set_xlim(0, 100)
                ax.set_ylim(-1, 1)
                ax.grid(True, alpha=0.3, axis='x')
                ax.set_xticks([])
                ax.set_yticks([])
        
        self.apply_theme()
        self.canvas.draw()