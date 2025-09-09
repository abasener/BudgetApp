"""
Chart Widget - Matplotlib integration with PyQt6 and theme support
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from themes import theme_manager
import numpy as np


class BaseChartWidget(QWidget):
    """Base class for matplotlib chart widgets with theme support"""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(8, 6), tight_layout=True)
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
            title_label = QLabel(self.title)
            title_label.setFont(theme_manager.get_font("subtitle"))
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_label)
        
        # Add canvas
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
        
        # Remove widget border/frame styling
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
            # Show "No data" message
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No spending data available', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=14, color=theme_manager.get_color('text_secondary'))
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
            if "Savings Rate" in self.title:
                # Remove axis labels and legends for savings charts
                ax.grid(True, alpha=0.3)
                
                # Remove x-axis ticks for top savings chart
                if "1" in self.title:
                    ax.set_xticks([])
                else:
                    # Bottom chart keeps x-axis labels
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
            matrix = np.zeros((len(categories), len(days)))
            
            for i, category in enumerate(categories):
                amounts = data[category]
                for j, amount in enumerate(amounts[:len(days)]):
                    matrix[i, j] = amount
            
            # Create heatmap
            colors = theme_manager.get_colors()
            im = ax.imshow(matrix, cmap='viridis', aspect='auto')
            
            # Set ticks and labels
            ax.set_xticks(range(len(days)))
            ax.set_xticklabels(days)
            ax.set_yticks(range(len(categories)))
            ax.set_yticklabels(categories)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Amount ($)', color=colors['text_primary'])
            
            # Style text
            ax.set_xlabel(xlabel, color=colors['text_primary'])
            ax.set_ylabel(ylabel, color=colors['text_primary'])
            
            # Rotate x labels
            plt.setp(ax.get_xticklabels(), rotation=0, ha='center')
        
        self.apply_theme()
        self.canvas.draw()