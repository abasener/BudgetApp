"""
Settings Dialog - Configure persistent application settings
"""

import json
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QComboBox, QPushButton, QLabel, QGroupBox, QMessageBox, QDoubleSpinBox)
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
        
        # Theme settings group
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QFormLayout()
        
        # Default theme dropdown
        self.default_theme_combo = QComboBox()
        self.populate_theme_combo()
        theme_layout.addRow("Default Theme:", self.default_theme_combo)
        
        theme_group.setLayout(theme_layout)
        main_layout.addWidget(theme_group)
        
        # Sorting settings group
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
        main_layout.addWidget(sorting_group)
        
        # Dashboard chart settings group
        dashboard_group = QGroupBox("Dashboard Chart Settings")
        dashboard_layout = QFormLayout()
        
        # First line plot account
        self.chart1_account_combo = QComboBox()
        self.populate_account_combo(self.chart1_account_combo)
        dashboard_layout.addRow("First Chart Account:", self.chart1_account_combo)
        
        # Second line plot account
        self.chart2_account_combo = QComboBox()
        self.populate_account_combo(self.chart2_account_combo)
        dashboard_layout.addRow("Second Chart Account:", self.chart2_account_combo)
        
        dashboard_group.setLayout(dashboard_layout)
        main_layout.addWidget(dashboard_group)
        
        # Calculator settings group
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
        main_layout.addWidget(calculator_group)
        
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
            "default_hourly_rate": 50.00
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
    
    def get_ui_settings(self):
        """Get current settings from UI controls"""
        return {
            "default_theme": self.default_theme_combo.currentData(),
            "bills_sort_order": self.bills_sort_combo.currentText(),
            "savings_sort_order": self.savings_sort_combo.currentText(),
            "dashboard_chart1_account": self.chart1_account_combo.currentData(),
            "dashboard_chart2_account": self.chart2_account_combo.currentData(),
            "default_hourly_rate": self.hourly_rate_spin.value()
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
            """)
            
        except Exception as e:
            print(f"Error applying theme to settings dialog: {e}")


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
        "default_hourly_rate": 50.00
    }


def get_setting(key, default=None):
    """Get a specific setting value"""
    settings = load_app_settings()
    return settings.get(key, default)