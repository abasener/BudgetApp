"""
Theme Manager - Flexible theming system for colors, fonts, and GIFs
"""

import os
from pathlib import Path
from typing import Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QFont


class ThemeManager(QObject):
    """Manages application themes with colors, fonts, and GIF assets"""
    
    theme_changed = pyqtSignal(str)  # Signal emitted when theme changes
    
    def __init__(self):
        super().__init__()
        self.current_theme = "dark"  # Default theme
        self.themes_dir = Path(__file__).parent
        self.assets_dir = self.themes_dir / "assets"
        
        # Ensure assets directory exists
        self.assets_dir.mkdir(exist_ok=True)
        
        # Initialize themes
        self.themes = self._load_themes()
    
    def _load_themes(self) -> Dict[str, Dict[str, Any]]:
        """Load all theme definitions"""
        return {
            "dark": {
                "name": "Dark (Current)",
                "colors": {
                    # Main application colors
                    "background": "#2b2b2b",
                    "surface": "#3c3c3c",
                    "surface_variant": "#484848",
                    "text_primary": "#ffffff",
                    "text_secondary": "#cccccc",
                    "text_disabled": "#888888",
                    
                    # Accent colors
                    "primary": "#4CAF50",      # Green
                    "primary_dark": "#388E3C",
                    "secondary": "#FF9800",    # Orange
                    "accent": "#2196F3",       # Blue
                    
                    # Chart colors (for consistency)
                    "chart_colors": ["#4CAF50", "#FF9800", "#2196F3", "#9C27B0", "#F44336", "#00BCD4", "#FFEB3B", "#795548"],
                    
                    # Status colors
                    "success": "#4CAF50",
                    "warning": "#FF9800",
                    "error": "#F44336",
                    "info": "#2196F3",
                    
                    # UI element colors
                    "border": "#555555",
                    "hover": "#484848",
                    "selected": "#4CAF50",
                    "disabled": "#666666"
                },
                "fonts": {
                    "main": {"family": "Arial", "size": 10},
                    "title": {"family": "Arial", "size": 18, "weight": "bold"},
                    "subtitle": {"family": "Arial", "size": 14, "weight": "bold"},
                    "small": {"family": "Arial", "size": 9},
                    "monospace": {"family": "Consolas", "size": 9}
                },
                "gifs": {
                    "dashboard_animation": "dark/moon.gif",     # Your moon animation
                    "loading": "dark/loading.gif",
                    "success": "dark/success.gif"
                }
            },
            
            "light": {
                "name": "Light",
                "colors": {
                    "background": "#ffffff",
                    "surface": "#f5f5f5",
                    "surface_variant": "#e0e0e0",
                    "text_primary": "#000000",
                    "text_secondary": "#666666",
                    "text_disabled": "#999999",
                    
                    "primary": "#2E7D32",      # Dark green
                    "primary_dark": "#1B5E20",
                    "secondary": "#F57C00",    # Dark orange
                    "accent": "#1976D2",       # Dark blue
                    
                    "chart_colors": ["#2E7D32", "#F57C00", "#1976D2", "#7B1FA2", "#C62828", "#00838F", "#F57F17", "#5D4037"],
                    
                    "success": "#2E7D32",
                    "warning": "#F57C00",
                    "error": "#C62828",
                    "info": "#1976D2",
                    
                    "border": "#cccccc",
                    "hover": "#e0e0e0",
                    "selected": "#2E7D32",
                    "disabled": "#cccccc"
                },
                "fonts": {
                    "main": {"family": "Arial", "size": 10},
                    "title": {"family": "Arial", "size": 18, "weight": "bold"},
                    "subtitle": {"family": "Arial", "size": 14, "weight": "bold"},
                    "small": {"family": "Arial", "size": 9},
                    "monospace": {"family": "Consolas", "size": 9}
                },
                "gifs": {
                    "dashboard_animation": "light/sun.gif",
                    "loading": "light/loading.gif",
                    "success": "light/success.gif"
                }
            },
            
            "coffee": {
                "name": "Coffee (Browns & Orange)",
                "colors": {
                    "background": "#2d2520",
                    "surface": "#3d342a",
                    "surface_variant": "#4d4137",
                    "text_primary": "#f4f1ea",
                    "text_secondary": "#d4c4b0",
                    "text_disabled": "#9d8b74",
                    
                    "primary": "#D7950B",      # Golden orange
                    "primary_dark": "#B8860B",
                    "secondary": "#CD853F",    # Peru
                    "accent": "#FF7F50",       # Coral
                    
                    "chart_colors": ["#D7950B", "#CD853F", "#FF7F50", "#DEB887", "#F4A460", "#DAA520", "#B22222", "#8B4513"],
                    
                    "success": "#228B22",
                    "warning": "#FF8C00",
                    "error": "#DC143C",
                    "info": "#4682B4",
                    
                    "border": "#6b5d4f",
                    "hover": "#4d4137",
                    "selected": "#D7950B",
                    "disabled": "#5d4e3f"
                },
                "fonts": {
                    "main": {"family": "Georgia", "size": 10},
                    "title": {"family": "Georgia", "size": 18, "weight": "bold"},
                    "subtitle": {"family": "Georgia", "size": 14, "weight": "bold"},
                    "small": {"family": "Georgia", "size": 9},
                    "monospace": {"family": "Consolas", "size": 9}
                },
                "gifs": {
                    "dashboard_animation": "coffee/steam.gif",
                    "loading": "coffee/brewing.gif",
                    "success": "coffee/cup.gif"
                }
            },
            
            "excel_blue": {
                "name": "Excel Blue (Blues & Yellows)",
                "colors": {
                    "background": "#1e3a5f",
                    "surface": "#2a4b73",
                    "surface_variant": "#355d87",
                    "text_primary": "#ffffff",
                    "text_secondary": "#e6f3ff",
                    "text_disabled": "#9bb5d6",
                    
                    "primary": "#FFD700",      # Gold
                    "primary_dark": "#DAA520",
                    "secondary": "#00BFFF",    # Deep sky blue
                    "accent": "#32CD32",       # Lime green
                    
                    "chart_colors": ["#FFD700", "#00BFFF", "#32CD32", "#FF69B4", "#FF4500", "#9370DB", "#00CED1", "#F0E68C"],
                    
                    "success": "#32CD32",
                    "warning": "#FFD700",
                    "error": "#FF4500",
                    "info": "#00BFFF",
                    
                    "border": "#4a6b91",
                    "hover": "#355d87",
                    "selected": "#FFD700",
                    "disabled": "#3f5a7a"
                },
                "fonts": {
                    "main": {"family": "Segoe UI", "size": 10},
                    "title": {"family": "Segoe UI", "size": 18, "weight": "bold"},
                    "subtitle": {"family": "Segoe UI", "size": 14, "weight": "bold"},
                    "small": {"family": "Segoe UI", "size": 9},
                    "monospace": {"family": "Consolas", "size": 9}
                },
                "gifs": {
                    "dashboard_animation": "excel_blue/waves.gif",
                    "loading": "excel_blue/loading.gif",
                    "success": "excel_blue/star.gif"
                }
            },
            
            "cyberpunk": {
                "name": "Cyberpunk (Neon Sci-Fi)",
                "colors": {
                    "background": "#0a0a0a",
                    "surface": "#1a1a1a",
                    "surface_variant": "#252525",
                    "text_primary": "#00ffff",    # Cyan
                    "text_secondary": "#ff00ff",  # Magenta
                    "text_disabled": "#666666",
                    
                    "primary": "#00ff00",         # Neon green
                    "primary_dark": "#00cc00",
                    "secondary": "#ff0080",       # Hot pink
                    "accent": "#ffff00",          # Electric yellow
                    
                    "chart_colors": ["#00ff00", "#ff0080", "#00ffff", "#ffff00", "#ff8000", "#8000ff", "#ff4080", "#00ff80"],
                    
                    "success": "#00ff00",
                    "warning": "#ffff00", 
                    "error": "#ff0040",
                    "info": "#00ffff",
                    
                    "border": "#333333",
                    "hover": "#2a2a2a",
                    "selected": "#00ff00",
                    "disabled": "#404040"
                },
                "fonts": {
                    "main": {"family": "Consolas", "size": 9},
                    "title": {"family": "Consolas", "size": 16, "weight": "bold"},
                    "subtitle": {"family": "Consolas", "size": 12, "weight": "bold"},
                    "small": {"family": "Consolas", "size": 8},
                    "monospace": {"family": "Courier New", "size": 8}
                },
                "gifs": {
                    "dashboard_animation": "cyberpunk/matrix.gif",
                    "loading": "cyberpunk/loading.gif",
                    "success": "cyberpunk/success.gif"
                }
            }
        }
    
    def get_available_themes(self) -> Dict[str, str]:
        """Get list of available themes"""
        return {theme_id: theme_data["name"] for theme_id, theme_data in self.themes.items()}
    
    def set_theme(self, theme_id: str):
        """Set the current theme"""
        if theme_id in self.themes:
            self.current_theme = theme_id
            self.theme_changed.emit(theme_id)
            print(f"Theme changed to: {self.themes[theme_id]['name']}")
    
    def get_color(self, color_name: str) -> str:
        """Get a color from the current theme"""
        theme = self.themes.get(self.current_theme, self.themes["dark"])
        return theme["colors"].get(color_name, "#ffffff")
    
    def get_colors(self) -> Dict[str, str]:
        """Get all colors from the current theme"""
        theme = self.themes.get(self.current_theme, self.themes["dark"])
        return theme["colors"].copy()
    
    def get_chart_colors(self) -> list:
        """Get chart color palette for current theme"""
        theme = self.themes.get(self.current_theme, self.themes["dark"])
        return theme["colors"].get("chart_colors", ["#4CAF50", "#FF9800", "#2196F3"])
    
    def get_font(self, font_type: str = "main") -> QFont:
        """Get a font from the current theme"""
        theme = self.themes.get(self.current_theme, self.themes["dark"])
        font_config = theme["fonts"].get(font_type, theme["fonts"]["main"])
        
        font = QFont(font_config["family"], font_config["size"])
        
        if font_config.get("weight") == "bold":
            font.setBold(True)
            
        return font
    
    def get_gif_path(self, gif_name: str) -> str:
        """Get path to a GIF asset for the current theme"""
        theme = self.themes.get(self.current_theme, self.themes["dark"])
        gif_relative_path = theme["gifs"].get(gif_name, "dark/loading.gif")
        gif_path = self.assets_dir / gif_relative_path
        
        # Return path if file exists, otherwise return placeholder
        if gif_path.exists():
            return str(gif_path)
        else:
            # Return a placeholder or create theme directory structure
            theme_dir = self.assets_dir / self.current_theme
            theme_dir.mkdir(exist_ok=True)
            return ""  # Will handle missing GIFs gracefully in UI
    
    def get_stylesheet(self) -> str:
        """Generate QStyleSheet for the current theme"""
        colors = self.get_colors()
        
        return f"""
        /* Main Window Styling */
        QMainWindow {{
            background-color: {colors['background']};
            color: {colors['text_primary']};
        }}
        
        /* Tab Widget */
        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            background-color: {colors['surface']};
        }}
        
        QTabWidget::tab-bar {{
            alignment: left;
        }}
        
        QTabBar::tab {{
            background-color: {colors['surface_variant']};
            color: {colors['text_secondary']};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['primary']};
            color: {colors['background']};
            font-weight: bold;
        }}
        
        QTabBar::tab:hover {{
            background-color: {colors['hover']};
        }}
        
        /* Frames and Panels */
        QFrame {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
        }}
        
        /* Labels */
        QLabel {{
            color: {colors['text_primary']};
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {colors['surface_variant']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 8px 16px;
        }}
        
        QPushButton:hover {{
            background-color: {colors['hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['selected']};
        }}
        
        /* Toolbar */
        QToolBar {{
            background-color: {colors['surface']};
            border: none;
            spacing: 4px;
            padding: 4px;
        }}
        
        /* Menu Bar */
        QMenuBar {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 4px 8px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors['primary']};
        }}
        
        QMenu {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
        }}
        
        QMenu::item {{
            padding: 4px 16px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors['primary']};
        }}
        
        /* Scroll Area */
        QScrollArea {{
            background-color: {colors['background']};
            border: none;
        }}
        
        /* Table Widget */
        QTableWidget {{
            background-color: {colors['surface']};
            alternate-background-color: {colors['surface_variant']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            gridline-color: {colors['border']};
        }}
        
        QHeaderView::section {{
            background-color: {colors['primary']};
            color: {colors['background']};
            padding: 4px;
            border: 1px solid {colors['border']};
            font-weight: bold;
        }}
        
        /* Progress Bar */
        QProgressBar {{
            background-color: {colors['surface_variant']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: 3px;
        }}
        """
    
    def create_theme_assets_structure(self):
        """Create directory structure for theme assets"""
        for theme_id in self.themes.keys():
            theme_dir = self.assets_dir / theme_id
            theme_dir.mkdir(exist_ok=True)
            
            # Create placeholder info file
            info_file = theme_dir / "info.txt"
            if not info_file.exists():
                info_file.write_text(f"""
Theme: {self.themes[theme_id]['name']}
GIF Assets needed:
- dashboard_animation: Main dashboard animated element
- loading: Loading spinner/animation  
- success: Success confirmation animation

Place your GIF files in this directory with the expected names.
                """.strip())


# Global theme manager instance
theme_manager = ThemeManager()