"""
Remove Category Dialog - Dialog for removing categories and reassigning transactions
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                             QPushButton, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from themes import theme_manager


class RemoveCategoryDialog(QDialog):
    def __init__(self, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager
        self.setWindowTitle("Remove Category")
        self.setFixedSize(450, 280)
        
        # Get all categories
        self.all_categories = self.transaction_manager.get_all_categories()
        
        if len(self.all_categories) < 2:
            # Need at least 2 categories (one to remove, one to reassign to)
            QMessageBox.warning(parent, "Cannot Remove Category", 
                              "You need at least 2 categories to perform this operation.\n"
                              "You cannot remove a category if there's nowhere to reassign the transactions.")
            self.reject()
            return
        
        self.init_ui()
        
    def init_ui(self):
        colors = theme_manager.get_colors()
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🗑️ Remove Category")
        title.setFont(theme_manager.get_font("subtitle"))
        title.setStyleSheet(f"color: {colors['text_primary']}; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Warning message
        warning = QLabel("⚠️ This will permanently remove the category and reassign all existing transactions.")
        warning.setFont(theme_manager.get_font("small"))
        warning.setStyleSheet(f"color: {colors.get('warning', colors['text_secondary'])}; margin-bottom: 15px;")
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning.setWordWrap(True)
        main_layout.addWidget(warning)
        
        # Selection section
        selection_frame = QFrame()
        selection_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 15px;
            }}
        """)
        selection_layout = QVBoxLayout(selection_frame)
        selection_layout.setSpacing(12)
        
        # Category to remove section
        remove_section = QVBoxLayout()
        remove_section.setSpacing(5)
        
        remove_label = QLabel("Category to Remove:")
        remove_label.setFont(theme_manager.get_font("small"))
        remove_label.setStyleSheet(f"color: {colors['text_primary']}; font-weight: bold;")
        remove_section.addWidget(remove_label)
        
        self.remove_combo = QComboBox()
        self.remove_combo.addItems(self.all_categories)
        self.remove_combo.setFixedHeight(35)
        self.remove_combo.setFont(theme_manager.get_font("input"))
        self.remove_combo.currentTextChanged.connect(self.on_remove_category_changed)
        self.remove_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {colors['background']};
                border: 2px solid {colors['border']};
                border-radius: 4px;
                padding: 8px 12px;
                color: {colors['text_primary']};
            }}
            QComboBox:focus {{
                border-color: {colors.get('error', colors['primary'])};
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
        remove_section.addWidget(self.remove_combo)
        selection_layout.addLayout(remove_section)
        
        # Replacement category section  
        replace_section = QVBoxLayout()
        replace_section.setSpacing(5)
        
        replace_label = QLabel("Reassign Transactions to:")
        replace_label.setFont(theme_manager.get_font("small"))
        replace_label.setStyleSheet(f"color: {colors['text_primary']}; font-weight: bold;")
        replace_section.addWidget(replace_label)
        
        self.replace_combo = QComboBox()
        self.replace_combo.setFixedHeight(35)
        self.replace_combo.setFont(theme_manager.get_font("input"))
        self.replace_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {colors['background']};
                border: 2px solid {colors['border']};
                border-radius: 4px;
                padding: 8px 12px;
                color: {colors['text_primary']};
            }}
            QComboBox:focus {{
                border-color: {colors['primary']};
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
        replace_section.addWidget(self.replace_combo)
        selection_layout.addLayout(replace_section)
        
        main_layout.addWidget(selection_frame)
        
        # Transaction count info
        self.info_label = QLabel()
        self.info_label.setFont(theme_manager.get_font("small"))
        self.info_label.setStyleSheet(f"color: {colors['text_secondary']}; font-style: italic;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setWordWrap(True)
        main_layout.addWidget(self.info_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(35)
        cancel_btn.setFixedWidth(100)
        cancel_btn.setFont(theme_manager.get_font("button"))
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['surface']};
                color: {colors['text_primary']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {colors.get('hover', colors['surface_variant'])};
            }}
        """)
        
        # Remove button
        self.remove_btn = QPushButton("Remove Category")
        self.remove_btn.setFixedHeight(35)
        self.remove_btn.setFixedWidth(140)
        self.remove_btn.setFont(theme_manager.get_font("button"))
        self.remove_btn.clicked.connect(self.remove_category)
        self.remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('error', '#e74c3c')};
                color: white;
                border: 1px solid {colors.get('error', '#e74c3c')};
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #c0392b;
            }}
            QPushButton:disabled {{
                background-color: {colors.get('surface_variant', colors['surface'])};
                color: {colors.get('text_secondary', colors['text_primary'])};
                border-color: {colors['border']};
            }}
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.remove_btn)
        
        main_layout.addLayout(button_layout)
        
        # Initialize the replacement dropdown
        self.on_remove_category_changed()
        
        self.setLayout(main_layout)
        
        # Style the dialog
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['background']};
                border: 2px solid {colors.get('error', colors['primary'])};
                border-radius: 8px;
            }}
        """)
        
    def on_remove_category_changed(self):
        """Update replacement dropdown when remove category changes"""
        selected_category = self.remove_combo.currentText()
        
        # Populate replacement dropdown with all categories except the selected one
        replacement_options = [cat for cat in self.all_categories if cat != selected_category]
        
        self.replace_combo.clear()
        self.replace_combo.addItems(replacement_options)
        
        # Update info about transaction count
        self.update_transaction_info(selected_category)
    
    def update_transaction_info(self, category_to_remove):
        """Update the info label with transaction count"""
        try:
            # Get transactions for this category
            transactions = self.transaction_manager.get_transactions_by_category(category_to_remove)
            count = len(transactions)
            
            if count == 0:
                self.info_label.setText(f"No transactions found for '{category_to_remove}'")
            elif count == 1:
                self.info_label.setText(f"1 transaction will be reassigned")
            else:
                self.info_label.setText(f"{count} transactions will be reassigned")
                
        except Exception as e:
            print(f"Error getting transaction count: {e}")
            self.info_label.setText("Unable to determine transaction count")
    
    def remove_category(self):
        """Remove the category after confirmation"""
        category_to_remove = self.remove_combo.currentText()
        replacement_category = self.replace_combo.currentText()
        
        if not category_to_remove or not replacement_category:
            QMessageBox.warning(self, "Invalid Selection", 
                              "Please select both a category to remove and a replacement category.")
            return
        
        if category_to_remove == replacement_category:
            QMessageBox.warning(self, "Invalid Selection", 
                              "Cannot replace a category with itself.")
            return
        
        # Show confirmation dialog
        if not self.show_confirmation_dialog(category_to_remove, replacement_category):
            return  # User cancelled
        
        try:
            # Remove category and reassign transactions
            success = self.transaction_manager.remove_category(category_to_remove, replacement_category)
            
            if success:
                QMessageBox.information(self, "Success", 
                                      f"Category '{category_to_remove}' has been removed successfully!\n"
                                      f"All transactions have been reassigned to '{replacement_category}'.")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", 
                                  "Failed to remove category. Please try again.")
                
        except Exception as e:
            print(f"Error removing category: {e}")
            QMessageBox.critical(self, "Error", 
                               f"An error occurred while removing the category:\n{str(e)}")
    
    def show_confirmation_dialog(self, category_to_remove, replacement_category):
        """Show confirmation dialog for category removal"""
        try:
            # Get transaction count for more specific messaging
            transactions = self.transaction_manager.get_transactions_by_category(category_to_remove)
            count = len(transactions)
            
            if count == 0:
                message = f"Are you sure you want to remove '{category_to_remove}'?\n\n"
                message += "No existing transactions will be affected."
            elif count == 1:
                message = f"Are you sure you want to remove '{category_to_remove}'?\n\n"
                message += f"1 existing transaction will be changed to '{replacement_category}'."
            else:
                message = f"Are you sure you want to remove '{category_to_remove}'?\n\n"
                message += f"{count} existing transactions will be changed to '{replacement_category}'."
                
        except Exception as e:
            print(f"Error getting transaction count for confirmation: {e}")
            message = f"Are you sure you want to remove '{category_to_remove}'?\n\n"
            message += f"Existing references to it will be changed to '{replacement_category}'."
        
        # Show confirmation dialog
        reply = QMessageBox.question(
            self, 
            "Confirm Remove Category",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # Default to No for safety
        )
        
        return reply == QMessageBox.StandardButton.Yes