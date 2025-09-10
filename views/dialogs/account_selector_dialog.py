"""
Account Selector Dialog - Choose accounts/bills for savings rate plots
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QLabel, QPushButton, QListWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal
from themes import theme_manager


class AccountSelectorDialog(QDialog):
    """Dialog for selecting accounts or bills for savings rate plots"""
    
    # Signal emitted when account is selected (but dialog stays open)
    account_selected = pyqtSignal(str, object, str)  # type, account_obj, name
    
    def __init__(self, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager
        self.selected_account = None
        self.selected_type = None  # 'account' or 'bill'
        
        self.setWindowTitle("Select Account or Bill")
        self.setModal(True)
        self.resize(400, 300)
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Select Account or Bill to Track:")
        title.setFont(theme_manager.get_font("subtitle"))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Lists container
        lists_layout = QHBoxLayout()
        
        # Bills section
        bills_layout = QVBoxLayout()
        bills_label = QLabel("Bills:")
        bills_label.setFont(theme_manager.get_font("subtitle"))
        bills_layout.addWidget(bills_label)
        
        self.bills_list = QListWidget()
        self.bills_list.itemClicked.connect(self.on_bill_selected)
        bills_layout.addWidget(self.bills_list)
        
        # Accounts section  
        accounts_layout = QVBoxLayout()
        accounts_label = QLabel("Savings Accounts:")
        accounts_label.setFont(theme_manager.get_font("subtitle"))
        accounts_layout.addWidget(accounts_label)
        
        self.accounts_list = QListWidget()
        self.accounts_list.itemClicked.connect(self.on_account_selected)
        accounts_layout.addWidget(self.accounts_list)
        
        lists_layout.addLayout(bills_layout)
        lists_layout.addLayout(accounts_layout)
        layout.addLayout(lists_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.select_button = QPushButton("Select Account")
        self.select_button.clicked.connect(self.on_select_clicked)
        self.select_button.setEnabled(False)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Apply theme
        self.apply_theme()
    
    def apply_theme(self):
        colors = theme_manager.get_colors()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['surface']};
                color: {colors['text_primary']};
            }}
            QListWidget {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                color: {colors['text_primary']};
            }}
            QListWidget::item {{
                padding: 4px;
                border-bottom: 1px solid {colors['border']};
            }}
            QListWidget::item:selected {{
                background-color: {colors['primary']};
                color: {colors['surface']};
            }}
            QPushButton {{
                background-color: {colors['primary']};
                color: {colors['surface']};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {colors['border']};
            }}
            QPushButton:disabled {{
                background-color: {colors['surface_variant']};
                color: {colors['text_secondary']};
            }}
        """)
    
    def load_data(self):
        # Load bills
        try:
            bills = self.transaction_manager.get_all_bills()
            for bill in bills:
                item = QListWidgetItem(bill.name)
                item.setData(Qt.ItemDataRole.UserRole, ('bill', bill))
                self.bills_list.addItem(item)
        except Exception as e:
            print(f"Error loading bills: {e}")
        
        # Load accounts
        try:
            accounts = self.transaction_manager.get_all_accounts()
            for account in accounts:
                item = QListWidgetItem(account.name)
                item.setData(Qt.ItemDataRole.UserRole, ('account', account))
                self.accounts_list.addItem(item)
        except Exception as e:
            print(f"Error loading accounts: {e}")
    
    def on_bill_selected(self, item):
        # Clear account selection
        self.accounts_list.clearSelection()
        
        # Set selection
        item_type, bill = item.data(Qt.ItemDataRole.UserRole)
        self.selected_account = bill
        self.selected_type = 'bill'
        self.select_button.setEnabled(True)
    
    def on_account_selected(self, item):
        # Clear bills selection
        self.bills_list.clearSelection()
        
        # Set selection
        item_type, account = item.data(Qt.ItemDataRole.UserRole)
        self.selected_account = account
        self.selected_type = 'account'
        self.select_button.setEnabled(True)
    
    def on_select_clicked(self):
        """Handle select button click - emit signal but keep dialog open"""
        if self.selected_account:
            # Emit signal with selection data
            self.account_selected.emit(self.selected_type, self.selected_account, self.selected_account.name)
    
    def get_selected_account(self):
        """Return (type, account_obj, name) tuple"""
        if self.selected_account:
            return (self.selected_type, self.selected_account, self.selected_account.name)
        return None