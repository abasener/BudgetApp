"""
Add Category Dialog - Dialog for adding new spending categories
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QCompleter, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QFont
from themes import theme_manager
import difflib


class AddCategoryDialog(QDialog):
    def __init__(self, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager
        self.setWindowTitle("Add New Category")
        self.setFixedSize(400, 200)
        
        self.init_ui()
        
    def init_ui(self):
        colors = theme_manager.get_colors()
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📝 Add New Category")
        title.setFont(theme_manager.get_font("subtitle"))
        title.setStyleSheet(f"color: {colors['text_primary']}; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Instructions
        instructions = QLabel("Enter a new category name. Suggestions will appear as you type.")
        instructions.setFont(theme_manager.get_font("small"))
        instructions.setStyleSheet(f"color: {colors['text_secondary']}; margin-bottom: 10px;")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setWordWrap(True)
        main_layout.addWidget(instructions)
        
        # Input section
        input_frame = QFrame()
        input_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 10px;
            }}
        """)
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(8)
        
        # Category name label
        name_label = QLabel("Category Name:")
        name_label.setFont(theme_manager.get_font("small"))
        name_label.setStyleSheet(f"color: {colors['text_primary']}; font-weight: bold;")
        input_layout.addWidget(name_label)
        
        # Category name input with autocomplete
        self.category_input = QLineEdit()
        self.category_input.setFixedHeight(35)
        self.category_input.setFont(theme_manager.get_font("input"))
        self.category_input.setPlaceholderText("e.g., Entertainment, Food, Transportation...")
        self.category_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {colors['background']};
                border: 2px solid {colors['border']};
                border-radius: 4px;
                padding: 8px 12px;
                color: {colors['text_primary']};
            }}
            QLineEdit:focus {{
                border-color: {colors['primary']};
            }}
        """)
        
        # Setup autocomplete with existing categories
        self.setup_autocomplete()
        
        input_layout.addWidget(self.category_input)
        main_layout.addWidget(input_frame)
        
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
        
        # Add button
        self.add_btn = QPushButton("Add Category")
        self.add_btn.setFixedHeight(35)
        self.add_btn.setFixedWidth(120)
        self.add_btn.setFont(theme_manager.get_font("button"))
        self.add_btn.clicked.connect(self.add_category)
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['primary']};
                color: {colors['background']};
                border: 1px solid {colors['primary_dark'] if colors.get('primary_dark') else colors['border']};
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors.get('primary_dark', colors['primary'])};
            }}
            QPushButton:disabled {{
                background-color: {colors.get('surface_variant', colors['surface'])};
                color: {colors.get('text_secondary', colors['text_primary'])};
                border-color: {colors['border']};
            }}
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.add_btn)
        
        main_layout.addLayout(button_layout)
        
        # Connect input change to validation
        self.category_input.textChanged.connect(self.validate_input)
        self.validate_input()  # Initial validation
        
        self.setLayout(main_layout)
        
        # Style the dialog
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['background']};
                border: 2px solid {colors['primary']};
                border-radius: 8px;
            }}
        """)
        
        # Focus on input
        self.category_input.setFocus()
        
    def setup_autocomplete(self):
        """Setup autocomplete with existing categories"""
        try:
            # Get all existing categories from transactions
            existing_categories = self.transaction_manager.get_all_categories()
            if existing_categories:
                # Create completer with existing categories
                completer = QCompleter(existing_categories)
                completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
                completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                self.category_input.setCompleter(completer)
                
                # Store categories for validation
                self.existing_categories = [cat.lower().strip() for cat in existing_categories]
            else:
                self.existing_categories = []
                
        except Exception as e:
            print(f"Error setting up autocomplete: {e}")
            self.existing_categories = []
    
    def validate_input(self):
        """Validate input and enable/disable add button"""
        category_name = self.category_input.text().strip()
        
        if not category_name:
            self.add_btn.setEnabled(False)
            return
            
        # Only check for exact duplicates - allow similar names
        is_duplicate = self.is_exact_duplicate(category_name)
        self.add_btn.setEnabled(not is_duplicate)
        
        # Don't show warnings here - they'll be shown in the confirmation dialog
    
    def is_exact_duplicate(self, category_name):
        """Check if category name is an exact duplicate (case-insensitive)"""
        if not category_name or not category_name.strip():
            return False
            
        category_lower = category_name.lower().strip()
        return category_lower in self.existing_categories
    
    def find_similar_categories(self, category_name):
        """Find categories that are similar to the given name"""
        if not category_name or not category_name.strip():
            return []
            
        category_lower = category_name.lower().strip()
        similar_categories = []
        
        for existing_cat in self.existing_categories:
            # Calculate similarity ratio
            similarity = difflib.SequenceMatcher(None, category_lower, existing_cat.lower()).ratio()
            
            # If similarity is high (>0.75), it's likely similar
            if similarity > 0.75:
                similar_categories.append((existing_cat, similarity))
            
            # Also check if one is a substring of the other (like "Food" vs "Foods")
            elif (category_lower in existing_cat.lower() or existing_cat.lower() in category_lower) and \
               abs(len(category_lower) - len(existing_cat)) <= 3:
                similar_categories.append((existing_cat, 0.8))  # Assign high similarity for substrings
        
        # Sort by similarity (highest first) and return just the category names
        similar_categories.sort(key=lambda x: x[1], reverse=True)
        return [cat[0] for cat in similar_categories[:3]]  # Return top 3 similar categories
    
    def add_category(self):
        """Add the new category with confirmation dialog"""
        category_name = self.category_input.text().strip()
        
        if not category_name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a category name.")
            return
        
        # Check for exact duplicates
        if self.is_exact_duplicate(category_name):
            QMessageBox.warning(self, "Duplicate Category", 
                              f"Category '{category_name}' already exists.")
            return
        
        # Show confirmation dialog with similarity warnings
        if not self.show_confirmation_dialog(category_name):
            return  # User cancelled
        
        try:
            # Add category to the database
            success = self.transaction_manager.add_category(category_name)
            
            if success:
                QMessageBox.information(self, "Success", 
                                      f"Category '{category_name}' has been added successfully!")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", 
                                  "Failed to add category. Please try again.")
                
        except Exception as e:
            print(f"Error adding category: {e}")
            QMessageBox.critical(self, "Error", 
                               f"An error occurred while adding the category:\n{str(e)}")
    
    def show_confirmation_dialog(self, category_name):
        """Show confirmation dialog with similarity warnings"""
        similar_categories = self.find_similar_categories(category_name)
        
        # Build confirmation message
        message = f"You are about to add '{category_name}'"
        
        if similar_categories:
            if len(similar_categories) == 1:
                message += f"\n\n⚠️  This category is similar to: '{similar_categories[0]}'"
            else:
                similar_list = "', '".join(similar_categories)
                message += f"\n\n⚠️  This category is similar to: '{similar_list}'"
            
            message += "\n\nAre you sure you want to add this category?"
        else:
            message += "\n\nAre you sure?"
        
        # Show confirmation dialog
        reply = QMessageBox.question(
            self, 
            "Confirm Add Category",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # Default to No for safety
        )
        
        return reply == QMessageBox.StandardButton.Yes