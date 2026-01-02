"""
Savings View - Individual savings account rows with progress bars, charts, and details
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                             QScrollArea, QPushButton, QComboBox, QToolButton, QCheckBox)
from PyQt6.QtCore import Qt
from themes import theme_manager
from widgets import AccountRowWidget
from views.dialogs.settings_dialog import get_setting, save_setting


class SavingsView(QWidget):
    def __init__(self, transaction_manager=None):
        super().__init__()
        self.transaction_manager = transaction_manager

        # Store account row widgets
        self.account_rows = []

        # Load settings
        self.current_sort = get_setting("savings_sort_order", "Alphabetical")
        self.hide_inactive = get_setting("savings_hide_inactive", False)

        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("💰 Savings Accounts")
        title.setFont(theme_manager.get_font("title"))
        colors = theme_manager.get_colors()
        title.setStyleSheet(f"color: {colors['text_primary']};")
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Slim toolbar
        self.create_toolbar()
        self.apply_toolbar_theme()  # Apply initial theme styling
        main_layout.addWidget(self.toolbar)
        
        # Create scroll area for account rows
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Scroll content widget
        self.scroll_content = QWidget()
        self.accounts_layout = QVBoxLayout(self.scroll_content)
        self.accounts_layout.setSpacing(10)
        self.accounts_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add stretch at bottom to push account rows to top
        self.accounts_layout.addStretch()
        
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)
        
        self.setLayout(main_layout)
        
        # Style the scroll area
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {colors['border']};
                border-radius: 4px;
                background-color: {colors['surface']};
            }}
            QScrollBar:vertical {{
                background-color: {colors['surface_variant']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {colors['primary']};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {colors['accent']};
            }}
        """)
    
    def create_toolbar(self):
        """Create slim toolbar with add savings, refresh and sort options"""
        self.toolbar = QFrame()
        self.toolbar.setFrameStyle(QFrame.Shape.Box)
        self.toolbar.setFixedHeight(45)  # Slim height

        colors = theme_manager.get_colors()
        self.toolbar.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface_variant']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 2px;
            }}
        """)

        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setSpacing(8)
        toolbar_layout.setContentsMargins(8, 4, 8, 4)

        # Add Savings button - secondary focus
        self.add_savings_button = QPushButton("+ Savings")
        self.add_savings_button.setFont(theme_manager.get_font("button"))
        self.add_savings_button.setFixedHeight(30)
        self.add_savings_button.clicked.connect(self.on_add_savings_clicked)
        # Styling applied in apply_toolbar_theme method
        toolbar_layout.addWidget(self.add_savings_button)

        # Refresh button - compact tool button with just emoji (primary focus)
        self.refresh_button = QToolButton()
        self.refresh_button.setText("🔄")
        self.refresh_button.setToolTip("Refresh Savings")
        self.refresh_button.setFixedSize(40, 30)
        self.refresh_button.clicked.connect(self.refresh)
        # Styling applied in on_theme_changed method
        toolbar_layout.addWidget(self.refresh_button)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"color: {colors['border']};")
        toolbar_layout.addWidget(separator)

        # Sort label
        sort_label = QLabel("Sort by:")
        sort_label.setStyleSheet(f"color: {colors['text_primary']}; font-weight: bold; font-size: 12px;")
        toolbar_layout.addWidget(sort_label)

        # Sort dropdown - slim design
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Alphabetical",
            "Highest Balance",
            "Goal Progress",
            "Goal Amount"
        ])
        self.sort_combo.setCurrentText(self.current_sort)
        self.sort_combo.currentTextChanged.connect(self.on_sort_changed)
        self.sort_combo.setFixedHeight(30)
        self.sort_combo.setFixedWidth(120)
        self.sort_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 12px;
                color: {colors['text_primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {colors['text_secondary']};
                margin-right: 6px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                selection-background-color: {colors['primary']};
                selection-color: {colors['surface']};
            }}
        """)
        toolbar_layout.addWidget(self.sort_combo)

        # Separator before hide inactive
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setStyleSheet(f"color: {colors['border']};")
        toolbar_layout.addWidget(separator2)

        # Hide inactive checkbox
        self.hide_inactive_checkbox = QCheckBox("Hide inactive")
        self.hide_inactive_checkbox.setChecked(self.hide_inactive)
        self.hide_inactive_checkbox.stateChanged.connect(self.on_hide_inactive_changed)
        self.hide_inactive_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {colors['text_primary']};
                font-size: 12px;
                spacing: 5px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {colors['border']};
                border-radius: 3px;
                background-color: {colors['surface']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {colors['primary']};
                border-color: {colors['primary']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {colors['primary']};
            }}
        """)
        toolbar_layout.addWidget(self.hide_inactive_checkbox)

        # Push everything to the left
        toolbar_layout.addStretch()
    
    def lighten_color(self, color: str, factor: float) -> str:
        """Lighten or darken a hex color by a factor"""
        try:
            color = color.lstrip('#')
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            new_rgb = tuple(min(255, max(0, int(c * factor))) for c in rgb)
            return f"#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}"
        except:
            return color
    
    def apply_toolbar_theme(self):
        """Apply theme styling to toolbar elements"""
        colors = theme_manager.get_colors()

        # Style Add Savings button (QPushButton) - secondary focus
        if hasattr(self, 'add_savings_button'):
            self.add_savings_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['secondary']};
                    color: {colors['text_primary']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 4px 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {colors['accent']};
                    border-color: {colors['secondary']};
                }}
                QPushButton:pressed {{
                    background-color: {colors['selected']};
                }}
            """)

        # Style refresh button (QToolButton) - primary focus
        if hasattr(self, 'refresh_button'):
            self.refresh_button.setStyleSheet(f"""
                QToolButton {{
                    background-color: {colors['primary']};
                    color: {colors['text_primary']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 4px;
                    font-size: 16px;
                }}
                QToolButton:hover {{
                    background-color: {colors['primary_dark']};
                    border-color: {colors['primary']};
                }}
                QToolButton:pressed {{
                    background-color: {colors['selected']};
                }}
            """)

    def on_sort_changed(self, sort_option):
        """Handle sort option change"""
        self.current_sort = sort_option
        save_setting("savings_sort_order", sort_option)
        self.refresh()  # Refresh with new sort

    def on_hide_inactive_changed(self, state):
        """Handle hide inactive checkbox change"""
        self.hide_inactive = bool(state)
        save_setting("savings_hide_inactive", self.hide_inactive)
        self.refresh()  # Refresh with new filter

    def sort_accounts(self, accounts):
        """Sort accounts according to current sort option, always putting inactive accounts at bottom"""
        if not accounts:
            return accounts

        try:
            # First, separate active and inactive accounts
            active_accounts = [a for a in accounts if a.is_currently_active]
            inactive_accounts = [a for a in accounts if not a.is_currently_active]

            def sort_group(account_group):
                """Apply current sort to a group of accounts"""
                if not account_group:
                    return account_group

                if self.current_sort == "Alphabetical":
                    return sorted(account_group, key=lambda a: (a.name or "").lower())

                elif self.current_sort == "Highest Balance":
                    # Highest running_total first, alphabetical tiebreaker
                    return sorted(account_group, key=lambda a: (-(a.running_total or 0), (a.name or "").lower()))

                elif self.current_sort == "Goal Progress":
                    # Highest goal progress percentage first
                    def progress_score(account):
                        if not account.goal_amount or account.goal_amount <= 0:
                            return (-1, (account.name or "").lower())  # No goal = lowest priority
                        progress = min(100, (account.running_total / account.goal_amount) * 100)
                        return (-progress, (account.name or "").lower())

                    return sorted(account_group, key=progress_score)

                elif self.current_sort == "Goal Amount":
                    # Highest goal amount first, alphabetical tiebreaker
                    return sorted(account_group, key=lambda a: (-(a.goal_amount or 0), (a.name or "").lower()))

                else:
                    # Default to alphabetical
                    return sorted(account_group, key=lambda a: (a.name or "").lower())

            # Sort each group separately, then combine with active first
            sorted_active = sort_group(active_accounts)
            sorted_inactive = sort_group(inactive_accounts)

            return sorted_active + sorted_inactive

        except Exception as e:
            print(f"Error sorting accounts: {e}")
            # Fall back to alphabetical with inactive at bottom
            active = [a for a in accounts if a.is_currently_active]
            inactive = [a for a in accounts if not a.is_currently_active]
            return sorted(active, key=lambda a: (a.name or "").lower()) + sorted(inactive, key=lambda a: (a.name or "").lower())
    
    def refresh(self):
        """Refresh savings view with current account data"""
        if not self.transaction_manager:
            self.show_no_data_message("Transaction manager not available")
            return

        try:
            # Reload settings from settings file
            self.current_sort = get_setting("savings_sort_order", "Alphabetical")
            self.hide_inactive = get_setting("savings_hide_inactive", False)

            # Update checkbox state without triggering signal
            if hasattr(self, 'hide_inactive_checkbox'):
                self.hide_inactive_checkbox.blockSignals(True)
                self.hide_inactive_checkbox.setChecked(self.hide_inactive)
                self.hide_inactive_checkbox.blockSignals(False)

            # Get all accounts
            accounts = self.transaction_manager.get_all_accounts()

            if not accounts:
                self.show_no_data_message("No savings accounts configured")
                return

            # Filter out inactive accounts if hide_inactive is enabled
            if self.hide_inactive:
                accounts = [a for a in accounts if a.is_currently_active]

                if not accounts:
                    self.show_no_data_message("No active accounts (inactive accounts are hidden)")
                    return

            # Sort accounts according to current sort option
            sorted_accounts = self.sort_accounts(accounts)

            # Clear existing account rows
            self.clear_account_rows()

            # Separate active and inactive for adding spacer
            active_accounts = [a for a in sorted_accounts if a.is_currently_active]
            inactive_accounts = [a for a in sorted_accounts if not a.is_currently_active]

            # Create account row widgets for active accounts
            for account in active_accounts:
                account_row = AccountRowWidget(account, self.transaction_manager, is_active=True)

                # Connect signals for popup buttons
                account_row.see_more_clicked.connect(self.on_see_more_clicked)
                account_row.see_history_clicked.connect(self.on_see_history_clicked)
                account_row.activation_changed.connect(self.on_account_activation_changed)

                # Add to layout (insert before stretch)
                self.accounts_layout.insertWidget(self.accounts_layout.count() - 1, account_row)
                self.account_rows.append(account_row)

            # Add spacer with divider line between active and inactive sections
            if active_accounts and inactive_accounts:
                colors = theme_manager.get_colors()
                # Create a container widget with a centered horizontal line
                spacer_container = QWidget()
                spacer_layout = QVBoxLayout(spacer_container)
                spacer_layout.setContentsMargins(20, 10, 20, 10)  # Horizontal margins for the line, vertical for spacing
                spacer_layout.setSpacing(0)

                # Create the divider line (same style as account borders)
                divider = QFrame()
                divider.setFrameShape(QFrame.Shape.HLine)
                divider.setFixedHeight(2)  # Thin line like borders
                divider.setStyleSheet(f"background-color: {colors['border']}; border: none;")

                spacer_layout.addWidget(divider)
                self.accounts_layout.insertWidget(self.accounts_layout.count() - 1, spacer_container)

            # Create account row widgets for inactive accounts
            for account in inactive_accounts:
                account_row = AccountRowWidget(account, self.transaction_manager, is_active=False)

                # Connect signals for popup buttons
                account_row.see_more_clicked.connect(self.on_see_more_clicked)
                account_row.see_history_clicked.connect(self.on_see_history_clicked)
                account_row.activation_changed.connect(self.on_account_activation_changed)

                # Add to layout (insert before stretch)
                self.accounts_layout.insertWidget(self.accounts_layout.count() - 1, account_row)
                self.account_rows.append(account_row)


        except Exception as e:
            error_msg = f"Error refreshing savings accounts: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.show_no_data_message(error_msg)
    
    def clear_account_rows(self):
        """Clear all existing account row widgets and dividers"""
        # Clear tracked account rows
        for account_row in self.account_rows:
            account_row.setParent(None)
            account_row.deleteLater()
        self.account_rows.clear()

        # Also clear any divider/spacer widgets that were added to the layout
        # We need to remove all widgets except the stretch at the end
        while self.accounts_layout.count() > 1:  # Keep the stretch
            item = self.accounts_layout.takeAt(0)
            widget = item.widget() if item else None
            if widget:
                widget.setParent(None)
                widget.deleteLater()
    
    def show_no_data_message(self, message: str):
        """Show a message when no accounts are available"""
        self.clear_account_rows()
        
        # Create message widget
        message_widget = QWidget()
        message_layout = QVBoxLayout(message_widget)
        message_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        colors = theme_manager.get_colors()
        
        # Message label
        message_label = QLabel(message)
        message_label.setFont(theme_manager.get_font("subtitle"))
        message_label.setStyleSheet(f"color: {colors['text_secondary']}; padding: 50px;")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_layout.addWidget(message_label)
        
        # Add to layout
        self.accounts_layout.insertWidget(0, message_widget)
    
    def on_see_more_clicked(self, account):
        """Handle 'See More' button click - open account editor"""
        try:
            from views.dialogs.account_editor_dialog import AccountEditorDialog
            
            dialog = AccountEditorDialog(account, self.transaction_manager, self)
            dialog.account_updated.connect(self.on_account_updated)
            dialog.exec()
            
        except Exception as e:
            print(f"Error opening account editor: {e}")
            import traceback
            traceback.print_exc()
    
    def on_see_history_clicked(self, account):
        """Handle 'See History' button click - open transaction history"""
        try:
            from views.dialogs.account_transaction_history_dialog import AccountTransactionHistoryDialog
            
            dialog = AccountTransactionHistoryDialog(account, self.transaction_manager, self)
            dialog.account_updated.connect(self.on_account_updated)
            dialog.exec()
            
        except Exception as e:
            print(f"Error opening account transaction history: {e}")
            import traceback
            traceback.print_exc()

    def on_account_activation_changed(self, account, is_active):
        """Handle when an account's activation status is changed via the toggle"""
        print(f"[DEBUG] on_account_activation_changed called: {account.name}, is_active={is_active}")
        print(f"[DEBUG] account.is_currently_active = {account.is_currently_active}")
        try:
            # Refresh the entire view to reflect the new active/inactive status
            # This will re-sort accounts and update visual styling
            self.refresh()
        except Exception as e:
            print(f"Error refreshing after activation change: {e}")

    def on_account_updated(self, updated_account):
        """Handle when account data is updated from dialogs"""
        try:
            # Refresh the entire savings view to reflect changes
            self.refresh()

        except Exception as e:
            print(f"Error refreshing savings view: {e}")

    def on_add_savings_clicked(self):
        """Handle Add Savings button click - open add account dialog"""
        try:
            from views.dialogs.add_account_dialog import AddAccountDialog
            from PyQt6.QtWidgets import QDialog

            dialog = AddAccountDialog(self.transaction_manager, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh()

        except Exception as e:
            print(f"Error opening add account dialog: {e}")
            import traceback
            traceback.print_exc()
    
    def on_theme_changed(self, theme_id):
        """Handle theme change for savings view - optimized for performance"""
        try:
            # Update UI styling without recalculating data
            self.update_view_styling()
            # Account row widgets will auto-update via their own theme_changed signals
        except Exception as e:
            print(f"Error applying theme to savings view: {e}")
    
    def update_view_styling(self):
        """Update only the visual styling of the savings view"""
        colors = theme_manager.get_colors()
        
        # Update header title color
        for child in self.findChildren(QLabel):
            if "Savings Accounts" in child.text():
                child.setStyleSheet(f"color: {colors['text_primary']};")
        
        # Update toolbar styling
        if hasattr(self, 'toolbar'):
            self.toolbar.setStyleSheet(f"""
                QFrame {{
                    background-color: {colors['surface_variant']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 2px;
                }}
            """)
        
        # Update Add Savings button (QPushButton) - secondary focus
        if hasattr(self, 'add_savings_button'):
            self.add_savings_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['secondary']};
                    color: {colors['text_primary']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 4px 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {colors['accent']};
                    border-color: {colors['secondary']};
                }}
                QPushButton:pressed {{
                    background-color: {colors['selected']};
                }}
            """)

        # Update refresh button (QToolButton) - primary focus
        if hasattr(self, 'refresh_button'):
            self.refresh_button.setStyleSheet(f"""
                QToolButton {{
                    background-color: {colors['primary']};
                    color: {colors['text_primary']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 4px;
                    font-size: 16px;
                }}
                QToolButton:hover {{
                    background-color: {colors['primary_dark']};
                    border-color: {colors['primary']};
                }}
                QToolButton:pressed {{
                    background-color: {colors['selected']};
                }}
            """)
        
        # Update sort dropdown
        if hasattr(self, 'sort_combo'):
            self.sort_combo.setStyleSheet(f"""
                QComboBox {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 2px 8px;
                    font-size: 12px;
                    color: {colors['text_primary']};
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 20px;
                }}
                QComboBox::down-arrow {{
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 4px solid {colors['text_secondary']};
                    margin-right: 6px;
                }}
                QComboBox QAbstractItemView {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    selection-background-color: {colors['primary']};
                    selection-color: {colors['surface']};
                }}
            """)

        # Update hide inactive checkbox
        if hasattr(self, 'hide_inactive_checkbox'):
            self.hide_inactive_checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {colors['text_primary']};
                    font-size: 12px;
                    spacing: 5px;
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 1px solid {colors['border']};
                    border-radius: 3px;
                    background-color: {colors['surface']};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {colors['primary']};
                    border-color: {colors['primary']};
                }}
                QCheckBox::indicator:hover {{
                    border-color: {colors['primary']};
                }}
            """)

        # Update scroll area and its content widget
        if hasattr(self, 'scroll_area'):
            self.scroll_area.setStyleSheet(f"""
                QScrollArea {{
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    background-color: {colors['background']};
                }}
                QScrollBar:vertical {{
                    background-color: {colors['surface_variant']};
                    width: 12px;
                    border-radius: 6px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: {colors['primary']};
                    border-radius: 6px;
                    min-height: 20px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background-color: {colors.get('accent', colors['primary'])};
                }}
            """)
            
            # Update scroll content widget background
            if hasattr(self, 'scroll_content'):
                self.scroll_content.setStyleSheet(f"""
                    QWidget {{
                        background-color: {colors['background']};
                    }}
                """)