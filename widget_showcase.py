"""
PyQt6 Widget Showcase - A comprehensive demonstration of all available UI elements

This is a standalone testing tool to explore PyQt6 widgets and their variants.
Shows inputs, buttons, layouts, and styling options with dark theme colors.

Dependencies: PyQt6 only (pip install PyQt6)
"""

import sys
import numpy as np
import matplotlib
matplotlib.use('QtAgg')  # Use QtAgg for PyQt6 compatibility
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFormLayout, QScrollArea, QLabel, QPushButton, QLineEdit, QTextEdit,
    QPlainTextEdit, QCheckBox, QRadioButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QSlider, QDial, QProgressBar, QDateEdit, QTimeEdit, QDateTimeEdit,
    QGroupBox, QFrame, QTabWidget, QListWidget, QTableWidget, QTreeWidget,
    QTableWidgetItem, QTreeWidgetItem, QSplitter, QToolBar, QStatusBar,
    QMenuBar, QMenu, QToolButton, QButtonGroup, QLCDNumber, QCalendarWidget,
    QFontComboBox, QColorDialog, QFileDialog, QMessageBox, QInputDialog,
    QListWidgetItem
)
from PyQt6.QtCore import Qt, QDate, QTime, QDateTime
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette

# Dark theme colors (hardcoded from BudgetApp dark theme)
COLORS = {
    'background': '#1a1a1a',
    'surface': '#2d2d2d',
    'surface_variant': '#3d3d3d',
    'primary': '#4a9eff',
    'secondary': '#90ee90',
    'accent': '#ffaa00',
    'error': '#ff4444',
    'text_primary': '#ffffff',
    'text_secondary': '#b0b0b0',
    'border': '#555555',
    'hover': '#4a4a4a',
    'selected': '#5a5a5a'
}


class WidgetShowcase(QMainWindow):
    """Comprehensive widget showcase with dark theme"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Widget Showcase - Side by Side Comparison")
        self.setGeometry(50, 50, 1800, 900)

        # Track current mode: False = populated (default), True = blank
        self.blank_mode = False

        # Create central widget with vertical layout
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setSpacing(0)
        central_layout.setContentsMargins(0, 0, 0, 0)

        # Add toggle button at the top
        toggle_button = QPushButton("Switch to Plots View")
        toggle_button.setFixedHeight(35)
        toggle_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface_variant']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
                border: 1px solid {COLORS['primary']};
            }}
        """)
        toggle_button.clicked.connect(self.toggle_view)
        central_layout.addWidget(toggle_button)
        self.toggle_button = toggle_button

        # Create main splitter for side-by-side comparison
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter = main_splitter
        main_splitter.setStyleSheet("")  # Ensure splitter has no styling

        # LEFT SIDE - THEMED/STYLED
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Apply theme stylesheet ONLY to left scroll area
        left_scroll.setStyleSheet(self.get_theme_stylesheet())

        left_content = QWidget()
        left_layout = QVBoxLayout(left_content)
        left_layout.setSpacing(20)
        left_layout.setContentsMargins(20, 20, 20, 20)

        # Left title
        left_title = QLabel("🎨 THEMED (Styled)")
        left_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        left_title.setStyleSheet(f"color: {COLORS['primary']}; padding: 10px;")
        left_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(left_title)

        left_subtitle = QLabel("All widgets with custom dark theme styling")
        left_subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px; padding-bottom: 10px;")
        left_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(left_subtitle)

        left_layout.addWidget(self.create_separator())

        # Add all sections to LEFT SIDE (THEMED)
        left_layout.addWidget(self.create_section_header("Buttons", "Clickable elements for user actions. Variants include push buttons, tool buttons, radio buttons, and checkboxes."))
        left_layout.addWidget(self.create_button_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Text Inputs", "Single-line and multi-line text entry fields. Variants include plain text, passwords, numbers, dates, and autocomplete."))
        left_layout.addWidget(self.create_text_input_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Number Inputs", "Specialized inputs for numeric values with increment/decrement buttons and validation."))
        left_layout.addWidget(self.create_number_input_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Selection Widgets", "Widgets for choosing from predefined options: dropdowns, radio buttons, checkboxes."))
        left_layout.addWidget(self.create_selection_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Date & Time Pickers", "Widgets for selecting dates, times, and date-time combinations with built-in calendars."))
        left_layout.addWidget(self.create_datetime_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Sliders & Dials", "Interactive continuous value selectors. Less common but great for volume, brightness, or progress."))
        left_layout.addWidget(self.create_slider_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Display Widgets", "Read-only widgets for showing information: progress bars, LCD numbers, labels."))
        left_layout.addWidget(self.create_display_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Containers & Layouts", "Organizational elements: group boxes, frames, tabs, splitters. Essential for structuring UIs."))
        left_layout.addWidget(self.create_container_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Lists, Tables & Trees", "Data display widgets for showing collections: lists, tables with rows/columns, hierarchical trees."))
        left_layout.addWidget(self.create_data_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Dialogs & Popups", "Modal windows for user interaction: message boxes, file pickers, input dialogs, color pickers."))
        left_layout.addWidget(self.create_dialog_section())
        left_layout.addStretch()

        left_scroll.setWidget(left_content)

        # RIGHT SIDE - NATIVE/UNSTYLED
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.Shape.NoFrame)
        right_scroll.setStyleSheet("")  # Remove all styling from right side

        right_content = QWidget()
        right_content.setStyleSheet("")  # Ensure no styling
        right_layout = QVBoxLayout(right_content)
        right_layout.setSpacing(20)
        right_layout.setContentsMargins(20, 20, 20, 20)

        # Right title
        right_title = QLabel("⚙ NATIVE (Unstyled)")
        right_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        right_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(right_title)

        right_subtitle = QLabel("All widgets with default Qt/Windows appearance")
        right_subtitle.setStyleSheet("font-size: 13px; padding-bottom: 10px;")
        right_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(right_subtitle)

        # Separator line
        sep_right = QFrame()
        sep_right.setFrameShape(QFrame.Shape.HLine)
        sep_right.setFrameShadow(QFrame.Shadow.Sunken)
        right_layout.addWidget(sep_right)

        # Add all sections to RIGHT SIDE (NATIVE)
        right_layout.addWidget(self.create_section_header("Buttons", "Clickable elements for user actions. Variants include push buttons, tool buttons, radio buttons, and checkboxes."))
        right_layout.addWidget(self.create_button_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Text Inputs", "Single-line and multi-line text entry fields. Variants include plain text, passwords, numbers, dates, and autocomplete."))
        right_layout.addWidget(self.create_text_input_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Number Inputs", "Specialized inputs for numeric values with increment/decrement buttons and validation."))
        right_layout.addWidget(self.create_number_input_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Selection Widgets", "Widgets for choosing from predefined options: dropdowns, radio buttons, checkboxes."))
        right_layout.addWidget(self.create_selection_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Date & Time Pickers", "Widgets for selecting dates, times, and date-time combinations with built-in calendars."))
        right_layout.addWidget(self.create_datetime_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Sliders & Dials", "Interactive continuous value selectors. Less common but great for volume, brightness, or progress."))
        right_layout.addWidget(self.create_slider_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Display Widgets", "Read-only widgets for showing information: progress bars, LCD numbers, labels."))
        right_layout.addWidget(self.create_display_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Containers & Layouts", "Organizational elements: group boxes, frames, tabs, splitters. Essential for structuring UIs."))
        right_layout.addWidget(self.create_container_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Lists, Tables & Trees", "Data display widgets for showing collections: lists, tables with rows/columns, hierarchical trees."))
        right_layout.addWidget(self.create_data_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Dialogs & Popups", "Modal windows for user interaction: message boxes, file pickers, input dialogs, color pickers."))
        right_layout.addWidget(self.create_dialog_section())
        right_layout.addStretch()

        right_scroll.setWidget(right_content)

        # Add both sides to splitter
        main_splitter.addWidget(left_scroll)
        main_splitter.addWidget(right_scroll)
        main_splitter.setSizes([900, 900])  # Equal split

        # Store references to scroll areas for toggling
        self.left_scroll = left_scroll
        self.right_scroll = right_scroll

        # Add splitter to central layout
        central_layout.addWidget(main_splitter)

        self.setCentralWidget(central_widget)

    def toggle_view(self):
        """Toggle between widgets and plots views"""
        self.blank_mode = not self.blank_mode

        if self.blank_mode:
            # Switch to plots view
            self.toggle_button.setText("Switch to Widgets View")
            self.show_plots_view()
        else:
            # Switch back to widgets view
            self.toggle_button.setText("Switch to Plots View")
            self.show_widgets_view()

    def show_plots_view(self):
        """Show plots/charts reference view"""
        # Create left side (themed plots)
        plots_left = QScrollArea()
        plots_left.setWidgetResizable(True)
        plots_left.setFrameShape(QFrame.Shape.NoFrame)
        plots_left.setStyleSheet(self.get_theme_stylesheet())

        plots_left_content = QWidget()
        plots_left_layout = QVBoxLayout(plots_left_content)
        plots_left_layout.setSpacing(20)
        plots_left_layout.setContentsMargins(20, 20, 20, 20)

        # Add title
        left_title = QLabel("🎨 STYLED PLOTS")
        left_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        left_title.setStyleSheet(f"color: {COLORS['primary']}; padding: 10px;")
        left_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        plots_left_layout.addWidget(left_title)

        left_subtitle = QLabel("Matplotlib plots with custom dark theme styling")
        left_subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px; padding-bottom: 10px;")
        left_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        plots_left_layout.addWidget(left_subtitle)

        plots_left_layout.addWidget(self.create_separator())

        # Add plot sections to LEFT SIDE (STYLED)
        plots_left_layout.addWidget(self.create_section_header("Basic Line & Scatter", "Fundamental plots for showing trends, relationships, and data points"))
        plots_left_layout.addWidget(self.create_line_scatter_section(styled=True))
        plots_left_layout.addWidget(self.create_separator())

        plots_left_layout.addWidget(self.create_section_header("Bar Charts & Histograms", "Comparing categories and showing distributions"))
        plots_left_layout.addWidget(self.create_bar_hist_section(styled=True))
        plots_left_layout.addWidget(self.create_separator())

        plots_left_layout.addWidget(self.create_section_header("Area & Fill Plots", "Showing cumulative data and filled regions"))
        plots_left_layout.addWidget(self.create_area_section(styled=True))
        plots_left_layout.addWidget(self.create_separator())

        plots_left_layout.addWidget(self.create_section_header("Pie & Donut Charts", "Showing proportions and percentages"))
        plots_left_layout.addWidget(self.create_pie_section(styled=True))
        plots_left_layout.addWidget(self.create_separator())

        plots_left_layout.addWidget(self.create_section_header("Statistical Plots", "Box plots, violin plots, and distributions"))
        plots_left_layout.addWidget(self.create_statistical_section(styled=True))
        plots_left_layout.addWidget(self.create_separator())

        plots_left_layout.addWidget(self.create_section_header("Heatmaps & Confusion Matrix", "2D data visualization and ML metrics"))
        plots_left_layout.addWidget(self.create_heatmap_section(styled=True))
        plots_left_layout.addWidget(self.create_separator())

        plots_left_layout.addWidget(self.create_section_header("Specialty Plots", "Waterfall, step, stem, and other specialized visualizations"))
        plots_left_layout.addWidget(self.create_specialty_section(styled=True))
        plots_left_layout.addWidget(self.create_separator())

        plots_left_layout.addWidget(self.create_section_header("3D Plots", "Three-dimensional visualizations"))
        plots_left_layout.addWidget(self.create_3d_section(styled=True))
        plots_left_layout.addWidget(self.create_separator())

        plots_left_layout.addWidget(self.create_section_header("Advanced Charts", "Bubble, radar, candlestick, and stream plots"))
        plots_left_layout.addWidget(self.create_advanced_section(styled=True))
        plots_left_layout.addWidget(self.create_separator())

        plots_left_layout.addWidget(self.create_section_header("Hierarchical & Set Plots", "Treemap, dendrogram, venn diagrams"))
        plots_left_layout.addWidget(self.create_hierarchical_section(styled=True))
        plots_left_layout.addWidget(self.create_separator())

        plots_left_layout.addWidget(self.create_section_header("Distribution & Comparison", "Ridgeline, parallel coordinates, word cloud"))
        plots_left_layout.addWidget(self.create_distribution_section(styled=True))

        plots_left_layout.addStretch()
        plots_left.setWidget(plots_left_content)

        # Create right side (default plots)
        plots_right = QScrollArea()
        plots_right.setWidgetResizable(True)
        plots_right.setFrameShape(QFrame.Shape.NoFrame)
        plots_right.setStyleSheet("")

        plots_right_content = QWidget()
        plots_right_content.setStyleSheet("")
        plots_right_layout = QVBoxLayout(plots_right_content)
        plots_right_layout.setSpacing(20)
        plots_right_layout.setContentsMargins(20, 20, 20, 20)

        # Add title
        right_title = QLabel("⚙ DEFAULT PLOTS")
        right_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        right_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        plots_right_layout.addWidget(right_title)

        right_subtitle = QLabel("Matplotlib plots with default styling")
        right_subtitle.setStyleSheet("font-size: 13px; padding-bottom: 10px;")
        right_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        plots_right_layout.addWidget(right_subtitle)

        # Separator line
        sep_right = QFrame()
        sep_right.setFrameShape(QFrame.Shape.HLine)
        sep_right.setFrameShadow(QFrame.Shadow.Sunken)
        plots_right_layout.addWidget(sep_right)

        # Add plot sections to RIGHT SIDE (DEFAULT)
        plots_right_layout.addWidget(self.create_section_header("Basic Line & Scatter", "Fundamental plots for showing trends, relationships, and data points"))
        plots_right_layout.addWidget(self.create_line_scatter_section(styled=False))
        plots_right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        plots_right_layout.addWidget(self.create_section_header("Bar Charts & Histograms", "Comparing categories and showing distributions"))
        plots_right_layout.addWidget(self.create_bar_hist_section(styled=False))
        plots_right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        plots_right_layout.addWidget(self.create_section_header("Area & Fill Plots", "Showing cumulative data and filled regions"))
        plots_right_layout.addWidget(self.create_area_section(styled=False))
        plots_right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        plots_right_layout.addWidget(self.create_section_header("Pie & Donut Charts", "Showing proportions and percentages"))
        plots_right_layout.addWidget(self.create_pie_section(styled=False))
        plots_right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        plots_right_layout.addWidget(self.create_section_header("Statistical Plots", "Box plots, violin plots, and distributions"))
        plots_right_layout.addWidget(self.create_statistical_section(styled=False))
        plots_right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        plots_right_layout.addWidget(self.create_section_header("Heatmaps & Confusion Matrix", "2D data visualization and ML metrics"))
        plots_right_layout.addWidget(self.create_heatmap_section(styled=False))
        plots_right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        plots_right_layout.addWidget(self.create_section_header("Specialty Plots", "Waterfall, step, stem, and other specialized visualizations"))
        plots_right_layout.addWidget(self.create_specialty_section(styled=False))
        plots_right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        plots_right_layout.addWidget(self.create_section_header("3D Plots", "Three-dimensional visualizations"))
        plots_right_layout.addWidget(self.create_3d_section(styled=False))
        plots_right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        plots_right_layout.addWidget(self.create_section_header("Advanced Charts", "Bubble, radar, candlestick, and stream plots"))
        plots_right_layout.addWidget(self.create_advanced_section(styled=False))
        plots_right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        plots_right_layout.addWidget(self.create_section_header("Hierarchical & Set Plots", "Treemap, dendrogram, venn diagrams"))
        plots_right_layout.addWidget(self.create_hierarchical_section(styled=False))
        plots_right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        plots_right_layout.addWidget(self.create_section_header("Distribution & Comparison", "Ridgeline, parallel coordinates, word cloud"))
        plots_right_layout.addWidget(self.create_distribution_section(styled=False))

        plots_right_layout.addStretch()
        plots_right.setWidget(plots_right_content)

        # Replace widgets in splitter
        self.main_splitter.replaceWidget(0, plots_left)
        self.main_splitter.replaceWidget(1, plots_right)

        # Store references
        self.left_scroll = plots_left
        self.right_scroll = plots_right

    def show_widgets_view(self):
        """Show populated view with all widgets"""
        # LEFT SIDE - THEMED/STYLED
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.Shape.NoFrame)
        left_scroll.setStyleSheet(self.get_theme_stylesheet())

        left_content = QWidget()
        left_layout = QVBoxLayout(left_content)
        left_layout.setSpacing(20)
        left_layout.setContentsMargins(20, 20, 20, 20)

        # Left title
        left_title = QLabel("🎨 THEMED (Styled)")
        left_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        left_title.setStyleSheet(f"color: {COLORS['primary']}; padding: 10px;")
        left_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(left_title)

        left_subtitle = QLabel("All widgets with custom dark theme styling")
        left_subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px; padding-bottom: 10px;")
        left_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(left_subtitle)

        left_layout.addWidget(self.create_separator())

        # Add all sections to LEFT SIDE (THEMED)
        left_layout.addWidget(self.create_section_header("Buttons", "Clickable elements for user actions. Variants include push buttons, tool buttons, radio buttons, and checkboxes."))
        left_layout.addWidget(self.create_button_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Text Inputs", "Single-line and multi-line text entry fields. Variants include plain text, passwords, numbers, dates, and autocomplete."))
        left_layout.addWidget(self.create_text_input_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Number Inputs", "Specialized inputs for numeric values with increment/decrement buttons and validation."))
        left_layout.addWidget(self.create_number_input_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Selection Widgets", "Widgets for choosing from predefined options: dropdowns, radio buttons, checkboxes."))
        left_layout.addWidget(self.create_selection_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Date & Time Pickers", "Widgets for selecting dates, times, and date-time combinations with built-in calendars."))
        left_layout.addWidget(self.create_datetime_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Sliders & Dials", "Interactive continuous value selectors. Less common but great for volume, brightness, or progress."))
        left_layout.addWidget(self.create_slider_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Display Widgets", "Read-only widgets for showing information: progress bars, LCD numbers, labels."))
        left_layout.addWidget(self.create_display_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Containers & Layouts", "Organizational elements: group boxes, frames, tabs, splitters. Essential for structuring UIs."))
        left_layout.addWidget(self.create_container_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Lists, Tables & Trees", "Data display widgets for showing collections: lists, tables with rows/columns, hierarchical trees."))
        left_layout.addWidget(self.create_data_section())
        left_layout.addWidget(self.create_separator())

        left_layout.addWidget(self.create_section_header("Dialogs & Popups", "Modal windows for user interaction: message boxes, file pickers, input dialogs, color pickers."))
        left_layout.addWidget(self.create_dialog_section())
        left_layout.addStretch()

        left_scroll.setWidget(left_content)

        # RIGHT SIDE - NATIVE/UNSTYLED
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.Shape.NoFrame)
        right_scroll.setStyleSheet("")

        right_content = QWidget()
        right_content.setStyleSheet("")
        right_layout = QVBoxLayout(right_content)
        right_layout.setSpacing(20)
        right_layout.setContentsMargins(20, 20, 20, 20)

        # Right title
        right_title = QLabel("⚙ NATIVE (Unstyled)")
        right_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        right_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(right_title)

        right_subtitle = QLabel("All widgets with default Qt/Windows appearance")
        right_subtitle.setStyleSheet("font-size: 13px; padding-bottom: 10px;")
        right_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(right_subtitle)

        # Separator line
        sep_right = QFrame()
        sep_right.setFrameShape(QFrame.Shape.HLine)
        sep_right.setFrameShadow(QFrame.Shadow.Sunken)
        right_layout.addWidget(sep_right)

        # Add all sections to RIGHT SIDE (NATIVE)
        right_layout.addWidget(self.create_section_header("Buttons", "Clickable elements for user actions. Variants include push buttons, tool buttons, radio buttons, and checkboxes."))
        right_layout.addWidget(self.create_button_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Text Inputs", "Single-line and multi-line text entry fields. Variants include plain text, passwords, numbers, dates, and autocomplete."))
        right_layout.addWidget(self.create_text_input_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Number Inputs", "Specialized inputs for numeric values with increment/decrement buttons and validation."))
        right_layout.addWidget(self.create_number_input_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Selection Widgets", "Widgets for choosing from predefined options: dropdowns, radio buttons, checkboxes."))
        right_layout.addWidget(self.create_selection_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Date & Time Pickers", "Widgets for selecting dates, times, and date-time combinations with built-in calendars."))
        right_layout.addWidget(self.create_datetime_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Sliders & Dials", "Interactive continuous value selectors. Less common but great for volume, brightness, or progress."))
        right_layout.addWidget(self.create_slider_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Display Widgets", "Read-only widgets for showing information: progress bars, LCD numbers, labels."))
        right_layout.addWidget(self.create_display_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Containers & Layouts", "Organizational elements: group boxes, frames, tabs, splitters. Essential for structuring UIs."))
        right_layout.addWidget(self.create_container_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Lists, Tables & Trees", "Data display widgets for showing collections: lists, tables with rows/columns, hierarchical trees."))
        right_layout.addWidget(self.create_data_section())
        right_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        right_layout.addWidget(self.create_section_header("Dialogs & Popups", "Modal windows for user interaction: message boxes, file pickers, input dialogs, color pickers."))
        right_layout.addWidget(self.create_dialog_section())
        right_layout.addStretch()

        right_scroll.setWidget(right_content)

        # Replace widgets in splitter
        self.main_splitter.replaceWidget(0, left_scroll)
        self.main_splitter.replaceWidget(1, right_scroll)

        # Store references
        self.left_scroll = left_scroll
        self.right_scroll = right_scroll

    def get_theme_stylesheet(self) -> str:
        """Get the dark theme stylesheet"""
        stylesheet = f"""
            QMainWindow, QWidget {{
                background-color: {COLORS['background']};
                color: {COLORS['text_primary']};
            }}
            QScrollArea {{
                border: none;
                background-color: {COLORS['background']};
            }}
            QGroupBox {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding: 15px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                color: {COLORS['primary']};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QPushButton {{
                background-color: {COLORS['surface_variant']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['selected']};
            }}
            QPushButton:default {{
                border: 3px solid {COLORS['primary']};
                background-color: {COLORS['surface_variant']};
                font-weight: bold;
            }}
            QPushButton:default:hover {{
                background-color: {COLORS['hover']};
                border: 3px solid {COLORS['primary']};
            }}
            QPushButton:default:pressed {{
                background-color: {COLORS['selected']};
                border: 3px solid {COLORS['primary']};
            }}
            QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox,
            QComboBox, QDateEdit, QTimeEdit, QDateTimeEdit {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 6px;
            }}
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {COLORS['text_primary']};
            }}
            /* Only style checkboxes and radio buttons that explicitly have the themed property */
            QCheckBox[themedStyle="true"], QRadioButton[themedStyle="true"] {{
                color: {COLORS['text_primary']};
                spacing: 8px;
            }}
            QCheckBox[themedStyle="true"]::indicator, QRadioButton[themedStyle="true"]::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {COLORS['border']};
                border-radius: 3px;
                background-color: {COLORS['surface']};
            }}
            QCheckBox[themedStyle="true"]::indicator:checked {{
                background-color: {COLORS['secondary']};
                border-color: {COLORS['secondary']};
            }}
            QRadioButton[themedStyle="true"]::indicator {{
                border-radius: 9px;
            }}
            QRadioButton[themedStyle="true"]::indicator:checked {{
                background-color: {COLORS['primary']};
                border-color: {COLORS['primary']};
            }}
            QSlider::groove:horizontal {{
                background: {COLORS['surface_variant']};
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['primary']};
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }}
            QSlider::groove:vertical {{
                background: {COLORS['surface_variant']};
                width: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:vertical {{
                background: {COLORS['primary']};
                height: 16px;
                margin: 0 -5px;
                border-radius: 8px;
            }}
            QDial {{
                background-color: {COLORS['surface']};
            }}
            QDial::handle {{
                background: {COLORS['primary']};
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
            }}
            QToolButton {{
                background-color: {COLORS['surface_variant']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 6px;
            }}
            QToolButton:hover {{
                background-color: {COLORS['hover']};
            }}
            QToolButton:pressed {{
                background-color: {COLORS['selected']};
            }}
            QLCDNumber {{
                background-color: {COLORS['surface']};
                color: {COLORS['primary']};
                border: 1px solid {COLORS['border']};
            }}
            QCalendarWidget {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
            }}
            QCalendarWidget QAbstractItemView {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                selection-background-color: {COLORS['primary']};
                selection-color: {COLORS['background']};
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background-color: {COLORS['surface_variant']};
            }}
            QCalendarWidget QToolButton {{
                color: {COLORS['text_primary']};
                background-color: {COLORS['surface_variant']};
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: {COLORS['hover']};
            }}
            QProgressBar {{
                background-color: {COLORS['surface_variant']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                text-align: center;
                color: {COLORS['text_primary']};
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['primary']};
                border-radius: 3px;
            }}
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                background: {COLORS['surface']};
            }}
            QTabBar::tab {{
                background: {COLORS['surface_variant']};
                color: {COLORS['text_secondary']};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['primary']};
                color: {COLORS['background']};
            }}
            QTableWidget {{
                background-color: {COLORS['surface']};
                alternate-background-color: {COLORS['surface_variant']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                gridline-color: {COLORS['border']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: {COLORS['background']};
                padding: 6px;
                border: none;
                font-weight: bold;
            }}
            QListWidget, QTreeWidget {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                alternate-background-color: {COLORS['surface_variant']};
            }}
            QFrame[frameShape="4"] {{ /* HLine */
                background-color: {COLORS['border']};
                max-height: 1px;
            }}
            QToolTip {{
                background-color: {COLORS['surface_variant']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                padding: 4px;
            }}
        """
        return stylesheet

    def create_section_header(self, title: str, description: str) -> QWidget:
        """Create a styled section header with title and description"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 10, 0, 10)

        title_label = QLabel(f"📌 {title}")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {COLORS['accent']};")
        title_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px; font-style: italic;")
        desc_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(desc_label)

        return widget

    def create_separator(self) -> QFrame:
        """Create a horizontal separator line"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet(f"background-color: {COLORS['border']};")
        return line

    def create_button_section(self) -> QWidget:
        """Create button showcase section"""
        group = QGroupBox("Button Widgets (QPushButton, QToolButton, QCheckBox, QRadioButton)")
        layout = QVBoxLayout()

        # Standard buttons
        label1 = QLabel("QPushButton Variants:")
        label1.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label1)

        row1 = QHBoxLayout()
        btn1 = QPushButton("Default Button")
        btn1.setToolTip("QPushButton - Standard clickable button")
        row1.addWidget(btn1)

        btn2 = QPushButton("Primary Action")
        btn2.setStyleSheet(f"background-color: {COLORS['primary']}; font-weight: bold;")
        btn2.setToolTip("QPushButton with primary styling")
        row1.addWidget(btn2)

        btn3 = QPushButton("Success")
        btn3.setStyleSheet(f"background-color: {COLORS['secondary']}; color: black;")
        btn3.setToolTip("QPushButton with success/green styling")
        row1.addWidget(btn3)

        btn4 = QPushButton("Danger")
        btn4.setStyleSheet(f"background-color: {COLORS['error']};")
        btn4.setToolTip("QPushButton with error/danger styling")
        row1.addWidget(btn4)

        btn5 = QPushButton("Disabled")
        btn5.setEnabled(False)
        btn5.setToolTip("QPushButton - Disabled state")
        row1.addWidget(btn5)

        row1.addStretch()
        layout.addLayout(row1)

        # Checkboxes
        label2 = QLabel("Checkboxes (QCheckBox):")
        label2.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label2)

        row2 = QHBoxLayout()
        cb1 = QCheckBox("Unchecked")
        cb1.setProperty("themedStyle", "true")
        cb1.setToolTip("QCheckBox - Default unchecked state")
        row2.addWidget(cb1)

        cb2 = QCheckBox("Checked")
        cb2.setChecked(True)
        cb2.setProperty("themedStyle", "true")
        cb2.setToolTip("QCheckBox - Checked state")
        row2.addWidget(cb2)

        cb3 = QCheckBox("Tristate")
        cb3.setTristate(True)
        cb3.setCheckState(Qt.CheckState.PartiallyChecked)
        cb3.setProperty("themedStyle", "true")
        cb3.setToolTip("QCheckBox - Tristate mode (3 states: unchecked, partial, checked)")
        row2.addWidget(cb3)

        cb4 = QCheckBox("Disabled")
        cb4.setEnabled(False)
        cb4.setProperty("themedStyle", "true")
        cb4.setToolTip("QCheckBox - Disabled state")
        row2.addWidget(cb4)

        row2.addStretch()
        layout.addLayout(row2)

        # Radio buttons
        label3 = QLabel("Radio Buttons (QRadioButton) - Only one can be selected in a group:")
        label3.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label3)

        row3 = QHBoxLayout()
        rb1 = QRadioButton("Option 1")
        rb1.setChecked(True)
        rb1.setProperty("themedStyle", "true")
        rb1.setToolTip("QRadioButton - Mutually exclusive selection")
        row3.addWidget(rb1)

        rb2 = QRadioButton("Option 2")
        rb2.setProperty("themedStyle", "true")
        rb2.setToolTip("QRadioButton - Only one radio button in a group can be selected")
        row3.addWidget(rb2)

        rb3 = QRadioButton("Option 3")
        rb3.setProperty("themedStyle", "true")
        row3.addWidget(rb3)

        rb4 = QRadioButton("Disabled")
        rb4.setEnabled(False)
        rb4.setProperty("themedStyle", "true")
        row3.addWidget(rb4)

        row3.addStretch()
        layout.addLayout(row3)

        # Tool buttons
        label4 = QLabel("Tool Buttons (QToolButton) - Compact buttons for toolbars:")
        label4.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label4)

        row4 = QHBoxLayout()
        tb1 = QToolButton()
        tb1.setText("📁")
        tb1.setToolTip("QToolButton - Compact button, often used in toolbars")
        row4.addWidget(tb1)

        tb2 = QToolButton()
        tb2.setText("💾")
        tb2.setToolTip("QToolButton - Can display icons or text")
        row4.addWidget(tb2)

        tb3 = QToolButton()
        tb3.setText("✂")
        tb3.setToolTip("QToolButton - Cut/scissors icon")
        row4.addWidget(tb3)

        tb4 = QToolButton()
        tb4.setText("📋")
        tb4.setToolTip("QToolButton - Clipboard icon")
        row4.addWidget(tb4)

        tb5 = QToolButton()
        tb5.setText("⚙")
        tb5.setToolTip("QToolButton - Settings/gear icon")
        row4.addWidget(tb5)

        row4.addStretch()
        layout.addLayout(row4)

        group.setLayout(layout)
        return group

    def create_text_input_section(self) -> QWidget:
        """Create text input showcase section"""
        group = QGroupBox("Text Input Widgets (QLineEdit, QTextEdit, QPlainTextEdit)")
        layout = QVBoxLayout()

        # Single-line inputs
        label_sli = QLabel("Single-Line Inputs (QLineEdit):")
        label_sli.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label_sli)

        form = QFormLayout()
        form.setSpacing(10)

        le1 = QLineEdit()
        le1.setPlaceholderText("Normal text input")
        le1.setToolTip("QLineEdit - Single-line text input")
        form.addRow("Default:", le1)

        le2 = QLineEdit()
        le2.setPlaceholderText("Password")
        le2.setEchoMode(QLineEdit.EchoMode.Password)
        le2.setToolTip("QLineEdit with EchoMode.Password - Characters hidden")
        form.addRow("Password:", le2)

        le3 = QLineEdit()
        le3.setText("Read-only text")
        le3.setReadOnly(True)
        le3.setToolTip("QLineEdit - ReadOnly mode")
        form.addRow("Read-Only:", le3)

        le4 = QLineEdit()
        le4.setPlaceholderText("Max 10 characters")
        le4.setMaxLength(10)
        le4.setToolTip("QLineEdit with maxLength=10")
        form.addRow("Max Length:", le4)

        le5 = QLineEdit()
        le5.setPlaceholderText("Enter email")
        le5.setToolTip("QLineEdit - Can validate with regex or custom validators")
        form.addRow("Validated:", le5)

        layout.addLayout(form)

        # Multi-line inputs
        label_mli = QLabel("\nMulti-Line Inputs:")
        label_mli.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label_mli)

        te1 = QTextEdit()
        te1.setPlaceholderText("QTextEdit - Rich text editor\nSupports formatting, colors, fonts\nGood for: formatted text, HTML")
        te1.setMaximumHeight(80)
        te1.setToolTip("QTextEdit - Rich text with formatting support (bold, italic, colors, etc.)")
        layout.addWidget(te1)

        te2 = QPlainTextEdit()
        te2.setPlaceholderText("QPlainTextEdit - Plain text only\nNo formatting\nGood for: code, logs, plain text")
        te2.setMaximumHeight(80)
        te2.setToolTip("QPlainTextEdit - Plain text only, faster for large documents")
        layout.addWidget(te2)

        group.setLayout(layout)
        return group

    def create_number_input_section(self) -> QWidget:
        """Create number input showcase section"""
        group = QGroupBox("Number Input Widgets (QSpinBox, QDoubleSpinBox)")
        layout = QFormLayout()
        layout.setSpacing(10)

        # Integer spinner
        spin1 = QSpinBox()
        spin1.setRange(0, 100)
        spin1.setValue(50)
        spin1.setToolTip("QSpinBox - Integer input with up/down buttons\nRange: 0-100")
        layout.addRow("Integer (QSpinBox):", spin1)

        # Integer with prefix/suffix
        spin2 = QSpinBox()
        spin2.setRange(0, 1000)
        spin2.setValue(100)
        spin2.setPrefix("$")
        spin2.setSuffix(" USD")
        spin2.setToolTip("QSpinBox with prefix '$' and suffix ' USD'")
        layout.addRow("With Prefix/Suffix:", spin2)

        # Double spinner
        dspin1 = QDoubleSpinBox()
        dspin1.setRange(0.0, 10.0)
        dspin1.setValue(5.5)
        dspin1.setDecimals(2)
        dspin1.setSingleStep(0.1)
        dspin1.setToolTip("QDoubleSpinBox - Decimal/float input\nRange: 0.0-10.0, Step: 0.1")
        layout.addRow("Decimal (QDoubleSpinBox):", dspin1)

        # Double with prefix/suffix
        dspin2 = QDoubleSpinBox()
        dspin2.setRange(0.0, 100.0)
        dspin2.setValue(25.5)
        dspin2.setDecimals(1)
        dspin2.setSuffix("%")
        dspin2.setToolTip("QDoubleSpinBox with '%' suffix for percentages")
        layout.addRow("Percentage:", dspin2)

        group.setLayout(layout)
        return group

    def create_selection_section(self) -> QWidget:
        """Create selection widget showcase section"""
        group = QGroupBox("Selection Widgets (QComboBox, QFontComboBox)")
        layout = QFormLayout()
        layout.setSpacing(10)

        # Basic dropdown
        combo1 = QComboBox()
        combo1.addItems(["Option 1", "Option 2", "Option 3", "Option 4"])
        combo1.setToolTip("QComboBox - Dropdown selection list")
        layout.addRow("Dropdown (QComboBox):", combo1)

        # Editable dropdown
        combo2 = QComboBox()
        combo2.addItems(["Apple", "Banana", "Cherry"])
        combo2.setEditable(True)
        combo2.setToolTip("QComboBox with editable=True - User can type custom values")
        layout.addRow("Editable Dropdown:", combo2)

        # Font selector
        font_combo = QFontComboBox()
        font_combo.setToolTip("QFontComboBox - Special combobox for font selection")
        layout.addRow("Font Selector:", font_combo)

        group.setLayout(layout)
        return group

    def create_datetime_section(self) -> QWidget:
        """Create date/time picker showcase section"""
        group = QGroupBox("Date & Time Widgets (QDateEdit, QTimeEdit, QDateTimeEdit, QCalendarWidget)")
        layout = QVBoxLayout()

        form = QFormLayout()
        form.setSpacing(10)

        # Date picker
        date1 = QDateEdit()
        date1.setDate(QDate.currentDate())
        date1.setCalendarPopup(True)
        date1.setToolTip("QDateEdit - Date picker with calendar popup")
        form.addRow("Date (QDateEdit):", date1)

        # Time picker
        time1 = QTimeEdit()
        time1.setTime(QTime.currentTime())
        time1.setToolTip("QTimeEdit - Time picker (hours, minutes, seconds)")
        form.addRow("Time (QTimeEdit):", time1)

        # DateTime picker
        datetime1 = QDateTimeEdit()
        datetime1.setDateTime(QDateTime.currentDateTime())
        datetime1.setCalendarPopup(True)
        datetime1.setToolTip("QDateTimeEdit - Combined date and time picker")
        form.addRow("DateTime (QDateTimeEdit):", datetime1)

        layout.addLayout(form)

        # Calendar widget
        label_cal = QLabel("\nCalendar Widget (QCalendarWidget) - Full month view:")
        label_cal.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label_cal)
        cal = QCalendarWidget()
        cal.setMaximumHeight(200)
        cal.setToolTip("QCalendarWidget - Interactive calendar for date selection")
        layout.addWidget(cal)

        group.setLayout(layout)
        return group

    def create_slider_section(self) -> QWidget:
        """Create slider and dial showcase section"""
        group = QGroupBox("Sliders & Dials (QSlider, QDial)")
        layout = QVBoxLayout()

        # Horizontal slider
        label_hslide = QLabel("Horizontal Slider (QSlider):")
        label_hslide.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label_hslide)
        slider1 = QSlider(Qt.Orientation.Horizontal)
        slider1.setRange(0, 100)
        slider1.setValue(50)
        slider1.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider1.setTickInterval(10)
        slider1.setToolTip("QSlider(Qt.Horizontal) - Horizontal slider with tick marks")
        layout.addWidget(slider1)

        # Vertical slider
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Vertical Slider:"))
        slider2 = QSlider(Qt.Orientation.Vertical)
        slider2.setRange(0, 100)
        slider2.setValue(75)
        slider2.setTickPosition(QSlider.TickPosition.TicksLeft)
        slider2.setMaximumHeight(100)
        slider2.setToolTip("QSlider(Qt.Vertical) - Vertical slider")
        h_layout.addWidget(slider2)

        # Dial
        h_layout.addWidget(QLabel("Dial:"))
        dial = QDial()
        dial.setRange(0, 100)
        dial.setValue(30)
        dial.setNotchesVisible(True)
        dial.setMaximumSize(80, 80)
        dial.setToolTip("QDial - Circular dial control (less common, good for volume/rotation)")
        h_layout.addWidget(dial)

        h_layout.addStretch()
        layout.addLayout(h_layout)

        group.setLayout(layout)
        return group

    def create_display_section(self) -> QWidget:
        """Create display widget showcase section"""
        group = QGroupBox("Display Widgets (QProgressBar, QLCDNumber, QLabel)")
        layout = QVBoxLayout()

        # Progress bars
        label_prog = QLabel("Progress Bars (QProgressBar):")
        label_prog.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label_prog)
        prog1 = QProgressBar()
        prog1.setValue(45)
        prog1.setToolTip("QProgressBar - Shows progress from 0-100%")
        layout.addWidget(prog1)

        prog2 = QProgressBar()
        prog2.setRange(0, 0)  # Indeterminate
        prog2.setToolTip("QProgressBar with range(0,0) - Indeterminate/busy indicator")
        layout.addWidget(prog2)

        # LCD Number
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("LCD Number (QLCDNumber):"))
        lcd = QLCDNumber()
        lcd.display(12345)
        lcd.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        lcd.setMaximumWidth(150)
        lcd.setToolTip("QLCDNumber - Digital display (good for counters, timers)")
        h_layout.addWidget(lcd)
        h_layout.addStretch()
        layout.addLayout(h_layout)

        # Labels
        label_lbls = QLabel("\nLabels (QLabel) - Text display with formatting:")
        label_lbls.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label_lbls)
        label1 = QLabel("Plain text label")
        label1.setToolTip("QLabel - Basic text display")
        layout.addWidget(label1)

        label2 = QLabel("<b>Bold</b>, <i>Italic</i>, <u>Underline</u>, <font color='#4a9eff'>Colored</font>")
        label2.setToolTip("QLabel with HTML formatting")
        layout.addWidget(label2)

        group.setLayout(layout)
        return group

    def create_container_section(self) -> QWidget:
        """Create container and layout showcase section"""
        group = QGroupBox("Containers & Layout Widgets (QGroupBox, QFrame, QTabWidget, QSplitter)")
        layout = QVBoxLayout()

        label_gb = QLabel("Group Box (QGroupBox) - You're looking at one! Creates titled containers.")
        label_gb.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label_gb)

        # Frame examples
        label_frames = QLabel("\nFrames (QFrame) - Can be panels, separators, or borders:")
        label_frames.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label_frames)
        frame1 = QFrame()
        frame1.setFrameShape(QFrame.Shape.Box)
        frame1.setFrameShadow(QFrame.Shadow.Raised)
        frame1.setMaximumHeight(50)
        frame_layout = QVBoxLayout(frame1)
        frame_layout.addWidget(QLabel("Box frame with raised shadow"))
        layout.addWidget(frame1)

        # Tabs
        label_tabs = QLabel("\nTab Widget (QTabWidget) - Multiple pages in tabs:")
        label_tabs.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label_tabs)
        tabs = QTabWidget()
        tabs.addTab(QLabel("Content for Tab 1"), "Tab 1")
        tabs.addTab(QLabel("Content for Tab 2"), "Tab 2")
        tabs.addTab(QLabel("Content for Tab 3"), "Tab 3")
        tabs.setMaximumHeight(100)
        tabs.setToolTip("QTabWidget - Organize content in tabs")
        layout.addWidget(tabs)

        # Splitter
        label_split = QLabel("\nSplitter (QSplitter) - Resizable panels:")
        label_split.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label_split)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(QLabel("Left Panel\n(drag the divider)"))
        splitter.addWidget(QLabel("Right Panel"))
        splitter.setMaximumHeight(60)
        splitter.setToolTip("QSplitter - User can drag divider to resize panels")
        layout.addWidget(splitter)

        group.setLayout(layout)
        return group

    def create_data_section(self) -> QWidget:
        """Create data display widget showcase section"""
        group = QGroupBox("Data Display Widgets (QListWidget, QTableWidget, QTreeWidget)")
        layout = QVBoxLayout()

        # List
        label_list = QLabel("List (QListWidget) - Vertical list of items:")
        label_list.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label_list)
        list_widget = QListWidget()
        list_widget.addItems(["List Item 1", "List Item 2", "List Item 3", "List Item 4"])
        list_widget.setMaximumHeight(100)
        list_widget.setToolTip("QListWidget - Simple list, can be single or multi-select")
        layout.addWidget(list_widget)

        # Table
        label_table = QLabel("\nTable (QTableWidget) - Rows and columns:")
        label_table.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label_table)
        table = QTableWidget(3, 4)
        table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3", "Column 4"])
        for row in range(3):
            for col in range(4):
                table.setItem(row, col, QTableWidgetItem(f"Cell {row},{col}"))
        table.setMaximumHeight(150)
        table.setToolTip("QTableWidget - Spreadsheet-like grid with rows/columns")
        layout.addWidget(table)

        # Tree
        label_tree = QLabel("\nTree (QTreeWidget) - Hierarchical data:")
        label_tree.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label_tree)
        tree = QTreeWidget()
        tree.setHeaderLabels(["Name", "Value"])
        parent1 = QTreeWidgetItem(tree, ["Parent 1", "Data"])
        QTreeWidgetItem(parent1, ["Child 1.1", "100"])
        QTreeWidgetItem(parent1, ["Child 1.2", "200"])
        parent2 = QTreeWidgetItem(tree, ["Parent 2", "Data"])
        QTreeWidgetItem(parent2, ["Child 2.1", "300"])
        tree.expandAll()
        tree.setMaximumHeight(150)
        tree.setToolTip("QTreeWidget - Hierarchical tree structure (folders, categories, etc.)")
        layout.addWidget(tree)

        group.setLayout(layout)
        return group

    def create_dialog_section(self) -> QWidget:
        """Create dialog showcase section"""
        group = QGroupBox("Dialog Widgets - Click buttons to open modal dialogs")
        layout = QVBoxLayout()

        label_msgbox = QLabel("Message Boxes (QMessageBox) - Standard dialogs:")
        label_msgbox.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label_msgbox)
        btn_row1 = QHBoxLayout()

        btn_info = QPushButton("Information")
        btn_info.clicked.connect(lambda: QMessageBox.information(self, "Info", "This is an information message."))
        btn_info.setToolTip("QMessageBox.information() - Info dialog")
        btn_row1.addWidget(btn_info)

        btn_warn = QPushButton("Warning")
        btn_warn.clicked.connect(lambda: QMessageBox.warning(self, "Warning", "This is a warning message."))
        btn_warn.setToolTip("QMessageBox.warning() - Warning dialog")
        btn_row1.addWidget(btn_warn)

        btn_error = QPushButton("Error")
        btn_error.clicked.connect(lambda: QMessageBox.critical(self, "Error", "This is an error message."))
        btn_error.setToolTip("QMessageBox.critical() - Error dialog")
        btn_row1.addWidget(btn_error)

        btn_question = QPushButton("Question")
        btn_question.clicked.connect(lambda: QMessageBox.question(self, "Question", "Do you agree?"))
        btn_question.setToolTip("QMessageBox.question() - Yes/No question")
        btn_row1.addWidget(btn_question)

        btn_row1.addStretch()
        layout.addLayout(btn_row1)

        label_inputdlg = QLabel("\nInput Dialogs (QInputDialog) - Get user input:")
        label_inputdlg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label_inputdlg)
        btn_row2 = QHBoxLayout()

        btn_text = QPushButton("Text Input")
        btn_text.clicked.connect(lambda: QInputDialog.getText(self, "Input", "Enter your name:"))
        btn_text.setToolTip("QInputDialog.getText() - Single-line text input")
        btn_row2.addWidget(btn_text)

        btn_int = QPushButton("Number Input")
        btn_int.clicked.connect(lambda: QInputDialog.getInt(self, "Input", "Enter a number:", 50, 0, 100))
        btn_int.setToolTip("QInputDialog.getInt() - Integer input with range")
        btn_row2.addWidget(btn_int)

        btn_item = QPushButton("Choice Input")
        btn_item.clicked.connect(lambda: QInputDialog.getItem(self, "Select", "Choose:", ["A", "B", "C"]))
        btn_item.setToolTip("QInputDialog.getItem() - Select from dropdown list")
        btn_row2.addWidget(btn_item)

        btn_row2.addStretch()
        layout.addLayout(btn_row2)

        label_filedlg = QLabel("\nFile & Color Dialogs:")
        label_filedlg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label_filedlg)
        btn_row3 = QHBoxLayout()

        btn_file = QPushButton("Open File")
        btn_file.clicked.connect(lambda: QFileDialog.getOpenFileName(self, "Select File"))
        btn_file.setToolTip("QFileDialog.getOpenFileName() - File picker dialog")
        btn_row3.addWidget(btn_file)

        btn_color = QPushButton("Pick Color")
        btn_color.clicked.connect(lambda: QColorDialog.getColor())
        btn_color.setToolTip("QColorDialog.getColor() - Color picker dialog")
        btn_row3.addWidget(btn_color)

        btn_row3.addStretch()
        layout.addLayout(btn_row3)

        group.setLayout(layout)
        return group

    # ============= PLOT CREATION METHODS =============

    def create_plot_widget(self, plot_func, title: str, styled: bool, width=600, height=400) -> QWidget:
        """Helper to create a matplotlib plot widget"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        # Add title label
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        if styled:
            title_label.setStyleSheet(f"color: {COLORS['accent']}; padding: 3px;")
        layout.addWidget(title_label)

        # Create matplotlib figure
        fig = Figure(figsize=(width/100, height/100), dpi=100)
        canvas = FigureCanvas(fig)
        canvas.setFixedSize(width, height)

        # Apply styling if needed
        if styled:
            fig.patch.set_facecolor(COLORS['surface'])

        # Call the plot function to populate the figure
        plot_func(fig, styled)

        layout.addWidget(canvas)
        return container

    def create_line_scatter_section(self, styled: bool) -> QWidget:
        """Line plots and scatter plots"""
        group = QGroupBox("Line & Scatter Plots")
        layout = QVBoxLayout()

        # Row 1: Plot and Scatter
        row1 = QHBoxLayout()
        row1.addWidget(self.create_plot_widget(self.plot_line, "Plot", styled, 320, 240))
        row1.addWidget(self.create_plot_widget(self.plot_scatter, "Scatter", styled, 320, 240))
        row1.addStretch()
        layout.addLayout(row1)

        # Row 2: Plot with markers and Error bars
        row2 = QHBoxLayout()
        row2.addWidget(self.create_plot_widget(self.plot_with_markers, "Plot (with markers)", styled, 320, 240))
        row2.addWidget(self.create_plot_widget(self.plot_errorbar, "Errorbar", styled, 320, 240))
        row2.addStretch()
        layout.addLayout(row2)

        group.setLayout(layout)
        return group

    def create_bar_hist_section(self, styled: bool) -> QWidget:
        """Bar charts and histograms"""
        group = QGroupBox("Bar Charts & Histograms")
        layout = QVBoxLayout()

        # Row 1: Vertical and Horizontal Bar (side by side since they're rotations)
        row1 = QHBoxLayout()
        row1.addWidget(self.create_plot_widget(self.plot_bar_vertical, "Bar (vertical)", styled, 320, 240))
        row1.addWidget(self.create_plot_widget(self.plot_bar_horizontal, "Barh (horizontal)", styled, 320, 240))
        row1.addStretch()
        layout.addLayout(row1)

        # Row 2: Histogram and Grouped Bar
        row2 = QHBoxLayout()
        row2.addWidget(self.create_plot_widget(self.plot_histogram, "Hist", styled, 320, 240))
        row2.addWidget(self.create_plot_widget(self.plot_bar_grouped, "Bar (grouped)", styled, 320, 240))
        row2.addStretch()
        layout.addLayout(row2)

        # Row 3: Stacked Bar
        row3 = QHBoxLayout()
        row3.addWidget(self.create_plot_widget(self.plot_bar_stacked, "Bar (stacked)", styled, 320, 240))
        row3.addStretch()
        layout.addLayout(row3)

        group.setLayout(layout)
        return group

    def create_area_section(self, styled: bool) -> QWidget:
        """Area and fill plots"""
        group = QGroupBox("Area & Fill Plots")
        layout = QVBoxLayout()

        # Row 1: Fill and Stackplot
        row1 = QHBoxLayout()
        row1.addWidget(self.create_plot_widget(self.plot_fill_between, "Fill_between", styled, 320, 240))
        row1.addWidget(self.create_plot_widget(self.plot_stackplot, "Stackplot", styled, 320, 240))
        row1.addStretch()
        layout.addLayout(row1)

        group.setLayout(layout)
        return group

    def create_pie_section(self, styled: bool) -> QWidget:
        """Pie and donut charts"""
        group = QGroupBox("Pie & Donut Charts")
        layout = QVBoxLayout()

        # Row 1: Pie and Donut
        row1 = QHBoxLayout()
        row1.addWidget(self.create_plot_widget(self.plot_pie, "Pie", styled, 320, 240))
        row1.addWidget(self.create_plot_widget(self.plot_donut, "Pie (donut style)", styled, 320, 240))
        row1.addStretch()
        layout.addLayout(row1)

        group.setLayout(layout)
        return group

    def create_statistical_section(self, styled: bool) -> QWidget:
        """Statistical plots"""
        group = QGroupBox("Statistical Plots")
        layout = QVBoxLayout()

        # Row 1: Box and Violin
        row1 = QHBoxLayout()
        row1.addWidget(self.create_plot_widget(self.plot_boxplot, "Boxplot", styled, 320, 240))
        row1.addWidget(self.create_plot_widget(self.plot_violinplot, "Violinplot", styled, 320, 240))
        row1.addStretch()
        layout.addLayout(row1)

        group.setLayout(layout)
        return group

    def create_heatmap_section(self, styled: bool) -> QWidget:
        """Heatmaps and confusion matrices"""
        group = QGroupBox("Heatmaps & Matrices")
        layout = QVBoxLayout()

        # Row 1: Heatmap (imshow) and Confusion Matrix
        row1 = QHBoxLayout()
        row1.addWidget(self.create_plot_widget(self.plot_imshow, "Imshow (heatmap)", styled, 320, 240))
        row1.addWidget(self.create_plot_widget(self.plot_confusion_matrix, "Confusion Matrix (sklearn)", styled, 320, 240))
        row1.addStretch()
        layout.addLayout(row1)

        group.setLayout(layout)
        return group

    def create_specialty_section(self, styled: bool) -> QWidget:
        """Specialty and less common plots"""
        group = QGroupBox("Specialty Plots")
        layout = QVBoxLayout()

        # Row 1: Step and Stem
        row1 = QHBoxLayout()
        row1.addWidget(self.create_plot_widget(self.plot_step, "Step", styled, 320, 240))
        row1.addWidget(self.create_plot_widget(self.plot_stem, "Stem", styled, 320, 240))
        row1.addStretch()
        layout.addLayout(row1)

        # Row 2: Contour and Contourf
        row2 = QHBoxLayout()
        row2.addWidget(self.create_plot_widget(self.plot_contour, "Contour", styled, 320, 240))
        row2.addWidget(self.create_plot_widget(self.plot_contourf, "Contourf (filled)", styled, 320, 240))
        row2.addStretch()
        layout.addLayout(row2)

        # Row 3: Polar and Hexbin
        row3 = QHBoxLayout()
        row3.addWidget(self.create_plot_widget(self.plot_polar, "Polar", styled, 320, 240))
        row3.addWidget(self.create_plot_widget(self.plot_hexbin, "Hexbin", styled, 320, 240))
        row3.addStretch()
        layout.addLayout(row3)

        # Row 4: Quiver
        row4 = QHBoxLayout()
        row4.addWidget(self.create_plot_widget(self.plot_quiver, "Quiver (vector field)", styled, 320, 240))
        row4.addStretch()
        layout.addLayout(row4)

        group.setLayout(layout)
        return group

    def create_3d_section(self, styled: bool) -> QWidget:
        """3D plots"""
        group = QGroupBox("3D Plots")
        layout = QVBoxLayout()

        # Row 1: 3D Scatter and 3D Surface
        row1 = QHBoxLayout()
        row1.addWidget(self.create_plot_widget(self.plot_3d_scatter, "Scatter (3D)", styled, 320, 240))
        row1.addWidget(self.create_plot_widget(self.plot_3d_surface, "Surface (3D)", styled, 320, 240))
        row1.addStretch()
        layout.addLayout(row1)

        # Row 2: 3D Line and 3D Wireframe
        row2 = QHBoxLayout()
        row2.addWidget(self.create_plot_widget(self.plot_3d_line, "Plot (3D)", styled, 320, 240))
        row2.addWidget(self.create_plot_widget(self.plot_3d_wireframe, "Wireframe (3D)", styled, 320, 240))
        row2.addStretch()
        layout.addLayout(row2)

        group.setLayout(layout)
        return group

    def create_advanced_section(self, styled: bool) -> QWidget:
        """Advanced chart types"""
        group = QGroupBox("Advanced Charts")
        layout = QVBoxLayout()

        # Row 1: Bubble and Radar
        row1 = QHBoxLayout()
        row1.addWidget(self.create_plot_widget(self.plot_bubble, "Scatter (bubble)", styled, 320, 240))
        row1.addWidget(self.create_plot_widget(self.plot_radar, "Radar / Spider", styled, 320, 240))
        row1.addStretch()
        layout.addLayout(row1)

        # Row 2: Candlestick and Stream
        row2 = QHBoxLayout()
        row2.addWidget(self.create_plot_widget(self.plot_candlestick, "Candlestick (mplfinance)", styled, 320, 240))
        row2.addWidget(self.create_plot_widget(self.plot_stream, "Streamgraph", styled, 320, 240))
        row2.addStretch()
        layout.addLayout(row2)

        group.setLayout(layout)
        return group

    def create_hierarchical_section(self, styled: bool) -> QWidget:
        """Hierarchical and set visualization plots"""
        group = QGroupBox("Hierarchical & Set Plots")
        layout = QVBoxLayout()

        # Row 1: Treemap and Dendrogram
        row1 = QHBoxLayout()
        row1.addWidget(self.create_plot_widget(self.plot_treemap, "Treemap (squarify)", styled, 320, 240))
        row1.addWidget(self.create_plot_widget(self.plot_dendrogram, "Dendrogram (scipy)", styled, 320, 240))
        row1.addStretch()
        layout.addLayout(row1)

        # Row 2: Venn diagram and Sankey
        row2 = QHBoxLayout()
        row2.addWidget(self.create_plot_widget(self.plot_venn, "Venn (matplotlib_venn)", styled, 320, 240))
        row2.addWidget(self.create_plot_widget(self.plot_sankey, "Sankey", styled, 320, 240))
        row2.addStretch()
        layout.addLayout(row2)

        group.setLayout(layout)
        return group

    def create_distribution_section(self, styled: bool) -> QWidget:
        """Distribution and comparison plots"""
        group = QGroupBox("Distribution & Comparison")
        layout = QVBoxLayout()

        # Row 1: Ridgeline and Parallel Coordinates
        row1 = QHBoxLayout()
        row1.addWidget(self.create_plot_widget(self.plot_ridgeline, "Ridgeline (joypy)", styled, 320, 240))
        row1.addWidget(self.create_plot_widget(self.plot_parallel, "Parallel Coordinates (pandas)", styled, 320, 240))
        row1.addStretch()
        layout.addLayout(row1)

        # Row 2: Word Cloud
        row2 = QHBoxLayout()
        row2.addWidget(self.create_plot_widget(self.plot_wordcloud, "Word Cloud (wordcloud)", styled, 320, 240))
        row2.addStretch()
        layout.addLayout(row2)

        group.setLayout(layout)
        return group

    # ============= INDIVIDUAL PLOT FUNCTIONS =============

    def plot_line(self, fig, styled):
        """Basic line plot"""
        ax = fig.add_subplot(111)
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y, color=COLORS['primary'] if styled else None, linewidth=2)
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        ax.grid(True, alpha=0.3)
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        fig.tight_layout()

    def plot_scatter(self, fig, styled):
        """Scatter plot"""
        ax = fig.add_subplot(111)
        x = np.random.randn(50)
        y = np.random.randn(50)
        ax.scatter(x, y, c=COLORS['accent'] if styled else None, alpha=0.6, s=50)
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        ax.grid(True, alpha=0.3)
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        fig.tight_layout()

    def plot_with_markers(self, fig, styled):
        """Line plot with markers"""
        ax = fig.add_subplot(111)
        x = np.linspace(0, 10, 20)
        y = x ** 0.5
        ax.plot(x, y, marker='o', color=COLORS['secondary'] if styled else None, linewidth=2, markersize=6)
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        ax.grid(True, alpha=0.3)
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        fig.tight_layout()

    def plot_errorbar(self, fig, styled):
        """Error bar plot"""
        ax = fig.add_subplot(111)
        x = np.arange(0, 10, 1)
        y = x ** 2
        yerr = x * 2
        ax.errorbar(x, y, yerr=yerr, fmt='o-', color=COLORS['primary'] if styled else None,
                    ecolor=COLORS['error'] if styled else None, capsize=5)
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        ax.grid(True, alpha=0.3)
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        fig.tight_layout()

    def plot_bar_vertical(self, fig, styled):
        """Vertical bar chart"""
        ax = fig.add_subplot(111)
        categories = ['A', 'B', 'C', 'D', 'E']
        values = [23, 45, 56, 78, 32]
        ax.bar(categories, values, color=COLORS['primary'] if styled else None)
        ax.set_xlabel('Category', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Value', color=COLORS['text_secondary'] if styled else 'black')
        ax.grid(True, alpha=0.3, axis='y')
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        fig.tight_layout()

    def plot_bar_horizontal(self, fig, styled):
        """Horizontal bar chart"""
        ax = fig.add_subplot(111)
        categories = ['A', 'B', 'C', 'D', 'E']
        values = [23, 45, 56, 78, 32]
        ax.barh(categories, values, color=COLORS['accent'] if styled else None)
        ax.set_ylabel('Category', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_xlabel('Value', color=COLORS['text_secondary'] if styled else 'black')
        ax.grid(True, alpha=0.3, axis='x')
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        fig.tight_layout()

    def plot_histogram(self, fig, styled):
        """Histogram"""
        ax = fig.add_subplot(111)
        data = np.random.randn(1000)
        ax.hist(data, bins=30, color=COLORS['secondary'] if styled else None, alpha=0.7, edgecolor='black')
        ax.set_xlabel('Value', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Frequency', color=COLORS['text_secondary'] if styled else 'black')
        ax.grid(True, alpha=0.3, axis='y')
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        fig.tight_layout()

    def plot_bar_grouped(self, fig, styled):
        """Grouped bar chart"""
        ax = fig.add_subplot(111)
        categories = ['A', 'B', 'C', 'D']
        group1 = [20, 35, 30, 25]
        group2 = [25, 32, 34, 20]
        x = np.arange(len(categories))
        width = 0.35
        ax.bar(x - width/2, group1, width, label='Group 1', color=COLORS['primary'] if styled else None)
        ax.bar(x + width/2, group2, width, label='Group 2', color=COLORS['accent'] if styled else None)
        ax.set_xlabel('Category', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Value', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
            legend = ax.get_legend()
            legend.get_frame().set_facecolor(COLORS['surface_variant'])
            legend.get_frame().set_edgecolor(COLORS['border'])
            for text in legend.get_texts():
                text.set_color(COLORS['text_primary'])
        fig.tight_layout()

    def plot_bar_stacked(self, fig, styled):
        """Stacked bar chart"""
        ax = fig.add_subplot(111)
        categories = ['A', 'B', 'C', 'D']
        group1 = [20, 35, 30, 25]
        group2 = [25, 32, 34, 20]
        group3 = [15, 18, 22, 28]
        ax.bar(categories, group1, label='Group 1', color=COLORS['primary'] if styled else None)
        ax.bar(categories, group2, bottom=group1, label='Group 2', color=COLORS['secondary'] if styled else None)
        bottom_for_g3 = [g1 + g2 for g1, g2 in zip(group1, group2)]
        ax.bar(categories, group3, bottom=bottom_for_g3, label='Group 3', color=COLORS['accent'] if styled else None)
        ax.set_xlabel('Category', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Value', color=COLORS['text_secondary'] if styled else 'black')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
            legend = ax.get_legend()
            legend.get_frame().set_facecolor(COLORS['surface_variant'])
            legend.get_frame().set_edgecolor(COLORS['border'])
            for text in legend.get_texts():
                text.set_color(COLORS['text_primary'])
        fig.tight_layout()

    def plot_fill_between(self, fig, styled):
        """Fill between plot"""
        ax = fig.add_subplot(111)
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.sin(x) + 0.5
        ax.plot(x, y1, color=COLORS['primary'] if styled else 'blue')
        ax.plot(x, y2, color=COLORS['accent'] if styled else 'orange')
        ax.fill_between(x, y1, y2, alpha=0.3, color=COLORS['secondary'] if styled else 'green')
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        ax.grid(True, alpha=0.3)
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        fig.tight_layout()

    def plot_stackplot(self, fig, styled):
        """Stacked area plot"""
        ax = fig.add_subplot(111)
        x = np.linspace(0, 10, 50)
        y1 = np.sin(x) + 5
        y2 = np.cos(x) + 5
        y3 = np.sin(x + 1) + 5
        colors = [COLORS['primary'], COLORS['secondary'], COLORS['accent']] if styled else None
        ax.stackplot(x, y1, y2, y3, labels=['A', 'B', 'C'], colors=colors, alpha=0.7)
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
            legend = ax.get_legend()
            legend.get_frame().set_facecolor(COLORS['surface_variant'])
            legend.get_frame().set_edgecolor(COLORS['border'])
            for text in legend.get_texts():
                text.set_color(COLORS['text_primary'])
        fig.tight_layout()

    def plot_pie(self, fig, styled):
        """Pie chart"""
        ax = fig.add_subplot(111)
        sizes = [25, 30, 20, 25]
        labels = ['A', 'B', 'C', 'D']
        colors = [COLORS['primary'], COLORS['secondary'], COLORS['accent'], COLORS['error']] if styled else None
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        if styled:
            for text in ax.texts:
                text.set_color(COLORS['text_primary'])
        fig.tight_layout()

    def plot_donut(self, fig, styled):
        """Donut chart (pie with hole)"""
        ax = fig.add_subplot(111)
        sizes = [25, 30, 20, 25]
        labels = ['A', 'B', 'C', 'D']
        colors = [COLORS['primary'], COLORS['secondary'], COLORS['accent'], COLORS['error']] if styled else None
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors,
                                           startangle=90, wedgeprops=dict(width=0.5))
        if styled:
            for text in ax.texts:
                text.set_color(COLORS['text_primary'])
        fig.tight_layout()

    def plot_boxplot(self, fig, styled):
        """Box plot"""
        ax = fig.add_subplot(111)
        data = [np.random.normal(0, std, 100) for std in range(1, 5)]
        bp = ax.boxplot(data, patch_artist=True)
        if styled:
            for patch in bp['boxes']:
                patch.set_facecolor(COLORS['primary'])
            for element in ['whiskers', 'fliers', 'means', 'medians', 'caps']:
                if element in bp:
                    for item in bp[element]:
                        item.set_color(COLORS['text_secondary'])
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        ax.set_xticklabels(['A', 'B', 'C', 'D'])
        ax.set_ylabel('Value', color=COLORS['text_secondary'] if styled else 'black')
        ax.grid(True, alpha=0.3, axis='y')
        fig.tight_layout()

    def plot_violinplot(self, fig, styled):
        """Violin plot"""
        ax = fig.add_subplot(111)
        data = [np.random.normal(0, std, 100) for std in range(1, 5)]
        vp = ax.violinplot(data, showmeans=True, showmedians=True)
        if styled:
            for pc in vp['bodies']:
                pc.set_facecolor(COLORS['primary'])
                pc.set_alpha(0.7)
            for partname in ('cbars', 'cmins', 'cmaxes', 'cmedians', 'cmeans'):
                if partname in vp:
                    vp[partname].set_edgecolor(COLORS['text_secondary'])
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        ax.set_xticks([1, 2, 3, 4])
        ax.set_xticklabels(['A', 'B', 'C', 'D'])
        ax.set_ylabel('Value', color=COLORS['text_secondary'] if styled else 'black')
        ax.grid(True, alpha=0.3, axis='y')
        fig.tight_layout()

    def plot_imshow(self, fig, styled):
        """Heatmap using imshow"""
        ax = fig.add_subplot(111)
        data = np.random.rand(10, 10)
        cmap = 'viridis' if not styled else 'plasma'
        im = ax.imshow(data, cmap=cmap, aspect='auto')
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        fig.colorbar(im, ax=ax)
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        fig.tight_layout()

    def plot_confusion_matrix(self, fig, styled):
        """Confusion matrix (sklearn style)"""
        ax = fig.add_subplot(111)
        # Sample confusion matrix data
        cm = np.array([[50, 2], [5, 43]])
        cmap = 'Blues' if not styled else 'RdPu'
        im = ax.imshow(cm, cmap=cmap, aspect='auto')

        # Add text annotations
        for i in range(2):
            for j in range(2):
                text_color = COLORS['text_primary'] if styled else 'white' if cm[i, j] > cm.max() / 2 else 'black'
                ax.text(j, i, str(cm[i, j]), ha='center', va='center', color=text_color, fontsize=14, fontweight='bold')

        ax.set_xlabel('Predicted', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Actual', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['Class 0', 'Class 1'])
        ax.set_yticklabels(['Class 0', 'Class 1'])
        if styled:
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        fig.tight_layout()

    def plot_step(self, fig, styled):
        """Step plot"""
        ax = fig.add_subplot(111)
        x = np.arange(0, 10, 1)
        y = np.random.randint(0, 10, 10)
        ax.step(x, y, where='mid', color=COLORS['primary'] if styled else None, linewidth=2)
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        ax.grid(True, alpha=0.3)
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        fig.tight_layout()

    def plot_stem(self, fig, styled):
        """Stem plot"""
        ax = fig.add_subplot(111)
        x = np.linspace(0, 10, 20)
        y = np.sin(x)
        markerline, stemlines, baseline = ax.stem(x, y)
        if styled:
            markerline.set_color(COLORS['accent'])
            stemlines.set_color(COLORS['primary'])
            baseline.set_color(COLORS['border'])
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        ax.grid(True, alpha=0.3)
        fig.tight_layout()

    def plot_contour(self, fig, styled):
        """Contour plot"""
        ax = fig.add_subplot(111)
        x = np.linspace(-3, 3, 100)
        y = np.linspace(-3, 3, 100)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X) * np.cos(Y)
        cmap = 'viridis' if not styled else 'plasma'
        cs = ax.contour(X, Y, Z, cmap=cmap)
        ax.clabel(cs, inline=True, fontsize=8)
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        fig.tight_layout()

    def plot_contourf(self, fig, styled):
        """Filled contour plot"""
        ax = fig.add_subplot(111)
        x = np.linspace(-3, 3, 100)
        y = np.linspace(-3, 3, 100)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X) * np.cos(Y)
        cmap = 'viridis' if not styled else 'plasma'
        cf = ax.contourf(X, Y, Z, cmap=cmap)
        fig.colorbar(cf, ax=ax)
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        fig.tight_layout()

    def plot_polar(self, fig, styled):
        """Polar plot"""
        ax = fig.add_subplot(111, projection='polar')
        theta = np.linspace(0, 2 * np.pi, 100)
        r = np.abs(np.sin(3 * theta))
        ax.plot(theta, r, color=COLORS['primary'] if styled else None, linewidth=2)
        ax.fill(theta, r, alpha=0.3, color=COLORS['secondary'] if styled else None)
        ax.set_title('Polar Plot', pad=20, color=COLORS['text_primary'] if styled else 'black')
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            ax.spines['polar'].set_color(COLORS['border'])
        fig.tight_layout()

    def plot_hexbin(self, fig, styled):
        """Hexbin plot"""
        ax = fig.add_subplot(111)
        x = np.random.randn(1000)
        y = np.random.randn(1000)
        cmap = 'viridis' if not styled else 'plasma'
        hb = ax.hexbin(x, y, gridsize=20, cmap=cmap)
        fig.colorbar(hb, ax=ax)
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        fig.tight_layout()

    def plot_quiver(self, fig, styled):
        """Quiver plot (vector field)"""
        ax = fig.add_subplot(111)
        x = np.arange(0, 2.2, 0.2)
        y = np.arange(0, 2.2, 0.2)
        X, Y = np.meshgrid(x, y)
        U = np.cos(X) * Y
        V = np.sin(Y) * X
        color = COLORS['primary'] if styled else 'blue'
        ax.quiver(X, Y, U, V, color=color, alpha=0.8)
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        fig.tight_layout()

    # ============= 3D PLOT FUNCTIONS =============

    def plot_3d_scatter(self, fig, styled):
        """3D Scatter plot"""
        from mpl_toolkits.mplot3d import Axes3D
        ax = fig.add_subplot(111, projection='3d')
        x = np.random.randn(50)
        y = np.random.randn(50)
        z = np.random.randn(50)
        ax.scatter(x, y, z, c=COLORS['primary'] if styled else None, marker='o', s=50, alpha=0.6)
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_zlabel('Z', color=COLORS['text_secondary'] if styled else 'black')
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False
        fig.tight_layout()

    def plot_3d_surface(self, fig, styled):
        """3D Surface plot"""
        from mpl_toolkits.mplot3d import Axes3D
        ax = fig.add_subplot(111, projection='3d')
        x = np.linspace(-5, 5, 50)
        y = np.linspace(-5, 5, 50)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(np.sqrt(X**2 + Y**2))
        cmap = 'plasma' if styled else 'viridis'
        surf = ax.plot_surface(X, Y, Z, cmap=cmap, alpha=0.8)
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_zlabel('Z', color=COLORS['text_secondary'] if styled else 'black')
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
        fig.tight_layout()

    def plot_3d_line(self, fig, styled):
        """3D Line plot"""
        from mpl_toolkits.mplot3d import Axes3D
        ax = fig.add_subplot(111, projection='3d')
        t = np.linspace(0, 10, 100)
        x = np.sin(t)
        y = np.cos(t)
        z = t
        ax.plot(x, y, z, color=COLORS['primary'] if styled else None, linewidth=2)
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_zlabel('Z', color=COLORS['text_secondary'] if styled else 'black')
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
        fig.tight_layout()

    def plot_3d_wireframe(self, fig, styled):
        """3D Wireframe plot"""
        from mpl_toolkits.mplot3d import Axes3D
        ax = fig.add_subplot(111, projection='3d')
        x = np.linspace(-5, 5, 30)
        y = np.linspace(-5, 5, 30)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(np.sqrt(X**2 + Y**2))
        ax.plot_wireframe(X, Y, Z, color=COLORS['primary'] if styled else None, alpha=0.7)
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_zlabel('Z', color=COLORS['text_secondary'] if styled else 'black')
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
        fig.tight_layout()

    # ============= ADVANCED PLOT FUNCTIONS =============

    def plot_bubble(self, fig, styled):
        """Bubble plot (scatter with size variation)"""
        ax = fig.add_subplot(111)
        x = np.random.randn(30)
        y = np.random.randn(30)
        sizes = np.random.randint(50, 500, 30)  # Varying bubble sizes
        ax.scatter(x, y, s=sizes, c=COLORS['accent'] if styled else None, alpha=0.5, edgecolors='black', linewidth=1)
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        ax.grid(True, alpha=0.3)
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        fig.tight_layout()

    def plot_radar(self, fig, styled):
        """Radar/Spider chart"""
        categories = ['A', 'B', 'C', 'D', 'E']
        values = [4, 3, 5, 4, 4]

        # Number of variables
        N = len(categories)
        # Compute angle for each axis
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        # Complete the loop
        values += values[:1]
        angles += angles[:1]

        ax = fig.add_subplot(111, projection='polar')
        ax.plot(angles, values, color=COLORS['primary'] if styled else 'blue', linewidth=2)
        ax.fill(angles, values, color=COLORS['primary'] if styled else 'blue', alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 6)
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            ax.spines['polar'].set_color(COLORS['border'])
        fig.tight_layout()

    def plot_candlestick(self, fig, styled):
        """Candlestick chart (finance)"""
        try:
            import pandas as pd
            import mplfinance as mpf

            # Create sample data
            dates = pd.date_range('2024-01-01', periods=20, freq='D')
            data = pd.DataFrame({
                'Open': np.random.uniform(90, 110, 20),
                'High': np.random.uniform(110, 120, 20),
                'Low': np.random.uniform(80, 90, 20),
                'Close': np.random.uniform(90, 110, 20)
            }, index=dates)

            # Use matplotlib directly for compatibility
            ax = fig.add_subplot(111)
            for i in range(len(data)):
                color = COLORS['success'] if data['Close'].iloc[i] > data['Open'].iloc[i] else COLORS['error'] if styled else ('green' if data['Close'].iloc[i] > data['Open'].iloc[i] else 'red')
                ax.plot([i, i], [data['Low'].iloc[i], data['High'].iloc[i]], color=color, linewidth=1)
                ax.plot([i, i], [data['Open'].iloc[i], data['Close'].iloc[i]], color=color, linewidth=4)

            ax.set_xlabel('Days', color=COLORS['text_secondary'] if styled else 'black')
            ax.set_ylabel('Price', color=COLORS['text_secondary'] if styled else 'black')
            ax.grid(True, alpha=0.3)
            if styled:
                ax.set_facecolor(COLORS['background'])
                ax.tick_params(colors=COLORS['text_secondary'])
                for spine in ax.spines.values():
                    spine.set_color(COLORS['border'])
        except ImportError:
            # Fallback if mplfinance not available
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'mplfinance not installed\npip install mplfinance',
                   ha='center', va='center', fontsize=12,
                   color=COLORS['text_secondary'] if styled else 'black')
            if styled:
                ax.set_facecolor(COLORS['background'])
        fig.tight_layout()

    def plot_stream(self, fig, styled):
        """Streamgraph (stacked area with baseline offset)"""
        ax = fig.add_subplot(111)
        x = np.linspace(0, 10, 50)
        y1 = np.sin(x) + 2
        y2 = np.cos(x) + 2
        y3 = np.sin(x + 1) + 2
        colors = [COLORS['primary'], COLORS['secondary'], COLORS['accent']] if styled else None
        ax.stackplot(x, y1, y2, y3, labels=['A', 'B', 'C'], colors=colors, alpha=0.7, baseline='wiggle')
        ax.set_xlabel('X', color=COLORS['text_secondary'] if styled else 'black')
        ax.set_ylabel('Y', color=COLORS['text_secondary'] if styled else 'black')
        ax.legend(loc='upper left')
        if styled:
            ax.set_facecolor(COLORS['background'])
            ax.tick_params(colors=COLORS['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
            legend = ax.get_legend()
            legend.get_frame().set_facecolor(COLORS['surface_variant'])
            legend.get_frame().set_edgecolor(COLORS['border'])
            for text in legend.get_texts():
                text.set_color(COLORS['text_primary'])
        fig.tight_layout()

    # ============= HIERARCHICAL PLOT FUNCTIONS =============

    def plot_treemap(self, fig, styled):
        """Treemap"""
        try:
            import squarify
            ax = fig.add_subplot(111)
            sizes = [40, 30, 20, 10]
            labels = ['A\n40', 'B\n30', 'C\n20', 'D\n10']
            colors_list = [COLORS['primary'], COLORS['secondary'], COLORS['accent'], COLORS['error']] if styled else None
            squarify.plot(sizes=sizes, label=labels, color=colors_list, alpha=0.7, ax=ax, text_kwargs={'fontsize':10, 'color': COLORS['text_primary'] if styled else 'black'})
            ax.axis('off')
            if styled:
                ax.set_facecolor(COLORS['background'])
        except ImportError:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'squarify not installed\npip install squarify',
                   ha='center', va='center', fontsize=12,
                   color=COLORS['text_secondary'] if styled else 'black')
            if styled:
                ax.set_facecolor(COLORS['background'])
        fig.tight_layout()

    def plot_dendrogram(self, fig, styled):
        """Dendrogram (hierarchical clustering)"""
        try:
            from scipy.cluster.hierarchy import dendrogram, linkage
            ax = fig.add_subplot(111)
            # Generate sample data
            X = np.random.randn(10, 2)
            Z = linkage(X, 'ward')
            if styled:
                dendrogram(Z, ax=ax, color_threshold=0, above_threshold_color=COLORS['primary'])
            else:
                dendrogram(Z, ax=ax)
            ax.set_xlabel('Sample', color=COLORS['text_secondary'] if styled else 'black')
            ax.set_ylabel('Distance', color=COLORS['text_secondary'] if styled else 'black')
            if styled:
                ax.set_facecolor(COLORS['background'])
                ax.tick_params(colors=COLORS['text_secondary'])
                for spine in ax.spines.values():
                    spine.set_color(COLORS['border'])
        except ImportError:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'scipy not installed\npip install scipy',
                   ha='center', va='center', fontsize=12,
                   color=COLORS['text_secondary'] if styled else 'black')
            if styled:
                ax.set_facecolor(COLORS['background'])
        fig.tight_layout()

    def plot_venn(self, fig, styled):
        """Venn diagram"""
        try:
            from matplotlib_venn import venn2
            ax = fig.add_subplot(111)
            v = venn2(subsets=(30, 20, 10), set_labels=('A', 'B'), ax=ax)
            if styled:
                if v.get_patch_by_id('10'):
                    v.get_patch_by_id('10').set_color(COLORS['primary'])
                    v.get_patch_by_id('10').set_alpha(0.7)
                if v.get_patch_by_id('01'):
                    v.get_patch_by_id('01').set_color(COLORS['secondary'])
                    v.get_patch_by_id('01').set_alpha(0.7)
                if v.get_patch_by_id('11'):
                    v.get_patch_by_id('11').set_color(COLORS['accent'])
                    v.get_patch_by_id('11').set_alpha(0.7)
                for text in v.set_labels:
                    if text:
                        text.set_color(COLORS['text_primary'])
                for text in v.subset_labels:
                    if text:
                        text.set_color(COLORS['text_primary'])
                ax.set_facecolor(COLORS['background'])
        except ImportError:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'matplotlib-venn not installed\npip install matplotlib-venn',
                   ha='center', va='center', fontsize=10,
                   color=COLORS['text_secondary'] if styled else 'black')
            if styled:
                ax.set_facecolor(COLORS['background'])
        fig.tight_layout()

    def plot_sankey(self, fig, styled):
        """Sankey diagram"""
        from matplotlib.sankey import Sankey
        ax = fig.add_subplot(111)
        sankey = Sankey(ax=ax, scale=0.01, offset=0.2)
        sankey.add(flows=[0.25, 0.15, 0.60, -0.20, -0.15, -0.05, -0.50, -0.10],
                  labels=['', '', '', 'First', 'Second', 'Third', 'Fourth', 'Fifth'],
                  orientations=[-1, 1, 0, 1, 1, 1, 0, -1],
                  facecolor=COLORS['primary'] if styled else 'lightskyblue')
        diagrams = sankey.finish()
        if styled:
            ax.set_facecolor(COLORS['background'])
        fig.tight_layout()

    # ============= DISTRIBUTION PLOT FUNCTIONS =============

    def plot_ridgeline(self, fig, styled):
        """Ridgeline plot (joyplot)"""
        try:
            import joypy
            import pandas as pd
            # Create sample data
            data = pd.DataFrame({
                'Category': np.repeat(['A', 'B', 'C', 'D'], 100),
                'Value': np.concatenate([
                    np.random.normal(0, 1, 100),
                    np.random.normal(2, 1, 100),
                    np.random.normal(4, 1, 100),
                    np.random.normal(6, 1, 100)
                ])
            })
            fig.clf()  # Clear figure for joypy
            joypy.joyplot(data, by='Category', column='Value', figsize=(3.2, 2.4),
                         color=COLORS['primary'] if styled else None, alpha=0.7, legend=False, fig=fig)
            if styled:
                for ax in fig.get_axes():
                    ax.set_facecolor(COLORS['background'])
                    ax.tick_params(colors=COLORS['text_secondary'])
                    for spine in ax.spines.values():
                        spine.set_color(COLORS['border'])
        except ImportError:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'joypy not installed\npip install joypy',
                   ha='center', va='center', fontsize=12,
                   color=COLORS['text_secondary'] if styled else 'black')
            if styled:
                ax.set_facecolor(COLORS['background'])
        fig.tight_layout()

    def plot_parallel(self, fig, styled):
        """Parallel coordinates plot"""
        try:
            import pandas as pd
            from pandas.plotting import parallel_coordinates
            # Create sample data
            data = pd.DataFrame({
                'A': np.random.randn(20),
                'B': np.random.randn(20),
                'C': np.random.randn(20),
                'D': np.random.randn(20),
                'Category': np.random.choice(['X', 'Y', 'Z'], 20)
            })
            ax = fig.add_subplot(111)
            parallel_coordinates(data, 'Category', ax=ax,
                               color=[COLORS['primary'], COLORS['secondary'], COLORS['accent']] if styled else None)
            ax.set_xlabel('Variables', color=COLORS['text_secondary'] if styled else 'black')
            ax.set_ylabel('Value', color=COLORS['text_secondary'] if styled else 'black')
            ax.grid(True, alpha=0.3)
            if styled:
                ax.set_facecolor(COLORS['background'])
                ax.tick_params(colors=COLORS['text_secondary'])
                for spine in ax.spines.values():
                    spine.set_color(COLORS['border'])
                legend = ax.get_legend()
                if legend:
                    legend.get_frame().set_facecolor(COLORS['surface_variant'])
                    legend.get_frame().set_edgecolor(COLORS['border'])
                    for text in legend.get_texts():
                        text.set_color(COLORS['text_primary'])
        except ImportError:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'pandas not installed\npip install pandas',
                   ha='center', va='center', fontsize=12,
                   color=COLORS['text_secondary'] if styled else 'black')
            if styled:
                ax.set_facecolor(COLORS['background'])
        fig.tight_layout()

    def plot_wordcloud(self, fig, styled):
        """Word cloud"""
        try:
            from wordcloud import WordCloud
            ax = fig.add_subplot(111)
            # Sample text
            text = "Python data visualization matplotlib plot chart graph scatter bar line pie histogram"
            text = text * 10  # Repeat to make it more interesting

            wordcloud = WordCloud(width=400, height=300, background_color=COLORS['background'] if styled else 'white',
                                 colormap='plasma' if styled else 'viridis').generate(text)
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            if styled:
                ax.set_facecolor(COLORS['background'])
        except ImportError:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'wordcloud not installed\npip install wordcloud',
                   ha='center', va='center', fontsize=12,
                   color=COLORS['text_secondary'] if styled else 'black')
            if styled:
                ax.set_facecolor(COLORS['background'])
        fig.tight_layout()


def check_optional_packages():
    """Check for optional packages and print installation instructions"""
    optional_packages = {
        'squarify': 'Treemap plots',
        'scipy': 'Dendrogram plots',
        'matplotlib_venn': 'Venn diagrams',
        'joypy': 'Ridgeline plots',
        'wordcloud': 'Word cloud plots',
        'mplfinance': 'Candlestick charts',
        'pandas': 'Parallel coordinates plots'
    }

    missing = []
    for package, description in optional_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing.append((package, description))

    if missing:
        print("\n" + "="*60)
        print("OPTIONAL PACKAGES NOT INSTALLED")
        print("="*60)
        print("\nThe following packages are not installed.")
        print("Some plot types will show a 'not installed' message:\n")
        for package, description in missing:
            print(f"  • {package:20} - {description}")

        print("\nTo install all missing packages, run:")
        packages_str = ' '.join([pkg for pkg, _ in missing])
        print(f"\n  pip install {packages_str}")
        print("\n" + "="*60 + "\n")
    else:
        print("\n✓ All optional packages are installed!\n")


def main():
    """Run the widget showcase application"""
    # Check for optional packages and print installation instructions
    check_optional_packages()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for consistent look across platforms

    window = WidgetShowcase()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
