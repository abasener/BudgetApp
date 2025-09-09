"""
Add Account Dialog - Create new accounts with goal amounts
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QDoubleSpinBox, QCheckBox, QPushButton, 
                             QLabel, QMessageBox)


class AddAccountDialog(QDialog):
    def __init__(self, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager
        self.setWindowTitle("Add New Account")
        self.setModal(True)
        self.resize(400, 300)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Create New Account")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Account name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Emergency Fund, Car Savings, etc.")
        form_layout.addRow("Account Name:", self.name_edit)
        
        # Starting balance
        self.balance_spin = QDoubleSpinBox()
        self.balance_spin.setRange(0.00, 999999.99)
        self.balance_spin.setDecimals(2)
        self.balance_spin.setValue(0.00)
        form_layout.addRow("Starting Balance ($):", self.balance_spin)
        
        # Goal amount
        self.goal_spin = QDoubleSpinBox()
        self.goal_spin.setRange(0.00, 999999.99)
        self.goal_spin.setDecimals(2)
        self.goal_spin.setValue(0.00)
        form_layout.addRow("Savings Goal ($):", self.goal_spin)
        
        # Goal explanation
        goal_note = QLabel("Set to 0.00 for no specific goal")
        goal_note.setStyleSheet("color: gray; font-size: 11px;")
        form_layout.addRow("", goal_note)
        
        # Auto-save amount (happens after bills during paycheck processing)
        self.auto_save_spin = QDoubleSpinBox()
        self.auto_save_spin.setRange(0.00, 999999.99)
        self.auto_save_spin.setDecimals(2)
        self.auto_save_spin.setValue(0.00)
        form_layout.addRow("Auto-Save Amount ($):", self.auto_save_spin)
        
        # Auto-save explanation
        auto_save_note = QLabel("Amount to auto-save each paycheck (after bills, set to 0.00 to disable)")
        auto_save_note.setStyleSheet("color: gray; font-size: 11px;")
        form_layout.addRow("", auto_save_note)
        
        # Default savings checkbox
        self.default_save_checkbox = QCheckBox("Make this the default savings account")
        form_layout.addRow("", self.default_save_checkbox)
        
        # Default explanation
        default_note = QLabel("Default savings account receives automatic savings from paychecks")
        default_note.setStyleSheet("color: gray; font-size: 11px; margin-bottom: 10px;")
        form_layout.addRow("", default_note)
        
        layout.addLayout(form_layout)
        
        # Preview section
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("background: #f0f0f0; padding: 10px; border: 1px solid #ccc;")
        self.update_preview()
        layout.addWidget(self.preview_label)
        
        # Connect signals for live preview
        self.name_edit.textChanged.connect(self.update_preview)
        self.balance_spin.valueChanged.connect(self.update_preview)
        self.goal_spin.valueChanged.connect(self.update_preview)
        self.auto_save_spin.valueChanged.connect(self.update_preview)
        self.default_save_checkbox.toggled.connect(self.update_preview)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.create_button = QPushButton("Create Account")
        self.create_button.clicked.connect(self.create_account)
        self.create_button.setStyleSheet("font-weight: bold;")
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def update_preview(self):
        """Update the preview of the account to be created"""
        name = self.name_edit.text().strip() or "[Account Name]"
        balance = self.balance_spin.value()
        goal = self.goal_spin.value()
        auto_save = self.auto_save_spin.value()
        is_default = self.default_save_checkbox.isChecked()
        
        preview_text = f"Preview: {name}\n"
        preview_text += f"Starting Balance: ${balance:.2f}\n"
        
        if goal > 0:
            if balance > 0:
                progress = min(100, (balance / goal) * 100)
                preview_text += f"Savings Goal: ${goal:.2f} ({progress:.1f}% complete)\n"
                preview_text += f"Remaining: ${max(0, goal - balance):.2f}\n"
            else:
                preview_text += f"Savings Goal: ${goal:.2f}\n"
        else:
            preview_text += "No specific savings goal\n"
        
        if auto_save > 0:
            preview_text += f"Auto-Save: ${auto_save:.2f} per paycheck (after bills)\n"
        else:
            preview_text += "No automatic savings\n"
        
        if is_default:
            preview_text += "Default savings account (will receive automatic paycheck savings)"
        
        self.preview_label.setText(preview_text)
    
    def validate_form(self):
        """Validate form data"""
        name = self.name_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Account name is required")
            return False
        
        if len(name) < 2:
            QMessageBox.warning(self, "Validation Error", "Account name must be at least 2 characters")
            return False
        
        # Check for duplicate name
        try:
            existing_accounts = self.transaction_manager.get_all_accounts()
            for account in existing_accounts:
                if account.name.lower() == name.lower():
                    QMessageBox.warning(self, "Validation Error", f"An account named '{name}' already exists")
                    return False
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error checking existing accounts: {str(e)}")
            return False
        
        balance = self.balance_spin.value()
        goal = self.goal_spin.value()
        
        if balance < 0:
            QMessageBox.warning(self, "Validation Error", "Starting balance cannot be negative")
            return False
        
        if goal < 0:
            QMessageBox.warning(self, "Validation Error", "Goal amount cannot be negative")
            return False
        
        # Warn if making default savings when another exists
        if self.default_save_checkbox.isChecked():
            try:
                existing_default = self.transaction_manager.get_default_savings_account()
                if existing_default:
                    response = QMessageBox.question(
                        self,
                        "Replace Default Savings?",
                        f"'{existing_default.name}' is currently the default savings account.\n\n"
                        f"Make '{name}' the new default instead?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if response != QMessageBox.StandardButton.Yes:
                        return False
            except:
                pass  # Continue if unable to check
        
        return True
    
    def create_account(self):
        """Create the new account"""
        if not self.validate_form():
            return
        
        try:
            name = self.name_edit.text().strip()
            balance = self.balance_spin.value()
            goal = self.goal_spin.value()
            auto_save = self.auto_save_spin.value()
            is_default = self.default_save_checkbox.isChecked()
            
            # If making this default, remove default flag from existing default
            if is_default:
                try:
                    existing_default = self.transaction_manager.get_default_savings_account()
                    if existing_default:
                        # Update existing default to false
                        existing_default.is_default_save = False
                        self.transaction_manager.db.commit()
                except:
                    pass  # Continue if unable to update
            
            # Create new account directly in database
            from models import Account
            
            new_account = Account(
                name=name,
                running_total=balance,
                goal_amount=goal,
                auto_save_amount=auto_save,
                is_default_save=is_default
            )
            
            self.transaction_manager.db.add(new_account)
            self.transaction_manager.db.commit()
            self.transaction_manager.db.refresh(new_account)
            
            # Success message
            success_text = f"Account '{name}' created successfully!\n\n"
            success_text += f"Account ID: {new_account.id}\n"
            success_text += f"Starting Balance: ${balance:.2f}\n"
            
            if goal > 0:
                success_text += f"Savings Goal: ${goal:.2f}\n"
            
            if auto_save > 0:
                success_text += f"Auto-Save: ${auto_save:.2f} per paycheck\n"
            
            if is_default:
                success_text += "Set as default savings account\n"
            
            success_text += "\nThe dashboard will refresh to show the new account."
            
            QMessageBox.information(self, "Account Created", success_text)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating account: {str(e)}")
            import traceback
            traceback.print_exc()