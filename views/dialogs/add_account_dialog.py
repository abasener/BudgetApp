"""
Add Account Dialog - Create new accounts with goal amounts
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QDoubleSpinBox, QCheckBox, QPushButton, 
                             QLabel, QMessageBox)
from themes import theme_manager


class AddAccountDialog(QDialog):
    def __init__(self, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager
        self.setWindowTitle("Add New Account")
        self.setModal(True)
        self.resize(400, 300)
        
        self.init_ui()
        self.apply_theme()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Create New Account")
        title.setFont(theme_manager.get_font("title"))
        layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Account name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Emergency Fund, Car Savings, etc.")
        self.name_edit.textChanged.connect(self.validate_create_button)
        form_layout.addRow("Account Name:", self.name_edit)

        # Starting balance (with tooltip)
        balance_label = QLabel("Starting Balance ($):")
        balance_label.setToolTip("Initial amount when account is created")
        self.balance_spin = QDoubleSpinBox()
        self.balance_spin.setRange(-999999.99, 999999.99)
        self.balance_spin.setDecimals(2)
        self.balance_spin.setValue(0.00)
        self.balance_spin.setToolTip("Initial amount when account is created")
        form_layout.addRow(balance_label, self.balance_spin)

        # Goal amount (with tooltip)
        goal_label = QLabel("Savings Goal ($):")
        goal_label.setToolTip("Set to 0.00 for no specific goal")
        self.goal_spin = QDoubleSpinBox()
        self.goal_spin.setRange(0.00, 999999.99)
        self.goal_spin.setDecimals(2)
        self.goal_spin.setValue(0.00)
        self.goal_spin.setToolTip("Set to 0.00 for no specific goal")
        form_layout.addRow(goal_label, self.goal_spin)

        # Auto-save amount (with tooltip)
        auto_save_label = QLabel("Auto-Save Amount:")
        auto_save_label.setToolTip("Per paycheck (after bills) - values < 1.0 = % of income (e.g., 0.200 = 20%)")
        self.auto_save_spin = QDoubleSpinBox()
        self.auto_save_spin.setRange(0.00, 999999.99)
        self.auto_save_spin.setDecimals(3)  # Allow for percentages like 0.300
        self.auto_save_spin.setValue(0.00)
        self.auto_save_spin.setToolTip("Per paycheck (after bills) - values < 1.0 = % of income (e.g., 0.200 = 20%)")
        form_layout.addRow(auto_save_label, self.auto_save_spin)

        # Default savings checkbox (with tooltip)
        self.default_save_checkbox = QCheckBox("Make this the default savings account")
        self.default_save_checkbox.setToolTip("Default savings account receives automatic savings from paychecks")
        form_layout.addRow("", self.default_save_checkbox)
        
        layout.addLayout(form_layout)
        
        # Preview section
        self.preview_label = QLabel()
        # Preview styling will be handled by apply_theme
        self.update_preview()
        layout.addWidget(self.preview_label)
        
        # Connect signals for live preview
        self.name_edit.textChanged.connect(self.update_preview)
        self.balance_spin.valueChanged.connect(self.update_preview)
        self.goal_spin.valueChanged.connect(self.update_preview)
        self.auto_save_spin.valueChanged.connect(self.update_preview)
        self.default_save_checkbox.toggled.connect(self.update_preview)
        
        # Buttons (right-justified with focused style for Create)
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.create_account)
        self.create_button.setDefault(True)
        self.create_button.setEnabled(False)  # Disabled until name is entered

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.create_button)
        layout.addLayout(button_layout)

        # Apply button theme
        self.apply_button_theme()

        self.setLayout(layout)
    
    def validate_create_button(self):
        """Enable/disable Create button based on whether name is entered"""
        name = self.name_edit.text().strip()
        self.create_button.setEnabled(bool(name))

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
            # Check if this is a percentage-based auto-save
            if auto_save < 1.0 and auto_save > 0:
                preview_text += f"Auto-Save: {auto_save * 100:.1f}% per paycheck (after bills)\n"
            else:
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

        # Note: Starting balance can be negative (for accounts with debt/overdrafts)

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
            from views.dialogs.settings_dialog import get_setting

            name = self.name_edit.text().strip()
            balance = self.balance_spin.value()
            goal = self.goal_spin.value()
            auto_save = self.auto_save_spin.value()
            is_default = self.default_save_checkbox.isChecked()

            # Create new account using transaction manager (handles defaults and balance history)
            new_account = self.transaction_manager.add_account(
                name=name,
                goal_amount=goal,
                auto_save_amount=auto_save,
                is_default_save=is_default,
                initial_balance=balance
            )

            # Check if testing mode is enabled
            testing_mode = get_setting("testing_mode", False)

            if testing_mode:
                # In testing mode, show detailed verification from database
                from models import Account

                # Retrieve the account from database to verify
                saved_account = self.transaction_manager.db.query(Account).filter(
                    Account.id == new_account.id
                ).first()

                if saved_account:
                    # Build verification details
                    details = [
                        "✓ Account Created Successfully",
                        "",
                        "DATABASE VERIFICATION:",
                        f"• Account ID: {saved_account.id}",
                        f"• Name: {saved_account.name}",
                        f"• Starting Balance: ${balance:.2f}",
                        f"• Goal Amount: ${saved_account.goal_amount:.2f}",
                        f"• Auto-Save Amount: {saved_account.auto_save_amount:.3f}",
                        f"• Is Default Save: {saved_account.is_default_save}",
                    ]

                    # Show auto-save with percentage if applicable
                    if saved_account.auto_save_amount > 0:
                        if saved_account.auto_save_amount < 1.0:
                            details.append(f"• Auto-Save Display: {saved_account.auto_save_amount * 100:.1f}% per paycheck")
                        else:
                            details.append(f"• Auto-Save Display: ${saved_account.auto_save_amount:.2f} per paycheck")

                    QMessageBox.information(
                        self,
                        "Success - Testing Mode",
                        "\n".join(details)
                    )
                else:
                    QMessageBox.warning(self, "Testing Mode", "Account created but could not verify in database")

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating account: {str(e)}")
            import traceback
            traceback.print_exc()

    def apply_button_theme(self):
        """Apply focused styling to Create button, normal styling to Cancel"""
        colors = theme_manager.get_colors()

        # Create button - focused style (primary background with primary_dark hover)
        self.create_button.setStyleSheet(f"""
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
        """)
        
        # Preview label special styling
        if hasattr(self, 'preview_label'):
            self.preview_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {colors['surface_variant']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 10px;
                    color: {colors['text_primary']};
                }}
            """)