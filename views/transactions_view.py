"""
Transactions View - Advanced data inspection and debugging interface
Shows all transactions organized by type (Bills, Savings, Paycheck, Spending)
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QLineEdit, QPushButton, QLabel)
from PyQt6.QtCore import Qt
from themes import theme_manager
from views.transactions_table_widget import TransactionTableWidget


class TransactionsView(QWidget):
    """
    Main Transactions tab with 4 sub-tabs for different transaction types
    Provides advanced search, filtering, and bulk editing capabilities
    """

    def __init__(self, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager

        # Track which sub-tab is currently active
        self.current_subtab = "bills"

        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        """Initialize the UI with sub-tabs and controls"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create sub-tabs widget
        self.sub_tabs = QTabWidget()
        self.sub_tabs.currentChanged.connect(self.on_subtab_changed)

        # Create each sub-tab
        self.bills_tab = self.create_subtab_widget("Bills")
        self.savings_tab = self.create_subtab_widget("Savings")
        self.paycheck_tab = self.create_subtab_widget("Paycheck")
        self.spending_tab = self.create_subtab_widget("Spending")

        # Add sub-tabs
        self.sub_tabs.addTab(self.bills_tab, "Bills")
        self.sub_tabs.addTab(self.savings_tab, "Savings")
        self.sub_tabs.addTab(self.paycheck_tab, "Paycheck")
        self.sub_tabs.addTab(self.spending_tab, "Spending")

        main_layout.addWidget(self.sub_tabs)
        self.setLayout(main_layout)

    def create_subtab_widget(self, tab_name):
        """
        Create a sub-tab widget with search bar, table, and action buttons

        Args:
            tab_name: Name of the tab ("Bills", "Savings", etc.)

        Returns:
            QWidget configured for this sub-tab
        """
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Top bar with search and action buttons
        top_bar = QHBoxLayout()

        # Search bar
        search_label = QLabel("🔍 Search:")
        search_label.setFont(theme_manager.get_font("main"))

        search_input = QLineEdit()
        search_input.setPlaceholderText(f"Search {tab_name.lower()} transactions...")
        search_input.setFont(theme_manager.get_font("main"))
        search_input.setClearButtonEnabled(True)
        search_input.textChanged.connect(lambda text: self.on_search_changed(tab_name.lower(), text))

        # Store search input for later reference
        setattr(self, f"{tab_name.lower()}_search_input", search_input)

        top_bar.addWidget(search_label)
        top_bar.addWidget(search_input, 1)  # Stretch factor of 1

        # Delete button
        delete_btn = QPushButton("Delete Selected")
        delete_btn.setFont(theme_manager.get_font("button"))
        delete_btn.clicked.connect(lambda: self.on_delete_clicked(tab_name.lower()))
        setattr(self, f"{tab_name.lower()}_delete_btn", delete_btn)
        top_bar.addWidget(delete_btn)

        # Save button
        save_btn = QPushButton("Save Changes")
        save_btn.setFont(theme_manager.get_font("button"))
        save_btn.clicked.connect(lambda: self.on_save_clicked(tab_name.lower()))
        setattr(self, f"{tab_name.lower()}_save_btn", save_btn)
        top_bar.addWidget(save_btn)

        layout.addLayout(top_bar)

        # Create table widget
        table = TransactionTableWidget()

        # Store table for later reference
        setattr(self, f"{tab_name.lower()}_table", table)

        # Load initial data (will be replaced with real data in refresh)
        # For now, use test data for non-bills tabs
        if tab_name.lower() == "bills":
            # Bills tab will load real data in refresh()
            pass
        else:
            self.load_test_data(tab_name.lower(), table)

        layout.addWidget(table)

        widget.setLayout(layout)
        return widget

    def on_subtab_changed(self, index):
        """Handle sub-tab change"""
        tab_names = ["bills", "savings", "paycheck", "spending"]
        if 0 <= index < len(tab_names):
            self.current_subtab = tab_names[index]

    def load_test_data(self, tab_name, table):
        """Load test data for demonstration (will be replaced with real data in Phase 4-7)"""
        # Define columns based on tab type
        # Note: 🔒 column moved before notes so notes can stretch
        if tab_name == "bills":
            columns = ["Date", "Account", "Amount", "🔒", "Manual Notes", "Auto Notes"]
            test_data = [
                {"Date": "10/28/2024", "Account": "Internet", "Amount": "$65.00", "🔒": "",
                 "Manual Notes": "October bill", "Auto Notes": "Manual: Bill payment"},
                {"Date": "10/25/2024", "Account": "Rent", "Amount": "$1200.00", "🔒": "🔒",
                 "Manual Notes": "Monthly rent", "Auto Notes": "Generated: Auto saved from payweek 30"},
                {"Date": "10/21/2024", "Account": "Internet", "Amount": "$100.00", "🔒": "🔒",
                 "Manual Notes": "", "Auto Notes": "Generated: Auto saved from payweek 30"},
            ]
            locked_rows = {1, 2}  # Rows 1 and 2 are locked
        elif tab_name == "savings":
            columns = ["Date", "Account", "Amount", "🔒", "Manual Notes", "Auto Notes"]
            test_data = [
                {"Date": "10/28/2024", "Account": "Emergency Fund", "Amount": "$500.00", "🔒": "",
                 "Manual Notes": "Emergency deposit", "Auto Notes": "Manual: Transfer from checking"},
                {"Date": "10/27/2024", "Account": "Emergency Fund", "Amount": "$767.22", "🔒": "🔒",
                 "Manual Notes": "", "Auto Notes": "Generated: Rollover into Emergency Fund from payweek 30"},
                {"Date": "10/21/2024", "Account": "Vacation", "Amount": "$200.00", "🔒": "",
                 "Manual Notes": "Save for trip", "Auto Notes": "Manual: Vacation savings"},
            ]
            locked_rows = {1}  # Row 1 is locked (rollover)
        elif tab_name == "paycheck":
            columns = ["Earned Date", "Start Date", "Amount", "🔒", "Manual Notes", "Auto Notes"]
            test_data = [
                {"Earned Date": "10/15/2024", "Start Date": "10/21/2024", "Amount": "$4237.50", "🔒": "🔒",
                 "Manual Notes": "Bi-weekly paycheck", "Auto Notes": "Generated: Paycheck 30"},
                {"Earned Date": "10/01/2024", "Start Date": "10/07/2024", "Amount": "$4237.50", "🔒": "🔒",
                 "Manual Notes": "Bi-weekly paycheck", "Auto Notes": "Generated: Paycheck 29"},
            ]
            locked_rows = {0, 1}  # All paychecks are locked
        else:  # spending
            columns = ["Date", "Category", "Amount", "Paycheck #", "Week", "🔒", "Abnormal", "Manual Notes", "Auto Notes"]
            test_data = [
                {"Date": "10/28/2024", "Category": "Groceries", "Amount": "$45.67", "Paycheck #": "30",
                 "Week": "second", "🔒": "", "Abnormal": "",
                 "Manual Notes": "Walmart", "Auto Notes": "Manual: Spending for payweek 30 week 2"},
                {"Date": "10/27/2024", "Category": "Rollover", "Amount": "$312.76", "Paycheck #": "30",
                 "Week": "first", "🔒": "🔒", "Abnormal": "",
                 "Manual Notes": "", "Auto Notes": "Generated: Rollover into second week (Week 60) from first week (Week 59) in payweek 30"},
                {"Date": "10/26/2024", "Category": "Gas", "Amount": "$35.00", "Paycheck #": "30",
                 "Week": "first", "🔒": "", "Abnormal": "",
                 "Manual Notes": "Shell", "Auto Notes": "Manual: Spending for payweek 30 week 1"},
                {"Date": "10/25/2024", "Category": "Coffee", "Amount": "$5.50", "Paycheck #": "30",
                 "Week": "first", "🔒": "", "Abnormal": "☑",
                 "Manual Notes": "Starbucks", "Auto Notes": "Manual: Spending for payweek 30 week 1"},
            ]
            locked_rows = {1}  # Rollover is locked

        # Set columns and load data
        table.set_columns(columns)
        table.load_data(test_data, locked_rows)

    def load_bills_data(self):
        """Load real bills transaction data from database"""
        from models.transactions import TransactionType

        # Get all transactions that affect bills
        # 1. BILL_PAY transactions (payments from bill accounts)
        # 2. SAVING transactions with bill_id (deposits to bill accounts)
        transactions = self.transaction_manager.session.query(
            self.transaction_manager.transaction_class
        ).filter(
            (self.transaction_manager.transaction_class.transaction_type == TransactionType.BILL_PAY.value) |
            ((self.transaction_manager.transaction_class.transaction_type == TransactionType.SAVING.value) &
             (self.transaction_manager.transaction_class.bill_id.isnot(None)))
        ).order_by(self.transaction_manager.transaction_class.date.asc()).all()

        # Get bill names lookup
        bills = self.transaction_manager.session.query(
            self.transaction_manager.bill_class
        ).all()
        bill_names = {bill.id: bill.name for bill in bills}

        # Convert to table format
        rows_data = []
        locked_rows = set()

        for idx, trans in enumerate(transactions):
            # Get bill name
            bill_name = bill_names.get(trans.bill_id, "Unknown")

            # Determine if locked (auto-generated transactions)
            is_locked = self.is_transaction_locked(trans)
            if is_locked:
                locked_rows.add(idx)

            # Generate auto-notes
            auto_notes = self.generate_auto_notes(trans)

            row = {
                "Date": trans.date.strftime("%m/%d/%Y"),
                "Account": bill_name,
                "Amount": f"${trans.amount:,.2f}",
                "🔒": "🔒" if is_locked else "",
                "Manual Notes": trans.description or "",
                "Auto Notes": auto_notes
            }
            rows_data.append(row)

        # Set columns and load data
        columns = ["Date", "Account", "Amount", "🔒", "Manual Notes", "Auto Notes"]
        table = getattr(self, "bills_table", None)
        if table:
            table.set_columns(columns)
            table.load_data(rows_data, locked_rows)

    def is_transaction_locked(self, transaction):
        """Determine if a transaction should be locked (non-editable)"""
        from models.transactions import TransactionType

        # Always locked transaction types
        if transaction.transaction_type in [TransactionType.ROLLOVER.value, TransactionType.INCOME.value]:
            return True

        # SAVING transactions are locked if auto-generated from paycheck
        if transaction.transaction_type == TransactionType.SAVING.value:
            # Check if description indicates auto-generation
            if transaction.description and "auto saved" in transaction.description.lower():
                return True

        return False

    def generate_auto_notes(self, transaction):
        """Generate auto-notes for a transaction"""
        from models.transactions import TransactionType

        # Determine if manual or generated
        is_manual = not self.is_transaction_locked(transaction)
        prefix = "Manual:" if is_manual else "Generated:"

        # Generate description based on type
        if transaction.transaction_type == TransactionType.BILL_PAY.value:
            return f"{prefix} Bill payment"

        elif transaction.transaction_type == TransactionType.SAVING.value:
            # Check if it's an auto-save from paycheck
            if transaction.description and "auto saved" in transaction.description.lower():
                # Extract payweek number from week_number
                payweek = (transaction.week_number + 1) // 2 if transaction.week_number else "?"
                return f"{prefix} Auto saved from payweek {payweek}"
            else:
                return f"{prefix} Manual deposit"

        return f"{prefix} Transaction"

    def on_search_changed(self, tab_name, search_text):
        """Handle search text change"""
        table = getattr(self, f"{tab_name}_table", None)
        if table:
            table.filter_by_search(search_text)

    def on_delete_clicked(self, tab_name):
        """Handle delete button click"""
        table = getattr(self, f"{tab_name}_table", None)
        if table:
            count = table.mark_selected_for_deletion()
            if count:
                print(f"Marked {count} row(s) for deletion in {tab_name}")

    def on_save_clicked(self, tab_name):
        """Handle save button click"""
        # Will implement in Phase 8
        print(f"Save clicked for {tab_name}")

    def refresh(self):
        """Refresh all sub-tabs with real data"""
        try:
            # Load bills data (Phase 4)
            self.load_bills_data()

            # TODO: Phase 5-7 - Load other tabs
            # self.load_savings_data()
            # self.load_paycheck_data()
            # self.load_spending_data()

        except Exception as e:
            print(f"Error refreshing transactions view: {e}")
            import traceback
            traceback.print_exc()

    def on_theme_changed(self):
        """Handle theme changes"""
        self.apply_theme()

    def apply_theme(self):
        """Apply current theme to all UI elements"""
        colors = theme_manager.get_colors()

        # Style the main widget
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['background']};
                color: {colors['text_primary']};
            }}
        """)

        # Style sub-tabs
        if hasattr(self, 'sub_tabs'):
            self.sub_tabs.setStyleSheet(f"""
                QTabWidget::pane {{
                    border: 1px solid {colors['border']};
                    background-color: {colors['surface']};
                    border-radius: 4px;
                }}
                QTabBar::tab {{
                    background-color: {colors['surface_variant']};
                    color: {colors['text_secondary']};
                    padding: 8px 16px;
                    margin-right: 2px;
                    border: 1px solid {colors['border']};
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }}
                QTabBar::tab:selected {{
                    background-color: {colors['surface']};
                    color: {colors['text_primary']};
                    font-weight: bold;
                }}
                QTabBar::tab:hover {{
                    background-color: {colors['hover']};
                }}
            """)

        # Style search inputs
        for tab_name in ["bills", "savings", "paycheck", "spending"]:
            search_input = getattr(self, f"{tab_name}_search_input", None)
            if search_input:
                search_input.setStyleSheet(f"""
                    QLineEdit {{
                        background-color: {colors['surface']};
                        color: {colors['text_primary']};
                        border: 1px solid {colors['border']};
                        border-radius: 4px;
                        padding: 6px;
                    }}
                    QLineEdit:focus {{
                        border-color: {colors['primary']};
                    }}
                """)

        # Style buttons (Delete = normal, Save = primary)
        for tab_name in ["bills", "savings", "paycheck", "spending"]:
            delete_btn = getattr(self, f"{tab_name}_delete_btn", None)
            save_btn = getattr(self, f"{tab_name}_save_btn", None)

            if delete_btn:
                delete_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {colors['surface']};
                        color: {colors['text_primary']};
                        border: 1px solid {colors['border']};
                        border-radius: 4px;
                        padding: 6px 12px;
                    }}
                    QPushButton:hover {{
                        background-color: {colors['hover']};
                    }}
                    QPushButton:pressed {{
                        background-color: {colors['selected']};
                    }}
                """)

            if save_btn:
                save_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {colors['primary']};
                        color: {colors['text_primary']};
                        border: 1px solid {colors['border']};
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
