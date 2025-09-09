"""
New Dashboard Layout - matches user's diagram exactly
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QCheckBox, QPushButton)
from PyQt6.QtCore import Qt
from themes import theme_manager
from widgets import PieChartWidget, LineChartWidget, BarChartWidget, ProgressChartWidget, AnimatedGifWidget

def create_new_dashboard_layout(self):
    """Create the new layout exactly matching the user's diagram"""
    main_layout = QVBoxLayout()
    main_layout.setSpacing(3)
    main_layout.setContentsMargins(5, 5, 5, 5)
    
    # Header section - compact
    header_layout = QHBoxLayout()
    header_layout.setSpacing(10)
    
    # Title - smaller
    title = QLabel("💰 Financial Control Panel")
    title.setFont(theme_manager.get_font("subtitle"))
    header_layout.addWidget(title)
    
    header_layout.addStretch()
    
    # Analytics toggle
    self.analytics_toggle = QCheckBox("Normal Spending Only")
    self.analytics_toggle.setChecked(True)
    self.analytics_toggle.toggled.connect(self.toggle_analytics_mode)
    self.analytics_toggle.setToolTip("Filter abnormal transactions from analytics")
    header_layout.addWidget(self.analytics_toggle)
    
    main_layout.addLayout(header_layout)
    
    # TOP ROW - All elements horizontally: Pie charts | Category Key | Week | Accounts | Bills | [Calc]
    top_row = QHBoxLayout()
    top_row.setSpacing(3)
    top_row.setAlignment(Qt.AlignmentFlag.AlignTop)
    
    # Pie charts section (stacked vertically)
    pie_charts_container = QVBoxLayout()
    pie_charts_container.setSpacing(1)
    
    # Total spending pie chart (larger)
    self.total_pie_chart = PieChartWidget("")
    self.total_pie_chart.setMinimumHeight(120)
    self.total_pie_chart.setMaximumHeight(120)
    pie_charts_container.addWidget(self.total_pie_chart)
    
    # Weekly spending pie chart (smaller)
    self.weekly_pie_chart = PieChartWidget("")
    self.weekly_pie_chart.setMinimumHeight(90)
    self.weekly_pie_chart.setMaximumHeight(90)
    pie_charts_container.addWidget(self.weekly_pie_chart)
    
    top_row.addLayout(pie_charts_container)
    
    # Category key
    self.category_key_frame = QFrame()
    self.category_key_frame.setFrameStyle(QFrame.Shape.Box)
    self.category_key_frame.setMaximumWidth(100)
    self.category_key_frame.setMinimumHeight(210)
    self.category_key_frame.setMaximumHeight(210)
    
    colors = theme_manager.get_colors()
    self.category_key_frame.setStyleSheet(f"""
        QFrame {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            margin: 2px;
        }}
    """)
    
    key_layout = QVBoxLayout()
    key_title = QLabel("Categories")
    key_title.setFont(theme_manager.get_font("small"))
    key_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    key_title.setStyleSheet(f"color: {colors['primary']}; font-weight: bold;")
    key_layout.addWidget(key_title)
    
    # Category key will be populated in refresh
    self.category_key_layout = QVBoxLayout()
    key_layout.addLayout(self.category_key_layout)
    key_layout.addStretch()
    
    self.category_key_frame.setLayout(key_layout)
    top_row.addWidget(self.category_key_frame)
    
    # Week status card - takes space it needs
    weekly_status_card = self.create_dynamic_card("Week", "weekly_status", fixed_lines=4)
    top_row.addWidget(weekly_status_card)
    
    # Accounts card - takes space it needs (priority for sizing)
    account_summary_card = self.create_dynamic_card("Accounts", "account_summary")
    top_row.addWidget(account_summary_card)
    
    # Bills card - takes space it needs (priority for sizing)
    bills_status_card = self.create_dynamic_card("Bills", "bills_status")
    top_row.addWidget(bills_status_card)
    
    # Hour calculator button
    self.hour_calc_button = QPushButton("Calc")
    self.hour_calc_button.setMaximumWidth(60)
    self.hour_calc_button.setMaximumHeight(30)
    self.hour_calc_button.clicked.connect(self.open_hour_calculator_popup)
    top_row.addWidget(self.hour_calc_button, 0, Qt.AlignmentFlag.AlignTop)
    
    main_layout.addLayout(top_row)
    
    # BOTTOM ROW - Future space | Stacked chart areas
    bottom_row = QHBoxLayout()
    bottom_row.setSpacing(3)
    
    # Left: Future feature space
    placeholder_box = QFrame()
    placeholder_box.setFrameStyle(QFrame.Shape.Box)
    placeholder_box.setMinimumHeight(150)
    placeholder_box.setMaximumHeight(200)
    placeholder_box.setMaximumWidth(400)
    
    placeholder_box.setStyleSheet(f"""
        QFrame {{
            background-color: {colors['surface_variant']};
            border: 2px dashed {colors['primary']};
            border-radius: 4px;
            margin: 2px;
        }}
    """)
    
    placeholder_layout = QVBoxLayout()
    placeholder_label = QLabel("💡 Available for future features")
    placeholder_label.setFont(theme_manager.get_font("small"))
    placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    placeholder_label.setStyleSheet(f"""
        QLabel {{
            color: {colors['primary']};
            font-style: italic;
        }}
    """)
    placeholder_layout.addWidget(placeholder_label)
    placeholder_box.setLayout(placeholder_layout)
    
    bottom_row.addWidget(placeholder_box)
    
    # Right: Stacked chart areas (one on top of other for wider plots)
    stacked_charts = QVBoxLayout()
    stacked_charts.setSpacing(3)
    
    # Top chart area
    top_chart = QFrame()
    top_chart.setFrameStyle(QFrame.Shape.Box)
    top_chart.setStyleSheet(f"""
        QFrame {{
            background-color: {colors['surface_variant']};
            border: 2px dashed {colors['secondary']};
            border-radius: 4px;
            margin: 2px;
        }}
    """)
    
    top_chart_layout = QVBoxLayout()
    top_chart_label = QLabel("📊 Top Chart")
    top_chart_label.setFont(theme_manager.get_font("subtitle"))
    top_chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    top_chart_label.setStyleSheet(f"color: {colors['secondary']}; font-style: italic;")
    top_chart_layout.addWidget(top_chart_label)
    top_chart.setLayout(top_chart_layout)
    
    stacked_charts.addWidget(top_chart)
    
    # Bottom chart area
    bottom_chart = QFrame()
    bottom_chart.setFrameStyle(QFrame.Shape.Box)
    bottom_chart.setStyleSheet(f"""
        QFrame {{
            background-color: {colors['surface_variant']};
            border: 2px dashed {colors['accent']};
            border-radius: 4px;
            margin: 2px;
        }}
    """)
    
    bottom_chart_layout = QVBoxLayout()
    bottom_chart_label = QLabel("📈 Bottom Chart")
    bottom_chart_label.setFont(theme_manager.get_font("subtitle"))
    bottom_chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    bottom_chart_label.setStyleSheet(f"color: {colors['accent']}; font-style: italic;")
    bottom_chart_layout.addWidget(bottom_chart_label)
    bottom_chart.setLayout(bottom_chart_layout)
    
    stacked_charts.addWidget(bottom_chart)
    
    bottom_row.addLayout(stacked_charts, 1)  # Charts take more space
    
    main_layout.addLayout(bottom_row)
    
    # Continue with existing middle and bottom sections...
    # (Keep the existing chart sections below this)
    
    return main_layout