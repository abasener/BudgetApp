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
        label = QLabel("Theme:")
        layout.addWidget(label)
        
        # Theme combo box
        self.theme_combo = QComboBox()
        self.populate_themes()
        self.theme_combo.currentTextChanged.connect(self.on_combo_changed)
        layout.addWidget(self.theme_combo)
        
        self.setLayout(layout)
    
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
        # Update combo box selection
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == theme_id:
                self.theme_combo.blockSignals(True)
                self.theme_combo.setCurrentIndex(i)
                self.theme_combo.blockSignals(False)
                break