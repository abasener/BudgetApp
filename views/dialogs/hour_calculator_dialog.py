"""
Hour Calculator Dialog - Calculate work hours needed for expenses and goals
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QDoubleSpinBox, QPushButton, QLabel, 
                             QTextEdit, QMessageBox, QFrame, QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import date, timedelta
from themes import theme_manager
from views.dialogs.settings_dialog import get_setting, save_setting


class HourCalculatorDialog(QDialog):
    def __init__(self, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager
        self.setWindowTitle("💼 Hour Calculator")
        self.setModal(True)
        self.resize(550, 650)
        
        self.init_ui()
        self.apply_theme()
        self.calculate_breakdown()  # Initial calculation
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Hour Calculator")
        title.setFont(theme_manager.get_font("title"))
        layout.addWidget(title)
        
        # Input form
        form_layout = QFormLayout()
        
        # Hourly rate - load from settings
        self.hourly_rate_spin = QDoubleSpinBox()
        self.hourly_rate_spin.setRange(5.00, 999.99)
        self.hourly_rate_spin.setDecimals(2)
        default_rate = get_setting("default_hourly_rate", 50.00)
        self.hourly_rate_spin.setValue(default_rate)
        self.hourly_rate_spin.valueChanged.connect(self.calculate_breakdown)
        self.hourly_rate_spin.valueChanged.connect(self.save_hourly_rate)
        form_layout.addRow("Hourly Rate ($):", self.hourly_rate_spin)
        
        # Hours worked per 2 weeks
        self.hours_worked_spin = QDoubleSpinBox()
        self.hours_worked_spin.setRange(0.0, 168.0)  # Max 168 hours in 2 weeks
        self.hours_worked_spin.setDecimals(1)
        self.hours_worked_spin.setValue(40.0)  # Default 40 hours
        self.hours_worked_spin.valueChanged.connect(self.calculate_breakdown)
        form_layout.addRow("Hours Worked (2 weeks):", self.hours_worked_spin)
        
        # Minimum daily spending threshold
        self.min_daily_spin = QDoubleSpinBox()
        self.min_daily_spin.setRange(0.00, 999.99)
        self.min_daily_spin.setDecimals(2)
        self.min_daily_spin.setValue(30.00)
        self.min_daily_spin.valueChanged.connect(self.calculate_breakdown)
        form_layout.addRow("Min Daily Spending ($):", self.min_daily_spin)
        
        layout.addLayout(form_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Calculation results
        results_label = QLabel("Calculation Results:")
        results_label.setFont(theme_manager.get_font("subtitle"))
        layout.addWidget(results_label)
        
        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(250)
        self.results_text.setMaximumHeight(350)
        # Use monospace font for better alignment
        self.results_text.setFont(theme_manager.get_font("monospace"))
        layout.addWidget(self.results_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.recalculate_btn = QPushButton("Recalculate")
        self.recalculate_btn.clicked.connect(self.calculate_breakdown)
        button_layout.addWidget(self.recalculate_btn)
        
        button_layout.addStretch()
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setDefault(True)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def save_hourly_rate(self, value):
        """Save hourly rate to app settings when changed"""
        save_setting("default_hourly_rate", value)

    def calculate_breakdown(self):
        """Calculate and display the income/expense breakdown"""
        try:
            # Get input values
            hourly_rate = self.hourly_rate_spin.value()
            hours_worked = self.hours_worked_spin.value()
            min_daily = self.min_daily_spin.value()
            
            # Calculate gross income (2 weeks)
            gross_income = hourly_rate * hours_worked
            
            # Calculate dynamic percentage deductions (taxes, etc.) from bills
            percentage_rate = self.get_percentage_deductions()
            percentage_deductions = gross_income * percentage_rate
            net_income = gross_income - percentage_deductions
            
            # Get bills and savings data
            bills_total = self.get_bills_total()
            savings_total = self.get_auto_savings_total()
            
            # Calculate coverage
            total_fixed_expenses = bills_total + savings_total
            remaining_after_fixed = net_income - total_fixed_expenses
            
            # Build results text
            results = []
            results.append("=== INCOME BREAKDOWN (2 weeks) ===")
            results.append(f"Gross Income:         ${gross_income:,.2f}")
            results.append(f"Dynamic Savings ({percentage_rate*100:.1f}%): -${percentage_deductions:,.2f}")
            results.append(f"Net Income:           ${net_income:,.2f}")
            results.append("")
            
            results.append("=== FIXED EXPENSES (2 weeks) ===")
            results.append(f"Bills Total:          ${bills_total:,.2f}")
            results.append(f"Auto Savings:         ${savings_total:,.2f}")
            results.append(f"Total Fixed:          ${total_fixed_expenses:,.2f}")
            results.append("")
            
            results.append("=== COVERAGE ANALYSIS ===")
            if remaining_after_fixed >= 0:
                daily_leftover = remaining_after_fixed / 14  # 14 days in 2 weeks
                results.append(f"✓ COVERS ALL EXPENSES")
                results.append(f"Amount left over:     ${remaining_after_fixed:,.2f}")
                results.append(f"Daily spending money: ${daily_leftover:,.2f}/day")
                
                if daily_leftover < min_daily:
                    shortage = (min_daily * 14) - remaining_after_fixed
                    results.append(f"⚠️  Below min daily target of ${min_daily:.2f}/day")
                    results.append(f"Need additional:      ${shortage:,.2f}")
            else:
                deficit = abs(remaining_after_fixed)
                results.append(f"❌ DEFICIT: ${deficit:,.2f}")
                additional_hours = deficit / (hourly_rate * (1 - percentage_rate))
                results.append(f"Need {additional_hours:.1f} more hours")
            
            results.append("")
            results.append("=== RECOMMENDATION ===")
            
            # Calculate hours needed for bills + min daily spending
            target_net_income = total_fixed_expenses + (min_daily * 14)
            target_gross_income = target_net_income / (1 - percentage_rate)
            hours_needed = target_gross_income / hourly_rate
            
            results.append(f"To cover bills + ${min_daily:.2f}/day:")
            results.append(f"Hours needed:         {hours_needed:.1f} hours")
            results.append(f"Gross income needed:  ${target_gross_income:,.2f}")
            results.append(f"After taxes:          ${target_net_income:,.2f}")
            
            # Display results
            self.results_text.setPlainText("\n".join(results))
            
        except Exception as e:
            error_text = f"Error calculating breakdown: {str(e)}\n\nPlease check your input values and try again."
            self.results_text.setPlainText(error_text)
    
    def get_percentage_deductions(self):
        """Get total percentage deductions from bills with auto_save < 1.0"""
        try:
            bills = self.transaction_manager.get_all_bills()
            total_percentage = 0.0
            
            for bill in bills:
                # Check if bill has auto_save amount less than 1 (indicating percentage)
                if hasattr(bill, 'auto_save_amount') and bill.auto_save_amount is not None:
                    if 0 < bill.auto_save_amount < 1.0:
                        # This is a percentage (e.g., 0.1 = 10%)
                        total_percentage += bill.auto_save_amount
            
            return total_percentage
            
        except Exception as e:
            print(f"Error getting percentage deductions: {e}")
            return 0.0  # Default to 0% if error
    
    def get_bills_total(self):
        """Get total of all fixed bills (bi-weekly amount), excluding percentage-based bills"""
        try:
            bills = self.transaction_manager.get_all_bills()
            total = 0.0
            
            for bill in bills:
                # Skip percentage-based bills (auto_save < 1.0) as they're handled separately
                is_percentage_bill = (hasattr(bill, 'auto_save_amount') and 
                                    bill.auto_save_amount is not None and 
                                    0 < bill.auto_save_amount < 1.0)
                
                if not is_percentage_bill and hasattr(bill, 'typical_amount') and bill.typical_amount:
                    # For simplicity, assume bills are monthly - divide by 2 for bi-weekly
                    bi_weekly_amount = bill.typical_amount / 2
                    total += bi_weekly_amount
            
            return total
            
        except Exception as e:
            print(f"Error getting bills total: {e}")
            return 0.0
    
    def get_auto_savings_total(self):
        """Get total auto-savings amount (bi-weekly)"""
        try:
            accounts = self.transaction_manager.get_all_accounts()
            total = 0.0
            
            # For now, we'll estimate based on typical saving patterns
            # This could be enhanced to track actual auto-save amounts
            savings_accounts = [acc for acc in accounts if 'saving' in acc.name.lower()]
            
            # Simple estimate: $50 bi-weekly per savings account
            total = len(savings_accounts) * 50.0
            
            return total
            
        except Exception as e:
            print(f"Error getting auto savings total: {e}")
            return 0.0
    
    def apply_theme(self):
        """Apply current theme to dialog"""
        colors = theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['background']};
                color: {colors['text_primary']};
            }}
            
            QLabel {{
                color: {colors['text_primary']};
            }}
            
            QDoubleSpinBox, QSpinBox {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 4px 8px;
                color: {colors['text_primary']};
            }}
            
            QDoubleSpinBox:hover, QSpinBox:hover {{
                border: 1px solid {colors['primary']};
            }}
            
            QDoubleSpinBox:focus, QSpinBox:focus {{
                border: 2px solid {colors['primary']};
            }}
            
            QTextEdit {{
                background-color: {colors['background']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 8px;
                color: {colors['text_primary']};
                font-family: monospace;
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
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                color: {colors['text_secondary']};
            }}
            
            QFrame {{
                color: {colors['border']};
            }}
        """)