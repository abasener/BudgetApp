"""
Savings View - Individual savings account rows with progress bars, charts, and details
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QScrollArea, QPushButton, QComboBox)
from PyQt6.QtCore import Qt
from themes import theme_manager
from widgets import AccountRowWidget
from views.dialogs.settings_dialog import get_setting


class SavingsView(QWidget):
    def __init__(self, transaction_manager=None):
        super().__init__()
        self.transaction_manager = transaction_manager
        
        # Store account row widgets
        self.account_rows = []
        
        # Load sort option from settings
        self.current_sort = get_setting("savings_sort_order", "Alphabetical")
        
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
        """Create slim toolbar with refresh and sort options"""
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
        
        # Refresh button - slim design
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setFixedHeight(30)
        self.refresh_button.setFixedWidth(90)
        self.refresh_button.clicked.connect(self.refresh)
        self.refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['primary']};
                color: {colors['surface']};
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                padding: 2px 8px;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(colors['primary'], 1.1)};
            }}
            QPushButton:pressed {{
                background-color: {self.lighten_color(colors['primary'], 0.9)};
            }}
        """)
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
    
    def on_sort_changed(self, sort_option):
        """Handle sort option change"""
        self.current_sort = sort_option
        print(f"Savings sort changed to: {sort_option}")
        self.refresh()  # Refresh with new sort
    
    def sort_accounts(self, accounts):
        """Sort accounts according to current sort option"""
        if not accounts:
            return accounts
            
        try:
            if self.current_sort == "Alphabetical":
                return sorted(accounts, key=lambda a: (a.name or "").lower())
                
            elif self.current_sort == "Highest Balance":
                # Highest running_total first, alphabetical tiebreaker
                return sorted(accounts, key=lambda a: (-(a.running_total or 0), (a.name or "").lower()))
                
            elif self.current_sort == "Goal Progress":
                # Highest goal progress percentage first
                def progress_score(account):
                    if not account.goal_amount or account.goal_amount <= 0:
                        return (-1, (account.name or "").lower())  # No goal = lowest priority
                    progress = min(100, (account.running_total / account.goal_amount) * 100)
                    return (-progress, (account.name or "").lower())
                
                return sorted(accounts, key=progress_score)
                
            elif self.current_sort == "Goal Amount":
                # Highest goal amount first, alphabetical tiebreaker
                return sorted(accounts, key=lambda a: (-(a.goal_amount or 0), (a.name or "").lower()))
                
            else:
                # Default to alphabetical
                return sorted(accounts, key=lambda a: (a.name or "").lower())
                
        except Exception as e:
            print(f"Error sorting accounts: {e}")
            # Fall back to alphabetical
            return sorted(accounts, key=lambda a: (a.name or "").lower())
    
    def refresh(self):
        """Refresh savings view with current account data"""
        if not self.transaction_manager:
            self.show_no_data_message("Transaction manager not available")
            return
        
        try:
            # Reload sort setting from settings file
            self.current_sort = get_setting("savings_sort_order", "Alphabetical")
            # Get all accounts
            accounts = self.transaction_manager.get_all_accounts()
            
            if not accounts:
                self.show_no_data_message("No savings accounts configured")
                return
            
            # Sort accounts according to current sort option
            sorted_accounts = self.sort_accounts(accounts)
            
            # Clear existing account rows
            self.clear_account_rows()
            
            # Create account row widgets
            for account in sorted_accounts:
                account_row = AccountRowWidget(account, self.transaction_manager)
                
                # Connect signals for popup buttons
                account_row.see_more_clicked.connect(self.on_see_more_clicked)
                account_row.see_history_clicked.connect(self.on_see_history_clicked)
                
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
        """Clear all existing account row widgets"""
        for account_row in self.account_rows:
            account_row.setParent(None)
            account_row.deleteLater()
        
        self.account_rows.clear()
    
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
    
    def on_account_updated(self, updated_account):
        """Handle when account data is updated from dialogs"""
        try:
            # Refresh the entire savings view to reflect changes
            self.refresh()
            
        except Exception as e:
            print(f"Error refreshing savings view: {e}")
    
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
        
        # Update refresh button
        if hasattr(self, 'refresh_button'):
            self.refresh_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['primary']};
                    color: {colors['surface']};
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 2px 8px;
                }}
                QPushButton:hover {{
                    background-color: {self.lighten_color(colors['primary'], 1.1)};
                }}
                QPushButton:pressed {{
                    background-color: {self.lighten_color(colors['primary'], 0.9)};
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