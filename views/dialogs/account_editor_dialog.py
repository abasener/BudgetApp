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
        self.auto_save_amount_spin.setDecimals(2)
        self.auto_save_amount_spin.setSuffix(" $")
        auto_save_layout.addWidget(self.auto_save_amount_spin)
        
        auto_save_note = QLabel("(per paycheck)")
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
                'is_default_save': getattr(self.account, 'is_default_save', False)
            }

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

            # Update progress info
            self.update_progress_info()

        except Exception as e:
            print(f"Error loading account data: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Failed to load account data: {str(e)}")

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
                        change_summary.append(f"Auto-save: ${old_value:.2f} → ${new_value:.2f}")
                    elif key == 'starting_amount':
                        change_summary.append(f"Starting amount: ${old_value:.2f} → ${new_value:.2f}")
                    else:
                        change_summary.append(f"{key.replace('_', ' ').title()}: {old_value} → {new_value}")

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

            # Save to database
            self.transaction_manager.db.commit()

            QMessageBox.information(self, "Success", "Account updated successfully!")

            # Emit signal and close
            self.account_updated.emit(self.account)
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