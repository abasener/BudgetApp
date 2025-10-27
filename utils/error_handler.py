"""
Error Handler - Provides user-friendly or technical error messages based on testing mode
"""

import traceback
from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import json
import os


def is_testing_mode():
    """Check if testing mode is enabled in settings"""
    settings_file = "app_settings.json"
    try:
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                return settings.get("testing_mode", False)
    except Exception:
        pass
    return False


class TechnicalErrorDialog(QDialog):
    """Dialog for displaying technical error details with copyable text"""

    def __init__(self, title, error_message, traceback_text=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(600, 400)

        layout = QVBoxLayout()

        # Error message label
        error_label = QLabel("Error Details (Click text below to select and copy):")
        error_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(error_label)

        # Text edit for copyable error details
        self.error_text = QTextEdit()
        self.error_text.setReadOnly(True)
        self.error_text.setFont(QFont("Courier", 9))

        # Build the error text
        full_error = f"Error: {error_message}\n"
        if traceback_text:
            full_error += f"\nTraceback:\n{traceback_text}"

        self.error_text.setPlainText(full_error)
        layout.addWidget(self.error_text)

        # Copy button
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(copy_button)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def copy_to_clipboard(self):
        """Copy the error text to clipboard"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.error_text.toPlainText())

        # Show brief notification
        QMessageBox.information(self, "Copied", "Error details copied to clipboard")


def show_error(parent, title, error, context=None):
    """
    Show an error message appropriate to the current mode

    Args:
        parent: Parent widget for the dialog
        title: Error dialog title
        error: The exception or error message
        context: Optional context about what was happening when the error occurred
    """
    if is_testing_mode():
        # Testing mode - show technical details
        error_msg = str(error)
        tb_text = None

        if isinstance(error, Exception):
            tb_text = traceback.format_exc()

        dialog = TechnicalErrorDialog(
            f"Technical Error - {title}",
            error_msg,
            tb_text,
            parent
        )
        dialog.exec()
    else:
        # User mode - show friendly message
        friendly_msg = get_friendly_error_message(error, context)
        QMessageBox.warning(parent, title, friendly_msg)


def get_friendly_error_message(error, context=None):
    """
    Convert technical errors to user-friendly messages

    Args:
        error: The exception or error message
        context: Optional context about what was happening

    Returns:
        A user-friendly error message
    """
    error_str = str(error).lower()

    # Database errors
    if "database" in error_str or "sqlite" in error_str:
        return "There was a problem accessing the data. Please try restarting the application."

    # File errors
    elif "file not found" in error_str or "no such file" in error_str:
        return "A required file could not be found. Please check your installation."

    elif "permission denied" in error_str or "access denied" in error_str:
        return "The application doesn't have permission to access a required file or folder."

    # Network errors
    elif "connection" in error_str or "network" in error_str:
        return "A network connection problem occurred. Please check your internet connection."

    # Import errors
    elif "import" in error_str or "module" in error_str:
        return "A required component could not be loaded. Please reinstall the application."

    # Value errors
    elif "invalid" in error_str or "value" in error_str:
        if context:
            return f"The entered value is not valid for {context}. Please check and try again."
        return "An invalid value was entered. Please check your input and try again."

    # Date errors
    elif "date" in error_str or "time" in error_str:
        return "There was a problem with the date or time format. Please check your input."

    # Division by zero
    elif "division" in error_str or "zero" in error_str:
        return "A calculation error occurred. Please check your values."

    # Memory errors
    elif "memory" in error_str:
        return "The application is running low on memory. Please close other applications and try again."

    # Generic fallback
    else:
        if context:
            return f"An error occurred while {context}. Please try again or contact support if the problem persists."
        return "An unexpected error occurred. Please try again or restart the application."


def handle_exception(exc_type, exc_value, exc_traceback, parent=None):
    """
    Global exception handler that can be connected to sys.excepthook

    Args:
        exc_type: Exception type
        exc_value: Exception value
        exc_traceback: Exception traceback
        parent: Parent widget for error dialog
    """
    # Ignore KeyboardInterrupt
    if issubclass(exc_type, KeyboardInterrupt):
        return

    # Format the error
    error_msg = f"{exc_type.__name__}: {exc_value}"

    if is_testing_mode():
        # In testing mode, also print to console
        import sys
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    # Show appropriate error dialog
    show_error(parent, "Application Error", exc_value)


def safe_operation(operation, parent=None, context=None, fallback=None):
    """
    Wrapper for operations that might fail, providing appropriate error handling

    Args:
        operation: Callable to execute
        parent: Parent widget for error dialogs
        context: Description of what's being attempted
        fallback: Value to return if operation fails

    Returns:
        Result of operation or fallback value
    """
    try:
        return operation()
    except Exception as e:
        show_error(parent, "Operation Failed", e, context)
        return fallback