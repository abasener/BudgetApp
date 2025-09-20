"""
Settings Dialog - Configure persistent application settings
"""

import json
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
                             QComboBox, QPushButton, QLabel, QGroupBox, QMessageBox, QDoubleSpinBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from themes import theme_manager


class SettingsDialog(QDialog):
    """Dialog for configuring persistent application settings"""
    
    settings_saved = pyqtSignal()  # Signal when settings are saved
    
    def __init__(self, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager
        self.settings_file = "app_settings.json"
        self.original_settings = {}
        self.current_settings = {}
        
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(500, 400)
        
        self.init_ui()
        self.load_settings()
        self.apply_theme()
    
    def init_ui(self):
        """Initialize the UI layout"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        # Header
        header_label = QLabel("Application Settings")
        header_label.setFont(theme_manager.get_font("title"))
        main_layout.addWidget(header_label)

        # Create 2-column layout for settings groups
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(20)

        # LEFT COLUMN
        left_column = QVBoxLayout()
        left_column.setSpacing(15)

        # Sorting settings group (LEFT)
        sorting_group = QGroupBox("Sorting Settings")
        sorting_layout = QFormLayout()

        # Bills sorting order
        self.bills_sort_combo = QComboBox()
        self.bills_sort_combo.addItems(["Alphabetical", "Amount (High to Low)", "Amount (Low to High)", "Due Date"])
        sorting_layout.addRow("Bills Sort Order:", self.bills_sort_combo)

        # Savings sorting order
        self.savings_sort_combo = QComboBox()
        self.savings_sort_combo.addItems(["Alphabetical", "Balance (High to Low)", "Balance (Low to High)", "Goal Progress"])
        sorting_layout.addRow("Savings Sort Order:", self.savings_sort_combo)

        sorting_group.setLayout(sorting_layout)
        left_column.addWidget(sorting_group)

        # Graph Filtering settings group (LEFT)
        filtering_group = QGroupBox("Graph Filtering Settings")
        filtering_layout = QFormLayout()

        # Default "Normal Spending Only" checkbox state
        self.default_analytics_checkbox = QCheckBox("Default to Normal Spending Only")
        self.default_analytics_checkbox.setChecked(True)  # Default to true
        self.default_analytics_checkbox.setToolTip("When enabled, the dashboard will start with 'Normal Spending Only' checked")
        filtering_layout.addRow("", self.default_analytics_checkbox)

        # Time frame filtering dropdown
        self.time_frame_combo = QComboBox()
        self.time_frame_combo.addItems([
            "All Time",
            "Last Year",
            "Last Month",
            "Last 20 Entries"
        ])
        self.time_frame_combo.setToolTip("Filter charts and plots to show only recent data")
        filtering_layout.addRow("Time Frame Filter:", self.time_frame_combo)

        # Dashboard chart account fields (moved from dashboard group)
        self.chart1_account_combo = QComboBox()
        self.populate_account_combo(self.chart1_account_combo)
        filtering_layout.addRow("First Chart Account:", self.chart1_account_combo)

        self.chart2_account_combo = QComboBox()
        self.populate_account_combo(self.chart2_account_combo)
        filtering_layout.addRow("Second Chart Account:", self.chart2_account_combo)

        filtering_group.setLayout(filtering_layout)
        left_column.addWidget(filtering_group)

        # RIGHT COLUMN
        right_column = QVBoxLayout()
        right_column.setSpacing(15)

        # Theme settings group (RIGHT)
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QFormLayout()

        # Default theme dropdown
        self.default_theme_combo = QComboBox()
        self.populate_theme_combo()
        theme_layout.addRow("Default Theme:", self.default_theme_combo)

        theme_group.setLayout(theme_layout)
        right_column.addWidget(theme_group)

        # Calculator settings group (RIGHT)
        calculator_group = QGroupBox("Calculator Settings")
        calculator_layout = QFormLayout()
        
        # Default hourly rate
        self.hourly_rate_spin = QDoubleSpinBox()
        self.hourly_rate_spin.setMinimum(0.01)
        self.hourly_rate_spin.setMaximum(1000.00)
        self.hourly_rate_spin.setDecimals(2)
        self.hourly_rate_spin.setValue(50.00)  # Default value
        self.hourly_rate_spin.setSuffix(" $/hour")
        self.hourly_rate_spin.setToolTip("Default hourly rate for the hour calculator")
        calculator_layout.addRow("Default Hourly Rate:", self.hourly_rate_spin)
        
        calculator_group.setLayout(calculator_layout)
        right_column.addWidget(calculator_group)

        # Add columns to main layout
        columns_layout.addLayout(left_column)
        columns_layout.addLayout(right_column)
        main_layout.addLayout(columns_layout)

        # Data management group
        data_group = QGroupBox("Data Management")
        data_layout = QVBoxLayout()

        # Create 2x2 grid for buttons
        button_grid = QGridLayout()

        # Top row - Testing functions
        import_test_button = QPushButton("📥 Import Test Data")
        import_test_button.setStyleSheet("color: blue; font-weight: bold; padding: 8px;")
        import_test_button.setToolTip("Import test data from TestData/Data2.xlsx if file exists and has expected format")
        import_test_button.clicked.connect(self.import_test_data)
        button_grid.addWidget(import_test_button, 0, 0)

        reset_test_button = QPushButton("🧪 Reset Test Data")
        reset_test_button.setStyleSheet("color: orange; font-weight: bold; padding: 8px;")
        reset_test_button.setToolTip("Delete transactions and weeks, reset account balances, keep bills and accounts")
        reset_test_button.clicked.connect(self.confirm_reset_test)
        button_grid.addWidget(reset_test_button, 0, 1)

        # Bottom row - Data management
        export_data_button = QPushButton("📊 Export All Data")
        export_data_button.setStyleSheet("color: green; font-weight: bold; padding: 8px;")
        export_data_button.setToolTip("Export all data to CSV files for backup or analysis")
        export_data_button.clicked.connect(self.export_data)
        button_grid.addWidget(export_data_button, 1, 0)

        reset_data_button = QPushButton("🗑️ Reset All Data")
        reset_data_button.setStyleSheet("color: red; font-weight: bold; padding: 8px;")
        reset_data_button.setToolTip("Permanently delete all transactions, accounts, bills, and weeks")
        reset_data_button.clicked.connect(self.confirm_reset_data)
        button_grid.addWidget(reset_data_button, 1, 1)

        # Add grid to layout
        data_layout.addLayout(button_grid)

        # Warning label
        warning_label = QLabel("⚠️ Warning: Reset will permanently delete ALL your data!")
        warning_label.setStyleSheet("color: orange; font-style: italic; padding: 5px;")
        data_layout.addWidget(warning_label)

        data_group.setLayout(data_layout)
        main_layout.addWidget(data_group)

        # Buttons
        button_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_button)
        
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        main_layout.addWidget(QGroupBox())  # Spacer
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def populate_theme_combo(self):
        """Populate theme dropdown with available themes"""
        for theme_id, theme_info in theme_manager.themes.items():
            self.default_theme_combo.addItem(theme_info['name'], theme_id)
    
    def populate_account_combo(self, combo):
        """Populate account dropdown with available accounts plus random option"""
        combo.addItem("Random (Default)", "random")
        
        try:
            accounts = self.transaction_manager.get_all_accounts()
            for account in accounts:
                combo.addItem(account.name, account.name)
        except Exception as e:
            print(f"Error loading accounts for settings: {e}")
    
    def get_default_settings(self):
        """Get default application settings"""
        return {
            "default_theme": "dark",
            "bills_sort_order": "Alphabetical",
            "savings_sort_order": "Alphabetical",
            "dashboard_chart1_account": "random",
            "dashboard_chart2_account": "random",
            "default_hourly_rate": 50.00,
            "default_analytics_only": True,
            "time_frame_filter": "All Time"
        }
    
    def load_settings(self):
        """Load settings from file or use defaults"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.current_settings = json.load(f)
            else:
                self.current_settings = self.get_default_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.current_settings = self.get_default_settings()
        
        # Store original settings for change detection
        self.original_settings = self.current_settings.copy()
        
        # Apply settings to UI
        self.apply_settings_to_ui()
    
    def apply_settings_to_ui(self):
        """Apply loaded settings to UI controls"""
        # Set default theme
        theme_index = self.default_theme_combo.findData(self.current_settings.get("default_theme", "dark"))
        if theme_index >= 0:
            self.default_theme_combo.setCurrentIndex(theme_index)
        
        # Set bills sort order
        bills_sort = self.current_settings.get("bills_sort_order", "Alphabetical")
        bills_index = self.bills_sort_combo.findText(bills_sort)
        if bills_index >= 0:
            self.bills_sort_combo.setCurrentIndex(bills_index)
        
        # Set savings sort order
        savings_sort = self.current_settings.get("savings_sort_order", "Alphabetical")
        savings_index = self.savings_sort_combo.findText(savings_sort)
        if savings_index >= 0:
            self.savings_sort_combo.setCurrentIndex(savings_index)
        
        # Set dashboard chart accounts
        chart1_account = self.current_settings.get("dashboard_chart1_account", "random")
        chart1_index = self.chart1_account_combo.findData(chart1_account)
        if chart1_index >= 0:
            self.chart1_account_combo.setCurrentIndex(chart1_index)
            
        chart2_account = self.current_settings.get("dashboard_chart2_account", "random")
        chart2_index = self.chart2_account_combo.findData(chart2_account)
        if chart2_index >= 0:
            self.chart2_account_combo.setCurrentIndex(chart2_index)
            
        # Set default hourly rate
        hourly_rate = self.current_settings.get("default_hourly_rate", 50.00)
        self.hourly_rate_spin.setValue(hourly_rate)

        # Set default analytics checkbox state
        default_analytics = self.current_settings.get("default_analytics_only", True)
        self.default_analytics_checkbox.setChecked(default_analytics)

        # Set time frame filter
        time_frame = self.current_settings.get("time_frame_filter", "All Time")
        time_frame_index = self.time_frame_combo.findText(time_frame)
        if time_frame_index >= 0:
            self.time_frame_combo.setCurrentIndex(time_frame_index)
    
    def get_ui_settings(self):
        """Get current settings from UI controls"""
        return {
            "default_theme": self.default_theme_combo.currentData(),
            "bills_sort_order": self.bills_sort_combo.currentText(),
            "savings_sort_order": self.savings_sort_combo.currentText(),
            "dashboard_chart1_account": self.chart1_account_combo.currentData(),
            "dashboard_chart2_account": self.chart2_account_combo.currentData(),
            "default_hourly_rate": self.hourly_rate_spin.value(),
            "default_analytics_only": self.default_analytics_checkbox.isChecked(),
            "time_frame_filter": self.time_frame_combo.currentText()
        }
    
    def reset_to_defaults(self):
        """Reset all settings to default values"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.current_settings = self.get_default_settings()
            self.apply_settings_to_ui()
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            # Get current UI values
            new_settings = self.get_ui_settings()
            
            # Check if anything changed
            changes = []
            for key, new_value in new_settings.items():
                old_value = self.original_settings.get(key)
                if new_value != old_value:
                    changes.append(f"{key}: {old_value} → {new_value}")
            
            if not changes:
                QMessageBox.information(self, "No Changes", "No changes were made to settings.")
                return
            
            # Show confirmation
            change_text = "The following settings will be changed:\n\n" + "\n".join(changes)
            change_text += "\n\nThese changes will take effect after restarting the application."
            
            reply = QMessageBox.question(
                self, "Save Settings", change_text,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Save to file
            with open(self.settings_file, 'w') as f:
                json.dump(new_settings, f, indent=2)
            
            # Apply theme change immediately if changed
            if new_settings["default_theme"] != self.original_settings.get("default_theme"):
                theme_manager.set_theme(new_settings["default_theme"])
            
            QMessageBox.information(self, "Settings Saved", 
                                  "Settings have been saved successfully!\n\n"
                                  "Some changes may require restarting the application to take full effect.")
            
            # Emit signal and close
            self.settings_saved.emit()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
            print(f"Error saving settings: {e}")
    
    def apply_theme(self):
        """Apply current theme to dialog"""
        try:
            colors = theme_manager.get_colors()
            
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
                    min-height: 20px;
                }}
                
                QComboBox:hover {{
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
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid {colors['text_primary']};
                    margin-right: 5px;
                }}
                
                QComboBox QAbstractItemView {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    selection-background-color: {colors['primary']};
                    selection-color: {colors['background']};
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
                
                QDoubleSpinBox {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 4px 8px;
                    color: {colors['text_primary']};
                    min-height: 20px;
                }}
                
                QDoubleSpinBox:hover {{
                    border: 1px solid {colors['primary']};
                }}
                
                QDoubleSpinBox:focus {{
                    border: 2px solid {colors['primary']};
                }}
                
                QDoubleSpinBox::up-button {{
                    background-color: {colors['surface_variant']};
                    border: 1px solid {colors['border']};
                    border-radius: 2px;
                    width: 16px;
                    margin: 1px;
                }}
                
                QDoubleSpinBox::up-button:hover {{
                    background-color: {colors['primary']};
                }}
                
                QDoubleSpinBox::up-button:pressed {{
                    background-color: {colors.get('primary_dark', colors['primary'])};
                }}
                
                QDoubleSpinBox::down-button {{
                    background-color: {colors['surface_variant']};
                    border: 1px solid {colors['border']};
                    border-radius: 2px;
                    width: 16px;
                    margin: 1px;
                }}
                
                QDoubleSpinBox::down-button:hover {{
                    background-color: {colors['primary']};
                }}
                
                QDoubleSpinBox::down-button:pressed {{
                    background-color: {colors.get('primary_dark', colors['primary'])};
                }}
                
                QDoubleSpinBox::up-arrow {{
                    image: none;
                    border-left: 3px solid transparent;
                    border-right: 3px solid transparent;
                    border-bottom: 3px solid {colors['text_primary']};
                    width: 6px;
                    height: 3px;
                }}
                
                QDoubleSpinBox::down-arrow {{
                    image: none;
                    border-left: 3px solid transparent;
                    border-right: 3px solid transparent;
                    border-top: 3px solid {colors['text_primary']};
                    width: 6px;
                    height: 3px;
                }}

                QCheckBox {{
                    color: {colors['text_primary']};
                    spacing: 8px;
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
            """)
            
        except Exception as e:
            print(f"Error applying theme to settings dialog: {e}")

    def confirm_reset_data(self):
        """Math-based confirmation dialog for data reset"""
        import random
        from models import get_db, Week, Transaction, Account, Bill, AccountHistory

        # Generate random math problem
        num1 = random.randint(2, 99)
        num2 = random.randint(2, 99)
        correct_answer = num1 * num2

        # Create custom dialog
        from PyQt6.QtWidgets import QInputDialog

        # First confirmation
        reply = QMessageBox.question(
            self,
            "⚠️ DANGER: Reset All Data",
            "This will permanently delete ALL your data:\n\n"
            "• All transactions (spending, income, bills)\n"
            "• All pay weeks and periods\n"
            "• All savings accounts\n"
            "• All bills\n\n"
            "This action CANNOT be undone!\n\n"
            "Are you absolutely sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Math verification
        answer, ok = QInputDialog.getInt(
            self,
            "Math Verification Required",
            f"To confirm this dangerous action, solve:\n\n{num1} × {num2} = ?",
            0, 0, 999999, 1
        )

        if not ok:
            return

        if answer != correct_answer:
            QMessageBox.critical(
                self,
                "Incorrect Answer",
                f"Incorrect! The answer was {correct_answer}.\n\nData reset cancelled for your protection."
            )
            return

        # Perform the reset
        try:
            db = get_db()

            # Count items before deletion
            transaction_count = db.query(Transaction).count()
            week_count = db.query(Week).count()
            account_count = db.query(Account).count()
            bill_count = db.query(Bill).count()
            history_count = db.query(AccountHistory).count()

            # Delete all data (order matters due to foreign keys)
            db.query(AccountHistory).delete()  # Delete history first (references transactions)
            db.query(Transaction).delete()
            db.query(Week).delete()
            db.query(Account).delete()
            db.query(Bill).delete()

            db.commit()
            db.close()

            QMessageBox.information(
                self,
                "✅ Data Reset Complete",
                f"Successfully deleted:\n\n"
                f"• {transaction_count} transactions\n"
                f"• {week_count} weeks\n"
                f"• {account_count} accounts\n"
                f"• {bill_count} bills\n"
                f"• {history_count} balance history entries\n\n"
                f"Your app now has a clean slate!"
            )

            # Signal that settings changed so main window refreshes
            self.settings_saved.emit()

        except Exception as e:
            QMessageBox.critical(self, "Reset Failed", f"Error during data reset: {e}")

    def confirm_reset_test(self):
        """Math-based confirmation dialog for test data reset"""
        import random
        from models import get_db, Week, Transaction, Account, Bill, AccountHistory

        # Generate random math problem
        num1 = random.randint(2, 50)
        num2 = random.randint(2, 50)
        correct_answer = num1 * num2

        # Create custom dialog
        from PyQt6.QtWidgets import QInputDialog

        # First confirmation
        reply = QMessageBox.question(
            self,
            "⚠️ Reset Test Data",
            "This will reset for testing by deleting:\n\n"
            "• All transactions (spending, income, bills)\n"
            "• All pay weeks and periods\n"
            "• Reset all account balances to $0\n\n"
            "This will keep:\n"
            "• All savings accounts (structure)\n"
            "• All bills (structure)\n\n"
            "This action cannot be undone!\n\n"
            "Are you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Math verification
        answer, ok = QInputDialog.getInt(
            self,
            "Math Verification Required",
            f"To confirm this action, solve:\n\n{num1} × {num2} = ?",
            0, 0, 999999, 1
        )

        if not ok:
            return

        if answer != correct_answer:
            QMessageBox.critical(
                self,
                "Incorrect Answer",
                f"Incorrect! The answer was {correct_answer}.\n\nTest reset cancelled for your protection."
            )
            return

        # Perform the test reset
        try:
            db = get_db()

            # Count items before deletion
            transaction_count = db.query(Transaction).count()
            week_count = db.query(Week).count()
            history_count = db.query(AccountHistory).count()

            # Delete AccountHistory first (references transactions)
            db.query(AccountHistory).delete()

            # Delete transactions and weeks
            db.query(Transaction).delete()
            db.query(Week).delete()

            # Reset account and bill balances by creating new starting balance entries
            accounts = db.query(Account).all()
            bills = db.query(Bill).all()
            account_count = len(accounts)
            bill_count = len(bills)

            # Create starting balance entries for accounts (usually $0)
            from models.account_history import AccountHistory

            for account in accounts:
                # Create starting balance entry (typically $0)
                starting_entry = AccountHistory.create_starting_balance_entry(
                    account_id=account.id,
                    account_type="account",
                    starting_balance=0.0
                )
                db.add(starting_entry)

            for bill in bills:
                # Create starting balance entry (typically $0)
                starting_entry = AccountHistory.create_starting_balance_entry(
                    account_id=bill.id,
                    account_type="bill",
                    starting_balance=0.0
                )
                db.add(starting_entry)

            db.commit()
            db.close()

            QMessageBox.information(
                self,
                "Test Reset Complete",
                f"Successfully reset test data:\n\n"
                f"• Deleted {transaction_count} transactions\n"
                f"• Deleted {week_count} weeks\n"
                f"• Deleted {history_count} balance history entries\n"
                f"• Reset {account_count} account balances to $0\n"
                f"• Reset {bill_count} bill balances to $0\n\n"
                f"Ready for testing!"
            )

            # Signal that settings changed so main window refreshes
            self.settings_saved.emit()

        except Exception as e:
            QMessageBox.critical(self, "Reset Failed", f"Error during test reset: {e}")

    def export_data(self):
        """Export all data to CSV files"""
        from PyQt6.QtWidgets import QFileDialog
        from models import get_db, Week, Transaction, Account, Bill, AccountHistory
        import csv
        import os
        from datetime import datetime

        # Let user choose export directory
        export_dir = QFileDialog.getExistingDirectory(
            self,
            "Choose Export Directory",
            os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )

        if not export_dir:
            return

        try:
            db = get_db()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Export transactions
            transactions = db.query(Transaction).all()
            if transactions:
                transactions_file = os.path.join(export_dir, f"transactions_{timestamp}.csv")
                with open(transactions_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'ID', 'Transaction_Type', 'Week_Number', 'Amount', 'Date',
                        'Category', 'Description', 'Account_ID', 'Account_Name',
                        'Bill_ID', 'Bill_Type', 'Is_Spending', 'Is_Income',
                        'Is_Saving', 'Is_Bill_Pay', 'Include_In_Analytics'
                    ])

                    for t in transactions:
                        writer.writerow([
                            t.id, t.transaction_type, t.week_number, t.amount, t.date,
                            t.category, t.description, t.account_id, t.account_saved_to,
                            t.bill_id, t.bill_type, t.is_spending, t.is_income,
                            t.is_saving, t.is_bill_pay, t.include_in_analytics
                        ])

            # Export weeks
            weeks = db.query(Week).all()
            if weeks:
                weeks_file = os.path.join(export_dir, f"weeks_{timestamp}.csv")
                with open(weeks_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Week_Number', 'Start_Date', 'End_Date', 'Running_Total'])

                    for w in weeks:
                        writer.writerow([w.id, w.week_number, w.start_date, w.end_date, w.running_total])

            # Export accounts
            accounts = db.query(Account).all()
            if accounts:
                accounts_file = os.path.join(export_dir, f"accounts_{timestamp}.csv")
                with open(accounts_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Name', 'Account_Type', 'Goal_Amount', 'Current_Balance', 'Auto_Save_Amount', 'Is_Default_Savings'])

                    for a in accounts:
                        current_balance = a.get_current_balance(db)
                        writer.writerow([a.id, a.name, a.account_type, a.goal_amount, current_balance,
                                       getattr(a, 'auto_save_amount', 0.0), a.is_default_savings])

            # Export bills
            bills = db.query(Bill).all()
            if bills:
                bills_file = os.path.join(export_dir, f"bills_{timestamp}.csv")
                with open(bills_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Name', 'Bill_Type', 'Amount_To_Save', 'Current_Balance'])

                    for b in bills:
                        current_balance = b.get_current_balance(db)
                        writer.writerow([b.id, b.name, b.bill_type, b.amount_to_save, current_balance])

            # Export AccountHistory
            history_entries = db.query(AccountHistory).all()
            if history_entries:
                history_file = os.path.join(export_dir, f"account_history_{timestamp}.csv")
                with open(history_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Account_ID', 'Account_Type', 'Transaction_ID', 'Transaction_Date',
                                   'Change_Amount', 'Running_Total', 'Description'])

                    for h in history_entries:
                        writer.writerow([h.id, h.account_id, h.account_type, h.transaction_id, h.transaction_date,
                                       h.change_amount, h.running_total, h.description or ""])

            db.close()

            # Count exported items
            transaction_count = len(transactions) if transactions else 0
            week_count = len(weeks) if weeks else 0
            account_count = len(accounts) if accounts else 0
            bill_count = len(bills) if bills else 0
            history_count = len(history_entries) if history_entries else 0

            QMessageBox.information(
                self,
                "Export Complete",
                f"Successfully exported to {export_dir}:\n\n"
                f"• {transaction_count} transactions\n"
                f"• {week_count} weeks\n"
                f"• {account_count} accounts\n"
                f"• {bill_count} bills\n"
                f"• {history_count} balance history entries\n\n"
                f"Files are timestamped: {timestamp}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Error during data export: {e}")

    def import_test_data(self):
        """Import test data from TestData/Data2.xlsx with validation"""
        import os

        # Step 1: Check if file exists
        excel_file = "TestData/Data2.xlsx"
        if not os.path.exists(excel_file):
            QMessageBox.warning(
                self,
                "File Not Found",
                f"Step 1 Failed: Test data file not found.\n\n"
                f"Expected file: {excel_file}\n"
                f"Please ensure the test data file exists in the TestData directory."
            )
            return

        try:
            import pandas as pd

            # Step 2: Try to read the Excel file and verify structure
            try:
                # Read Spending table (columns 0-3)
                spending_df = pd.read_excel(excel_file, sheet_name=0, header=0, usecols=[0, 1, 2, 3])
                spending_df = spending_df.dropna(how='all')

                # Read Paychecks table (columns 5-7)
                paychecks_df = pd.read_excel(excel_file, sheet_name=0, header=0, usecols=[5, 6, 7])
                paychecks_df = paychecks_df.dropna(how='all')

            except Exception as e:
                QMessageBox.warning(
                    self,
                    "File Format Error",
                    f"Step 2 Failed: Could not read expected table structure.\n\n"
                    f"Error: {e}\n\n"
                    f"Expected: Two tables side by side in the Excel file."
                )
                return

            # Step 3: Verify headers
            expected_spending_headers = ["Date", "Day", "Catigorie", "Amount"]
            expected_paycheck_headers = ["Start date", "Pay Date", "Amount.1"]

            spending_headers = list(spending_df.columns)
            paycheck_headers = list(paychecks_df.columns)

            if spending_headers != expected_spending_headers:
                QMessageBox.warning(
                    self,
                    "Header Validation Failed",
                    f"Step 3 Failed: Spending table headers don't match.\n\n"
                    f"Expected: {expected_spending_headers}\n"
                    f"Found: {spending_headers}\n\n"
                    f"Please check the Excel file format."
                )
                return

            if paycheck_headers != expected_paycheck_headers:
                QMessageBox.warning(
                    self,
                    "Header Validation Failed",
                    f"Step 3 Failed: Paycheck table headers don't match.\n\n"
                    f"Expected: {expected_paycheck_headers}\n"
                    f"Found: {paycheck_headers}\n\n"
                    f"Please check the Excel file format."
                )
                return

            # All validation passed - confirm import
            reply = QMessageBox.question(
                self,
                "Import Test Data",
                f"All validation checks passed!\n\n"
                f"Found:\n"
                f"• {len(spending_df)} spending transactions\n"
                f"• {len(paychecks_df)} paychecks\n\n"
                f"This will import the test data into your current database.\n"
                f"Are you sure you want to proceed?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Import the data using our existing import script logic
            self.perform_test_data_import(excel_file)

        except ImportError:
            QMessageBox.critical(
                self,
                "Missing Dependency",
                "pandas library is required for Excel file processing.\n"
                "Please install pandas to use this feature."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"Unexpected error during validation: {e}"
            )

    def perform_test_data_import(self, excel_file):
        """Perform the actual test data import"""
        try:
            import pandas as pd
            from services.transaction_manager import TransactionManager
            from services.paycheck_processor import PaycheckProcessor
            from datetime import datetime

            transaction_manager = TransactionManager()
            paycheck_processor = PaycheckProcessor()

            # Read the Excel data
            spending_df = pd.read_excel(excel_file, sheet_name=0, header=0, usecols=[0, 1, 2, 3])
            spending_df = spending_df.dropna(how='all')

            paychecks_df = pd.read_excel(excel_file, sheet_name=0, header=0, usecols=[5, 6, 7])
            paychecks_df = paychecks_df.dropna(how='all')

            # Import paychecks first
            paycheck_count = 0
            for idx, row in paychecks_df.iterrows():
                if pd.isna(row["Start date"]) or pd.isna(row["Pay Date"]) or pd.isna(row["Amount.1"]):
                    continue

                start_date = pd.to_datetime(row["Start date"]).date()
                pay_date = pd.to_datetime(row["Pay Date"]).date()
                amount = float(row["Amount.1"])

                try:
                    paycheck_processor.process_new_paycheck(amount, pay_date, start_date)
                    paycheck_count += 1
                except Exception as e:
                    print(f"Error processing paycheck: {e}")
                    continue

            # Import spending transactions
            transaction_count = 0
            negative_count = 0

            for idx, row in spending_df.iterrows():
                if pd.isna(row["Date"]) or pd.isna(row["Catigorie"]) or pd.isna(row["Amount"]):
                    continue

                transaction_date = pd.to_datetime(row["Date"]).date()
                category = str(row["Catigorie"]).strip()
                amount = float(row["Amount"])

                # Determine which week this transaction belongs to
                week_number = transaction_manager.get_week_number_for_date(transaction_date)
                if week_number is None:
                    continue

                # Determine include_in_analytics flag (negative amounts excluded from plotting)
                include_in_analytics = amount >= 0
                if amount < 0:
                    negative_count += 1

                transaction_data = {
                    "transaction_type": "spending",
                    "week_number": week_number,
                    "amount": abs(amount),
                    "date": transaction_date,
                    "description": f"{category} transaction",
                    "category": category,
                    "include_in_analytics": include_in_analytics
                }

                try:
                    transaction_manager.add_transaction(transaction_data)
                    transaction_count += 1
                except Exception as e:
                    print(f"Error adding transaction: {e}")
                    continue

            transaction_manager.close()
            paycheck_processor.close()

            # Show success message
            QMessageBox.information(
                self,
                "Import Successful",
                f"Test data imported successfully!\n\n"
                f"Imported:\n"
                f"• {paycheck_count} paychecks\n"
                f"• {transaction_count} spending transactions\n"
                f"  - {transaction_count - negative_count} positive (included in analytics)\n"
                f"  - {negative_count} negative (excluded from analytics)\n\n"
                f"The application data has been updated with the test dataset."
            )

            # Signal that data changed so main window refreshes
            self.settings_saved.emit()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Error during test data import: {e}"
            )


def load_app_settings():
    """Load application settings from file"""
    try:
        if os.path.exists("app_settings.json"):
            with open("app_settings.json", 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading app settings: {e}")
    
    # Return defaults if file doesn't exist or error occurs
    return {
        "default_theme": "dark",
        "bills_sort_order": "Alphabetical",
        "savings_sort_order": "Alphabetical",
        "dashboard_chart1_account": "random",
        "dashboard_chart2_account": "random",
        "default_hourly_rate": 50.00,
        "default_analytics_only": True,
        "time_frame_filter": "All Time"
    }


def get_setting(key, default=None):
    """Get a specific setting value"""
    settings = load_app_settings()
    return settings.get(key, default)