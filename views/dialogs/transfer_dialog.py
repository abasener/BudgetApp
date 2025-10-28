"""
Transfer Money Dialog - Move funds between accounts, bills, and weeks
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QComboBox, QDoubleSpinBox, QSpinBox, QDateEdit, QPushButton,
                             QLabel, QLineEdit, QMessageBox, QFrame)
from PyQt6.QtCore import QDate
from datetime import date
from themes import theme_manager

from models import TransactionType


class TransferDialog(QDialog):
    def __init__(self, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager
        self.setWindowTitle("Transfer Money")
        self.setModal(True)
        self.resize(500, 400)

        # Track if user has manually edited notes
        self.from_notes_manual = False
        self.to_notes_manual = False

        self.init_ui()
        self.load_accounts_and_bills()
        self.apply_theme()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title = QLabel("Transfer Money")
        title.setFont(theme_manager.get_font("title"))
        title.setFixedHeight(30)
        layout.addWidget(title)

        # === FROM Section ===
        from_label = QLabel("FROM:")
        from_label.setFont(theme_manager.get_font("subtitle"))
        layout.addWidget(from_label)

        from_form = QFormLayout()
        from_form.setVerticalSpacing(8)

        # FROM dropdown with week number spinner
        from_row_layout = QHBoxLayout()
        self.from_combo = QComboBox()
        self.from_combo.currentIndexChanged.connect(self.on_from_selection_changed)
        from_row_layout.addWidget(self.from_combo, stretch=1)

        # Week number spinner (hidden by default)
        self.from_week_spin = QSpinBox()
        self.from_week_spin.setMinimum(1)
        self.from_week_spin.setMaximum(1)  # Will be updated when week is selected
        self.from_week_spin.setPrefix("Week ")
        self.from_week_spin.setVisible(False)  # Hidden initially
        from_row_layout.addWidget(self.from_week_spin)

        from_form.addRow("Account/Bill/Week:", from_row_layout)

        self.from_notes_edit = QLineEdit()
        self.from_notes_edit.setPlaceholderText("Transferring $__ to __")
        self.from_notes_edit.textEdited.connect(self.on_from_notes_edited)
        from_form.addRow("Notes:", self.from_notes_edit)

        layout.addLayout(from_form)

        # === Separator ===
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator1)

        # === SHARED Section (Amount & Date) ===
        shared_form = QFormLayout()
        shared_form.setVerticalSpacing(8)

        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0.01, 99999.99)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setValue(0.00)
        self.amount_spin.valueChanged.connect(self.update_notes)
        shared_form.addRow("Amount ($):", self.amount_spin)

        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("MM/dd/yyyy")
        self.date_edit.setCalendarPopup(True)
        shared_form.addRow("Date:", self.date_edit)

        layout.addLayout(shared_form)

        # === Separator ===
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator2)

        # === TO Section ===
        to_label = QLabel("TO:")
        to_label.setFont(theme_manager.get_font("subtitle"))
        layout.addWidget(to_label)

        to_form = QFormLayout()
        to_form.setVerticalSpacing(8)

        # TO dropdown with week number spinner
        to_row_layout = QHBoxLayout()
        self.to_combo = QComboBox()
        self.to_combo.currentIndexChanged.connect(self.on_to_selection_changed)
        to_row_layout.addWidget(self.to_combo, stretch=1)

        # Week number spinner (hidden by default)
        self.to_week_spin = QSpinBox()
        self.to_week_spin.setMinimum(1)
        self.to_week_spin.setMaximum(1)  # Will be updated when week is selected
        self.to_week_spin.setPrefix("Week ")
        self.to_week_spin.setVisible(False)  # Hidden initially
        to_row_layout.addWidget(self.to_week_spin)

        to_form.addRow("Account/Bill/Week:", to_row_layout)

        self.to_notes_edit = QLineEdit()
        self.to_notes_edit.setPlaceholderText("Transferring $__ from __")
        self.to_notes_edit.textEdited.connect(self.on_to_notes_edited)
        to_form.addRow("Notes:", self.to_notes_edit)

        layout.addLayout(to_form)

        layout.addStretch()

        # === Buttons ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        self.transfer_button = QPushButton("Create Transfer")
        self.transfer_button.clicked.connect(self.create_transfer)
        self.transfer_button.setDefault(True)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.transfer_button)
        layout.addLayout(button_layout)

        # Apply button theme
        self.apply_button_theme()

        self.setLayout(layout)

    def load_accounts_and_bills(self):
        """Populate FROM and TO dropdowns with accounts, bills, and current week"""
        self.from_combo.clear()
        self.to_combo.clear()

        # Store references to items (type, id, name)
        self.from_items = []
        self.to_items = []

        # Load savings accounts FIRST
        accounts = self.transaction_manager.get_all_accounts()
        for account in accounts:
            balance = account.get_current_balance()
            display_text = f"{account.name} (${balance:,.2f})"

            self.from_combo.addItem(display_text)
            self.from_items.append(("account", account.id, account.name))

            self.to_combo.addItem(display_text)
            self.to_items.append(("account", account.id, account.name))

        # Load bills SECOND
        bills = self.transaction_manager.get_all_bills()
        for bill in bills:
            balance = bill.get_current_balance()
            display_text = f"{bill.name} (${balance:,.2f})"

            self.from_combo.addItem(display_text)
            self.from_items.append(("bill", bill.id, bill.name))

            self.to_combo.addItem(display_text)
            self.to_items.append(("bill", bill.id, bill.name))

        # Add "Current Week" option LAST (at bottom of list)
        current_week = self.transaction_manager.get_current_week()
        if current_week:
            # Store max week number for spinner range
            self.max_week_number = current_week.week_number
            week_display = f"Current Week (Week {current_week.week_number})"

            # Add to FROM dropdown
            self.from_combo.addItem(week_display)
            self.from_items.append(("week", current_week.week_number, f"Week {current_week.week_number}"))

            # Add to TO dropdown
            self.to_combo.addItem(week_display)
            self.to_items.append(("week", current_week.week_number, f"Week {current_week.week_number}"))
        else:
            self.max_week_number = 1

    def on_from_notes_edited(self):
        """Mark that user manually edited FROM notes"""
        self.from_notes_manual = True

    def on_to_notes_edited(self):
        """Mark that user manually edited TO notes"""
        self.to_notes_manual = True

    def on_from_selection_changed(self):
        """Handle FROM dropdown selection - show/hide week spinner"""
        from_idx = self.from_combo.currentIndex()
        if from_idx < 0 or from_idx >= len(self.from_items):
            return

        from_type, from_id, from_name = self.from_items[from_idx]

        # Show/hide week spinner based on selection
        if from_type == "week":
            # Use stored max week number (paycheck week, not calendar week)
            if hasattr(self, 'max_week_number'):
                self.from_week_spin.setMaximum(self.max_week_number)
                self.from_week_spin.setValue(self.max_week_number)  # Default to current
            self.from_week_spin.setVisible(True)
        else:
            self.from_week_spin.setVisible(False)

        # Update notes
        self.update_notes()

    def on_to_selection_changed(self):
        """Handle TO dropdown selection - show/hide week spinner"""
        to_idx = self.to_combo.currentIndex()
        if to_idx < 0 or to_idx >= len(self.to_items):
            return

        to_type, to_id, to_name = self.to_items[to_idx]

        # Show/hide week spinner based on selection
        if to_type == "week":
            # Use stored max week number (paycheck week, not calendar week)
            if hasattr(self, 'max_week_number'):
                self.to_week_spin.setMaximum(self.max_week_number)
                self.to_week_spin.setValue(self.max_week_number)  # Default to current
            self.to_week_spin.setVisible(True)
        else:
            self.to_week_spin.setVisible(False)

        # Update notes
        self.update_notes()

    def update_notes(self):
        """Auto-update notes when selections or amount change"""
        amount = self.amount_spin.value()

        # Get FROM selection
        from_idx = self.from_combo.currentIndex()
        if from_idx < 0 or from_idx >= len(self.from_items):
            return
        from_type, from_id, from_name = self.from_items[from_idx]

        # If FROM is week, update name to include week number
        if from_type == "week" and self.from_week_spin.isVisible():
            from_name = f"Week {self.from_week_spin.value()}"

        # Get TO selection
        to_idx = self.to_combo.currentIndex()
        if to_idx < 0 or to_idx >= len(self.to_items):
            return
        to_type, to_id, to_name = self.to_items[to_idx]

        # If TO is week, update name to include week number
        if to_type == "week" and self.to_week_spin.isVisible():
            to_name = f"Week {self.to_week_spin.value()}"

        # Auto-update FROM notes if not manually edited
        if not self.from_notes_manual:
            self.from_notes_edit.setText(f"Transferring ${amount:.2f} to {to_name}")

        # Auto-update TO notes if not manually edited
        if not self.to_notes_manual:
            self.to_notes_edit.setText(f"Transferring ${amount:.2f} from {from_name}")

    def create_transfer(self):
        """Create the transfer transaction(s)"""
        amount = self.amount_spin.value()
        transfer_date = self.date_edit.date().toPyDate()

        # Get FROM selection
        from_idx = self.from_combo.currentIndex()
        if from_idx < 0 or from_idx >= len(self.from_items):
            QMessageBox.warning(self, "Invalid Selection", "Please select a valid FROM account/bill.")
            return
        from_type, from_id, from_name = self.from_items[from_idx]

        # If FROM is week, get the selected week number
        if from_type == "week" and self.from_week_spin.isVisible():
            from_id = self.from_week_spin.value()  # Use selected week number
            from_name = f"Week {from_id}"

        # Get TO selection
        to_idx = self.to_combo.currentIndex()
        if to_idx < 0 or to_idx >= len(self.to_items):
            QMessageBox.warning(self, "Invalid Selection", "Please select a valid TO account/bill/week.")
            return
        to_type, to_id, to_name = self.to_items[to_idx]

        # If TO is week, get the selected week number
        if to_type == "week" and self.to_week_spin.isVisible():
            to_id = self.to_week_spin.value()  # Use selected week number
            to_name = f"Week {to_id}"

        # Validate amount
        if amount <= 0:
            QMessageBox.warning(self, "Invalid Amount", "Transfer amount must be greater than zero.")
            return

        # Validate not same account/week
        if from_type == to_type and from_id == to_id:
            QMessageBox.warning(self, "Invalid Transfer",
                              "Cannot transfer from an account/week to itself.")
            return

        # Check balance and warn if insufficient
        if from_type == "account":
            from_account = self.transaction_manager.get_account_by_id(from_id)
            if from_account:
                current_balance = from_account.get_current_balance()
                if current_balance < amount:
                    deficit = amount - current_balance
                    reply = QMessageBox.warning(self, "Insufficient Balance",
                        f"You are trying to transfer ${amount:.2f} from {from_name} "
                        f"but there is only ${current_balance:.2f} in {from_name}.\n\n"
                        f"This will mean that {from_name} will have a final balance of "
                        f"-${deficit:.2f}.\n\n"
                        f"Are you sure you want to proceed?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.No:
                        return

        elif from_type == "bill":
            from_bill = self.transaction_manager.get_bill_by_id(from_id)
            if from_bill:
                current_balance = from_bill.get_current_balance()
                if current_balance < amount:
                    deficit = amount - current_balance
                    reply = QMessageBox.warning(self, "Insufficient Balance",
                        f"You are trying to transfer ${amount:.2f} from {from_name} "
                        f"but there is only ${current_balance:.2f} in {from_name}.\n\n"
                        f"This will mean that {from_name} will have a final balance of "
                        f"-${deficit:.2f}.\n\n"
                        f"Are you sure you want to proceed?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.No:
                        return

        # Get notes
        from_notes = self.from_notes_edit.text() or f"Transfer to {to_name}"
        to_notes = self.to_notes_edit.text() or f"Transfer from {from_name}"

        # Determine week_number for transactions
        # If week is involved, use the selected week number
        # Otherwise, use current week (for account-to-account transfers)
        if from_type == "week":
            week_number = from_id  # from_id is already the selected week number
        elif to_type == "week":
            week_number = to_id    # to_id is already the selected week number
        else:
            # Account-to-account transfer: use current week
            current_week = self.transaction_manager.get_current_week()
            if not current_week:
                QMessageBox.critical(self, "Error", "No current week found. Please add a paycheck first.")
                return
            week_number = current_week.week_number

        try:
            # Determine transaction pattern
            if from_type == "week" or to_type == "week":
                # SINGLE TRANSACTION (Week involved)
                self._create_week_transfer(from_type, from_id, to_type, to_id,
                                          amount, transfer_date, week_number,
                                          from_notes, to_notes)
            else:
                # TWO TRANSACTIONS (No week)
                self._create_account_transfer(from_type, from_id, to_type, to_id,
                                             amount, transfer_date, week_number,
                                             from_notes, to_notes)

            # Trigger parent refresh BEFORE showing success message (hides the processing delay)
            if self.parent():
                if hasattr(self.parent(), 'refresh_all_views'):
                    self.parent().refresh_all_views()

            # Show success message after refresh is done
            QMessageBox.information(self, "Success", f"Transfer of ${amount:.2f} completed successfully!")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create transfer: {str(e)}")

    def _create_week_transfer(self, from_type, from_id, to_type, to_id,
                             amount, transfer_date, week_number, from_notes, to_notes):
        """Create single transaction for week transfers

        Important: Week transfers create only ONE transaction on the account side.
        The note should always reference the OTHER side (the week), not the account.
        """
        if from_type == "week":
            # Week → Account/Bill (positive amount)
            # Transaction lives on the account, so use FROM_notes which says "from Week X"
            transaction = {
                "transaction_type": TransactionType.SAVING.value,
                "week_number": week_number,
                "amount": amount,  # Positive = into account
                "date": transfer_date,
                "description": from_notes,  # "Transferring $X from Week Y"
                "account_id": to_id if to_type == "account" else None,
                "bill_id": to_id if to_type == "bill" else None
            }
            self.transaction_manager.add_transaction(transaction)

        else:  # to_type == "week"
            # Account/Bill → Week (negative amount)
            # Transaction lives on the account, so use TO_notes which says "to Week X"
            transaction = {
                "transaction_type": TransactionType.SAVING.value,
                "week_number": week_number,
                "amount": -amount,  # Negative = out of account
                "date": transfer_date,
                "description": to_notes,  # "Transferring $X to Week Y"
                "account_id": from_id if from_type == "account" else None,
                "bill_id": from_id if from_type == "bill" else None
            }
            self.transaction_manager.add_transaction(transaction)

    def _create_account_transfer(self, from_type, from_id, to_type, to_id,
                                 amount, transfer_date, week_number, from_notes, to_notes):
        """Create two transactions for account-to-account transfers"""
        # Transaction 1: Withdraw from source
        transaction_from = {
            "transaction_type": TransactionType.SAVING.value,
            "week_number": week_number,
            "amount": -amount,  # Negative = out
            "date": transfer_date,
            "description": from_notes,
            "account_id": from_id if from_type == "account" else None,
            "bill_id": from_id if from_type == "bill" else None
        }
        self.transaction_manager.add_transaction(transaction_from)

        # Transaction 2: Deposit to destination
        transaction_to = {
            "transaction_type": TransactionType.SAVING.value,
            "week_number": week_number,
            "amount": amount,  # Positive = in
            "date": transfer_date,
            "description": to_notes,
            "account_id": to_id if to_type == "account" else None,
            "bill_id": to_id if to_type == "bill" else None
        }
        self.transaction_manager.add_transaction(transaction_to)

    def apply_theme(self):
        """Apply current theme to dialog"""
        colors = theme_manager.get_colors()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['surface']};
            }}
            QLabel {{
                color: {colors['text_primary']};
            }}
            QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit {{
                background-color: {colors['background']};
                color: {colors['text_primary']};
                border: 1px solid {colors['border']};
                padding: 5px;
            }}
        """)

    def apply_button_theme(self):
        """Apply theme to buttons"""
        colors = theme_manager.get_colors()

        # Transfer button (primary action)
        self.transfer_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['primary']};
                color: {colors['background']};
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {colors['accent']};
            }}
        """)

        # Cancel button (secondary action)
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['surface_variant']};
                color: {colors['text_primary']};
                border: 1px solid {colors['border']};
                padding: 8px 16px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {colors['border']};
            }}
        """)
