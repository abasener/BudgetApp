"""
Theme Selector Widget - Allows users to change themes
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import pyqtSignal
from themes import theme_manager


class ThemeSelector(QWidget):
    """Widget for selecting application theme"""
    
    theme_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # Connect to theme manager
        theme_manager.theme_changed.connect(self.on_theme_changed)
    
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        self.label = QLabel("Theme:")
        self.label.setFont(theme_manager.get_font("menu"))
        layout.addWidget(self.label)
        
        # Theme combo box
        self.theme_combo = QComboBox()
        self.theme_combo.setFont(theme_manager.get_font("menu"))
        self.populate_themes()
        self.theme_combo.currentTextChanged.connect(self.on_combo_changed)
        layout.addWidget(self.theme_combo)
        
        self.setLayout(layout)
        
        # Apply initial theme styling
        self.apply_dropdown_theme()
    
    def populate_themes(self):
        """Populate the combo box with available themes"""
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        
        available_themes = theme_manager.get_available_themes()
        for theme_id, theme_name in available_themes.items():
            self.theme_combo.addItem(theme_name, theme_id)
        
        # Select current theme
        current_theme = theme_manager.current_theme
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == current_theme:
                self.theme_combo.setCurrentIndex(i)
                break
        
        self.theme_combo.blockSignals(False)
    
    def on_combo_changed(self, theme_name):
        """Handle combo box selection change"""
        # Find theme ID by name
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemText(i) == theme_name:
                theme_id = self.theme_combo.itemData(i)
                if theme_id != theme_manager.current_theme:
                    theme_manager.set_theme(theme_id)
                    self.theme_changed.emit(theme_id)
                break
    
    def on_theme_changed(self, theme_id):
        """Handle theme change from theme manager"""
        # Update fonts for new theme
        self.label.setFont(theme_manager.get_font("menu"))
        self.theme_combo.setFont(theme_manager.get_font("menu"))
        
        # Apply theme styling to dropdown
        self.apply_dropdown_theme()
        
        # Update combo box selection
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == theme_id:
                self.theme_combo.blockSignals(True)
                self.theme_combo.setCurrentIndex(i)
                self.theme_combo.blockSignals(False)
                break
                
    def apply_dropdown_theme(self):
        """Apply current theme styling to the dropdown"""
        colors = theme_manager.get_colors()
        
        # Style the combo box and dropdown
        self.theme_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {colors['surface']};
                color: {colors['text_primary']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 4px 8px;
                padding-right: 20px;
            }}
            
            QComboBox:hover {{
                background-color: {colors['hover']};
            }}
            
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border: none;
            }}
            
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {colors['surface']};
                color: {colors['text_primary']};
                border: 1px solid {colors['border']};
                selection-background-color: {colors['primary']};
                selection-color: {colors['background']};
            }}
            
            QComboBox QAbstractItemView::item {{
                padding: 4px 8px;
            }}
            
            QComboBox QAbstractItemView::item:selected {{
                background-color: {colors['primary']};
                color: {colors['background']};
            }}
            
            QComboBox QAbstractItemView::item:hover {{
                background-color: {colors['hover']};
            }}
        """)