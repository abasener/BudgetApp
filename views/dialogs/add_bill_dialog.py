"""
Add Bill Dialog - Create new recurring bills with all configuration options
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QDoubleSpinBox, QSpinBox, QDateEdit, 
                             QPushButton, QLabel, QMessageBox, QTextEdit, QComboBox, QCheckBox)
from PyQt6.QtCore import QDate
from datetime import date, timedelta
from themes import theme_manager


class SavingsPlanDialog(QDialog):
    def __init__(self, parent, explanation_text, calculated_amount, current_amount):
        super().__init__(parent)
        self.calculated_amount = calculated_amount
        self.current_amount = current_amount
        self.setWindowTitle("Savings Plan Analysis")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        self.apply_theme()
        
        # Title
        title = QLabel("Savings Plan Analysis")
        title.setFont(theme_manager.get_font("title"))
        layout.addWidget(title)
        
        # Current vs calculated info (main content)
        # Extract the key parts from explanation_text
        lines = explanation_text.split('\n')
        payment_line = next((line for line in lines if line.startswith('Payment:')), '')
        bi_weekly_line = next((line for line in lines if line.startswith('Bi-weekly savings needed:')), '')
        planned_line = next((line for line in lines if line.startswith('Planned amount:')), '')
        
        # Find over/under saving status
        status_line = ""
        for line in lines:
            if 'Over saves by' in line or 'Under saves by' in line or 'Saving the amount expected' in line:
                status_line = line
                break
        
        comparison_text = f"""
{payment_line}
{bi_weekly_line}

{planned_line}

{status_line}

CURRENT VS RECOMMENDED:
Your current setting: ${current_amount:.2f}
Calculated recommendation: ${calculated_amount:.2f}
Difference: ${calculated_amount - current_amount:+.2f}

Note: This is an estimate. Adjust based on your actual payment schedule.
        """.strip()
        
        comparison_area = QTextEdit()
        comparison_area.setPlainText(comparison_text)
        comparison_area.setReadOnly(True)
        comparison_area.setMinimumHeight(200)
        layout.addWidget(comparison_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.reject)  # Just close dialog
        
        auto_set_button = QPushButton("Auto Set Calculated Amount")
        auto_set_button.clicked.connect(self.accept)  # Return 1 to indicate auto set
        auto_set_button.setFont(theme_manager.get_font("button_bold"))
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(auto_set_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def apply_theme(self):
        """Apply current theme to dialog"""
        colors = theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['background']};
                color: {colors['text_primary']};
            }}
            
            QLabel {{
                color: {colors['text_primary']};
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


class AddBillDialog(QDialog):
    def __init__(self, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager
        self.setWindowTitle("Add New Bill")
        self.setModal(True)
        self.resize(500, 600)
        
        self.init_ui()
        self.apply_theme()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Create New Recurring Bill")
        title.setFont(theme_manager.get_font("title"))
        layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Bill name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Rent, Car Insurance, Phone Bill")
        self.name_edit.textChanged.connect(self.update_preview)
        form_layout.addRow("Bill Name:", self.name_edit)
        
        # Bill type/category (multi-select like spending categories)
        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        self.type_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.type_combo.currentTextChanged.connect(self.update_preview)
        form_layout.addRow("Bill Type/Category:", self.type_combo)
        
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
        
        # Amount to save per bi-weekly period (dollar amount or percentage)
        self.save_amount_spin = QDoubleSpinBox()
        self.save_amount_spin.setRange(0.00, 99999.99)
        self.save_amount_spin.setDecimals(2)
        self.save_amount_spin.setValue(50.00)
        self.save_amount_spin.valueChanged.connect(self.update_preview)
        form_layout.addRow("Amount to Save (bi-weekly):", self.save_amount_spin)
        
        # Percentage savings note
        percentage_note = QLabel("Tip: Use values < 1.0 for percentage (e.g., 0.1 = 10% of income)")
        percentage_note.setFont(theme_manager.get_font("small"))
        form_layout.addRow("", percentage_note)
        
        # Check savings plan button
        self.check_plan_button = QPushButton("Check Savings Plan")
        self.check_plan_button.clicked.connect(self.check_savings_plan)
        form_layout.addRow("", self.check_plan_button)
        
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
        preview_label.setFont(theme_manager.get_font("subtitle"))
        layout.addWidget(preview_label)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        layout.addWidget(self.preview_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.create_button = QPushButton("Create Bill")
        self.create_button.clicked.connect(self.create_bill)
        self.create_button.setFont(theme_manager.get_font("button_bold"))
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Initial setup
        self.load_bill_types()
        self.update_preview()
    
    def load_bill_types(self):
        """Load existing bill types from database"""
        try:
            existing_bills = self.transaction_manager.get_all_bills()
            bill_types = set()
            for bill in existing_bills:
                if bill.bill_type:
                    bill_types.add(bill.bill_type.strip())
            
            self.type_combo.clear()
            if bill_types:
                self.type_combo.addItems(sorted(bill_types))
            else:
                # Default categories if none exist
                default_types = ["Housing", "Utilities", "Transportation", "Education", "Government", "Healthcare"]
                self.type_combo.addItems(default_types)
                
        except Exception:
            # Fallback categories
            default_types = ["Housing", "Utilities", "Transportation", "Education", "Government", "Healthcare"]
            self.type_combo.addItems(default_types)
    
    def check_savings_plan(self):
        """Check the savings plan and show detailed analysis"""
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
        current_save_amount = self.save_amount_spin.value()
        
        # Calculate over/under savings compared to planned amount
        planned_amount = payment_amount
        total_saved_over_period = bi_weekly_savings * (days_between / 14)
        difference = total_saved_over_period - planned_amount
        
        # Show explanation
        explanation = f"""
Auto-calculated savings amount:

Payment: ${payment_amount:.2f} {frequency}
Bi-weekly savings needed: ${bi_weekly_savings:.2f}

Planned amount: ${planned_amount:.2f}

"""
        
        if abs(difference) < 1:  # Within $1, consider it accurate
            explanation += "Saving the amount expected to be taken"
        elif difference > 0:
            explanation += f"Over saves by ${difference:.2f}"
        else:
            weeks_till_used = abs(difference) / bi_weekly_savings if bi_weekly_savings > 0 else 0
            explanation += f"Under saves by ${abs(difference):.2f}, {weeks_till_used:.1f} weeks till savings used"
        
        explanation += "\n\nNote: This is an estimate. Adjust the amount based on your actual payment schedule."
        
        # Show custom savings plan dialog
        plan_dialog = SavingsPlanDialog(self, explanation, bi_weekly_savings, current_save_amount)
        result = plan_dialog.exec()
        
        # If user clicked "Auto Set", update the spin box and refresh preview
        if result == 1:  # Auto Set was clicked
            self.save_amount_spin.setValue(bi_weekly_savings)
            self.update_preview()
    
    def update_preview(self):
        """Update the preview of the bill to be created"""
        name = self.name_edit.text().strip() or "[Bill Name]"
        bill_type = self.type_combo.currentText().strip() or "[Bill Type]"
        frequency = self.frequency_combo.currentText()
        amount = self.amount_spin.value()
        save_amount = self.save_amount_spin.value()
        saved_amount = self.saved_amount_spin.value()
        is_variable = self.variable_checkbox.isChecked()
        qdate = self.last_payment_edit.date()
        last_payment = date(qdate.year(), qdate.month(), qdate.day())
        notes = self.notes_edit.text().strip()
        
        # Handle percentage vs dollar amount savings
        if save_amount < 1.0 and save_amount > 0:
            # Percentage-based saving
            savings_display = f"{save_amount * 100:.1f}% of income"
            savings_type = "Percentage-based"
            # For preview, assume $1500 bi-weekly income as example
            example_dollar_amount = save_amount * 1500
            monthly_savings = example_dollar_amount * 2.17
        else:
            # Dollar amount saving
            savings_display = f"${save_amount:.2f}"
            savings_type = "Fixed amount"
            monthly_savings = save_amount * 2.17
        
        preview_text = f"""
BILL PREVIEW:

Name: {name}
Type: {bill_type}
Payment Frequency: {frequency}
Typical Amount: ${amount:.2f}
Variable Amount: {"Yes" if is_variable else "No"}

SAVINGS PLAN:
Bi-weekly Savings: {savings_display} ({savings_type})
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
        bill_type = self.type_combo.currentText().strip()
        
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
        qdate = self.last_payment_edit.date()
        last_payment = date(qdate.year(), qdate.month(), qdate.day())
        
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
            bill_type = self.type_combo.currentText().strip()
            frequency = self.frequency_combo.currentText()
            amount = self.amount_spin.value()
            save_amount = self.save_amount_spin.value()
            saved_amount = self.saved_amount_spin.value()
            is_variable = self.variable_checkbox.isChecked()
            qdate = self.last_payment_edit.date()
            last_payment = date(qdate.year(), qdate.month(), qdate.day())
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
            if save_amount < 1.0 and save_amount > 0:
                success_text += f"Bi-weekly Savings: {save_amount * 100:.1f}% of income\n"
            else:
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
    
    def apply_theme(self):
        """Apply current theme to dialog"""
        colors = theme_manager.get_colors()
        
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
            
            QLineEdit, QDoubleSpinBox, QDateEdit, QSpinBox {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 4px 8px;
                color: {colors['text_primary']};
            }}
            
            QLineEdit:hover, QDoubleSpinBox:hover, QDateEdit:hover, QSpinBox:hover {{
                border: 1px solid {colors['primary']};
            }}
            
            QLineEdit:focus, QDoubleSpinBox:focus, QDateEdit:focus, QSpinBox:focus {{
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
            
            QPushButton:disabled {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                color: {colors['text_secondary']};
            }}
        """)