"""
Pay Bill Dialog - Handle bill payments with tracking
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QComboBox, QDoubleSpinBox, QDateEdit, QPushButton, 
                             QLabel, QTextEdit, QMessageBox, QFrame)
from PyQt6.QtCore import QDate
from datetime import date, timedelta


class PayBillDialog(QDialog):
    def __init__(self, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager
        self.setWindowTitle("Pay Bill")
        self.setModal(True)
        self.resize(450, 500)
        
        self.selected_bill = None
        
        self.init_ui()
        self.load_bills()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Pay Bill")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Bill selection
        self.bill_combo = QComboBox()
        self.bill_combo.currentIndexChanged.connect(self.on_bill_selected)
        form_layout.addRow("Select Bill:", self.bill_combo)
        
        # Payment date
        self.payment_date_edit = QDateEdit()
        self.payment_date_edit.setDate(QDate.currentDate())
        self.payment_date_edit.setCalendarPopup(True)
        form_layout.addRow("Payment Date:", self.payment_date_edit)
        
        # Payment amount
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0.01, 99999.99)
        self.amount_spin.setDecimals(2)
        form_layout.addRow("Payment Amount ($):", self.amount_spin)
        
        # Week selection
        self.week_combo = QComboBox()
        form_layout.addRow("Week:", self.week_combo)
        
        layout.addLayout(form_layout)
        
        # Bill information section
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Shape.Box)
        info_layout = QVBoxLayout()
        
        info_title = QLabel("Bill Information")
        info_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(info_title)
        
        self.bill_info_text = QTextEdit()
        self.bill_info_text.setReadOnly(True)
        self.bill_info_text.setMaximumHeight(150)
        info_layout.addWidget(self.bill_info_text)
        
        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.pay_button = QPushButton("Pay Bill")
        self.pay_button.clicked.connect(self.pay_bill)
        self.pay_button.setStyleSheet("font-weight: bold;")
        self.pay_button.setEnabled(False)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.pay_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_bills(self):
        """Load bills from database"""
        try:
            bills = self.transaction_manager.get_all_bills()
            self.bill_combo.clear()
            
            if not bills:
                self.bill_combo.addItem("No bills found")
                self.bill_info_text.setPlainText("No bills available to pay.")
                return
            
            self.bill_combo.addItem("Select a bill...", None)
            for bill in bills:
                display_text = f"{bill.name} - ${bill.amount_to_pay:.2f}"
                if bill.next_payment_date:
                    display_text += f" (Due: {bill.next_payment_date})"
                self.bill_combo.addItem(display_text, bill.id)
            
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
                        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading bills: {str(e)}")
    
    def on_bill_selected(self):
        """Handle bill selection"""
        bill_id = self.bill_combo.currentData()
        
        if bill_id is None:
            self.selected_bill = None
            self.bill_info_text.setPlainText("Please select a bill to see details.")
            self.pay_button.setEnabled(False)
            return
        
        try:
            bill = self.transaction_manager.get_bill_by_id(bill_id)
            if not bill:
                self.bill_info_text.setPlainText("Bill not found.")
                self.pay_button.setEnabled(False)
                return
            
            self.selected_bill = bill
            
            # Set default payment amount
            self.amount_spin.setValue(bill.typical_amount)
            
            # Display bill information
            info_text = f"""
BILL DETAILS:

Name: {bill.name}
Type: {bill.bill_type}
Typical Payment: ${bill.typical_amount:.2f}
Payment Frequency: {bill.payment_frequency}
Variable Amount: {'Yes' if bill.is_variable else 'No'}

SAVINGS STATUS:
Amount Saved: ${bill.running_total:.2f}
Amount to Save (bi-weekly): ${bill.amount_to_save:.2f}

PAYMENT HISTORY:
Last Payment: {bill.last_payment_date if bill.last_payment_date else 'Never'}
Last Amount: ${bill.last_payment_amount:.2f} {f'on {bill.last_payment_date}' if bill.last_payment_date else ''}

PAYMENT PROCESS:
• This payment will be deducted from saved amount
• Payment details recorded for tracking
• Bill savings total will be reset to $0.00
• No automatic date calculations (manual system)
            """.strip()
            
            self.bill_info_text.setPlainText(info_text)
            self.pay_button.setEnabled(True)
            
        except Exception as e:
            self.bill_info_text.setPlainText(f"Error loading bill details: {str(e)}")
            self.pay_button.setEnabled(False)
    
    def validate_form(self):
        """Validate form data"""
        if not self.selected_bill:
            QMessageBox.warning(self, "Validation Error", "Please select a bill to pay")
            return False
        
        if self.amount_spin.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Payment amount must be greater than 0")
            return False
        
        payment_amount = self.amount_spin.value()
        saved_amount = self.selected_bill.running_total
        
        if payment_amount > saved_amount:
            response = QMessageBox.question(
                self,
                "Insufficient Savings",
                f"Payment amount (${payment_amount:.2f}) is greater than saved amount (${saved_amount:.2f}).\n\n"
                f"Shortfall: ${payment_amount - saved_amount:.2f}\n\n"
                f"Continue with payment anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if response != QMessageBox.StandardButton.Yes:
                return False
        
        return True
    
    def pay_bill(self):
        """Process the bill payment"""
        if not self.validate_form():
            return
        
        try:
            payment_amount = self.amount_spin.value()
            payment_date = self.payment_date_edit.date().toPython()
            week_number = self.week_combo.currentData()
            
            # Show confirmation
            response = QMessageBox.question(
                self,
                "Confirm Bill Payment",
                f"Pay {self.selected_bill.name} ${payment_amount:.2f} on {payment_date}?\n\n"
                f"This will:\n"
                f"• Create a bill payment transaction\n"
                f"• Update the bill's payment schedule\n"
                f"• Reset the bill's saved amount to $0.00",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if response != QMessageBox.StandardButton.Yes:
                return
            
            # Create bill payment transaction
            transaction_data = {
                "transaction_type": "bill_pay",
                "amount": payment_amount,
                "date": payment_date,
                "description": f"Paid {self.selected_bill.name}",
                "week_number": week_number,
                "bill_id": self.selected_bill.id,
                "bill_type": self.selected_bill.bill_type
            }
            
            transaction = self.transaction_manager.add_transaction(transaction_data)
            
            # Update bill payment tracking (manual system - no automatic dates)
            self.selected_bill.last_payment_date = payment_date
            self.selected_bill.last_payment_amount = payment_amount
            self.selected_bill.running_total = 0.0  # Reset saved amount
            self.transaction_manager.db.commit()
            
            # Show success message
            success_message = f"""
Bill payment processed successfully!

PAYMENT DETAILS:
• Bill: {self.selected_bill.name}
• Amount: ${payment_amount:.2f}
• Date: {payment_date}
• Transaction ID: {transaction.id}

BILL STATUS UPDATED:
• Last Payment: {payment_date}
• Last Amount: ${payment_amount:.2f}
• Saved Amount: Reset to $0.00

Manual System: No automatic due dates calculated.
The dashboard will refresh to show updated data.
            """.strip()
            
            QMessageBox.information(self, "Payment Processed", success_message)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error processing payment: {str(e)}")
            import traceback
            traceback.print_exc()