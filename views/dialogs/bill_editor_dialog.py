"""
Bill Editor Dialog - Admin controls for editing all bill fields
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QDoubleSpinBox, QComboBox, QCheckBox, QTextEdit, QPushButton,
                             QDateEdit, QFormLayout, QMessageBox, QFrame, QGroupBox)
from PyQt6.QtCore import QDate, pyqtSignal
from datetime import date, timedelta
from themes import theme_manager
from models import Transaction


class BillEditorDialog(QDialog):
    """Dialog for editing all bill fields with admin controls"""
    
    bill_updated = pyqtSignal(object)  # Signal when bill is updated
    
    def __init__(self, bill, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager
        self.original_values = {}  # Store original values for change tracking

        # Refresh bill data from database to get latest running_total
        self.bill = self.transaction_manager.get_bill_by_id(bill.id)
        if not self.bill:
            self.bill = bill  # Fallback to passed bill if refresh fails

        self.setWindowTitle(f"Edit Bill: {self.bill.name}")
        self.setModal(True)
        self.resize(600, 700)

        self.init_ui()
        self.load_bill_data()
        self.apply_theme()
    
    def init_ui(self):
        """Initialize the UI layout"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # Header
        header_label = QLabel("Bill Editor - Admin Controls")
        header_label.setFont(theme_manager.get_font("title"))
        main_layout.addWidget(header_label)
        
        # Warning note
        warning_label = QLabel("⚠️ Admin Mode: Changes will affect money balances across accounts")
        warning_label.setStyleSheet("color: orange; font-weight: bold; padding: 8px; background-color: rgba(255, 165, 0, 0.1); border-radius: 4px;")
        main_layout.addWidget(warning_label)
        
        # Main fields section
        fields_group = QGroupBox("Bill Fields")
        fields_layout = QFormLayout()
        
        # All Bill model fields
        self.name_edit = QLineEdit()
        fields_layout.addRow("Name:", self.name_edit)
        
        self.bill_type_combo = QComboBox()
        self.bill_type_combo.setEditable(True)  # Allow typing new values
        self.bill_type_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Don't auto-add to list
        # Populate with existing bill types
        self.populate_bill_types()
        fields_layout.addRow("Bill Type:", self.bill_type_combo)
        
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["weekly", "monthly", "quarterly", "semi-annual", "yearly", "other"])
        fields_layout.addRow("Payment Frequency:", self.frequency_combo)
        
        self.typical_amount_spin = QDoubleSpinBox()
        self.typical_amount_spin.setRange(0, 99999.99)
        self.typical_amount_spin.setDecimals(2)
        self.typical_amount_spin.setSuffix(" $")
        fields_layout.addRow("Typical Amount:", self.typical_amount_spin)
        
        # Amount to save with percentage note
        amount_layout = QHBoxLayout()
        self.amount_to_save_spin = QDoubleSpinBox()
        self.amount_to_save_spin.setRange(0, 99999.99)
        self.amount_to_save_spin.setDecimals(3)  # Allow for percentages like 0.30
        amount_layout.addWidget(self.amount_to_save_spin)
        
        percentage_note = QLabel("(Values < 1.0 = % of income)")
        percentage_note.setStyleSheet("color: gray; font-style: italic;")
        amount_layout.addWidget(percentage_note)
        fields_layout.addRow("Amount to Save (Bi-weekly):", amount_layout)
        
        # Starting amount (editable)
        starting_layout = QHBoxLayout()
        self.starting_amount_spin = QDoubleSpinBox()
        self.starting_amount_spin.setRange(0, 999999.99)
        self.starting_amount_spin.setDecimals(2)
        self.starting_amount_spin.setSuffix(" $")
        starting_layout.addWidget(self.starting_amount_spin)

        starting_note = QLabel("(initial balance when bill was created)")
        starting_note.setStyleSheet("color: gray; font-style: italic;")
        starting_layout.addWidget(starting_note)
        fields_layout.addRow("Starting Amount:", starting_layout)

        # Current balance (read-only, from AccountHistory)
        balance_layout = QHBoxLayout()
        self.current_balance_label = QLabel("$0.00")
        self.current_balance_label.setStyleSheet("font-weight: bold; color: #28a745;")
        balance_layout.addWidget(self.current_balance_label)

        balance_note = QLabel("(from AccountHistory - edit via transaction history)")
        balance_note.setStyleSheet("color: gray; font-style: italic;")
        balance_layout.addWidget(balance_note)
        fields_layout.addRow("Current Balance:", balance_layout)
        
        self.last_payment_date = QDateEdit()
        self.last_payment_date.setDisplayFormat("MM/dd/yyyy")
        self.last_payment_date.setCalendarPopup(True)
        fields_layout.addRow("Last Payment Date:", self.last_payment_date)
        
        self.last_payment_amount_spin = QDoubleSpinBox()
        self.last_payment_amount_spin.setRange(0, 99999.99)
        self.last_payment_amount_spin.setDecimals(2)
        self.last_payment_amount_spin.setSuffix(" $")
        fields_layout.addRow("Last Payment Amount:", self.last_payment_amount_spin)
        
        self.is_variable_checkbox = QCheckBox("Variable amount bill")
        fields_layout.addRow("Is Variable:", self.is_variable_checkbox)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(60)
        fields_layout.addRow("Notes:", self.notes_edit)

        # Activation Status (editable - user can modify activation periods)
        self.status_edit = QLineEdit()
        self.status_edit.setPlaceholderText("(start, end), (start, current) - dates as M/D/YYYY")
        fields_layout.addRow("Status:", self.status_edit)

        fields_group.setLayout(fields_layout)
        main_layout.addWidget(fields_group)
        
        # Calculator section
        calc_group = QGroupBox("Calculate Needed Amount")
        calc_layout = QVBoxLayout()
        
        calc_info = QLabel("Calculate recommended bi-weekly savings amount:")
        calc_layout.addWidget(calc_info)
        
        calc_button_layout = QHBoxLayout()
        self.calculate_button = QPushButton("Calculate Recommended Amount")
        self.calculate_button.clicked.connect(self.calculate_needed_amount)
        calc_button_layout.addWidget(self.calculate_button)
        calc_button_layout.addStretch()
        calc_layout.addLayout(calc_button_layout)
        
        calc_group.setLayout(calc_layout)
        main_layout.addWidget(calc_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        self.save_button.setStyleSheet("font-weight: bold;")
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def populate_bill_types(self):
        """Populate bill type dropdown with existing types"""
        try:
            # Get all existing bills
            bills = self.transaction_manager.get_all_bills()
            
            # Extract unique bill types
            bill_types = set()
            for bill in bills:
                if bill.bill_type:
                    bill_types.add(bill.bill_type)
            
            # Add common bill types
            common_types = ["Housing", "Transportation", "Utilities", "Education", "Healthcare", 
                           "Insurance", "Government", "Entertainment", "Food", "Personal"]
            bill_types.update(common_types)
            
            # Sort and add to combo
            sorted_types = sorted(list(bill_types))
            self.bill_type_combo.addItems(sorted_types)
            
        except Exception as e:
            print(f"Error populating bill types: {e}")
            # Add fallback common types
            self.bill_type_combo.addItems(["Housing", "Transportation", "Utilities", "Education"])
    
    def load_bill_data(self):
        """Load current bill data into the form"""
        try:
            # Get current balance from AccountHistory
            current_balance = self.bill.get_current_balance(self.transaction_manager.db)

            # Get starting balance from AccountHistory
            starting_balance = self.get_starting_balance()

            # Store original values for change tracking
            self.original_values = {
                'name': self.bill.name,
                'bill_type': self.bill.bill_type,
                'payment_frequency': self.bill.payment_frequency,
                'typical_amount': self.bill.typical_amount,
                'amount_to_save': self.bill.amount_to_save,
                'starting_amount': starting_balance,
                'last_payment_date': self.bill.last_payment_date,
                'last_payment_amount': self.bill.last_payment_amount,
                'is_variable': self.bill.is_variable,
                'notes': self.bill.notes,
                'activation_periods': self.bill._get_periods_list() if hasattr(self.bill, '_get_periods_list') else []
            }
            # Store original status text for comparison
            self.original_status_text = self.format_activation_periods()

            # Load values into form
            self.name_edit.setText(self.bill.name or "")
            self.bill_type_combo.setCurrentText(self.bill.bill_type or "")

            # Set frequency combo
            frequency = self.bill.payment_frequency or "monthly"
            index = self.frequency_combo.findText(frequency)
            if index >= 0:
                self.frequency_combo.setCurrentIndex(index)

            self.typical_amount_spin.setValue(self.bill.typical_amount or 0)
            self.amount_to_save_spin.setValue(self.bill.amount_to_save or 0)
            self.starting_amount_spin.setValue(starting_balance)
            self.current_balance_label.setText(f"${current_balance:.2f}")

            # Set date
            if self.bill.last_payment_date:
                qdate = QDate(self.bill.last_payment_date.year,
                             self.bill.last_payment_date.month,
                             self.bill.last_payment_date.day)
                self.last_payment_date.setDate(qdate)
            else:
                self.last_payment_date.setDate(QDate.currentDate())

            self.last_payment_amount_spin.setValue(self.bill.last_payment_amount or 0)
            self.is_variable_checkbox.setChecked(self.bill.is_variable or False)
            self.notes_edit.setPlainText(self.bill.notes or "")

            # Load activation status
            self.status_edit.setText(self.format_activation_periods())

        except Exception as e:
            print(f"Error loading bill data: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Failed to load bill data: {str(e)}")

    def format_activation_periods(self):
        """Format activation periods for display as [(start, end), ...]"""
        try:
            periods = self.bill._get_periods_list() if hasattr(self.bill, '_get_periods_list') else []

            if not periods:
                return "No activation history"

            formatted_periods = []
            for period in periods:
                start_str = period.get('start', 'unknown')
                end_val = period.get('end')

                # Format start date (M/D/YYYY)
                if start_str and start_str != 'unknown':
                    try:
                        from datetime import datetime
                        start_date = datetime.strptime(start_str, "%Y-%m-%d")
                        start_formatted = start_date.strftime("%-m/%-d/%Y").replace("-", "/")
                        # Windows doesn't support %-m, so fallback
                        start_formatted = f"{start_date.month}/{start_date.day}/{start_date.year}"
                    except:
                        start_formatted = start_str
                else:
                    start_formatted = "unknown"

                # Format end date (M/D/YYYY or 'current')
                if end_val is None:
                    end_formatted = "current"
                else:
                    try:
                        from datetime import datetime
                        end_date = datetime.strptime(end_val, "%Y-%m-%d")
                        end_formatted = f"{end_date.month}/{end_date.day}/{end_date.year}"
                    except:
                        end_formatted = end_val

                formatted_periods.append(f"({start_formatted}, {end_formatted})")

            return ", ".join(formatted_periods)

        except Exception as e:
            print(f"Error formatting activation periods: {e}")
            return "Error loading status"

    def parse_activation_periods(self, text):
        """Parse user-entered activation periods text back into list of dicts.

        Expected format: (M/D/YYYY, M/D/YYYY), (M/D/YYYY, current)
        Returns: (success, result) where result is either list of periods or error message
        """
        from datetime import datetime

        text = text.strip()
        if not text or text == "No activation history":
            return True, []

        periods = []

        # Split by ), ( to get individual periods
        # First remove any leading/trailing whitespace from each period
        period_texts = []
        current = ""
        paren_depth = 0

        for char in text:
            if char == '(':
                paren_depth += 1
                current += char
            elif char == ')':
                paren_depth -= 1
                current += char
                if paren_depth == 0:
                    period_texts.append(current.strip())
                    current = ""
            elif char == ',' and paren_depth == 0:
                # Skip commas between periods
                continue
            else:
                current += char

        if current.strip():
            period_texts.append(current.strip())

        for period_text in period_texts:
            period_text = period_text.strip()
            if not period_text:
                continue

            # Remove outer parentheses
            if period_text.startswith('(') and period_text.endswith(')'):
                period_text = period_text[1:-1]

            # Split by comma
            parts = [p.strip() for p in period_text.split(',')]
            if len(parts) != 2:
                return False, f"Invalid period format: ({period_text}) - expected (start, end)"

            start_str, end_str = parts

            # Parse start date
            try:
                start_date = datetime.strptime(start_str, "%m/%d/%Y").date()
            except ValueError:
                try:
                    # Try single-digit month/day format
                    parts_date = start_str.split('/')
                    if len(parts_date) == 3:
                        start_date = datetime(int(parts_date[2]), int(parts_date[0]), int(parts_date[1])).date()
                    else:
                        return False, f"Invalid start date format: {start_str} - expected M/D/YYYY"
                except:
                    return False, f"Invalid start date format: {start_str} - expected M/D/YYYY"

            # Parse end date (could be "current" or a date)
            if end_str.lower() == "current":
                end_date = None
            else:
                try:
                    end_date = datetime.strptime(end_str, "%m/%d/%Y").date()
                except ValueError:
                    try:
                        parts_date = end_str.split('/')
                        if len(parts_date) == 3:
                            end_date = datetime(int(parts_date[2]), int(parts_date[0]), int(parts_date[1])).date()
                        else:
                            return False, f"Invalid end date format: {end_str} - expected M/D/YYYY or 'current'"
                    except:
                        return False, f"Invalid end date format: {end_str} - expected M/D/YYYY or 'current'"

            periods.append({
                'start': start_date.isoformat(),
                'end': end_date.isoformat() if end_date else None
            })

        return True, periods

    def validate_activation_periods(self, periods):
        """Validate activation periods according to rules.

        Rules:
        1. First start cannot be earlier than bill creation date
        2. end >= start + 1 day (for each period)
        3. For consecutive periods: start2 >= end1 + 1 day
        4. Final end must be at most today (or None for 'current')

        Returns: (valid, error_message)
        """
        from datetime import date, timedelta, datetime

        if not periods:
            return True, None

        today = date.today()

        # Get bill creation date (use created_at if available, otherwise first activation)
        creation_date = None
        if hasattr(self.bill, 'created_at') and self.bill.created_at:
            if isinstance(self.bill.created_at, datetime):
                creation_date = self.bill.created_at.date()
            else:
                creation_date = self.bill.created_at

        # If no creation date, use the original first activation period start
        if not creation_date and self.original_values.get('activation_periods'):
            first_period = self.original_values['activation_periods'][0]
            if first_period.get('start'):
                creation_date = date.fromisoformat(first_period['start'])

        prev_end = None

        for i, period in enumerate(periods):
            start_str = period.get('start')
            end_str = period.get('end')

            if not start_str:
                return False, f"Period {i+1}: Missing start date"

            start_date = date.fromisoformat(start_str)
            end_date = date.fromisoformat(end_str) if end_str else None

            # Rule 1: First start cannot be earlier than creation date
            if i == 0 and creation_date and start_date < creation_date:
                return False, f"({start_date.month}/{start_date.day}/{start_date.year}, ...): Start date cannot be earlier than bill creation date ({creation_date.month}/{creation_date.day}/{creation_date.year})"

            # Rule 2: end >= start + 1 day
            if end_date is not None:
                if end_date < start_date + timedelta(days=1):
                    return False, f"({start_date.month}/{start_date.day}/{start_date.year}, {end_date.month}/{end_date.day}/{end_date.year}): End date must be at least 1 day after start date"

                # Rule 4: Final end must be at most today
                if i == len(periods) - 1 and end_date > today:
                    return False, f"({start_date.month}/{start_date.day}/{start_date.year}, {end_date.month}/{end_date.day}/{end_date.year}): End date cannot be in the future"

            # Rule 3: For consecutive periods, start2 >= end1 + 1 day
            if prev_end is not None:
                if start_date < prev_end + timedelta(days=1):
                    return False, f"Period {i+1} start ({start_date.month}/{start_date.day}/{start_date.year}) must be at least 1 day after previous period end ({prev_end.month}/{prev_end.day}/{prev_end.year})"

            prev_end = end_date

        return True, None

    def get_starting_balance(self):
        """Get the starting balance from AccountHistory"""
        try:
            from models.account_history import AccountHistoryManager
            history_manager = AccountHistoryManager(self.transaction_manager.db)
            account_history = history_manager.get_account_history(self.bill.id, "bill")

            # Find the starting balance entry (transaction_id is None)
            for entry in account_history:
                if entry.transaction_id is None and "Starting balance" in (entry.description or ""):
                    return entry.change_amount

            return 0.0  # No starting balance found

        except Exception as e:
            print(f"Error getting starting balance: {e}")
            return 0.0

    def update_starting_balance(self, new_starting_amount):
        """Update or create the starting balance entry in AccountHistory"""
        try:
            from models.account_history import AccountHistoryManager, AccountHistory
            from datetime import date, timedelta

            history_manager = AccountHistoryManager(self.transaction_manager.db)
            account_history = history_manager.get_account_history(self.bill.id, "bill")

            # Find the earliest transaction date to set starting balance date
            earliest_transaction_date = date.today()  # Default to today
            transaction_entries = [entry for entry in account_history if entry.transaction_id is not None]

            if transaction_entries:
                earliest_transaction_date = min(entry.transaction_date for entry in transaction_entries)

            # Set starting balance date to 1 day before earliest transaction
            starting_date = earliest_transaction_date - timedelta(days=1)

            # Find existing starting balance entry
            starting_entry = None
            for entry in account_history:
                if entry.transaction_id is None and "Starting balance" in (entry.description or ""):
                    starting_entry = entry
                    break

            if starting_entry:
                # Update existing starting balance
                old_amount = starting_entry.change_amount
                starting_entry.change_amount = new_starting_amount
                starting_entry.transaction_date = starting_date
                print(f"Updated starting balance: ${old_amount:.2f} → ${new_starting_amount:.2f}")
            else:
                # Create new starting balance entry
                starting_entry = AccountHistory.create_starting_balance_entry(
                    account_id=self.bill.id,
                    account_type="bill",
                    starting_balance=new_starting_amount,
                    date=starting_date
                )
                self.transaction_manager.db.add(starting_entry)
                print(f"Created new starting balance: ${new_starting_amount:.2f}")

            # Recalculate all running totals for this bill
            history_manager.recalculate_account_history(self.bill.id, "bill")

        except Exception as e:
            print(f"Error updating starting balance: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def calculate_needed_amount(self):
        """Calculate and suggest optimal bi-weekly savings amount"""
        try:
            payment_amount = self.typical_amount_spin.value()
            frequency = self.frequency_combo.currentText()
            
            if payment_amount <= 0:
                QMessageBox.warning(self, "Invalid Amount", "Please enter a valid typical amount first.")
                return
            
            # Convert frequency to days
            frequency_days = {
                "weekly": 7,
                "monthly": 30,
                "quarterly": 90,
                "semi-annual": 180,
                "yearly": 365,
                "other": 30  # Default to monthly
            }
            
            days_between = frequency_days.get(frequency, 30)
            
            # Calculate bi-weekly savings needed
            bi_weekly_savings = (payment_amount / days_between) * 14
            current_save_amount = self.amount_to_save_spin.value()
            
            # Show calculator dialog
            from views.dialogs.add_bill_dialog import SavingsPlanDialog
            
            explanation = f"""
Auto-calculated savings amount:

Payment: ${payment_amount:.2f} {frequency}
Bi-weekly savings needed: ${bi_weekly_savings:.2f}

Current setting: ${current_save_amount:.2f}
Recommended: ${bi_weekly_savings:.2f}
Difference: ${bi_weekly_savings - current_save_amount:+.2f}
            """.strip()
            
            calc_dialog = SavingsPlanDialog(self, explanation, bi_weekly_savings, current_save_amount)
            if calc_dialog.exec() == QDialog.DialogCode.Accepted:
                # Update the amount if user accepts
                self.amount_to_save_spin.setValue(bi_weekly_savings)
                
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"Error calculating amount: {str(e)}")
    
    def get_changes(self):
        """Get list of changed fields"""
        changes = []
        
        # Check each field for changes
        current_values = {
            'name': self.name_edit.text().strip(),
            'bill_type': self.bill_type_combo.currentText().strip(),
            'payment_frequency': self.frequency_combo.currentText(),
            'typical_amount': self.typical_amount_spin.value(),
            'amount_to_save': self.amount_to_save_spin.value(),
            'starting_amount': self.starting_amount_spin.value(),
            'last_payment_date': date(self.last_payment_date.date().year(),
                                     self.last_payment_date.date().month(),
                                     self.last_payment_date.date().day()),
            'last_payment_amount': self.last_payment_amount_spin.value(),
            'is_variable': self.is_variable_checkbox.isChecked(),
            'notes': self.notes_edit.toPlainText().strip() or None
        }
        
        for field, new_value in current_values.items():
            old_value = self.original_values[field]
            if new_value != old_value:
                if field == 'last_payment_date':
                    changes.append(f"{field}: {old_value} → {new_value}")
                elif field == 'amount_to_save':
                    # Handle percentage vs dollar display for amount_to_save
                    if new_value < 1.0 and new_value > 0:
                        changes.append(f"{field}: {old_value * 100:.1f}% → {new_value * 100:.1f}%")
                    else:
                        changes.append(f"{field}: ${old_value:.2f} → ${new_value:.2f}")
                elif field in ['typical_amount', 'starting_amount', 'last_payment_amount']:
                    changes.append(f"{field}: ${old_value:.2f} → ${new_value:.2f}")
                else:
                    changes.append(f"{field}: {old_value} → {new_value}")
        
        return changes, current_values
    
    def save_changes(self):
        """Save changes with confirmation dialog"""
        try:
            from views.dialogs.settings_dialog import get_setting

            changes, new_values = self.get_changes()

            # Check if activation periods were edited
            current_status_text = self.status_edit.text().strip()
            status_changed = current_status_text != self.original_status_text
            new_activation_periods = None

            if status_changed:
                # Parse the new activation periods
                parse_success, parse_result = self.parse_activation_periods(current_status_text)

                if not parse_success:
                    # Show error popup (always, not just in testing mode)
                    QMessageBox.warning(self, "Invalid Activation Periods", parse_result)
                    return

                new_activation_periods = parse_result

                # Validate the parsed periods
                valid, error_msg = self.validate_activation_periods(new_activation_periods)

                if not valid:
                    QMessageBox.warning(self, "Invalid Activation Periods", error_msg)
                    return

                # Add to changes list
                changes.append(f"activation_periods: {self.original_status_text} → {current_status_text}")

            if not changes:
                QMessageBox.information(self, "No Changes", "No changes were made.")
                return

            # Show confirmation dialog
            change_text = "You are about to change:\n\n" + "\n".join(changes)
            change_text += "\n\nAre you sure you want to continue?"

            reply = QMessageBox.question(self, "Confirm Changes", change_text,
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Apply changes to bill
            self.bill.name = new_values['name']
            self.bill.bill_type = new_values['bill_type']
            self.bill.payment_frequency = new_values['payment_frequency']
            self.bill.typical_amount = new_values['typical_amount']
            self.bill.amount_to_save = new_values['amount_to_save']
            self.bill.last_payment_date = new_values['last_payment_date']
            self.bill.last_payment_amount = new_values['last_payment_amount']
            self.bill.is_variable = new_values['is_variable']
            self.bill.notes = new_values['notes']

            # Handle starting amount change
            if new_values['starting_amount'] != self.original_values['starting_amount']:
                self.update_starting_balance(new_values['starting_amount'])

            # Handle activation periods change
            if status_changed and new_activation_periods is not None:
                self.bill.activation_periods = new_activation_periods

            # Save to database
            self.transaction_manager.db.commit()

            # Emit signal that bill was updated
            self.bill_updated.emit(self.bill)

            # Show testing mode details if enabled
            testing_mode = get_setting("testing_mode", False)
            if testing_mode and status_changed:
                details = [
                    "✓ Activation Periods Updated",
                    "",
                    "CHANGES:",
                    f"• Old: {self.original_status_text}",
                    f"• New: {current_status_text}",
                    "",
                    "DATABASE:",
                    f"• Bill: {self.bill.name}",
                    f"• Periods: {new_activation_periods}",
                    f"• Is Currently Active: {self.bill.is_currently_active}",
                ]
                QMessageBox.information(self, "Success - Testing Mode", "\n".join(details))
            else:
                QMessageBox.information(self, "Success", "Bill updated successfully!")

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving changes: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def apply_theme(self):
        """Apply current theme to the dialog"""
        colors = theme_manager.get_colors()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['background']};
                color: {colors['text_primary']};
            }}
            
            QLabel {{
                color: {colors['text_primary']};
            }}
            
            QLineEdit, QDoubleSpinBox, QDateEdit {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 4px 8px;
                color: {colors['text_primary']};
            }}
            
            QLineEdit:hover, QDoubleSpinBox:hover, QDateEdit:hover {{
                border: 1px solid {colors['primary']};
            }}
            
            QLineEdit:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
                border: 2px solid {colors['primary']};
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
            
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {colors['border']};
                border-radius: 4px;
                margin-top: 1ex;
                padding-top: 10px;
                color: {colors['text_primary']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {colors['primary']};
            }}
        """)