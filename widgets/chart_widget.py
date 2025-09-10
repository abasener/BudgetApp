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
                        background-color: {colors['border']};
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
    
    def __init__(self, title: str = "Spending by Category", parent=None):
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
            
            # Plot each series
            for i, (series_name, series_data) in enumerate(data.items()):
                if series_data:
                    x_vals, y_vals = zip(*series_data)
                    color = colors[i % len(colors)]
                    ax.plot(x_vals, y_vals, marker='o', label=series_name, 
                           color=color, linewidth=2, markersize=4)
            
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
            
            # X-axis with dollar amounts - only show a few key values
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