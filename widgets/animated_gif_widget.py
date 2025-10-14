"""
Animated GIF Widget - Displays animated GIFs with theme support
"""

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QMovie, QPixmap
from themes import theme_manager
from pathlib import Path
import random


class AnimatedGifWidget(QLabel):
    """Widget that displays animated GIFs from theme assets"""

    def __init__(self, gif_name: str, size: tuple = None, parent=None):
        super().__init__(parent)
        self.gif_name = gif_name
        self.movie = None
        self.target_size = size  # Target size for scaling (can be constraints, not fixed)

        # Set up widget - center the GIF both horizontally and vertically
        self.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        # Don't use setScaledContents - it stretches without preserving aspect ratio
        # We'll handle scaling manually with aspect ratio preservation

        # Load initial GIF
        self.load_gif()

        # Connect to theme changes
        theme_manager.theme_changed.connect(self.on_theme_changed)
    
    def get_random_gif_from_theme(self) -> str:
        """
        Get a random GIF from the current theme's assets folder

        Returns path to randomly selected GIF, or empty string if none found
        """
        # Get current theme ID
        current_theme = theme_manager.current_theme

        # Build path to theme's asset folder
        assets_dir = Path(theme_manager.assets_dir)
        theme_assets_dir = assets_dir / current_theme

        # Check if theme folder exists
        if not theme_assets_dir.exists():
            theme_assets_dir.mkdir(parents=True, exist_ok=True)
            return ""

        # Get all .gif files in the theme folder
        gif_files = list(theme_assets_dir.glob("*.gif"))

        # Return empty if no GIFs found
        if not gif_files:
            return ""

        # Randomly select one GIF
        selected_gif = random.choice(gif_files)
        return str(selected_gif)

    def load_gif(self):
        """Load a random GIF from the current theme's asset folder"""
        gif_path = self.get_random_gif_from_theme()

        if gif_path and gif_path.strip():
            try:
                # Stop existing movie
                if self.movie:
                    self.movie.stop()
                    self.movie.deleteLater()

                # Create new movie
                self.movie = QMovie(gif_path)

                # Set the movie
                self.setMovie(self.movie)

                # CRITICAL: Must scale AFTER setting the movie and after first frame loads
                # Connect to frameChanged signal to scale on first frame
                self.movie.frameChanged.connect(self.on_first_frame, Qt.ConnectionType.SingleShotConnection)

                # Start the movie
                self.movie.start()

                # Debug: Uncomment to see which GIF was loaded
                # print(f"Loaded random GIF: {gif_path}")

            except Exception as e:
                print(f"Failed to load GIF {gif_path}: {e}")
                self.show_placeholder()
        else:
            self.show_placeholder()

    def on_first_frame(self, frame_number):
        """Called when first frame is loaded - now we can get proper dimensions"""
        if frame_number == 0:  # First frame
            self.scale_movie_to_fit()

    def scale_movie_to_fit(self):
        """
        Scale the movie to fit within the allowed space while maintaining aspect ratio

        Uses the SMALLER of w_scale or h_scale to ensure the GIF fits completely within
        the allowed area without stretching or distortion. At least one dimension will
        perfectly fit the allowed area, the other may be smaller.
        """
        if not self.movie:
            return

        # Get the movie's original size (first frame)
        movie_size = self.movie.currentPixmap().size()

        if movie_size.isEmpty():
            # If no frame loaded yet, use target size or widget size
            if self.target_size:
                self.movie.setScaledSize(QSize(*self.target_size))
            else:
                self.movie.setScaledSize(self.size())
            return

        gif_width = movie_size.width()
        gif_height = movie_size.height()

        # Get allowed area size - use target_size if provided, otherwise widget's actual size
        if self.target_size:
            allowed_width, allowed_height = self.target_size
        else:
            allowed_width = self.width()
            allowed_height = self.height()

        # Avoid division by zero
        if gif_width == 0 or gif_height == 0 or allowed_width == 0 or allowed_height == 0:
            return

        # Calculate scale factors
        w_scale = allowed_width / gif_width
        h_scale = allowed_height / gif_height

        # Choose the SMALLER scale to fit within the area (maintains aspect ratio, no stretching)
        # This ensures the GIF fits completely within allowed area without distortion
        scale = min(w_scale, h_scale)

        # Calculate new dimensions (aspect ratio preserved)
        new_width = int(gif_width * scale)
        new_height = int(gif_height * scale)

        # Set scaled size
        self.movie.setScaledSize(QSize(new_width, new_height))

        # Set the widget's fixed size to match the GIF so border hugs the content
        self.setFixedSize(new_width, new_height)

        # Add border around the GIF
        colors = theme_manager.get_colors()
        self.setStyleSheet(f"""
            QLabel {{
                border: 1px solid {colors['border']};
                border-radius: 4px;
                background-color: transparent;
            }}
        """)
    
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