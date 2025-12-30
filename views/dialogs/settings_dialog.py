"""
Settings Dialog - Configure persistent application settings
"""

import json
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
                             QComboBox, QPushButton, QLabel, QGroupBox, QMessageBox, QDoubleSpinBox, QCheckBox, QWidget,
                             QListWidget, QListWidgetItem, QAbstractItemView, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from themes import theme_manager


# All available tabs with their properties
# Format: (internal_id, display_name, is_required)
ALL_TABS = [
    ("dashboard", "Dashboard", False),
    ("bills", "Bills", True),  # Required
    ("savings", "Savings", True),  # Required (called "Accounts" in some docs)
    ("weekly", "Weekly", True),  # Required (called "Week" in some docs)
    ("categories", "Categories", False),
    ("yearly", "Yearly", False),
    ("reimbursements", "Reimbursements", False),
    ("scratch_pad", "Scratch Pad", False),
    ("transactions", "Transactions", False),  # Settings-controlled
    ("taxes", "Taxes", False),  # Settings-controlled
]

# Default tab order (all visible)
DEFAULT_TAB_ORDER = [tab[0] for tab in ALL_TABS]
DEFAULT_HIDDEN_TABS = []


class TabOrderWidget(QWidget):
    """Widget for reordering tabs via drag-and-drop with visibility toggle"""

    order_changed = pyqtSignal()  # Emitted when order or visibility changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Visible tabs section
        visible_label = QLabel("Visible Tabs (drag to reorder):")
        visible_label.setFont(QFont(visible_label.font().family(), -1, QFont.Weight.Bold))
        layout.addWidget(visible_label)

        self.visible_list = QListWidget()
        self.visible_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.visible_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.visible_list.setMinimumHeight(120)
        self.visible_list.model().rowsMoved.connect(self._on_order_changed)
        layout.addWidget(self.visible_list)

        # Buttons to move between lists
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.hide_btn = QPushButton("Hide ▼")
        self.hide_btn.setToolTip("Move selected tab to hidden")
        self.hide_btn.clicked.connect(self._hide_selected)
        btn_layout.addWidget(self.hide_btn)

        self.show_btn = QPushButton("Show ▲")
        self.show_btn.setToolTip("Move selected tab to visible")
        self.show_btn.clicked.connect(self._show_selected)
        btn_layout.addWidget(self.show_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Hidden tabs section
        hidden_label = QLabel("Hidden Tabs:")
        hidden_label.setFont(QFont(hidden_label.font().family(), -1, QFont.Weight.Bold))
        layout.addWidget(hidden_label)

        self.hidden_list = QListWidget()
        self.hidden_list.setMinimumHeight(60)
        self.hidden_list.setMaximumHeight(80)
        layout.addWidget(self.hidden_list)

        # Info label
        info_label = QLabel("🔒 = Required (cannot hide)")
        info_label.setStyleSheet("color: gray; font-style: italic; font-size: 11px;")
        layout.addWidget(info_label)

    def load_tab_settings(self, tab_order: list, hidden_tabs: list):
        """Load tab order and visibility from settings"""
        self.visible_list.clear()
        self.hidden_list.clear()

        # Build lookup for tab info
        tab_info = {tab[0]: (tab[1], tab[2]) for tab in ALL_TABS}

        # Add visible tabs in order
        for tab_id in tab_order:
            if tab_id in tab_info and tab_id not in hidden_tabs:
                display_name, is_required = tab_info[tab_id]
                self._add_tab_item(self.visible_list, tab_id, display_name, is_required)

        # Add any tabs not in order (new tabs) to visible list
        for tab_id, display_name, is_required in ALL_TABS:
            if tab_id not in tab_order and tab_id not in hidden_tabs:
                self._add_tab_item(self.visible_list, tab_id, display_name, is_required)

        # Add hidden tabs
        for tab_id in hidden_tabs:
            if tab_id in tab_info:
                display_name, is_required = tab_info[tab_id]
                # Required tabs can't be hidden - move to visible
                if is_required:
                    self._add_tab_item(self.visible_list, tab_id, display_name, is_required)
                else:
                    self._add_tab_item(self.hidden_list, tab_id, display_name, is_required)

    def _add_tab_item(self, list_widget: QListWidget, tab_id: str, display_name: str, is_required: bool):
        """Add a tab item to a list widget"""
        # Show lock icon for required tabs
        text = f"🔒 {display_name}" if is_required else display_name
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, tab_id)
        item.setData(Qt.ItemDataRole.UserRole + 1, is_required)

        # Make required tabs not draggable to hidden
        if is_required:
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsDragEnabled)

        list_widget.addItem(item)

    def _hide_selected(self):
        """Move selected visible tab to hidden"""
        current = self.visible_list.currentItem()
        if not current:
            return

        is_required = current.data(Qt.ItemDataRole.UserRole + 1)
        if is_required:
            QMessageBox.information(self, "Required Tab",
                "This tab is required and cannot be hidden.")
            return

        tab_id = current.data(Qt.ItemDataRole.UserRole)
        display_name = current.text()

        # Remove from visible, add to hidden
        row = self.visible_list.row(current)
        self.visible_list.takeItem(row)

        item = QListWidgetItem(display_name)
        item.setData(Qt.ItemDataRole.UserRole, tab_id)
        item.setData(Qt.ItemDataRole.UserRole + 1, False)
        self.hidden_list.addItem(item)

        self.order_changed.emit()

    def _show_selected(self):
        """Move selected hidden tab to visible"""
        current = self.hidden_list.currentItem()
        if not current:
            return

        tab_id = current.data(Qt.ItemDataRole.UserRole)
        display_name = current.text()

        # Remove from hidden, add to visible at end
        row = self.hidden_list.row(current)
        self.hidden_list.takeItem(row)

        item = QListWidgetItem(display_name)
        item.setData(Qt.ItemDataRole.UserRole, tab_id)
        item.setData(Qt.ItemDataRole.UserRole + 1, False)
        self.visible_list.addItem(item)

        self.order_changed.emit()

    def _on_order_changed(self):
        """Handle when tab order changes via drag-drop"""
        self.order_changed.emit()

    def get_tab_order(self) -> list:
        """Get current tab order (visible tabs only)"""
        order = []
        for i in range(self.visible_list.count()):
            item = self.visible_list.item(i)
            order.append(item.data(Qt.ItemDataRole.UserRole))
        return order

    def get_hidden_tabs(self) -> list:
        """Get list of hidden tab IDs"""
        hidden = []
        for i in range(self.hidden_list.count()):
            item = self.hidden_list.item(i)
            hidden.append(item.data(Qt.ItemDataRole.UserRole))
        return hidden

    def apply_theme(self):
        """Apply current theme to the widget"""
        colors = theme_manager.get_colors()

        list_style = f"""
            QListWidget {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 4px;
                color: {colors['text_primary']};
            }}
            QListWidget::item {{
                padding: 6px 8px;
                border-radius: 3px;
                margin: 2px 0;
            }}
            QListWidget::item:selected {{
                background-color: {colors['primary']};
                color: {colors['background']};
            }}
            QListWidget::item:hover {{
                background-color: {colors['hover']};
            }}
        """

        self.visible_list.setStyleSheet(list_style)
        self.hidden_list.setStyleSheet(list_style)


class SettingsDialog(QDialog):
    """Dialog for configuring persistent application settings"""
    
    settings_saved = pyqtSignal()  # Signal when settings are saved
    
    def __init__(self, transaction_manager, parent=None):
        super().__init__(parent)
        self.transaction_manager = transaction_manager
        self.settings_file = "app_settings.json"
        self.original_settings = {}
        self.current_settings = {}
        
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(500, 400)
        
        self.init_ui()
        self.load_settings()
        self.apply_theme()
    
    def init_ui(self):
        """Initialize the UI layout"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        # Header
        header_label = QLabel("Budget Settings")
        header_label.setFont(theme_manager.get_font("title"))
        main_layout.addWidget(header_label)

        # ============================================
        # TOP SECTION: 2-column layout
        # Left: Graph and Data + Appearance (stacked)
        # Right: Tab Selection/Sort (spans full height)
        # ============================================
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(20)

        # LEFT COLUMN
        left_column = QVBoxLayout()
        left_column.setSpacing(15)

        # --- Graph and Data Group ---
        graph_data_group = QGroupBox("Graph and Data")
        graph_data_layout = QFormLayout()

        # Normal only checkbox (Label [checkbox])
        self.default_analytics_checkbox = QCheckBox()
        self.default_analytics_checkbox.setChecked(True)
        self.default_analytics_checkbox.setToolTip("When enabled, charts will filter out abnormal spending by default")
        graph_data_layout.addRow("Normal Only:", self.default_analytics_checkbox)

        # Time frame filtering dropdown
        self.time_frame_combo = QComboBox()
        self.time_frame_combo.addItems([
            "All Time",
            "Last Year",
            "Last Month",
            "Last 20 Entries"
        ])
        self.time_frame_combo.setToolTip("Filter charts and plots to show only recent data")
        graph_data_layout.addRow("Time Frame Filter:", self.time_frame_combo)

        # Dashboard charts - both dropdowns on same row
        charts_widget = QWidget()
        charts_layout = QHBoxLayout(charts_widget)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(10)

        self.chart1_account_combo = QComboBox()
        self.populate_account_combo(self.chart1_account_combo)
        charts_layout.addWidget(self.chart1_account_combo)

        self.chart2_account_combo = QComboBox()
        self.populate_account_combo(self.chart2_account_combo)
        charts_layout.addWidget(self.chart2_account_combo)

        graph_data_layout.addRow("Dashboard Charts:", charts_widget)

        # Backup buttons row
        backup_widget = QWidget()
        backup_layout = QHBoxLayout(backup_widget)
        backup_layout.setContentsMargins(0, 0, 0, 0)
        backup_layout.setSpacing(10)

        make_backup_btn = QPushButton("Make Backup")
        make_backup_btn.setToolTip("Create a backup of your data in the BackUps folder")
        make_backup_btn.clicked.connect(self.make_backup)
        backup_layout.addWidget(make_backup_btn)

        restore_backup_btn = QPushButton("Restore Backup")
        restore_backup_btn.setToolTip("Restore data from a previous backup")
        restore_backup_btn.clicked.connect(self.restore_backup)
        backup_layout.addWidget(restore_backup_btn)

        graph_data_layout.addRow("Backups:", backup_widget)

        graph_data_group.setLayout(graph_data_layout)
        left_column.addWidget(graph_data_group)

        # --- Appearance Group ---
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout()

        self.default_theme_combo = QComboBox()
        self.populate_theme_combo()
        appearance_layout.addRow("Theme:", self.default_theme_combo)

        appearance_group.setLayout(appearance_layout)
        left_column.addWidget(appearance_group)

        # Add stretch to push groups to top
        left_column.addStretch()

        # RIGHT COLUMN - Tab Selection/Sort
        right_column = QVBoxLayout()
        right_column.setSpacing(15)

        tab_group = QGroupBox("Tab Selection/Sort")
        tab_layout = QVBoxLayout()

        # Tab order widget with drag-drop
        self.tab_order_widget = TabOrderWidget()
        tab_layout.addWidget(self.tab_order_widget)

        tab_group.setLayout(tab_layout)
        right_column.addWidget(tab_group)

        # Add columns to main layout
        columns_layout.addLayout(left_column, 1)  # stretch factor 1
        columns_layout.addLayout(right_column, 1)  # stretch factor 1
        main_layout.addLayout(columns_layout)

        # ============================================
        # BOTTOM SECTION: Advanced (full width)
        # ============================================
        advanced_group = QGroupBox("Advanced")
        advanced_layout = QVBoxLayout()

        # Row 1: Testing mode checkbox
        row1_widget = QWidget()
        row1_layout = QHBoxLayout(row1_widget)
        row1_layout.setContentsMargins(0, 0, 0, 0)

        self.testing_mode_checkbox = QCheckBox()
        self.testing_mode_checkbox.setChecked(False)
        self.testing_mode_checkbox.setToolTip("Enable testing mode for development and debugging")
        row1_layout.addWidget(QLabel("Testing Mode:"))
        row1_layout.addWidget(self.testing_mode_checkbox)
        row1_layout.addStretch()

        advanced_layout.addWidget(row1_widget)

        # Row 2: Export/Import buttons
        row2_widget = QWidget()
        row2_layout = QHBoxLayout(row2_widget)
        row2_layout.setContentsMargins(0, 0, 0, 0)

        export_btn = QPushButton("Export Data")
        export_btn.setToolTip("Export all data to Excel file")
        export_btn.clicked.connect(self.export_data)
        row2_layout.addWidget(export_btn)

        import_btn = QPushButton("Import Data")
        import_btn.setToolTip("Import data from Excel file")
        import_btn.clicked.connect(self.import_test_data)
        row2_layout.addWidget(import_btn)

        row2_layout.addStretch()

        advanced_layout.addWidget(row2_widget)

        # Row 3: Load Test Data + Reset All Data (dangerous buttons at bottom)
        row3_widget = QWidget()
        row3_layout = QHBoxLayout(row3_widget)
        row3_layout.setContentsMargins(0, 0, 0, 0)

        load_test_btn = QPushButton("Load Test Data")
        load_test_btn.setToolTip("Delete ALL data and generate fresh test data")
        load_test_btn.clicked.connect(self.confirm_load_test_data)
        row3_layout.addWidget(load_test_btn)

        reset_data_btn = QPushButton("Reset All Data")
        reset_data_btn.setStyleSheet("color: red; font-weight: bold;")
        reset_data_btn.setToolTip("Permanently delete all transactions, accounts, bills, and weeks")
        reset_data_btn.clicked.connect(self.confirm_reset_data)
        row3_layout.addWidget(reset_data_btn)

        row3_layout.addStretch()

        advanced_layout.addWidget(row3_widget)

        advanced_group.setLayout(advanced_layout)
        main_layout.addWidget(advanced_group)

        # ============================================
        # DIALOG BUTTONS: Cancel / Save
        # ============================================
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)

        # Apply button theme
        self.apply_button_theme()

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
    
    def populate_theme_combo(self):
        """Populate theme dropdown with available themes"""
        for theme_id, theme_info in theme_manager.themes.items():
            self.default_theme_combo.addItem(theme_info['name'], theme_id)
    
    def populate_account_combo(self, combo):
        """Populate account dropdown with available accounts plus random option"""
        combo.addItem("Random (Default)", "random")
        
        try:
            accounts = self.transaction_manager.get_all_accounts()
            for account in accounts:
                combo.addItem(account.name, account.name)
        except Exception as e:
            print(f"Error loading accounts for settings: {e}")
    
    def get_default_settings(self):
        """Get default application settings"""
        return {
            "default_theme": "dark",
            "bills_sort_order": "Alphabetical",
            "savings_sort_order": "Alphabetical",
            "dashboard_chart1_account": "random",
            "dashboard_chart2_account": "random",
            "default_hourly_rate": 50.00,
            "default_analytics_only": True,
            "time_frame_filter": "All Time",
            "enable_tax_features": False,
            "testing_mode": False,
            "enable_transactions_tab": False
        }
    
    def load_settings(self):
        """Load settings from file or use defaults"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.current_settings = json.load(f)
            else:
                self.current_settings = self.get_default_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.current_settings = self.get_default_settings()
        
        # Store original settings for change detection
        self.original_settings = self.current_settings.copy()
        
        # Apply settings to UI
        self.apply_settings_to_ui()
    
    def apply_settings_to_ui(self):
        """Apply loaded settings to UI controls"""
        # Set default theme
        theme_index = self.default_theme_combo.findData(self.current_settings.get("default_theme", "dark"))
        if theme_index >= 0:
            self.default_theme_combo.setCurrentIndex(theme_index)

        # Set dashboard chart accounts
        chart1_account = self.current_settings.get("dashboard_chart1_account", "random")
        chart1_index = self.chart1_account_combo.findData(chart1_account)
        if chart1_index >= 0:
            self.chart1_account_combo.setCurrentIndex(chart1_index)

        chart2_account = self.current_settings.get("dashboard_chart2_account", "random")
        chart2_index = self.chart2_account_combo.findData(chart2_account)
        if chart2_index >= 0:
            self.chart2_account_combo.setCurrentIndex(chart2_index)

        # Set default analytics checkbox state
        default_analytics = self.current_settings.get("default_analytics_only", True)
        self.default_analytics_checkbox.setChecked(default_analytics)

        # Set time frame filter
        time_frame = self.current_settings.get("time_frame_filter", "All Time")
        time_frame_index = self.time_frame_combo.findText(time_frame)
        if time_frame_index >= 0:
            self.time_frame_combo.setCurrentIndex(time_frame_index)

        # Set testing mode checkbox state
        testing_mode = self.current_settings.get("testing_mode", False)
        self.testing_mode_checkbox.setChecked(testing_mode)

        # Load tab order settings
        tab_order = self.current_settings.get("tab_order", DEFAULT_TAB_ORDER)
        hidden_tabs = self.current_settings.get("hidden_tabs", DEFAULT_HIDDEN_TABS)
        self.tab_order_widget.load_tab_settings(tab_order, hidden_tabs)

    def get_ui_settings(self):
        """Get current settings from UI controls"""
        # Get existing settings to preserve values not shown in UI
        existing = load_app_settings()

        # Update with UI values
        return {
            "default_theme": self.default_theme_combo.currentData(),
            "bills_sort_order": existing.get("bills_sort_order", "Alphabetical"),  # Preserved from local controls
            "savings_sort_order": existing.get("savings_sort_order", "Alphabetical"),  # Preserved from local controls
            "dashboard_chart1_account": self.chart1_account_combo.currentData(),
            "dashboard_chart2_account": self.chart2_account_combo.currentData(),
            "default_hourly_rate": existing.get("default_hourly_rate", 50.00),  # Preserved from hour calculator
            "default_analytics_only": self.default_analytics_checkbox.isChecked(),
            "time_frame_filter": self.time_frame_combo.currentText(),
            "enable_tax_features": existing.get("enable_tax_features", False),  # Preserved
            "testing_mode": self.testing_mode_checkbox.isChecked(),
            "enable_transactions_tab": existing.get("enable_transactions_tab", False),  # Preserved
            "tab_order": self.tab_order_widget.get_tab_order(),
            "hidden_tabs": self.tab_order_widget.get_hidden_tabs()
        }
    
    def apply_button_theme(self):
        """Apply focused styling to Save button, normal styling to others"""
        colors = theme_manager.get_colors()

        # Save button - focused style (primary background with primary_dark hover)
        self.save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['primary']};
                color: {colors['background']};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: {colors['primary_dark']};
            }}

            QPushButton:pressed {{
                background-color: {colors['selected']};
            }}
        """)

        # Cancel button uses default theme styling (cleared)
        self.cancel_button.setStyleSheet("")

    def reset_to_defaults(self):
        """Reset all settings to default values and save"""
        # Create custom Yes/No dialog with Yes focused
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Reset Settings")
        msg_box.setText("Are you sure you want to reset all settings to their default values?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)

        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            self.current_settings = self.get_default_settings()
            self.apply_settings_to_ui()

            # Save the reset settings
            try:
                with open(self.settings_file, 'w') as f:
                    json.dump(self.current_settings, f, indent=2)

                QMessageBox.information(self, "Settings Reset", "Settings have been reset to defaults and saved.")
                self.settings_saved.emit()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save reset settings: {str(e)}")
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            # Get current UI values
            new_settings = self.get_ui_settings()

            # Check if anything changed
            changes = []
            for key, new_value in new_settings.items():
                old_value = self.original_settings.get(key)
                if new_value != old_value:
                    changes.append(f"{key}: {old_value} → {new_value}")

            if not changes:
                QMessageBox.information(self, "No Changes", "No changes were made to settings.")
                return

            # Save to file
            with open(self.settings_file, 'w') as f:
                json.dump(new_settings, f, indent=2)

            # Apply theme change immediately if changed
            if new_settings["default_theme"] != self.original_settings.get("default_theme"):
                theme_manager.set_theme(new_settings["default_theme"])

            # Check if testing mode is enabled
            testing_mode = new_settings.get("testing_mode", False)

            if testing_mode:
                # In testing mode, show detailed change list
                change_details = [
                    "✓ Settings Saved Successfully",
                    "",
                    f"Success: {len(changes)} changes made",
                    ""
                ]
                for change in changes:
                    change_details.append(f"• {change}")

                QMessageBox.information(
                    self,
                    "Success - Testing Mode",
                    "\n".join(change_details)
                )
            # If not in testing mode, just close without popup

            # Emit signal and close
            self.settings_saved.emit()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
            print(f"Error saving settings: {e}")
    
    def apply_theme(self):
        """Apply current theme to dialog"""
        try:
            colors = theme_manager.get_colors()
            
            self.setStyleSheet(f"""
                QDialog {{
                    background-color: {colors['background']};
                    color: {colors['text_primary']};
                }}
                
                QLabel {{
                    color: {colors['text_primary']};
                }}
                
                QComboBox {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 4px 8px;
                    color: {colors['text_primary']};
                    min-height: 20px;
                }}
                
                QComboBox:hover {{
                    border: 1px solid {colors['primary']};
                }}
                
                QComboBox:focus {{
                    border: 2px solid {colors['primary']};
                }}
                
                QComboBox::drop-down {{
                    border: none;
                    width: 20px;
                }}
                
                QComboBox::down-arrow {{
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid {colors['text_primary']};
                    margin-right: 5px;
                }}
                
                QComboBox QAbstractItemView {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    selection-background-color: {colors['primary']};
                    selection-color: {colors['background']};
                }}
                
                QPushButton {{
                    background-color: {colors['primary']};
                    color: {colors['surface']};
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                
                QPushButton:hover {{
                    background-color: {colors['accent']};
                }}
                
                QPushButton:pressed {{
                    background-color: {colors['primary']};
                }}
                
                QGroupBox {{
                    font-weight: bold;
                    border: 2px solid {colors['border']};
                    border-radius: 5px;
                    margin: 10px 0px;
                    padding-top: 10px;
                    color: {colors['text_primary']};
                }}
                
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }}
                
                QDoubleSpinBox {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 4px 8px;
                    color: {colors['text_primary']};
                    min-height: 20px;
                }}
                
                QDoubleSpinBox:hover {{
                    border: 1px solid {colors['primary']};
                }}
                
                QDoubleSpinBox:focus {{
                    border: 2px solid {colors['primary']};
                }}
                
                QDoubleSpinBox::up-button {{
                    background-color: {colors['surface_variant']};
                    border: 1px solid {colors['border']};
                    border-radius: 2px;
                    width: 16px;
                    margin: 1px;
                }}
                
                QDoubleSpinBox::up-button:hover {{
                    background-color: {colors['primary']};
                }}
                
                QDoubleSpinBox::up-button:pressed {{
                    background-color: {colors.get('primary_dark', colors['primary'])};
                }}
                
                QDoubleSpinBox::down-button {{
                    background-color: {colors['surface_variant']};
                    border: 1px solid {colors['border']};
                    border-radius: 2px;
                    width: 16px;
                    margin: 1px;
                }}
                
                QDoubleSpinBox::down-button:hover {{
                    background-color: {colors['primary']};
                }}
                
                QDoubleSpinBox::down-button:pressed {{
                    background-color: {colors.get('primary_dark', colors['primary'])};
                }}
                
                QDoubleSpinBox::up-arrow {{
                    image: none;
                    border-left: 3px solid transparent;
                    border-right: 3px solid transparent;
                    border-bottom: 3px solid {colors['text_primary']};
                    width: 6px;
                    height: 3px;
                }}
                
                QDoubleSpinBox::down-arrow {{
                    image: none;
                    border-left: 3px solid transparent;
                    border-right: 3px solid transparent;
                    border-top: 3px solid {colors['text_primary']};
                    width: 6px;
                    height: 3px;
                }}

                QCheckBox {{
                    color: {colors['text_primary']};
                    spacing: 8px;
                }}

                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 1px solid {colors['border']};
                    border-radius: 2px;
                    background-color: {colors['surface']};
                }}

                QCheckBox::indicator:hover {{
                    border: 1px solid {colors['primary']};
                }}

                QCheckBox::indicator:checked {{
                    background-color: {colors['primary']};
                    border: 1px solid {colors['primary']};
                }}
            """)
            
        except Exception as e:
            print(f"Error applying theme to settings dialog: {e}")

    def make_backup(self):
        """Create a backup of all data files to BackUps folder"""
        import shutil
        from datetime import datetime

        try:
            # Create BackUps folder if it doesn't exist
            backup_dir = "BackUps"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            # Create dated subfolder
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            backup_path = os.path.join(backup_dir, timestamp)
            os.makedirs(backup_path)

            # Files to backup
            files_to_backup = [
                "budget.db",
                "app_settings.json",
                "scratch_pad_workspace.json"
            ]

            backed_up = []
            for filename in files_to_backup:
                if os.path.exists(filename):
                    shutil.copy2(filename, backup_path)
                    backed_up.append(filename)

            if backed_up:
                QMessageBox.information(
                    self,
                    "Backup Complete",
                    f"Backup created successfully!\n\nLocation: {backup_path}\n\nFiles backed up:\n" + "\n".join(f"  - {f}" for f in backed_up)
                )
            else:
                QMessageBox.warning(self, "Backup", "No files found to backup.")

        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Failed to create backup: {str(e)}")

    def restore_backup(self):
        """Show list of available backups and restore selected one"""
        import shutil

        try:
            backup_dir = "BackUps"
            if not os.path.exists(backup_dir):
                QMessageBox.information(self, "No Backups", "No backups found. The BackUps folder doesn't exist.")
                return

            # Get list of backup folders
            backups = sorted([d for d in os.listdir(backup_dir) if os.path.isdir(os.path.join(backup_dir, d))], reverse=True)

            if not backups:
                QMessageBox.information(self, "No Backups", "No backup folders found in BackUps directory.")
                return

            # Show selection dialog
            from PyQt6.QtWidgets import QInputDialog
            backup_name, ok = QInputDialog.getItem(
                self,
                "Restore Backup",
                "Select a backup to restore:",
                backups,
                0,
                False
            )

            if not ok or not backup_name:
                return

            # Confirm restore
            reply = QMessageBox.warning(
                self,
                "Confirm Restore",
                f"This will replace your current data with the backup from:\n\n{backup_name}\n\nThis action cannot be undone. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            backup_path = os.path.join(backup_dir, backup_name)
            restored = []

            # Files to restore
            for filename in ["budget.db", "app_settings.json", "scratch_pad_workspace.json"]:
                backup_file = os.path.join(backup_path, filename)
                if os.path.exists(backup_file):
                    shutil.copy2(backup_file, filename)
                    restored.append(filename)

            if restored:
                QMessageBox.information(
                    self,
                    "Restore Complete",
                    f"Backup restored successfully!\n\nFiles restored:\n" + "\n".join(f"  - {f}" for f in restored) +
                    "\n\nPlease restart the application for changes to take effect."
                )
            else:
                QMessageBox.warning(self, "Restore", "No files found in the selected backup.")

        except Exception as e:
            QMessageBox.critical(self, "Restore Error", f"Failed to restore backup: {str(e)}")

    def confirm_reset_data(self):
        """Math-based confirmation dialog for data reset"""
        import random
        from models import get_db, Week, Transaction, Account, Bill, AccountHistory

        # Generate random math problem
        num1 = random.randint(2, 99)
        num2 = random.randint(2, 99)
        correct_answer = num1 * num2

        # Create custom dialog
        from PyQt6.QtWidgets import QInputDialog

        # First confirmation
        reply = QMessageBox.question(
            self,
            "⚠️ DANGER: Reset All Data",
            "This will permanently delete ALL your data:\n\n"
            "• All transactions (spending, income, bills)\n"
            "• All pay weeks and periods\n"
            "• All savings accounts\n"
            "• All bills\n\n"
            "This action CANNOT be undone!\n\n"
            "Are you absolutely sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Math verification
        answer, ok = QInputDialog.getInt(
            self,
            "Math Verification Required",
            f"To confirm this dangerous action, solve:\n\n{num1} × {num2} = ?",
            0, 0, 999999, 1
        )

        if not ok:
            return

        if answer != correct_answer:
            QMessageBox.critical(
                self,
                "Incorrect Answer",
                f"Incorrect! The answer was {correct_answer}.\n\nData reset cancelled for your protection."
            )
            return

        # Perform the reset
        try:
            db = get_db()

            # Count items before deletion
            transaction_count = db.query(Transaction).count()
            week_count = db.query(Week).count()
            account_count = db.query(Account).count()
            bill_count = db.query(Bill).count()
            history_count = db.query(AccountHistory).count()

            # Delete all data (order matters due to foreign keys)
            db.query(AccountHistory).delete()  # Delete history first (references transactions)
            db.query(Transaction).delete()
            db.query(Week).delete()
            db.query(Account).delete()
            db.query(Bill).delete()

            db.commit()
            db.close()

            QMessageBox.information(
                self,
                "✅ Data Reset Complete",
                f"Successfully deleted:\n\n"
                f"• {transaction_count} transactions\n"
                f"• {week_count} weeks\n"
                f"• {account_count} accounts\n"
                f"• {bill_count} bills\n"
                f"• {history_count} balance history entries\n\n"
                f"Your app now has a clean slate!"
            )

            # Signal that settings changed so main window refreshes
            self.settings_saved.emit()

        except Exception as e:
            QMessageBox.critical(self, "Reset Failed", f"Error during data reset: {e}")

    def confirm_load_test_data(self):
        """Math-based confirmation dialog to load test data from generate_test_data.py"""
        import random

        # Generate random math problem
        num1 = random.randint(2, 50)
        num2 = random.randint(2, 50)
        correct_answer = num1 * num2

        # First confirmation
        reply = QMessageBox.question(
            self,
            "⚠️ Load Test Data",
            "This will delete ALL existing data and generate fresh test data:\n\n"
            "• All transactions, weeks, and history will be deleted\n"
            "• All accounts and bills will be deleted\n"
            "• Fresh test accounts, bills, and transactions will be created\n\n"
            "This action cannot be undone!\n\n"
            "Are you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Math verification with hidden answer
        from PyQt6.QtWidgets import QLineEdit
        dialog = QDialog(self)
        dialog.setWindowTitle("Math Verification Required")
        dialog_layout = QVBoxLayout()

        # Get background color for hiding the answer
        colors = theme_manager.get_colors()
        bg_color = colors['surface']

        # Create label with hidden answer (answer is same color as background)
        prompt_label = QLabel()
        prompt_label.setTextFormat(Qt.TextFormat.RichText)
        prompt_label.setText(
            f"To confirm this action, solve:<br><br>"
            f"{num1} × {num2} = ?<span style='color: {bg_color};'>{correct_answer}</span>"
        )
        prompt_label.setFont(theme_manager.get_font("main"))
        prompt_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        dialog_layout.addWidget(prompt_label)

        # Input field
        input_field = QLineEdit()
        input_field.setPlaceholderText("Enter answer")
        dialog_layout.addWidget(input_field)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        dialog_layout.addLayout(button_layout)

        dialog.setLayout(dialog_layout)

        # Connect buttons
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        # Show dialog
        result = dialog.exec()
        if result != QDialog.DialogCode.Accepted:
            return

        # Get the answer
        try:
            answer = int(input_field.text())
        except ValueError:
            answer = -1

        if answer != correct_answer:
            QMessageBox.critical(
                self,
                "Incorrect Answer",
                f"Incorrect! The answer was {correct_answer}.\n\nTest data load cancelled for your protection."
            )
            return

        # Run the generate_test_data script
        try:
            # Close transaction manager's database connection
            if hasattr(self.transaction_manager, 'db'):
                self.transaction_manager.db.close()

            # Close any existing database connections first
            from models.database import engine
            engine.dispose()

            # Import and run the generate_test_data function
            import sys
            import os

            # Add the project root to sys.path if not already there
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            # Import the generate_test_data module
            from generate_test_data import generate_test_data

            # Run the test data generation
            generate_test_data()

            # Reconnect transaction_manager to database
            from models import get_db
            self.transaction_manager.db = get_db()

            QMessageBox.information(
                self,
                "✅ Test Data Loaded",
                "Successfully generated fresh test data!\n\n"
                "• Created test accounts and bills\n"
                "• Created paychecks and weeks\n"
                "• Created spending transactions\n"
                "• Created transfers and abnormal transactions\n\n"
                "Ready for testing!"
            )

            # Signal that settings changed so main window refreshes
            self.settings_saved.emit()

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Load Failed", f"Error loading test data: {e}")

    def confirm_reset_test(self):
        """Math-based confirmation dialog for test data reset"""
        import random
        from models import get_db, Week, Transaction, Account, Bill, AccountHistory

        # Generate random math problem
        num1 = random.randint(2, 50)
        num2 = random.randint(2, 50)
        correct_answer = num1 * num2

        # Create custom dialog
        from PyQt6.QtWidgets import QInputDialog

        # First confirmation
        reply = QMessageBox.question(
            self,
            "⚠️ Reset Test Data",
            "This will reset for testing by deleting:\n\n"
            "• All transactions (spending, income, bills)\n"
            "• All pay weeks and periods\n"
            "• Reset all account balances to their starting values\n\n"
            "This will keep:\n"
            "• All savings accounts (structure and starting balances)\n"
            "• All bills (structure and starting balances)\n\n"
            "This action cannot be undone!\n\n"
            "Are you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Math verification with hidden answer
        from PyQt6.QtWidgets import QLineEdit
        dialog = QDialog(self)
        dialog.setWindowTitle("Math Verification Required")
        dialog_layout = QVBoxLayout()

        # Get background color for hiding the answer
        colors = theme_manager.get_colors()
        bg_color = colors['surface']

        # Create label with hidden answer (answer is same color as background)
        prompt_label = QLabel()
        prompt_label.setTextFormat(Qt.TextFormat.RichText)
        prompt_label.setText(
            f"To confirm this action, solve:<br><br>"
            f"{num1} × {num2} = ?<span style='color: {bg_color};'>{correct_answer}</span>"
        )
        prompt_label.setFont(theme_manager.get_font("main"))
        prompt_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        dialog_layout.addWidget(prompt_label)

        # Input field
        input_field = QLineEdit()
        input_field.setPlaceholderText("Enter answer")
        dialog_layout.addWidget(input_field)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        dialog_layout.addLayout(button_layout)

        dialog.setLayout(dialog_layout)

        # Connect buttons
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        # Show dialog
        result = dialog.exec()
        if result != QDialog.DialogCode.Accepted:
            return

        # Get the answer
        try:
            answer = int(input_field.text())
        except ValueError:
            answer = -1

        if answer != correct_answer:
            QMessageBox.critical(
                self,
                "Incorrect Answer",
                f"Incorrect! The answer was {correct_answer}.\n\nTest reset cancelled for your protection."
            )
            return

        # Perform the test reset
        try:
            # Close transaction manager's database connection
            if hasattr(self.transaction_manager, 'db'):
                self.transaction_manager.db.close()

            # Close any existing database connections first
            from models.database import engine, SessionLocal
            engine.dispose()

            # Create new session for this operation
            db = SessionLocal()

            # Count items before deletion
            transaction_count = db.query(Transaction).count()
            week_count = db.query(Week).count()
            history_count = db.query(AccountHistory).count()

            # Get accounts and bills
            accounts = db.query(Account).all()
            bills = db.query(Bill).all()
            account_count = len(accounts)
            bill_count = len(bills)

            # Get starting balances BEFORE deleting AccountHistory
            account_starting_balances = {}
            bill_starting_balances = {}

            # Get starting balances for accounts
            for account in accounts:
                # Find the starting balance entry (transaction_id is None, earliest date)
                starting_entry = db.query(AccountHistory).filter(
                    AccountHistory.account_id == account.id,
                    AccountHistory.account_type == "savings",
                    AccountHistory.transaction_id.is_(None)
                ).order_by(AccountHistory.transaction_date, AccountHistory.id).first()

                if starting_entry:
                    account_starting_balances[account.id] = starting_entry.change_amount
                else:
                    account_starting_balances[account.id] = 0.0

            # Get starting balances for bills
            for bill in bills:
                # Find the starting balance entry (transaction_id is None, earliest date)
                starting_entry = db.query(AccountHistory).filter(
                    AccountHistory.account_id == bill.id,
                    AccountHistory.account_type == "bill",
                    AccountHistory.transaction_id.is_(None)
                ).order_by(AccountHistory.transaction_date, AccountHistory.id).first()

                if starting_entry:
                    bill_starting_balances[bill.id] = starting_entry.change_amount
                else:
                    bill_starting_balances[bill.id] = 0.0

            # Now delete AccountHistory first (references transactions)
            db.query(AccountHistory).delete()

            # Delete transactions and weeks
            db.query(Transaction).delete()
            db.query(Week).delete()

            # Commit deletions before adding new entries
            db.commit()

            # Create starting balance entries for accounts using preserved values
            from models.account_history import AccountHistory

            for account in accounts:
                starting_balance = account_starting_balances[account.id]
                starting_entry = AccountHistory.create_starting_balance_entry(
                    account_id=account.id,
                    account_type="savings",
                    starting_balance=starting_balance
                )
                db.add(starting_entry)

            for bill in bills:
                starting_balance = bill_starting_balances[bill.id]
                starting_entry = AccountHistory.create_starting_balance_entry(
                    account_id=bill.id,
                    account_type="bill",
                    starting_balance=starting_balance
                )
                db.add(starting_entry)

            db.commit()
            db.close()

            # Reconnect transaction_manager to database
            from models import get_db
            self.transaction_manager.db = get_db()

            QMessageBox.information(
                self,
                "Test Reset Complete",
                f"Successfully reset test data:\n\n"
                f"• Deleted {transaction_count} transactions\n"
                f"• Deleted {week_count} weeks\n"
                f"• Deleted {history_count} balance history entries\n"
                f"• Reset {account_count} account balances to starting values\n"
                f"• Reset {bill_count} bill balances to starting values\n\n"
                f"Ready for testing!"
            )

            # Signal that settings changed so main window refreshes
            self.settings_saved.emit()

        except Exception as e:
            QMessageBox.critical(self, "Reset Failed", f"Error during test reset: {e}")

    def export_data(self):
        """Export all data to single Excel file matching import format"""
        from PyQt6.QtWidgets import QFileDialog
        from models import get_db, Week, Transaction, Account, Bill, AccountHistory
        import pandas as pd
        import os
        from datetime import datetime

        # Let user choose export location
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"budget_export_{timestamp}.xlsx"

        export_file, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data",
            os.path.join(os.path.expanduser("~"), default_filename),
            "Excel Files (*.xlsx)"
        )

        if not export_file:
            return

        try:
            db = get_db()

            # Prepare Spending table (columns A-D)
            spending_transactions = db.query(Transaction).filter(
                Transaction.transaction_type == "spending"
            ).order_by(Transaction.date).all()

            spending_data = []
            for t in spending_transactions:
                spending_data.append({
                    "Date": t.date,
                    "Day": t.date.strftime("%A"),
                    "Catigorie": t.category or "",
                    "Amount": t.amount
                })

            # Prepare Paychecks table (columns F-H)
            # Only export week 1 of each pay period (odd week numbers represent paychecks)
            weeks = db.query(Week).filter(Week.week_number % 2 == 1).order_by(Week.start_date).all()
            paycheck_data = []
            for w in weeks:
                paycheck_data.append({
                    "Start date": w.start_date,
                    "Pay Date": w.end_date,
                    "Amount.1": w.running_total
                })

            # Prepare BillPays table (columns J-L)
            billpay_transactions = db.query(Transaction).filter(
                Transaction.transaction_type == "bill_pay"
            ).order_by(Transaction.date).all()

            billpay_data = []
            for t in billpay_transactions:
                bill_name = t.bill.name if t.bill else (t.bill_type or "Unknown")
                billpay_data.append({
                    "Date.1": t.date,
                    "Bill": bill_name,
                    "Amount.2": -t.amount  # Negative for payments
                })

            # Prepare Accounts metadata (columns N-R)
            accounts = db.query(Account).all()
            account_data = []
            for a in accounts:
                # Get starting balance from AccountHistory
                first_history = db.query(AccountHistory).filter(
                    AccountHistory.account_id == a.id,
                    AccountHistory.transaction_id == None
                ).order_by(AccountHistory.transaction_date).first()

                starting_balance = first_history.change_amount if first_history else 0.0

                account_data.append({
                    "Account Name": a.name,
                    "Starting Balance": starting_balance,
                    "Goal Amount": a.goal_amount or 0.0,
                    "Auto Save Amount": a.auto_save_amount or 0.0,
                    "Is Default": 1.0 if a.is_default_save else 0.0
                })

            # Prepare Bills metadata (columns T-AA)
            bills = db.query(Bill).all()
            bill_data = []
            for b in bills:
                # Get starting balance from AccountHistory
                first_history = db.query(AccountHistory).filter(
                    AccountHistory.account_id == b.id,
                    AccountHistory.account_type == "bill",
                    AccountHistory.transaction_id == None
                ).order_by(AccountHistory.transaction_date).first()

                starting_balance = first_history.change_amount if first_history else 0.0

                bill_data.append({
                    "Bill Name": b.name,
                    "Bill Type": b.bill_type or "",
                    "Bill Starting Balance": starting_balance,
                    "Payment Frequency": b.payment_frequency or "monthly",
                    "Typical Amount": b.typical_amount or 0.0,
                    "Amount To Save": b.amount_to_save or 0.0,
                    "Is Variable": 1.0 if b.is_variable else 0.0,
                    "Notes": b.notes or ""
                })

            # Create DataFrames
            spending_df = pd.DataFrame(spending_data)
            paychecks_df = pd.DataFrame(paycheck_data)
            billpays_df = pd.DataFrame(billpay_data)
            accounts_df = pd.DataFrame(account_data)
            bills_df = pd.DataFrame(bill_data)

            # Create Excel writer
            with pd.ExcelWriter(export_file, engine='openpyxl') as writer:
                # Write all tables to the same sheet at specific column positions
                sheet_name = 'Sheet1'

                # Spending (columns A-D, 0-3)
                if not spending_df.empty:
                    spending_df.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0, index=False)

                # Paychecks (columns F-H, 5-7)
                if not paychecks_df.empty:
                    paychecks_df.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=5, index=False)

                # BillPays (columns J-L, 9-11)
                if not billpays_df.empty:
                    billpays_df.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=9, index=False)

                # Accounts (columns N-R, 13-17)
                if not accounts_df.empty:
                    accounts_df.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=13, index=False)

                # Bills (columns T-AA, 19-26)
                if not bills_df.empty:
                    bills_df.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=19, index=False)

            db.close()

            QMessageBox.information(
                self,
                "Export Complete",
                f"Successfully exported to:\n{export_file}\n\n"
                f"• {len(spending_df)} spending transactions\n"
                f"• {len(paychecks_df)} paychecks\n"
                f"• {len(billpays_df)} bill payments\n"
                f"• {len(accounts_df)} accounts\n"
                f"• {len(bills_df)} bills"
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Export Failed", f"Error during data export: {e}")

    def import_test_data(self):
        """Import data from user-selected Excel file with validation and mode selection"""
        from PyQt6.QtWidgets import (QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                      QRadioButton, QPushButton, QProgressBar, QTextEdit, QGroupBox)
        from PyQt6.QtCore import Qt, QTimer
        import os

        # Let user choose file
        excel_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Excel File to Import",
            os.path.expanduser("~"),
            "Excel Files (*.xlsx *.xls)"
        )

        if not excel_file:
            return

        try:
            import pandas as pd

            # Read entire file once to avoid pandas usecols bug with formatted/merged cells
            full_df = pd.read_excel(excel_file, sheet_name=0, header=0)

            # Extract transaction tables
            spending_df = full_df.iloc[:, 0:4].copy()
            spending_df.columns = ['Date', 'Day', 'Catigorie', 'Amount']
            spending_df = spending_df.dropna(how='all')

            paychecks_df = full_df.iloc[:, 5:8].copy()
            paychecks_df.columns = ['Start date', 'Pay Date', 'Amount.1']
            paychecks_df = paychecks_df.dropna(how='all')

            try:
                billpays_df = full_df.iloc[:, 9:12].copy()
                billpays_df.columns = ['Date.1', 'Bill', 'Amount.2']
                billpays_df = billpays_df.dropna(how='all')
            except:
                billpays_df = pd.DataFrame()

            # Extract metadata tables
            try:
                accounts_df = full_df.iloc[:, 13:18].copy()
                accounts_df.columns = ['Account Name', 'Starting Balance', 'Goal Amount', 'Auto Save Amount', 'Is Default']
                accounts_df = accounts_df[accounts_df['Account Name'].notna()]
            except:
                accounts_df = pd.DataFrame()

            try:
                bills_df = full_df.iloc[:, 19:27].copy()
                bills_df.columns = ['Bill Name', 'Bill Type', 'Bill Starting Balance', 'Payment Frequency',
                                   'Typical Amount', 'Amount To Save', 'Is Variable', 'Notes']
                bills_df = bills_df[bills_df['Bill Name'].notna()]
            except:
                bills_df = pd.DataFrame()

            # Create combined import dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Import Data")
            dialog.setMinimumWidth(500)
            main_layout = QVBoxLayout()

            # Top row: Found data (left) and mode selection (right)
            top_layout = QHBoxLayout()

            # Left: Found data display
            found_text = QTextEdit()
            found_text.setReadOnly(True)
            found_text.setMaximumHeight(120)
            found_data = f"Found in file:\n• {len(spending_df)} spending transactions\n• {len(paychecks_df)} paychecks\n• {len(billpays_df)} bill payments\n• {len(accounts_df)} accounts\n• {len(bills_df)} bills"
            found_text.setPlainText(found_data)
            top_layout.addWidget(found_text)

            # Right: Import mode selection
            mode_group = QGroupBox("Import Mode")
            mode_layout = QVBoxLayout()
            replace_radio = QRadioButton("Replace - Delete all existing data")
            merge_radio = QRadioButton("Merge - Skip duplicates")
            append_radio = QRadioButton("Append - Add all data")
            replace_radio.setChecked(True)
            mode_layout.addWidget(replace_radio)
            mode_layout.addWidget(merge_radio)
            mode_layout.addWidget(append_radio)
            mode_group.setLayout(mode_layout)
            top_layout.addWidget(mode_group)

            main_layout.addLayout(top_layout)

            # Middle row: Progress bar
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(0)
            main_layout.addWidget(progress_bar)

            # Bottom row: Results text (initially hidden)
            results_text = QTextEdit()
            results_text.setReadOnly(True)
            results_text.setMinimumHeight(225)
            results_text.setMaximumHeight(225)
            results_text.hide()
            main_layout.addWidget(results_text)

            # Buttons
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            import_button = QPushButton("Import")
            cancel_button = QPushButton("Cancel")
            button_layout.addWidget(import_button)
            button_layout.addWidget(cancel_button)
            main_layout.addLayout(button_layout)

            dialog.setLayout(main_layout)

            # Store references for import function
            dialog.import_mode = None
            dialog.should_import = False

            def on_import():
                if replace_radio.isChecked():
                    dialog.import_mode = "replace"
                elif merge_radio.isChecked():
                    dialog.import_mode = "merge"
                else:
                    dialog.import_mode = "append"
                dialog.should_import = True

                # Disable mode selection and import button during import
                replace_radio.setEnabled(False)
                merge_radio.setEnabled(False)
                append_radio.setEnabled(False)
                import_button.setEnabled(False)
                cancel_button.setText("Close")

                # Start import
                QTimer.singleShot(100, lambda: self.perform_test_data_import_with_dialog(
                    excel_file, dialog.import_mode, spending_df, paychecks_df,
                    billpays_df, accounts_df, bills_df, progress_bar, results_text, dialog
                ))

            def on_cancel():
                if not dialog.should_import or results_text.isVisible():
                    dialog.reject()

            import_button.clicked.connect(on_import)
            cancel_button.clicked.connect(on_cancel)

            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Error during import: {e}")

    def perform_test_data_import_with_dialog(self, excel_file, import_mode, spending_df, paychecks_df, billpays_df, accounts_df, bills_df, progress_bar, results_text, dialog):
        """Perform the actual data import with integrated progress bar and results display"""
        from PyQt6.QtCore import QCoreApplication

        try:
            import pandas as pd
            from services.transaction_manager import TransactionManager
            from services.paycheck_processor import PaycheckProcessor
            from models import get_db, Bill, Transaction, Week, Account, AccountHistory
            from datetime import datetime

            db = get_db()
            transaction_manager = TransactionManager()
            paycheck_processor = PaycheckProcessor()

            # Calculate total items for smooth progress updates
            total_items = len(accounts_df) + len(bills_df) + len(paychecks_df) + len(spending_df) + len(billpays_df)
            items_processed = 0

            progress_bar.setValue(0)
            QCoreApplication.processEvents()

            # Handle Replace mode: Clear all existing data
            if import_mode == "replace":
                try:
                    db.query(Transaction).delete()
                    db.query(Week).delete()
                    db.query(AccountHistory).delete()
                    if not accounts_df.empty:
                        db.query(Account).delete()
                    if not bills_df.empty:
                        db.query(Bill).delete()
                    db.commit()
                except Exception as e:
                    db.rollback()
                    print(f"Error clearing data: {e}")

            # For merge mode, get existing data for duplicate detection
            existing_weeks = set()
            existing_transactions = set()
            if import_mode == "merge":
                weeks = db.query(Week).all()
                for week in weeks:
                    existing_weeks.add((week.start_date, week.end_date))
                transactions = db.query(Transaction).all()
                for txn in transactions:
                    key = (txn.date, txn.amount, txn.category or txn.bill_type or "")
                    existing_transactions.add(key)

            # Import accounts metadata FIRST
            account_created = 0
            account_updated = 0
            account_skipped = 0

            if not accounts_df.empty:
                for idx, row in accounts_df.iterrows():
                    if pd.isna(row["Account Name"]):
                        continue

                    account_name = str(row["Account Name"]).strip()
                    starting_balance = float(row["Starting Balance"]) if not pd.isna(row["Starting Balance"]) else 0.0
                    goal_amount = float(row["Goal Amount"]) if not pd.isna(row["Goal Amount"]) else 0.0
                    auto_save_amount = float(row["Auto Save Amount"]) if not pd.isna(row["Auto Save Amount"]) else 0.0
                    is_default = bool(row["Is Default"]) if not pd.isna(row["Is Default"]) else False

                    existing_account = db.query(Account).filter(Account.name == account_name).first()

                    if import_mode == "append" and existing_account:
                        account_skipped += 1
                        continue

                    if import_mode == "merge":
                        if existing_account:
                            existing_account.goal_amount = goal_amount
                            existing_account.auto_save_amount = auto_save_amount
                            existing_account.is_default_save = is_default
                            account_updated += 1
                        else:
                            new_account = Account(
                                name=account_name,
                                goal_amount=goal_amount,
                                auto_save_amount=auto_save_amount,
                                is_default_save=is_default
                            )
                            db.add(new_account)
                            db.flush()
                            new_account.initialize_history(db, starting_balance=starting_balance)
                            account_created += 1
                    else:
                        new_account = Account(
                            name=account_name,
                            goal_amount=goal_amount,
                            auto_save_amount=auto_save_amount,
                            is_default_save=is_default
                        )
                        db.add(new_account)
                        db.flush()
                        new_account.initialize_history(db, starting_balance=starting_balance)
                        account_created += 1

                    # Update progress
                    items_processed += 1
                    if total_items > 0:
                        progress_bar.setValue(int((items_processed / total_items) * 100))
                        QCoreApplication.processEvents()

                db.commit()

            # Import bills metadata SECOND
            bill_created = 0
            bill_updated = 0
            bill_skipped = 0

            if not bills_df.empty:
                for idx, row in bills_df.iterrows():
                    if pd.isna(row["Bill Name"]):
                        continue

                    bill_name = str(row["Bill Name"]).strip()
                    bill_type = str(row["Bill Type"]).strip() if not pd.isna(row["Bill Type"]) else ""
                    starting_balance = float(row["Bill Starting Balance"]) if not pd.isna(row["Bill Starting Balance"]) else 0.0
                    payment_frequency = str(row["Payment Frequency"]).strip() if not pd.isna(row["Payment Frequency"]) else "monthly"
                    typical_amount = float(row["Typical Amount"]) if not pd.isna(row["Typical Amount"]) else 0.0
                    amount_to_save = float(row["Amount To Save"]) if not pd.isna(row["Amount To Save"]) else 0.0
                    is_variable = bool(row["Is Variable"]) if not pd.isna(row["Is Variable"]) else False
                    notes = str(row["Notes"]).strip() if not pd.isna(row["Notes"]) else ""

                    existing_bill = db.query(Bill).filter(Bill.name == bill_name).first()

                    if import_mode == "append" and existing_bill:
                        bill_skipped += 1
                        continue

                    if import_mode == "merge":
                        if existing_bill:
                            existing_bill.bill_type = bill_type
                            existing_bill.payment_frequency = payment_frequency
                            existing_bill.typical_amount = typical_amount
                            existing_bill.amount_to_save = amount_to_save
                            existing_bill.is_variable = is_variable
                            existing_bill.notes = notes
                            bill_updated += 1
                        else:
                            new_bill = Bill(
                                name=bill_name,
                                bill_type=bill_type,
                                payment_frequency=payment_frequency,
                                typical_amount=typical_amount,
                                amount_to_save=amount_to_save,
                                is_variable=is_variable,
                                notes=notes
                            )
                            db.add(new_bill)
                            db.flush()
                            new_bill.initialize_history(db, starting_balance=starting_balance)
                            bill_created += 1
                    else:
                        new_bill = Bill(
                            name=bill_name,
                            bill_type=bill_type,
                            payment_frequency=payment_frequency,
                            typical_amount=typical_amount,
                            amount_to_save=amount_to_save,
                            is_variable=is_variable,
                            notes=notes
                        )
                        db.add(new_bill)
                        db.flush()
                        new_bill.initialize_history(db, starting_balance=starting_balance)
                        bill_created += 1

                    # Update progress
                    items_processed += 1
                    if total_items > 0:
                        progress_bar.setValue(int((items_processed / total_items) * 100))
                        QCoreApplication.processEvents()

                db.commit()

            # Import paychecks THIRD (creates Week records needed by transactions)
            paycheck_count = 0
            paycheck_skipped = 0

            for idx, row in paychecks_df.iterrows():
                if pd.isna(row["Start date"]) or pd.isna(row["Pay Date"]) or pd.isna(row["Amount.1"]):
                    continue

                start_date = pd.to_datetime(row["Start date"]).date()
                pay_date = pd.to_datetime(row["Pay Date"]).date()
                amount = float(row["Amount.1"])

                if import_mode == "merge" and (start_date, pay_date) in existing_weeks:
                    paycheck_skipped += 1
                    continue

                try:
                    paycheck_processor.process_new_paycheck(amount, pay_date, start_date)
                    paycheck_count += 1
                except Exception as e:
                    if import_mode == "append":
                        paycheck_skipped += 1
                    continue

                # Update progress
                items_processed += 1
                if total_items > 0:
                    progress_bar.setValue(int((items_processed / total_items) * 100))
                    if idx % 5 == 0:  # Process events every 5 paychecks to reduce overhead
                        QCoreApplication.processEvents()

            # Import spending transactions FOURTH
            transaction_count = 0
            transaction_skipped = 0
            negative_count = 0

            for idx, row in spending_df.iterrows():
                if pd.isna(row["Date"]) or pd.isna(row["Catigorie"]) or pd.isna(row["Amount"]):
                    continue

                transaction_date = pd.to_datetime(row["Date"]).date()
                category = str(row["Catigorie"]).strip()
                amount = float(row["Amount"])

                # For merge mode, skip if transaction already exists
                if import_mode == "merge":
                    txn_key = (transaction_date, abs(amount), category)
                    if txn_key in existing_transactions:
                        transaction_skipped += 1
                        continue

                # Determine which week this transaction belongs to
                week_number = transaction_manager.get_week_number_for_date(transaction_date)
                if week_number is None:
                    continue

                # Determine include_in_analytics flag (negative amounts excluded from plotting)
                include_in_analytics = amount >= 0
                if amount < 0:
                    negative_count += 1

                transaction_data = {
                    "transaction_type": "spending",
                    "week_number": week_number,
                    "amount": abs(amount),
                    "date": transaction_date,
                    "description": f"{category} transaction",
                    "category": category,
                    "include_in_analytics": include_in_analytics
                }

                try:
                    transaction_manager.add_transaction(transaction_data)
                    transaction_count += 1
                except Exception as e:
                    continue

                # Update progress
                items_processed += 1
                if total_items > 0:
                    progress_bar.setValue(int((items_processed / total_items) * 100))
                    if idx % 20 == 0:  # Process events every 20 transactions to reduce overhead
                        QCoreApplication.processEvents()

            # Import bill payments FIFTH
            billpay_count = 0
            billpay_skipped = 0
            unmatched_bills = set()

            if not billpays_df.empty:
                existing_bills = {bill.name.lower(): bill for bill in db.query(Bill).all()}

                for idx, row in billpays_df.iterrows():
                    if pd.isna(row["Date.1"]) or pd.isna(row["Bill"]) or pd.isna(row["Amount.2"]):
                        continue

                    transaction_date = pd.to_datetime(row["Date.1"]).date()
                    bill_name = str(row["Bill"]).strip()
                    amount = float(row["Amount.2"])

                    # Find matching bill (case-insensitive)
                    bill_name_lower = bill_name.lower()
                    if bill_name_lower not in existing_bills:
                        unmatched_bills.add(bill_name)
                        continue

                    matched_bill = existing_bills[bill_name_lower]

                    # For merge mode, skip if bill transaction already exists
                    if import_mode == "merge":
                        txn_key = (transaction_date, abs(amount), matched_bill.bill_type)
                        if txn_key in existing_transactions:
                            billpay_skipped += 1
                            continue

                    # Determine which week this transaction belongs to
                    week_number = transaction_manager.get_week_number_for_date(transaction_date)
                    if week_number is None:
                        continue

                    # Determine transaction type based on amount sign
                    if amount < 0:
                        transaction_data = {
                            "transaction_type": "bill_pay",
                            "week_number": week_number,
                            "amount": abs(amount),
                            "date": transaction_date,
                            "description": f"Payment for {bill_name}",
                            "bill_id": matched_bill.id,
                            "bill_type": matched_bill.bill_type
                        }
                    else:
                        transaction_data = {
                            "transaction_type": "saving",
                            "week_number": week_number,
                            "amount": amount,
                            "date": transaction_date,
                            "description": f"Manual savings for {bill_name}",
                            "bill_id": matched_bill.id,
                            "bill_type": matched_bill.bill_type
                        }

                    try:
                        transaction_manager.add_transaction(transaction_data)
                        billpay_count += 1
                    except Exception as e:
                        continue

                    # Update progress
                    items_processed += 1
                    if total_items > 0:
                        progress_bar.setValue(int((items_processed / total_items) * 100))
                        if idx % 10 == 0:  # Process events every 10 bill payments to reduce overhead
                            QCoreApplication.processEvents()

            transaction_manager.close()
            paycheck_processor.close()
            db.close()

            progress_bar.setValue(100)
            QCoreApplication.processEvents()

            # Build success message
            mode_names = {"replace": "Replace", "merge": "Merge", "append": "Append"}
            message = f"Data imported successfully using {mode_names.get(import_mode, import_mode)} mode!\n\n"

            if not accounts_df.empty or not bills_df.empty:
                message += "Metadata:\n"
                if not accounts_df.empty:
                    message += f"• Accounts - Created: {account_created}, Updated: {account_updated}, Skipped: {account_skipped}\n"
                if not bills_df.empty:
                    message += f"• Bills - Created: {bill_created}, Updated: {bill_updated}, Skipped: {bill_skipped}\n"
                message += "\n"

            message += "Transactions:\n"
            message += f"• {paycheck_count} paychecks imported"
            if paycheck_skipped > 0:
                message += f" ({paycheck_skipped} skipped)"
            message += "\n"

            message += f"• {transaction_count} spending transactions imported"
            if transaction_skipped > 0:
                message += f" ({transaction_skipped} skipped)"
            message += f"\n  - {transaction_count - negative_count} positive (included in analytics)\n"
            message += f"  - {negative_count} negative (excluded from analytics)\n"

            if not billpays_df.empty:
                message += f"• {billpay_count} bill payments imported"
                if billpay_skipped > 0:
                    message += f" ({billpay_skipped} skipped)"
                message += "\n"

            if unmatched_bills:
                message += f"\n⚠️ Unmatched Bills (not imported):\n"
                for bill in sorted(unmatched_bills):
                    message += f"  - {bill}\n"

            # Show results in the dialog
            results_text.setPlainText(message)
            results_text.show()
            self.settings_saved.emit()

        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = f"Error during import: {e}"
            results_text.setPlainText(error_msg)
            results_text.show()
            progress_bar.setValue(0)


def load_app_settings():
    """Load application settings from file"""
    try:
        if os.path.exists("app_settings.json"):
            with open("app_settings.json", 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading app settings: {e}")
    
    # Return defaults if file doesn't exist or error occurs
    return {
        "default_theme": "dark",
        "bills_sort_order": "Alphabetical",
        "savings_sort_order": "Alphabetical",
        "dashboard_chart1_account": "random",
        "dashboard_chart2_account": "random",
        "default_hourly_rate": 50.00,
        "default_analytics_only": True,
        "time_frame_filter": "All Time",
        "enable_tax_features": False,
        "testing_mode": False
    }


def get_setting(key, default=None):
    """Get a specific setting value"""
    settings = load_app_settings()
    return settings.get(key, default)


def save_setting(key, value):
    """Save a specific setting value to app_settings.json"""
    try:
        settings = load_app_settings()
        settings[key] = value
        with open("app_settings.json", 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving setting {key}: {e}")
        return False