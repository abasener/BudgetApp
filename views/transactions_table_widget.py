"""
Transaction Table Widget - Reusable table component for transaction viewing/editing
"""

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QCheckBox, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from themes import theme_manager


class TransactionTableWidget(QTableWidget):
    """
    Reusable table widget for displaying and editing transactions

    Features:
    - Sortable columns (click headers)
    - Search filtering
    - Row selection (single + multi)
    - Delete marking (red text)
    - Locked row styling (grayed + lock icon)
    """

    # Signal emitted when a row is edited
    row_edited = pyqtSignal(int)  # row index

    def __init__(self, parent=None):
        super().__init__(parent)

        # Track state
        self.all_rows_data = []  # Store all data (before filtering)
        self.filtered_rows = []  # Currently visible rows after filtering
        self.deleted_rows = set()  # Set of row indices marked for deletion
        self.locked_rows = set()  # Set of row indices that are locked
        self.edited_rows = set()  # Set of row indices that have been edited
        self.transaction_ids = {}  # Map row index -> transaction ID
        self.current_sort_column = 0  # Column currently sorted by
        self.current_sort_order = Qt.SortOrder.AscendingOrder  # Current sort direction

        # Track special columns
        self.lock_column_index = -1  # Index of lock/editable column
        self.abnormal_column_index = -1  # Index of abnormal checkbox column

        self.init_table()

    def init_table(self):
        """Initialize table settings"""
        # Enable sorting
        self.setSortingEnabled(False)  # We'll handle sorting manually for more control

        # Selection behavior
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)  # Multi-select with Ctrl

        # Editing
        self.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)

        # Alternating row colors
        self.setAlternatingRowColors(True)

        # Stretch last column
        self.horizontalHeader().setStretchLastSection(True)

        # Click header to sort
        self.horizontalHeader().sectionClicked.connect(self.on_header_clicked)

        # Track edits
        self.itemChanged.connect(self.on_item_changed)

    def set_columns(self, column_headers):
        """
        Set table columns

        Args:
            column_headers: List of column header names
        """
        self.setColumnCount(len(column_headers))

        # Replace 🔒 with "Editable" in headers
        display_headers = []
        for i, header in enumerate(column_headers):
            if header == "🔒":
                display_headers.append("Editable")
                self.lock_column_index = i
            elif header == "Abnormal":
                display_headers.append("Abnormal")
                self.abnormal_column_index = i
            else:
                display_headers.append(header)

        self.setHorizontalHeaderLabels(display_headers)

        # Configure column resize modes
        # - Editable column: fixed tight width
        # - Last 1-2 columns (Notes): stretch to fill available space
        # - Other columns: resize to content
        for i in range(len(column_headers)):
            if i == self.lock_column_index:
                # Lock column: fixed width (tight)
                self.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                self.setColumnWidth(i, 70)  # Fixed width for "Editable" column
            elif i >= len(column_headers) - 2:
                # Last 2 columns (typically Manual Notes and Auto Notes): stretch
                self.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            else:
                # All other columns: resize to content
                self.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

    def load_data(self, rows_data, locked_row_indices=None, transaction_ids=None):
        """
        Load data into table

        Args:
            rows_data: List of dicts, each dict represents a row
                      Each dict should have keys matching column headers
            locked_row_indices: Set of row indices that should be locked (non-editable)
            transaction_ids: Dict mapping row index -> transaction ID for saving changes
        """
        self.all_rows_data = rows_data
        self.filtered_rows = list(range(len(rows_data)))  # Initially show all rows
        self.deleted_rows = set()
        self.edited_rows = set()
        self.locked_rows = locked_row_indices if locked_row_indices else set()
        self.transaction_ids = transaction_ids if transaction_ids else {}

        self.refresh_display()

    def refresh_display(self):
        """Refresh table display based on current filtered rows"""
        # Block signals while populating to avoid triggering itemChanged
        self.blockSignals(True)

        # Get theme colors for styling
        colors = theme_manager.get_colors()

        # Clear table
        self.setRowCount(0)

        # Populate with filtered rows
        for display_row_idx, data_row_idx in enumerate(self.filtered_rows):
            self.insertRow(display_row_idx)
            row_data = self.all_rows_data[data_row_idx]

            # Populate cells
            for col_idx, (key, value) in enumerate(row_data.items()):
                # Apply styling based on state
                is_locked = data_row_idx in self.locked_rows
                is_deleted = data_row_idx in self.deleted_rows

                # Handle special columns
                if col_idx == self.lock_column_index:
                    # Lock/Editable column - always non-editable, show icon
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Always non-editable
                    item.setData(Qt.ItemDataRole.UserRole, data_row_idx)
                    # Don't make it italic even if row is locked
                    if is_deleted:
                        item.setForeground(QColor(colors['error']))  # Use theme error color
                        font = item.font()
                        font.setStrikeOut(True)
                        item.setFont(font)
                    elif is_locked:
                        # Still gray but not italic - use theme text_secondary color
                        item.setForeground(QColor(colors['text_secondary']))
                    self.setItem(display_row_idx, col_idx, item)

                elif col_idx == self.abnormal_column_index:
                    # Abnormal column - use checkbox widget
                    checkbox_widget = QWidget()
                    checkbox_layout = QHBoxLayout(checkbox_widget)
                    checkbox_layout.setContentsMargins(0, 0, 0, 0)
                    checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

                    checkbox = QCheckBox()
                    checkbox.setChecked(str(value) == "☑")
                    checkbox.setEnabled(not is_locked and not is_deleted)  # Disable if locked/deleted

                    checkbox_layout.addWidget(checkbox)
                    self.setCellWidget(display_row_idx, col_idx, checkbox_widget)

                else:
                    # Regular column
                    item = QTableWidgetItem(str(value))
                    item.setData(Qt.ItemDataRole.UserRole, data_row_idx)

                    if is_locked:
                        # Locked rows: grayed out and non-editable
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        item.setForeground(QColor(colors['text_secondary']))  # Use theme secondary text
                        font = item.font()
                        font.setItalic(True)
                        item.setFont(font)

                    if is_deleted:
                        # Deleted rows: red text
                        item.setForeground(QColor(colors['error']))  # Use theme error color
                        font = item.font()
                        font.setStrikeOut(True)
                        item.setFont(font)

                    self.setItem(display_row_idx, col_idx, item)

        # Restore signals
        self.blockSignals(False)

        # Apply theme
        self.apply_theme()

    def on_header_clicked(self, logical_index):
        """Handle column header click for sorting"""
        # Toggle sort order if clicking same column
        if logical_index == self.current_sort_column:
            if self.current_sort_order == Qt.SortOrder.AscendingOrder:
                self.current_sort_order = Qt.SortOrder.DescendingOrder
            else:
                self.current_sort_order = Qt.SortOrder.AscendingOrder
        else:
            # New column, default to ascending
            self.current_sort_column = logical_index
            self.current_sort_order = Qt.SortOrder.AscendingOrder

        # Update header to show sort indicator
        self.horizontalHeader().setSortIndicator(logical_index, self.current_sort_order)

        # Perform sort
        self.sort_data(logical_index, self.current_sort_order)

    def sort_data(self, column_index, sort_order):
        """
        Sort table data by column

        Args:
            column_index: Column to sort by
            sort_order: Qt.SortOrder.AscendingOrder or DescendingOrder
        """
        # Get column header name
        column_name = self.horizontalHeaderItem(column_index).text()
        # Remove sort indicator (▲/▼) if present
        column_name = column_name.replace(" ▲", "").replace(" ▼", "")

        # Sort filtered rows based on data
        reverse = (sort_order == Qt.SortOrder.DescendingOrder)

        def get_sort_key(row_idx):
            row_data = self.all_rows_data[row_idx]
            value = row_data.get(column_name, "")
            # Try to convert to number for numeric sorting
            try:
                # Remove $ and , for dollar amounts
                if isinstance(value, str) and value.startswith("$"):
                    return float(value.replace("$", "").replace(",", ""))
                return float(value)
            except (ValueError, AttributeError):
                return str(value).lower()

        self.filtered_rows.sort(key=get_sort_key, reverse=reverse)

        # Update header to show sort indicator
        for i in range(self.columnCount()):
            header_item = self.horizontalHeaderItem(i)
            if header_item:
                text = header_item.text().replace(" ▲", "").replace(" ▼", "")
                if i == column_index:
                    text += " ▲" if sort_order == Qt.SortOrder.AscendingOrder else " ▼"
                header_item.setText(text)

        # Refresh display
        self.refresh_display()

    def filter_by_search(self, search_text):
        """
        Filter table rows by search text

        Args:
            search_text: Text to search for (case-insensitive, searches all fields)
        """
        if not search_text:
            # Show all rows if search is empty
            self.filtered_rows = list(range(len(self.all_rows_data)))
        else:
            search_lower = search_text.lower()
            self.filtered_rows = []

            for row_idx, row_data in enumerate(self.all_rows_data):
                # Check if search text appears in any field
                for value in row_data.values():
                    if search_lower in str(value).lower():
                        self.filtered_rows.append(row_idx)
                        break  # Found match, move to next row

        # Refresh display
        self.refresh_display()

    def mark_selected_for_deletion(self):
        """Mark currently selected rows for deletion (turn red)"""
        selected_items = self.selectedItems()

        if not selected_items:
            return

        # Get unique row indices from selected items
        selected_rows = set()
        for item in selected_items:
            data_row_idx = item.data(Qt.ItemDataRole.UserRole)

            # Don't allow deleting locked rows
            if data_row_idx not in self.locked_rows:
                selected_rows.add(data_row_idx)

        # Add to deleted set
        self.deleted_rows.update(selected_rows)

        # Refresh display to show red text
        self.refresh_display()

        return len(selected_rows)  # Return count of rows marked

    def get_deleted_rows(self):
        """Get list of data row indices marked for deletion"""
        return list(self.deleted_rows)

    def get_edited_rows(self):
        """Get list of row indices that have been edited"""
        return list(self.edited_rows)

    def clear_change_tracking(self):
        """Clear all change tracking (called when switching tabs)"""
        self.edited_rows = set()
        self.deleted_rows = set()

    def get_row_data(self, row_index):
        """
        Get current data for a row from the table

        Args:
            row_index: The data row index (not display row index)

        Returns:
            Dict with column names as keys and current cell values
        """
        # Find this data row in the displayed rows
        try:
            display_row = self.filtered_rows.index(row_index)
        except ValueError:
            # Row not currently visible (filtered out)
            return None

        row_data = {}
        for col_idx in range(self.columnCount()):
            header = self.horizontalHeaderItem(col_idx).text()
            # Remove sort indicators from header
            header = header.replace(" ▲", "").replace(" ▼", "")

            # Get cell value
            if col_idx == self.abnormal_column_index:
                # Get checkbox state
                widget = self.cellWidget(display_row, col_idx)
                if widget:
                    checkbox = widget.findChild(QCheckBox)
                    row_data[header] = checkbox.isChecked() if checkbox else False
            else:
                item = self.item(display_row, col_idx)
                row_data[header] = item.text() if item else ""

        return row_data

    def on_item_changed(self, item):
        """Handle when an item is edited"""
        # Get original data row index
        data_row_idx = item.data(Qt.ItemDataRole.UserRole)

        # Don't allow editing locked or deleted rows
        if data_row_idx in self.locked_rows or data_row_idx in self.deleted_rows:
            return

        # Mark row as edited
        self.edited_rows.add(data_row_idx)

        # Emit signal
        self.row_edited.emit(data_row_idx)

    def apply_theme(self):
        """Apply current theme colors to table"""
        colors = theme_manager.get_colors()

        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {colors['surface']};
                color: {colors['text_primary']};
                border: 1px solid {colors['border']};
                gridline-color: {colors['border']};
                selection-background-color: {colors['primary']};
            }}
            QTableWidget::item {{
                padding: 4px;
                background-color: {colors['surface']};
            }}
            QTableWidget::item:selected {{
                background-color: {colors['primary']};
                color: {colors['background']};
            }}
            QHeaderView::section {{
                background-color: {colors['surface_variant']};
                color: {colors['text_primary']};
                padding: 6px;
                border: 1px solid {colors['border']};
                font-weight: bold;
            }}
            QHeaderView::section:hover {{
                background-color: {colors['hover']};
            }}
        """)
