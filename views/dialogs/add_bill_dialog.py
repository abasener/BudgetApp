"""
Add Bill Dialog - Create new recurring bills with all configuration options
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QDoubleSpinBox, QSpinBox, QDateEdit,
                             QPushButton, QLabel, QMessageBox, QTextEdit, QComboBox, QCheckBox, QWidget)
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

        # Reverse the difference sign (negative = not saving enough)
        difference = current_amount - calculated_amount

        comparison_text = f"""
{payment_line}

CURRENT VS RECOMMENDED:
Current: ${current_amount:.2f}
Recommendation: ${calculated_amount:.2f}
Saving difference: ${difference:+.2f}

Note: This is an estimate. Adjust based on your actual payment schedule.
        """.strip()
        
        comparison_area = QTextEdit()
        comparison_area.setPlainText(comparison_text)
        comparison_area.setReadOnly(True)
        comparison_area.setMinimumHeight(200)
        layout.addWidget(comparison_area)
        
        # Buttons (right-justified with focused style for Proceed)
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)  # Just close dialog

        proceed_button = QPushButton("Proceed")
        proceed_button.clicked.connect(self.accept)  # Return 1 to indicate auto set
        proceed_button.setDefault(True)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(proceed_button)
        layout.addLayout(button_layout)

        # Apply button theme
        self.apply_button_theme(proceed_button, cancel_button)
        
        self.setLayout(layout)

    def apply_button_theme(self, proceed_button, cancel_button):
        """Apply focused styling to Proceed button, normal styling to Cancel"""
        colors = theme_manager.get_colors()

        # Proceed button - focused style (primary background with primary_dark hover)
        proceed_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['primary']};
                color: {colors['background']};
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: {colors['primary_dark']};
            }}

            QPushButton:pressed {{
                background-color: {colors['selected']};
            }}
        """)

        # Cancel button - normal style (will inherit from main apply_theme)
        cancel_button.setStyleSheet("")

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
        self.resize(800, 500)
        
        self.init_ui()
        self.apply_theme()
    
    def init_ui(self):
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Create New Recurring Bill")
        title.setFont(theme_manager.get_font("title"))
        main_layout.addWidget(title)

        # Horizontal layout for fields (left) and preview (right)
        content_layout = QHBoxLayout()

        # Left side: Form fields (2/3 width)
        left_widget = QWidget()
        form_layout = QFormLayout()
        left_widget.setLayout(form_layout)
        
        # Bill name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Rent, Car Insurance, Phone Bill")
        self.name_edit.textChanged.connect(self.update_preview)
        self.name_edit.textChanged.connect(self.validate_create_button)
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
        
        # Amount to save per bi-weekly period (with tooltip and calculate button)
        save_amount_label = QLabel("Amount to Save (bi-weekly):")
        save_amount_label.setToolTip("Values < 1.0 = % of income (e.g., 0.300 = 30% of paycheck)")

        # Create horizontal layout for spin box and button
        save_amount_layout = QHBoxLayout()
        self.save_amount_spin = QDoubleSpinBox()
        self.save_amount_spin.setRange(0.00, 99999.99)
        self.save_amount_spin.setDecimals(3)  # Allow for percentages like 0.300
        self.save_amount_spin.setValue(50.00)
        self.save_amount_spin.setToolTip("Values < 1.0 = % of income (e.g., 0.300 = 30% of paycheck)")
        self.save_amount_spin.valueChanged.connect(self.update_preview)

        self.check_plan_button = QPushButton("Calculate Savings")
        self.check_plan_button.clicked.connect(self.check_savings_plan)

        save_amount_layout.addWidget(self.save_amount_spin)
        save_amount_layout.addWidget(self.check_plan_button)

        form_layout.addRow(save_amount_label, save_amount_layout)

        # Starting balance (with tooltip)
        starting_label = QLabel("Starting Balance ($):")
        starting_label.setToolTip("Initial amount saved for this bill")
        self.starting_balance_spin = QDoubleSpinBox()
        self.starting_balance_spin.setRange(0.00, 99999.99)
        self.starting_balance_spin.setDecimals(2)
        self.starting_balance_spin.setValue(0.00)
        self.starting_balance_spin.setToolTip("Initial amount saved for this bill")
        self.starting_balance_spin.valueChanged.connect(self.update_preview)
        form_layout.addRow(starting_label, self.starting_balance_spin)
        
        # Last payment date (optional)
        self.last_payment_edit = QDateEdit()
        self.last_payment_edit.setDate(QDate.currentDate().addDays(-30))
        self.last_payment_edit.setCalendarPopup(True)
        form_layout.addRow("Last Payment Date (optional):", self.last_payment_edit)
        
        # Notes field
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("e.g., 'Varies by semester', 'Due around month-end'")
        form_layout.addRow("Notes:", self.notes_edit)

        # Add left widget to content layout (2/3 width)
        content_layout.addWidget(left_widget, 2)

        # Right side: Preview (1/3 width, full height)
        right_layout = QVBoxLayout()

        preview_label = QLabel("Bill Preview:")
        preview_label.setFont(theme_manager.get_font("subtitle"))
        right_layout.addWidget(preview_label)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMinimumHeight(400)
        right_layout.addWidget(self.preview_text)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # Add right widget to content layout (1/3 width)
        content_layout.addWidget(right_widget, 1)

        main_layout.addLayout(content_layout)

        # Buttons (right-justified with focused style for Create) - full width at bottom
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.create_bill)
        self.create_button.setDefault(True)
        self.create_button.setEnabled(False)  # Disabled until name is entered

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.create_button)
        main_layout.addLayout(button_layout)

        # Apply button theme
        self.apply_button_theme()

        self.setLayout(main_layout)

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
    
    def validate_create_button(self):
        """Enable/disable Create button based on whether name is entered"""
        name = self.name_edit.text().strip()
        self.create_button.setEnabled(bool(name))

    def update_preview(self):
        """Update the preview of the bill to be created"""
        name = self.name_edit.text().strip() or "[Bill Name]"
        bill_type = self.type_combo.currentText().strip() or "[Bill Type]"
        frequency = self.frequency_combo.currentText()
        amount = self.amount_spin.value()
        save_amount = self.save_amount_spin.value()
        starting_balance = self.starting_balance_spin.value()
        is_variable = self.variable_checkbox.isChecked()
        qdate = self.last_payment_edit.date()
        last_payment = date(qdate.year(), qdate.month(), qdate.day())
        notes = self.notes_edit.text().strip()
        
        # Calculate recommended bi-weekly savings based on payment frequency
        frequency_days = {
            "weekly": 7,
            "monthly": 30,
            "quarterly": 90,
            "semester": 120,
            "semi-annual": 180,
            "yearly": 365,
            "other": 30
        }
        days_between = frequency_days.get(frequency, 30)
        recommended_bi_weekly = (amount / days_between) * 14
        paychecks_per_cycle = days_between / 14

        # Determine actual bi-weekly amount (handle percentage vs fixed)
        if save_amount < 1.0 and save_amount > 0:
            # Percentage-based - estimate using $4000 paycheck
            actual_bi_weekly = save_amount * 4000
        else:
            # Fixed amount
            actual_bi_weekly = save_amount

        # Calculate difference (positive = over-saving, negative = under-saving)
        savings_difference = actual_bi_weekly - recommended_bi_weekly

        preview_text = f"""
BILL PREVIEW:

Name: {name}
Type: {bill_type}
Payment Frequency: {frequency}
Typical Amount: ${amount:.2f}
Variable Amount: {"Yes" if is_variable else "No"}

EXPECTATION:
Starting Balance: ${starting_balance:.2f}"""

        # Show shortfall if not fully funded
        if starting_balance < amount:
            shortfall = amount - starting_balance
            preview_text += f"\nNeed ${shortfall:.2f} per cycle"
            preview_text += f"\n     ~{paychecks_per_cycle:.1f} paychecks per billing cycle"

        # Savings Plan Status
        if abs(savings_difference) < 1.0:
            # Correct payment
            preview_text += f"\n\nSAVINGS PLAN: ✅\nCorrect payment: ${actual_bi_weekly:.2f} per paycheck"
        elif savings_difference < 0:
            # Under payment
            # Calculate total under per billing cycle
            under_per_cycle = abs(savings_difference) * paychecks_per_cycle
            preview_text += f"\n\nSAVINGS PLAN: ⚠️\nUnder payment: ${under_per_cycle:.2f} per billing cycle"
            preview_text += f"\n     ~${abs(savings_difference):.2f} per paycheck"
            # Calculate how many billing cycles they can afford with current savings
            cycles_affordable = starting_balance / amount if amount > 0 else 0
            preview_text += f"\nWith savings you have {cycles_affordable:.1f} billing cycles in reserve"
        else:
            # Over payment
            # Calculate total over per billing cycle
            over_per_cycle = savings_difference * paychecks_per_cycle
            preview_text += f"\n\nSAVINGS PLAN: ❕\nOver payment: ${over_per_cycle:.2f} per billing cycle"
            preview_text += f"\n     ~${savings_difference:.2f} per paycheck"
            # Calculate paychecks needed to get one billing cycle ahead
            paychecks_to_get_ahead = amount / savings_difference if savings_difference > 0 else 0
            preview_text += f"\n{paychecks_to_get_ahead:.1f} paychecks to get ahead a billing cycle"

        if notes:
            preview_text += f"\n\nNotes: {notes}"

        self.preview_text.setPlainText(preview_text.strip())
    
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
            from views.dialogs.settings_dialog import get_setting

            # Collect form data
            name = self.name_edit.text().strip()
            bill_type = self.type_combo.currentText().strip()
            frequency = self.frequency_combo.currentText()
            amount = self.amount_spin.value()
            save_amount = self.save_amount_spin.value()
            starting_balance = self.starting_balance_spin.value()
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
                running_total=0.0,  # Will be calculated from AccountHistory
                last_payment_date=last_payment,
                last_payment_amount=0.0,  # Will be set when first payment is made
                is_variable=is_variable,
                notes=notes if notes else None
            )

            self.transaction_manager.db.add(new_bill)
            self.transaction_manager.db.commit()
            self.transaction_manager.db.refresh(new_bill)

            # Create starting balance entry in AccountHistory if starting_balance > 0
            if starting_balance > 0:
                from models.account_history import AccountHistory
                from datetime import date as date_class

                starting_entry = AccountHistory.create_starting_balance_entry(
                    account_id=new_bill.id,
                    account_type="bill",
                    starting_balance=starting_balance,
                    date=date_class.today()
                )
                self.transaction_manager.db.add(starting_entry)
                self.transaction_manager.db.commit()

            # Check if testing mode is enabled
            testing_mode = get_setting("testing_mode", False)

            if testing_mode:
                # In testing mode, show detailed verification from database
                saved_bill = self.transaction_manager.db.query(Bill).filter(
                    Bill.id == new_bill.id
                ).first()

                if saved_bill:
                    # Build verification details
                    details = [
                        "✓ Bill Created Successfully",
                        "",
                        "DATABASE VERIFICATION:",
                        f"• Bill ID: {saved_bill.id}",
                        f"• Name: {saved_bill.name}",
                        f"• Type: {saved_bill.bill_type}",
                        f"• Typical Amount: ${saved_bill.typical_amount:.2f}",
                        f"• Frequency: {saved_bill.payment_frequency}",
                        f"• Variable Amount: {saved_bill.is_variable}",
                        f"• Amount to Save: {saved_bill.amount_to_save:.3f}",
                        f"• Starting Balance: ${starting_balance:.2f}",
                    ]

                    # Show amount to save with percentage if applicable
                    if saved_bill.amount_to_save < 1.0 and saved_bill.amount_to_save > 0:
                        details.append(f"• Savings Display: {saved_bill.amount_to_save * 100:.1f}% of income")
                    else:
                        details.append(f"• Savings Display: ${saved_bill.amount_to_save:.2f} bi-weekly")

                    if saved_bill.notes:
                        details.append(f"• Notes: {saved_bill.notes}")

                    QMessageBox.information(
                        self,
                        "Success - Testing Mode",
                        "\n".join(details)
                    )
                else:
                    QMessageBox.warning(self, "Testing Mode", "Bill created but could not verify in database")

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating bill: {str(e)}")
            import traceback
            traceback.print_exc()

    def apply_button_theme(self):
        """Apply focused styling to Create button, normal styling to Cancel"""
        colors = theme_manager.get_colors()

        # Create button - focused style (primary background with primary_dark hover)
        self.create_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['primary']};
                color: {colors['background']};
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: {colors['primary_dark']};
            }}

            QPushButton:pressed {{
                background-color: {colors['selected']};
            }}
        """)

        # Cancel button - normal style (will inherit from main apply_theme)
        self.cancel_button.setStyleSheet("")
    
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