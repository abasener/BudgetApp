"""
Budget App - Desktop application for tracking expenses, bills, savings, and income
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, 
                             QWidget, QMenuBar, QMenu, QToolBar, QPushButton, QDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from views.dialogs.add_transaction_dialog import AddTransactionDialog
from views.dialogs.add_paycheck_dialog import AddPaycheckDialog
from views.dialogs.pay_bill_dialog import PayBillDialog
from views.dialogs.add_account_dialog import AddAccountDialog
from views.dialogs.add_bill_dialog import AddBillDialog

from views.dashboard import DashboardView
from views.bills_view import BillsView 
from views.weekly_view import WeeklyView
from services.transaction_manager import TransactionManager
from services.analytics import AnalyticsEngine
from services.paycheck_processor import PaycheckProcessor


class BudgetApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Budget App")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize services
        self.transaction_manager = TransactionManager()
        self.analytics_engine = AnalyticsEngine()
        self.paycheck_processor = PaycheckProcessor()
        
        self.init_ui()
        
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
        
        # Add tabs
        self.tabs.addTab(self.dashboard, "Dashboard")
        self.tabs.addTab(self.bills_view, "Bills")
        self.tabs.addTab(self.weekly_view, "Weekly")
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)
        
        # Create menu bar and toolbar
        self.create_menu_bar()
        self.create_toolbar()
        
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
        
        # Refresh button
        refresh_btn = QPushButton("Refresh All")
        refresh_btn.clicked.connect(self.refresh_all_views)
        refresh_btn.setStyleSheet("padding: 5px 10px;")
        toolbar.addWidget(refresh_btn)
        
        toolbar.addSeparator()
        
        # Add transaction button  
        add_transaction_btn = QPushButton("Add Transaction")
        add_transaction_btn.clicked.connect(self.open_add_transaction_dialog)
        add_transaction_btn.setStyleSheet("padding: 5px 10px; font-weight: bold;")
        toolbar.addWidget(add_transaction_btn)
        
        # Add paycheck button
        add_paycheck_btn = QPushButton("Add Paycheck")
        add_paycheck_btn.clicked.connect(self.open_add_paycheck_dialog)
        add_paycheck_btn.setStyleSheet("padding: 5px 10px; background-color: #4CAF50; color: white; font-weight: bold;")
        toolbar.addWidget(add_paycheck_btn)
        
        # Pay bill button
        pay_bill_btn = QPushButton("Pay Bill")
        pay_bill_btn.clicked.connect(self.open_pay_bill_dialog)
        pay_bill_btn.setStyleSheet("padding: 5px 10px; background-color: #FF9800; color: white; font-weight: bold;")
        toolbar.addWidget(pay_bill_btn)
        
        toolbar.addSeparator()
        
        # Admin buttons (less prominent)
        add_account_btn = QPushButton("+ Account")
        add_account_btn.clicked.connect(self.open_add_account_dialog)
        add_account_btn.setStyleSheet("padding: 3px 8px; font-size: 11px;")
        toolbar.addWidget(add_account_btn)
        
        add_bill_btn = QPushButton("+ Bill")
        add_bill_btn.clicked.connect(self.open_add_bill_dialog)
        add_bill_btn.setStyleSheet("padding: 3px 8px; font-size: 11px;")
        toolbar.addWidget(add_bill_btn)
        
    def refresh_all_views(self):
        """Refresh all tabs - called after any data change"""
        print("Refreshing all views...")
        try:
            self.dashboard.refresh()
            self.bills_view.refresh()
            self.weekly_view.refresh()
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
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()