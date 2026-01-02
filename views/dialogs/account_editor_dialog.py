"""
Account Editor Dialog - Admin controls for editing all savings account fields
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QDoubleSpinBox, QCheckBox, QPushButton,
                             QFormLayout, QMessageBox, QFrame, QGroupBox)
from PyQt6.QtCore import pyqtSignal
from themes import theme_manager


class AccountEditorDialog(QDialog):
    """Dialog for editing all account fields with admin controls"""
    
    account_updated = pyqtSignal(object)  # Signal when account is updated
    
    def __init__(self, account, transaction_manager, parent=None):
        super().__init__(parent)
        self.account = account
        self.transaction_manager = transaction_manager
        self.original_values = {}  # Store original values for change tracking
        
        self.setWindowTitle(f"Edit Account: {account.name}")
        self.setModal(True)
        self.resize(500, 400)
        
        self.init_ui()
        self.load_account_data()
        self.apply_theme()
    
    def init_ui(self):
        """Initialize the UI layout"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # Header
        header_label = QLabel("Account Editor - Admin Controls")
        header_label.setFont(theme_manager.get_font("title"))
        main_layout.addWidget(header_label)
        
        # Warning note
        warning_label = QLabel("⚠️ Admin Mode: Changes will affect account balances")
        warning_label.setStyleSheet("color: orange; font-weight: bold; padding: 8px; background-color: rgba(255, 165, 0, 0.1); border-radius: 4px;")
        main_layout.addWidget(warning_label)
        
        # Main fields section
        fields_group = QGroupBox("Account Fields")
        fields_layout = QFormLayout()
        
        # Account name
        self.name_edit = QLineEdit()
        fields_layout.addRow("Name:", self.name_edit)
        
        # Starting amount (editable)
        starting_layout = QHBoxLayout()
        self.starting_amount_spin = QDoubleSpinBox()
        self.starting_amount_spin.setRange(0, 999999.99)
        self.starting_amount_spin.setDecimals(2)
        self.starting_amount_spin.setSuffix(" $")
        starting_layout.addWidget(self.starting_amount_spin)

        starting_note = QLabel("(initial balance when account was created)")
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
        
        # Goal amount
        self.goal_amount_spin = QDoubleSpinBox()
        self.goal_amount_spin.setRange(0, 999999.99)
        self.goal_amount_spin.setDecimals(2)
        self.goal_amount_spin.setSuffix(" $")
        fields_layout.addRow("Goal Amount:", self.goal_amount_spin)
        
        # Auto-save amount
        auto_save_layout = QHBoxLayout()
        self.auto_save_amount_spin = QDoubleSpinBox()
        self.auto_save_amount_spin.setRange(0, 9999.99)
        self.auto_save_amount_spin.setDecimals(3)  # Allow for percentages like 0.30
        auto_save_layout.addWidget(self.auto_save_amount_spin)

        auto_save_note = QLabel("(per paycheck - values < 1.0 = % of income)")
        auto_save_note.setStyleSheet("color: gray; font-style: italic;")
        auto_save_layout.addWidget(auto_save_note)
        fields_layout.addRow("Auto-Save Amount:", auto_save_layout)
        
        # Default savings account checkbox
        self.is_default_save_check = QCheckBox("Set as default savings account")
        fields_layout.addRow("Default Account:", self.is_default_save_check)

        # Account ID (read-only)
        self.account_id_label = QLabel("N/A")
        self.account_id_label.setStyleSheet("font-family: monospace; color: gray;")
        fields_layout.addRow("Account ID:", self.account_id_label)

        # Created date (read-only)
        self.created_at_label = QLabel("N/A")
        self.created_at_label.setStyleSheet("color: gray;")
        fields_layout.addRow("Created:", self.created_at_label)

        # Last updated date (read-only)
        self.updated_at_label = QLabel("N/A")
        self.updated_at_label.setStyleSheet("color: gray;")
        fields_layout.addRow("Last Updated:", self.updated_at_label)

        # Activation Status (editable - user can modify activation periods)
        self.status_edit = QLineEdit()
        self.status_edit.setPlaceholderText("(start, end), (start, current) - dates as M/D/YYYY")
        fields_layout.addRow("Status:", self.status_edit)

        fields_group.setLayout(fields_layout)
        main_layout.addWidget(fields_group)
        
        # Progress info (read-only display)
        progress_group = QGroupBox("Progress Information")
        progress_layout = QFormLayout()
        
        self.progress_label = QLabel("Calculating...")
        progress_layout.addRow("Goal Progress:", self.progress_label)
        
        self.remaining_label = QLabel("Calculating...")
        progress_layout.addRow("Amount Remaining:", self.remaining_label)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_account)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addWidget(QFrame())  # Spacer
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Connect signals for real-time updates
        self.goal_amount_spin.valueChanged.connect(self.update_progress_info)
    
    def load_account_data(self):
        """Load current account data into form fields"""
        try:
            # Get current balance from AccountHistory
            current_balance = self.account.get_current_balance(self.transaction_manager.db)

            # Get starting balance from AccountHistory
            starting_balance = self.get_starting_balance()

            # Store original values
            self.original_values = {
                'name': self.account.name,
                'starting_amount': starting_balance,
                'goal_amount': getattr(self.account, 'goal_amount', 0.0),
                'auto_save_amount': getattr(self.account, 'auto_save_amount', 0.0),
                'is_default_save': getattr(self.account, 'is_default_save', False),
                'activation_periods': self.account._get_periods_list() if hasattr(self.account, '_get_periods_list') else []
            }
            # Store original status text for comparison
            self.original_status_text = self.format_activation_periods()

            # Populate form fields
            self.name_edit.setText(self.original_values['name'])
            self.starting_amount_spin.setValue(self.original_values['starting_amount'])
            self.current_balance_label.setText(f"${current_balance:.2f}")
            self.goal_amount_spin.setValue(self.original_values['goal_amount'])
            self.auto_save_amount_spin.setValue(self.original_values['auto_save_amount'])
            self.is_default_save_check.setChecked(self.original_values['is_default_save'])

            # Populate read-only fields
            self.account_id_label.setText(str(self.account.id))

            # Format timestamps
            if hasattr(self.account, 'created_at') and self.account.created_at:
                self.created_at_label.setText(self.account.created_at.strftime("%Y-%m-%d %H:%M:%S"))
            else:
                self.created_at_label.setText("Unknown")

            if hasattr(self.account, 'updated_at') and self.account.updated_at:
                self.updated_at_label.setText(self.account.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
            else:
                self.updated_at_label.setText("Unknown")

            # Load activation status
            self.status_edit.setText(self.format_activation_periods())

            # Update progress info
            self.update_progress_info()

        except Exception as e:
            print(f"Error loading account data: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Failed to load account data: {str(e)}")

    def format_activation_periods(self):
        """Format activation periods for display as [(start, end), ...]"""
        try:
            periods = self.account._get_periods_list() if hasattr(self.account, '_get_periods_list') else []

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
                continue
            else:
                current += char

        if current.strip():
            period_texts.append(current.strip())

        for period_text in period_texts:
            period_text = period_text.strip()
            if not period_text:
                continue

            if period_text.startswith('(') and period_text.endswith(')'):
                period_text = period_text[1:-1]

            parts = [p.strip() for p in period_text.split(',')]
            if len(parts) != 2:
                return False, f"Invalid period format: ({period_text}) - expected (start, end)"

            start_str, end_str = parts

            try:
                start_date = datetime.strptime(start_str, "%m/%d/%Y").date()
            except ValueError:
                try:
                    parts_date = start_str.split('/')
                    if len(parts_date) == 3:
                        start_date = datetime(int(parts_date[2]), int(parts_date[0]), int(parts_date[1])).date()
                    else:
                        return False, f"Invalid start date format: {start_str} - expected M/D/YYYY"
                except:
                    return False, f"Invalid start date format: {start_str} - expected M/D/YYYY"

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
        1. First start cannot be earlier than account creation date
        2. end >= start + 1 day (for each period)
        3. For consecutive periods: start2 >= end1 + 1 day
        4. Final end must be at most today (or None for 'current')
        5. If is_default_save, the last period must end with 'current' (cannot be deactivated)

        Returns: (valid, error_message)
        """
        from datetime import date, timedelta, datetime

        # Check if this is the default savings account
        is_default_save = getattr(self.account, 'is_default_save', False)

        # Rule 5: Default savings account must have at least one period ending with 'current'
        if is_default_save:
            if not periods:
                return False, f"Default savings account '{self.account.name}' must always be active. Change the default savings account first if you want to deactivate this one."

            last_period = periods[-1]
            if last_period.get('end') is not None:
                return False, f"Default savings account '{self.account.name}' must always be active. Change the default savings account first if you want to deactivate this one."

        if not periods:
            return True, None

        today = date.today()

        creation_date = None
        if hasattr(self.account, 'created_at') and self.account.created_at:
            if isinstance(self.account.created_at, datetime):
                creation_date = self.account.created_at.date()
            else:
                creation_date = self.account.created_at

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

            if i == 0 and creation_date and start_date < creation_date:
                return False, f"({start_date.month}/{start_date.day}/{start_date.year}, ...): Start date cannot be earlier than account creation date ({creation_date.month}/{creation_date.day}/{creation_date.year})"

            if end_date is not None:
                if end_date < start_date + timedelta(days=1):
                    return False, f"({start_date.month}/{start_date.day}/{start_date.year}, {end_date.month}/{end_date.day}/{end_date.year}): End date must be at least 1 day after start date"

                if i == len(periods) - 1 and end_date > today:
                    return False, f"({start_date.month}/{start_date.day}/{start_date.year}, {end_date.month}/{end_date.day}/{end_date.year}): End date cannot be in the future"

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
            account_history = history_manager.get_account_history(self.account.id, "savings")

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
            account_history = history_manager.get_account_history(self.account.id, "savings")

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
                    account_id=self.account.id,
                    account_type="savings",
                    starting_balance=new_starting_amount,
                    date=starting_date
                )
                self.transaction_manager.db.add(starting_entry)
                print(f"Created new starting balance: ${new_starting_amount:.2f}")

            # Recalculate all running totals for this account
            history_manager.recalculate_account_history(self.account.id, "savings")

        except Exception as e:
            print(f"Error updating starting balance: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def update_progress_info(self):
        """Update the progress information display"""
        try:
            # Get current balance from AccountHistory
            current_balance = self.account.get_current_balance(self.transaction_manager.db)
            goal_amount = self.goal_amount_spin.value()

            if goal_amount > 0:
                progress_percent = min(100, (current_balance / goal_amount) * 100)
                remaining_amount = max(0, goal_amount - current_balance)

                self.progress_label.setText(f"{progress_percent:.1f}%")

                if remaining_amount > 0:
                    self.remaining_label.setText(f"${remaining_amount:.2f}")
                else:
                    self.remaining_label.setText("Goal achieved!")
            else:
                self.progress_label.setText("No goal set")
                self.remaining_label.setText("N/A")

        except Exception as e:
            print(f"Error updating progress info: {e}")
            self.progress_label.setText("Error")
            self.remaining_label.setText("Error")
    
    def save_account(self):
        """Save changes to the account"""
        try:
            from views.dialogs.settings_dialog import get_setting

            # Validate inputs
            name = self.name_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "Validation Error", "Account name cannot be empty.")
                return

            # Check for duplicate names (if name changed)
            if name != self.original_values['name']:
                existing_account = self.transaction_manager.get_all_accounts()
                existing_names = [acc.name for acc in existing_account if acc.id != self.account.id]
                if name in existing_names:
                    QMessageBox.warning(self, "Validation Error", "An account with this name already exists.")
                    return

            # Check if activation periods were edited
            current_status_text = self.status_edit.text().strip()
            status_changed = current_status_text != self.original_status_text
            new_activation_periods = None

            if status_changed:
                # Parse the new activation periods
                parse_success, parse_result = self.parse_activation_periods(current_status_text)

                if not parse_success:
                    QMessageBox.warning(self, "Invalid Activation Periods", parse_result)
                    return

                new_activation_periods = parse_result

                # Validate the parsed periods
                valid, error_msg = self.validate_activation_periods(new_activation_periods)

                if not valid:
                    QMessageBox.warning(self, "Invalid Activation Periods", error_msg)
                    return

            # Get all current values (no more running_total editing)
            current_values = {
                'name': name,
                'starting_amount': self.starting_amount_spin.value(),
                'goal_amount': self.goal_amount_spin.value(),
                'auto_save_amount': self.auto_save_amount_spin.value(),
                'is_default_save': self.is_default_save_check.isChecked()
            }

            # Check if anything changed
            changes_made = False
            change_summary = []

            for key, new_value in current_values.items():
                old_value = self.original_values[key]
                if new_value != old_value:
                    changes_made = True
                    if key == 'goal_amount':
                        change_summary.append(f"Goal: ${old_value:.2f} → ${new_value:.2f}")
                    elif key == 'auto_save_amount':
                        # Handle percentage vs dollar display for auto_save_amount
                        if new_value < 1.0 and new_value > 0:
                            change_summary.append(f"Auto-save: {old_value * 100:.1f}% → {new_value * 100:.1f}%")
                        else:
                            change_summary.append(f"Auto-save: ${old_value:.2f} → ${new_value:.2f}")
                    elif key == 'starting_amount':
                        change_summary.append(f"Starting amount: ${old_value:.2f} → ${new_value:.2f}")
                    else:
                        change_summary.append(f"{key.replace('_', ' ').title()}: {old_value} → {new_value}")

            # Add activation periods change to summary
            if status_changed:
                changes_made = True
                change_summary.append(f"Activation periods: {self.original_status_text} → {current_status_text}")

            if not changes_made:
                QMessageBox.information(self, "No Changes", "No changes were made to the account.")
                self.reject()
                return

            # Confirm changes
            change_text = "\n".join(change_summary)
            reply = QMessageBox.question(
                self, "Confirm Changes",
                f"Are you sure you want to make these changes?\n\n{change_text}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Apply changes to account object
            self.account.name = current_values['name']
            self.account.goal_amount = current_values['goal_amount']
            self.account.auto_save_amount = current_values['auto_save_amount']

            # Handle starting amount change
            if current_values['starting_amount'] != self.original_values['starting_amount']:
                self.update_starting_balance(current_values['starting_amount'])

            # Handle default savings account flag
            if current_values['is_default_save'] and not self.original_values['is_default_save']:
                # Setting as default - remove default from all others
                self.transaction_manager.set_default_savings_account(self.account.id)
            elif not current_values['is_default_save'] and self.original_values['is_default_save']:
                # Trying to remove default flag - check if there are other accounts
                all_accounts = self.transaction_manager.get_all_accounts()
                other_accounts = [acc for acc in all_accounts if acc.id != self.account.id]

                if not other_accounts:
                    # This is the only account - cannot remove default flag
                    QMessageBox.warning(self, "Cannot Remove Default",
                                      "Cannot remove default savings account flag. At least one account must be the default.")
                    return
                else:
                    # Ask user to choose a new default account
                    from PyQt6.QtWidgets import QInputDialog
                    account_names = [acc.name for acc in other_accounts]
                    choice, ok = QInputDialog.getItem(self, "Choose New Default Account",
                                                    "Please choose a new default savings account:",
                                                    account_names, 0, False)
                    if not ok:
                        # User cancelled - don't make changes
                        return

                    # Find the chosen account and set it as default
                    chosen_account = next(acc for acc in other_accounts if acc.name == choice)
                    self.transaction_manager.set_default_savings_account(chosen_account.id)

            # Handle activation periods change
            if status_changed and new_activation_periods is not None:
                self.account.activation_periods = new_activation_periods

            # Save to database
            self.transaction_manager.db.commit()

            # Emit signal and close
            self.account_updated.emit(self.account)

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
                    f"• Account: {self.account.name}",
                    f"• Periods: {new_activation_periods}",
                    f"• Is Currently Active: {self.account.is_currently_active}",
                ]
                QMessageBox.information(self, "Success - Testing Mode", "\n".join(details))
            else:
                QMessageBox.information(self, "Success", "Account updated successfully!")

            self.accept()

        except Exception as e:
            print(f"Error saving account: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to save account: {str(e)}")
    
    def apply_theme(self):
        """Apply current theme to dialog"""
        try:
            colors = theme_manager.get_colors()
            
            # Comprehensive dialog styling
            self.setStyleSheet(f"""
                QDialog {{
                    background-color: {colors['background']};
                    color: {colors['text_primary']};
                }}
                
                QLabel {{
                    color: {colors['text_primary']};
                }}
                
                QLineEdit, QDoubleSpinBox {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 4px 8px;
                    color: {colors['text_primary']};
                }}
                
                QLineEdit:hover, QDoubleSpinBox:hover {{
                    border: 1px solid {colors['primary']};
                }}
                
                QLineEdit:focus, QDoubleSpinBox:focus {{
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
                    border-radius: 5px;
                    margin: 10px 0px;
                    padding-top: 10px;
                    color: {colors['text_primary']};
                }}
                
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }}
                QPushButton {{
                    background-color: {colors['primary']};
                    color: {colors['surface']};
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {colors['accent']};
                }}
                QPushButton:pressed {{
                    background-color: {colors['primary']};
                }}
                QLineEdit, QDoubleSpinBox {{
                    background-color: {colors['surface_variant']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 4px;
                    color: {colors['text_primary']};
                }}
            """)
            
        except Exception as e:
            print(f"Error applying theme to account editor dialog: {e}")