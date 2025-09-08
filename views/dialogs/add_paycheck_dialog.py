"""
Add Paycheck Dialog - Implements bi-weekly paycheck processing logic
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QDoubleSpinBox, QDateEdit, QPushButton, QLabel, 
                             QTextEdit, QMessageBox, QFrame)
from PyQt6.QtCore import QDate
from datetime import date, timedelta


class AddPaycheckDialog(QDialog):
    def __init__(self, paycheck_processor, transaction_manager, parent=None):
        super().__init__(parent)
        self.paycheck_processor = paycheck_processor
        self.transaction_manager = transaction_manager
        self.setWindowTitle("Add Paycheck - Bi-weekly Processing")
        self.setModal(True)
        self.resize(500, 600)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Add Bi-weekly Paycheck")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Input form
        form_layout = QFormLayout()
        
        # Paycheck amount
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(100.00, 99999.99)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setValue(1500.00)  # Default amount
        self.amount_spin.valueChanged.connect(self.calculate_preview)
        form_layout.addRow("Gross Paycheck ($):", self.amount_spin)
        
        # Paycheck date
        self.paycheck_date_edit = QDateEdit()
        self.paycheck_date_edit.setDate(QDate.currentDate())
        self.paycheck_date_edit.setCalendarPopup(True)
        form_layout.addRow("Paycheck Date:", self.paycheck_date_edit)
        
        # Week start date (with default logic)
        self.week_start_edit = QDateEdit()
        self.week_start_edit.setDate(self.calculate_week_start())
        self.week_start_edit.setCalendarPopup(True)
        form_layout.addRow("Week Start Date:", self.week_start_edit)
        
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
        self.preview_text.setMaximumHeight(200)
        preview_layout.addWidget(self.preview_text)
        
        preview_frame.setLayout(preview_layout)
        layout.addWidget(preview_frame)
        
        # Explanation section
        explanation_frame = QFrame()
        explanation_frame.setFrameStyle(QFrame.Shape.Box)
        explanation_layout = QVBoxLayout()
        
        explanation_title = QLabel("How Paycheck Processing Works")
        explanation_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        explanation_layout.addWidget(explanation_title)
        
        explanation_text = QLabel("""
1. Gross paycheck amount is entered
2. Bills are deducted (bi-weekly savings portion)
3. Automatic savings deducted (10% of gross)
4. Remaining amount is split between Week 1 and Week 2
5. All transactions and account updates are recorded
6. Bill savings are allocated for upcoming payments

IMPORTANT: This follows strict bi-weekly periods starting on
Mondays. You can adjust the start date if adding missed
paychecks or handling schedule changes.
        """)
        explanation_text.setStyleSheet("margin: 5px; padding: 5px;")
        explanation_layout.addWidget(explanation_text)
        
        explanation_frame.setLayout(explanation_layout)
        layout.addWidget(explanation_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.process_button = QPushButton("Process Paycheck")
        self.process_button.clicked.connect(self.process_paycheck)
        self.process_button.setStyleSheet("font-weight: bold;")
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.process_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Initial preview calculation
        self.calculate_preview()
    
    def calculate_week_start(self):
        """Calculate default week start date (Monday of current week for bi-weekly periods)"""
        today = date.today()
        days_since_monday = today.weekday()  # 0=Monday, 6=Sunday
        monday = today - timedelta(days=days_since_monday)
        return QDate.fromString(monday.isoformat(), "yyyy-MM-dd")
    
    def calculate_preview(self):
        """Calculate and display preview of paycheck processing"""
        try:
            paycheck_amount = self.amount_spin.value()
            
            # Calculate bills deduction
            bills_deducted = self.paycheck_processor.calculate_bills_deduction()
            
            # Calculate automatic savings (10%)
            automatic_savings = self.paycheck_processor.calculate_automatic_savings(paycheck_amount)
            
            # Calculate remaining and split
            remaining_for_weeks = paycheck_amount - bills_deducted - automatic_savings
            week1_allocation = remaining_for_weeks / 2
            week2_allocation = remaining_for_weeks / 2
            
            # Format preview text
            preview = f"""
PAYCHECK PROCESSING BREAKDOWN:

Gross Paycheck: ${paycheck_amount:.2f}

DEDUCTIONS:
  Bills (bi-weekly): ${bills_deducted:.2f}
  Automatic Savings (10%): ${automatic_savings:.2f}
  Total Deductions: ${bills_deducted + automatic_savings:.2f}

WEEKLY ALLOCATIONS:
  Remaining for weeks: ${remaining_for_weeks:.2f}
  Week 1 allocation: ${week1_allocation:.2f}
  Week 2 allocation: ${week2_allocation:.2f}

TRANSACTIONS TO BE CREATED:
  • Income transaction: ${paycheck_amount:.2f}
  • Automatic savings: ${automatic_savings:.2f}
  • Bill savings allocations: ${bills_deducted:.2f}
  • Account balance updates

NET EFFECT:
  Take-home for spending: ${remaining_for_weeks:.2f}
  Split across 2 weeks: ${week1_allocation:.2f} each
            """.strip()
            
            self.preview_text.setPlainText(preview)
            
        except Exception as e:
            self.preview_text.setPlainText(f"Error calculating preview: {str(e)}")
    
    def validate_form(self):
        """Validate form data"""
        if self.amount_spin.value() <= 100:
            QMessageBox.warning(self, "Validation Error", "Paycheck amount must be at least $100")
            return False
        
        paycheck_date = self.paycheck_date_edit.date().toPython()
        week_start = self.week_start_edit.date().toPython()
        
        if paycheck_date > date.today() + timedelta(days=7):
            QMessageBox.warning(self, "Validation Error", "Paycheck date cannot be more than 1 week in the future")
            return False
        
        if week_start > paycheck_date:
            QMessageBox.warning(self, "Validation Error", "Week start date cannot be after paycheck date")
            return False
        
        return True
    
    def process_paycheck(self):
        """Process the paycheck using the paycheck processor"""
        if not self.validate_form():
            return
        
        try:
            paycheck_amount = self.amount_spin.value()
            paycheck_date = self.paycheck_date_edit.date().toPython()
            week_start = self.week_start_edit.date().toPython()
            
            # Show confirmation dialog
            response = QMessageBox.question(
                self, 
                "Confirm Paycheck Processing",
                f"Process paycheck of ${paycheck_amount:.2f} dated {paycheck_date}?\n\n"
                f"This will create multiple transactions and update account balances.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if response != QMessageBox.StandardButton.Yes:
                return
            
            # Process the paycheck
            split_result = self.paycheck_processor.process_new_paycheck(
                paycheck_amount, 
                paycheck_date
            )
            
            # Show success message with details
            success_message = f"""
Paycheck processed successfully!

SUMMARY:
• Gross Paycheck: ${split_result.gross_paycheck:.2f}
• Bills Deducted: ${split_result.bills_deducted:.2f}
• Automatic Savings: ${split_result.automatic_savings:.2f}
• Week 1 Allocation: ${split_result.week1_allocation:.2f}
• Week 2 Allocation: ${split_result.week2_allocation:.2f}

TRANSACTIONS CREATED:
• Income transaction recorded
• Automatic savings allocated
• Bill savings updated
• Account balances updated

The dashboard will refresh to show updated data.
            """.strip()
            
            QMessageBox.information(self, "Paycheck Processed", success_message)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error processing paycheck: {str(e)}")
            import traceback
            traceback.print_exc()