"""
PyQt6 Widget Showcase - A comprehensive demonstration of all available UI elements

This is a standalone testing tool to explore PyQt6 widgets and their variants.
Shows inputs, buttons, layouts, and styling options with dark theme colors.

Dependencies: PyQt6 only (pip install PyQt6)
"""

import sys
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

        # DON'T apply theme to main window - we'll apply it only to left side
        # self.apply_dark_theme()

        # Create main splitter for side-by-side comparison
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
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

        self.setCentralWidget(main_splitter)

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


def main():
    """Run the widget showcase application"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for consistent look across platforms

    window = WidgetShowcase()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
