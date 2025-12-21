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
        # Note: "Accounts" combines Bills + Savings history
        # "Transfers" shows Week<->Account and Account<->Account transfers
        self.accounts_tab = self.create_subtab_widget("Accounts")
        self.paycheck_tab = self.create_subtab_widget("Paycheck")
        self.spending_tab = self.create_subtab_widget("Spending")
        self.transfers_tab = self.create_subtab_widget("Transfers")

        # Add sub-tabs
        self.sub_tabs.addTab(self.accounts_tab, "Accounts")
        self.sub_tabs.addTab(self.paycheck_tab, "Paycheck")
        self.sub_tabs.addTab(self.spending_tab, "Spending")
        self.sub_tabs.addTab(self.transfers_tab, "Transfers")

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
        # All tabs now load real data in refresh()
        pass

        layout.addWidget(table)

        widget.setLayout(layout)
        return widget

    def on_subtab_changed(self, index):
        """Handle sub-tab change"""
        tab_names = ["accounts", "paycheck", "spending", "transfers"]
        if 0 <= index < len(tab_names):
            # Clear change tracking from ALL tabs when switching
            for tab_name in tab_names:
                table = getattr(self, f"{tab_name}_table", None)
                if table:
                    table.clear_change_tracking()

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

    def load_accounts_data(self):
        """
        Load merged Bills + Savings account history data.
        This shows all AccountHistory entries for both bill and savings accounts.
        """
        from models.account_history import AccountHistory, AccountHistoryManager
        from models.transactions import Transaction

        history_manager = AccountHistoryManager(self.transaction_manager.db)
        all_history_entries = []

        # Get all bills and their history
        bills = self.transaction_manager.get_all_bills()
        for bill in bills:
            bill_history = history_manager.get_account_history(bill.id, "bill")
            for entry in bill_history:
                # Skip starting balance entries (they have no transaction_id)
                if entry.transaction_id is not None:
                    all_history_entries.append((entry, bill.name, "Bill"))

        # Get all savings accounts and their history
        accounts = self.transaction_manager.get_all_accounts()
        for account in accounts:
            account_history = history_manager.get_account_history(account.id, "savings")
            for entry in account_history:
                # Skip starting balance entries (they have no transaction_id)
                if entry.transaction_id is not None:
                    all_history_entries.append((entry, account.name, "Savings"))

        # Sort by date (oldest first)
        all_history_entries.sort(key=lambda x: x[0].transaction_date)

        # Convert to table format
        rows_data = []
        locked_rows = set()
        transaction_ids = {}  # Map row index -> transaction ID
        row_idx = 0

        for history_entry, account_name, account_type in all_history_entries:
            # Get the associated transaction for description and locking logic
            trans = self.transaction_manager.db.query(Transaction).filter_by(id=history_entry.transaction_id).first()
            if not trans:
                continue

            # Store transaction ID for saving changes
            transaction_ids[row_idx] = trans.id

            # Determine if locked (auto-generated transactions)
            is_locked = self.is_transaction_locked(trans)
            if is_locked:
                locked_rows.add(row_idx)

            # Format amount with proper sign display (use change_amount from AccountHistory)
            amount_value = history_entry.change_amount

            # Generate auto-notes (pass amount for deposit/withdrawal detection)
            auto_notes = self.generate_auto_notes(trans, amount_value)
            if amount_value >= 0:
                amount_display = f"${amount_value:,.2f}"
            else:
                amount_display = f"-${abs(amount_value):,.2f}"

            row = {
                "ID": str(trans.id),
                "Date": history_entry.transaction_date.strftime("%m/%d/%Y"),
                "Account": account_name,
                "Acct Type": account_type,
                "Amount": amount_display,
                "Type": trans.transaction_type or "",
                "Week": str(trans.week_number) if trans.week_number else "",
                "🔒": "🔒" if is_locked else "",
                "Manual Notes": trans.description or "",
                "Auto Notes": auto_notes
            }
            rows_data.append(row)
            row_idx += 1

        # Set columns and load data
        columns = ["ID", "Date", "Account", "Acct Type", "Amount", "Type", "Week", "🔒", "Manual Notes", "Auto Notes"]
        table = getattr(self, "accounts_table", None)
        if table:
            table.set_columns(columns)
            table.load_data(rows_data, locked_rows, transaction_ids)

    def load_paycheck_data(self):
        """Load real paycheck transaction data from database"""
        from models.transactions import Transaction, TransactionType

        # Get all INCOME transactions (paychecks)
        all_transactions = self.transaction_manager.get_all_transactions()
        paychecks = [
            t for t in all_transactions
            if t.transaction_type == TransactionType.INCOME.value
        ]

        # Sort by date (oldest first)
        paychecks.sort(key=lambda t: t.date)

        # Get week information for start/end dates
        all_weeks = self.transaction_manager.get_all_weeks()
        weeks_by_number = {week.week_number: week for week in all_weeks}

        # Convert to table format
        rows_data = []
        locked_rows = set()
        transaction_ids = {}  # Map row index -> transaction ID

        for idx, paycheck in enumerate(paychecks):
            # Store transaction ID for saving changes
            transaction_ids[idx] = paycheck.id

            # Check if locked using standard logic (paychecks are now editable!)
            is_locked = self.is_transaction_locked(paycheck)
            if is_locked:
                locked_rows.add(idx)

            # Get the week for start date and paycheck number
            week = weeks_by_number.get(paycheck.week_number)
            if week:
                start_date = week.start_date
                end_date = week.end_date
                # Calculate paycheck number from week number
                payweek = (paycheck.week_number + 1) // 2
            else:
                # Fallback if week not found
                start_date = paycheck.date
                end_date = paycheck.date
                payweek = "?"

            # Generate auto-notes with date range
            # Note: Paychecks are user-entered, so they're "Manual" not "Generated"
            auto_notes = f"Manual: Paycheck {payweek} for {start_date.strftime('%m/%d/%Y')} to {end_date.strftime('%m/%d/%Y')}"

            # Format amount (paychecks are always positive)
            amount_value = paycheck.amount
            amount_display = f"${amount_value:,.2f}"

            row = {
                "ID": str(paycheck.id),
                "Earned Date": paycheck.date.strftime("%m/%d/%Y"),
                "Start Date": start_date.strftime("%m/%d/%Y"),
                "Amount": amount_display,
                "Type": paycheck.transaction_type or "",
                "Week": str(paycheck.week_number) if paycheck.week_number else "",
                "🔒": "🔒" if is_locked else "",
                "Manual Notes": paycheck.description or "",
                "Auto Notes": auto_notes
            }
            rows_data.append(row)

        # Set columns and load data
        columns = ["ID", "Earned Date", "Start Date", "Amount", "Type", "Week", "🔒", "Manual Notes", "Auto Notes"]
        table = getattr(self, "paycheck_table", None)
        if table:
            table.set_columns(columns)
            table.load_data(rows_data, locked_rows, transaction_ids)

    def load_spending_data(self):
        """Load real spending transaction data from database"""
        from models.transactions import Transaction, TransactionType
        import calendar

        # Get all transactions
        all_transactions = self.transaction_manager.get_all_transactions()

        # Filter for spending-related transactions:
        # 1. SPENDING transactions (regular spending)
        # 2. ROLLOVER transactions (week 1 → week 2) - user wants to see rollovers with spending
        # Note: SAVING (transfers) are now in the Transfers tab
        spending_transactions = [
            t for t in all_transactions
            if t.transaction_type in [TransactionType.SPENDING.value, TransactionType.ROLLOVER.value]
        ]

        # Sort by date (oldest first)
        spending_transactions.sort(key=lambda t: t.date)

        # Convert to table format
        rows_data = []
        locked_rows = set()
        transaction_ids = {}  # Map row index -> transaction ID

        for idx, trans in enumerate(spending_transactions):
            # Store transaction ID for saving changes
            transaction_ids[idx] = trans.id

            # Check if locked (rollovers are locked, spending is editable)
            is_locked = self.is_transaction_locked(trans)
            if is_locked:
                locked_rows.add(idx)

            # Calculate paycheck number
            payweek = (trans.week_number + 1) // 2 if trans.week_number else "?"

            # Calculate week position (first/second)
            if trans.week_number:
                week_position = "first" if trans.week_number % 2 == 1 else "second"
            else:
                week_position = ""

            # Get day of week (Monday, Tuesday, etc.)
            day_name = calendar.day_name[trans.date.weekday()]

            # Generate category display
            if trans.transaction_type == TransactionType.ROLLOVER.value:
                category = "Rollover"
            else:
                category = trans.category or "Uncategorized"

            # Generate auto-notes
            if trans.transaction_type == TransactionType.ROLLOVER.value:
                # Rollover transactions get their own special note
                auto_notes = f"Generated: Rollover from week {trans.week_number}" if trans.week_number else "Generated: Rollover"
            else:
                # Regular spending: "Manual: Paycheck N bought Category on Day"
                auto_notes = f"Manual: Paycheck {payweek} bought {category} on {day_name}"

            # Format amount (spending is always shown as positive in this view)
            amount_value = abs(trans.amount)
            amount_display = f"${amount_value:,.2f}"

            # Get abnormal flag
            abnormal = "☑" if trans.include_in_analytics == False else ""

            row = {
                "ID": str(trans.id),
                "Date": trans.date.strftime("%m/%d/%Y"),
                "Category": category,
                "Amount": amount_display,
                "Type": trans.transaction_type or "",
                "Paycheck #": str(payweek),
                "Week #": str(trans.week_number) if trans.week_number else "",
                "Week Pos": week_position,
                "🔒": "🔒" if is_locked else "",
                "Abnormal": abnormal,
                "Manual Notes": trans.description or "",
                "Auto Notes": auto_notes
            }
            rows_data.append(row)

        # Set columns and load data
        columns = ["ID", "Date", "Category", "Amount", "Type", "Paycheck #", "Week #", "Week Pos", "🔒", "Abnormal", "Manual Notes", "Auto Notes"]
        table = getattr(self, "spending_table", None)
        if table:
            table.set_columns(columns)
            table.load_data(rows_data, locked_rows, transaction_ids)

    def load_transfers_data(self):
        """
        Load transfer transactions (type=saving) with From/To display.

        Transfers include:
        - Week ↔ Account/Bill (single transaction)
        - Account ↔ Account (two transactions)

        For Week ↔ Account:
        - amount > 0: Week is source, Account is destination
        - amount < 0: Account is source, Week is destination

        For Account ↔ Account:
        - Two transactions with opposite signs
        - Negative = source account, Positive = destination account
        """
        from models.transactions import Transaction, TransactionType

        # Get all transactions
        all_transactions = self.transaction_manager.get_all_transactions()

        # Filter for transfer transactions (type=saving, excluding end-of-period rollovers)
        transfer_transactions = []
        for t in all_transactions:
            if t.transaction_type == TransactionType.SAVING.value:
                # Exclude end-of-period auto-rollovers (they belong to Accounts tab via AccountHistory)
                if t.description:
                    if "end-of-period" in t.description.lower():
                        continue
                transfer_transactions.append(t)

        # Sort by date (oldest first)
        transfer_transactions.sort(key=lambda t: t.date)

        # Build account/bill name lookup
        accounts = self.transaction_manager.get_all_accounts()
        account_names = {a.id: a.name for a in accounts}
        bills = self.transaction_manager.get_all_bills()
        bill_names = {b.id: b.name for b in bills}

        # Convert to table format with From/To columns
        rows_data = []
        locked_rows = set()
        transaction_ids = {}  # Map row index -> transaction ID

        for idx, trans in enumerate(transfer_transactions):
            # Store transaction ID for saving changes
            transaction_ids[idx] = trans.id

            # Check if locked
            is_locked = self.is_transaction_locked(trans)
            if is_locked:
                locked_rows.add(idx)

            # Determine From/To based on amount sign and linked account/bill
            # Positive amount = money going INTO account (Week -> Account)
            # Negative amount = money coming OUT OF account (Account -> Week)

            from_source = ""
            to_dest = ""

            if trans.account_id:
                account_name = account_names.get(trans.account_id, "Unknown Account")
                if trans.amount >= 0:
                    # Week -> Account
                    from_source = f"Week {trans.week_number}" if trans.week_number else "Week ?"
                    to_dest = account_name
                else:
                    # Account -> Week
                    from_source = account_name
                    to_dest = f"Week {trans.week_number}" if trans.week_number else "Week ?"
            elif trans.bill_id:
                bill_name = bill_names.get(trans.bill_id, "Unknown Bill")
                if trans.amount >= 0:
                    # Week -> Bill
                    from_source = f"Week {trans.week_number}" if trans.week_number else "Week ?"
                    to_dest = bill_name
                else:
                    # Bill -> Week
                    from_source = bill_name
                    to_dest = f"Week {trans.week_number}" if trans.week_number else "Week ?"
            else:
                # No account or bill linked - possibly incomplete data
                from_source = "Unknown"
                to_dest = "Unknown"

            # Amount is always displayed as positive (absolute value)
            amount_value = abs(trans.amount)
            amount_display = f"${amount_value:,.2f}"

            row = {
                "ID": str(trans.id),
                "Date": trans.date.strftime("%m/%d/%Y"),
                "Amount": amount_display,
                "From": from_source,
                "To": to_dest,
                "Week": str(trans.week_number) if trans.week_number else "",
                "🔒": "🔒" if is_locked else "",
                "Manual Notes": trans.description or "",
                "Auto Notes": f"Manual: Transfer {amount_display} from {from_source} to {to_dest}"
            }
            rows_data.append(row)

        # Set columns and load data
        columns = ["ID", "Date", "Amount", "From", "To", "Week", "🔒", "Manual Notes", "Auto Notes"]
        table = getattr(self, "transfers_table", None)
        if table:
            table.set_columns(columns)
            table.load_data(rows_data, locked_rows, transaction_ids)

    def is_transaction_locked(self, transaction):
        """
        Determine if a transaction should be locked (non-editable)

        ONLY lock auto-calculated transactions that would break if edited:
        - rollover transactions (Week 1→Week 2, Week 2→Savings)
        - end-of-period savings (auto-rollover to savings account)

        Everything else is editable including:
        - income (paychecks)
        - spending
        - bill_pay
        - manual savings/transfers
        - auto-allocations (editing just adjusts week balance, rollovers recalculate)
        """
        from models.transactions import TransactionType

        # Rollover transactions are always locked (auto-calculated)
        if transaction.transaction_type == TransactionType.ROLLOVER.value:
            return True

        # End-of-period savings (Week 2 → Savings account auto-rollover)
        # These are part of the rollover system and should be locked
        if transaction.transaction_type == TransactionType.SAVING.value:
            if transaction.description:
                desc_lower = transaction.description.lower()
                if "end-of-period" in desc_lower:
                    return True

        # Everything else is editable
        return False

    def generate_auto_notes(self, transaction, amount_value=None):
        """
        Generate auto-notes for a transaction

        Args:
            transaction: Transaction object
            amount_value: Optional amount value (from AccountHistory.change_amount) for deposit/withdrawal detection
        """
        from models.transactions import TransactionType

        # Determine if manual or generated
        is_manual = not self.is_transaction_locked(transaction)
        prefix = "Manual:" if is_manual else "Generated:"

        # Calculate payweek number for context
        payweek = (transaction.week_number + 1) // 2 if transaction.week_number else "?"

        # Generate description based on type
        if transaction.transaction_type == TransactionType.BILL_PAY.value:
            return f"{prefix} Bill payment"

        elif transaction.transaction_type == TransactionType.ROLLOVER.value:
            # Rollover transaction - check if it's week-to-week or week-to-account
            if transaction.account_id:
                # Week 2 → Savings account rollover
                account_name = transaction.account.name if transaction.account else "account"
                return f"{prefix} Rollover into {account_name} from payweek {payweek}"
            else:
                # Week 1 → Week 2 rollover
                week_position = "first" if transaction.week_number % 2 == 1 else "second"
                next_position = "second" if week_position == "first" else "first"
                return f"{prefix} Rollover from {week_position} week to {next_position} week in payweek {payweek}"

        elif transaction.transaction_type == TransactionType.SAVING.value:
            # Check if it's auto-generated
            if transaction.description:
                desc_lower = transaction.description.lower()

                # End-of-period rollover (week 2 → savings account)
                if "end-of-period" in desc_lower:
                    return f"{prefix} Rollover from payweek {payweek}"

                # Paycheck allocation
                if ("allocation" in desc_lower and "savings" in desc_lower) or "auto saved" in desc_lower:
                    return f"{prefix} Savings allocation from payweek {payweek}"

            # Manual transaction - use amount to determine deposit vs withdrawal
            if is_manual and amount_value is not None:
                if amount_value >= 0:
                    return f"{prefix} Deposit"
                else:
                    return f"{prefix} Withdrawal"

            # Fallback
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
        """Handle save button click - save edited/deleted transactions to database"""
        from PyQt6.QtWidgets import QMessageBox
        from models.transactions import Transaction
        from datetime import datetime

        table = getattr(self, f"{tab_name}_table", None)
        if not table:
            return

        # Get changes
        edited_rows = table.get_edited_rows()
        deleted_rows = table.get_deleted_rows()

        if not edited_rows and not deleted_rows:
            QMessageBox.information(self, "No Changes", "No changes to save.")
            return

        # Track results
        successes = []
        failures = []

        # Process deletions
        for row_idx in deleted_rows:
            trans_id = table.transaction_ids.get(row_idx)
            if trans_id is None:
                failures.append((row_idx, "No transaction ID found"))
                continue

            try:
                success = self.transaction_manager.delete_transaction(trans_id)
                if success:
                    successes.append((trans_id, "Deleted"))
                else:
                    failures.append((trans_id, "Delete failed"))
            except Exception as e:
                failures.append((trans_id, f"Delete error: {str(e)}"))

        # Process edits
        for row_idx in edited_rows:
            if row_idx in deleted_rows:
                continue  # Already deleted, skip

            trans_id = table.transaction_ids.get(row_idx)
            if trans_id is None:
                failures.append((row_idx, "No transaction ID found"))
                continue

            # Get current row data from table
            row_data = table.get_row_data(row_idx)
            if not row_data:
                failures.append((trans_id, "Could not read row data"))
                continue

            # Validate and convert data
            updates, validation_error = self._validate_and_convert_row_data(row_data, tab_name)
            if validation_error:
                failures.append((trans_id, validation_error))
                continue

            # Update transaction in database
            try:
                updated_trans = self.transaction_manager.update_transaction(trans_id, updates)
                if updated_trans:
                    changes = self._format_changes(row_data, updates)
                    successes.append((trans_id, changes))
                else:
                    failures.append((trans_id, "Update failed"))
            except Exception as e:
                failures.append((trans_id, f"Update error: {str(e)}"))

        # Show results dialog
        self._show_save_results_dialog(successes, failures)

        # Reload table data from database
        self.refresh()

    def _validate_and_convert_row_data(self, row_data, tab_name):
        """
        Validate and convert row data to database format

        Returns:
            (updates_dict, error_message) - either updates dict or error message
        """
        from datetime import datetime

        updates = {}

        # Parse date
        if "Date" in row_data:
            try:
                date_obj = datetime.strptime(row_data["Date"], "%m/%d/%Y").date()
                updates["date"] = date_obj
            except ValueError:
                return None, f"Invalid date format: {row_data['Date']}"

        # Parse amount (remove $ and commas)
        # IMPORTANT: For Accounts tab, user sees AccountHistory.change_amount (negative for payments)
        # but we need to store it as Transaction.amount (positive)
        if "Amount" in row_data:
            try:
                amount_str = row_data["Amount"].replace("$", "").replace(",", "").strip()
                amount = float(amount_str)

                # For Accounts tab: convert change_amount → transaction.amount
                # Accounts show negative for payments/withdrawals, but transaction stores positive
                if tab_name == "accounts":
                    updates["amount"] = abs(amount)  # Always store as positive in transaction
                else:
                    updates["amount"] = amount  # Spending/Paycheck/Transfers: use as-is

            except ValueError:
                return None, f"Invalid amount: {row_data['Amount']}"

        # Get description from Manual Notes
        if "Manual Notes" in row_data:
            updates["description"] = row_data["Manual Notes"]

        # Get abnormal flag (for spending)
        if "Abnormal" in row_data:
            updates["include_in_analytics"] = not row_data["Abnormal"]  # Abnormal checked = exclude

        return updates, None

    def _format_changes(self, row_data, updates):
        """Format changes for display in results dialog"""
        changes = []
        for key, value in updates.items():
            if key == "date":
                changes.append(f"Date: {value}")
            elif key == "amount":
                changes.append(f"Amount: ${value:,.2f}")
            elif key == "description":
                changes.append(f"Notes: {value}")
        return ", ".join(changes) if changes else "Updated"

    def _show_save_results_dialog(self, successes, failures):
        """Show dialog with save results"""
        from PyQt6.QtWidgets import QMessageBox

        message = ""

        if successes:
            message += f"<b>{len(successes)} transaction(s) succeeded:</b><br>"
            for trans_id, details in successes[:5]:  # Show first 5
                message += f"&nbsp;&nbsp;ID {trans_id}: {details}<br>"
            if len(successes) > 5:
                message += f"&nbsp;&nbsp;...and {len(successes) - 5} more<br>"
            message += "<br>"

        if failures:
            message += f"<b>{len(failures)} transaction(s) failed:</b><br>"
            for trans_id, error in failures[:5]:  # Show first 5
                message += f"&nbsp;&nbsp;ID {trans_id}: {error}<br>"
            if len(failures) > 5:
                message += f"&nbsp;&nbsp;...and {len(failures) - 5} more<br>"

        if not message:
            message = "No changes processed."

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Save Results")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def refresh(self):
        """Refresh all sub-tabs with real data"""
        try:
            # Load accounts data (merged Bills + Savings)
            self.load_accounts_data()

            # Load paycheck data
            self.load_paycheck_data()

            # Load spending data
            self.load_spending_data()

            # Load transfers data
            self.load_transfers_data()

        except Exception as e:
            print(f"Error refreshing transactions view: {e}")
            import traceback
            traceback.print_exc()

    def on_theme_changed(self):
        """Handle theme changes"""
        self.apply_theme()

        # Apply theme to all table widgets
        for tab_name in ["accounts", "paycheck", "spending", "transfers"]:
            table = getattr(self, f"{tab_name}_table", None)
            if table:
                table.apply_theme()
                table.refresh_display()  # Re-render with new colors

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
        for tab_name in ["accounts", "paycheck", "spending", "transfers"]:
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
        for tab_name in ["accounts", "paycheck", "spending", "transfers"]:
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
                        background-color: {colors['secondary']};
                        color: {colors['background']};
                        border: 1px solid {colors['secondary']};
                        border-radius: 4px;
                        padding: 6px 12px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {colors['accent']};
                    }}
                    QPushButton:pressed {{
                        background-color: {colors['primary_dark']};
                    }}
                """)
