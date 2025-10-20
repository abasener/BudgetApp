"""
Add Paycheck Dialog - Implements bi-weekly paycheck processing logic
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QDoubleSpinBox, QDateEdit, QPushButton, QLabel, 
                             QTextEdit, QMessageBox, QFrame)
from PyQt6.QtCore import QDate
from datetime import date, timedelta
from themes import theme_manager


class AddPaycheckDialog(QDialog):
    def __init__(self, paycheck_processor, transaction_manager, parent=None):
        super().__init__(parent)
        self.paycheck_processor = paycheck_processor
        self.transaction_manager = transaction_manager
        self.setWindowTitle("Add Paycheck - Bi-weekly Processing")
        self.setModal(True)
        self.resize(500, 600)
        
        self.init_ui()
        self.apply_theme()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Add Bi-weekly Paycheck")
        title.setFont(theme_manager.get_font("title"))
        layout.addWidget(title)
        
        # Input form
        form_layout = QFormLayout()
        
        # Paycheck amount (default to average of past paychecks)
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(100.00, 99999.99)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setValue(self.calculate_average_paycheck())
        self.amount_spin.valueChanged.connect(self.calculate_preview)
        form_layout.addRow("Gross Paycheck ($):", self.amount_spin)

        # Date Submitted (when work period ended - defaults to last Friday)
        date_submitted_label = QLabel("Date Submitted:")
        date_submitted_label.setToolTip("The date you finished work for this pay period (typically the last Friday of the period)")
        self.paycheck_date_edit = QDateEdit()
        self.paycheck_date_edit.setDate(self.calculate_last_friday())
        self.paycheck_date_edit.setDisplayFormat("MM/dd/yyyy")
        self.paycheck_date_edit.setCalendarPopup(True)
        form_layout.addRow(date_submitted_label, self.paycheck_date_edit)

        # Budget Start Date (when budget sees the money - defaults to next available date)
        budget_start_label = QLabel("Budget Start Date:")
        budget_start_label.setToolTip("The date your budget will start using this paycheck (Monday after the last budget week ends)")
        self.week_start_edit = QDateEdit()
        self.week_start_edit.setDate(self.calculate_next_budget_date())
        self.week_start_edit.setDisplayFormat("MM/dd/yyyy")
        self.week_start_edit.setCalendarPopup(True)
        form_layout.addRow(budget_start_label, self.week_start_edit)
        
        layout.addLayout(form_layout)
        
        # Preview section
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.Shape.Box)
        preview_layout = QVBoxLayout()
        
        preview_title = QLabel("Paycheck Processing Preview")
        preview_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        preview_layout.addWidget(preview_title)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(300)  # Increased height for more detail
        preview_layout.addWidget(self.preview_text)
        
        preview_frame.setLayout(preview_layout)
        layout.addWidget(preview_frame)
        
        # Buttons (right-justified with focused style for Save)
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        self.process_button = QPushButton("Save Paycheck")
        self.process_button.clicked.connect(self.process_paycheck)
        self.process_button.setDefault(True)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.process_button)
        layout.addLayout(button_layout)

        # Apply button theme
        self.apply_button_theme()
        
        self.setLayout(layout)
        
        # Initial preview calculation
        self.calculate_preview()
    
    def calculate_average_paycheck(self):
        """Calculate average paycheck amount from past paychecks, rounded to nearest $100"""
        from models import Transaction, TransactionType

        try:
            # Get all past income transactions
            paychecks = self.paycheck_processor.db.query(Transaction).filter(
                Transaction.transaction_type == TransactionType.INCOME.value
            ).all()

            if paychecks:
                # Calculate average
                avg = sum(p.amount for p in paychecks) / len(paychecks)
                # Round to nearest $100
                rounded_avg = round(avg / 100) * 100
                return rounded_avg
            else:
                # Default if no paychecks found
                return 1500.00
        except Exception:
            return 1500.00

    def calculate_next_budget_date(self):
        """Calculate next available budget start date (day after last budget week ends)"""
        try:
            # Get the latest week from the database
            from models import Week
            latest_week = self.paycheck_processor.db.query(Week).order_by(Week.end_date.desc()).first()

            if latest_week:
                # Next budget date is the day after the latest week ends
                next_date = latest_week.end_date + timedelta(days=1)
                return QDate.fromString(next_date.isoformat(), "yyyy-MM-dd")
            else:
                # No weeks exist, default to next Monday
                today = date.today()
                days_since_monday = today.weekday()  # 0=Monday, 6=Sunday
                monday = today - timedelta(days=days_since_monday)
                return QDate.fromString(monday.isoformat(), "yyyy-MM-dd")
        except Exception:
            # Fallback to current Monday if there's an error
            today = date.today()
            days_since_monday = today.weekday()
            monday = today - timedelta(days=days_since_monday)
            return QDate.fromString(monday.isoformat(), "yyyy-MM-dd")

    def calculate_last_friday(self):
        """Calculate the most recent Friday (not next Friday, but last Friday)"""
        today = date.today()
        days_since_friday = (today.weekday() - 4) % 7  # 4 = Friday, 0=Monday, 6=Sunday

        if days_since_friday == 0 and today.weekday() == 4:
            # Today is Friday
            last_friday = today
        else:
            # Go back to last Friday
            last_friday = today - timedelta(days=days_since_friday if days_since_friday > 0 else days_since_friday + 7)

        return QDate.fromString(last_friday.isoformat(), "yyyy-MM-dd")
    
    def calculate_preview(self):
        """Calculate and display preview of paycheck processing"""
        try:
            from views.dialogs.settings_dialog import get_setting

            paycheck_amount = self.amount_spin.value()
            testing_mode = get_setting("testing_mode", False)

            # Calculate bills deduction (including percentage-based)
            bills_deducted = self.paycheck_processor.calculate_bills_deduction(paycheck_amount)

            # Calculate account auto-savings (after bills) - pass paycheck amount for percentage calculations
            account_auto_savings = self.paycheck_processor.calculate_account_auto_savings(paycheck_amount)

            # Calculate remaining and split
            remaining_for_weeks = paycheck_amount - bills_deducted - account_auto_savings
            per_week_allocation = remaining_for_weeks / 2

            # Format enhanced preview text
            preview = f"""
PAYCHECK PROCESSING BREAKDOWN:

Gross Paycheck: ${paycheck_amount:.2f}

DEDUCTIONS:
  Bills (bi-weekly savings): ${bills_deducted:.2f}
  Account Auto-Savings: ${account_auto_savings:.2f}
  Total Deductions: ${bills_deducted + account_auto_savings:.2f}

WEEKLY ALLOCATIONS:
  Remaining for weeks: ${remaining_for_weeks:.2f}
  Per-Week allocation: ${per_week_allocation:.2f}

BILL SAVINGS BREAKDOWN:
  (Money set aside for upcoming bills)"""

            # Add bill breakdown details with percentage handling
            try:
                bills = self.paycheck_processor.transaction_manager.get_all_bills()
                for bill in bills:
                    if bill.amount_to_save > 0:
                        if bill.amount_to_save < 1.0:
                            # Percentage-based - show calculated amount and percentage
                            calculated_amount = bill.amount_to_save * paycheck_amount
                            preview += f"\n  • {bill.name}: ${calculated_amount:.2f} ({bill.amount_to_save*100:.0f}% of income)"
                        else:
                            # Fixed amount
                            preview += f"\n  • {bill.name}: ${bill.amount_to_save:.2f}"
            except:
                preview += "\n  • (Bill details loading...)"

            # Add account auto-savings breakdown if any exist
            try:
                accounts = self.paycheck_processor.transaction_manager.get_all_accounts()
                account_savings_list = []
                for account in accounts:
                    if hasattr(account, 'auto_save_amount') and account.auto_save_amount > 0:
                        if account.auto_save_amount < 1.0:
                            # Percentage-based
                            calculated_amount = account.auto_save_amount * paycheck_amount
                            account_savings_list.append(f"  • {account.name}: ${calculated_amount:.2f} ({account.auto_save_amount*100:.0f}% of income)")
                        else:
                            # Fixed amount
                            account_savings_list.append(f"  • {account.name}: ${account.auto_save_amount:.2f}")

                if account_savings_list:
                    preview += "\n\nACCOUNT AUTO-SAVINGS BREAKDOWN:"
                    for item in account_savings_list:
                        preview += f"\n{item}"
            except:
                pass

            preview += f"""

TRANSACTIONS TO BE CREATED:
  1. Income transaction: ${paycheck_amount:.2f}
  2. Bill savings allocations: ${bills_deducted:.2f}
  3. Account auto-savings: ${account_auto_savings:.2f}
  4. Account balance updates
  5. Week allocation tracking"""

            # Testing mode only section
            if testing_mode:
                preview += """

SYSTEM NOTES (Testing Mode):
  • Follows strict bi-weekly periods (Monday starts)
  • All transactions are recorded automatically
  • Account balances updated in real-time"""

            self.preview_text.setPlainText(preview.strip())

        except Exception as e:
            self.preview_text.setPlainText(f"Error calculating preview: {str(e)}")
    
    def validate_form(self):
        """Validate form data"""
        # Paycheck amount validation
        if self.amount_spin.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Paycheck amount must be positive")
            return False

        week_start = self.week_start_edit.date().toPyDate()

        # Budget Start Date must be on Monday
        if week_start.weekday() != 0:  # 0 = Monday
            QMessageBox.warning(
                self,
                "Validation Error",
                f"Budget Start Date must be a Monday.\n\n"
                f"Selected date ({week_start.strftime('%m/%d/%Y')}) is a {week_start.strftime('%A')}.\n\n"
                f"Please select a Monday for the budget to start."
            )
            return False

        # Check for overlapping pay periods - this is now an ERROR, not a question
        existing_weeks = self.paycheck_processor.transaction_manager.get_all_weeks()
        week1_end = week_start + timedelta(days=6)
        week2_start = week_start + timedelta(days=7)
        week2_end = week2_start + timedelta(days=6)

        for existing_week in existing_weeks:
            # Check if new week 1 overlaps with existing weeks
            if (week_start <= existing_week.end_date and week1_end >= existing_week.start_date):
                QMessageBox.critical(
                    self,
                    "Overlapping Budget Period",
                    f"New paycheck overlaps with existing Week {existing_week.week_number}.\n\n"
                    f"Existing week runs from {existing_week.start_date.strftime('%m/%d/%Y')} "
                    f"to {existing_week.end_date.strftime('%m/%d/%Y')}.\n\n"
                    f"Please change the Budget Start Date to avoid overlap."
                )
                return False

            # Check if new week 2 overlaps with existing weeks
            if (week2_start <= existing_week.end_date and week2_end >= existing_week.start_date):
                QMessageBox.critical(
                    self,
                    "Overlapping Budget Period",
                    f"New paycheck's second week overlaps with existing Week {existing_week.week_number}.\n\n"
                    f"Existing week runs from {existing_week.start_date.strftime('%m/%d/%Y')} "
                    f"to {existing_week.end_date.strftime('%m/%d/%Y')}.\n\n"
                    f"Please change the Budget Start Date to avoid overlap."
                )
                return False

        return True
    
    def process_paycheck(self):
        """Process the paycheck using the paycheck processor"""
        if not self.validate_form():
            return

        try:
            from views.dialogs.settings_dialog import get_setting

            paycheck_amount = self.amount_spin.value()
            paycheck_date = self.paycheck_date_edit.date().toPyDate()
            week_start = self.week_start_edit.date().toPyDate()

            # Process the paycheck
            split_result = self.paycheck_processor.process_new_paycheck(
                paycheck_amount,
                paycheck_date,
                week_start
            )

            # Check if testing mode is enabled
            testing_mode = get_setting("testing_mode", False)

            if testing_mode:
                # In testing mode, show detailed verification from database
                from models import Transaction, TransactionType, Week

                # Get the transactions that were just created
                week1 = self.paycheck_processor.transaction_manager.get_week_by_number(split_result.week_start_date.isocalendar()[1])
                income_transactions = self.paycheck_processor.db.query(Transaction).filter(
                    Transaction.transaction_type == TransactionType.INCOME.value,
                    Transaction.date == paycheck_date
                ).order_by(Transaction.id.desc()).limit(1).all()

                if income_transactions:
                    saved_income = income_transactions[0]

                    # Build verification details
                    details = [
                        "✓ Paycheck Saved Successfully",
                        "",
                        "DATABASE VERIFICATION:",
                        f"• Transaction ID: {saved_income.id}",
                        f"• Type: {saved_income.transaction_type}",
                        f"• Amount: ${saved_income.amount:.2f}",
                        f"• Date: {saved_income.date}",
                        f"• Week Number: {saved_income.week_number}",
                        f"• Description: {saved_income.description}",
                        "",
                        "SPLIT RESULT:",
                        f"• Gross Paycheck: ${split_result.gross_paycheck:.2f}",
                        f"• Bills Deducted: ${split_result.bills_deducted:.2f}",
                        f"• Automatic Savings: ${split_result.automatic_savings:.2f}",
                        f"• Account Auto-Savings: ${split_result.account_auto_savings:.2f}",
                        f"• Remaining for Weeks: ${split_result.remaining_for_weeks:.2f}",
                        f"• Week 1 Allocation: ${split_result.week1_allocation:.2f}",
                        f"• Week 2 Allocation: ${split_result.week2_allocation:.2f}",
                    ]

                    QMessageBox.information(
                        self,
                        "Success - Testing Mode",
                        "\n".join(details)
                    )
                else:
                    QMessageBox.warning(self, "Testing Mode", "Paycheck processed but could not verify in database")

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error processing paycheck: {str(e)}")
            import traceback
            traceback.print_exc()

    def get_bills_breakdown(self):
        """Get detailed breakdown of money allocated to bills"""
        bills = self.paycheck_processor.transaction_manager.get_all_bills()
        paycheck_amount = self.amount_spin.value()

        if not bills:
            return "• No bills configured"

        breakdown = []
        total_bills = 0.0

        for bill in bills:
            if bill.amount_to_save > 0:
                # Calculate amount based on percentage vs fixed
                if bill.amount_to_save < 1.0:
                    amount = bill.amount_to_save * paycheck_amount
                    breakdown.append(f"• {bill.name}: ${amount:.2f} ({bill.amount_to_save*100:.1f}% of paycheck)")
                else:
                    amount = bill.amount_to_save
                    breakdown.append(f"• {bill.name}: ${amount:.2f}")
                total_bills += amount

        if not breakdown:
            return "• No bill auto-savings configured"

        breakdown.append(f"• TOTAL BILLS: ${total_bills:.2f}")
        return "\n".join(breakdown)

    def get_savings_breakdown(self):
        """Get detailed breakdown of money allocated to savings accounts"""
        accounts = self.paycheck_processor.transaction_manager.get_all_accounts()
        paycheck_amount = self.amount_spin.value()

        if not accounts:
            return "• No savings accounts configured"

        breakdown = []
        total_savings = 0.0

        for account in accounts:
            if hasattr(account, 'auto_save_amount') and account.auto_save_amount > 0:
                # Calculate amount based on percentage vs fixed
                if account.auto_save_amount < 1.0:
                    amount = account.auto_save_amount * paycheck_amount
                    breakdown.append(f"• {account.name}: ${amount:.2f} ({account.auto_save_amount*100:.1f}% of paycheck)")
                else:
                    amount = account.auto_save_amount
                    breakdown.append(f"• {account.name}: ${amount:.2f}")
                total_savings += amount

        if not breakdown:
            return "• No account auto-savings configured"

        breakdown.append(f"• TOTAL SAVINGS: ${total_savings:.2f}")
        return "\n".join(breakdown)

    def apply_button_theme(self):
        """Apply focused styling to Save button, normal styling to Cancel"""
        colors = theme_manager.get_colors()

        # Save button - focused style (primary background with primary_dark hover)
        self.process_button.setStyleSheet(f"""
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
        
        # Main dialog styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['background']};
                color: {colors['text_primary']};
            }}
            
            QLabel {{
                color: {colors['text_primary']};
            }}
            
            QDoubleSpinBox, QDateEdit {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 4px 8px;
                color: {colors['text_primary']};
            }}
            
            QDoubleSpinBox:hover, QDateEdit:hover {{
                border: 1px solid {colors['primary']};
            }}
            
            QDoubleSpinBox:focus, QDateEdit:focus {{
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
            
            QFrame {{
                background-color: {colors['surface_variant']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
            }}
        """)