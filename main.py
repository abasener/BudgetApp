"""
Budget App - Desktop application for tracking expenses, bills, savings, and income

"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout,
                             QWidget, QMenuBar, QMenu, QToolBar, QPushButton, QDialog, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from utils.error_handler import handle_exception, show_error, is_testing_mode
from views.dialogs.add_transaction_dialog import AddTransactionDialog
from views.dialogs.add_paycheck_dialog import AddPaycheckDialog
from views.dialogs.pay_bill_dialog import PayBillDialog
from views.dialogs.transfer_dialog import TransferDialog
from views.dialogs.add_account_dialog import AddAccountDialog
from views.dialogs.add_bill_dialog import AddBillDialog
from views.dialogs.settings_dialog import SettingsDialog, load_app_settings

from views.dashboard import DashboardView
from views.bills_view import BillsView
from views.weekly_view import WeeklyView
from views.savings_view import SavingsView
from views.categories_view import CategoriesView
from views.year_overview_view import YearOverviewView
from views.transactions_view import TransactionsView
from views.reimbursements_view import ReimbursementsView
from views.scratch_pad_view import ScratchPadView
# Conditional import for optional tax features
try:
    from views.taxes_view import TaxesView
    TAX_MODULE_AVAILABLE = True
except ImportError as e:
    # Only show in console, not as error dialog since this is optional
    TAX_MODULE_AVAILABLE = False
from services.transaction_manager import TransactionManager
from services.analytics import AnalyticsEngine
from services.paycheck_processor import PaycheckProcessor
from themes import theme_manager
from widgets import ThemeSelector


class BudgetApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Budget App")
        self.setGeometry(100, 100, 1200, 1000)  # Increased height for taller charts
        
        # Load settings and apply default theme
        self.app_settings = load_app_settings()
        default_theme = self.app_settings.get("default_theme", "dark")
        theme_manager.set_theme(default_theme)
        
        # Initialize services
        self.transaction_manager = TransactionManager()
        self.analytics_engine = AnalyticsEngine()
        self.paycheck_processor = PaycheckProcessor()
        
        self.init_ui()
        self.apply_theme()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.on_theme_changed)
        
    def init_ui(self):
        # Create central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Initialize views with services
        self.dashboard = DashboardView(
            transaction_manager=self.transaction_manager,
            analytics_engine=self.analytics_engine
        )
        self.bills_view = BillsView(
            transaction_manager=self.transaction_manager
        )
        self.weekly_view = WeeklyView(
            transaction_manager=self.transaction_manager,
            paycheck_processor=self.paycheck_processor
        )
        self.savings_view = SavingsView(
            transaction_manager=self.transaction_manager
        )
        self.categories_view = CategoriesView(
            transaction_manager=self.transaction_manager,
            analytics_engine=self.analytics_engine
        )
        self.year_overview_view = YearOverviewView(
            transaction_manager=self.transaction_manager,
            analytics_engine=self.analytics_engine
        )

        # Initialize taxes view (will be added conditionally)
        if TAX_MODULE_AVAILABLE:
            self.taxes_view = TaxesView(
                transaction_manager=self.transaction_manager,
                analytics_engine=self.analytics_engine
            )
        else:
            self.taxes_view = None

        # Initialize transactions view (will be added conditionally)
        self.transactions_view = TransactionsView(
            transaction_manager=self.transaction_manager
        )

        # Initialize reimbursements view
        self.reimbursements_view = ReimbursementsView(
            transaction_manager=self.transaction_manager
        )

        # Initialize scratch pad view
        self.scratch_pad_view = ScratchPadView(
            transaction_manager=self.transaction_manager
        )

        # Add tabs
        self.tabs.addTab(self.dashboard, "Dashboard")
        self.tabs.addTab(self.bills_view, "Bills")
        self.tabs.addTab(self.savings_view, "Savings")
        self.tabs.addTab(self.weekly_view, "Weekly")
        self.tabs.addTab(self.categories_view, "Categories")
        self.tabs.addTab(self.year_overview_view, "Yearly")

        # Add Reimbursements tab (always visible for now)
        self.reimbursements_tab_index = self.tabs.addTab(self.reimbursements_view, "Reimbursements")

        # Add Scratch Pad tab (always visible)
        self.scratch_pad_tab_index = self.tabs.addTab(self.scratch_pad_view, "Scratch Pad")

        # Add Transactions tab if enabled in settings
        if self.app_settings.get("enable_transactions_tab", False):
            self.transactions_tab_index = self.tabs.addTab(self.transactions_view, "Transactions")
        else:
            self.transactions_tab_index = -1

        # Add Taxes tab if enabled in settings and module available
        if TAX_MODULE_AVAILABLE and self.app_settings.get("enable_tax_features", False):
            self.taxes_tab_index = self.tabs.addTab(self.taxes_view, "Taxes")
        else:
            self.taxes_tab_index = -1
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)

        # Connect tab change to refresh handler
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # Create menu bar and toolbar
        self.create_menu_bar()
        self.create_toolbar()
        
        # Create theme assets directory structure
        theme_manager.create_theme_assets_structure()
        
    def create_menu_bar(self):
        menubar = self.menuBar()

        # ============================================================
        # FILE MENU
        # ============================================================
        file_menu = menubar.addMenu('File')

        # Import Data (Excel)
        import_action = QAction('Import Data (Excel)', self)
        import_action.triggered.connect(self.open_import_dialog)
        file_menu.addAction(import_action)

        # Export Data (Excel)
        export_action = QAction('Export Data (Excel)', self)
        export_action.triggered.connect(self.open_export_dialog)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        # Reset All Data
        reset_all_action = QAction('Reset All Data...', self)
        reset_all_action.triggered.connect(self.open_reset_all_dialog)
        file_menu.addAction(reset_all_action)

        file_menu.addSeparator()

        # Exit
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ============================================================
        # EDIT MENU
        # ============================================================
        edit_menu = menubar.addMenu('Edit')

        # Add Transaction
        add_transaction_action = QAction('Add Transaction', self)
        add_transaction_action.triggered.connect(self.open_add_transaction_dialog)
        edit_menu.addAction(add_transaction_action)

        # Add Paycheck
        add_paycheck_action = QAction('Add Paycheck', self)
        add_paycheck_action.triggered.connect(self.open_add_paycheck_dialog)
        edit_menu.addAction(add_paycheck_action)

        # Pay Bill
        pay_bill_action = QAction('Pay Bill', self)
        pay_bill_action.triggered.connect(self.open_pay_bill_dialog)
        edit_menu.addAction(pay_bill_action)

        # Transfer Money
        transfer_money_action = QAction('Transfer Money', self)
        transfer_money_action.triggered.connect(self.open_transfer_dialog)
        edit_menu.addAction(transfer_money_action)

        edit_menu.addSeparator()

        # Add Savings Account
        add_account_action = QAction('Add Savings Account', self)
        add_account_action.triggered.connect(self.open_add_account_dialog)
        edit_menu.addAction(add_account_action)

        # Add Bill Account
        add_bill_action = QAction('Add Bill Account', self)
        add_bill_action.triggered.connect(self.open_add_bill_dialog)
        edit_menu.addAction(add_bill_action)

        # ============================================================
        # VIEW MENU
        # ============================================================
        view_menu = menubar.addMenu('View')

        # Refresh All
        refresh_action = QAction('Refresh All', self)
        refresh_action.triggered.connect(self.refresh_all_views)
        view_menu.addAction(refresh_action)

        view_menu.addSeparator()

        # Tab navigation
        dashboard_action = QAction('Dashboard', self)
        dashboard_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        view_menu.addAction(dashboard_action)

        bills_action = QAction('Bills', self)
        bills_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        view_menu.addAction(bills_action)

        savings_action = QAction('Savings', self)
        savings_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        view_menu.addAction(savings_action)

        weekly_action = QAction('Weekly', self)
        weekly_action.triggered.connect(lambda: self.tabs.setCurrentIndex(3))
        view_menu.addAction(weekly_action)

        categories_action = QAction('Categories', self)
        categories_action.triggered.connect(lambda: self.tabs.setCurrentIndex(4))
        view_menu.addAction(categories_action)

        yearly_action = QAction('Yearly', self)
        yearly_action.triggered.connect(lambda: self.tabs.setCurrentIndex(5))
        view_menu.addAction(yearly_action)

        # ============================================================
        # TOOLS MENU
        # ============================================================
        tools_menu = menubar.addMenu('Tools')

        # Hour Calculator
        hour_calc_action = QAction('Hour Calculator...', self)
        hour_calc_action.triggered.connect(self.open_hour_calculator_dialog)
        tools_menu.addAction(hour_calc_action)

        # ============================================================
        # HELP MENU
        # ============================================================
        help_menu = menubar.addMenu('Help')

        # About Budget App
        about_action = QAction('About Budget App', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        # User Guide
        user_guide_action = QAction('User Guide', self)
        user_guide_action.triggered.connect(self.open_user_guide)
        help_menu.addAction(user_guide_action)

        help_menu.addSeparator()

        # Questions / FAQ
        faq_action = QAction('Questions / FAQ', self)
        faq_action.triggered.connect(self.show_faq_placeholder)
        help_menu.addAction(faq_action)

        # Report Bug
        report_bug_action = QAction('Report Bug', self)
        report_bug_action.triggered.connect(self.open_report_bug)
        help_menu.addAction(report_bug_action)
        
    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Store button references for theme updates
        self.toolbar_buttons = []

        # === Main Action Buttons ===
        # Add transaction button (PRIMARY focus - green in dark theme)
        add_transaction_btn = QPushButton("Add Transaction")
        add_transaction_btn.clicked.connect(self.open_add_transaction_dialog)
        add_transaction_btn.setFont(theme_manager.get_font("button"))
        self.toolbar_buttons.append(('primary', add_transaction_btn))
        toolbar.addWidget(add_transaction_btn)

        # Add paycheck button (SECONDARY focus - light blue in dark theme)
        add_paycheck_btn = QPushButton("Add Paycheck")
        add_paycheck_btn.clicked.connect(self.open_add_paycheck_dialog)
        add_paycheck_btn.setFont(theme_manager.get_font("button"))
        self.toolbar_buttons.append(('secondary', add_paycheck_btn))
        toolbar.addWidget(add_paycheck_btn)

        # Pay bill button (normal - unfocused)
        pay_bill_btn = QPushButton("Pay Bill")
        pay_bill_btn.clicked.connect(self.open_pay_bill_dialog)
        pay_bill_btn.setFont(theme_manager.get_font("button"))
        self.toolbar_buttons.append(('normal', pay_bill_btn))
        toolbar.addWidget(pay_bill_btn)

        # Transfer money button (normal - unfocused)
        transfer_btn = QPushButton("Transfer Money")
        transfer_btn.clicked.connect(self.open_transfer_dialog)
        transfer_btn.setFont(theme_manager.get_font("button"))
        self.toolbar_buttons.append(('normal', transfer_btn))
        toolbar.addWidget(transfer_btn)

        toolbar.addSeparator()

        # === Right Side Controls ===
        # Theme selector
        self.theme_selector = ThemeSelector()
        self.theme_selector.theme_changed.connect(self.on_theme_changed)
        toolbar.addWidget(self.theme_selector)

        # Settings button (gear icon only)
        settings_btn = QPushButton("⚙️")
        settings_btn.clicked.connect(self.open_settings_dialog)
        settings_btn.setFont(theme_manager.get_font("button_small"))
        settings_btn.setToolTip("Settings")
        self.toolbar_buttons.append(('small', settings_btn))
        toolbar.addWidget(settings_btn)

        # Refresh button (refresh emoji only - at the end)
        refresh_btn = QPushButton("🔄")
        refresh_btn.clicked.connect(self.refresh_all_views)
        refresh_btn.setFont(theme_manager.get_font("button_small"))
        refresh_btn.setToolTip("Refresh All")
        self.toolbar_buttons.append(('small', refresh_btn))
        toolbar.addWidget(refresh_btn)
        
        # Apply initial theme to toolbar buttons
        self.apply_toolbar_theme()
        
    def apply_toolbar_theme(self):
        """Apply theme colors to toolbar buttons"""
        if not hasattr(self, 'toolbar_buttons'):
            return
            
        colors = theme_manager.get_colors()
        
        for button_type, button in self.toolbar_buttons:
            if button_type == 'primary':
                # Primary action button (Add Paycheck)
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {colors['primary']};
                        color: {colors['background']};
                        border: 1px solid {colors['primary_dark']};
                        border-radius: 4px;
                        padding: 5px 10px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {colors['primary_dark']};
                    }}
                """)
            elif button_type == 'secondary':
                # Secondary action button (Pay Bill)
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {colors['secondary']};
                        color: {colors['background']};
                        border: 1px solid {colors['secondary']};
                        border-radius: 4px;
                        padding: 5px 10px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {colors['accent']};
                    }}
                """)
            elif button_type == 'small':
                # Small admin buttons
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {colors['surface_variant']};
                        color: {colors['text_secondary']};
                        border: 1px solid {colors['border']};
                        border-radius: 3px;
                        padding: 3px 8px;
                    }}
                    QPushButton:hover {{
                        background-color: {colors['hover']};
                        color: {colors['text_primary']};
                    }}
                """)
            else:  # 'normal'
                # Regular buttons
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {colors['surface']};
                        color: {colors['text_primary']};
                        border: 1px solid {colors['border']};
                        border-radius: 4px;
                        padding: 5px 10px;
                    }}
                    QPushButton:hover {{
                        background-color: {colors['hover']};
                    }}
                """)
        
    def refresh_all_views(self):
        """Refresh all tabs - called after any data change"""
        try:
            # Old rollover system removed - live rollover system handles everything now
            # self.paycheck_processor.check_and_process_rollovers()

            self.dashboard.refresh()
            self.bills_view.refresh()
            self.savings_view.refresh()
            self.weekly_view.refresh()
            self.categories_view.refresh()
            self.year_overview_view.refresh()

            # Refresh transactions view if enabled
            if self.transactions_tab_index >= 0:
                self.transactions_view.refresh()

            # Refresh taxes view if enabled
            if self.taxes_tab_index >= 0:
                self.taxes_view.refresh()
        except Exception as e:
            show_error(self, "Refresh Error", e, "refreshing application views")

    def on_tab_changed(self, index):
        """
        Handle tab change - refresh the newly selected tab

        ADDED: Nov 3, 2024
        Purpose: Ensure tabs always show latest data after changes in other tabs
        Example: Edit transaction in Transactions tab → switch to Bills tab → see updated line plot

        Performance Note: This triggers a full refresh on every tab switch.
        For optimization ideas, see Feature 4.4 in PROJECT_PLAN.md
        """
        try:
            # Map index to view and refresh it
            if index == 0:  # Dashboard
                self.dashboard.refresh()
            elif index == 1:  # Bills
                self.bills_view.refresh()
            elif index == 2:  # Savings
                self.savings_view.refresh()
            elif index == 3:  # Weekly
                self.weekly_view.refresh()
            elif index == 4:  # Categories
                self.categories_view.refresh()
            elif index == 5:  # Yearly
                self.year_overview_view.refresh()
            elif index == self.reimbursements_tab_index:  # Reimbursements
                self.reimbursements_view.refresh()
            elif index == self.transactions_tab_index and self.transactions_tab_index >= 0:
                self.transactions_view.refresh()
            elif index == self.taxes_tab_index and self.taxes_tab_index >= 0:
                self.taxes_view.refresh()
        except Exception as e:
            print(f"Error refreshing tab {index}: {e}")

    def open_add_transaction_dialog(self):
        """Open dialog to add new transaction"""
        try:
            dialog = AddTransactionDialog(self.transaction_manager, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_all_views()
        except Exception as e:
            show_error(self, "Dialog Error", e, "opening Add Transaction dialog")
    
    def open_add_paycheck_dialog(self):
        """Open dialog to add paycheck with bi-weekly processing"""
        try:
            dialog = AddPaycheckDialog(self.paycheck_processor, self.transaction_manager, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_all_views()
        except Exception as e:
            show_error(self, "Dialog Error", e, "opening Add Paycheck dialog")
    
    def open_pay_bill_dialog(self):
        """Open dialog to pay a bill"""
        try:
            dialog = PayBillDialog(self.transaction_manager, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_all_views()
        except Exception as e:
            show_error(self, "Dialog Error", e, "opening Pay Bill dialog")

    def open_transfer_dialog(self):
        """Open dialog to transfer money between accounts"""
        try:
            dialog = TransferDialog(self.transaction_manager, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_all_views()
        except Exception as e:
            show_error(self, "Dialog Error", e, "opening Transfer dialog")

    def open_add_account_dialog(self):
        """Open dialog to add new account (admin function)"""
        try:
            dialog = AddAccountDialog(self.transaction_manager, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_all_views()
        except Exception as e:
            show_error(self, "Dialog Error", e, "opening Add Account dialog")
    
    def open_add_bill_dialog(self):
        """Open dialog to add new bill (admin function)"""
        try:
            dialog = AddBillDialog(self.transaction_manager, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_all_views()
        except Exception as e:
            show_error(self, "Dialog Error", e, "opening Add Bill dialog")
    
    def open_settings_dialog(self):
        """Open settings dialog"""
        try:
            dialog = SettingsDialog(self.transaction_manager, self)
            dialog.settings_saved.connect(self.on_settings_saved)
            dialog.exec()
        except Exception as e:
            show_error(self, "Dialog Error", e, "opening Settings dialog")
    
    def on_settings_saved(self):
        """Handle when settings are saved"""
        # Reload settings
        old_tax_enabled = self.taxes_tab_index >= 0
        old_transactions_enabled = self.transactions_tab_index >= 0
        self.app_settings = load_app_settings()
        new_tax_enabled = self.app_settings.get("enable_tax_features", False) and TAX_MODULE_AVAILABLE
        new_transactions_enabled = self.app_settings.get("enable_transactions_tab", False)

        # Update transactions tab visibility if it changed
        if old_transactions_enabled != new_transactions_enabled:
            if new_transactions_enabled and self.transactions_view:
                # Add the Transactions tab (before Taxes if it exists)
                self.transactions_tab_index = self.tabs.addTab(self.transactions_view, "Transactions")
            else:
                # Remove the Transactions tab
                if self.transactions_tab_index >= 0:
                    self.tabs.removeTab(self.transactions_tab_index)
                    self.transactions_tab_index = -1

        # Update tax tab visibility if it changed
        if old_tax_enabled != new_tax_enabled:
            if new_tax_enabled and self.taxes_view:
                # Add the Taxes tab at the end
                self.taxes_tab_index = self.tabs.addTab(self.taxes_view, "Taxes")
            else:
                # Remove the Taxes tab
                if self.taxes_tab_index >= 0:
                    self.tabs.removeTab(self.taxes_tab_index)
                    self.taxes_tab_index = -1

        # Refresh all views to apply new sorting settings
        self.refresh_all_views()

    # ============================================================
    # FILE MENU HANDLERS
    # ============================================================

    def open_import_dialog(self):
        """Open import data dialog from settings"""
        try:
            # Create settings dialog and directly call import method
            settings_dialog = SettingsDialog(self.transaction_manager, self)
            settings_dialog.import_test_data()
            # Refresh after import
            self.refresh_all_views()
        except Exception as e:
            show_error(self, "Import Error", e, "importing data")

    def open_export_dialog(self):
        """Open export data dialog from settings"""
        try:
            # Create settings dialog and directly call export method
            settings_dialog = SettingsDialog(self.transaction_manager, self)
            settings_dialog.export_data()
        except Exception as e:
            show_error(self, "Export Error", e, "exporting data")

    def open_reset_all_dialog(self):
        """Open reset all data confirmation dialog"""
        try:
            # Create settings dialog and directly call reset method
            settings_dialog = SettingsDialog(self.transaction_manager, self)
            settings_dialog.confirm_reset_data()
            # Refresh after reset
            self.refresh_all_views()
        except Exception as e:
            show_error(self, "Reset Error", e, "resetting data")

    # ============================================================
    # TOOLS MENU HANDLERS
    # ============================================================

    def open_hour_calculator_dialog(self):
        """Open hour calculator dialog"""
        try:
            from views.dialogs.hour_calculator_dialog import HourCalculatorDialog
            dialog = HourCalculatorDialog(self.transaction_manager, self)
            dialog.exec()
        except Exception as e:
            show_error(self, "Dialog Error", e, "opening Hour Calculator dialog")

    # ============================================================
    # HELP MENU HANDLERS
    # ============================================================

    def show_about_dialog(self):
        """Show About Budget App dialog"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "About Budget App",
            "<h2>Budget App</h2>"
            "<p>Version 2.0</p>"
            "<p>A comprehensive budget tracking application with bi-weekly paycheck processing, "
            "bill management, savings goals, and detailed analytics.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Bi-weekly paycheck processing</li>"
            "<li>Bill tracking and payment history</li>"
            "<li>Savings account management</li>"
            "<li>Weekly spending analysis</li>"
            "<li>Category-based spending insights</li>"
            "<li>Yearly overview and trends</li>"
            "</ul>"
            "<p>Built with PyQt6 and SQLAlchemy</p>"
        )

    def open_user_guide(self):
        """Open user guide documentation"""
        import os
        import subprocess
        import sys

        readme_path = os.path.join(os.path.dirname(__file__), "readme2.txt")

        if os.path.exists(readme_path):
            try:
                if sys.platform == "win32":
                    os.startfile(readme_path)
                elif sys.platform == "darwin":
                    subprocess.run(["open", readme_path])
                else:
                    subprocess.run(["xdg-open", readme_path])
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    "Could Not Open Guide",
                    f"Could not open user guide:\n{str(e)}\n\nPlease open readme2.txt manually."
                )
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Guide Not Found",
                "User guide file (readme2.txt) not found."
            )

    def show_faq_placeholder(self):
        """Show FAQ placeholder - will be implemented later"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Questions / FAQ",
            "The FAQ and Questions section is coming soon!\n\n"
            "This will provide answers to common questions about using the Budget App."
        )

    def open_report_bug(self):
        """Open bug report page on GitHub"""
        import webbrowser
        # Open GitHub issues page
        webbrowser.open("https://github.com")
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Report a Bug",
            "Your browser has been opened to GitHub.\n\n"
            "Please report any bugs or issues you encounter."
        )
    
    def apply_theme(self):
        """Apply the current theme to the application"""
        stylesheet = theme_manager.get_stylesheet()
        self.setStyleSheet(stylesheet)
        
        # Apply theme-specific fonts
        title_font = theme_manager.get_font("title")
        self.setFont(theme_manager.get_font("main"))
        
    
    def on_theme_changed(self, theme_id):
        """Handle theme change"""
        self.apply_theme()
        
        # Apply theme to toolbar buttons
        self.apply_toolbar_theme()
        
        # Notify all views of theme change
        try:
            if hasattr(self.dashboard, 'on_theme_changed'):
                self.dashboard.on_theme_changed(theme_id)
            if hasattr(self.bills_view, 'on_theme_changed'):
                self.bills_view.on_theme_changed(theme_id)
            if hasattr(self.savings_view, 'on_theme_changed'):
                self.savings_view.on_theme_changed(theme_id)
            if hasattr(self.weekly_view, 'on_theme_changed'):
                self.weekly_view.on_theme_changed(theme_id)
            if hasattr(self.categories_view, 'on_theme_changed'):
                self.categories_view.on_theme_changed(theme_id)
            if hasattr(self.year_overview_view, 'on_theme_changed'):
                self.year_overview_view.on_theme_changed(theme_id)
            if hasattr(self.transactions_view, 'on_theme_changed'):
                self.transactions_view.on_theme_changed()
        except Exception as e:
            show_error(self, "Theme Error", e, "applying theme changes")
    
    def closeEvent(self, event):
        """Clean up resources when closing the application"""
        try:
            self.transaction_manager.close()
            self.analytics_engine.close()
            self.paycheck_processor.close()
        except Exception as e:
            # In testing mode, show technical error; otherwise silently continue
            if is_testing_mode():
                show_error(self, "Cleanup Error", e, "cleaning up resources")
        event.accept()


def main():
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Set up global exception handler
    def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
        # Get the main window if it exists
        window = None
        for widget in app.topLevelWidgets():
            if isinstance(widget, BudgetApp):
                window = widget
                break
        handle_exception(exc_type, exc_value, exc_traceback, window)

    sys.excepthook = handle_uncaught_exception

    window = BudgetApp()
    window.show()

    # Refresh all views after startup to ensure data loads properly
    window.refresh_all_views()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()