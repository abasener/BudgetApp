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
        self.preview_text.setMaximumHeight(300)  # Increased height for more detail
        preview_layout.addWidget(self.preview_text)
        
        preview_frame.setLayout(preview_layout)
        layout.addWidget(preview_frame)
        
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
            
            # Calculate bills deduction (including percentage-based)
            bills_deducted = self.paycheck_processor.calculate_bills_deduction(paycheck_amount)
            
            # Calculate automatic savings (10%)
            automatic_savings = self.paycheck_processor.calculate_automatic_savings(paycheck_amount)
            
            # Calculate account auto-savings (after bills)
            account_auto_savings = self.paycheck_processor.calculate_account_auto_savings()
            
            # Calculate remaining and split
            remaining_for_weeks = paycheck_amount - bills_deducted - automatic_savings - account_auto_savings
            week1_allocation = remaining_for_weeks / 2
            week2_allocation = remaining_for_weeks / 2
            
            # Format enhanced preview text
            preview = f"""
PAYCHECK PROCESSING BREAKDOWN:

Gross Paycheck: ${paycheck_amount:.2f}

DEDUCTIONS:
  Bills (bi-weekly savings): ${bills_deducted:.2f}
  Automatic Savings (10%): ${automatic_savings:.2f}
  Account Auto-Savings: ${account_auto_savings:.2f}
  Total Deductions: ${bills_deducted + automatic_savings + account_auto_savings:.2f}

WEEKLY ALLOCATIONS:
  Remaining for weeks: ${remaining_for_weeks:.2f}
  Week 1 allocation: ${week1_allocation:.2f}
  Week 2 allocation: ${week2_allocation:.2f}

TRANSACTIONS TO BE CREATED:
  1. Income transaction: ${paycheck_amount:.2f}
  2. Automatic savings transfer: ${automatic_savings:.2f}
  3. Bill savings allocations: ${bills_deducted:.2f}
  4. Account auto-savings: ${account_auto_savings:.2f}
  5. Account balance updates
  6. Week allocation tracking

BILL SAVINGS BREAKDOWN:
  (Money set aside for upcoming bills)"""
            
            # Add bill breakdown details
            try:
                bills = self.paycheck_processor.transaction_manager.get_all_bills()
                for bill in bills[:5]:  # Show first 5 bills
                    if bill.amount_to_save > 0:
                        preview += f"\n  • {bill.name}: ${bill.amount_to_save:.2f}"
            except:
                preview += "\n  • (Bill details loading...)"
            
            preview += f"""

NET EFFECT:
  Take-home for spending: ${remaining_for_weeks:.2f}
  Split across 2 weeks: ${week1_allocation:.2f} each
  
SYSTEM NOTES:
  • Follows strict bi-weekly periods (Monday starts)
  • All transactions recorded automatically
  • Account balances updated in real-time
            """.strip()
            
            self.preview_text.setPlainText(preview)
            
        except Exception as e:
            self.preview_text.setPlainText(f"Error calculating preview: {str(e)}")
    
    def validate_form(self):
        """Validate form data"""
        if self.amount_spin.value() <= 100:
            QMessageBox.warning(self, "Validation Error", "Paycheck amount must be at least $100")
            return False
        
        paycheck_date = self.paycheck_date_edit.date().toPyDate()
        week_start = self.week_start_edit.date().toPyDate()
        
        if paycheck_date > date.today() + timedelta(days=7):
            QMessageBox.warning(self, "Validation Error", "Paycheck date cannot be more than 1 week in the future")
            return False
        
        if week_start > paycheck_date:
            QMessageBox.warning(self, "Validation Error", "Week start date cannot be after paycheck date")
            return False

        # Check for overlapping pay periods
        existing_weeks = self.paycheck_processor.transaction_manager.get_all_weeks()
        week2_start = week_start + timedelta(days=7)

        for existing_week in existing_weeks:
            # Check if new week 1 overlaps with existing weeks
            if (week_start <= existing_week.end_date and
                week_start + timedelta(days=6) >= existing_week.start_date):
                response = QMessageBox.question(
                    self, "Overlapping Pay Period Detected",
                    f"The new pay period (Week starting {week_start.strftime('%m/%d/%Y')}) "
                    f"overlaps with existing Week {existing_week.week_number} "
                    f"({existing_week.start_date.strftime('%m/%d/%Y')} - {existing_week.end_date.strftime('%m/%d/%Y')}).\n\n"
                    "This might indicate duplicate paycheck entries or incorrect dates.\n\n"
                    "Are you sure you want to continue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if response != QMessageBox.StandardButton.Yes:
                    return False
                break

            # Check if new week 2 overlaps with existing weeks
            if (week2_start <= existing_week.end_date and
                week2_start + timedelta(days=6) >= existing_week.start_date):
                response = QMessageBox.question(
                    self, "Overlapping Pay Period Detected",
                    f"The new pay period (Week 2 starting {week2_start.strftime('%m/%d/%Y')}) "
                    f"overlaps with existing Week {existing_week.week_number} "
                    f"({existing_week.start_date.strftime('%m/%d/%Y')} - {existing_week.end_date.strftime('%m/%d/%Y')}).\n\n"
                    "This might indicate duplicate paycheck entries or incorrect dates.\n\n"
                    "Are you sure you want to continue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if response != QMessageBox.StandardButton.Yes:
                    return False
                break
        
        return True
    
    def process_paycheck(self):
        """Process the paycheck using the paycheck processor"""
        if not self.validate_form():
            return
        
        try:
            paycheck_amount = self.amount_spin.value()
            paycheck_date = self.paycheck_date_edit.date().toPyDate()
            week_start = self.week_start_edit.date().toPyDate()
            
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
            week_start = self.week_start_edit.date().toPyDate()
            split_result = self.paycheck_processor.process_new_paycheck(
                paycheck_amount,
                paycheck_date,
                week_start
            )
            
            # Show success message with details
            success_message = f"""
Paycheck processed successfully!

SUMMARY:
• Gross Paycheck: ${split_result.gross_paycheck:.2f}
• Bills Deducted: ${split_result.bills_deducted:.2f}
• Automatic Savings: ${split_result.automatic_savings:.2f}
• Account Auto-Savings: ${split_result.account_auto_savings:.2f}
• Week 1 Allocation: ${split_result.week1_allocation:.2f}
• Week 2 Allocation: ${split_result.week2_allocation:.2f}

TRANSACTIONS CREATED:
• Income transaction recorded
• Automatic savings allocated
• Bill savings updated
• Account auto-savings allocated
• Account balances updated

The dashboard will refresh to show updated data.
            """.strip()
            
            QMessageBox.information(self, "Paycheck Processed", success_message)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error processing paycheck: {str(e)}")
            import traceback
            traceback.print_exc()
    
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