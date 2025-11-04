"""
Bill Transaction History Dialog - Simple transaction editing like Weekly tab
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime
from themes import theme_manager
from utils.error_handler import is_testing_mode


class BillTransactionHistoryDialog(QDialog):
    """Dialog for editing bill transactions - simplified approach"""

    bill_updated = pyqtSignal(object)  # Signal when bill is modified

    def __init__(self, bill, transaction_manager, parent=None):
        super().__init__(parent)
        self.bill = bill
        self.transaction_manager = transaction_manager

        self.setWindowTitle(f"Transaction History: {bill.name}")
        self.setModal(True)
        self.resize(1000, 600)

        try:
            self.init_ui()
            self.load_transactions()
            self.apply_theme()

        except Exception as e:
            print(f"Error in BillTransactionHistoryDialog init: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Initialization Error", f"Error loading transaction history:\n{str(e)}")

    def init_ui(self):
        """Initialize the UI - Simple transaction table like Weekly tab"""
        layout = QVBoxLayout()

        # Header
        header = QLabel(f"Transaction History: {self.bill.name}")
        header.setFont(theme_manager.get_font("title"))
        layout.addWidget(header)

        # Info label
        info = QLabel("Edit cells to modify transactions, select rows to mark for deletion, then click 'Save Changes' to apply all modifications.")
        layout.addWidget(info)

        # Transaction table - simplified columns like Weekly tab
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # Simplified columns
        self.table.setHorizontalHeaderLabels([
            "Date", "Amount", "Description", "Type", "Running Total"
        ])

        # Basic table config
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(False)  # Keep chronological order

        # Auto-resize columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Amount
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)          # Description
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Total

        # Track changes but don't save immediately
        self.pending_changes = {}  # {row: {column: new_value}}
        self.rows_to_delete = set()
        self.original_values = {}  # Store original values {row: {column: value}}
        self.loading_data = False  # Flag to prevent cellChanged during load

        # Connect cell edit signal to track changes (not save immediately)
        self.table.cellChanged.connect(self.on_cell_changed)

        # Connect selection changed signal for cell highlighting
        self.table.itemSelectionChanged.connect(self.on_selection_changed)

        layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()

        delete_btn = QPushButton("Delete Entry")
        delete_btn.clicked.connect(self.mark_for_deletion)
        button_layout.addWidget(delete_btn)

        button_layout.addStretch()

        # Save/Close buttons
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_all_changes)
        save_btn.setStyleSheet("font-weight: bold; background-color: #28a745; color: white; padding: 5px 15px;")
        button_layout.addWidget(save_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_transactions(self):
        """Load all transactions for this bill - store transaction IDs for editing"""
        try:
            # Set loading flag to block cellChanged signal
            self.loading_data = True

            # Clear pending changes
            self.pending_changes = {}
            self.rows_to_delete = set()
            self.original_values = {}

            # Get AccountHistory entries directly for this bill
            from models.account_history import AccountHistoryManager

            history_manager = AccountHistoryManager(self.transaction_manager.db)
            account_history = history_manager.get_account_history(self.bill.id, "bill")

            # Sort by date (oldest first, newest last)
            account_history.sort(key=lambda h: h.transaction_date, reverse=False)

            # Populate table with simplified data
            self.table.setRowCount(len(account_history))
            self.transaction_ids = {}  # Store {row: transaction_id} mapping

            for row, history_entry in enumerate(account_history):
                # Store the transaction ID for this row
                self.transaction_ids[row] = history_entry.transaction_id

                # Store original values for this row
                if row not in self.original_values:
                    self.original_values[row] = {}

                # Date (editable for transactions)
                date_str = str(history_entry.transaction_date)
                date_item = QTableWidgetItem(date_str)
                self.original_values[row][0] = date_str
                if history_entry.transaction_id is None:
                    date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 0, date_item)

                # Amount (editable for transactions)
                amount_str = f"{history_entry.change_amount:.2f}"
                amount_item = QTableWidgetItem(amount_str)
                self.original_values[row][1] = amount_str
                if history_entry.transaction_id is None:
                    amount_item.setFlags(amount_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 1, amount_item)

                # Description (editable for transactions)
                description = ""
                if history_entry.transaction_id is None:
                    description = "Starting Balance"
                else:
                    # Get description from transaction
                    try:
                        from models.transactions import Transaction
                        transaction = self.transaction_manager.db.query(Transaction).filter_by(id=history_entry.transaction_id).first()
                        if transaction:
                            description = transaction.description or ""
                    except:
                        description = ""

                desc_item = QTableWidgetItem(description)
                self.original_values[row][2] = description
                if history_entry.transaction_id is None:
                    desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 2, desc_item)

                # Type (read-only)
                type_text = "Starting Balance" if history_entry.transaction_id is None else "Transaction"
                type_item = QTableWidgetItem(type_text)
                type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 3, type_item)

                # Running Total (read-only)
                # For starting balance, show the starting amount (change_amount), not accumulated total
                if history_entry.transaction_id is None:
                    total_display = f"${history_entry.change_amount:.2f}"
                else:
                    total_display = f"${history_entry.running_total:.2f}"
                total_item = QTableWidgetItem(total_display)
                total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 4, total_item)

            # Clear loading flag to re-enable cellChanged signal
            self.loading_data = False

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Load Error", f"Error loading transactions: {str(e)}")

    def on_selection_changed(self):
        """Handle row selection - highlight entire row subtly"""
        try:
            colors = theme_manager.get_colors()
            hover_color = colors.get('hover', '#2A2A2A')

            # Reset all rows to default colors first (unless edited or marked for deletion)
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        # Check if this row is marked for deletion
                        if row in self.rows_to_delete:
                            continue  # Keep red text for deleted rows

                        # Check if this cell has pending changes
                        if row in self.pending_changes and col in self.pending_changes[row]:
                            continue  # Keep edited cell highlighting

                        # Reset to default
                        item.setBackground(Qt.GlobalColor.transparent)
                        item.setForeground(Qt.GlobalColor.white)

            # Highlight selected row(s)
            selected_items = self.table.selectedItems()
            if selected_items:
                selected_rows = set(item.row() for item in selected_items)
                for row in selected_rows:
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        if item:
                            # Don't override deletion highlighting
                            if row in self.rows_to_delete:
                                continue
                            # Don't override edited cell highlighting
                            if row in self.pending_changes and col in self.pending_changes[row]:
                                continue
                            # Apply subtle row highlight
                            from PyQt6.QtGui import QColor
                            item.setBackground(QColor(hover_color))

        except Exception:
            pass  # Silently ignore selection errors

    def on_cell_changed(self, row, column):
        """Track cell changes but don't save immediately"""
        try:
            # Ignore signals during data loading
            if self.loading_data:
                return

            # Only track changes to editable columns (0=Date, 1=Amount, 2=Description)
            if column not in [0, 1, 2]:
                return

            transaction_id = self.transaction_ids.get(row)

            if not transaction_id:
                return  # Can't edit starting balance

            # Get the new value
            item = self.table.item(row, column)
            if not item:
                return

            new_value = item.text()

            # Check if value actually changed from original
            original_value = self.original_values.get(row, {}).get(column, "")
            if new_value == original_value:
                # Value reverted to original - remove from pending changes
                if row in self.pending_changes and column in self.pending_changes[row]:
                    del self.pending_changes[row][column]
                    if not self.pending_changes[row]:  # Remove row if no changes left
                        del self.pending_changes[row]
                    # Clear highlight
                    item.setBackground(Qt.GlobalColor.transparent)
                return

            # Store the pending change
            if row not in self.pending_changes:
                self.pending_changes[row] = {}

            self.pending_changes[row][column] = new_value

            # Mark cell as changed visually with subtle theme-based color
            colors = theme_manager.get_colors()
            warning_color = colors.get('warning', '#FACC15')
            surface_color = colors.get('surface', '#161616')

            # Blend warning color with surface for subtle highlight
            from PyQt6.QtGui import QColor
            warning_qcolor = QColor(warning_color)
            surface_qcolor = QColor(surface_color)

            # Mix 25% warning with 75% surface for subtle effect
            blend_r = int(surface_qcolor.red() * 0.75 + warning_qcolor.red() * 0.25)
            blend_g = int(surface_qcolor.green() * 0.75 + warning_qcolor.green() * 0.25)
            blend_b = int(surface_qcolor.blue() * 0.75 + warning_qcolor.blue() * 0.25)
            blended_color = QColor(blend_r, blend_g, blend_b)

            item.setBackground(blended_color)

        except Exception:
            pass  # Silently ignore cell change errors

    def mark_for_deletion(self):
        """Mark selected rows for deletion"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select rows to mark for deletion")
            return

        # Check if any selected rows are starting balance
        starting_balance_rows = []
        valid_rows = []

        for row in selected_rows:
            transaction_id = self.transaction_ids.get(row)
            if transaction_id is None:
                starting_balance_rows.append(row)
            else:
                valid_rows.append(row)

        if starting_balance_rows:
            QMessageBox.warning(self, "Cannot Delete", "Starting balance entries cannot be deleted")

        if not valid_rows:
            return

        # Mark rows for deletion (no confirmation popup - confirmation happens at save)
        for row in valid_rows:
            self.rows_to_delete.add(row)
            # Visual indication - make entire row text red
            from PyQt6.QtGui import QColor
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    item.setForeground(QColor("#EF4444"))  # Red text color
                    item.setBackground(Qt.GlobalColor.transparent)  # Clear background


    def save_all_changes(self):
        """Apply all pending changes and deletions to the database"""
        if not self.pending_changes and not self.rows_to_delete:
            QMessageBox.information(self, "No Changes", "No changes to save")
            return

        # Build detailed change list for confirmation
        change_summary = []

        # List edits
        for row, changes in self.pending_changes.items():
            transaction_id = self.transaction_ids.get(row)
            if not transaction_id:
                continue

            for column, new_value in changes.items():
                field_names = {0: "Date", 1: "Amount", 2: "Description"}
                field_name = field_names.get(column, f"Column {column}")
                original_value = self.original_values.get(row, {}).get(column, "")

                change_summary.append(
                    f"Transaction {transaction_id}: Change {field_name} from '{original_value}' to '{new_value}'"
                )

        # List deletions
        for row in self.rows_to_delete:
            transaction_id = self.transaction_ids.get(row)
            if transaction_id:
                change_summary.append(f"Transaction {transaction_id}: Remove")

        # Show confirmation dialog
        if change_summary:
            message = "Proposed Changes:\n\n" + "\n".join(change_summary)
        else:
            message = "No changes to apply"

        reply = QMessageBox.question(self, "Confirm Changes", message,
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Track changes for verification
        changes_log = []

        try:
            from models.transactions import Transaction

            # Apply edits first using transaction_manager to properly handle AccountHistory
            updated_transactions = 0
            for row, changes in self.pending_changes.items():
                transaction_id = self.transaction_ids.get(row)

                if not transaction_id:
                    continue

                transaction = self.transaction_manager.db.query(Transaction).filter_by(id=transaction_id).first()
                if not transaction:
                    continue

                # Build update data for transaction_manager
                update_data = {}

                for column, new_value in changes.items():
                    if column == 0:  # Date
                        try:
                            new_date = datetime.strptime(new_value, '%Y-%m-%d').date()
                            update_data['date'] = new_date
                        except Exception as e:
                            QMessageBox.warning(self, "Invalid Date", f"Invalid date format in row {row+1}: {new_value}")
                            self.transaction_manager.db.rollback()
                            return
                    elif column == 1:  # Amount
                        try:
                            new_amount = float(new_value)
                            # Convert change_amount (what user sees) to transaction.amount
                            # Bills show negative for payments, but transaction stores positive
                            update_data['amount'] = abs(new_amount)
                        except Exception as e:
                            QMessageBox.warning(self, "Invalid Amount", f"Invalid amount in row {row+1}: {new_value}")
                            self.transaction_manager.db.rollback()
                            return
                    elif column == 2:  # Description
                        update_data['description'] = new_value

                # Use transaction_manager to update - this will handle AccountHistory properly
                if update_data:
                    try:
                        result = self.transaction_manager.update_transaction(transaction_id, update_data)
                        updated_transactions += 1

                        # Log change for verification
                        for col, val in changes.items():
                            field_names = {0: "Date", 1: "Amount", 2: "Description"}
                            field_name = field_names.get(col, f"Column {col}")
                            original = self.original_values.get(row, {}).get(col, "")
                            changes_log.append({
                                'type': 'edit',
                                'transaction_id': transaction_id,
                                'field': field_name,
                                'original': original,
                                'new': val,
                                'success': True
                            })
                    except Exception as e:
                        # Log failed change
                        for col, val in changes.items():
                            field_names = {0: "Date", 1: "Amount", 2: "Description"}
                            field_name = field_names.get(col, f"Column {col}")
                            original = self.original_values.get(row, {}).get(col, "")
                            changes_log.append({
                                'type': 'edit',
                                'transaction_id': transaction_id,
                                'field': field_name,
                                'original': original,
                                'new': val,
                                'success': False,
                                'error': str(e)
                            })

                        QMessageBox.warning(self, "Update Error", f"Failed to update transaction: {str(e)}")
                        self.transaction_manager.db.rollback()
                        return

            # Delete marked transactions using transaction_manager
            deleted_transactions = 0
            for row in self.rows_to_delete:
                transaction_id = self.transaction_ids.get(row)

                if not transaction_id:
                    continue

                try:
                    result = self.transaction_manager.delete_transaction(transaction_id)
                    deleted_transactions += 1

                    # Log deletion for verification
                    changes_log.append({
                        'type': 'delete',
                        'transaction_id': transaction_id,
                        'success': True
                    })
                except Exception as e:
                    # Log failed deletion
                    changes_log.append({
                        'type': 'delete',
                        'transaction_id': transaction_id,
                        'success': False,
                        'error': str(e)
                    })

                    QMessageBox.warning(self, "Delete Error", f"Failed to delete transaction: {str(e)}")
                    self.transaction_manager.db.rollback()
                    return

            # Trigger rollover recalculation
            try:
                current_week = self.transaction_manager.get_current_week()
                if current_week:
                    self.transaction_manager.trigger_rollover_recalculation(current_week.week_number)
            except Exception:
                pass  # Non-critical, continue

            # Success - reload and notify
            self.load_transactions()
            self.bill_updated.emit(self.bill)

            # Show post-save report only in testing mode
            if is_testing_mode():
                self.show_verification_report(changes_log, updated_transactions, deleted_transactions)

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Save Error", f"Failed to save changes: {str(e)}")
            self.transaction_manager.db.rollback()
            self.load_transactions()

    def show_verification_report(self, changes_log, expected_updates, expected_deletes):
        """Show post-save verification report in testing mode"""
        try:
            # Verify changes were applied by re-querying database
            from models.transactions import Transaction

            verification_results = []
            failed_changes = []
            successful_changes = []

            for change in changes_log:
                transaction_id = change['transaction_id']

                if change['type'] == 'edit':
                    # Verify the edit was applied
                    transaction = self.transaction_manager.db.query(Transaction).filter_by(id=transaction_id).first()

                    if not transaction:
                        failed_changes.append(
                            f"Failed: Transaction {transaction_id} - Not found in database"
                        )
                        continue

                    # Check if the field was updated correctly
                    field = change['field']
                    expected_value = change['new']

                    if field == "Date":
                        actual_value = str(transaction.date)
                        values_match = actual_value == expected_value
                    elif field == "Amount":
                        actual_value = f"{transaction.amount:.2f}"
                        # Compare as floats to handle decimal formatting differences
                        try:
                            values_match = abs(float(actual_value) - float(expected_value)) < 0.01
                        except:
                            values_match = actual_value == expected_value
                    elif field == "Description":
                        actual_value = transaction.description or ""
                        values_match = actual_value == expected_value
                    else:
                        actual_value = ""
                        values_match = actual_value == expected_value

                    if values_match:
                        successful_changes.append(
                            f"Transaction {transaction_id}: Changed {field} from '{change['original']}' to '{expected_value}'"
                        )
                    else:
                        failed_changes.append(
                            f"Failed: Transaction {transaction_id} - {field} expected '{expected_value}', found '{actual_value}'"
                        )

                elif change['type'] == 'delete':
                    # Verify deletion
                    transaction = self.transaction_manager.db.query(Transaction).filter_by(id=transaction_id).first()

                    if transaction:
                        failed_changes.append(
                            f"Failed: Transaction {transaction_id} - Still exists (deletion failed)"
                        )
                    else:
                        successful_changes.append(
                            f"Transaction {transaction_id}: Removed"
                        )

            # Build report
            report_lines = []

            if successful_changes:
                report_lines.append("=== SUCCESSFUL CHANGES ===")
                report_lines.extend(successful_changes)
                report_lines.append("")

            if failed_changes:
                report_lines.append("=== FAILED CHANGES ===")
                report_lines.extend(failed_changes)
                report_lines.append("")

            # Summary
            total_expected = len(changes_log)
            total_successful = len(successful_changes)
            total_failed = len(failed_changes)

            report_lines.append("=== SUMMARY ===")
            report_lines.append(f"Expected changes: {total_expected}")
            report_lines.append(f"Successful: {total_successful}")
            report_lines.append(f"Failed: {total_failed}")

            report = "\n".join(report_lines)

            # Show report
            QMessageBox.information(self, "Testing Mode - Verification Report", report)

        except Exception:
            pass  # Silently ignore report generation errors

    def apply_theme(self):
        """Apply current theme - with hover effect for editable cells"""
        try:
            colors = theme_manager.get_colors()
            hover_color = colors.get('hover', '#2A2A2A')

            # Apply theme with hover effect
            self.setStyleSheet(f"""
                QDialog {{
                    background-color: {colors.get('background', '#2b2b2b')};
                    color: {colors.get('text_primary', '#ffffff')};
                }}

                QTableWidget::item:hover {{
                    background-color: {hover_color};
                }}

                QTableWidget::item:selected {{
                    background-color: {colors.get('primary', '#49A041')};
                }}
            """)
        except Exception as e:
            # Fall back to basic styling
            self.setStyleSheet("QDialog { background-color: #2b2b2b; color: #ffffff; }")
