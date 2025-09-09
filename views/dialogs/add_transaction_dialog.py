"""
Add Transaction Dialog - Dynamic form based on transaction type
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QComboBox, QLineEdit, QDoubleSpinBox, QDateEdit,
                             QCheckBox, QPushButton, QLabel, QTextEdit, QMessageBox)
from PyQt6.QtCore import QDate
from datetime import date

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
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Transaction Type Selection
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Spending",
            "Bill Payment", 
            "Saving"
        ])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        form_layout.addRow("Transaction Type:", self.type_combo)
        
        # Basic fields (always visible)
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0.01, 99999.99)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setValue(0.01)
        form_layout.addRow("Amount ($):", self.amount_spin)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Date:", self.date_edit)
        
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("e.g., 'Paid someone else's gas, will get reimbursed'")
        form_layout.addRow("Notes:", self.notes_edit)
        
        # Dynamic fields container
        self.dynamic_layout = QFormLayout()
        
        # Spending-specific fields
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)  # Allow typing new categories
        self.category_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Don't auto-add to list
        self.analytics_checkbox = QCheckBox("Include in analytics (uncheck for abnormal transactions)")
        self.analytics_checkbox.setChecked(True)
        
        # Bill-specific fields
        self.bill_combo = QComboBox()
        
        # Saving-specific fields
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
        
        # Initialize with spending fields
        self.on_type_changed("Spending")
    
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
    
    def on_type_changed(self, transaction_type):
        """Update form based on selected transaction type"""
        self.clear_dynamic_fields()
        
        if transaction_type == "Spending":
            self.dynamic_layout.addRow("Category:", self.category_combo)
            self.dynamic_layout.addRow("", self.analytics_checkbox)
            
            self.category_combo.setVisible(True)
            self.analytics_checkbox.setVisible(True)
            self.bill_combo.setVisible(False)
            self.account_combo.setVisible(False)
            
        elif transaction_type == "Bill Payment":
            self.dynamic_layout.addRow("Bill:", self.bill_combo)
            
            self.category_combo.setVisible(False)
            self.analytics_checkbox.setVisible(False)
            self.bill_combo.setVisible(True)
            self.account_combo.setVisible(False)
            
        elif transaction_type == "Saving":
            self.dynamic_layout.addRow("Account:", self.account_combo)
            
            self.category_combo.setVisible(False)
            self.analytics_checkbox.setVisible(False)
            self.bill_combo.setVisible(False)
            self.account_combo.setVisible(True)
    
    def validate_form(self):
        """Validate form data"""
        if self.amount_spin.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Amount must be greater than 0")
            return False
        
        transaction_type = self.type_combo.currentText()
        
        if transaction_type == "Spending" and not self.category_combo.currentText().strip():
            QMessageBox.warning(self, "Validation Error", "Category is required for spending transactions")
            return False
        
        if transaction_type == "Bill Payment" and self.bill_combo.currentData() is None:
            QMessageBox.warning(self, "Validation Error", "Please select a bill")
            return False
        
        if transaction_type == "Saving" and self.account_combo.currentData() is None:
            QMessageBox.warning(self, "Validation Error", "Please select an account")
            return False
        
        return True
    
    def save_transaction(self):
        """Save the transaction to database"""
        if not self.validate_form():
            return
        
        try:
            transaction_type = self.type_combo.currentText()
            transaction_date = self.date_edit.date().toPython()
            
            # Calculate week number from date
            week_number = self.calculate_week_from_date(transaction_date)
            
            # Base transaction data
            self.transaction_data = {
                "transaction_type": self.get_transaction_type_value(transaction_type),
                "amount": self.amount_spin.value(),
                "date": transaction_date,
                "description": self.notes_edit.text().strip(),
                "week_number": week_number
            }
            
            # Add type-specific fields
            if transaction_type == "Spending":
                self.transaction_data.update({
                    "category": self.category_combo.currentText().strip(),
                    "include_in_analytics": self.analytics_checkbox.isChecked()
                })
                
            elif transaction_type == "Bill Payment":
                self.transaction_data.update({
                    "bill_id": self.bill_combo.currentData()
                })
                
            elif transaction_type == "Saving":
                self.transaction_data.update({
                    "account_id": self.account_combo.currentData()
                })
            
            # Save to database
            transaction = self.transaction_manager.add_transaction(self.transaction_data)
            
            QMessageBox.information(self, "Success", f"Transaction saved successfully!\n\nID: {transaction.id}")
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
    
    def get_transaction_type_value(self, display_name):
        """Convert display name to database enum value"""
        mapping = {
            "Spending": TransactionType.SPENDING.value,
            "Bill Payment": TransactionType.BILL_PAY.value,
            "Saving": TransactionType.SAVING.value
        }
        return mapping.get(display_name, TransactionType.SPENDING.value)