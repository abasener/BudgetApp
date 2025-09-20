"""
Bill Transaction History Dialog - Direct table editing for bill transactions
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QDateEdit, QDoubleSpinBox,
                             QStyledItemDelegate, QWidget, QAbstractItemView)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from datetime import datetime, date
from themes import theme_manager


class DateEditDelegate(QStyledItemDelegate):
    """Simplified delegate for date editing in table cells"""

    def createEditor(self, parent, option, index):
        try:
            editor = QDateEdit(parent)
            editor.setCalendarPopup(True)
            editor.setDate(QDate.currentDate())
            return editor
        except Exception as e:
            return None

    def setEditorData(self, editor, index):
        try:
            if editor is None:
                return
            value = index.model().data(index, Qt.ItemDataRole.EditRole)
            if isinstance(value, str):
                try:
                    date_obj = datetime.strptime(value, '%Y-%m-%d').date()
                    editor.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
                except:
                    editor.setDate(QDate.currentDate())
            elif isinstance(value, date):
                editor.setDate(QDate(value.year, value.month, value.day))
        except Exception as e:

    def setModelData(self, editor, model, index):
        try:
            if editor is None:
                return
            date_value = editor.date().toPython()
            model.setData(index, date_value.strftime('%Y-%m-%d'), Qt.ItemDataRole.EditRole)
        except Exception as e:


class AmountEditDelegate(QStyledItemDelegate):
    """Simplified delegate for amount editing in table cells"""

    def createEditor(self, parent, option, index):
        try:
            editor = QDoubleSpinBox(parent)
            editor.setRange(-99999.99, 99999.99)
            editor.setDecimals(2)
            return editor
        except Exception as e:
            return None

    def setEditorData(self, editor, index):
        try:
            if editor is None:
                return
            value = index.model().data(index, Qt.ItemDataRole.EditRole)
            if isinstance(value, str):
                try:
                    # Remove $ and parse
                    amount = float(value.replace('$', '').replace(',', ''))
                    editor.setValue(amount)
                except:
                    editor.setValue(0.0)
            elif isinstance(value, (int, float)):
                editor.setValue(value)
        except Exception as e:

    def setModelData(self, editor, model, index):
        try:
            if editor is None:
                return
            model.setData(index, editor.value(), Qt.ItemDataRole.EditRole)
        except Exception as e:


class BillTransactionHistoryDialog(QDialog):
    """Dialog for direct table editing of bill transactions"""

    bill_updated = pyqtSignal(object)  # Signal when transactions are modified

    def __init__(self, bill, transaction_manager, parent=None):
        try:
            super().__init__(parent)
            self.bill = bill
            self.transaction_manager = transaction_manager
            self.original_transactions = {}  # Store original transaction data for change tracking
            self.deleted_transactions = []  # Track deleted transactions

            self.setWindowTitle(f"Transaction History: {bill.name}")
            self.setModal(True)
            self.resize(1000, 600)

            self.init_ui()

            self.load_transactions()

            self.apply_theme()


            # Force a refresh to ensure everything is properly displayed
            self.update()

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()

        # Header
        header = QLabel(f"Transaction History: {self.bill.name}")
        header.setFont(theme_manager.get_font("title"))
        layout.addWidget(header)

        # Info
        info = QLabel("Direct table editing: Click cells to edit Date, Amount, and Description. Use 'Delete Selected' button or right-click rows to delete. Changes saved on 'Save All'.")
        info.setStyleSheet("color: orange; padding: 8px; background-color: rgba(255, 165, 0, 0.1); border-radius: 4px;")
        layout.addWidget(info)

        # Transaction table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Date", "Amount", "Type", "Description", "ID", "Running Total"
        ])

        # Configure table
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(False)  # Disable sorting to maintain data integrity

        # Configure table stretching
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Amount
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)           # Description - stretches
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Running Total

        # Disable custom delegates for now to prevent crashes
        # TODO: Re-enable delegates once crash is fixed
        # date_delegate = DateEditDelegate()
        # amount_delegate = AmountEditDelegate()
        # self.table.setItemDelegateForColumn(0, date_delegate)
        # self.table.setItemDelegateForColumn(1, amount_delegate)

        # Enable right-click context menu for row deletion
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_transactions)
        button_layout.addWidget(self.refresh_button)

        self.delete_selected_button = QPushButton("Delete Selected")
        self.delete_selected_button.clicked.connect(self.delete_selected_row)
        self.delete_selected_button.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")
        button_layout.addWidget(self.delete_selected_button)

        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Save All Changes")
        self.save_button.clicked.connect(self.save_all_changes)
        self.save_button.setStyleSheet("font-weight: bold; background-color: #28a745; color: white;")
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_transactions(self):
        """Load all transactions for this bill using AccountHistory"""
        try:

            # Get AccountHistory entries directly for this bill
            from models.account_history import AccountHistoryManager

            history_manager = AccountHistoryManager(self.transaction_manager.db)
            account_history = history_manager.get_account_history(self.bill.id, "bill")

            # Include both transaction entries AND starting balance entries
            all_history = account_history  # Show all entries including starting balance

            # Sort by date (newest first)
            all_history.sort(key=lambda h: h.transaction_date, reverse=True)

            # Reset tracking
            self.original_transactions = {}
            self.deleted_transactions = []

            # Populate table
            self.table.setRowCount(len(all_history))

            for row, history_entry in enumerate(all_history):

                # Store original data for change tracking
                self.original_transactions[history_entry.id] = {
                    'date': history_entry.transaction_date,
                    'amount': history_entry.change_amount,
                    'running_total': history_entry.running_total,
                    'transaction_id': history_entry.transaction_id,
                    'history_entry': history_entry
                }

                try:
                    # Date column (editable)
                    date_item = QTableWidgetItem(str(history_entry.transaction_date))
                    date_item.setData(Qt.ItemDataRole.UserRole, history_entry.id)  # Store history entry ID
                    date_item.setFlags(date_item.flags() | Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row, 0, date_item)

                    # Amount column (editable)
                    amount_item = QTableWidgetItem(f"{history_entry.change_amount:.2f}")
                    amount_item.setFlags(amount_item.flags() | Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row, 1, amount_item)

                    # Type column (read-only, informational)
                    if history_entry.transaction_id is None:
                        # This is a starting balance entry
                        type_item = QTableWidgetItem("Starting Balance")
                        type_item.setStyleSheet("color: #007acc; font-weight: bold;")  # Blue color for starting balance
                    else:
                        # This is a regular transaction
                        type_item = QTableWidgetItem("Transaction")

                    type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row, 2, type_item)

                    # Description column (read-only for starting balance, editable for transactions)
                    description = ""
                    is_starting_balance = history_entry.transaction_id is None

                    if is_starting_balance:
                        # Starting balance entry - use its description directly
                        description = history_entry.description or "Starting balance"
                    else:
                        # Regular transaction - get description from transaction table
                        try:
                            from models.transactions import Transaction
                            transaction = self.transaction_manager.db.query(Transaction).filter_by(id=history_entry.transaction_id).first()
                            if transaction:
                                description = transaction.description or ""
                            else:
                                description = f"Transaction {history_entry.transaction_id} not found"
                        except Exception as desc_error:
                            description = "Error loading description"

                    desc_item = QTableWidgetItem(description)
                    desc_item.setFlags(desc_item.flags() | Qt.ItemFlag.ItemIsEditable)  # Make editable
                    self.table.setItem(row, 3, desc_item)

                    # ID column (read-only)
                    id_item = QTableWidgetItem(str(history_entry.id))
                    id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row, 4, id_item)

                    # Running Total column (read-only, will be recalculated)
                    total_item = QTableWidgetItem(f"${history_entry.running_total:.2f}")
                    total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row, 5, total_item)


                except Exception as row_error:
                    import traceback
                    traceback.print_exc()
                    # Continue to next row instead of crashing


        except Exception as e:
            error_msg = f"Error loading transactions: {str(e)}"
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", error_msg)

    def show_context_menu(self, position):
        """Show context menu for row deletion"""
        if self.table.itemAt(position) is not None:
            current_row = self.table.currentRow()

            # Check if this is a starting balance entry (non-deletable)
            date_item = self.table.item(current_row, 0)
            history_id = date_item.data(Qt.ItemDataRole.UserRole)

            if history_id in self.original_transactions:
                original = self.original_transactions[history_id]
                history_entry = original['history_entry']

                # Check if this is a starting balance entry
                if history_entry.transaction_id is None:
                    QMessageBox.warning(
                        self,
                        "Cannot Delete Starting Balance",
                        "Starting balance entries cannot be deleted.\n\nYou can edit the starting amount in the 'See More' dialog instead."
                    )
                    return

            menu = QMessageBox()
            menu.setIcon(QMessageBox.Icon.Question)
            menu.setWindowTitle("Delete Row")
            menu.setText("Delete this transaction row?")
            menu.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if menu.exec() == QMessageBox.StandardButton.Yes:
                self.delete_row(current_row)

    def delete_selected_row(self):
        """Delete the currently selected row via button click"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a row to delete.")
            return

        # Check if this is a starting balance entry (non-deletable)
        date_item = self.table.item(current_row, 0)
        history_id = date_item.data(Qt.ItemDataRole.UserRole)

        if history_id in self.original_transactions:
            original = self.original_transactions[history_id]
            history_entry = original['history_entry']

            # Check if this is a starting balance entry
            if history_entry.transaction_id is None:
                QMessageBox.warning(
                    self,
                    "Cannot Delete Starting Balance",
                    "Starting balance entries cannot be deleted.\n\nYou can edit the starting amount in the 'See More' dialog instead."
                )
                return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Mark row {current_row + 1} for deletion?\n\nThis will be applied when you click 'Save All Changes'.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_row(current_row)

    def delete_row(self, row):
        """Mark a row for deletion"""
        if row >= 0 and row < self.table.rowCount():
            # Get history entry ID from first column
            date_item = self.table.item(row, 0)
            history_id = date_item.data(Qt.ItemDataRole.UserRole)

            # Mark for deletion
            if history_id in self.original_transactions:
                self.deleted_transactions.append(self.original_transactions[history_id])

            # Remove from table
            self.table.removeRow(row)

    def save_all_changes(self):
        """Save all changes with confirmation popup"""
        try:
            changes = []

            # Check for deletions
            if self.deleted_transactions:
                changes.append(f"Delete {len(self.deleted_transactions)} transaction(s)")

            # Check for edits
            edits = 0
            for row in range(self.table.rowCount()):
                date_item = self.table.item(row, 0)
                amount_item = self.table.item(row, 1)
                desc_item = self.table.item(row, 3)
                history_id = date_item.data(Qt.ItemDataRole.UserRole)

                if history_id in self.original_transactions:
                    original = self.original_transactions[history_id]
                    new_date_str = date_item.text()
                    new_amount = float(amount_item.text())
                    new_description = desc_item.text()

                    # Get original description
                    original_description = ""
                    history_entry = original['history_entry']

                    if history_entry.transaction_id is None:
                        # Starting balance entry - get description from history entry
                        original_description = history_entry.description or "Starting balance"
                    else:
                        # Regular transaction - get description from transaction table
                        try:
                            from models.transactions import Transaction
                            transaction = self.transaction_manager.db.query(Transaction).filter_by(id=original['transaction_id']).first()
                            if transaction:
                                original_description = transaction.description or ""
                        except:
                            pass

                    # Check for changes
                    date_changed = str(original['date']) != new_date_str
                    amount_changed = abs(original['amount'] - new_amount) > 0.01
                    description_changed = original_description != new_description

                    if date_changed or amount_changed or description_changed:
                        edits += 1

            if edits > 0:
                changes.append(f"Edit {edits} transaction(s)")

            if not changes:
                QMessageBox.information(self, "No Changes", "No changes were made.")
                return

            # Show confirmation dialog
            change_text = "You are about to:\n\n" + "\n".join(f"• {change}" for change in changes)
            change_text += "\n\nThis will update AccountHistory and recalculate running totals."
            change_text += "\n\nAre you sure you want to continue?"

            reply = QMessageBox.question(self, "Confirm Changes", change_text,
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Apply changes
            from models.account_history import AccountHistoryManager
            history_manager = AccountHistoryManager(self.transaction_manager.db)

            # Process deletions
            for deleted in self.deleted_transactions:
                history_entry = deleted['history_entry']

                # Delete the history entry
                if deleted['transaction_id']:
                    # Also delete the associated transaction
                    from models.transactions import Transaction
                    transaction = self.transaction_manager.db.query(Transaction).filter_by(id=deleted['transaction_id']).first()
                    if transaction:
                        self.transaction_manager.db.delete(transaction)

                self.transaction_manager.db.delete(history_entry)

            # Process edits
            for row in range(self.table.rowCount()):
                date_item = self.table.item(row, 0)
                amount_item = self.table.item(row, 1)
                desc_item = self.table.item(row, 3)
                history_id = date_item.data(Qt.ItemDataRole.UserRole)

                if history_id in self.original_transactions:
                    original = self.original_transactions[history_id]
                    new_date_str = date_item.text()
                    new_amount = float(amount_item.text())
                    new_description = desc_item.text()

                    # Get original description
                    original_description = ""
                    history_entry = original['history_entry']

                    if history_entry.transaction_id is None:
                        # Starting balance entry - get description from history entry
                        original_description = history_entry.description or "Starting balance"
                    else:
                        # Regular transaction - get description from transaction table
                        try:
                            from models.transactions import Transaction
                            transaction = self.transaction_manager.db.query(Transaction).filter_by(id=original['transaction_id']).first()
                            if transaction:
                                original_description = transaction.description or ""
                        except:
                            pass

                    # Check for changes
                    date_changed = str(original['date']) != new_date_str
                    amount_changed = abs(original['amount'] - new_amount) > 0.01
                    description_changed = original_description != new_description

                    if date_changed or amount_changed or description_changed:
                        history_entry = original['history_entry']

                        # Update the history entry
                        if date_changed:
                            try:
                                new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
                                history_entry.transaction_date = new_date

                                # Also update the transaction date if exists
                                if history_entry.transaction_id:
                                    from models.transactions import Transaction
                                    transaction = self.transaction_manager.db.query(Transaction).filter_by(id=history_entry.transaction_id).first()
                                    if transaction:
                                        transaction.date = new_date
                            except ValueError:
                                QMessageBox.warning(self, "Invalid Date", f"Invalid date format in row {row+1}: {new_date_str}")
                                return

                        if amount_changed:
                            history_entry.change_amount = new_amount

                            # Also update the transaction amount if exists
                            if history_entry.transaction_id:
                                from models.transactions import Transaction
                                transaction = self.transaction_manager.db.query(Transaction).filter_by(id=history_entry.transaction_id).first()
                                if transaction:
                                    transaction.amount = new_amount

                        if description_changed:
                            # Update description
                            if history_entry.transaction_id is None:
                                # Starting balance entry - update history entry description
                                history_entry.description = new_description
                            else:
                                # Regular transaction - update transaction description
                                from models.transactions import Transaction
                                transaction = self.transaction_manager.db.query(Transaction).filter_by(id=history_entry.transaction_id).first()
                                if transaction:
                                    transaction.description = new_description

            # Recalculate all running totals for this bill
            history_manager.recalculate_account_history(self.bill.id, "bill")

            # Commit all changes
            self.transaction_manager.db.commit()

            QMessageBox.information(self, "Success", "All changes saved successfully!")

            # Auto-refresh and reorder: reload transactions to get updated running totals and proper ordering
            self.load_transactions()

            # Trigger rollover recalculation to update any dependent calculations
            try:
                # Get current week to trigger rollover recalculation if needed
                current_week = self.transaction_manager.get_current_week()
                if current_week:
                    self.transaction_manager.trigger_rollover_recalculation(current_week.week_number)
            except Exception as recalc_error:

            # Emit signal to update parent views
            self.bill_updated.emit(self.bill)

        except Exception as e:
            self.transaction_manager.db.rollback()
            QMessageBox.critical(self, "Error", f"Error saving changes: {str(e)}")
            import traceback
            traceback.print_exc()

    def apply_theme(self):
        """Apply current theme"""
        try:
            colors = theme_manager.get_colors()

            # Check for missing colors and provide defaults
            required_colors = ['background', 'text_primary', 'surface', 'surface_variant', 'border', 'primary', 'hover', 'accent']
            for color_key in required_colors:
                if color_key not in colors:
                    colors[color_key] = '#333333'  # Dark gray default

            self.setStyleSheet(f"""
                QDialog {{
                    background-color: {colors['background']};
                    color: {colors['text_primary']};
                }}

                QLabel {{
                    color: {colors['text_primary']};
                }}

                QTableWidget {{
                    background-color: {colors['surface']};
                    alternate-background-color: {colors['surface_variant']};
                    gridline-color: {colors['border']};
                    color: {colors['text_primary']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                }}

                QTableWidget::item {{
                    padding: 4px;
                    border: none;
                }}

                QTableWidget::item:selected {{
                    background-color: {colors['primary']};
                    color: {colors['background']};
                }}

                QTableWidget::item:hover {{
                    background-color: {colors['hover']};
                }}

                QHeaderView::section {{
                    background-color: {colors['surface']};
                    color: {colors['text_primary']};
                    padding: 6px;
                    border: 1px solid {colors['border']};
                    font-weight: bold;
                }}

                QHeaderView::section:hover {{
                    background-color: {colors['hover']};
                }}

                QPushButton {{
                    background-color: {colors['primary']};
                    color: {colors['surface']};
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}

                QPushButton:hover {{
                    background-color: {colors['accent']};
                }}

                QPushButton:pressed {{
                    background-color: {colors['primary']};
                }}
            """)

        except Exception as e:
            import traceback
            traceback.print_exc()
            # Apply a minimal fallback theme
            self.setStyleSheet("QDialog { background-color: #2b2b2b; color: #ffffff; }")