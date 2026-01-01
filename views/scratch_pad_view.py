"""
Scratch Pad View - Excel-like workspace for user calculations

Features:
- 26x50 grid (A-Z columns, 1-50 rows)
- Formula support: =A1+B2, =SUM(A1:A10), =AVERAGE(B1:B10)
- External variables: =GET(emergency fund balance)
- Date arithmetic: =11/25/2025 - CURRENT_DATE
- Auto-save to JSON
- Cell highlighting when dependencies are selected
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QToolButton, QLabel,
                             QLineEdit, QPushButton, QCompleter, QComboBox)
from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QColor, QFont
from themes import theme_manager
from services.workspace_calculator import WorkspaceCalculator, CircularReferenceError
from datetime import date
import json
from pathlib import Path


class ScratchPadView(QWidget):
    """Scratch Pad tab for user calculations and planning"""

    def __init__(self, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager
        self.calculator = WorkspaceCalculator(transaction_manager)
        self.current_cell = None  # Track selected cell for highlighting
        self.updating_formula_bar = False  # Flag to prevent infinite loops
        self.inserting_cell_ref = False  # Flag for cell reference insertion mode

        # Grid dimensions
        self.num_rows = 50
        self.num_cols = 26  # A-Z

        self.init_ui()
        self.setup_completer()
        self.load_workspace()
        self.apply_theme()

        # Connect to theme changes
        theme_manager.theme_changed.connect(self.apply_theme)

    def init_ui(self):
        """Initialize the UI layout"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Top bar with title and buttons
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        # Title
        title = QLabel("🧮 Scratch Pad")
        title.setFont(theme_manager.get_font("title"))
        top_bar.addWidget(title)

        top_bar.addStretch()

        # Format dropdown
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Text", "Header 1", "Header 2", "Notes"])
        self.format_combo.setToolTip("Format selected cell(s)")
        self.format_combo.setFixedWidth(100)
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        top_bar.addWidget(self.format_combo)

        # Refresh button
        self.refresh_button = QToolButton()
        self.refresh_button.setText("🔄")
        self.refresh_button.setToolTip("Refresh all cells (updates external variables)")
        self.refresh_button.setFixedSize(40, 30)
        self.refresh_button.clicked.connect(self.refresh_all)
        top_bar.addWidget(self.refresh_button)

        # Clear All button
        self.clear_button = QToolButton()
        self.clear_button.setText("🗑️")
        self.clear_button.setToolTip("Clear all cells")
        self.clear_button.setFixedSize(40, 30)
        self.clear_button.clicked.connect(self.clear_all)
        top_bar.addWidget(self.clear_button)

        # Load Test Data button
        self.test_data_button = QToolButton()
        self.test_data_button.setText("📋")
        self.test_data_button.setToolTip("Load test data (demonstrates all features)")
        self.test_data_button.setFixedSize(40, 30)
        self.test_data_button.clicked.connect(self.load_test_data)
        top_bar.addWidget(self.test_data_button)

        main_layout.addLayout(top_bar)

        # Formula bar (like Excel)
        formula_bar_layout = QHBoxLayout()
        formula_bar_layout.setSpacing(10)

        # Cell reference label
        self.cell_ref_label = QLabel("A1")
        self.cell_ref_label.setFixedWidth(50)
        self.cell_ref_label.setFont(theme_manager.get_font("main"))
        formula_bar_layout.addWidget(self.cell_ref_label)

        # Formula editor
        self.formula_edit = QLineEdit()
        self.formula_edit.setPlaceholderText("Enter value or formula (start with = for formulas)")
        self.formula_edit.setFont(theme_manager.get_font("main"))
        self.formula_edit.returnPressed.connect(self.on_formula_entered)
        self.formula_edit.setFocusPolicy(Qt.FocusPolicy.ClickFocus)  # Allow clicking
        formula_bar_layout.addWidget(self.formula_edit)

        main_layout.addLayout(formula_bar_layout)

        # Error message label (shown when cell has error)
        self.error_label = QLabel("")
        self.error_label.setFont(theme_manager.get_font("small"))
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)  # Hidden by default
        main_layout.addWidget(self.error_label)

        # Grid table
        self.table = QTableWidget()
        self.table.setRowCount(self.num_rows)
        self.table.setColumnCount(self.num_cols)

        # Set column headers (A-Z)
        headers = [chr(ord('A') + i) for i in range(self.num_cols)]
        self.table.setHorizontalHeaderLabels(headers)

        # Set row headers (1-50)
        self.table.setVerticalHeaderLabels([str(i + 1) for i in range(self.num_rows)])

        # Configure table
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # CHANGED: Allow multiple cell selection (was SingleSelection)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ContiguousSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Keep selection visible

        # Disable in-cell editing - all editing happens in formula bar
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Set default column width
        for col in range(self.num_cols):
            self.table.setColumnWidth(col, 100)

        # Connect signals
        self.table.currentCellChanged.connect(self.on_cell_selected)

        # Install event filter to capture keystrokes in table and redirect to formula bar
        self.table.installEventFilter(self)

        main_layout.addWidget(self.table)

        # Help text
        help_text = QLabel(
            "💡 Quick Guide: Numbers, text, dates (MM/DD/YYYY) | Formulas start with = | "
            "Functions: SUM(A1:A10), AVERAGE(B1:B5), GET(account_name balance) | "
            "Cell refs: A1, B2 | Date math: =12/25/2025 - CURRENT_DATE"
        )
        help_text.setWordWrap(True)
        help_text.setFont(theme_manager.get_font("small"))
        main_layout.addWidget(help_text)

        self.setLayout(main_layout)

    def setup_completer(self):
        """Setup autocomplete for formula bar"""
        # Create completer
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setWidget(self.formula_edit)

        # Create model for dynamic suggestions
        self.completer_model = QStringListModel()
        self.completer.setModel(self.completer_model)

        # DO NOT attach completer to QLineEdit - we'll handle completion manually
        # This prevents the default behavior of replacing all text

        # Connect to text changes to update suggestions dynamically
        self.formula_edit.textChanged.connect(self.update_completer_suggestions)

        # Connect to completion activation to handle cursor positioning
        self.completer.activated.connect(self.on_completion_activated)

    def get_account_names(self):
        """Get list of account and bill names from database"""
        try:
            from models import get_db, Account, Bill
            db = get_db()

            accounts = db.query(Account).all()
            bills = db.query(Bill).all()

            account_names = [a.name for a in accounts]
            bill_names = [b.name for b in bills]

            db.close()
            return account_names + bill_names
        except Exception as e:
            print(f"Error getting account names: {e}")
            return []

    def get_account_type(self, account_name):
        """Determine if account is a Bill or Savings account"""
        try:
            from models import get_db, Account, Bill
            db = get_db()

            # Check if it's a savings account
            account = db.query(Account).filter(Account.name.ilike(account_name)).first()
            if account:
                db.close()
                return "savings"

            # Check if it's a bill
            bill = db.query(Bill).filter(Bill.name.ilike(account_name)).first()
            if bill:
                db.close()
                return "bill"

            db.close()
            return None
        except Exception as e:
            print(f"Error determining account type: {e}")
            return None

    def update_completer_suggestions(self):
        """Update completer suggestions based on current context"""
        # Skip if we're programmatically updating the formula bar
        if self.updating_formula_bar:
            return

        text = self.formula_edit.text()
        cursor_pos = self.formula_edit.cursorPosition()

        # Don't show suggestions if formula bar is empty or has no =
        if not text or '=' not in text:
            self.completer_model.setStringList([])
            return

        # Get text up to cursor position for context
        text_before_cursor = text[:cursor_pos]

        suggestions = []

        # Only suggest if we have a formula (starts with =) or we're inside one
        if '=' in text_before_cursor:
            # Get the part after the last =
            formula_part = text_before_cursor.split('=')[-1]

            # Check if we're inside a GET function
            if 'GET(' in formula_part.upper():
                # Extract what's inside GET()
                get_start = formula_part.upper().rfind('GET(')
                inside_get = formula_part[get_start + 4:]

                # Check if we have a comma (suggesting properties)
                if ',' in inside_get:
                    # Suggest properties
                    account_part = inside_get.split(',')[0].strip()
                    account_type = self.get_account_type(account_part)

                    if account_type == "bill":
                        suggestions = ["balance", "goal", "auto_save", "typical"]
                    elif account_type == "savings":
                        suggestions = ["balance", "goal", "auto_save"]
                    else:
                        # Unknown account, suggest all
                        suggestions = ["balance", "goal", "auto_save", "typical"]
                else:
                    # Suggest account names
                    suggestions = self.get_account_names()

            # Check if we're inside SUM or AVERAGE function
            elif 'SUM(' in formula_part.upper() or 'AVERAGE(' in formula_part.upper():
                # Don't suggest anything inside SUM/AVERAGE (user types cell ranges)
                suggestions = []

            # Check if we're starting to type a function (no open parens yet, or just typed one)
            else:
                # Suggest functions when user is typing at formula level
                functions = ["SUM()", "AVERAGE()", "GET()", "CURRENT_DATE"]
                suggestions = functions

            # If we typed something, filter suggestions
            if formula_part:
                # Get the last word being typed
                last_word = formula_part.split()[-1] if formula_part.split() else formula_part
                # Remove special characters from last word
                for char in ['(', ')', ',', '+', '-', '*', '/']:
                    last_word = last_word.replace(char, '')

                if last_word:
                    # Filter suggestions that start with the last word (case insensitive)
                    filtered = [s for s in suggestions if s.lower().startswith(last_word.lower())]
                    suggestions = filtered if filtered else suggestions

        # Update the model
        self.completer_model.setStringList(suggestions)

        # Show completer if we have suggestions
        if suggestions:
            # Force the completer popup to appear
            self.completer.complete()

    def on_completion_activated(self, completion):
        """Handle when a completion is selected"""
        # Block the completer update while we're modifying text
        self.updating_formula_bar = True

        # Get current text and cursor position
        text = self.formula_edit.text()
        cursor_pos = self.formula_edit.cursorPosition()

        # Find what we're replacing
        text_before_cursor = text[:cursor_pos]
        text_after_cursor = text[cursor_pos:]

        # Get the partial word being typed
        # Look backwards from cursor to find the start of the current word
        # DON'T stop at '=' - we want to keep it
        start_pos = cursor_pos
        for i in range(cursor_pos - 1, -1, -1):
            char = text[i]
            # Stop at these delimiters but NOT at '='
            if char in [' ', '(', ',', '+', '-', '*', '/']:
                start_pos = i + 1
                break
            # If we hit '=', that's the beginning - keep the = and replace after it
            if char == '=':
                start_pos = i + 1
                break
            if i == 0:
                start_pos = 0

        # Build new text
        new_text = text[:start_pos] + completion + text_after_cursor

        # Set new text
        self.formula_edit.setText(new_text)

        # Position cursor
        if completion.endswith('()'):
            # For functions, position cursor inside parentheses
            new_cursor_pos = start_pos + len(completion) - 1
        else:
            # For accounts/properties, position cursor after the completion
            new_cursor_pos = start_pos + len(completion)

        self.formula_edit.setCursorPosition(new_cursor_pos)

        self.updating_formula_bar = False

    def get_cell_ref(self, row: int, col: int) -> str:
        """Convert row/col to cell reference (e.g., A1)"""
        return self.calculator.cell_ref_to_str(row, col)

    def on_cell_selected(self, row: int, col: int, prev_row: int, prev_col: int):
        """Handle cell selection - update formula bar and highlight dependencies"""
        # Clear previous highlighting
        self.clear_highlights()

        if row < 0 or col < 0:
            return

        cell_ref = self.get_cell_ref(row, col)

        # If we're inserting a cell reference (editing a formula), don't update current_cell or formula bar
        if self.inserting_cell_ref:
            return

        self.current_cell = cell_ref

        # Update cell reference label
        self.cell_ref_label.setText(cell_ref)

        # Update formula bar (block signals to prevent triggering completer updates)
        self.updating_formula_bar = True
        if cell_ref in self.calculator.cells:
            cell_data = self.calculator.cells[cell_ref]

            # Show the formula in the formula bar
            formula = cell_data["formula"]
            self.formula_edit.setText(formula)

            # If error, show error message in the error label
            if cell_data.get("type") == "error" and "error_message" in cell_data:
                error_msg = cell_data["error_message"]
                # Show error message in disabled color
                self.error_label.setText(f"Error: {error_msg}")
                self.error_label.setVisible(True)
            else:
                # Hide error label for non-error cells
                self.error_label.setVisible(False)
        else:
            self.formula_edit.setText("")
            self.error_label.setVisible(False)

        self.updating_formula_bar = False

        # Update format dropdown to show current cell's format
        self.update_format_dropdown()

        # Highlight cells this cell depends on
        if cell_ref in self.calculator.dependencies:
            for dep_ref in self.calculator.dependencies[cell_ref]:
                self.highlight_cell(dep_ref, QColor(173, 216, 230, 100))  # Light blue

    def clear_highlights(self):
        """Clear all cell highlighting"""
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                item = self.table.item(row, col)
                if item:
                    item.setBackground(QColor(255, 255, 255, 0))  # Transparent

    def highlight_cell(self, cell_ref: str, color: QColor):
        """Highlight a specific cell"""
        pos = self.calculator.parse_cell_reference(cell_ref)
        if not pos:
            return

        row, col = pos
        item = self.table.item(row, col)
        if not item:
            item = QTableWidgetItem()
            self.table.setItem(row, col, item)

        item.setBackground(color)

    def on_formula_entered(self):
        """Handle Enter key in formula bar"""
        if self.current_cell:
            formula = self.formula_edit.text().strip()
            # Preserve existing format if cell already exists
            existing_format = "P"
            if self.current_cell in self.calculator.cells:
                existing_format = self.calculator.cells[self.current_cell].get("format", "P")
            self.set_cell_formula(self.current_cell, formula, format_type=existing_format)

    def on_cell_edited(self, row: int, col: int):
        """Handle direct cell editing"""
        cell_ref = self.get_cell_ref(row, col)
        item = self.table.item(row, col)

        if item:
            text = item.text().strip()

            # Check if we already have a formula for this cell
            # If we do, and the text matches the displayed value, ignore this edit
            # (it's just from programmatic display update)
            if cell_ref in self.calculator.cells:
                stored_value = self.calculator.cells[cell_ref]["value"]

                # Format the stored value the same way we display it
                # Check for error tuple
                is_error = isinstance(stored_value, tuple) and len(stored_value) == 2 and stored_value[0] == "ERROR"

                if is_error:
                    display_text = "ERROR"
                elif isinstance(stored_value, date):
                    display_text = stored_value.strftime("%m/%d/%Y")
                elif isinstance(stored_value, float):
                    if stored_value == int(stored_value):
                        display_text = str(int(stored_value))
                    else:
                        display_text = f"{stored_value:.2f}"
                else:
                    display_text = str(stored_value)

                # If the text matches what we would display, it's not a real edit
                if text == display_text:
                    return

            # This is a real user edit
            if text:
                # Preserve existing format if cell already exists
                existing_format = "P"
                if cell_ref in self.calculator.cells:
                    existing_format = self.calculator.cells[cell_ref].get("format", "P")
                self.set_cell_formula(cell_ref, text, update_display=True, format_type=existing_format)

    def set_cell_formula(self, cell_ref: str, formula: str, update_display: bool = True, format_type: str = "P"):
        """Set a cell's formula and recalculate"""
        if not formula:
            # Clear cell
            if cell_ref in self.calculator.cells:
                del self.calculator.cells[cell_ref]
            if cell_ref in self.calculator.dependencies:
                del self.calculator.dependencies[cell_ref]

            pos = self.calculator.parse_cell_reference(cell_ref)
            if pos:
                row, col = pos
                item = self.table.item(row, col)
                if item:
                    item.setText("")

            # Save the workspace to persist the deletion
            self.save_workspace()
            return

        # Set formula and evaluate
        try:
            value = self.calculator.set_cell_formula(cell_ref, formula, format_type)

            # Update display
            if update_display:
                self.display_cell_value(cell_ref, value)

            # Recalculate dependent cells
            for dependent in self.calculator.get_dependent_cells(cell_ref):
                self.calculator.recalculate_cell(dependent)
                dep_value = self.calculator.cells[dependent]["value"]
                self.display_cell_value(dependent, dep_value)

            # Auto-save
            self.save_workspace()

        except Exception as e:
            print(f"Error setting cell formula: {e}")

    def display_cell_value(self, cell_ref: str, value):
        """Display value in the table"""
        pos = self.calculator.parse_cell_reference(cell_ref)
        if not pos:
            return

        row, col = pos

        # Block signals to prevent triggering on_cell_edited
        self.table.blockSignals(True)

        # Get or create item
        item = self.table.item(row, col)
        if not item:
            item = QTableWidgetItem()
            self.table.setItem(row, col, item)

        # Check for error tuple
        is_error = isinstance(value, tuple) and len(value) == 2 and value[0] == "ERROR"

        # Format value for display
        if is_error:
            # Display just "ERROR" in the cell
            display_text = "ERROR"

            # Use theme's error color directly
            colors = theme_manager.get_colors()
            item.setForeground(QColor(colors['error']))

        elif isinstance(value, date):
            display_text = value.strftime("%m/%d/%Y")
            item.setForeground(QColor(theme_manager.get_colors()['text_primary']))
        elif isinstance(value, float):
            # Format numbers nicely
            if value == int(value):
                display_text = str(int(value))
            else:
                display_text = f"{value:.2f}"
            item.setForeground(QColor(theme_manager.get_colors()['text_primary']))
        else:
            display_text = str(value)
            item.setForeground(QColor(theme_manager.get_colors()['text_primary']))

        item.setText(display_text)

        # Apply formatting based on format type
        format_type = self.calculator.cells.get(cell_ref, {}).get("format", "P")
        self.apply_cell_format(item, format_type, is_error)

        # Right-align numbers and dates
        if isinstance(value, (int, float, date)):
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        else:
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.table.blockSignals(False)

    def apply_cell_format(self, item, format_type, is_error=False):
        """Apply formatting to a table cell based on format type

        Format types:
        - H1: Primary color, bold, +10px font size
        - H2: Secondary color, bold, +2px font size
        - P: Normal (text_primary, regular)
        - n: Note (text_secondary, italic)
        """
        colors = theme_manager.get_colors()
        font = theme_manager.get_font("main")

        # Don't override error color
        if not is_error:
            if format_type == "H1":
                item.setForeground(QColor(colors['primary']))
                font.setBold(True)
                font.setPointSize(font.pointSize() + 4)  # SETTING: H1 size increase
            elif format_type == "H2":
                item.setForeground(QColor(colors['secondary']))
                font.setBold(True)
                font.setPointSize(font.pointSize() + 1)  # SETTING: H2 size increase
            elif format_type == "n":
                item.setForeground(QColor(colors['text_secondary']))
                font.setItalic(True)
            else:  # "P" or default
                item.setForeground(QColor(colors['text_primary']))

        item.setFont(font)

    def update_format_dropdown(self):
        """Update format dropdown to show current cell's format"""
        # Get the current/last selected cell
        selected_ranges = self.table.selectedRanges()
        if selected_ranges:
            sel_range = selected_ranges[0]
            # Get bottom-right cell (last selected)
            last_row = sel_range.bottomRow()
            last_col = sel_range.rightColumn()
            cell_ref = self.get_cell_ref(last_row, last_col)
        elif self.current_cell:
            cell_ref = self.current_cell
        else:
            return

        # Get format from cell data
        format_code = "P"  # Default
        if cell_ref in self.calculator.cells:
            format_code = self.calculator.cells[cell_ref].get("format", "P")

        # Map format code to display text
        format_map = {
            "P": "Text",
            "H1": "Header 1",
            "H2": "Header 2",
            "n": "Notes"
        }

        display_text = format_map.get(format_code, "Text")

        # Block signals to prevent triggering on_format_changed
        self.format_combo.blockSignals(True)
        self.format_combo.setCurrentText(display_text)
        self.format_combo.blockSignals(False)

    def on_format_changed(self, format_text):
        """Handle format dropdown change"""
        # Map display text to format code
        format_map = {
            "Text": "P",
            "Header 1": "H1",
            "Header 2": "H2",
            "Notes": "n"
        }

        format_code = format_map.get(format_text, "P")

        # Get selected cells
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return

        # Apply format to all selected cells
        for sel_range in selected_ranges:
            for row in range(sel_range.topRow(), sel_range.bottomRow() + 1):
                for col in range(sel_range.leftColumn(), sel_range.rightColumn() + 1):
                    cell_ref = self.get_cell_ref(row, col)

                    # Only update if cell exists
                    if cell_ref in self.calculator.cells:
                        # Update format in calculator
                        self.calculator.cells[cell_ref]["format"] = format_code

                        # Refresh display
                        value = self.calculator.cells[cell_ref]["value"]
                        self.display_cell_value(cell_ref, value)

        # Save changes
        self.save_workspace()

    def refresh_all(self):
        """Refresh all cells (recalculate with updated external variables)"""
        self.calculator.recalculate_all()

        # Update display for all cells
        for cell_ref in self.calculator.cells:
            value = self.calculator.cells[cell_ref]["value"]
            self.display_cell_value(cell_ref, value)

        self.save_workspace()

    def clear_all(self):
        """Clear all cells"""
        from PyQt6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Clear All Cells",
            "Are you sure you want to clear all cells? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.calculator.cells = {}
            self.calculator.dependencies = {}

            # Clear table
            self.table.blockSignals(True)
            for row in range(self.num_rows):
                for col in range(self.num_cols):
                    item = self.table.item(row, col)
                    if item:
                        item.setText("")
            self.table.blockSignals(False)

            self.save_workspace()

    def load_test_data(self):
        """Load test data from template file"""
        from PyQt6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Load Test Data",
            "This will replace all current data with test/demo data. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Clear current data (both calculator and visual table)
            self.calculator.cells = {}
            self.calculator.dependencies = {}

            # Clear the visual table
            self.table.blockSignals(True)
            for row in range(self.num_rows):
                for col in range(self.num_cols):
                    item = self.table.item(row, col)
                    if item:
                        item.setText("")
            self.table.blockSignals(False)

            # Load from test data file
            test_data_path = Path("scratch_pad_test_data.json")
            if not test_data_path.exists():
                QMessageBox.warning(
                    self,
                    "File Not Found",
                    "Test data file 'scratch_pad_test_data.json' not found."
                )
                return

            try:
                with open(test_data_path, 'r') as f:
                    test_data = json.load(f)

                # Load cells from test data
                for cell_ref, cell_data in test_data.get("cells", {}).items():
                    formula = cell_data["formula"]
                    format_type = cell_data.get("format", "P")
                    self.set_cell_formula(cell_ref, formula, format_type=format_type)

                # Save the loaded test data as current workspace
                self.save_workspace()

                QMessageBox.information(
                    self,
                    "Test Data Loaded",
                    "Test data loaded successfully!"
                )

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error Loading Test Data",
                    f"Failed to load test data: {str(e)}"
                )

    def save_workspace(self):
        """Save workspace to JSON file"""
        try:
            save_data = {
                "cells": {
                    ref: {
                        "formula": data["formula"],
                        "type": data["type"],
                        "format": data.get("format", "P")  # Default to P if not set
                    }
                    for ref, data in self.calculator.cells.items()
                }
            }

            save_path = Path("scratch_pad_workspace.json")
            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=2)

        except Exception as e:
            print(f"Error saving workspace: {e}")

    def load_workspace(self):
        """Load workspace from JSON file"""
        try:
            save_path = Path("scratch_pad_workspace.json")
            if not save_path.exists():
                return

            with open(save_path, 'r') as f:
                save_data = json.load(f)

            # Load cells
            for cell_ref, cell_data in save_data.get("cells", {}).items():
                formula = cell_data["formula"]
                format_type = cell_data.get("format", "P")  # Default to P if not in JSON
                self.set_cell_formula(cell_ref, formula, format_type=format_type)

        except Exception as e:
            print(f"Error loading workspace: {e}")

    def eventFilter(self, source, event):
        """Event filter to handle keyboard input in table and redirect to formula bar"""
        from PyQt6.QtCore import QEvent
        from PyQt6.QtGui import QKeyEvent

        # Handle mouse clicks on table cells when editing a formula
        # Use MouseButtonPress to intercept BEFORE the selection changes
        if source == self.table and event.type() == QEvent.Type.MouseButtonPress:
            # If formula bar has text starting with '=', we'll insert cell reference
            current_text = self.formula_edit.text()
            if current_text.startswith('='):
                # Store that we're in formula mode - we'll handle this on mouse release
                self.inserting_cell_ref = True
                return False  # Let the selection happen so we can read it

        # On mouse release, insert the cell reference if we're in formula mode
        if source == self.table and event.type() == QEvent.Type.MouseButtonRelease:
            current_text = self.formula_edit.text()
            if current_text.startswith('=') and hasattr(self, 'inserting_cell_ref') and self.inserting_cell_ref:
                self.inserting_cell_ref = False

                # Get the selected range (now it's been selected by the mouse press)
                selected_ranges = self.table.selectedRanges()
                if selected_ranges:
                    sel_range = selected_ranges[0]

                    # Build cell reference or range
                    if sel_range.rowCount() == 1 and sel_range.columnCount() == 1:
                        # Single cell - insert like "A1"
                        cell_ref = self.get_cell_ref(sel_range.topRow(), sel_range.leftColumn())
                    else:
                        # Range - insert like "A1:B5"
                        top_left = self.get_cell_ref(sel_range.topRow(), sel_range.leftColumn())
                        bottom_right = self.get_cell_ref(sel_range.bottomRow(), sel_range.rightColumn())
                        cell_ref = f"{top_left}:{bottom_right}"

                    # Insert at cursor position in formula bar
                    cursor_pos = self.formula_edit.cursorPosition()
                    new_text = current_text[:cursor_pos] + cell_ref + current_text[cursor_pos:]

                    self.updating_formula_bar = True
                    self.formula_edit.setText(new_text)
                    self.formula_edit.setCursorPosition(cursor_pos + len(cell_ref))
                    self.updating_formula_bar = False

                    # Keep focus on formula bar
                    self.formula_edit.setFocus()
                    return True

        # Handle keyboard input in the table - redirect to formula bar
        if source == self.table and event.type() == QEvent.Type.KeyPress:
            key_event = event
            key = key_event.key()
            text = key_event.text()

            # Ignore navigation keys (arrows, tab, etc.)
            from PyQt6.QtCore import Qt as QtCore
            navigation_keys = [
                QtCore.Key.Key_Up, QtCore.Key.Key_Down, QtCore.Key.Key_Left, QtCore.Key.Key_Right,
                QtCore.Key.Key_Tab, QtCore.Key.Key_Backtab, QtCore.Key.Key_Escape
            ]

            if key in navigation_keys:
                return False  # Let table handle navigation

            # Handle Copy (Ctrl+C) - copies formulas to clipboard, stores values for Ctrl+Shift+V
            if key == QtCore.Key.Key_C and key_event.modifiers() == QtCore.KeyboardModifier.ControlModifier:
                self.copy_selection()
                return True

            # Handle Paste Values (Ctrl+Shift+V) - paste as plain values, not formulas
            # Note: This must come BEFORE regular Ctrl+V check
            if key == QtCore.Key.Key_V and key_event.modifiers() == (QtCore.KeyboardModifier.ControlModifier | QtCore.KeyboardModifier.ShiftModifier):
                self.paste_selection_values()
                return True

            # Handle Paste (Ctrl+V)
            if key == QtCore.Key.Key_V and key_event.modifiers() == QtCore.KeyboardModifier.ControlModifier:
                self.paste_selection()
                return True

            # Handle Enter/Return - apply formula
            if key in [QtCore.Key.Key_Return, QtCore.Key.Key_Enter]:
                self.on_formula_entered()
                return True  # Consume event

            # Handle Delete - clear all selected cells
            if key == QtCore.Key.Key_Delete:
                self.delete_selection()
                return True

            if key == QtCore.Key.Key_Backspace:
                # Start editing in formula bar (clear and focus)
                self.formula_edit.clear()
                self.formula_edit.setFocus()
                return True

            # For printable characters, focus formula bar and start typing
            if text and text.isprintable():
                # If user starts typing, clear formula bar and start fresh
                # (unless they're continuing to type)
                if not self.formula_edit.hasFocus():
                    # If multiple cells are selected, focus on the last selected cell (bottom-right)
                    selected_ranges = self.table.selectedRanges()
                    if selected_ranges:
                        sel_range = selected_ranges[0]
                        # Set current cell to bottom-right of selection
                        last_row = sel_range.bottomRow()
                        last_col = sel_range.rightColumn()
                        self.current_cell = self.get_cell_ref(last_row, last_col)

                        # Update cell reference label
                        self.cell_ref_label.setText(self.current_cell)

                        # Clear selection and select only the last cell
                        self.table.setCurrentCell(last_row, last_col)

                    self.formula_edit.clear()
                    self.formula_edit.setFocus()
                    # Let the character be typed in the formula bar
                    self.formula_edit.setText(text)
                    self.formula_edit.setCursorPosition(len(text))
                    return True

        return super().eventFilter(source, event)

    def copy_selection(self):
        """Copy selected cells to clipboard (formulas with format).

        Also stores the displayed values internally for Ctrl+Shift+V paste.
        Format is stored as: formula|format (e.g., "=A1+B2|H1" or "Hello|P")
        """
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return

        sel_range = selected_ranges[0]

        # Build clipboard data as tab-separated formulas with format
        # Format: formula|format_code (e.g., "=A1+B2|H1")
        # Also build values data for paste-as-values (Ctrl+Shift+V)
        clipboard_data = []
        values_data = []
        for row in range(sel_range.topRow(), sel_range.bottomRow() + 1):
            row_formulas = []
            row_values = []
            for col in range(sel_range.leftColumn(), sel_range.rightColumn() + 1):
                cell_ref = self.get_cell_ref(row, col)
                if cell_ref in self.calculator.cells:
                    cell_data = self.calculator.cells[cell_ref]
                    # Copy the formula with format
                    formula = cell_data.get("formula", "")
                    format_type = cell_data.get("format", "P")
                    # Store as formula|format (use | as separator since it's unlikely in formulas)
                    row_formulas.append(f"{formula}|{format_type}")

                    # Also capture the displayed value for paste-as-values
                    value = cell_data.get("value", "")
                    if value is None or value == "":
                        row_values.append("")
                    elif isinstance(value, (int, float)):
                        if format_type == "$":
                            row_values.append(f"${value:,.2f}")
                        elif format_type == "%":
                            row_values.append(f"{value * 100:.1f}%")
                        else:
                            # Plain number - keep reasonable precision
                            if isinstance(value, float) and value != int(value):
                                row_values.append(f"{value:.4f}".rstrip('0').rstrip('.'))
                            else:
                                row_values.append(str(int(value) if isinstance(value, float) and value == int(value) else value))
                    else:
                        row_values.append(str(value))
                else:
                    row_formulas.append("|P")  # Empty cell with default format
                    row_values.append("")
            clipboard_data.append("\t".join(row_formulas))
            values_data.append("\t".join(row_values))

        # Store formulas+format to clipboard (for Ctrl+V)
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(clipboard_data))

        # Store values internally for paste-as-values (Ctrl+Shift+V)
        self._copied_values = "\n".join(values_data)

    def paste_selection(self):
        """Paste clipboard data to selected cells (with format if available).

        Clipboard data format: formula|format_code (e.g., "=A1+B2|H1")
        If no | separator found, assumes plain text with default format.
        """
        from PyQt6.QtWidgets import QApplication

        clipboard = QApplication.clipboard()
        text = clipboard.text()

        if not text:
            return

        # Get starting cell (top-left of selection or current cell)
        selected_ranges = self.table.selectedRanges()
        if selected_ranges:
            start_row = selected_ranges[0].topRow()
            start_col = selected_ranges[0].leftColumn()
        elif self.current_cell:
            pos = self.calculator.parse_cell_reference(self.current_cell)
            if not pos:
                return
            start_row, start_col = pos
        else:
            return

        # Parse clipboard data (tab-separated, newline-separated)
        rows = text.split("\n")
        for row_offset, row_text in enumerate(rows):
            if not row_text:
                continue
            cells = row_text.split("\t")
            for col_offset, cell_text in enumerate(cells):
                target_row = start_row + row_offset
                target_col = start_col + col_offset

                # Check bounds
                if target_row >= self.num_rows or target_col >= self.num_cols:
                    continue

                target_ref = self.get_cell_ref(target_row, target_col)

                # Parse formula and format (format: "formula|format_code")
                if "|" in cell_text:
                    # Split from the RIGHT to handle formulas that might contain |
                    parts = cell_text.rsplit("|", 1)
                    formula = parts[0]
                    format_code = parts[1] if len(parts) > 1 and parts[1] in ("P", "H1", "H2", "n", "$", "%") else "P"
                else:
                    # Plain text without format (e.g., pasted from external source)
                    formula = cell_text
                    format_code = "P"

                self.set_cell_formula(target_ref, formula, format_type=format_code)

    def paste_selection_values(self):
        """Paste the displayed values (not formulas) from the last copy operation.

        When you copy cells with Ctrl+C, both formulas and displayed values are captured.
        - Ctrl+V pastes the formulas (e.g., =A1+B2)
        - Ctrl+Shift+V pastes the displayed values (e.g., 24)

        This is useful when you want to "freeze" calculated results without
        maintaining the formula dependencies.
        """
        # Use the stored values from the last copy operation
        if not hasattr(self, '_copied_values') or not self._copied_values:
            return

        text = self._copied_values

        # Get starting cell (top-left of selection or current cell)
        selected_ranges = self.table.selectedRanges()
        if selected_ranges:
            start_row = selected_ranges[0].topRow()
            start_col = selected_ranges[0].leftColumn()
        elif self.current_cell:
            pos = self.calculator.parse_cell_reference(self.current_cell)
            if not pos:
                return
            start_row, start_col = pos
        else:
            return

        # Parse values data (tab-separated, newline-separated)
        rows = text.split("\n")
        for row_offset, row_text in enumerate(rows):
            if not row_text:
                continue
            cells = row_text.split("\t")
            for col_offset, cell_text in enumerate(cells):
                target_row = start_row + row_offset
                target_col = start_col + col_offset

                # Check bounds
                if target_row >= self.num_rows or target_col >= self.num_cols:
                    continue

                target_ref = self.get_cell_ref(target_row, target_col)
                self.set_cell_formula(target_ref, cell_text)

    def delete_selection(self):
        """Delete/clear all selected cells"""
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            # No selection, clear current cell if any
            if self.current_cell:
                self.set_cell_formula(self.current_cell, "")
                self.formula_edit.clear()
            return

        # Clear all cells in selection
        for sel_range in selected_ranges:
            for row in range(sel_range.topRow(), sel_range.bottomRow() + 1):
                for col in range(sel_range.leftColumn(), sel_range.rightColumn() + 1):
                    cell_ref = self.get_cell_ref(row, col)
                    self.set_cell_formula(cell_ref, "")

        # Clear formula bar
        self.formula_edit.clear()

        # Save changes
        self.save_workspace()

    def apply_theme(self):
        """Apply current theme to the view"""
        try:
            colors = theme_manager.get_colors()

            # Update main background
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {colors['background']};
                    color: {colors['text_primary']};
                }}
            """)

            # Update table styling
            self.table.setStyleSheet(f"""
                QTableWidget {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    gridline-color: {colors['border']};
                }}
                QTableWidget::item {{
                    padding: 5px;
                }}
                QTableWidget::item:selected {{
                    background-color: {colors['primary']};
                    color: {colors['background']};
                }}
                QTableWidget::item:selected:!active {{
                    background-color: {colors['primary']};
                    color: {colors['background']};
                }}
                QHeaderView::section {{
                    background-color: {colors['surface_variant']};
                    color: {colors['text_primary']};
                    padding: 5px;
                    border: 1px solid {colors['border']};
                    font-weight: bold;
                }}
            """)

            # Update title and error label
            for child in self.findChildren(QLabel):
                if "Scratch Pad" in child.text():
                    child.setStyleSheet(f"color: {colors['text_primary']};")
                elif child == self.error_label:
                    # Style error label with disabled color
                    child.setStyleSheet(f"color: {colors['text_disabled']};")
                else:
                    child.setStyleSheet(f"color: {colors['text_secondary']};")

            # Update formula bar
            if hasattr(self, 'formula_edit'):
                self.formula_edit.setStyleSheet(f"""
                    QLineEdit {{
                        background-color: {colors['surface']};
                        color: {colors['text_primary']};
                        border: 1px solid {colors['border']};
                        border-radius: 4px;
                        padding: 5px;
                    }}
                """)

            if hasattr(self, 'cell_ref_label'):
                self.cell_ref_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {colors['surface_variant']};
                        color: {colors['text_primary']};
                        border: 1px solid {colors['border']};
                        border-radius: 4px;
                        padding: 5px;
                        font-weight: bold;
                    }}
                """)

            # Update format dropdown
            if hasattr(self, 'format_combo'):
                self.format_combo.setStyleSheet(f"""
                    QComboBox {{
                        background-color: {colors['surface']};
                        color: {colors['text_primary']};
                        border: 1px solid {colors['border']};
                        border-radius: 4px;
                        padding: 5px;
                    }}
                    QComboBox::drop-down {{
                        border: none;
                    }}
                    QComboBox::down-arrow {{
                        image: none;
                        border-left: 4px solid transparent;
                        border-right: 4px solid transparent;
                        border-top: 6px solid {colors['text_primary']};
                        width: 0;
                        height: 0;
                        margin-right: 5px;
                    }}
                    QComboBox QAbstractItemView {{
                        background-color: {colors['surface']};
                        color: {colors['text_primary']};
                        selection-background-color: {colors['primary']};
                        border: 1px solid {colors['border']};
                    }}
                """)

            # Update buttons
            button_style = f"""
                QToolButton {{
                    background-color: {colors['primary']};
                    color: {colors['background']};
                    border: none;
                    border-radius: 4px;
                }}
                QToolButton:hover {{
                    background-color: {colors['accent']};
                }}
            """
            if hasattr(self, 'refresh_button'):
                self.refresh_button.setStyleSheet(button_style)
            if hasattr(self, 'clear_button'):
                self.clear_button.setStyleSheet(button_style)
            if hasattr(self, 'test_data_button'):
                self.test_data_button.setStyleSheet(button_style)

        except Exception as e:
            print(f"Error applying theme to scratch pad: {e}")
