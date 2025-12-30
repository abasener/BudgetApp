"""
Bills View - Individual bill rows with progress bars, charts, and details
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                             QScrollArea, QPushButton, QComboBox, QToolButton)
from PyQt6.QtCore import Qt
from themes import theme_manager
from widgets import BillRowWidget
from views.dialogs.settings_dialog import get_setting, save_setting


class BillsView(QWidget):
    def __init__(self, transaction_manager=None):
        super().__init__()
        self.transaction_manager = transaction_manager
        
        # Store bill row widgets
        self.bill_rows = []
        
        # Load sort option from settings
        self.current_sort = get_setting("bills_sort_order", "Alphabetical")
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("🧾 Bills Tab & Popups")
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
        
        # Create scroll area for bill rows
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Scroll content widget
        self.scroll_content = QWidget()
        self.bills_layout = QVBoxLayout(self.scroll_content)
        self.bills_layout.setSpacing(10)
        self.bills_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add stretch at bottom to push bill rows to top
        self.bills_layout.addStretch()
        
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
        """Create slim toolbar with add bill, refresh and sort options"""
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

        # Add Bill button - secondary focus
        self.add_bill_button = QPushButton("+ Bill")
        self.add_bill_button.setFont(theme_manager.get_font("button"))
        self.add_bill_button.setFixedHeight(30)
        self.add_bill_button.clicked.connect(self.on_add_bill_clicked)
        # Styling applied in apply_toolbar_theme method
        toolbar_layout.addWidget(self.add_bill_button)

        # Refresh button - compact tool button with just emoji (primary focus)
        self.refresh_button = QToolButton()
        self.refresh_button.setText("🔄")
        self.refresh_button.setToolTip("Refresh Bills")
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
            "Richest",
            "Closest",
            "Payment Size"
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
    
    def apply_toolbar_theme(self):
        """Apply theme styling to toolbar elements"""
        colors = theme_manager.get_colors()

        # Style Add Bill button (QPushButton) - secondary focus
        if hasattr(self, 'add_bill_button'):
            self.add_bill_button.setStyleSheet(f"""
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
        save_setting("bills_sort_order", sort_option)
        self.refresh()  # Refresh with new sort
    
    
    def sort_bills(self, bills):
        """Sort bills according to current sort option"""
        if not bills:
            return bills
            
        try:
            if self.current_sort == "Alphabetical":
                return sorted(bills, key=lambda b: (b.name or "").lower())
                
            elif self.current_sort == "Richest":
                # Highest running_total first, alphabetical tiebreaker
                return sorted(bills, key=lambda b: (-(b.running_total or 0), (b.name or "").lower()))
                
            elif self.current_sort == "Closest":
                # Most urgent payment due first
                from datetime import datetime, timedelta
                today = datetime.now().date()
                
                def urgency_score(bill):
                    if not bill.last_payment_date:
                        return (999999, (bill.name or "").lower())  # No date = least urgent (end of list)
                    
                    # Calculate when next payment is due
                    frequency = getattr(bill, 'payment_frequency', 'monthly').lower()
                    if frequency == 'weekly':
                        cycle_days = 7
                    elif frequency == 'monthly':
                        cycle_days = 30
                    elif frequency == 'quarterly':
                        cycle_days = 90
                    elif frequency == 'yearly':
                        cycle_days = 365
                    else:
                        cycle_days = 30
                    
                    if isinstance(bill.last_payment_date, str):
                        last_payment = datetime.strptime(bill.last_payment_date, '%Y-%m-%d').date()
                    else:
                        last_payment = bill.last_payment_date
                    
                    next_due = last_payment + timedelta(days=cycle_days)
                    days_until_due = (next_due - today).days
                    
                    return (days_until_due, (bill.name or "").lower())
                
                return sorted(bills, key=urgency_score)
                
            elif self.current_sort == "Payment Size":
                # Highest typical_amount first, alphabetical tiebreaker
                return sorted(bills, key=lambda b: (-(b.typical_amount or 0), (b.name or "").lower()))
                
            else:
                # Default to alphabetical
                return sorted(bills, key=lambda b: (b.name or "").lower())
                
        except Exception as e:
            print(f"Error sorting bills: {e}")
            # Fall back to alphabetical
            return sorted(bills, key=lambda b: (b.name or "").lower())
    
    def refresh(self):
        """Refresh bills view with current bill data"""
        if not self.transaction_manager:
            self.show_no_data_message("Transaction manager not available")
            return
        
        try:
            # Reload sort setting from settings file
            self.current_sort = get_setting("bills_sort_order", "Alphabetical")
            # Get all bills
            bills = self.transaction_manager.get_all_bills()
            
            if not bills:
                self.show_no_data_message("No bills configured")
                return
            
            # Sort bills according to current sort option
            sorted_bills = self.sort_bills(bills)
            
            # Clear existing bill rows
            self.clear_bill_rows()
            
            # Create bill row widgets
            for bill in sorted_bills:
                bill_row = BillRowWidget(bill, self.transaction_manager)
                
                # Connect signals for popup buttons (placeholder for now)
                bill_row.see_more_clicked.connect(self.on_see_more_clicked)
                bill_row.see_history_clicked.connect(self.on_see_history_clicked)
                
                # Add to layout (insert before stretch)
                self.bills_layout.insertWidget(self.bills_layout.count() - 1, bill_row)
                self.bill_rows.append(bill_row)
            
            
        except Exception as e:
            error_msg = f"Error refreshing bills: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.show_no_data_message(error_msg)
    
    def clear_bill_rows(self):
        """Clear all existing bill row widgets"""
        for bill_row in self.bill_rows:
            bill_row.setParent(None)
            bill_row.deleteLater()
        
        self.bill_rows.clear()
    
    def show_no_data_message(self, message: str):
        """Show a message when no bills are available"""
        self.clear_bill_rows()
        
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
        self.bills_layout.insertWidget(0, message_widget)
    
    def on_see_more_clicked(self, bill):
        """Handle 'See More' button click - open bill editor"""
        try:
            from views.dialogs.bill_editor_dialog import BillEditorDialog

            # Refresh bill data to ensure we have latest running_total values
            refreshed_bill = self.transaction_manager.get_bill_by_id(bill.id)
            if refreshed_bill:
                bill = refreshed_bill

            dialog = BillEditorDialog(bill, self.transaction_manager, self)
            dialog.bill_updated.connect(self.on_bill_updated)
            dialog.exec()
            
        except Exception as e:
            print(f"Error opening bill editor: {e}")
            import traceback
            traceback.print_exc()
    
    def on_see_history_clicked(self, bill):
        """Handle 'See History' button click - open transaction history"""
        try:
            from views.dialogs.bill_transaction_history_dialog import BillTransactionHistoryDialog

            dialog = BillTransactionHistoryDialog(bill, self.transaction_manager, parent=self)
            dialog.bill_updated.connect(self.on_bill_updated)
            dialog.exec()

        except Exception as e:
            import traceback
            traceback.print_exc()
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error Opening History", f"Failed to open transaction history:\n{str(e)}\n\nCheck console for details.")
    
    def on_bill_updated(self, updated_bill):
        """Handle when bill data is updated from dialogs"""
        try:
            # Refresh the entire bills view to reflect changes
            self.refresh()

        except Exception as e:
            print(f"Error refreshing bills view: {e}")

    def on_add_bill_clicked(self):
        """Handle Add Bill button click - open add bill dialog"""
        try:
            from views.dialogs.add_bill_dialog import AddBillDialog
            from PyQt6.QtWidgets import QDialog

            dialog = AddBillDialog(self.transaction_manager, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh()

        except Exception as e:
            print(f"Error opening add bill dialog: {e}")
            import traceback
            traceback.print_exc()
    
    def on_theme_changed(self, theme_id):
        """Handle theme change for bills view - optimized for performance"""
        try:
            # Update UI styling without recalculating data
            self.update_view_styling()
            # Bill row widgets will auto-update via their own theme_changed signals
        except Exception as e:
            print(f"Error applying theme to bills view: {e}")
    
    def update_view_styling(self):
        """Update only the visual styling of the bills view"""
        colors = theme_manager.get_colors()
        
        # Update header title color
        for child in self.findChildren(QLabel):
            if "Bills Tab" in child.text():
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
        
        # Update Add Bill button (QPushButton) - secondary focus
        if hasattr(self, 'add_bill_button'):
            self.add_bill_button.setStyleSheet(f"""
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