"""
Add Bill Dialog - Create new recurring bills with all configuration options
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QDoubleSpinBox, QSpinBox, QDateEdit, 
                             QPushButton, QLabel, QMessageBox, QTextEdit, QComboBox, QCheckBox)
from PyQt6.QtCore import QDate
from datetime import date, timedelta


class AddBillDialog(QDialog):
    def __init__(self, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager
        self.setWindowTitle("Add New Bill")
        self.setModal(True)
        self.resize(500, 600)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Create New Recurring Bill")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Bill name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Rent, Car Insurance, Phone Bill")
        self.name_edit.textChanged.connect(self.update_preview)
        form_layout.addRow("Bill Name:", self.name_edit)
        
        # Bill type/category
        self.type_edit = QLineEdit()
        self.type_edit.setPlaceholderText("e.g., Housing, Transportation, Utilities")
        self.type_edit.textChanged.connect(self.update_preview)
        form_layout.addRow("Bill Type/Category:", self.type_edit)
        
        # Payment frequency (dropdown)
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["weekly", "monthly", "quarterly", "semester", "semi-annual", "yearly", "other"])
        self.frequency_combo.setCurrentText("monthly")
        self.frequency_combo.currentTextChanged.connect(self.update_preview)
        form_layout.addRow("Payment Frequency:", self.frequency_combo)
        
        # Typical payment amount
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0.01, 99999.99)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setValue(100.00)
        self.amount_spin.valueChanged.connect(self.update_preview)
        form_layout.addRow("Typical Payment Amount ($):", self.amount_spin)
        
        # Variable amount checkbox
        self.variable_checkbox = QCheckBox("Amount varies (e.g., school, utilities)")
        self.variable_checkbox.toggled.connect(self.update_preview)
        form_layout.addRow("", self.variable_checkbox)
        
        # Amount to save per bi-weekly period
        self.save_amount_spin = QDoubleSpinBox()
        self.save_amount_spin.setRange(0.00, 99999.99)
        self.save_amount_spin.setDecimals(2)
        self.save_amount_spin.setValue(50.00)
        self.save_amount_spin.valueChanged.connect(self.update_preview)
        form_layout.addRow("Amount to Save (bi-weekly):", self.save_amount_spin)
        
        # Auto-calculate button
        self.auto_calc_button = QPushButton("Auto-Calculate Savings Amount")
        self.auto_calc_button.clicked.connect(self.auto_calculate_savings)
        form_layout.addRow("", self.auto_calc_button)
        
        # Starting saved amount
        self.saved_amount_spin = QDoubleSpinBox()
        self.saved_amount_spin.setRange(0.00, 99999.99)
        self.saved_amount_spin.setDecimals(2)
        self.saved_amount_spin.setValue(0.00)
        self.saved_amount_spin.valueChanged.connect(self.update_preview)
        form_layout.addRow("Already Saved Amount ($):", self.saved_amount_spin)
        
        # Last payment date (optional)
        self.last_payment_edit = QDateEdit()
        self.last_payment_edit.setDate(QDate.currentDate().addDays(-30))
        self.last_payment_edit.setCalendarPopup(True)
        form_layout.addRow("Last Payment Date (optional):", self.last_payment_edit)
        
        # Notes field
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("e.g., 'Varies by semester', 'Due around month-end'")
        form_layout.addRow("Notes:", self.notes_edit)
        
        layout.addLayout(form_layout)
        
        # Preview section
        preview_label = QLabel("Bill Preview:")
        preview_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(preview_label)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        layout.addWidget(self.preview_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.create_button = QPushButton("Create Bill")
        self.create_button.clicked.connect(self.create_bill)
        self.create_button.setStyleSheet("font-weight: bold;")
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Initial setup
        self.update_preview()
    
    def auto_calculate_savings(self):
        """Auto-calculate bi-weekly savings amount based on payment frequency"""
        payment_amount = self.amount_spin.value()
        frequency = self.frequency_combo.currentText()
        
        # Estimate days between payments for different frequencies
        frequency_days = {
            "weekly": 7,
            "monthly": 30,
            "quarterly": 90,
            "semester": 120,  # ~4 months
            "semi-annual": 180,
            "yearly": 365,
            "other": 30  # default to monthly
        }
        
        days_between = frequency_days.get(frequency, 30)
        
        # Calculate how much to save per bi-weekly period (14 days)
        bi_weekly_savings = (payment_amount / days_between) * 14
        
        self.save_amount_spin.setValue(bi_weekly_savings)
        
        # Show explanation
        explanation = f"""
Auto-calculated savings amount:

Payment: ${payment_amount:.2f} {frequency}
Estimated days between payments: {days_between}
Bi-weekly savings needed: ${bi_weekly_savings:.2f}

Calculation: (${payment_amount:.2f} ÷ {days_between} days) × 14 days = ${bi_weekly_savings:.2f}

Note: This is an estimate. Adjust the amount based on your actual payment schedule.
        """.strip()
        
        QMessageBox.information(self, "Auto-Calculate Savings", explanation)
    
    def update_preview(self):
        """Update the preview of the bill to be created"""
        name = self.name_edit.text().strip() or "[Bill Name]"
        bill_type = self.type_edit.text().strip() or "[Bill Type]"
        frequency = self.frequency_combo.currentText()
        amount = self.amount_spin.value()
        save_amount = self.save_amount_spin.value()
        saved_amount = self.saved_amount_spin.value()
        is_variable = self.variable_checkbox.isChecked()
        last_payment = self.last_payment_edit.date().toPython()
        notes = self.notes_edit.text().strip()
        
        # Calculate some helpful info
        monthly_savings = save_amount * 2.17  # Approximate monthly (26 bi-weekly periods / 12 months)
        
        preview_text = f"""
BILL PREVIEW:

Name: {name}
Type: {bill_type}
Payment Frequency: {frequency}
Typical Amount: ${amount:.2f}
Variable Amount: {"Yes" if is_variable else "No"}

SAVINGS PLAN:
Bi-weekly Savings: ${save_amount:.2f}
Approximate Monthly: ${monthly_savings:.2f}
Currently Saved: ${saved_amount:.2f}

PAYMENT TRACKING:
System: Manual entry only
Last Payment: {last_payment} (optional reference)
        """.strip()
        
        if notes:
            preview_text += f"\nNotes: {notes}"
        
        preview_text += "\n\nREADINESS:"
        
        if saved_amount >= amount:
            preview_text += f"\n✓ Fully funded (${saved_amount - amount:.2f} extra)"
        else:
            shortfall = amount - saved_amount
            bi_weekly_periods_needed = shortfall / save_amount if save_amount > 0 else 0
            preview_text += f"\n⚠ Need ${shortfall:.2f} more (~{bi_weekly_periods_needed:.1f} pay periods)"
        
        self.preview_text.setPlainText(preview_text)
    
    def validate_form(self):
        """Validate form data"""
        name = self.name_edit.text().strip()
        bill_type = self.type_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Bill name is required")
            return False
        
        if not bill_type:
            QMessageBox.warning(self, "Validation Error", "Bill type/category is required")
            return False
        
        if len(name) < 2:
            QMessageBox.warning(self, "Validation Error", "Bill name must be at least 2 characters")
            return False
        
        # Check for duplicate name
        try:
            existing_bills = self.transaction_manager.get_all_bills()
            for bill in existing_bills:
                if bill.name.lower() == name.lower():
                    QMessageBox.warning(self, "Validation Error", f"A bill named '{name}' already exists")
                    return False
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error checking existing bills: {str(e)}")
            return False
        
        if self.amount_spin.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Payment amount must be greater than 0")
            return False
        
        # Frequency validation is handled by combo box
        
        if self.save_amount_spin.value() < 0:
            QMessageBox.warning(self, "Validation Error", "Savings amount cannot be negative")
            return False
        
        # Validate dates
        last_payment = self.last_payment_edit.date().toPython()
        
        if last_payment > date.today():
            QMessageBox.warning(self, "Validation Error", "Last payment date cannot be in the future")
            return False
        
        return True
    
    def create_bill(self):
        """Create the new bill"""
        if not self.validate_form():
            return
        
        try:
            # Collect form data
            name = self.name_edit.text().strip()
            bill_type = self.type_edit.text().strip()
            frequency = self.frequency_combo.currentText()
            amount = self.amount_spin.value()
            save_amount = self.save_amount_spin.value()
            saved_amount = self.saved_amount_spin.value()
            is_variable = self.variable_checkbox.isChecked()
            last_payment = self.last_payment_edit.date().toPython()
            notes = self.notes_edit.text().strip()
            
            # Create new bill directly in database
            from models import Bill
            
            new_bill = Bill(
                name=name,
                bill_type=bill_type,
                payment_frequency=frequency,
                typical_amount=amount,
                amount_to_save=save_amount,
                running_total=saved_amount,
                last_payment_date=last_payment,
                last_payment_amount=0.0,  # Will be set when first payment is made
                is_variable=is_variable,
                notes=notes if notes else None
            )
            
            self.transaction_manager.db.add(new_bill)
            self.transaction_manager.db.commit()
            self.transaction_manager.db.refresh(new_bill)
            
            # Success message
            success_text = f"Bill '{name}' created successfully!\n\n"
            success_text += f"Bill ID: {new_bill.id}\n"
            success_text += f"Typical Amount: ${amount:.2f}\n"
            success_text += f"Frequency: {frequency}\n"
            success_text += f"Variable Amount: {'Yes' if is_variable else 'No'}\n"
            success_text += f"Bi-weekly Savings: ${save_amount:.2f}\n"
            
            if saved_amount > 0:
                success_text += f"Starting with ${saved_amount:.2f} already saved\n"
            
            if notes:
                success_text += f"Notes: {notes}\n"
                
            success_text += "\nRemember: All payments must be entered manually.\n"
            success_text += "The dashboard will refresh to show the new bill."
            
            QMessageBox.information(self, "Bill Created", success_text)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating bill: {str(e)}")
            import traceback
            traceback.print_exc()