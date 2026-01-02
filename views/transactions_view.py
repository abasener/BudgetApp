"""
Transactions View - Advanced data inspection and debugging interface
Shows all transactions organized by type (Bills, Savings, Paycheck, Spending)
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QLineEdit, QPushButton, QLabel, QToolButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from themes import theme_manager
from views.transactions_table_widget import TransactionTableWidget


class TransactionsView(QWidget):
    """
    Main Transactions tab with 4 sub-tabs for different transaction types
    Provides advanced search, filtering, and bulk editing capabilities
    """

    # Field descriptions for each sub-tab (used in info button tooltip)
    # NOTE: If a row is LOCKED (🔒), NO fields in that row can be edited.
    # The descriptions below apply to non-locked rows only.
    FIELD_INFO = {
        "accounts": {
            "ID": "Unique transaction ID. Cannot be changed.",
            "Locked": "If locked (🔒), entire row is read-only. System-generated transactions are locked.",
            "Date": "Transaction date. EDITABLE - changing auto-updates the Week.",
            "Account": "The bill/savings account. EDITABLE - must match an existing account name.",
            "Movement": "Money direction. EDITABLE - Deposit (into account), Withdrawal (from account), Payment (bill).",
            "Amount": "Dollar amount. EDITABLE - enter positive only. Use Movement for direction.",
            "Type": "Transaction type. Auto-set based on Movement/account. Cannot be changed.",
            "Week": "Week number. Auto-calculated from Date. Cannot be changed.",
            "Manual Notes": "Your notes. EDITABLE - displays in account history.",
            "Auto Notes": "System-generated description. Cannot be changed.",
        },
        "paycheck": {
            "ID": "Unique paycheck ID. Cannot be changed.",
            "Earned Date": "Date paycheck received. EDITABLE - for bookkeeping, no recalculation.",
            "Start Date": "Pay period start (must be Monday). EDITABLE - triggers full recalculation.",
            "Amount": "Paycheck amount. EDITABLE - enter positive. Triggers allocation recalculation.",
            "Type": "Always 'income'. Cannot be changed.",
            "Week": "Week number. Auto-calculated from dates. Cannot be changed.",
            "Locked": "If locked (🔒), entire row is read-only.",
            "Manual Notes": "Your notes. EDITABLE.",
            "Auto Notes": "System-generated date range. Cannot be changed.",
        },
        "spending": {
            "ID": "Unique transaction ID. Cannot be changed.",
            "Date": "Purchase date. EDITABLE - may move transaction to different week.",
            "Amount": "Dollar amount. EDITABLE - enter positive only.",
            "Category": "Spending category. EDITABLE - can type new. Rollovers show First/Second.",
            "Type": "Transaction type (spending/rollover). Cannot be changed.",
            "Abnormal": "Exclude from analytics. EDITABLE - checkbox.",
            "Paycheck": "Paycheck number. Auto-calculated from Week. Cannot be changed.",
            "Week": "Week number. Auto-calculated from Date. Cannot be changed.",
            "Locked": "If locked (🔒), entire row is read-only. Rollovers are locked.",
            "Manual Notes": "Your notes. EDITABLE.",
            "Auto Notes": "System-generated description. Cannot be changed.",
        },
        "transfers": {
            "ID": "Both transaction IDs (source/dest). Cannot be changed.",
            "Date": "Transfer date. EDITABLE - updates both linked transactions.",
            "Amount": "Dollar amount. EDITABLE - enter positive. From/To sets direction.",
            "From": "Source account. EDITABLE - must exist. Cannot match To.",
            "To": "Destination account. EDITABLE - must exist. Cannot match From.",
            "Week": "Week number. Auto-calculated from Date. Cannot be changed.",
            "Locked": "If locked (🔒), entire row is read-only.",
            "Manual Notes": "Your notes. EDITABLE - updates both linked transactions.",
            "Auto Notes": "System-generated description. Cannot be changed.",
        },
    }

    def __init__(self, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager

        # Track which sub-tab is currently active
        self.current_subtab = "accounts"

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

        # Info button (circular "i" button with tooltip)
        info_btn = QToolButton()
        info_btn.setText("i")
        info_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        info_btn.setFixedSize(24, 24)
        info_btn.setToolTip(self._get_field_info_tooltip(tab_name.lower()))
        # Make tooltip stay visible longer
        info_btn.setToolTipDuration(30000)  # 30 seconds
        setattr(self, f"{tab_name.lower()}_info_btn", info_btn)
        top_bar.addWidget(info_btn)

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

    def _get_field_info_tooltip(self, tab_name):
        """Generate tooltip text for the info button based on tab name"""
        field_info = self.FIELD_INFO.get(tab_name, {})
        if not field_info:
            return "No field information available."

        # Build tooltip text with field names in brackets
        lines = ["<b>Column Descriptions:</b><br>"]
        for field, description in field_info.items():
            lines.append(f"<b>[{field}]</b> - {description}<br>")

        return "".join(lines)

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
        """Deprecated - real data is loaded in refresh() via load_*_data() methods"""
        # This method is no longer used - all tabs load real data
        pass

    def load_accounts_data(self):
        """
        Load transactions involving Bills + Savings accounts directly from Transaction table.

        Shows all transactions where account_id or bill_id is set (Week↔Account transfers),
        EXCLUDING Account-to-Account transfers (those go in Transfers tab).

        Movement types:
        - Deposit: Money going INTO account from week (positive amount)
        - Withdrawal: Money going FROM account TO week (negative amount)
        - Payment: Money leaving budget entirely (bill_pay type)
        """
        from models.transactions import Transaction, TransactionType

        # Get all transactions that involve an account or bill
        all_transactions = self.transaction_manager.get_all_transactions()

        # Filter for transactions with account_id or bill_id set
        # Exclude Account-to-Account transfers (transfer_group_id is set)
        account_transactions = [
            t for t in all_transactions
            if (t.account_id is not None or t.bill_id is not None)
            and t.transfer_group_id is None  # Exclude Account-to-Account transfers
        ]

        # Sort by date (oldest first)
        account_transactions.sort(key=lambda t: t.date)

        # Build account/bill name lookup
        accounts = self.transaction_manager.get_all_accounts()
        account_names = {a.id: a.name for a in accounts}
        bills = self.transaction_manager.get_all_bills()
        bill_names = {b.id: b.name for b in bills}

        # Convert to table format
        rows_data = []
        locked_rows = set()
        transaction_ids = {}  # Map row index -> transaction ID

        for idx, trans in enumerate(account_transactions):
            # Store transaction ID for saving changes
            transaction_ids[idx] = trans.id

            # Determine if locked (auto-generated transactions)
            is_locked = self.is_transaction_locked(trans)
            if is_locked:
                locked_rows.add(idx)

            # Get account name
            if trans.account_id:
                account_name = account_names.get(trans.account_id, "Unknown Account")
            elif trans.bill_id:
                account_name = bill_names.get(trans.bill_id, "Unknown Bill")
            else:
                account_name = "Unknown"

            # Determine Movement type based on transaction characteristics
            # - Payment: bill_pay type (money leaving budget)
            # - Deposit: positive amount (money into account from week)
            # - Withdrawal: negative amount (money from account to week)
            amount_value = trans.amount

            if trans.transaction_type == TransactionType.BILL_PAY.value:
                movement = "Payment"
            elif amount_value >= 0:
                movement = "Deposit"
            else:
                movement = "Withdrawal"

            # All amounts shown as positive now - Movement indicates direction
            amount_display = f"${abs(amount_value):,.2f}"

            # Generate auto-notes
            auto_notes = self.generate_auto_notes(trans, amount_value)

            row = {
                "ID": str(trans.id),
                "Locked": "🔒" if is_locked else "",
                "Date": trans.date.strftime("%m/%d/%Y"),
                "Account": account_name,
                "Movement": movement,
                "Amount": amount_display,
                "Type": trans.transaction_type or "",
                "Week": str(trans.week_number) if trans.week_number else "",
                "Manual Notes": trans.description or "",
                "Auto Notes": auto_notes
            }
            rows_data.append(row)

        # Set columns and load data
        columns = ["ID", "Locked", "Date", "Account", "Movement", "Amount", "Type", "Week", "Manual Notes", "Auto Notes"]
        # Non-editable columns: ID, Locked, Type (auto-set), Week (auto-calc), Auto Notes
        non_editable = {"ID", "Locked", "Type", "Week", "Auto Notes"}
        # Fixed dropdown columns: Movement has 3 options
        dropdowns = {"Movement": ["Deposit", "Withdrawal", "Payment"]}
        # Editable dropdown columns: Account shows existing accounts but allows typing new
        all_account_names = list(account_names.values()) + list(bill_names.values())
        editable_dropdowns = {"Account": sorted(set(all_account_names))}

        table = getattr(self, "accounts_table", None)
        if table:
            table.set_columns(columns, non_editable, dropdowns, editable_dropdowns)
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
                "Locked": "🔒" if is_locked else "",
                "Manual Notes": paycheck.description or "",
                "Auto Notes": auto_notes
            }
            rows_data.append(row)

        # Set columns and load data
        columns = ["ID", "Earned Date", "Start Date", "Amount", "Type", "Week", "Locked", "Manual Notes", "Auto Notes"]
        # Non-editable columns: ID, Type, Week (auto-calc), Locked, Auto Notes
        # Earned Date and Start Date are editable (Start Date triggers recalc)
        non_editable = {"ID", "Type", "Week", "Locked", "Auto Notes"}

        table = getattr(self, "paycheck_table", None)
        if table:
            table.set_columns(columns, non_editable)
            table.load_data(rows_data, locked_rows, transaction_ids)

    def load_spending_data(self):
        """Load real spending transaction data from database

        Column order: [ID][Date][Amount][Category][Type][Abnormal][Paycheck][Week][Locked][Manual Notes][Auto Notes]
        - Removed Week Pos column
        - For rollovers: Category shows "First" or "Second" instead of "Rollover"
        """
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

            # Calculate week position (first/second) - used for rollover category display
            if trans.week_number:
                week_position = "First" if trans.week_number % 2 == 1 else "Second"
            else:
                week_position = ""

            # Get day of week (Monday, Tuesday, etc.)
            day_name = calendar.day_name[trans.date.weekday()]

            # Generate category display
            # For rollovers: show "First" or "Second" instead of "Rollover"
            if trans.transaction_type == TransactionType.ROLLOVER.value:
                category = week_position if week_position else "Rollover"
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
                "Amount": amount_display,
                "Category": category,
                "Type": trans.transaction_type or "",
                "Abnormal": abnormal,
                "Paycheck": str(payweek),
                "Week": str(trans.week_number) if trans.week_number else "",
                "Locked": "🔒" if is_locked else "",
                "Manual Notes": trans.description or "",
                "Auto Notes": auto_notes
            }
            rows_data.append(row)

        # Set columns and load data
        columns = ["ID", "Date", "Amount", "Category", "Type", "Abnormal", "Paycheck", "Week", "Locked", "Manual Notes", "Auto Notes"]
        # Non-editable columns: ID, Type, Paycheck (auto-calc), Week (auto-calc), Locked, Auto Notes
        non_editable = {"ID", "Type", "Paycheck", "Week", "Locked", "Auto Notes"}
        # Get all unique categories from spending transactions for editable dropdown
        existing_categories = set()
        for t in spending_transactions:
            if t.category:
                existing_categories.add(t.category)
        editable_dropdowns = {"Category": sorted(existing_categories)}

        table = getattr(self, "spending_table", None)
        if table:
            table.set_columns(columns, non_editable, None, editable_dropdowns)
            table.load_data(rows_data, locked_rows, transaction_ids)

    def load_transfers_data(self):
        """
        Load ONLY Account-to-Account transfer transactions.

        This tab shows transfers between two accounts (savings or bills),
        NOT Week↔Account transfers (those are shown in Accounts tab as Deposit/Withdrawal).

        Account-to-Account transfers are identified by having a transfer_group_id set.
        Each transfer creates two transactions with the same group_id:
        - Negative amount = source account (money leaving)
        - Positive amount = destination account (money arriving)

        We show each transaction separately so user can see both sides.
        """
        from models.transactions import Transaction, TransactionType

        # Get all transactions
        all_transactions = self.transaction_manager.get_all_transactions()

        # Filter for Account-to-Account transfers ONLY (have transfer_group_id)
        transfer_transactions = [
            t for t in all_transactions
            if t.transfer_group_id is not None
        ]

        # Sort by date, then by group_id to keep pairs together
        transfer_transactions.sort(key=lambda t: (t.date, t.transfer_group_id, t.amount))

        # Build account name lookup
        accounts = self.transaction_manager.get_all_accounts()
        account_names = {a.id: a.name for a in accounts}
        bills = self.transaction_manager.get_all_bills()
        bill_names = {b.id: b.name for b in bills}

        # Group transactions by transfer_group_id
        groups = {}
        for trans in transfer_transactions:
            if trans.transfer_group_id not in groups:
                groups[trans.transfer_group_id] = []
            groups[trans.transfer_group_id].append(trans)

        # Convert to table format with From/To columns
        # Show ONE row per transfer pair (not both transactions)
        rows_data = []
        locked_rows = set()
        transaction_ids = {}  # Map row index -> (source_trans_id, dest_trans_id) tuple
        row_idx = 0

        # Process each unique transfer group (one row per pair)
        for group_id, group_transactions in groups.items():
            if len(group_transactions) != 2:
                # Skip incomplete pairs (shouldn't happen, but be safe)
                continue

            # Find source (negative) and destination (positive) transactions
            source_trans = None
            dest_trans = None
            for trans in group_transactions:
                if trans.amount < 0:
                    source_trans = trans
                else:
                    dest_trans = trans

            if not source_trans or not dest_trans:
                continue

            # Get account names for source and destination
            if source_trans.account_id:
                from_account = account_names.get(source_trans.account_id, "Unknown Account")
            elif source_trans.bill_id:
                from_account = bill_names.get(source_trans.bill_id, "Unknown Bill")
            else:
                from_account = "Unknown"

            if dest_trans.account_id:
                to_account = account_names.get(dest_trans.account_id, "Unknown Account")
            elif dest_trans.bill_id:
                to_account = bill_names.get(dest_trans.bill_id, "Unknown Bill")
            else:
                to_account = "Unknown"

            # Store BOTH transaction IDs for saving changes (we'll update both when editing)
            # Use tuple: (source_id, dest_id)
            transaction_ids[row_idx] = (source_trans.id, dest_trans.id)

            # Check if locked (either transaction locked = row locked)
            is_locked = self.is_transaction_locked(source_trans) or self.is_transaction_locked(dest_trans)
            if is_locked:
                locked_rows.add(row_idx)

            # Amount is always positive (absolute value from source)
            amount_value = abs(source_trans.amount)
            amount_display = f"${amount_value:,.2f}"

            # Use source transaction for date/week/notes (they should be the same anyway)
            row = {
                "ID": f"{source_trans.id}/{dest_trans.id}",  # Show both IDs
                "Date": source_trans.date.strftime("%m/%d/%Y"),
                "Amount": amount_display,
                "From": from_account,
                "To": to_account,
                "Week": str(source_trans.week_number) if source_trans.week_number else "",
                "Locked": "🔒" if is_locked else "",
                "Manual Notes": source_trans.description or "",
                "Auto Notes": f"Transfer {amount_display} from {from_account} to {to_account}"
            }
            rows_data.append(row)
            row_idx += 1

        # Sort by date
        rows_data.sort(key=lambda r: r["Date"])

        # Set columns and load data
        columns = ["ID", "Date", "Amount", "From", "To", "Week", "Locked", "Manual Notes", "Auto Notes"]
        # Non-editable columns: ID, Week (auto-calc), Locked, Auto Notes
        non_editable = {"ID", "Week", "Locked", "Auto Notes"}
        # Editable dropdown columns: From and To show existing accounts but allow typing new
        all_account_names = list(account_names.values()) + list(bill_names.values())
        editable_dropdowns = {
            "From": sorted(set(all_account_names)),
            "To": sorted(set(all_account_names))
        }

        table = getattr(self, "transfers_table", None)
        if table:
            table.set_columns(columns, non_editable, None, editable_dropdowns)
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

            # Handle transfers tab - has tuple of (source_id, dest_id)
            if tab_name == "transfers" and isinstance(trans_id, tuple):
                source_id, dest_id = trans_id
                try:
                    success1 = self.transaction_manager.delete_transaction(source_id)
                    success2 = self.transaction_manager.delete_transaction(dest_id)
                    if success1 and success2:
                        successes.append((f"{source_id}/{dest_id}", "Deleted (both sides)"))
                    else:
                        failures.append((f"{source_id}/{dest_id}", "Delete failed"))
                except Exception as e:
                    failures.append((f"{source_id}/{dest_id}", f"Delete error: {str(e)}"))
            else:
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

            # Handle paycheck tab - special recalculation logic for start date/amount changes
            if tab_name == "paycheck" and updates.get("_needs_recalculation"):
                try:
                    # Get the original paycheck transaction
                    original_paycheck = self.transaction_manager.get_transaction_by_id(trans_id)
                    if not original_paycheck:
                        failures.append((trans_id, "Could not find original paycheck"))
                        continue

                    # Apply paycheck recalculation
                    success, message = self._apply_paycheck_recalculation(
                        original_paycheck, updates, row_data
                    )

                    if success:
                        successes.append((trans_id, message))
                    else:
                        failures.append((trans_id, message))
                except Exception as e:
                    failures.append((trans_id, f"Recalculation error: {str(e)}"))
                continue  # Skip normal update flow

            # Handle transfers tab - update BOTH transactions
            elif tab_name == "transfers" and isinstance(trans_id, tuple):
                source_id, dest_id = trans_id
                try:
                    # Build updates for source (negative amount, From account)
                    source_updates = self._build_transfer_source_updates(updates, row_data)
                    # Build updates for dest (positive amount, To account)
                    dest_updates = self._build_transfer_dest_updates(updates, row_data)

                    updated_source = self.transaction_manager.update_transaction(source_id, source_updates)
                    updated_dest = self.transaction_manager.update_transaction(dest_id, dest_updates)

                    if updated_source and updated_dest:
                        changes = self._format_changes(row_data, updates)
                        successes.append((f"{source_id}/{dest_id}", changes))
                    else:
                        failures.append((f"{source_id}/{dest_id}", "Update failed"))
                except Exception as e:
                    failures.append((f"{source_id}/{dest_id}", f"Update error: {str(e)}"))
            else:
                # Regular single transaction update
                try:
                    updated_trans = self.transaction_manager.update_transaction(trans_id, updates)
                    if updated_trans:
                        changes = self._format_changes(row_data, updates)
                        successes.append((trans_id, changes))
                    else:
                        failures.append((trans_id, "Update failed"))
                except Exception as e:
                    failures.append((trans_id, f"Update error: {str(e)}"))

        # Show results dialog only in testing mode
        from views.dialogs.settings_dialog import get_setting
        if get_setting("testing_mode", False):
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
        from models.transactions import TransactionType

        updates = {}

        # Route to tab-specific validation
        if tab_name == "accounts":
            return self._validate_accounts_row(row_data)
        elif tab_name == "spending":
            return self._validate_spending_row(row_data)
        elif tab_name == "paycheck":
            return self._validate_paycheck_row(row_data)
        elif tab_name == "transfers":
            return self._validate_transfers_row(row_data)

        return None, f"Unknown tab: {tab_name}"

    def _validate_accounts_row(self, row_data):
        """Validate and convert Accounts tab row data

        Returns (updates, errors) where:
        - updates: dict of valid field updates to apply
        - errors: list of error messages for failed fields (empty if all valid)

        Valid fields are saved even if some fields fail validation.
        """
        from datetime import datetime
        from models.transactions import TransactionType

        updates = {}
        errors = []

        # Parse and validate Date
        if "Date" in row_data:
            try:
                date_obj = datetime.strptime(row_data["Date"], "%m/%d/%Y").date()
                updates["date"] = date_obj
            except ValueError:
                errors.append(f"Invalid date format: {row_data['Date']} (use MM/DD/YYYY)")

        # Validate Account name - must match existing bill or savings account
        if "Account" in row_data:
            account_name = row_data["Account"].strip()
            account_id, bill_id, account_type = self._lookup_account_by_name(account_name)

            if account_id is None and bill_id is None:
                errors.append(f"Account not found: '{account_name}'")
            else:
                # Set the appropriate ID field
                if account_id:
                    updates["account_id"] = account_id
                    updates["bill_id"] = None
                else:
                    updates["bill_id"] = bill_id
                    updates["account_id"] = None

        # Get Movement type and parse Amount together (they're interdependent)
        movement = row_data.get("Movement", "").strip()

        if "Amount" in row_data:
            try:
                amount_str = row_data["Amount"].replace("$", "").replace(",", "").replace("-", "").strip()
                amount = abs(float(amount_str))  # Always positive base amount

                # Movement determines sign in database and transaction type
                if movement == "Deposit":
                    updates["amount"] = amount  # Positive = into account
                    updates["transaction_type"] = TransactionType.SAVING.value
                elif movement == "Withdrawal":
                    updates["amount"] = -amount  # Negative = out of account
                    updates["transaction_type"] = TransactionType.SAVING.value
                elif movement == "Payment":
                    updates["amount"] = amount  # Bill payments stored positive
                    updates["transaction_type"] = TransactionType.BILL_PAY.value
                else:
                    errors.append(f"Invalid movement type: '{movement}' (must be Deposit, Withdrawal, or Payment)")
            except ValueError:
                errors.append(f"Invalid amount: {row_data['Amount']}")

        # Manual Notes - always valid
        if "Manual Notes" in row_data:
            updates["description"] = row_data["Manual Notes"]

        # Return updates and combined error message (if any)
        error_msg = "; ".join(errors) if errors else None
        return updates, error_msg

    def _validate_spending_row(self, row_data):
        """Validate and convert Spending tab row data

        Returns (updates, errors) - valid fields saved even if some fail.
        """
        from datetime import datetime

        updates = {}
        errors = []

        # Parse Date
        if "Date" in row_data:
            try:
                date_obj = datetime.strptime(row_data["Date"], "%m/%d/%Y").date()
                updates["date"] = date_obj
            except ValueError:
                errors.append(f"Invalid date format: {row_data['Date']} (use MM/DD/YYYY)")

        # Parse Amount - spending is always positive in display and database
        if "Amount" in row_data:
            try:
                amount_str = row_data["Amount"].replace("$", "").replace(",", "").replace("-", "").strip()
                updates["amount"] = abs(float(amount_str))
            except ValueError:
                errors.append(f"Invalid amount: {row_data['Amount']}")

        # Category - always valid (can be new category)
        if "Category" in row_data:
            updates["category"] = row_data["Category"].strip()

        # Abnormal flag
        if "Abnormal" in row_data:
            updates["include_in_analytics"] = not row_data["Abnormal"]  # Checked = exclude

        # Manual Notes - always valid
        if "Manual Notes" in row_data:
            updates["description"] = row_data["Manual Notes"]

        error_msg = "; ".join(errors) if errors else None
        return updates, error_msg

    def _validate_paycheck_row(self, row_data):
        """Validate and convert Paycheck tab row data

        Returns (updates, errors) - valid fields saved even if some fail.

        IMPORTANT: Start Date and Amount changes trigger paycheck recalculation.
        This is a complex operation that:
        1. Checks for week overlap with other paychecks
        2. Checks that no spending transactions would be orphaned
        3. Deletes auto-generated transactions (auto-saves, rollovers)
        4. Re-runs paycheck processing with new values

        See TRANSACTIONS_TAB_ROADMAP.md for detailed documentation.
        """
        from datetime import datetime, timedelta

        updates = {}
        errors = []

        # Parse Earned Date (simple - just updates transaction date)
        if "Earned Date" in row_data:
            try:
                date_obj = datetime.strptime(row_data["Earned Date"], "%m/%d/%Y").date()
                updates["date"] = date_obj
            except ValueError:
                errors.append(f"Invalid earned date format: {row_data['Earned Date']} (use MM/DD/YYYY)")

        # Parse Amount - may trigger recalculation
        new_amount = None
        if "Amount" in row_data:
            try:
                amount_str = row_data["Amount"].replace("$", "").replace(",", "").replace("-", "").strip()
                new_amount = abs(float(amount_str))
                updates["amount"] = new_amount
            except ValueError:
                errors.append(f"Invalid amount: {row_data['Amount']}")

        # Parse Start Date - may trigger recalculation
        new_start_date = None
        if "Start Date" in row_data:
            try:
                new_start_date = datetime.strptime(row_data["Start Date"], "%m/%d/%Y").date()

                # Validate Start Date must be Monday
                if new_start_date.weekday() != 0:
                    errors.append(f"Start Date must be a Monday (got {new_start_date.strftime('%A')})")
                    new_start_date = None
            except ValueError:
                errors.append(f"Invalid start date format: {row_data['Start Date']} (use MM/DD/YYYY)")

        # If Start Date or Amount changed, mark for recalculation
        # The actual recalculation happens in _apply_paycheck_recalculation()
        if new_start_date is not None:
            updates["_new_start_date"] = new_start_date
            updates["_needs_recalculation"] = True

        if new_amount is not None:
            updates["_needs_recalculation"] = True

        # Manual Notes - always valid
        if "Manual Notes" in row_data:
            updates["description"] = row_data["Manual Notes"]

        error_msg = "; ".join(errors) if errors else None
        return updates, error_msg

    def _validate_transfers_row(self, row_data):
        """Validate and convert Transfers tab row data

        Returns (updates, errors) - valid fields saved even if some fail.
        """
        from datetime import datetime

        updates = {}
        errors = []

        # Parse Date
        if "Date" in row_data:
            try:
                date_obj = datetime.strptime(row_data["Date"], "%m/%d/%Y").date()
                updates["date"] = date_obj
            except ValueError:
                errors.append(f"Invalid date format: {row_data['Date']} (use MM/DD/YYYY)")

        # Parse Amount - transfers always positive in display
        if "Amount" in row_data:
            try:
                amount_str = row_data["Amount"].replace("$", "").replace(",", "").replace("-", "").strip()
                updates["amount"] = abs(float(amount_str))
            except ValueError:
                errors.append(f"Invalid amount: {row_data['Amount']}")

        # Validate From account
        from_account_id = None
        from_bill_id = None
        if "From" in row_data:
            from_name = row_data["From"].strip()
            from_account_id, from_bill_id, _ = self._lookup_account_by_name(from_name)
            if from_account_id is None and from_bill_id is None:
                errors.append(f"From account not found: '{from_name}'")
            else:
                updates["from_account_id"] = from_account_id
                updates["from_bill_id"] = from_bill_id

        # Validate To account
        to_account_id = None
        to_bill_id = None
        if "To" in row_data:
            to_name = row_data["To"].strip()
            to_account_id, to_bill_id, _ = self._lookup_account_by_name(to_name)
            if to_account_id is None and to_bill_id is None:
                errors.append(f"To account not found: '{to_name}'")
            else:
                updates["to_account_id"] = to_account_id
                updates["to_bill_id"] = to_bill_id

        # Check From and To are not the same account
        if "From" in row_data and "To" in row_data:
            from_name = row_data["From"].strip().lower()
            to_name = row_data["To"].strip().lower()
            if from_name == to_name:
                # Both From and To fail - remove their updates and add errors
                updates.pop("from_account_id", None)
                updates.pop("from_bill_id", None)
                updates.pop("to_account_id", None)
                updates.pop("to_bill_id", None)
                errors.append(f"From and To cannot be the same account: '{row_data['From']}'")

        # Manual Notes
        if "Manual Notes" in row_data:
            updates["description"] = row_data["Manual Notes"]

        error_msg = "; ".join(errors) if errors else None
        return updates, error_msg

    def _lookup_account_by_name(self, name):
        """
        Look up an account by name

        Returns:
            (account_id, bill_id, account_type) - one of account_id or bill_id will be set
        """
        name_lower = name.lower().strip()

        # Check savings accounts
        accounts = self.transaction_manager.get_all_accounts()
        for account in accounts:
            if account.name.lower().strip() == name_lower:
                return account.id, None, "savings"

        # Check bills
        bills = self.transaction_manager.get_all_bills()
        for bill in bills:
            if bill.name.lower().strip() == name_lower:
                return None, bill.id, "bill"

        return None, None, None

    def _apply_paycheck_recalculation(self, original_paycheck, updates, row_data):
        """
        Apply paycheck recalculation when start date or amount changes.

        This is a complex operation that:
        1. Validates the new start date doesn't overlap with other paychecks
        2. Checks that no spending transactions would be orphaned
        3. Deletes auto-generated transactions (auto-saves, rollovers)
        4. Updates or recreates the weeks with new dates
        5. Re-runs paycheck allocation with new amount

        Returns:
            (success: bool, message: str)
        """
        from datetime import timedelta
        from models.transactions import TransactionType

        new_start_date = updates.get("_new_start_date")
        new_amount = updates.get("amount", original_paycheck.amount)

        # Get current week info
        all_weeks = self.transaction_manager.get_all_weeks()
        current_week = next((w for w in all_weeks if w.week_number == original_paycheck.week_number), None)

        if not current_week:
            return False, "Could not find associated week"

        # If start date is changing, do overlap and orphan checks
        if new_start_date and new_start_date != current_week.start_date:
            # Calculate new week ranges
            new_week1_end = new_start_date + timedelta(days=6)
            new_week2_start = new_start_date + timedelta(days=7)
            new_week2_end = new_week2_start + timedelta(days=6)

            # Get the second week of this paycheck period
            week2_number = original_paycheck.week_number + 1
            current_week2 = next((w for w in all_weeks if w.week_number == week2_number), None)

            # Check for overlap with OTHER paychecks (exclude current paycheck's weeks)
            for existing_week in all_weeks:
                # Skip current paycheck's weeks
                if existing_week.week_number in [original_paycheck.week_number, week2_number]:
                    continue

                # Check if new week 1 overlaps
                if new_start_date <= existing_week.end_date and new_week1_end >= existing_week.start_date:
                    return False, f"New dates overlap with Week {existing_week.week_number} ({existing_week.start_date} - {existing_week.end_date})"

                # Check if new week 2 overlaps
                if new_week2_start <= existing_week.end_date and new_week2_end >= existing_week.start_date:
                    return False, f"New dates overlap with Week {existing_week.week_number} ({existing_week.start_date} - {existing_week.end_date})"

            # Check for orphaned spending transactions
            # Get all spending transactions in the current weeks
            all_transactions = self.transaction_manager.get_all_transactions()
            spending_in_weeks = [
                t for t in all_transactions
                if t.transaction_type == TransactionType.SPENDING.value
                and t.week_number in [original_paycheck.week_number, week2_number]
            ]

            # Check if any spending transactions would fall outside new date range
            for spending in spending_in_weeks:
                if spending.date < new_start_date or spending.date > new_week2_end:
                    return False, f"Cannot move dates: spending transaction on {spending.date} would be orphaned"

            # Delete auto-generated transactions (auto-saves, rollovers)
            # These are identified by transaction_type and are recreated during processing
            auto_generated_types = [TransactionType.ROLLOVER.value, TransactionType.SAVING.value]
            for trans in all_transactions:
                if trans.week_number in [original_paycheck.week_number, week2_number]:
                    if trans.transaction_type in auto_generated_types:
                        # Check if it's truly auto-generated (has no user description or specific patterns)
                        # Auto-saves have descriptions like "Savings allocation for..." or "Auto-savings allocation..."
                        desc = trans.description or ""
                        is_auto = (
                            "allocation for" in desc.lower() or
                            "auto-" in desc.lower() or
                            "end-of-period" in desc.lower() or
                            trans.transaction_type == TransactionType.ROLLOVER.value
                        )
                        if is_auto:
                            self.transaction_manager.delete_transaction(trans.id)

            # Update week dates
            current_week.start_date = new_start_date
            current_week.end_date = new_week1_end

            if current_week2:
                current_week2.start_date = new_week2_start
                current_week2.end_date = new_week2_end

            # Recreate auto-save transactions that were deleted
            # Uses PaycheckProcessor to ensure activation status is checked
            try:
                self._recreate_auto_save_transactions(
                    original_paycheck.week_number,
                    new_start_date,
                    updates.get("amount", original_paycheck.amount)
                )
            except Exception as e:
                print(f"Warning: Auto-save recreation failed: {e}")

        # Update paycheck amount and other fields
        simple_updates = {}
        if "date" in updates:
            simple_updates["date"] = updates["date"]
        if "amount" in updates:
            simple_updates["amount"] = updates["amount"]
        if "description" in updates:
            simple_updates["description"] = updates["description"]

        if simple_updates:
            self.transaction_manager.update_transaction(original_paycheck.id, simple_updates)

        # If amount changed, recalculate percentage-based auto-saves and rollovers
        if "amount" in updates and updates["amount"] != original_paycheck.amount:
            new_amount = updates["amount"]
            week2_number = original_paycheck.week_number + 1

            # Recalculate percentage-based auto-saves
            # These have descriptions containing "% of paycheck"
            try:
                self._recalculate_percentage_auto_saves(
                    original_paycheck.week_number,
                    week2_number,
                    new_amount
                )
            except Exception as e:
                print(f"Warning: Auto-save recalculation failed: {e}")

            # Trigger rollover recalculation for this paycheck period
            try:
                self.transaction_manager.trigger_rollover_recalculation(original_paycheck.week_number)
            except Exception as e:
                # Log but don't fail - the main update succeeded
                print(f"Warning: Rollover recalculation failed: {e}")

        changes = []
        if new_start_date and new_start_date != (current_week.start_date if current_week else None):
            changes.append(f"Start Date: {new_start_date}")
        if "amount" in updates:
            changes.append(f"Amount: ${updates['amount']:,.2f}")
        if "date" in updates:
            changes.append(f"Earned Date: {updates['date']}")

        return True, ", ".join(changes) if changes else "Updated"

    def _build_transfer_source_updates(self, updates, row_data):
        """Build updates dict for the source (withdrawal) side of a transfer"""
        source_updates = {}

        # Date applies to both
        if "date" in updates:
            source_updates["date"] = updates["date"]

        # Amount is negative for source (withdrawal)
        if "amount" in updates:
            source_updates["amount"] = -abs(updates["amount"])

        # From account becomes the account_id for source transaction
        if "from_account_id" in updates:
            source_updates["account_id"] = updates["from_account_id"]
            source_updates["bill_id"] = None
        elif "from_bill_id" in updates:
            source_updates["bill_id"] = updates["from_bill_id"]
            source_updates["account_id"] = None

        # Description
        if "description" in updates:
            source_updates["description"] = updates["description"]

        return source_updates

    def _build_transfer_dest_updates(self, updates, row_data):
        """Build updates dict for the destination (deposit) side of a transfer"""
        dest_updates = {}

        # Date applies to both
        if "date" in updates:
            dest_updates["date"] = updates["date"]

        # Amount is positive for dest (deposit)
        if "amount" in updates:
            dest_updates["amount"] = abs(updates["amount"])

        # To account becomes the account_id for dest transaction
        if "to_account_id" in updates:
            dest_updates["account_id"] = updates["to_account_id"]
            dest_updates["bill_id"] = None
        elif "to_bill_id" in updates:
            dest_updates["bill_id"] = updates["to_bill_id"]
            dest_updates["account_id"] = None

        # Description
        if "description" in updates:
            dest_updates["description"] = updates["description"]

        return dest_updates

    def _recalculate_percentage_auto_saves(self, week1_number, week2_number, new_paycheck_amount):
        """
        Recalculate percentage-based auto-saves when paycheck amount changes.

        Finds auto-save transactions with "% of paycheck" in description and
        recalculates their amounts based on the bill/account's percentage setting.
        """
        import re
        from models.transactions import TransactionType

        all_transactions = self.transaction_manager.get_all_transactions()

        for trans in all_transactions:
            # Only check transactions in this paycheck's weeks
            if trans.week_number not in [week1_number, week2_number]:
                continue

            # Only check SAVING type (auto-saves)
            if trans.transaction_type != TransactionType.SAVING.value:
                continue

            desc = trans.description or ""

            # Check if this is a percentage-based auto-save
            if "% of paycheck" not in desc:
                continue

            # Extract the percentage from the description (e.g., "10.0% of paycheck")
            match = re.search(r'\((\d+\.?\d*)% of paycheck\)', desc)
            if not match:
                continue

            percentage = float(match.group(1)) / 100.0  # Convert "10.0" to 0.1
            new_amount = percentage * new_paycheck_amount

            # Update the transaction with new amount
            self.transaction_manager.update_transaction(trans.id, {"amount": new_amount})

    def _recreate_auto_save_transactions(self, week_number: int, week_start_date, paycheck_amount: float):
        """
        Recreate auto-save transactions after they've been deleted during paycheck rebuild.

        This uses PaycheckProcessor's methods to ensure:
        1. Activation status is checked (inactive accounts/bills are skipped)
        2. Percentage-based vs fixed amount logic is applied correctly
        3. Transactions are created with proper descriptions

        Args:
            week_number: The week number for the transactions
            week_start_date: Start date of the pay period (used for activation check)
            paycheck_amount: The paycheck amount (for percentage-based calculations)
        """
        from services.paycheck_processor import PaycheckProcessor

        # Create a temporary processor to use its methods
        processor = PaycheckProcessor()

        try:
            # Recreate bill savings allocations
            # This checks bill.is_active_on(transaction_date) internally
            processor.update_bill_savings(week_number, week_start_date, paycheck_amount)

            # Recreate account auto-savings allocations
            # This checks account.is_active_on(transaction_date) internally
            processor.update_account_auto_savings(week_number, week_start_date, paycheck_amount)

        finally:
            processor.close()

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

            # Style info button (circular "i" button)
            info_btn = getattr(self, f"{tab_name}_info_btn", None)
            if info_btn:
                info_btn.setStyleSheet(f"""
                    QToolButton {{
                        background-color: {colors['primary']};
                        color: {colors['background']};
                        border: 2px solid {colors['primary']};
                        border-radius: 12px;
                        font-weight: bold;
                    }}
                    QToolButton:hover {{
                        background-color: {colors['accent']};
                        border-color: {colors['accent']};
                    }}
                    QToolButton:pressed {{
                        background-color: {colors['primary_dark']};
                        border-color: {colors['primary_dark']};
                    }}
                """)
