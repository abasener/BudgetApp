"""
Budget App - Desktop application for tracking expenses, bills, savings, and income

"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, 
                             QWidget, QMenuBar, QMenu, QToolBar, QPushButton, QDialog, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from views.dialogs.add_transaction_dialog import AddTransactionDialog
from views.dialogs.add_paycheck_dialog import AddPaycheckDialog
from views.dialogs.pay_bill_dialog import PayBillDialog
from views.dialogs.add_account_dialog import AddAccountDialog
from views.dialogs.add_bill_dialog import AddBillDialog
from views.dialogs.settings_dialog import SettingsDialog, load_app_settings

from views.dashboard import DashboardView
from views.bills_view import BillsView 
from views.weekly_view import WeeklyView
from views.savings_view import SavingsView
from views.categories_view import CategoriesView
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
        
        # Add tabs
        self.tabs.addTab(self.dashboard, "Dashboard")
        self.tabs.addTab(self.bills_view, "Bills")
        self.tabs.addTab(self.savings_view, "Savings")
        self.tabs.addTab(self.weekly_view, "Weekly")
        self.tabs.addTab(self.categories_view, "Categories")
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)
        
        # Create menu bar and toolbar
        self.create_menu_bar()
        self.create_toolbar()
        
        # Create theme assets directory structure
        theme_manager.create_theme_assets_structure()
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Add transaction action
        add_transaction_action = QAction('Add Transaction', self)
        add_transaction_action.triggered.connect(self.open_add_transaction_dialog)
        file_menu.addAction(add_transaction_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        refresh_action = QAction('Refresh All', self)
        refresh_action.triggered.connect(self.refresh_all_views)
        tools_menu.addAction(refresh_action)
        
        tools_menu.addSeparator()
        
        # Add paycheck action
        add_paycheck_action = QAction('Add Paycheck', self)
        add_paycheck_action.triggered.connect(self.open_add_paycheck_dialog)
        tools_menu.addAction(add_paycheck_action)
        
        # Pay bill action
        pay_bill_action = QAction('Pay Bill', self)
        pay_bill_action.triggered.connect(self.open_pay_bill_dialog)
        tools_menu.addAction(pay_bill_action)
        
        # Admin menu
        admin_menu = menubar.addMenu('Admin')
        
        add_account_action = QAction('Add Account', self)
        add_account_action.triggered.connect(self.open_add_account_dialog)
        admin_menu.addAction(add_account_action)
        
        add_bill_action = QAction('Add Bill', self)
        add_bill_action.triggered.connect(self.open_add_bill_dialog)
        admin_menu.addAction(add_bill_action)
        
    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Store button references for theme updates
        self.toolbar_buttons = []
        
        # Refresh button
        refresh_btn = QPushButton("Refresh All")
        refresh_btn.clicked.connect(self.refresh_all_views)
        refresh_btn.setFont(theme_manager.get_font("button"))
        self.toolbar_buttons.append(('normal', refresh_btn))
        toolbar.addWidget(refresh_btn)
        
        toolbar.addSeparator()
        
        # Add transaction button  
        add_transaction_btn = QPushButton("Add Transaction")
        add_transaction_btn.clicked.connect(self.open_add_transaction_dialog)
        add_transaction_btn.setFont(theme_manager.get_font("button"))
        self.toolbar_buttons.append(('normal', add_transaction_btn))
        toolbar.addWidget(add_transaction_btn)
        
        # Add paycheck button (primary accent)
        add_paycheck_btn = QPushButton("Add Paycheck")
        add_paycheck_btn.clicked.connect(self.open_add_paycheck_dialog)
        add_paycheck_btn.setFont(theme_manager.get_font("button"))
        self.toolbar_buttons.append(('primary', add_paycheck_btn))
        toolbar.addWidget(add_paycheck_btn)
        
        # Pay bill button (secondary accent)
        pay_bill_btn = QPushButton("Pay Bill")
        pay_bill_btn.clicked.connect(self.open_pay_bill_dialog)
        pay_bill_btn.setFont(theme_manager.get_font("button"))
        self.toolbar_buttons.append(('secondary', pay_bill_btn))
        toolbar.addWidget(pay_bill_btn)
        
        toolbar.addSeparator()
        
        # Admin buttons (less prominent)
        add_account_btn = QPushButton("+ Account")
        add_account_btn.clicked.connect(self.open_add_account_dialog)
        add_account_btn.setFont(theme_manager.get_font("button_small"))
        self.toolbar_buttons.append(('small', add_account_btn))
        toolbar.addWidget(add_account_btn)
        
        add_bill_btn = QPushButton("+ Bill")
        add_bill_btn.clicked.connect(self.open_add_bill_dialog)
        add_bill_btn.setFont(theme_manager.get_font("button_small"))
        self.toolbar_buttons.append(('small', add_bill_btn))
        toolbar.addWidget(add_bill_btn)
        
        toolbar.addSeparator()
        
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
        print("Refreshing all views...")
        try:
            # Check for and process any pending rollovers before refreshing views
            self.paycheck_processor.check_and_process_rollovers()
            
            self.dashboard.refresh()
            self.bills_view.refresh()
            self.savings_view.refresh()
            self.weekly_view.refresh()
            self.categories_view.refresh()
            print("All views refreshed successfully")
        except Exception as e:
            print(f"Error refreshing views: {e}")
        
    def open_add_transaction_dialog(self):
        """Open dialog to add new transaction"""
        try:
            dialog = AddTransactionDialog(self.transaction_manager, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_all_views()
        except Exception as e:
            print(f"Error opening add transaction dialog: {e}")
    
    def open_add_paycheck_dialog(self):
        """Open dialog to add paycheck with bi-weekly processing"""
        try:
            dialog = AddPaycheckDialog(self.paycheck_processor, self.transaction_manager, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_all_views()
        except Exception as e:
            print(f"Error opening add paycheck dialog: {e}")
    
    def open_pay_bill_dialog(self):
        """Open dialog to pay a bill"""
        try:
            dialog = PayBillDialog(self.transaction_manager, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_all_views()
        except Exception as e:
            print(f"Error opening pay bill dialog: {e}")
    
    def open_add_account_dialog(self):
        """Open dialog to add new account (admin function)"""
        try:
            dialog = AddAccountDialog(self.transaction_manager, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_all_views()
        except Exception as e:
            print(f"Error opening add account dialog: {e}")
    
    def open_add_bill_dialog(self):
        """Open dialog to add new bill (admin function)"""
        try:
            dialog = AddBillDialog(self.transaction_manager, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_all_views()
        except Exception as e:
            print(f"Error opening add bill dialog: {e}")
    
    def open_settings_dialog(self):
        """Open settings dialog"""
        try:
            dialog = SettingsDialog(self.transaction_manager, self)
            dialog.settings_saved.connect(self.on_settings_saved)
            dialog.exec()
        except Exception as e:
            print(f"Error opening settings dialog: {e}")
    
    def on_settings_saved(self):
        """Handle when settings are saved"""
        # Reload settings
        self.app_settings = load_app_settings()
        # Refresh all views to apply new sorting settings
        self.refresh_all_views()
    
    def apply_theme(self):
        """Apply the current theme to the application"""
        stylesheet = theme_manager.get_stylesheet()
        self.setStyleSheet(stylesheet)
        
        # Apply theme-specific fonts
        title_font = theme_manager.get_font("title")
        self.setFont(theme_manager.get_font("main"))
        
        print(f"Applied theme: {theme_manager.themes[theme_manager.current_theme]['name']}")
    
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
        except Exception as e:
            print(f"Error applying theme to views: {e}")
    
    def closeEvent(self, event):
        """Clean up resources when closing the application"""
        try:
            self.transaction_manager.close()
            self.analytics_engine.close()
            self.paycheck_processor.close()
        except:
            pass  # Ignore cleanup errors
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = BudgetApp()
    window.show()
    
    # Refresh all views after startup to ensure data loads properly
    window.refresh_all_views()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()