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
            "Saving",
            "Income"
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
        
        self.description_edit = QLineEdit()
        form_layout.addRow("Description:", self.description_edit)
        
        # Week selection
        self.week_combo = QComboBox()
        form_layout.addRow("Week:", self.week_combo)
        
        # Dynamic fields container
        self.dynamic_layout = QFormLayout()
        
        # Spending-specific fields
        self.category_edit = QLineEdit()
        self.analytics_checkbox = QCheckBox("Include in analytics (uncheck for abnormal transactions)")
        self.analytics_checkbox.setChecked(True)
        
        # Bill-specific fields
        self.bill_combo = QComboBox()
        self.bill_type_edit = QLineEdit()
        
        # Saving-specific fields
        self.account_combo = QComboBox()
        self.account_name_edit = QLineEdit()
        
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
        """Load accounts, bills, and weeks from database"""
        try:
            # Load weeks
            weeks = self.transaction_manager.get_all_weeks()
            self.week_combo.clear()
            for week in weeks:
                self.week_combo.addItem(
                    f"Week {week.week_number} ({week.start_date} to {week.end_date})",
                    week.week_number
                )
            
            # Set current week as default
            current_week = self.transaction_manager.get_current_week()
            if current_week:
                for i in range(self.week_combo.count()):
                    if self.week_combo.itemData(i) == current_week.week_number:
                        self.week_combo.setCurrentIndex(i)
                        break
            
            # Load accounts
            accounts = self.transaction_manager.get_all_accounts()
            self.account_combo.clear()
            for account in accounts:
                self.account_combo.addItem(account.name, account.id)
            
            # Load bills
            bills = self.transaction_manager.get_all_bills()
            self.bill_combo.clear()
            for bill in bills:
                self.bill_combo.addItem(f"{bill.name} (${bill.amount_to_pay:.2f})", bill.id)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading data: {str(e)}")
    
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
            self.dynamic_layout.addRow("Category:", self.category_edit)
            self.dynamic_layout.addRow("", self.analytics_checkbox)
            
            self.category_edit.setVisible(True)
            self.analytics_checkbox.setVisible(True)
            self.bill_combo.setVisible(False)
            self.bill_type_edit.setVisible(False)
            self.account_combo.setVisible(False)
            self.account_name_edit.setVisible(False)
            
        elif transaction_type == "Bill Payment":
            self.dynamic_layout.addRow("Bill:", self.bill_combo)
            self.dynamic_layout.addRow("Bill Type:", self.bill_type_edit)
            
            self.category_edit.setVisible(False)
            self.analytics_checkbox.setVisible(False)
            self.bill_combo.setVisible(True)
            self.bill_type_edit.setVisible(True)
            self.account_combo.setVisible(False)
            self.account_name_edit.setVisible(False)
            
        elif transaction_type == "Saving":
            self.dynamic_layout.addRow("Account:", self.account_combo)
            self.dynamic_layout.addRow("Account Name:", self.account_name_edit)
            
            self.category_edit.setVisible(False)
            self.analytics_checkbox.setVisible(False)
            self.bill_combo.setVisible(False)
            self.bill_type_edit.setVisible(False)
            self.account_combo.setVisible(True)
            self.account_name_edit.setVisible(True)
            
        elif transaction_type == "Income":
            # Income has no special fields, just basic ones
            self.category_edit.setVisible(False)
            self.analytics_checkbox.setVisible(False)
            self.bill_combo.setVisible(False)
            self.bill_type_edit.setVisible(False)
            self.account_combo.setVisible(False)
            self.account_name_edit.setVisible(False)
    
    def validate_form(self):
        """Validate form data"""
        if self.amount_spin.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Amount must be greater than 0")
            return False
        
        if not self.description_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Description is required")
            return False
        
        transaction_type = self.type_combo.currentText()
        
        if transaction_type == "Spending" and not self.category_edit.text().strip():
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
            
            # Base transaction data
            self.transaction_data = {
                "transaction_type": self.get_transaction_type_value(transaction_type),
                "amount": self.amount_spin.value(),
                "date": self.date_edit.date().toPython(),
                "description": self.description_edit.text().strip(),
                "week_number": self.week_combo.currentData()
            }
            
            # Add type-specific fields
            if transaction_type == "Spending":
                self.transaction_data.update({
                    "category": self.category_edit.text().strip(),
                    "include_in_analytics": self.analytics_checkbox.isChecked()
                })
                
            elif transaction_type == "Bill Payment":
                self.transaction_data.update({
                    "bill_id": self.bill_combo.currentData(),
                    "bill_type": self.bill_type_edit.text().strip()
                })
                
            elif transaction_type == "Saving":
                self.transaction_data.update({
                    "account_id": self.account_combo.currentData(),
                    "account_saved_to": self.account_combo.currentText()
                })
            
            # Save to database
            transaction = self.transaction_manager.add_transaction(self.transaction_data)
            
            QMessageBox.information(self, "Success", f"Transaction saved successfully!\n\nID: {transaction.id}")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving transaction: {str(e)}")
    
    def get_transaction_type_value(self, display_name):
        """Convert display name to database enum value"""
        mapping = {
            "Spending": TransactionType.SPENDING.value,
            "Bill Payment": TransactionType.BILL_PAY.value,
            "Saving": TransactionType.SAVING.value,
            "Income": TransactionType.INCOME.value
        }
        return mapping.get(display_name, TransactionType.SPENDING.value)