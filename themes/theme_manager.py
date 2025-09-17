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
                "name": "Dark",
                "colors": {
                    # Core neutrals (gray-based)
                    "background": "#0D0D0D",        # Almost black
                    "surface": "#161616",           # Dark gray
                    "surface_variant": "#1F1F1F",   # Medium dark gray
                    "text_primary": "#FFFFFF",      # White
                    "text_secondary": "#B3B3B3",    # Soft gray
                    "text_disabled": "#6E6E6E",     # Dim gray

                    # Accent (choose one main highlight color — here a vivid blue)
                    "primary": "#49A041FF",           # Bright blue highlight
                    "primary_dark": "#53E653",      # Darker blue
                    "secondary": "#8CBEFB",         # Lighter blue for hover/alt
                    "accent": "#9871F4",            # Purple accent (optional secondary pop)
                    "accent2": "#6BF164",           # Cyan highlight

                    # Chart colors (harmonized to match blue/purple system)
                    "chart_colors": [
                        "#44C01E", "#3F0979", "#D6CA18",
                        "#BF0AB0", "#965a3e", "#C9431E",
                        "#60A5FA", "#48EACFDD"
                    ],

                    # Status colors (slightly muted so they don’t overpower)
                    "success": "#22C55E",   # Green
                    "warning": "#FACC15",   # Amber
                    "error": "#EF4444",     # Red
                    "info": "#3B82F6",      # Blue

                    # UI states
                    "border": "#2A2A2A",
                    "hover": "#1F1F1F",
                    "selected": "#3B82F6",
                    "disabled": "#2E2E2E"
                },
                "fonts": {
                    "main": {"family": "Arial", "size": 10},
                    "title": {"family": "Arial", "size": 18, "weight": "bold"},
                    "subtitle": {"family": "Arial", "size": 14, "weight": "bold"},
                    "small": {"family": "Arial", "size": 9},
                    "button": {"family": "Arial", "size": 10, "weight": "bold"},
                    "button_small": {"family": "Arial", "size": 9},
                    "menu": {"family": "Arial", "size": 10},
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
                    # Base neutrals
                    "background": "#FFFFFF",        # Pure white background
                    "surface": "#F9FAFB",           # Very light gray card
                    "surface_variant": "#E5E7EB",   # Light gray separators
                    "text_primary": "#111827",      # Near-black text
                    "text_secondary": "#4B5563",    # Medium gray
                    "text_disabled": "#9CA3AF",     # Muted gray

                    # Accent colors (bright, modern)
                    "primary": "#3B82F6",           # Blue (main highlight, like buttons/links)
                    "primary_dark": "#2563EB",      # Darker blue
                    "secondary": "#EF4444",         # Bright red/pink
                    "accent": "#10B981",            # Emerald green
                    "accent2": "#F59E0B",           # Amber/yellow

                    # Chart colors (matching accents)
                    "chart_colors": [
                        "#44C01E", "#3F0979", "#D6CA18",
                        "#BF0AB0", "#965a3e", "#C9431E",
                        "#60A5FA", "#48EACFDD"
                    ],

                    # Status colors
                    "success": "#10B981",   # Green
                    "warning": "#F59E0B",   # Amber
                    "error": "#EF4444",     # Red
                    "info": "#3B82F6",      # Blue

                    # UI states
                    "border": "#E5E7EB",    # Light gray borders
                    "hover": "#F3F4F6",     # Slightly darker gray hover
                    "selected": "#3B82F6",  # Blue selection
                    "disabled": "#D1D5DB"   # Gray disabled
                },
                "fonts": {
                    "main": {"family": "Arial", "size": 10},
                    "title": {"family": "Arial", "size": 18, "weight": "bold"},
                    "subtitle": {"family": "Arial", "size": 14, "weight": "bold"},
                    "small": {"family": "Arial", "size": 9},
                    "button": {"family": "Arial", "size": 10, "weight": "bold"},
                    "button_small": {"family": "Arial", "size": 9},
                    "menu": {"family": "Arial", "size": 10},
                    "monospace": {"family": "Consolas", "size": 9}
                },
                "gifs": {
                    "dashboard_animation": "light/sun.gif",
                    "loading": "light/loading.gif",
                    "success": "light/success.gif"
                }
            },
            
            "coffee": {
                "name": "Coffee (Dark Wood)",
                "colors": {
                    # Dark wood inspired palette from new images - much darker like true dark mode
                    "background": "#140405",     # Very dark brown/black (#140405 from wood image)
                    "surface": "#2E0F0A",        # Dark brown surface (#2E0F0A from wood image)
                    "surface_variant": "#332120", # Medium dark brown (#332120 from wood image)
                    "text_primary": "#D2B06B",    # Light golden brown text for contrast
                    "text_secondary": "#B8956F",  # Medium golden brown text
                    "text_disabled": "#7A6043",   # Muted brown
                    
                    # Dark coffee palette with golden highlights for contrast
                    "primary": "#D2B06B",        # Golden brown (main accent)
                    "primary_dark": "#B8956F",   # Darker golden brown
                    "secondary": "#8B4513",      # Saddle brown (secondary accent)
                    "accent": "#CD853F",         # Peru brown (tertiary accent)
                    "accent2": "#A0522D",        # Sienna brown (fourth accent)
                    
                    "chart_colors": ["#D2B06B", "#8B4513", "#CD853F", "#A0522D", "#B8956F", "#D2691E", "#DEB887", "#8B7355"],
                    
                    "success": "#8B7355",       # Olive brown success
                    "warning": "#D2691E",       # Chocolate orange
                    "error": "#A0522D",         # Sienna (warm red-brown)
                    "info": "#CD853F",          # Peru brown
                    
                    "border": "#4A2C17",        # Very dark border
                    "hover": "#3D251A",         # Slightly lighter hover
                    "selected": "#D2B06B",      # Golden brown selection
                    "disabled": "#2A1A11"       # Very dark disabled
                },
                "fonts": {
                    "main": {"family": "Courier New", "size": 10},        # Typewriter feel
                    "title": {"family": "Courier New", "size": 18, "weight": "bold"},
                    "subtitle": {"family": "Courier New", "size": 14, "weight": "bold"},
                    "small": {"family": "Courier New", "size": 9},
                    "button": {"family": "Courier New", "size": 10, "weight": "bold"},
                    "button_small": {"family": "Courier New", "size": 9},
                    "menu": {"family": "Courier New", "size": 10},
                    "monospace": {"family": "Courier New", "size": 9}
                },
                "gifs": {
                    "dashboard_animation": "coffee/steam.gif",
                    "loading": "coffee/brewing.gif",
                    "success": "coffee/cup.gif"
                }
            },
            
            "excel_blue": {
                "name": "Excel Blue (Professional)",
                "colors": {
                    "background": "#1e3a5f",
                    "surface": "#2a4b73",
                    "surface_variant": "#732a71",
                    "text_primary": "#ffffff",
                    "text_secondary": "#e6f3ff",
                    "text_disabled": "#9bb5d6",
                    
                    "primary": "#FFD700",      # Gold
                    "primary_dark": "#A50C9E",
                    "secondary": "#00BFFF",    # Deep sky blue
                    "accent": "#32CD32",       # Lime green
                    
                    "chart_colors": [
                        "#58D831", "#3F0979", "#D6CA18",
                        "#BF0AB0", "#965a3e", "#04941ED1",
                        "#60A5FA", "#DA1010DD"
                    ],             

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
                    "button": {"family": "Segoe UI", "size": 10, "weight": "bold"},
                    "button_small": {"family": "Segoe UI", "size": 9},
                    "menu": {"family": "Segoe UI", "size": 10},
                    "monospace": {"family": "Consolas", "size": 9}
                },
                "gifs": {
                    "dashboard_animation": "excel_blue/waves.gif",
                    "loading": "excel_blue/loading.gif",
                    "success": "excel_blue/star.gif"
                }
            },
            
            "cyberpunk": {
                "name": "Cyberpunk",
                "colors": {
                    # Cyberpunk neon grid inspired palette
                    "background": "#0a0a0a",     # Pure black
                    "surface": "#1a0f2e",        # Dark purple-blue
                    "surface_variant": "#2d1b4e", # Medium purple
                    "text_primary": "#00ffff",    # Electric cyan
                    "text_secondary": "#ff00ff",  # Electric magenta
                    "text_disabled": "#666666",   # Dark gray
                    
                    # Neon color hierarchy from cyberpunk image
                    "primary": "#00ffff",        # Electric cyan (main)
                    "primary_dark": "#0099cc",   # Darker cyan
                    "secondary": "#ff00ff",      # Electric magenta (secondary)
                    "accent": "#8B5FBF",         # Electric purple (from image)
                    "accent2": "#ff0080",        # Hot pink highlight
                    
                    "chart_colors": ["#00ffff", "#ff00ff", "#8B5FBF", "#ff0080", "#00ff80", "#8000ff", "#ff4080", "#40ff80"],
                    
                    "success": "#00ff80",       # Neon green
                    "warning": "#ffff00",       # Electric yellow
                    "error": "#ff0040",         # Neon red
                    "info": "#00ffff",          # Cyan info
                    
                    "border": "#4a0e4e",
                    "hover": "#2d1b4e",
                    "selected": "#00ffff",
                    "disabled": "#404040"
                },
                "fonts": {
                    "main": {"family": "Consolas", "size": 10},     # Readable for main text
                    "title": {"family": "Orbitron", "size": 16, "weight": "bold", "fallback": "Consolas"},  # Futuristic for titles
                    "subtitle": {"family": "Orbitron", "size": 12, "weight": "bold", "fallback": "Consolas"},
                    "small": {"family": "Consolas", "size": 8},     # Readable for small text
                    "button": {"family": "Orbitron", "size": 10, "weight": "bold", "fallback": "Consolas"},
                    "button_small": {"family": "Consolas", "size": 9},  # Readable for small buttons
                    "menu": {"family": "Consolas", "size": 10},
                    "monospace": {"family": "Courier New", "size": 8}
                },
                "gifs": {
                    "dashboard_animation": "cyberpunk/matrix.gif",
                    "loading": "cyberpunk/loading.gif",
                    "success": "cyberpunk/success.gif"
                }
            },
            
            "honey": {
                "name": "Honey",
                "colors": {
                    # Honey bee inspired palette with gold and black
                    "background": "#000000",     # Deep black (#1A141A from image)
                    "surface": "#423738",        # Dark brown-gray (#423738 from image)
                    "surface_variant": "#8E5915", # Medium honey brown (#8E5915 from image)
                    "text_primary": "#E59312",    # Golden yellow text (#E59312 from image)
                    "text_secondary": "#D3AF85",  # Light honey cream (#D3AF85 from image)
                    "text_disabled": "#8E5915",   # Muted honey brown
                    
                    # Honey and gold palette with black contrast
                    "primary": "#F4B315",        # Bright honey gold (#F4B315 from image)
                    "primary_dark": "#E59312",   # Medium honey gold
                    "secondary": "#D3AF85",      # Light honey cream (secondary accent)
                    "accent": "#8E5915",         # Dark honey brown (tertiary accent)
                    "accent2": "#423738",        # Dark brown-gray (fourth accent)
                    
                    "chart_colors": ["#F4B315", "#E59312", "#D3AF85", "#8E5915", "#FFD700", "#DAA520", "#B8860B", "#CD853F"],
                    
                    "success": "#8E5915",       # Honey brown success
                    "warning": "#F4B315",       # Bright honey warning
                    "error": "#C29309",         # Orange-red error
                    "info": "#E59312",          # Medium honey info
                    
                    "border": "#5A4A2A",
                    "hover": "#2A1F1A",
                    "selected": "#F4B315",
                    "disabled": "#3D2F1F"
                },
                "fonts": {
                    "main": {"family": "Segoe UI", "size": 10},
                    "title": {"family": "Segoe UI", "size": 18, "weight": "bold"},
                    "subtitle": {"family": "Segoe UI", "size": 14, "weight": "bold"},
                    "small": {"family": "Segoe UI", "size": 9},
                    "button": {"family": "Segoe UI", "size": 10, "weight": "bold"},
                    "button_small": {"family": "Segoe UI", "size": 9},
                    "menu": {"family": "Segoe UI", "size": 10},
                    "monospace": {"family": "Consolas", "size": 9}
                },
                "gifs": {
                    "dashboard_animation": "honey/honeycomb.gif",
                    "loading": "honey/loading.gif",
                    "success": "honey/success.gif"
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
        
        # Handle fallback fonts for themes like cyberpunk
        family = font_config["family"]
        if "fallback" in font_config:
            # Try the primary font, fall back if not available
            font = QFont(family, font_config["size"])
            if not font.exactMatch():
                family = font_config["fallback"]
        
        font = QFont(family, font_config["size"])
        
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