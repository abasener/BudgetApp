"""
Animated GIF Widget - Displays animated GIFs with theme support
"""

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMovie, QPixmap
from themes import theme_manager


class AnimatedGifWidget(QLabel):
    """Widget that displays animated GIFs from theme assets"""
    
    def __init__(self, gif_name: str, size: tuple = None, parent=None):
        super().__init__(parent)
        self.gif_name = gif_name
        self.movie = None
        self.fixed_size = size
        
        # Set up widget
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.fixed_size:
            self.setFixedSize(*self.fixed_size)
        
        # Load initial GIF
        self.load_gif()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.on_theme_changed)
    
    def load_gif(self):
        """Load the GIF for the current theme"""
        gif_path = theme_manager.get_gif_path(self.gif_name)
        
        if gif_path and gif_path.strip():
            try:
                # Stop existing movie
                if self.movie:
                    self.movie.stop()
                    self.movie.deleteLater()
                
                # Create new movie
                self.movie = QMovie(gif_path)
                
                # Scale movie if size is specified
                if self.fixed_size:
                    self.movie.setScaledSize(self.size())
                
                # Set the movie and start it
                self.setMovie(self.movie)
                self.movie.start()
                
                print(f"Loaded GIF: {gif_path}")
                
            except Exception as e:
                print(f"Failed to load GIF {gif_path}: {e}")
                self.show_placeholder()
        else:
            self.show_placeholder()
    
    def show_placeholder(self):
        """Show a placeholder when GIF is not available"""
        # Stop any existing movie
        if self.movie:
            self.movie.stop()
            self.movie.deleteLater()
            self.movie = None
        
        # Create a simple placeholder
        colors = theme_manager.get_colors()
        placeholder_text = f"🎬\n{self.gif_name}\n(GIF placeholder)"
        
        self.setText(placeholder_text)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {colors['surface_variant']};
                color: {colors['text_secondary']};
                border: 2px dashed {colors['border']};
                border-radius: 8px;
                font-size: 10px;
                text-align: center;
            }}
        """)
    
    def on_theme_changed(self, theme_id):
        """Handle theme change"""
        self.load_gif()
    
    def start_animation(self):
        """Start the animation"""
        if self.movie:
            self.movie.start()
    
    def stop_animation(self):
        """Stop the animation"""
        if self.movie:
            self.movie.stop()
    
    def is_playing(self) -> bool:
        """Check if animation is currently playing"""
        return self.movie and self.movie.state() == QMovie.MovieState.Running
    
    def cleanup(self):
        """Clean up resources"""
        if self.movie:
            self.movie.stop()
            self.movie.deleteLater()
            self.movie = None