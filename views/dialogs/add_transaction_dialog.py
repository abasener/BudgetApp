"""
Add Transaction Dialog - Dynamic form based on transaction type
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QComboBox, QLineEdit, QDoubleSpinBox, QDateEdit,
                             QCheckBox, QPushButton, QLabel, QTextEdit, QMessageBox)
from PyQt6.QtCore import QDate
from datetime import date
from themes import theme_manager

from models import TransactionType


class AddTransactionDialog(QDialog):
    def __init__(self, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager
        self.setWindowTitle("Add Transaction")
        self.setModal(True)
        self.resize(400, 500)
        
        # Transaction data
        self.transaction_data = {}
        
        self.init_ui()
        self.load_data()
        self.apply_theme()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Mode Selection (3 modes for different types of money movement)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Spending",
            "Bills",
            "Savings"
        ])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        form_layout.addRow("Transaction Mode:", self.mode_combo)
        
        # Basic fields (always visible)
        amount_layout = QHBoxLayout()
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(-99999.99, 99999.99)  # Allow negative values
        self.amount_spin.setDecimals(2)
        self.amount_spin.setValue(1.00)
        amount_layout.addWidget(self.amount_spin)

        # Money flow note (will be updated based on mode)
        self.amount_note = QLabel()
        self.amount_note.setStyleSheet("color: gray; font-size: 11px; font-style: italic;")
        amount_layout.addWidget(self.amount_note)
        form_layout.addRow("Amount ($):", amount_layout)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("MM/dd/yyyy")
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Date:", self.date_edit)
        
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("e.g., 'Paid someone else's gas, will get reimbursed'")
        form_layout.addRow("Notes:", self.notes_edit)
        
        # Dynamic fields container
        self.dynamic_layout = QFormLayout()
        
        # Spending mode fields
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)  # Allow typing new categories
        self.category_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Don't auto-add to list
        self.analytics_checkbox = QCheckBox("Include in analytics")
        self.analytics_checkbox.setChecked(True)

        # Bills mode fields
        self.bill_combo = QComboBox()

        # Savings mode fields
        self.account_combo = QComboBox()
        
        layout.addLayout(form_layout)
        layout.addLayout(self.dynamic_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Transaction")
        self.save_button.clicked.connect(self.save_transaction)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Initialize with spending mode
        self.on_mode_changed("Spending")
    
    def load_data(self):
        """Load accounts, bills, and categories from database"""
        try:
            # Load existing categories from spending transactions
            categories = self.get_existing_categories()
            self.category_combo.clear()
            if categories:
                self.category_combo.addItems(sorted(categories))
            else:
                # Default categories if none exist
                default_categories = ["Food", "Transportation", "Entertainment", "Shopping", 
                                    "Utilities", "Healthcare", "Personal Care", "Miscellaneous"]
                self.category_combo.addItems(default_categories)
            
            # Load accounts
            accounts = self.transaction_manager.get_all_accounts()
            self.account_combo.clear()
            for account in accounts:
                self.account_combo.addItem(account.name, account.id)
            
            # Load bills
            bills = self.transaction_manager.get_all_bills()
            self.bill_combo.clear()
            for bill in bills:
                # Use typical_amount, or show as variable if not set
                display_amount = bill.typical_amount if bill.typical_amount > 0 else "Variable"
                if isinstance(display_amount, float):
                    self.bill_combo.addItem(f"{bill.name} (${display_amount:.2f})", bill.id)
                else:
                    self.bill_combo.addItem(f"{bill.name} ({display_amount})", bill.id)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading data: {str(e)}")
    
    def get_existing_categories(self):
        """Get list of existing categories from spending transactions"""
        try:
            spending_transactions = self.transaction_manager.get_spending_transactions(include_analytics_only=False)
            categories = set()
            for transaction in spending_transactions:
                if transaction.category:
                    categories.add(transaction.category.strip())
            return list(categories)
        except Exception:
            return []
    
    def clear_dynamic_fields(self):
        """Clear all dynamic fields from layout"""
        while self.dynamic_layout.count():
            child = self.dynamic_layout.takeAt(0)
            if child.widget():
                child.widget().setVisible(False)
    
    def on_mode_changed(self, mode):
        """Update form based on selected mode"""
        self.clear_dynamic_fields()

        if mode == "Spending":
            # Update amount note
            self.amount_note.setText("(+ = spent from week, - = gained to week)")

            # Show spending fields
            self.dynamic_layout.addRow("Category:", self.category_combo)
            self.dynamic_layout.addRow("", self.analytics_checkbox)

            self.category_combo.setVisible(True)
            self.analytics_checkbox.setVisible(True)
            self.analytics_checkbox.setChecked(True)  # Default true for spending
            self.bill_combo.setVisible(False)
            self.account_combo.setVisible(False)

        elif mode == "Bills":
            # Update amount note
            self.amount_note.setText("(+ = to bill account, - = from bill account)")

            # Show bills fields
            self.dynamic_layout.addRow("Bill Account:", self.bill_combo)

            self.category_combo.setVisible(False)
            self.analytics_checkbox.setVisible(False)
            self.bill_combo.setVisible(True)
            self.account_combo.setVisible(False)

        elif mode == "Savings":
            # Update amount note
            self.amount_note.setText("(+ = to savings account, - = from savings account)")

            # Show savings fields
            self.dynamic_layout.addRow("Savings Account:", self.account_combo)

            self.category_combo.setVisible(False)
            self.analytics_checkbox.setVisible(False)
            self.bill_combo.setVisible(False)
            self.account_combo.setVisible(True)
    
    def validate_form(self):
        """Validate form data"""
        if self.amount_spin.value() == 0:
            QMessageBox.warning(self, "Validation Error", "Amount cannot be zero")
            return False

        mode = self.mode_combo.currentText()

        if mode == "Spending" and not self.category_combo.currentText().strip():
            QMessageBox.warning(self, "Validation Error", "Category is required for spending transactions")
            return False

        if mode == "Bills" and self.bill_combo.currentData() is None:
            QMessageBox.warning(self, "Validation Error", "Please select a bill account")
            return False

        if mode == "Savings" and self.account_combo.currentData() is None:
            QMessageBox.warning(self, "Validation Error", "Please select a savings account")
            return False

        return True
    
    def save_transaction(self):
        """Save the transaction to database"""
        if not self.validate_form():
            return
        
        try:
            mode = self.mode_combo.currentText()
            transaction_date = self.date_edit.date().toPyDate()
            amount = self.amount_spin.value()

            # Calculate week number from date (auto-generated)
            week_number = self.calculate_week_from_date(transaction_date)

            # Base transaction data
            self.transaction_data = {
                "amount": amount,
                "date": transaction_date,
                "description": self.notes_edit.text().strip(),
                "week_number": week_number
            }

            # Auto-generate transaction_type and mode-specific fields
            if mode == "Spending":
                self.transaction_data.update({
                    "transaction_type": "spending",  # Auto-generated
                    "category": self.category_combo.currentText().strip(),
                    "include_in_analytics": self.analytics_checkbox.isChecked()
                })

            elif mode == "Bills":
                # Determine transaction type based on amount direction
                if amount > 0:
                    # Positive = money TO bill account (saving for bill)
                    self.transaction_data["transaction_type"] = "saving"
                else:
                    # Negative = money FROM bill account (spending from bill savings)
                    self.transaction_data["transaction_type"] = "spending"
                    self.transaction_data["amount"] = abs(amount)  # Make amount positive for spending

                self.transaction_data.update({
                    "bill_id": self.bill_combo.currentData(),
                    "include_in_analytics": False  # Auto-set to false
                })

            elif mode == "Savings":
                # Determine transaction type based on amount direction
                if amount > 0:
                    # Positive = money TO savings account
                    self.transaction_data["transaction_type"] = "saving"
                else:
                    # Negative = money FROM savings account
                    self.transaction_data["transaction_type"] = "spending"
                    self.transaction_data["amount"] = abs(amount)  # Make amount positive for spending

                self.transaction_data.update({
                    "account_id": self.account_combo.currentData(),
                    "include_in_analytics": False  # Auto-set to false
                })

            # Save to database
            transaction = self.transaction_manager.add_transaction(self.transaction_data)

            # Create success message
            mode_text = f"{mode} transaction"
            account_text = ""
            if mode == "Bills":
                bill_name = self.bill_combo.currentText()
                account_text = f"\nBill: {bill_name}"
            elif mode == "Savings":
                account_name = self.account_combo.currentText()
                account_text = f"\nAccount: {account_name}"

            success_msg = f"{mode_text} saved successfully!\n\nID: {transaction.id}{account_text}\nAmount: ${amount:.2f}"
            QMessageBox.information(self, "Success", success_msg)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving transaction: {str(e)}")
    
    def calculate_week_from_date(self, transaction_date):
        """Calculate week number from transaction date"""
        try:
            # Find the week that contains this date
            weeks = self.transaction_manager.get_all_weeks()
            for week in weeks:
                if week.start_date <= transaction_date <= week.end_date:
                    return week.week_number
            
            # If no week contains this date, use current week or create one
            current_week = self.transaction_manager.get_current_week()
            if current_week:
                return current_week.week_number
            else:
                # Fallback to week 1 if no weeks exist
                return 1
                
        except Exception:
            return 1  # Safe fallback
    
    
    def apply_theme(self):
        """Apply current theme to dialog"""
        colors = theme_manager.get_colors()
        
        # Main dialog styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['background']};
                color: {colors['text_primary']};
            }}
            
            QLabel {{
                color: {colors['text_primary']};
            }}
            
            QComboBox {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 4px 8px;
                color: {colors['text_primary']};
                selection-background-color: {colors['primary']};
            }}
            
            QComboBox:hover {{
                background-color: {colors['hover']};
                border: 1px solid {colors['primary']};
            }}
            
            QComboBox:focus {{
                border: 2px solid {colors['primary']};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QComboBox::down-arrow {{
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {colors['text_secondary']};
                margin-right: 4px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                selection-background-color: {colors['primary']};
                selection-color: {colors['background']};
            }}
            
            QLineEdit, QDoubleSpinBox, QDateEdit {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 4px 8px;
                color: {colors['text_primary']};
            }}
            
            QLineEdit:hover, QDoubleSpinBox:hover, QDateEdit:hover {{
                border: 1px solid {colors['primary']};
            }}
            
            QLineEdit:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
                border: 2px solid {colors['primary']};
            }}
            
            QTextEdit {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 4px;
                color: {colors['text_primary']};
            }}
            
            QTextEdit:focus {{
                border: 2px solid {colors['primary']};
            }}
            
            QCheckBox {{
                color: {colors['text_primary']};
            }}
            
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {colors['border']};
                border-radius: 2px;
                background-color: {colors['surface']};
            }}
            
            QCheckBox::indicator:hover {{
                border: 1px solid {colors['primary']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {colors['primary']};
                border: 1px solid {colors['primary']};
            }}
            
            QPushButton {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 6px 12px;
                color: {colors['text_primary']};
            }}
            
            QPushButton:hover {{
                background-color: {colors['hover']};
                border: 1px solid {colors['primary']};
            }}
            
            QPushButton:pressed {{
                background-color: {colors['primary']};
                color: {colors['background']};
            }}
        """)