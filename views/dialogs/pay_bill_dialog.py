"""
Pay Bill Dialog - Handle bill payments with tracking
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QComboBox, QDoubleSpinBox, QDateEdit, QPushButton, 
                             QLabel, QTextEdit, QMessageBox, QFrame)
from PyQt6.QtCore import QDate
from datetime import date, timedelta
from themes import theme_manager

from models import Transaction


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
        self.apply_theme()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Pay Bill")
        title.setFont(theme_manager.get_font("title"))
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
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.pay_button = QPushButton("Pay Bill")
        self.pay_button.clicked.connect(self.pay_bill)
        self.pay_button.setFont(theme_manager.get_font("button"))
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
                # Use typical_amount or calculate from payment history
                default_amount = self.get_bill_default_amount(bill)
                display_text = f"{bill.name} - ${default_amount:.2f}"
                if bill.payment_frequency:
                    display_text += f" ({bill.payment_frequency})"
                self.bill_combo.addItem(display_text, bill.id)
            
                        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading bills: {str(e)}")
    
    def get_bill_default_amount(self, bill):
        """Get smart default amount for bill - typical_amount or average from payment history"""
        # If typical_amount is set and > 0, use it
        if hasattr(bill, 'typical_amount') and bill.typical_amount > 0:
            return bill.typical_amount
        
        # Otherwise, calculate average from payment history
        try:
            bill_payments = self.transaction_manager.db.query(Transaction).filter(
                Transaction.bill_id == bill.id,
                Transaction.transaction_type == "bill_pay"
            ).all()
            
            if bill_payments:
                total = sum(payment.amount for payment in bill_payments)
                average = total / len(bill_payments)
                return average
            
            # Fallback to last_payment_amount if available
            if hasattr(bill, 'last_payment_amount') and bill.last_payment_amount > 0:
                return bill.last_payment_amount
        
        except Exception:
            pass  # Ignore errors, use fallback
        
        # Final fallback
        return 100.00
    
    def on_bill_selected(self):
        """Handle bill selection"""
        bill_id = self.bill_combo.currentData()
        
        if bill_id is None:
            self.selected_bill = None
            self.pay_button.setEnabled(False)
            return
        
        try:
            bill = self.transaction_manager.get_bill_by_id(bill_id)
            if not bill:
                self.pay_button.setEnabled(False)
                return
            
            self.selected_bill = bill
            
            # Set smart default payment amount
            default_amount = self.get_bill_default_amount(bill)
            self.amount_spin.setValue(default_amount)
            
            self.pay_button.setEnabled(True)
            
        except Exception as e:
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
            payment_date = self.payment_date_edit.date().toPyDate()
            
            # Calculate week number from payment date
            week_number = self.calculate_week_from_date(payment_date)
            
            # Show confirmation
            response = QMessageBox.question(
                self,
                "Confirm Bill Payment",
                f"Pay {self.selected_bill.name} ${payment_amount:.2f} on {payment_date}?\n\n"
                f"This will:\n"
                f"• Create a bill payment transaction\n"
                f"• Update the bill's payment history\n"
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
    
    def calculate_week_from_date(self, payment_date):
        """Calculate week number from payment date"""
        try:
            # Find the week that contains this date
            weeks = self.transaction_manager.get_all_weeks()
            for week in weeks:
                if week.start_date <= payment_date <= week.end_date:
                    return week.week_number
            
            # If no week contains this date, use current week
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
            
            QPushButton:disabled {{
                background-color: {colors['surface_variant']};
                color: {colors['text_secondary']};
                border: 1px solid {colors['border']};
            }}
            
            QFrame {{
                background-color: {colors['surface_variant']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
            }}
        """)