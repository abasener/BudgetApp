"""
Transaction History Dialog - Admin controls for editing bill transactions
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
                             QTableWidgetItem, QPushButton, QMessageBox, QHeaderView,
                             QComboBox, QDoubleSpinBox, QDateEdit, QLineEdit, QCheckBox,
                             QFormLayout, QGroupBox, QFrame)
from PyQt6.QtCore import QDate, pyqtSignal, Qt
from datetime import date
from themes import theme_manager


class TransactionEditor(QDialog):
    """Dialog for editing a single transaction"""
    
    def __init__(self, transaction, bill, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction = transaction
        self.bill = bill
        self.transaction_manager = transaction_manager
        self.original_values = {}
        
        self.setWindowTitle(f"Edit Transaction: {transaction.description}")
        self.setModal(True)
        self.resize(500, 400)
        
        self.init_ui()
        self.load_transaction_data()
        self.apply_theme()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Transaction Editor - Admin Controls")
        header.setFont(theme_manager.get_font("subtitle"))
        layout.addWidget(header)
        
        # Warning
        warning = QLabel("⚠️ Changes will rebalance money between bill and current week")
        warning.setStyleSheet(f"color: {theme_manager.get_colors().get('warning', 'orange')}; font-weight: bold; padding: 8px; background-color: rgba(255, 165, 0, 0.1); border-radius: 4px;")
        layout.addWidget(warning)
        
        # Form fields
        form = QFormLayout()
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["spending", "bill_pay", "saving", "income"])
        form.addRow("Type:", self.type_combo)
        
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(-99999.99, 99999.99)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setSuffix(" $")
        form.addRow("Amount:", self.amount_spin)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("MM/dd/yyyy")
        self.date_edit.setCalendarPopup(True)
        form.addRow("Date:", self.date_edit)
        
        self.description_edit = QLineEdit()
        form.addRow("Description:", self.description_edit)
        
        self.week_spin = QDoubleSpinBox()
        self.week_spin.setRange(1, 999)
        self.week_spin.setDecimals(0)
        form.addRow("Week Number:", self.week_spin)
        
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)  # Allow typing new values
        self.category_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Don't auto-add to list
        # Populate with existing categories
        self.populate_categories()
        form.addRow("Category:", self.category_combo)
        
        self.include_analytics = QCheckBox()
        form.addRow("Include in Analytics:", self.include_analytics)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.delete_button = QPushButton("Delete Transaction")
        self.delete_button.clicked.connect(self.delete_transaction)
        self.delete_button.setStyleSheet(f"background-color: {theme_manager.get_colors().get('error', '#dc3545')}; color: white;")
        button_layout.addWidget(self.delete_button)
        
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        self.save_button.setStyleSheet("font-weight: bold;")
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def populate_categories(self):
        """Populate category dropdown with existing categories"""
        try:
            # Get all existing transactions
            transactions = self.transaction_manager.get_all_transactions()
            
            # Extract unique categories
            categories = set()
            for transaction in transactions:
                if transaction.category:
                    categories.add(transaction.category)
            
            # Add common categories
            common_categories = ["Food", "Transportation", "Entertainment", "Shopping", "Utilities",
                               "Healthcare", "Personal Care", "Education", "Miscellaneous", "Bills"]
            categories.update(common_categories)
            
            # Sort and add to combo
            sorted_categories = sorted(list(categories))
            self.category_combo.addItems(sorted_categories)
            
        except Exception as e:
            print(f"Error populating categories: {e}")
            # Add fallback common categories
            self.category_combo.addItems(["Food", "Transportation", "Entertainment", "Shopping"])
    
    def load_transaction_data(self):
        """Load transaction data into form"""
        self.original_values = {
            'transaction_type': self.transaction.transaction_type,
            'amount': self.transaction.amount,
            'date': self.transaction.date,
            'description': self.transaction.description or "",
            'week_number': self.transaction.week_number,
            'category': self.transaction.category or "",
            'include_in_analytics': self.transaction.include_in_analytics or False
        }
        
        # Set form values
        type_index = self.type_combo.findText(self.transaction.transaction_type)
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)
        
        self.amount_spin.setValue(self.transaction.amount)
        
        if self.transaction.date:
            qdate = QDate(self.transaction.date.year, self.transaction.date.month, self.transaction.date.day)
            self.date_edit.setDate(qdate)
        
        self.description_edit.setText(self.transaction.description or "")
        self.week_spin.setValue(self.transaction.week_number)
        self.category_combo.setCurrentText(self.transaction.category or "")
        self.include_analytics.setChecked(self.transaction.include_in_analytics or False)
    
    def calculate_money_adjustments(self, old_amount, new_amount):
        """Calculate how money should be rebalanced"""
        amount_difference = new_amount - old_amount
        
        adjustments = {
            'bill_running_total_change': 0,
            'current_week_change': 0,
            'explanation': ""
        }
        
        transaction_type = self.transaction.transaction_type
        
        if transaction_type == "saving":
            # Savings to bill: increase = more to bill, less to current week
            adjustments['bill_running_total_change'] = amount_difference
            adjustments['current_week_change'] = -amount_difference
            adjustments['explanation'] = f"Bill balance: {amount_difference:+.2f}, Current week: {-amount_difference:+.2f}"
            
        elif transaction_type == "bill_pay":
            # Bill payment: increase = more paid, money comes from bill only
            adjustments['bill_running_total_change'] = -amount_difference
            adjustments['current_week_change'] = 0  # Payments don't affect current week
            adjustments['explanation'] = f"Bill balance: {-amount_difference:+.2f}, Current week: no change"
        
        return adjustments
    
    def save_changes(self):
        """Save transaction changes with money rebalancing"""
        try:
            # Get new values
            new_values = {
                'transaction_type': self.type_combo.currentText(),
                'amount': self.amount_spin.value(),
                'date': date(self.date_edit.date().year(), 
                         self.date_edit.date().month(), 
                         self.date_edit.date().day()),
                'description': self.description_edit.text().strip(),
                'week_number': int(self.week_spin.value()),
                'category': self.category_combo.currentText().strip(),
                'include_in_analytics': self.include_analytics.isChecked()
            }
            
            # Check for changes
            changes = []
            for field, new_value in new_values.items():
                old_value = self.original_values[field]
                if new_value != old_value:
                    if field == 'amount':
                        changes.append(f"{field}: ${old_value:.2f} → ${new_value:.2f}")
                    else:
                        changes.append(f"{field}: {old_value} → {new_value}")
            
            if not changes:
                QMessageBox.information(self, "No Changes", "No changes were made.")
                return
            
            # Calculate money adjustments for amount changes
            old_amount = self.original_values['amount']
            new_amount = new_values['amount']
            adjustments = self.calculate_money_adjustments(old_amount, new_amount)
            
            # Show confirmation dialog
            change_text = "You are about to change:\n\n" + "\n".join(changes)
            if adjustments['explanation']:
                change_text += f"\n\nMoney rebalancing:\n{adjustments['explanation']}"
            change_text += "\n\nAre you sure you want to continue?"
            
            reply = QMessageBox.question(self, "Confirm Changes", change_text,
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Apply changes to transaction
            self.transaction.transaction_type = new_values['transaction_type']
            self.transaction.amount = new_values['amount']
            self.transaction.date = new_values['date']
            self.transaction.description = new_values['description']
            self.transaction.week_number = new_values['week_number']
            self.transaction.category = new_values['category']
            self.transaction.include_in_analytics = new_values['include_in_analytics']
            
            # Apply money rebalancing
            if adjustments['bill_running_total_change'] != 0:
                self.bill.running_total += adjustments['bill_running_total_change']
            
            if adjustments['current_week_change'] != 0:
                current_week = self.transaction_manager.get_current_week()
                if current_week:
                    current_week.running_total += adjustments['current_week_change']
            
            # Save to database
            self.transaction_manager.db.commit()
            
            QMessageBox.information(self, "Success", "Transaction updated successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving changes: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def delete_transaction(self):
        """Delete transaction with money rebalancing"""
        try:
            # Calculate money to return
            amount = self.transaction.amount
            transaction_type = self.transaction.transaction_type
            
            return_text = f"Delete transaction: ${amount:.2f} ({transaction_type})\n\n"
            
            if transaction_type == "saving":
                return_text += f"This will remove ${amount:.2f} from bill and add it to current week."
            elif transaction_type == "bill_pay":
                return_text += f"This will add ${amount:.2f} back to bill balance."
            
            return_text += "\n\nAre you sure you want to delete this transaction?"
            
            reply = QMessageBox.question(self, "Confirm Deletion", return_text,
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Reverse the money effects
            if transaction_type == "saving":
                # Return money from bill to current week
                self.bill.running_total -= amount
                current_week = self.transaction_manager.get_current_week()
                if current_week:
                    current_week.running_total += amount
            elif transaction_type == "bill_pay":
                # Return money to bill
                self.bill.running_total += amount
            
            # Delete transaction
            self.transaction_manager.db.delete(self.transaction)
            self.transaction_manager.db.commit()
            
            QMessageBox.information(self, "Success", "Transaction deleted successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error deleting transaction: {str(e)}")
    
    def apply_theme(self):
        """Apply current theme"""
        colors = theme_manager.get_colors()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['surface']};
                color: {colors['text_primary']};
            }}
        """)


class TransactionHistoryDialog(QDialog):
    """Dialog for viewing and editing all transactions for a bill"""
    
    bill_updated = pyqtSignal(object)  # Signal when transactions are modified
    
    def __init__(self, bill, transaction_manager, parent=None):
        super().__init__(parent)
        self.bill = bill
        self.transaction_manager = transaction_manager
        
        self.setWindowTitle(f"Transaction History: {bill.name}")
        self.setModal(True)
        self.resize(900, 600)
        
        self.init_ui()
        self.load_transactions()
        self.apply_theme()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel(f"Transaction History: {self.bill.name}")
        header.setFont(theme_manager.get_font("title"))
        layout.addWidget(header)
        
        # Info
        info = QLabel("Admin controls for editing and deleting transactions. Changes will rebalance money flows.")
        info.setStyleSheet(f"color: {theme_manager.get_colors().get('warning', 'orange')}; padding: 8px; background-color: rgba(255, 165, 0, 0.1); border-radius: 4px;")
        layout.addWidget(info)
        
        # Transaction table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Date", "Type", "Amount", "Description", "Week", "Category", "Analytics"
        ])
        
        # Configure table
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        
        # Configure table stretching
        header = self.table.horizontalHeader()
        
        # Set specific columns to stretch and others to fit content
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Amount
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)           # Description - stretches
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Week
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Category
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Analytics
        
        # Double-click to edit
        self.table.itemDoubleClicked.connect(self.edit_selected_transaction)
        
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_transactions)
        button_layout.addWidget(self.refresh_button)
        
        self.edit_button = QPushButton("Edit Selected")
        self.edit_button.clicked.connect(self.edit_selected_transaction)
        button_layout.addWidget(self.edit_button)
        
        button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_transactions(self):
        """Load all transactions for this bill"""
        try:
            # Get all transactions for this bill
            all_transactions = self.transaction_manager.get_all_transactions()
            bill_transactions = []
            
            for transaction in all_transactions:
                if ((hasattr(transaction, 'bill_id') and transaction.bill_id == self.bill.id) or 
                    (hasattr(transaction, 'bill_type') and transaction.bill_type == self.bill.name)):
                    bill_transactions.append(transaction)
            
            # Sort by date (newest first)
            bill_transactions.sort(key=lambda t: t.date, reverse=True)
            
            # Populate table
            self.table.setRowCount(len(bill_transactions))
            
            for row, transaction in enumerate(bill_transactions):
                # Store transaction object in first column for reference
                date_item = QTableWidgetItem(str(transaction.date))
                date_item.setData(Qt.ItemDataRole.UserRole, transaction)
                self.table.setItem(row, 0, date_item)
                
                self.table.setItem(row, 1, QTableWidgetItem(transaction.transaction_type))
                self.table.setItem(row, 2, QTableWidgetItem(f"${transaction.amount:.2f}"))
                self.table.setItem(row, 3, QTableWidgetItem(transaction.description or ""))
                self.table.setItem(row, 4, QTableWidgetItem(str(transaction.week_number)))
                self.table.setItem(row, 5, QTableWidgetItem(transaction.category or ""))
                self.table.setItem(row, 6, QTableWidgetItem("Yes" if transaction.include_in_analytics else "No"))
            
            # Table automatically handles resizing with the header settings
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading transactions: {str(e)}")
    
    def edit_selected_transaction(self):
        """Edit the selected transaction"""
        try:
            current_row = self.table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "No Selection", "Please select a transaction to edit.")
                return
            
            # Get transaction from first column's user data
            date_item = self.table.item(current_row, 0)
            transaction = date_item.data(Qt.ItemDataRole.UserRole)
            
            if not transaction:
                QMessageBox.warning(self, "Error", "Could not find transaction data.")
                return
            
            # Open editor dialog
            editor = TransactionEditor(transaction, self.bill, self.transaction_manager, self)
            if editor.exec() == QDialog.DialogCode.Accepted:
                # Refresh table and emit signal
                self.load_transactions()
                self.bill_updated.emit(self.bill)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error editing transaction: {str(e)}")
    
    def apply_theme(self):
        """Apply current theme"""
        colors = theme_manager.get_colors()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['surface']};
                color: {colors['text_primary']};
            }}
            QTableWidget {{
                background-color: {colors['surface']};
                alternate-background-color: {colors['surface_variant']};
                gridline-color: {colors['border']};
                color: {colors['text_primary']};
            }}
            QTableWidget::item:selected {{
                background-color: {colors['primary']};
                color: {colors['background']};
            }}
            QTableWidget::item:hover {{
                background-color: {colors['hover']};
            }}
            QHeaderView::section {{
                background-color: {colors['surface_variant']};
                border: 1px solid {colors['border']};
                padding: 4px;
                font-weight: bold;
                color: {colors['text_primary']};
            }}
        """)